#!/usr/bin/env python3
"""Create a dependency-free SVG filmstrip, waveform, word-label, and silence view."""

from __future__ import annotations

import argparse
import base64
import html
import json
import math
import subprocess
from array import array
from pathlib import Path
from typing import Any


def run_bytes(command: list[str]) -> bytes:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.stdout if result.returncode == 0 else b""


def duration(path: Path) -> float:
    output = run_bytes(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)])
    return float(output.decode("utf-8", "replace").strip())


def frame_jpeg(video: Path, at: float, width: int = 240) -> bytes:
    return run_bytes(["ffmpeg", "-v", "error", "-ss", f"{at:.3f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "mjpeg", "pipe:1"])


def audio_samples(video: Path, start: float, end: float, rate: int = 8000) -> array:
    payload = run_bytes(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", str(video), "-t", f"{max(0.001, end-start):.3f}", "-map", "0:a:0?", "-ac", "1", "-ar", str(rate), "-f", "s16le", "pipe:1"])
    samples = array("h")
    samples.frombytes(payload[: len(payload) - len(payload) % 2])
    return samples


def transcript_words(path: Path | None, start: float, end: float) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    raw = data.get("words", []) if isinstance(data, dict) else []
    if not raw and isinstance(data, dict):
        raw = [word for segment in data.get("segments", []) if isinstance(segment, dict) for word in segment.get("words", [])]
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", item.get("word", ""))).strip()
        try:
            left = float(item.get("start", item.get("start_time")))
            right = float(item.get("end", item.get("end_time", left)))
        except (TypeError, ValueError):
            continue
        if text and right >= start and left <= end:
            result.append({"text": text, "start": left, "end": right})
    return sorted(result, key=lambda item: item["start"])


def fmt_time(seconds: float) -> str:
    minutes, secs = divmod(max(0.0, seconds), 60)
    return f"{int(minutes):02d}:{secs:06.3f}"


def svg_view(video: Path, start: float, end: float, transcript: Path | None = None, frames: int = 6, title: str = "") -> str:
    total = duration(video)
    start = max(0.0, min(start, total))
    end = max(start + 0.001, min(end, total))
    width, frame_h, wave_h = 1440, 150, 210
    margin, top = 24, 64
    inner = width - margin * 2
    times = [start + (end - start) * (i + 0.5) / frames for i in range(frames)]
    frame_w = inner / frames
    words = transcript_words(transcript, start, end)
    samples = audio_samples(video, start, end)
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="520" viewBox="0 0 {width} 520">', '<rect width="100%" height="100%" fill="#11151c"/>']
    heading = title or f"{video.name}  {fmt_time(start)} - {fmt_time(end)}"
    pieces.append(f'<text x="{margin}" y="35" fill="#f5f7fa" font-family="Arial" font-size="20">{html.escape(heading)}</text>')

    for index, at in enumerate(times):
        x = margin + index * frame_w
        jpg = frame_jpeg(video, at, int(frame_w))
        if jpg:
            encoded = base64.b64encode(jpg).decode("ascii")
            pieces.append(f'<image x="{x:.1f}" y="{top}" width="{frame_w-3:.1f}" height="{frame_h}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{encoded}"/>')
        pieces.append(f'<text x="{x+5:.1f}" y="{top+frame_h-8}" fill="white" stroke="black" stroke-width="0.6" font-family="Arial" font-size="13">{fmt_time(at)}</text>')

    wave_top = top + frame_h + 35
    bins = min(inner, 1200)
    values: list[float] = []
    if samples:
        step = max(1, len(samples) // bins)
        for index in range(0, len(samples), step):
            chunk = samples[index:index+step]
            values.append(max((abs(value) for value in chunk), default=0) / 32768.0)
    center = wave_top + wave_h / 2
    if values:
        upper = " ".join(f"{margin+i*inner/max(1,len(values)-1):.1f},{center-value*(wave_h*0.46):.1f}" for i, value in enumerate(values))
        lower = " ".join(f"{margin+i*inner/max(1,len(values)-1):.1f},{center+value*(wave_h*0.46):.1f}" for i, value in reversed(list(enumerate(values))))
        pieces.append(f'<polygon points="{upper} {lower}" fill="#63d4ff" opacity="0.72"/>')
    pieces.append(f'<line x1="{margin}" y1="{center}" x2="{width-margin}" y2="{center}" stroke="#aeb8c5" opacity="0.45"/>')

    for previous, current in zip(words, words[1:]):
        if current["start"] - previous["end"] >= 0.4:
            x = margin + (previous["end"] - start) / (end - start) * inner
            w = (current["start"] - previous["end"]) / (end - start) * inner
            pieces.append(f'<rect x="{x:.1f}" y="{wave_top}" width="{w:.1f}" height="{wave_h}" fill="#ffcc66" opacity="0.16"/>')

    label_y = wave_top + wave_h + 28
    for index, word in enumerate(words):
        x = margin + (word["start"] - start) / (end - start) * inner
        text = html.escape(word["text"][:22])
        y = label_y + (index % 2) * 22
        pieces.append(f'<text x="{x:.1f}" y="{y}" fill="#f5f7fa" font-family="Arial" font-size="12">{text}</text>')
    pieces.append(f'<text x="{margin}" y="505" fill="#97a4b3" font-family="Arial" font-size="12">Shaded bands: transcript silences >= 0.4s. Timestamps are navigation aids; verify by listening.</text>')
    pieces.append("</svg>")
    return "\n".join(pieces)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float)
    parser.add_argument("--window", type=float, help="Use start as center and this total width")
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--frames", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", default="")
    args = parser.parse_args()
    if not args.video.exists():
        parser.error("video does not exist")
    if args.window is not None:
        left, right = args.start - args.window / 2, args.start + args.window / 2
    else:
        left, right = args.start, args.end if args.end is not None else duration(args.video)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg_view(args.video, left, right, args.transcript, max(2, args.frames), args.title), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "start": left, "end": right}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
