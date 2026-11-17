#!/usr/bin/env python3
"""Measure picture and sound around SFX cues in a reference video or a review mix.

    python cue_probe.py frames   VIDEO --at 6.333 15.44 --out DIR [--radius 0.22] [--crop X0,Y0,X1,Y1]
    python cue_probe.py cuts     VIDEO --out DIR [--range A B] [--crop X0,Y0,X1,Y1] [--rows]
    python cue_probe.py onsets   MEDIA --out DIR [--range A B]
    python cue_probe.py envelope MEDIA --out DIR [--range A B] [--window 0.05] [--drop-db 20]
    python cue_probe.py ab       MEDIA --start S --end E --asset SFX.wav --target T --out DIR
                                 [--anchor A] [--peak-db -15] [--headroom-db 4]
                                 [--shift -0.08 0.08] [--cue-only] [--video] [--name NAME]

frames    Every native-rate frame within --radius of each --at time, on one
          sheet per time, labelled with frame number and real timestamp. Use it
          to name the last outgoing frame, the first changed frame and the first
          readable frame of a cut, flash, whip or graphic entrance.
cuts      Frame-to-frame difference over the whole file (or --range), with
          candidate cut and flash frames. A candidate is a place to look, not a
          proven edit: confirm each one on a `frames` sheet.
onsets    Sudden rises per frequency band, separately for mid (L+R) and side
          (L-R). A side-only onset is usually an effect or a wide music layer;
          a mid-only one is usually voice, kick or a centred hit.
envelope  Level per --window (50 ms) for the whole mix, the side signal and
          four bands, plus `drops`: stretches at least --drop-db under the
          median level. Use it for music dropouts, silences and loop seams, on
          a reference video or on Oxi's own review mix.
ab        Lay one SFX file over a stretch of the clip so that the audible
          anchor of the file (--anchor, seconds from the file start; default is
          its loudest sample) lands on --target. Writes the stretch without the
          cue, with it, and optionally with the cue --shift seconds earlier or
          later, all lowered by the same --headroom-db with no limiting, so the
          pair can be auditioned outside Premiere. Exits 1 if a file would clip.

Times are seconds from the start of the file, read from the frame timestamps
ffmpeg reports (never frame number / fps), so they hold for variable-frame-rate
phone footage too. Each command prints a short summary and writes
`<stem>.<command>.json` (and sheets or WAVs) into --out.

Needs ffmpeg and ffprobe 5.1 or newer on PATH, numpy, and Pillow for `frames`.
These are measurements of a finished mix. They say where energy and picture
change; which sound made the change still needs ears. See
references/sound-cue-placement.md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import wave

import numpy as np

ONSET_BANDS = [(30, 125), (125, 550), (550, 2200), (2200, 6500), (6500, 10500)]
ENVELOPE_BANDS = {"bass": (35, 160), "mid": (180, 1600),
                  "presence": (1600, 5500), "high": (5500, 10500)}
FONTS = ("consola.ttf", "DejaVuSansMono.ttf", "NotoSansMono-Regular.ttf", "arial.ttf")
SCAN_W, SCAN_H = 128, 96


def die(msg, code=2):
    print("cue_probe: " + msg, file=sys.stderr)
    raise SystemExit(code)


def need_tools():
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die("%s not found on PATH" % tool)


def fnum(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def probe(path):
    """Start time and duration of the file, and of its first video and audio stream."""
    if not os.path.isfile(path):
        die("file not found: %s" % path)
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=start_time,duration:stream=codec_type,start_time,width,height,avg_frame_rate",
         "-of", "json", path], capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        die("ffprobe cannot read %s: %s" % (path, res.stderr.strip()[-300:]))
    data = json.loads(res.stdout or "{}")
    fmt = data.get("format", {})
    info = {"start": fnum(fmt.get("start_time")), "duration": fnum(fmt.get("duration")),
            "video": None, "audio": None}
    for st in data.get("streams", []):
        kind = st.get("codec_type")
        if kind not in ("video", "audio") or info[kind] is not None:
            continue
        entry = {"start": fnum(st.get("start_time"), info["start"])}
        if kind == "video":
            num, _, den = (st.get("avg_frame_rate") or "0/1").partition("/")
            entry["fps"] = fnum(num) / fnum(den, 1.0) if fnum(den, 1.0) else 0.0
            entry["width"] = int(fnum(st.get("width")))
            entry["height"] = int(fnum(st.get("height")))
        info[kind] = entry
    return info


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False)


def out_path(args, suffix, stem=None):
    os.makedirs(args.out, exist_ok=True)
    stem = stem or os.path.splitext(os.path.basename(args.media))[0]
    return os.path.join(args.out, stem + suffix)


# --- picture -----------------------------------------------------------------

def frame_table(path, info):
    """Presentation timestamps of every video frame, seconds from the file start.

    Read from the packets (no decoding), so it is cheap on long files. The
    position of a timestamp in this table is the frame number.
    """
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "packet=pts_time,flags", "-of", "csv=p=0", path],
        capture_output=True, text=True, errors="replace")
    times = []
    for line in res.stdout.splitlines():
        parts = line.strip().split(",")
        if len(parts) > 1 and "D" in parts[1]:      # packet the player discards
            continue
        try:
            times.append(float(parts[0]))
        except ValueError:
            continue
    table = np.sort(np.asarray(times, float)) - info["start"]
    return table


def frame_numbers(table, times):
    """Frame number for each timestamp, or -1 when the table has no match within 2 ms."""
    if not len(table):
        return [-1] * len(times)
    pos = np.clip(np.searchsorted(table, times), 1, max(1, len(table) - 1))
    left = np.abs(table[pos - 1] - times)
    right = np.abs(table[np.minimum(pos, len(table) - 1)] - times)
    idx = np.where(left <= right, pos - 1, np.minimum(pos, len(table) - 1))
    off = np.abs(table[idx] - times)
    return [int(i) if o <= 0.002 else -1 for i, o in zip(idx, off)]


def timing(table):
    """Frame interval statistics; `vfr` is true when intervals differ by more than 1.5 ms."""
    if len(table) < 2:
        return {"frames": int(len(table)), "vfr": False}
    gaps = np.diff(table) * 1000.0
    return {"frames": int(len(table)),
            "frame_interval_ms": [round(float(gaps.min()), 3), round(float(np.median(gaps)), 3),
                                  round(float(gaps.max()), 3)],
            "vfr": bool(gaps.max() - gaps.min() > 1.5)}


def crop_filter(spec):
    if not spec:
        return ""
    try:
        x0, y0, x1, y1 = [float(v) for v in spec.split(",")]
    except ValueError:
        die("--crop wants four fractions X0,Y0,X1,Y1, for example 0,0,1,0.5")
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        die("--crop fractions must satisfy 0 <= X0 < X1 <= 1 and 0 <= Y0 < Y1 <= 1")
    return "crop=iw*%.4f:ih*%.4f:iw*%.4f:ih*%.4f," % (x1 - x0, y1 - y0, x0, y0)


PTS_RE = re.compile(r"pts_time:\s*(-?[0-9.]+)")
SIZE_RE = re.compile(r"\bs:(\d+)x(\d+)")


def ffmpeg_video_cmd(path, vf, pix, start, end):
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-loglevel", "info"]
    if start and start > 0:
        cmd += ["-ss", "%.6f" % start]
    cmd += ["-i", path]
    if end is not None:
        # trim reads each frame's own timestamp; -t rounds to the output frame
        # rate and loses the last frames of a variable-frame-rate window.
        vf = "trim=end=%.6f," % (end - (start or 0.0) + 0.0005) + vf
    cmd += ["-map", "0:v:0", "-an", "-vf", vf + "showinfo", "-fps_mode", "passthrough",
            "-f", "rawvideo", "-pix_fmt", pix, "-"]
    return cmd


def run_video(path, vf, pix, start, end, frame_bytes=None, consume=None):
    """Decode video and collect the timestamp ffmpeg reports for every frame.

    With `frame_bytes` and `consume`, frames are handed over one at a time
    (whole-file scans stay small in memory). Otherwise the raw output is
    returned whole, for short windows. Timestamps are seconds from file start.
    """
    proc = subprocess.Popen(ffmpeg_video_cmd(path, vf, pix, start, end),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    times, sizes, tail = [], [], []

    def drain():
        for raw in proc.stderr:
            line = raw.decode("utf-8", "replace")
            hit = PTS_RE.search(line)
            if hit and "showinfo" in line:
                times.append(float(hit.group(1)))
                if not sizes:
                    size = SIZE_RE.search(line)
                    if size:
                        sizes.append((int(size.group(1)), int(size.group(2))))
            else:
                tail.append(line)
                del tail[:-8]

    thread = threading.Thread(target=drain, daemon=True)
    thread.start()
    data = b""
    if consume is not None:
        while True:
            buf = proc.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                break
            consume(buf)
    else:
        data = proc.stdout.read()
    proc.wait()
    thread.join()
    if proc.returncode != 0:
        die("ffmpeg failed on %s: %s" % (path, "".join(tail).strip()[-400:]))
    shift = start if start and start > 0 else 0.0
    return data, [t + shift for t in times], (sizes[0] if sizes else (0, 0))


def load_font(name, size):
    from PIL import ImageFont
    for cand in ([name] if name else []) + list(FONTS):
        try:
            return ImageFont.truetype(cand, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:                       # Pillow before 10.1
        return ImageFont.load_default()


def cmd_frames(args):
    from PIL import Image, ImageDraw
    info = probe(args.media)
    if not info["video"]:
        die("no video stream in %s" % args.media)
    table = frame_table(args.media, info)
    font = load_font(args.font, 14)
    vf = crop_filter(args.crop) + (
        "scale=%d:%d:force_original_aspect_ratio=decrease:force_divisible_by=2," % (args.tile, args.tile))
    stem = os.path.splitext(os.path.basename(args.media))[0]
    report = {"media": os.path.abspath(args.media), "timing": timing(table),
              "radius": args.radius, "crop": args.crop, "sheets": []}
    for at in args.at:
        a, b = max(0.0, at - args.radius), at + args.radius
        data, times, (w, h) = run_video(args.media, vf, "rgb24", a, b)
        size = w * h * 3
        count = min(len(times), len(data) // size if size else 0)
        if not count:
            print("%.3f s: no frames decoded (past the end of the file?)" % at)
            report["sheets"].append({"at": at, "frames": []})
            continue
        frames = np.frombuffer(data[:count * size], np.uint8).reshape(count, h, w, 3)
        times = times[:count]
        numbers = frame_numbers(table, np.asarray(times))
        grey = frames.astype(np.float32).mean(axis=3)
        luma = grey.mean(axis=(1, 2))
        diff = np.concatenate([[0.0], np.abs(np.diff(grey, axis=0)).mean(axis=(1, 2))])
        nearest = int(np.argmin(np.abs(np.asarray(times) - at)))
        cols = min(args.cols, count)
        rows = math.ceil(count / cols)
        label_h = 22
        sheet = Image.new("RGB", (cols * w, rows * (h + label_h)), "#101314")
        draw = ImageDraw.Draw(sheet)
        for i in range(count):
            r, c = divmod(i, cols)
            x, y = c * w, r * (h + label_h)
            sheet.paste(Image.fromarray(frames[i]), (x, y))
            if i == nearest:
                draw.rectangle([x, y + h, x + w - 1, y + h + label_h - 1], fill="#b3261e")
            tag = ("f%d " % numbers[i] if numbers[i] >= 0 else "") + "%.3f" % times[i]
            draw.text((x + 3, y + h + 2), tag, font=font, fill="white")
        name = "%s.frames-%07.3f.jpg" % (stem, at)
        sheet.save(out_path(args, "", name), quality=89)
        entry = {"at": at, "sheet": name, "nearest_frame": numbers[nearest],
                 "frames": [{"frame": numbers[i], "t": round(times[i], 4),
                             "luma": round(float(luma[i]), 1), "diff": round(float(diff[i]), 2)}
                            for i in range(count)]}
        report["sheets"].append(entry)
        big = int(np.argmax(diff))
        print("%.3f s: %d frames %.3f-%.3f s, largest change into frame %s at %.3f s -> %s"
              % (at, count, times[0], times[-1],
                 numbers[big] if numbers[big] >= 0 else "?", times[big], name))
    if report["timing"].get("vfr"):
        print("variable frame rate: intervals %s ms; frame number / fps would be wrong here"
              % report["timing"]["frame_interval_ms"])
    write_json(out_path(args, ".frames.json"), report)
    return 0 if all(s["frames"] for s in report["sheets"]) else 1


def find_peaks(x, height=None, distance=1, prominence=None, wlen=2000):
    """Local maxima of `x`, filtered by height, then spacing, then prominence."""
    x = np.asarray(x, float)
    if len(x) < 3:
        return np.zeros(0, int)
    mid = x[1:-1]
    idx = np.flatnonzero((mid > x[:-2]) & (mid >= x[2:])) + 1
    if height is not None:
        idx = idx[x[idx] >= height]
    if distance > 1 and len(idx):
        keep = np.ones(len(idx), bool)
        for j in np.argsort(x[idx])[::-1]:
            if not keep[j]:
                continue
            k = j - 1
            while k >= 0 and idx[j] - idx[k] < distance:
                keep[k] = False
                k -= 1
            k = j + 1
            while k < len(idx) and idx[k] - idx[j] < distance:
                keep[k] = False
                k += 1
        idx = idx[keep]
    if prominence is not None and len(idx):
        idx = idx[np.array([peak_prominence(x, i, wlen) >= prominence for i in idx])]
    return idx


def peak_prominence(x, i, wlen):
    """Height of x[i] above the higher of the two valleys that separate it from a taller peak."""
    peak = x[i]
    bases = []
    for seg in (x[max(0, i - wlen):i][::-1], x[i + 1:i + 1 + wlen]):
        higher = np.flatnonzero(seg > peak)
        stop = higher[0] if len(higher) else len(seg)
        bases.append(float(seg[:stop].min()) if stop else float(peak))
    return float(peak - max(bases))


def cmd_cuts(args):
    info = probe(args.media)
    if not info["video"]:
        die("no video stream in %s" % args.media)
    table = frame_table(args.media, info)
    start, end = args.range if args.range else (None, None)
    vf = crop_filter(args.crop) + "scale=%d:%d:flags=area," % (SCAN_W, SCAN_H)
    stats = []
    prev = [None]

    def consume(buf):
        grey = np.frombuffer(buf, np.uint8).reshape(SCAN_H, SCAN_W).astype(np.float32)
        diff = float(np.abs(grey - prev[0]).mean()) if prev[0] is not None else 0.0
        prev[0] = grey
        lap = (grey[:-2, 1:-1] + grey[2:, 1:-1] + grey[1:-1, :-2] + grey[1:-1, 2:]
               - 4.0 * grey[1:-1, 1:-1])
        stats.append((diff, float(grey.mean()), float(lap.var())))

    _, times, _ = run_video(args.media, vf, "gray", start, end, SCAN_W * SCAN_H, consume)
    count = min(len(times), len(stats))
    if not count:
        die("no frames decoded from %s" % args.media, 1)
    times = np.asarray(times[:count])
    diff = np.array([s[0] for s in stats[:count]])
    luma = np.array([s[1] for s in stats[:count]])
    sharp = np.array([s[2] for s in stats[:count]])
    numbers = frame_numbers(table, times)
    floor = max(args.min_change, float(np.median(diff)) * 1.6)
    found = {int(i): "change" for i in find_peaks(diff, prominence=floor)}
    for i in range(1, count - 1):
        if diff[i] >= 18 and luma[i] >= luma[i - 1] + 17 and luma[i] >= luma[i + 1] + 17:
            found[i] = "flash"
    candidates = [{"frame": numbers[i], "t": round(float(times[i]), 4), "kind": found[i],
                   "diff": round(float(diff[i]), 2), "luma_before": round(float(luma[i - 1]), 1),
                   "luma": round(float(luma[i]), 1)} for i in sorted(found)]
    report = {"media": os.path.abspath(args.media), "timing": timing(table),
              "range": [float(times[0]), float(times[-1])], "scanned_frames": count,
              "crop": args.crop, "threshold": round(floor, 2), "candidates": candidates}
    write_json(out_path(args, ".cuts.json"), report)
    if args.rows:
        with open(out_path(args, ".cuts-rows.csv"), "w", encoding="utf-8") as fh:
            fh.write("frame,t,diff,luma,sharp\n")
            for i in range(count):
                fh.write("%d,%.4f,%.2f,%.1f,%.1f\n" % (numbers[i], times[i], diff[i], luma[i], sharp[i]))
    print("%d frames scanned, %.3f-%.3f s, %d candidates (threshold %.2f)"
          % (count, times[0], times[-1], len(candidates), floor))
    for c in candidates[:args.show]:
        print("  %-6s frame %-6s %8.3f s  diff %6.2f  luma %5.1f -> %5.1f"
              % (c["kind"], c["frame"] if c["frame"] >= 0 else "?", c["t"], c["diff"],
                 c["luma_before"], c["luma"]))
    if len(candidates) > args.show:
        print("  ... %d more in the JSON" % (len(candidates) - args.show))
    if report["timing"].get("vfr"):
        print("variable frame rate: intervals %s ms" % report["timing"]["frame_interval_ms"])
    return 0


# --- sound -------------------------------------------------------------------

def read_audio(path, rate, start=None, end=None):
    """Stereo float32 samples and the time, from file start, of the first sample."""
    info = probe(path)
    if not info["audio"]:
        die("no audio stream in %s" % path)
    first = max(0.0, info["audio"]["start"] - info["start"])
    # -ss after -i: the decoder runs from the file start and drops samples, so a
    # range is sample-identical to the same stretch of a whole-file decode.
    # Seeking the input instead restarts the resampler and shifts the waveform.
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-i", path]
    if start and start > first:
        cmd += ["-ss", "%.6f" % start]
        first = start
    if end is not None:
        cmd += ["-t", "%.6f" % max(0.0, end - first)]
    cmd += ["-vn", "-map", "0:a:0", "-ac", "2", "-ar", str(rate), "-f", "f32le", "-"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        die("ffmpeg cannot decode audio of %s: %s" % (path, res.stderr.decode("utf-8", "replace")[-300:]))
    samples = np.frombuffer(res.stdout, np.float32)
    return samples[:len(samples) // 2 * 2].reshape(-1, 2), first


def band_power(y, rate, size, hop, bands, centred):
    """Power per band and analysis frame, `len(bands)` x frames, from Hann-windowed FFTs."""
    window = np.hanning(size + 1)[:-1]
    if centred:                 # frame k is centred on sample k * hop; the tail is zero-filled
        y = np.concatenate([np.zeros(size // 2), y, np.zeros(size // 2)])
        y = np.concatenate([y, np.zeros(-(len(y) - size) % hop)])
    if len(y) < size:
        return np.zeros((len(bands), 0))
    frames = np.lib.stride_tricks.sliding_window_view(y, size)[::hop]
    freqs = np.fft.rfftfreq(size, 1.0 / rate)
    masks = [(freqs >= lo) & (freqs < hi) for lo, hi in bands]
    out = np.empty((len(bands), len(frames)))
    for a in range(0, len(frames), 4096):
        spec = np.abs(np.fft.rfft(frames[a:a + 4096] * window, axis=1)) ** 2
        for k, mask in enumerate(masks):
            out[k, a:a + 4096] = spec[:, mask].sum(axis=1)
    return out


def smooth_edges(x, pad):
    return np.pad(x, ((0, 0), (pad, pad)), mode="symmetric")


def onsets(y, rate, first, args):
    size, hop = 512, int(round(rate * 0.01))
    power = band_power(y, rate, size, hop, ONSET_BANDS, True) / np.hanning(size + 1)[:-1].sum() ** 2
    if power.shape[1] < 3:
        return []
    db = 10 * np.log10(np.maximum(power, 1e-10))
    short = np.lib.stride_tricks.sliding_window_view(smooth_edges(db, 1), 3, axis=1).mean(axis=2)
    floor = np.median(np.lib.stride_tricks.sliding_window_view(smooth_edges(db, 18), 37, axis=1), axis=2)
    delta = short - floor
    strength = np.maximum(delta, 0).mean(axis=0)
    peaks = find_peaks(strength, height=args.min_score, prominence=args.prominence,
                       distance=max(1, int(round(args.min_gap * rate / hop))))
    return [{"t": round(first + k * hop / rate, 2), "score": round(float(strength[k]), 1),
             "band": "%d-%d Hz" % ONSET_BANDS[int(np.argmax(delta[:, k]))],
             "db": round(float(10 * np.log10(power[:, k].sum() + 1e-10)), 1)} for k in peaks]


def cmd_onsets(args):
    start, end = args.range if args.range else (None, None)
    audio, first = read_audio(args.media, args.rate, start, end)
    if not len(audio):
        die("no audio decoded from %s" % args.media, 1)
    audio = audio.astype(np.float64)
    report = {"media": os.path.abspath(args.media), "range": [first, first + len(audio) / args.rate],
              "mid": onsets(audio.mean(axis=1), args.rate, first, args),
              "side": onsets((audio[:, 1] - audio[:, 0]) / 2, args.rate, first, args)}
    write_json(out_path(args, ".onsets.json"), report)
    print("%.2f-%.2f s: %d mid onsets, %d side onsets"
          % (report["range"][0], report["range"][1], len(report["mid"]), len(report["side"])))
    for name in ("mid", "side"):
        for o in report[name][:args.show]:
            print("  %-4s %8.2f s  score %4.1f  %-13s %6.1f dB" % (name, o["t"], o["score"], o["band"], o["db"]))
        if len(report[name]) > args.show:
            print("  ... %d more %s onsets in the JSON" % (len(report[name]) - args.show, name))
    return 0


def to_db(power):
    return 10 * np.log10(power + 1e-12)


def cmd_envelope(args):
    start, end = args.range if args.range else (None, None)
    audio, first = read_audio(args.media, args.rate, start, end)
    win = int(round(args.rate * args.window))
    n = len(audio) // win
    if n < 1:
        die("less than one %.3f s window of audio in %s" % (args.window, args.media), 1)
    st = audio[:n * win].astype(np.float64).reshape(n, win, 2)
    mono = st.mean(axis=2)
    series = {"rms": to_db((st ** 2).mean(axis=(1, 2))),
              "side": to_db((((st[:, :, 0] - st[:, :, 1]) / 2) ** 2).mean(axis=1))}
    scale = 2.0 / (win * (np.hanning(win + 1)[:-1] ** 2).sum())
    bands = band_power(mono.ravel(), args.rate, win, win, list(ENVELOPE_BANDS.values()), False) * scale
    for k, name in enumerate(ENVELOPE_BANDS):
        series[name] = to_db(bands[k])
    level = series["rms"]
    median = float(np.median(level))
    low = np.flatnonzero(level < median - args.drop_db)
    drops = []
    if len(low):
        for run in np.split(low, np.flatnonzero(np.diff(low) > 1) + 1):
            if len(run) >= args.min_windows:
                drops.append({"start": round(first + run[0] * args.window, 3),
                              "end": round(first + (run[-1] + 1) * args.window, 3),
                              "depth_db": round(float(np.median(level[run]) - median), 1)})
    report = {"media": os.path.abspath(args.media), "start": first, "window": args.window,
              "median_rms_dbfs": round(median, 1), "drop_db": args.drop_db, "drops": drops,
              "bands_hz": ENVELOPE_BANDS,
              "series": {k: np.round(v, 1).tolist() for k, v in series.items()}}
    write_json(out_path(args, ".envelope.json"), report)
    print("%d windows of %.0f ms from %.2f s, median %.1f dBFS, %d drops of %.0f dB or more"
          % (n, args.window * 1000, first, median, len(drops), args.drop_db))
    for d in drops:
        print("  drop %8.3f-%.3f s  %.1f dB under the median" % (d["start"], d["end"], d["depth_db"]))
    return 0


def dbfs(value):
    return round(20 * math.log10(value), 2) if value > 0 else -120.0


def write_wav(path, audio, rate):
    with wave.open(path, "wb") as fh:
        fh.setparams((2, 2, rate, 0, "NONE", "not compressed"))
        fh.writeframes(np.round(np.clip(audio, -1.0, 1.0) * 32767).astype("<i2").tobytes())


def cmd_ab(args):
    if args.end <= args.start:
        die("--end must be after --start")
    rate = 48000
    info = probe(args.media)
    bed, first = read_audio(args.media, rate, args.start, args.end)
    if abs(first - args.start) > 0.001 or not len(bed):
        die("the audio of %s starts at %.3f s; move --start to it or later" % (args.media, first))
    bed = bed.astype(np.float64)
    cue, _ = read_audio(args.asset, rate)
    cue = cue.astype(np.float64)
    if not len(cue) or not np.abs(cue).max():
        die("the asset %s is empty or silent" % args.asset)
    if args.peak_db is not None:
        cue = cue * (10 ** (args.peak_db / 20) / np.abs(cue).max())
    anchor = args.anchor
    if anchor is None:
        anchor = float(np.argmax(np.abs(cue).max(axis=1))) / rate
    gain = 10 ** (-args.headroom_db / 20)
    name = args.name or os.path.splitext(os.path.basename(args.media))[0]
    os.makedirs(args.out, exist_ok=True)

    def place(shift):
        at = int(round((args.target + shift - anchor - args.start) * rate))
        if at < 0 or at + len(cue) > len(bed):
            die("the cue (%.3f s long, anchor at %.3f s) does not fit %.3f-%.3f s when its anchor "
                "sits on %.3f s; widen --start/--end"
                % (len(cue) / rate, anchor, args.start, args.end, args.target + shift))
        return at

    def tag(shift):
        return "%s%03d" % ("m" if shift < 0 else "p", round(abs(shift) * 1000))

    versions = [("original", None, True)]
    versions.append(("overlay", 0.0, True))
    for shift in args.shift or []:
        versions.append(("overlay-" + tag(shift), shift, True))
    if args.cue_only:
        versions.append(("cue-only", 0.0, False))
    at0 = place(0.0)
    span = bed[at0:at0 + len(cue)]
    report = {"media": os.path.abspath(args.media), "asset": os.path.abspath(args.asset),
              "start": args.start, "end": args.end, "target": args.target,
              "anchor_in_asset": round(anchor, 4), "anchor_source": "given" if args.anchor is not None else "loudest sample",
              "cue_starts_at": round(args.start + at0 / rate, 4),
              "headroom_db": args.headroom_db,
              "cue_peak_dbfs_before_headroom": dbfs(float(np.abs(cue).max())),
              "cue_rms_dbfs_before_headroom": dbfs(float(np.sqrt((cue ** 2).mean()))),
              "bed_rms_dbfs_under_cue": dbfs(float(np.sqrt((span ** 2).mean()))),
              "files": []}
    clipped = False
    for label, shift, with_bed in versions:
        mix = bed.copy() if with_bed else np.zeros_like(bed)
        if shift is not None:
            at = place(shift)
            mix[at:at + len(cue)] += cue
        mix *= gain
        peak = float(np.abs(mix).max())
        clipped = clipped or peak >= 1.0
        wav = os.path.join(args.out, "%s-%s.wav" % (name, label))
        write_wav(wav, mix, rate)
        entry = {"file": os.path.basename(wav), "shift": shift, "peak_dbfs": dbfs(peak)}
        if args.video:
            if not info["video"]:
                die("--video needs a video stream in %s" % args.media)
            mp4 = os.path.join(args.out, "%s-%s.mp4" % (name, label))
            res = subprocess.run(
                ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", "%.6f" % args.start, "-i", args.media,
                 "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-t", "%.6f" % (args.end - args.start),
                 "-vf", "scale=640:640:force_original_aspect_ratio=decrease:force_divisible_by=2",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-c:a", "aac", "-b:a", "192k", mp4],
                capture_output=True, text=True, errors="replace")
            if res.returncode != 0:
                die("ffmpeg could not write %s: %s" % (mp4, res.stderr.strip()[-300:]), 1)
            entry["video"] = os.path.basename(mp4)
        report["files"].append(entry)
    write_json(os.path.join(args.out, name + ".ab.json"), report)
    print("cue anchor %.3f s into the asset (%s) on %.3f s; cue starts at %.3f s"
          % (anchor, report["anchor_source"], args.target, report["cue_starts_at"]))
    print("cue RMS %.1f dBFS over a bed of %.1f dBFS; every file lowered %.1f dB"
          % (report["cue_rms_dbfs_before_headroom"], report["bed_rms_dbfs_under_cue"], args.headroom_db))
    for f in report["files"]:
        print("  %-28s peak %6.2f dBFS" % (f["file"], f["peak_dbfs"]))
    if clipped:
        print("CLIPPED: a file reaches 0 dBFS; raise --headroom-db or lower --peak-db")
        return 1
    return 0


# --- command line ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    def common(name, audio_range=True):
        p = sub.add_parser(name)
        p.add_argument("media")
        p.add_argument("--out", required=True, help="folder for the JSON, sheets and WAVs")
        if audio_range:
            p.add_argument("--range", nargs=2, type=float, metavar=("A", "B"),
                           help="measure only A-B seconds")
        return p

    p = common("frames", False)
    p.add_argument("--at", nargs="+", type=float, required=True, help="cue times in seconds")
    p.add_argument("--radius", type=float, default=0.22, help="seconds shown on each side (default 0.22)")
    p.add_argument("--crop", help="part of the picture to show, as fractions X0,Y0,X1,Y1")
    p.add_argument("--tile", type=int, default=240, help="longest side of one frame in pixels")
    p.add_argument("--cols", type=int, default=8)
    p.add_argument("--font", help="font file for the labels; a monospace system font is found without it")
    p.set_defaults(func=cmd_frames)

    p = common("cuts")
    p.add_argument("--crop", help="part of the picture to measure, as fractions X0,Y0,X1,Y1")
    p.add_argument("--min-change", type=float, default=4.0,
                   help="smallest frame-difference prominence that counts (default 4, on 0-255)")
    p.add_argument("--rows", action="store_true", help="also write every frame's numbers to CSV")
    p.add_argument("--show", type=int, default=40, help="candidates to print")
    p.set_defaults(func=cmd_cuts)

    p = common("onsets")
    p.add_argument("--rate", type=int, default=24000)
    p.add_argument("--min-score", type=float, default=2.8, help="mean rise over the bands, dB")
    p.add_argument("--prominence", type=float, default=1.8)
    p.add_argument("--min-gap", type=float, default=0.08, help="seconds between two onsets")
    p.add_argument("--show", type=int, default=20, help="onsets to print per channel")
    p.set_defaults(func=cmd_onsets)

    p = common("envelope")
    p.add_argument("--rate", type=int, default=24000)
    p.add_argument("--window", type=float, default=0.05, help="seconds per level value")
    p.add_argument("--drop-db", type=float, default=20.0, help="dB under the median that counts as a drop")
    p.add_argument("--min-windows", type=int, default=3, help="shortest drop, in windows")
    p.set_defaults(func=cmd_envelope)

    p = common("ab", False)
    p.add_argument("--start", type=float, required=True)
    p.add_argument("--end", type=float, required=True)
    p.add_argument("--asset", required=True, help="the SFX file to lay over the clip")
    p.add_argument("--target", type=float, required=True, help="picture time the cue must land on")
    p.add_argument("--anchor", type=float, help="seconds into the asset that land on --target "
                                                "(default: its loudest sample)")
    p.add_argument("--peak-db", type=float, help="set the asset's peak to this dBFS before mixing")
    p.add_argument("--headroom-db", type=float, default=4.0, help="lower every output by this much")
    p.add_argument("--shift", nargs="+", type=float, metavar="SECONDS",
                   help="also write the cue this much earlier (negative) or later")
    p.add_argument("--cue-only", action="store_true", help="also write the cue without the clip's sound")
    p.add_argument("--video", action="store_true", help="also mux each version with the picture (MP4)")
    p.add_argument("--name", help="prefix of the output files (default: the media file name)")
    p.set_defaults(func=cmd_ab)

    args = ap.parse_args()
    need_tools()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
