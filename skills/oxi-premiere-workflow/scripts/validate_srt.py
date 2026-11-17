import argparse
import json
import re
import sys
from pathlib import Path


TIME_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s+-->\s+"
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})$"
)


def milliseconds(parts: tuple[str, ...]) -> int:
    h, m, s, ms = (int(value) for value in parts)
    return (((h * 60) + m) * 60 + s) * 1000 + ms


WORD_RE = re.compile(r"[^\W_]+", re.UNICODE)


def words(text: str) -> list[str]:
    """Lower-case words without punctuation; diacritics are kept."""
    return [w.casefold() for w in WORD_RE.findall(text)]


def verbatim_errors(cue_texts: list[str], transcript: str) -> list[str]:
    """Verbatim mode only: the cues, read in order, must carry exactly the
    transcript's words. Regrouping may move line and cue breaks, never words
    (idea from VideoLingo's split-then-map-back check, adopted 2026-11-16)."""
    import difflib

    got = words(" ".join(cue_texts))
    want = words(transcript)
    if got == want:
        return []
    errors = []
    matcher = difflib.SequenceMatcher(a=want, b=got, autojunk=False)
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            continue
        context = " ".join(want[max(0, a0 - 3):a0])
        errors.append(
            f"verbatim {tag} after '{context}': transcript {' '.join(want[a0:a1])!r}"
            f" vs SRT {' '.join(got[b0:b1])!r}"
        )
        if len(errors) >= 20:
            errors.append("verbatim: more differences omitted")
            break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate UTF-8 SRT structure and timing.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--max-lines", type=int, default=2)
    parser.add_argument(
        "--verbatim",
        type=Path,
        help="UTF-8 transcript the cues must reproduce word for word (verbatim captions only; "
        "never for Oxi's condensed sub)",
    )
    args = parser.parse_args()

    text = args.path.read_text(encoding="utf-8-sig").strip()
    blocks = re.split(r"\r?\n\s*\r?\n", text) if text else []
    errors: list[str] = []
    previous_end = 0
    last_end = 0
    cue_texts: list[str] = []

    for expected, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if len(lines) < 3:
            errors.append(f"cue {expected}: incomplete block")
            continue
        if lines[0].strip() != str(expected):
            errors.append(f"cue {expected}: numbering is {lines[0].strip()!r}")
        match = TIME_RE.match(lines[1].strip())
        if not match:
            errors.append(f"cue {expected}: invalid timecode")
            continue
        start = milliseconds(match.groups()[:4])
        end = milliseconds(match.groups()[4:])
        if end <= start:
            errors.append(f"cue {expected}: non-positive duration")
        if start < previous_end:
            errors.append(f"cue {expected}: overlaps previous cue")
        if len(lines[2:]) > args.max_lines:
            errors.append(f"cue {expected}: {len(lines[2:])} text lines")
        cue_texts.append(" ".join(lines[2:]))
        previous_end = end
        last_end = end

    if args.verbatim:
        errors.extend(verbatim_errors(cue_texts, args.verbatim.read_text(encoding="utf-8-sig")))

    result = {
        "path": str(args.path),
        "cues": len(blocks),
        "last_end_ms": last_end,
        "errors": errors,
        "valid": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
