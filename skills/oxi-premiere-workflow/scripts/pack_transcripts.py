#!/usr/bin/env python3
"""Pack common word-level ASR JSON into phrase-level Markdown plus a cache manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_word(item: dict[str, Any], fallback_speaker: str = "") -> dict[str, Any] | None:
    kind = str(item.get("type", "word"))
    if kind in {"spacing", "punctuation"} and not item.get("text") and not item.get("word"):
        return None
    text = str(item.get("text", item.get("word", ""))).strip()
    if not text:
        return None
    start = as_float(item.get("start", item.get("start_time", 0.0)))
    end = as_float(item.get("end", item.get("end_time", start)), start)
    return {
        "text": text,
        "start": start,
        "end": max(start, end),
        "speaker": str(item.get("speaker_id", item.get("speaker", fallback_speaker)) or ""),
        "type": kind,
    }


def extract_words(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("words"), list):
        return [w for item in data["words"] if isinstance(item, dict) if (w := normalize_word(item))]

    words: list[dict[str, Any]] = []
    segments = data.get("segments", []) if isinstance(data, dict) else []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        speaker = str(segment.get("speaker", segment.get("speaker_id", "")) or "")
        segment_words = segment.get("words")
        if isinstance(segment_words, list) and segment_words:
            for item in segment_words:
                if isinstance(item, dict) and (word := normalize_word(item, speaker)):
                    words.append(word)
            continue
        text = str(segment.get("text", "")).strip()
        if text:
            words.append({
                "text": text,
                "start": as_float(segment.get("start")),
                "end": as_float(segment.get("end"), as_float(segment.get("start"))),
                "speaker": speaker,
                "type": "segment",
            })
    return words


def group_phrases(words: list[dict[str, Any]], silence: float) -> list[dict[str, Any]]:
    phrases: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    def flush() -> None:
        if not current:
            return
        text = " ".join(str(w["text"]) for w in current)
        text = text.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
        phrases.append({
            "start": current[0]["start"],
            "end": current[-1]["end"],
            "speaker": current[0]["speaker"],
            "text": text,
            "words": len(current),
        })
        current.clear()

    for word in sorted(words, key=lambda item: (item["start"], item["end"])):
        if current:
            gap = word["start"] - current[-1]["end"]
            speaker_changed = bool(word["speaker"] and current[0]["speaker"] and word["speaker"] != current[0]["speaker"])
            if gap >= silence or speaker_changed:
                flush()
        current.append(word)
    flush()
    return phrases


def resolve_inputs(values: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    for value in values:
        if value.is_dir():
            found.extend(sorted(value.glob("*.json")))
        elif value.is_file():
            found.append(value)
    return list(dict.fromkeys(path.resolve() for path in found))


def media_fingerprint(path: Path | None, include_hash: bool) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    stat = path.stat()
    result: dict[str, Any] = {"path": str(path.resolve()), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    if include_hash:
        result["sha256"] = sha256(path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="Transcript JSON files or directories")
    parser.add_argument("--output", type=Path, required=True, help="Packed Markdown output")
    parser.add_argument("--manifest", type=Path, help="Manifest JSON; defaults beside output")
    parser.add_argument("--silence", type=float, default=0.5, help="Phrase break in seconds")
    parser.add_argument("--media-dir", type=Path, help="Optional source-media directory, matched by stem")
    parser.add_argument("--media-ext", action="append", default=[], help="Allowed source extension; repeatable")
    parser.add_argument("--hash-media", action="store_true", help="Include full SHA-256 of matched media")
    parser.add_argument("--asr-settings", default="", help="Provider/model/language settings recorded in manifest")
    args = parser.parse_args()

    inputs = resolve_inputs(args.inputs)
    if not inputs:
        parser.error("no transcript JSON files found")
    allowed = {ext.lower().lstrip(".") for ext in args.media_ext} or {"mp4", "mov", "mxf", "wav", "mp3", "m4a"}
    markdown = ["# Packed transcript", "", f"Phrase breaks: silence >= {args.silence:.3f}s or speaker change.", ""]
    manifest: dict[str, Any] = {"schema": 1, "silence_seconds": args.silence, "asr_settings": args.asr_settings, "items": []}

    for transcript in inputs:
        data = json.loads(transcript.read_text(encoding="utf-8-sig"))
        words = extract_words(data)
        phrases = group_phrases(words, args.silence)
        markdown.extend([f"## {transcript.stem}", ""])
        for phrase in phrases:
            speaker = f" {phrase['speaker']}" if phrase["speaker"] else ""
            markdown.append(f"- [{phrase['start']:.3f}-{phrase['end']:.3f}]{speaker}: {phrase['text']}")
        markdown.append("")

        media: Path | None = None
        if args.media_dir and args.media_dir.exists():
            media = next((p for p in args.media_dir.iterdir() if p.is_file() and p.stem == transcript.stem and p.suffix.lower().lstrip(".") in allowed), None)
        manifest["items"].append({
            "transcript": str(transcript),
            "transcript_sha256": sha256(transcript),
            "word_entries": len(words),
            "phrases": len(phrases),
            "media": media_fingerprint(media, args.hash_media),
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(markdown), encoding="utf-8")
    manifest_path = args.manifest or args.output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "manifest": str(manifest_path), "files": len(inputs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
