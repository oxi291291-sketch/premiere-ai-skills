#!/usr/bin/env python3
"""Create preserved per-cut visual evidence and a conservative listening checklist."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from array import array
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline_view import audio_samples, duration, svg_view  # noqa: E402


def read_cuts(path: Path) -> list[float]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return [float(row.get("time", row.get("seconds", ""))) for row in rows]
    data: Any = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, list):
        return [float(item["time"] if isinstance(item, dict) else item) for item in data]
    if isinstance(data, dict) and isinstance(data.get("cuts"), list):
        return [float(item["time"] if isinstance(item, dict) else item) for item in data["cuts"]]
    if isinstance(data, dict) and isinstance(data.get("ranges"), list):
        cuts, elapsed = [], 0.0
        ranges = data["ranges"]
        for item in ranges[:-1]:
            elapsed += float(item["end"]) - float(item["start"])
            cuts.append(elapsed)
        return cuts
    raise ValueError("unsupported cuts JSON schema")


def rms(values: array) -> float:
    return math.sqrt(sum(float(value) ** 2 for value in values) / max(1, len(values))) / 32768.0


def discontinuity(video: Path, cut: float, span: float = 0.05, rate: int = 16000) -> dict[str, Any]:
    samples = audio_samples(video, max(0.0, cut - span), cut + span, rate)
    middle = len(samples) // 2
    before, after = samples[:middle], samples[middle:]
    jump = abs((before[-1] if before else 0) - (after[0] if after else 0)) / 32768.0
    left_rms, right_rms = rms(before), rms(after)
    flagged = jump >= 0.18 and jump >= 2.5 * max(0.01, min(left_rms, right_rms))
    return {"sample_jump": round(jump, 6), "rms_before": round(left_rms, 6), "rms_after": round(right_rms, 6), "listen_flag": flagged}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="Review export from the edited output timeline")
    parser.add_argument("cuts", type=Path, help="JSON/CSV output-timeline cut times")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--window", type=float, default=3.0, help="Total seconds around each cut")
    parser.add_argument("--frames", type=int, default=6)
    args = parser.parse_args()
    if not args.video.exists() or not args.cuts.exists():
        parser.error("video and cuts file must exist")
    total = duration(args.video)
    cuts = sorted(set(time for time in read_cuts(args.cuts) if 0.0 < time < total))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for index, cut in enumerate(cuts, 1):
        view = args.output_dir / f"cut_{index:03d}_{cut:.3f}s.svg"
        view.write_text(svg_view(args.video, cut - args.window / 2, cut + args.window / 2, args.transcript, max(2, args.frames), f"Cut {index} at {cut:.3f}s"), encoding="utf-8")
        record = {"index": index, "time": cut, "view": view.name, **discontinuity(args.video, cut), "status": "needs-listening", "notes": ""}
        records.append(record)

    json_path = args.output_dir / "cut_qc.json"
    csv_path = args.output_dir / "cut_qc.csv"
    md_path = args.output_dir / "cut_qc.md"
    json_path.write_text(json.dumps({"schema": 1, "video": str(args.video.resolve()), "cuts": records}, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()) if records else ["index", "time", "view", "status", "notes"])
        writer.writeheader()
        writer.writerows(records)
    lines = ["# Cut-boundary QC", "", "Every boundary requires listening. A metric flag is not proof of a bad cut.", "", "| Cut | Time | Signal flag | Evidence | Status |", "|---:|---:|:---:|---|---|"]
    for record in records:
        lines.append(f"| {record['index']} | {record['time']:.3f}s | {'CHECK' if record['listen_flag'] else '-'} | [{record['view']}]({record['view']}) | needs-listening |")
    lines.extend(["", "Check clipped phonemes, grammar, repetition, missing reactions, picture jumps, A/V sync, captions, and clicks. Stop after three correction-and-QC passes and keep the safer longer edit when uncertain."])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"cuts": len(records), "output_dir": str(args.output_dir), "signal_flags": sum(1 for row in records if row["listen_flag"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
