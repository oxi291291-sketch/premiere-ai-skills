import argparse
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path


TICKS_PER_SECOND = 254_016_000_000


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild one FCP XML audio track as a WAV timeline.")
    parser.add_argument("xml_path", type=Path)
    parser.add_argument("wav_path", type=Path)
    parser.add_argument("--track", type=int, default=1, help="One-based audio track index")
    parser.add_argument("--dry-run", action="store_true")
    args_ns = parser.parse_args()

    root = ET.parse(args_ns.xml_path).getroot()
    sequence = root.find("sequence")
    if sequence is None:
        raise RuntimeError("Sequence not found")

    timebase = float(sequence.findtext("rate/timebase", "24"))
    ntsc = sequence.findtext("rate/ntsc", "FALSE").upper() == "TRUE"
    fps = timebase * 1000 / 1001 if ntsc else timebase

    file_paths: dict[str, str] = {}
    for file_el in root.findall(".//file"):
        file_id = file_el.get("id")
        url = file_el.findtext("pathurl")
        if file_id and url:
            decoded = urllib.parse.unquote(url)
            prefix = "file://localhost/"
            if decoded.startswith(prefix):
                decoded = decoded[len(prefix):]
            file_paths[file_id] = decoded.replace("/", "\\")

    tracks = sequence.findall("media/audio/track")
    track_index = args_ns.track - 1
    if track_index < 0 or track_index >= len(tracks):
        raise RuntimeError(f"Audio track {args_ns.track} not found")

    clips: list[tuple[str, float, float, float, float]] = []
    for clip in tracks[track_index].findall("clipitem"):
        if clip.findtext("enabled", "TRUE").upper() == "FALSE":
            continue
        file_el = clip.find("file")
        if file_el is None:
            continue
        source = file_paths.get(file_el.get("id", ""))
        if not source:
            continue
        start_frame = int(clip.findtext("start", "0"))
        end_frame = int(clip.findtext("end", "0"))
        ticks_in = clip.findtext("pproTicksIn")
        ticks_out = clip.findtext("pproTicksOut")
        if ticks_in is not None and ticks_out is not None:
            source_in = int(ticks_in) / TICKS_PER_SECOND
            source_out = int(ticks_out) / TICKS_PER_SECOND
        else:
            source_in = int(clip.findtext("in", "0")) / fps
            source_out = int(clip.findtext("out", "0")) / fps
        timeline_start = start_frame / fps
        timeline_duration = (end_frame - start_frame) / fps
        clips.append((source, source_in, source_out, timeline_start, timeline_duration))

    if not clips:
        raise RuntimeError("No usable audio clips found")
    if args_ns.dry_run:
        print(f"clips={len(clips)} fps={fps:.6f} track={args_ns.track}")
        return

    command = ["ffmpeg", "-y"]
    filters: list[str] = []
    labels: list[str] = []
    for index, (source, source_in, source_out, timeline_start, timeline_duration) in enumerate(clips):
        command += ["-ss", f"{source_in:.9f}", "-to", f"{source_out:.9f}", "-i", source]
        delay_ms = round(timeline_start * 1000)
        labels.append(f"a{index}")
        filters.append(
            f"[{index}:a]atrim=duration={timeline_duration:.9f},asetpts=PTS-STARTPTS,"
            f"aresample=16000,pan=mono|c0=0.5*c0+0.5*c1,adelay={delay_ms}:all=1[a{index}]"
        )

    mix_inputs = "".join(f"[{label}]" for label in labels)
    filters.append(f"{mix_inputs}amix=inputs={len(labels)}:normalize=0:dropout_transition=0[out]")
    filter_path = args_ns.wav_path.with_suffix(".filter.txt")
    filter_path.write_text(";\n".join(filters), encoding="utf-8")
    command += [
        "-filter_complex_script",
        str(filter_path),
        "-map",
        "[out]",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(args_ns.wav_path),
    ]
    subprocess.run(command, check=True)
    print(f"clips={len(clips)} fps={fps:.6f} wav={args_ns.wav_path}")


if __name__ == "__main__":
    main()
