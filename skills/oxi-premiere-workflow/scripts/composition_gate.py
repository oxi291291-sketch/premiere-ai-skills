#!/usr/bin/env python3
"""Composition gate: no overlay on the speaker's face, every overlay inside the safe zone.

Premiere use: references/composition-gate.md (frames from pr_export_frames.py,
base = the same times with the overlay tracks hidden). Copied from
oxi-auto-editor on 2026-10-31 and extended to read frame folders.

Usage:
  python composition_gate.py --times --plan work/text_plan.json [--srt work/sub.srt]
      prints the sample times, comma separated, for pr_export_frames.py --at.
  python composition_gate.py RENDER OUT_DIR --plan work/text_plan.json
      [--plan work/broll_plan.json] [--srt work/sub.srt] [--caption-box X,Y,W,H]
      [--base render/cut.mp4 | --overlay-layer render/overlay.webm]
      [--frame-plan work/frame_plan.json] [--zone 9x16 | --zone T,B,L,R]
      [--samples 3] [--face-every 1.0] [--model PATH]

Inputs
  RENDER        the draft (or final) with every overlay burned in: a video file,
                or a folder of stills written by pr_export_frames.py (times from
                its frames.json, else from names like frame_03_008.033s.png).
                With a folder, --base and --overlay-layer are folders too, with
                frames at the same times; only the exported times are checked.
  --plan        JSON with overlay windows: a list, or a dict holding the list
                under "overlays" or "items". Each item: start, end (seconds on
                the render's timeline), optional id, kind (text | caption |
                callout | broll; default from the file name), box [x, y, w, h]
                as fractions of the frame, full_frame (B-roll that replaces the
                picture). Items without start/end are ignored.
  --srt         every cue becomes a caption window; its box is measured, or
                --caption-box when nothing can be measured.
  --base        the same render without overlays (same cut, reframe, colour).
                Overlay boxes are then measured from the pixel difference and
                the face is detected on the base, where no text hides it.
  --overlay-layer  the overlay alone with alpha (HyperFrames --format webm/mov);
                boxes come from its alpha channel. Most exact source.
  --frame-plan  JSON whose "protect" list ({start, end, box}) marks the UI
                element or product to keep clear on screen recordings and
                product shots. --plan files may carry "protect" too.

Checks, at --samples frames inside each window
  1. every overlay box (measured, else declared) misses each face box padded
     by 10 % of its height, and every "protect" box;
  2. every text, caption and callout box, and every inset B-roll box, lies
     inside the zone. Full-frame B-roll is exempt; while it is on screen no
     speaker face is protected.
  With --face-every N, the face (unpadded) must also sit inside the zone on a
  frame every N s outside full-frame B-roll (acceptance row 4).

A measured box is reported under the id of the declared box it overlaps most.
When the layer or diff shows nothing inside an open window, the declared boxes
are checked instead; a box that cannot be measured or declared fails: the gate
never passes what it did not see. For the same reason a window with no sampled
frame fails, and so does a sample whose --base frame is missing. Faces shorter
than half the tallest face in the frame are ignored (background people, false
hits on props). Writes OUT_DIR/composition_gate.json and OUT_DIR/sheet.jpg
(failures first). Exit 0 pass, 1 fail, 2 setup error.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

SKILL = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = SKILL / "models" / "face_detection_yunet_2023mar.onnx"

# Margins kept clear, as fractions of the frame: top, bottom, left, right.
ZONES = {"9x16": (0.12, 0.25, 0.0, 0.15),
         "text_9x16": (0.16, 0.28, 0.10, 0.18)}  # working text inset, not a platform specification
FACE_PAD = 0.10           # of the face height, on every side
DIFF_LEVEL = 40           # 0..255, per-channel difference that counts as overlay
MIN_BLOCK = 0.0005        # smallest overlay block, fraction of the frame area
UNMEASURABLE = 0.5        # diff covering more than this is not an overlay
NEIGHBOUR_S = 0.25        # look this far outside a window for a hidden face
SIDE_FACE = 0.5           # faces shorter than this share of the tallest are ignored
BOX_KINDS = ("text", "caption", "callout", "broll")


def fail_setup(msg):
    print(f"composition_gate: {msg}", file=sys.stderr)
    sys.exit(2)


# ---------- video ----------

def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def frame_at(path, t, alpha=False):
    """Decoded frame at t seconds (BGR, or BGRA with alpha), None past the end."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}"]
    if alpha and str(path).lower().endswith(".webm"):
        cmd += ["-c:v", "libvpx-vp9"]  # the native vp9 decoder drops alpha
    cmd += ["-i", str(path), "-frames:v", "1", "-an",
            "-pix_fmt", "rgba" if alpha else "rgb24", "-f", "image2pipe", "-c:v", "png", "-"]
    data = subprocess.run(cmd, capture_output=True).stdout
    if not data:
        return None
    return cv2.imdecode(np.frombuffer(data, np.uint8),
                        cv2.IMREAD_UNCHANGED if alpha else cv2.IMREAD_COLOR)


FRAME_NAME = re.compile(r"frame_\d+_(\d+(?:\.\d+)?)s\.png$", re.I)


class Video:
    times = None  # any time can be decoded

    def __init__(self, path):
        self.path = path
        self.duration = duration(path)

    def at(self, t, alpha=False):
        return frame_at(self.path, t, alpha)


class Frames:
    """Stills from pr_export_frames.py, keyed by sequence time (ms)."""

    def __init__(self, path):
        d = Path(path)
        self.files = {}
        index = d / "frames.json"
        if index.is_file():
            for row in json.loads(index.read_text(encoding="utf-8")).get("frames", []):
                if row.get("file"):
                    f = Path(row["file"])
                    if not f.is_file():  # folder moved: the index holds absolute paths
                        f = d / f.name
                    self.files[round(float(row["t"]), 3)] = f
        else:
            for f in d.glob("*.png"):
                m = FRAME_NAME.search(f.name)
                if m:
                    self.files[round(float(m.group(1)), 3)] = f
        if not self.files:
            fail_setup(f"no frames in {path}: expected frames.json or frame_NN_SSS.SSSs.png")
        self.times = sorted(self.files)
        self.duration = self.times[-1] + 0.001

    def at(self, t, alpha=False):
        f = self.files.get(round(t, 3))
        if f is None or not f.is_file():
            return None
        # np.fromfile: cv2.imread cannot open non-ASCII paths on Windows.
        return cv2.imdecode(np.fromfile(str(f), np.uint8),
                            cv2.IMREAD_UNCHANGED if alpha else cv2.IMREAD_COLOR)


def open_source(path):
    return Frames(path) if Path(path).is_dir() else Video(path)


# ---------- geometry (boxes are x, y, w, h in pixels) ----------

def intersects(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def inside(box, zone):
    return (box[0] >= zone[0] and box[1] >= zone[1]
            and box[0] + box[2] <= zone[0] + zone[2] and box[1] + box[3] <= zone[1] + zone[3])


def zone_rect(margins, w, h):
    top, bottom, left, right = margins
    return (left * w, top * h, w * (1 - left - right), h * (1 - top - bottom))


def pad_face(box, w, h):
    p = box[3] * FACE_PAD
    x0, y0 = max(box[0] - p, 0), max(box[1] - p, 0)
    x1, y1 = min(box[0] + box[2] + p, w), min(box[1] + box[3] + p, h)
    return (x0, y0, x1 - x0, y1 - y0)


def to_px(frac, w, h):
    return (frac[0] * w, frac[1] * h, frac[2] * w, frac[3] * h)


def overlap(a, b):
    dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return dx * dy if dx > 0 and dy > 0 else 0.0


def owner(box, checked, w, h):
    """Id of the active overlay whose declared box overlaps a measured box most."""
    best, best_area = None, 0.0
    for x in checked:
        if x.get("box"):
            a = overlap(box, to_px(x["box"], w, h))
            if a > best_area:
                best, best_area = x["id"], a
    return best or "+".join(x["id"] for x in checked)


def to_frac(box, w, h):
    return [round(box[0] / w, 4), round(box[1] / h, 4), round(box[2] / w, 4), round(box[3] / h, 4)]


# ---------- detection ----------

class Faces:
    def __init__(self, model, score):
        # Load from bytes: OpenCV cannot open non-ASCII paths on Windows.
        buf = np.frombuffer(Path(model).read_bytes(), np.uint8)
        self.det = cv2.FaceDetectorYN.create("onnx", buf, np.zeros(0, np.uint8), (320, 320), score)

    def __call__(self, img):
        h, w = img.shape[:2]
        self.det.setInputSize((w, h))
        _, found = self.det.detect(img[:, :, :3].copy())
        if found is None:
            return []
        boxes = [(float(f[0]), float(f[1]), float(f[2]), float(f[3])) for f in found]
        # Keep the speaker and faces of similar size; small hits are background
        # people or false positives on props (hanging instruments, 2026-10-31 test).
        tallest = max(b[3] for b in boxes)
        return sorted((b for b in boxes if b[3] >= SIDE_FACE * tallest), key=lambda b: -b[3])


def blocks(mask, w, h):
    """Bounding boxes of overlay blocks: nearby glyphs merged into one block."""
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k = max(3, int(w * 0.02)) | 1
    merged = cv2.dilate(mask, np.ones((k, k), np.uint8))
    n, labels = cv2.connectedComponents(merged)
    out = []
    for i in range(1, n):
        ys, xs = np.nonzero((labels == i) & (mask > 0))
        if len(xs) < MIN_BLOCK * w * h:
            continue
        out.append((float(xs.min()), float(ys.min()),
                    float(xs.max() - xs.min() + 1), float(ys.max() - ys.min() + 1)))
    return out


def measure_diff(frame, base):
    """Overlay blocks from frame minus base; None when the difference is not an overlay."""
    h, w = frame.shape[:2]
    if base.shape[:2] != (h, w):
        base = cv2.resize(base, (w, h), interpolation=cv2.INTER_AREA)
    d = cv2.absdiff(cv2.GaussianBlur(frame, (5, 5), 0), cv2.GaussianBlur(base, (5, 5), 0)).max(axis=2)
    mask = (d > DIFF_LEVEL).astype(np.uint8)
    if mask.mean() > UNMEASURABLE:
        return None
    return blocks(mask, w, h)


def measure_alpha(layer, w, h):
    if layer is None or layer.ndim < 3 or layer.shape[2] < 4:
        return None
    if layer.shape[:2] != (h, w):
        layer = cv2.resize(layer, (w, h), interpolation=cv2.INTER_AREA)
    return blocks((layer[:, :, 3] > 24).astype(np.uint8), w, h)


# ---------- plans ----------

def srt_seconds(ts):
    hh, mm, rest = ts.strip().replace(",", ".").split(":")
    return int(hh) * 3600 + int(mm) * 60 + float(rest)


def read_srt(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    out = []
    for n, m in enumerate(re.finditer(r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)", text)):
        out.append({"id": f"sub{n + 1:03d}", "kind": "caption",
                    "start": srt_seconds(m.group(1)), "end": srt_seconds(m.group(2))})
    return out


def read_plan(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("overlays", data.get("items", []))
    protect = [] if isinstance(data, list) else data.get("protect", [])
    stem = Path(path).stem.lower()
    default = "broll" if "broll" in stem else "caption" if "sub" in stem else "text"
    windows = []
    for n, it in enumerate(items):
        if not isinstance(it, dict) or "start" not in it or "end" not in it:
            continue
        kind = it.get("kind", default)
        if kind not in BOX_KINDS:
            kind = default
        windows.append({"id": str(it.get("id", f"{stem}{n + 1:03d}")), "kind": kind,
                        "start": float(it["start"]), "end": float(it["end"]),
                        "box": it.get("box"), "full_frame": bool(it.get("full_frame"))})
    return windows, protect


def sample_times(win, k):
    a, b = win["start"], win["end"]
    if b - a < 0.6 or k <= 1:
        return [round((a + b) / 2, 3)]
    return [round(a + (b - a) * (i + 1) / (k + 1), 3) for i in range(k)]


# ---------- gate ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("render", nargs="?")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--times", action="store_true",
                    help="print the sample times for pr_export_frames.py --at and exit")
    ap.add_argument("--plan", action="append", default=[])
    ap.add_argument("--srt")
    ap.add_argument("--caption-box", help="x,y,w,h fractions, used when a caption box cannot be measured")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--base")
    src.add_argument("--overlay-layer")
    ap.add_argument("--frame-plan")
    ap.add_argument("--zone", default="9x16", help="9x16 or top,bottom,left,right fractions")
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--face-every", type=float, default=0.0)
    ap.add_argument("--model", default=os.environ.get("OXI_FACE_MODEL", str(DEFAULT_MODEL)))
    ap.add_argument("--score", type=float, default=0.6)
    args = ap.parse_args()

    if not args.times and not (args.render and args.out_dir):
        fail_setup("pass RENDER and OUT_DIR, or --times")
    if not args.times and not Path(args.model).is_file():
        fail_setup(f"face model not found: {args.model} (see references/composition-gate.md)")
    if args.zone in ZONES:
        margins = ZONES[args.zone]
    else:
        try:
            margins = tuple(float(v) for v in args.zone.split(","))
            assert len(margins) == 4
        except (ValueError, AssertionError):
            fail_setup(f"bad --zone {args.zone!r}")
    cap_box = [float(v) for v in args.caption_box.split(",")] if args.caption_box else None

    windows, protect = [], []
    for p in args.plan:
        w_, p_ = read_plan(p)
        windows += w_
        protect += p_
    if args.srt:
        windows += [dict(c, box=cap_box) for c in read_srt(args.srt)]
    if args.frame_plan:
        fp = json.loads(Path(args.frame_plan).read_text(encoding="utf-8"))
        protect += fp.get("protect", []) if isinstance(fp, dict) else []
    if not windows:
        fail_setup("no overlay windows: pass --plan and/or --srt")
    full_frame = [w for w in windows if w["kind"] == "broll" and w["full_frame"]]
    planned = sorted({t for w in windows if w not in full_frame
                      for t in sample_times(w, args.samples) if t >= 0})

    if args.times:
        print(",".join(f"{t:.3f}" for t in planned))
        return

    faces = Faces(args.model, args.score)
    render = open_source(args.render)
    base_src = open_source(args.base) if args.base else None
    layer_src = open_source(args.overlay_layer) if args.overlay_layer else None
    total = render.duration

    def broll_on(t):
        return any(w["start"] <= t < w["end"] for w in full_frame)

    def face_boxes(t, frame, base):
        """Faces to protect at t and where they were found."""
        if broll_on(t):
            return [], "full-frame B-roll"
        if base is not None:
            return faces(base), "base"
        found = faces(frame)
        if found:
            return found, "render"
        # An overlay may hide the face on the render: look just outside the window.
        for dt in (-NEIGHBOUR_S, NEIGHBOUR_S):
            nb = render.at(t + dt)  # a frame folder has no neighbours: None
            found = faces(nb) if nb is not None else []
            if found:
                return found, "render neighbour"
        return [], "none found"

    samples, covered = [], set()
    if render.times is None:
        times = [t for t in planned if t < total]
    else:  # a frame folder: check the frames that were exported
        times = [t for t in render.times if any(x["start"] <= t < x["end"] for x in windows)]
    for t in times:
        frame = render.at(t)
        if frame is None:
            continue
        h, w = frame.shape[:2]
        zone = zone_rect(margins, w, h)
        active = [x for x in windows if x["start"] <= t < x["end"]]
        checked = [x for x in active if x not in full_frame]
        if not checked:
            continue
        covered.update(id(x) for x in checked)
        base = base_src.at(t) if base_src else None
        if base is not None and base.shape[:2] != (h, w):
            base = cv2.resize(base, (w, h), interpolation=cv2.INTER_AREA)
        fboxes, fsource = face_boxes(t, frame, base)
        guard = [("face", pad_face(f, w, h)) for f in fboxes]
        guard += [("protect", to_px(p["box"], w, h)) for p in protect
                  if p.get("start", 0) <= t < p.get("end", total) and p.get("box")]

        measured, how = None, "declared"
        if layer_src:
            measured, how = measure_alpha(layer_src.at(t, alpha=True), w, h), "alpha"
        elif base is not None:
            measured, how = measure_diff(frame, base), "diff"
        boxes = []
        if measured:
            for m in measured:
                boxes.append({"id": owner(m, checked, w, h), "source": how, "box": m})
        else:
            # Nothing measured while windows are open: an empty layer or a diff that
            # missed the overlay must not pass silently, so fall back to declared boxes.
            src = ("declared" if how == "declared" else
                   f"declared ({how} unmeasurable)" if measured is None else
                   f"declared ({how} found nothing)")
            for x in checked:
                if x.get("box"):
                    boxes.append({"id": x["id"], "source": src, "box": to_px(x["box"], w, h)})
                else:
                    boxes.append({"id": x["id"], "source": "unknown", "box": None})

        problems = []
        if base_src and base is None:
            problems.append(f"base frame missing at {t:.3f}s: export the base at the same times")
        for b in boxes:
            if b["box"] is None:
                problems.append(f"{b['id']}: box not measured and not declared")
                continue
            for name, g in guard:
                if intersects(b["box"], g):
                    problems.append(f"{b['id']}: overlay covers the {name}")
            if not inside(b["box"], zone):
                problems.append(f"{b['id']}: outside the safe zone")
        samples.append({"t": t, "windows": [x["id"] for x in active], "face_source": fsource,
                        "faces": [to_frac(f, w, h) for f in fboxes],
                        "overlays": [dict(b, box=to_frac(b["box"], w, h) if b["box"] else None) for b in boxes],
                        "pass": not problems, "problems": problems,
                        "_draw": (frame, zone, [g for _, g in guard], boxes)})

    # A window the gate never looked at must not pass silently.
    unchecked = [x["id"] for x in windows if x not in full_frame and id(x) not in covered]

    framing = []
    if args.face_every > 0:
        src = base_src or render
        if src.times is None:
            grid = [args.face_every / 2 + i * args.face_every
                    for i in range(int((total - args.face_every / 2) // args.face_every) + 1)]
        else:  # a frame folder: every exported frame is a framing sample
            grid = src.times
        for t in grid:
            if broll_on(t):
                continue
            img = src.at(t)
            if img is not None:
                h, w = img.shape[:2]
                zone = zone_rect(margins, w, h)
                found = faces(img)
                framing.append({"t": round(t, 3), "faces": [to_frac(f, w, h) for f in found],
                                "pass": all(inside(f, zone) for f in found),
                                "note": "" if found else "no face found"})

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    failed = ([s for s in samples if not s["pass"]] + [f for f in framing if not f["pass"]]
              + unchecked)
    report = {"render": str(args.render), "zone_margins_tblr": margins, "face_pad": FACE_PAD,
              "box_source": "alpha" if args.overlay_layer else "diff" if args.base else "declared",
              "windows": len(windows), "samples": len(samples), "failed": len(failed),
              "pass": not failed,
              "results": [{k: v for k, v in s.items() if k != "_draw"} for s in samples],
              "unchecked_windows": unchecked,
              "framing": framing}
    (out / "composition_gate.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    write_sheet(out / "sheet.jpg", sorted(samples, key=lambda s: s["pass"])[:30])

    for s in samples:
        if not s["pass"]:
            print(f"FAIL {s['t']:8.3f}s  " + "; ".join(s["problems"]))
    for f in framing:
        if not f["pass"]:
            print(f"FAIL {f['t']:8.3f}s  face outside the safe zone")
    for i in unchecked:
        print(f"FAIL {i}: no frame sampled inside its window (export it with --times)")
    print(f"composition gate: {'PASS' if not failed else 'FAIL'}  "
          f"{len(samples)} samples, {len(failed)} failed, boxes {report['box_source']}  -> {out}")
    sys.exit(0 if not failed else 1)


def write_sheet(path, samples, thumb_w=270, cols=6):
    if not samples:
        return
    tiles = []
    for s in samples:
        frame, zone, guard, boxes = s["_draw"]
        img = frame[:, :, :3].copy()
        lw = max(2, img.shape[1] // 270)
        rect = lambda b, c: cv2.rectangle(img, (int(b[0]), int(b[1])),
                                          (int(b[0] + b[2]), int(b[1] + b[3])), c, lw)
        rect(zone, (0, 220, 255))
        for g in guard:
            rect(g, (0, 0, 255))
        for b in boxes:
            if b["box"] is not None:
                rect(b["box"], (0, 200, 0) if s["pass"] else (255, 0, 255))
        scale = thumb_w / img.shape[1]
        tile = cv2.resize(img, (thumb_w, int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA)
        cv2.putText(tile, f"{s['t']:.2f}s {'ok' if s['pass'] else 'FAIL'}", (6, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        tiles.append(tile)
    th = max(t.shape[0] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, th - t.shape[0], 0, 0, cv2.BORDER_CONSTANT) for t in tiles]
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    ok, buf = cv2.imencode(".jpg", np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
    Path(path).write_bytes(buf.tobytes())


if __name__ == "__main__":
    main()
