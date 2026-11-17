"""Compare on-screen text with the spoken words and the script, word by word.

    python text_voice_diff.py --texts texts.json [--asr asr.json] [--ref script.md ...]
        [--before 4] [--after 2] [--flicker 0.1] [--out report.json]

Why (Oxi, 2026-11-10, Job J v2 final QC): two text layers shipped to
final review with one wrong tone mark and one wrong letter in otherwise valid words. Both are real Vietnamese syllables, so a
dictionary check passes them. What catches them is the same word, spelled
differently, in what the presenter says (ASR) or in the approved script.

Inputs
  --texts  JSON list (or {"items": [...]}) of {id, start, end, text, track?}
           in sequence seconds, read live from the MOGRT text parameters.
  --asr    Whisper-shaped JSON: {"segments": [{"words": [{word,start,end}]}]}.
           Words starting inside [start - before, end + after] are compared.
  --ref    Script or source text files (md/txt/csv/json). The best-matching
           passage anywhere in them (match ratio >= --min-ref) is compared,
           without timing.

Flags (one per differing word, evidence word and source attached)
  DAU   same letters, different diacritics/tone (thử ↔ thủ)
  GAN   one letter apart once diacritics are removed (cạch ↔ cạnh, nữ ↔ ngữ);
        needs at least 3 letters, so 2-letter pairs (cả ↔ và) stay silent
  KY_TU a character that is not a letter or digit inside a word (t*)
  NHAY  two text clips on one track with a gap of 0 < gap <= --flicker s
        (the text blinks off for a few frames); reported, not gating.

Every DAU/GAN/KY_TU flag must be cleared in writing as: lỗi chữ, ASR/script
sai, or chủ ý. ASR agreeing with the text is not proof the text is right (on
v2 Whisper also heard "<lời thoại>"); the --ref check exists for that case.

Exit 0 when no DAU/GAN/KY_TU flag stands, 1 otherwise, 2 on bad input.
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata

PUNCT = re.compile(r"^[\s\.,;:!?\"'“”‘’()\[\]{}…–—\-/]+|[\s\.,;:!?\"'“”‘’()\[\]{}…–—\-/]+$")


def norm(tok):
    tok = unicodedata.normalize("NFC", tok).lower()
    return PUNCT.sub("", tok)


def tokens(text):
    out = []
    for raw in re.split(r"[\s/]+", text or ""):
        t = norm(raw)
        if t:
            out.append(t)
    return out


def fold(tok):
    tok = tok.replace("đ", "d")
    return "".join(c for c in unicodedata.normalize("NFD", tok) if unicodedata.category(c) != "Mn")


def lev1(a, b):
    """True when a and b differ by exactly one edit."""
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    for i in range(len(b)):
        if a == b[:i] + b[i + 1:]:
            return True
    return False


def classify(t, e):
    if t == e:
        return None
    ft, fe = fold(t), fold(e)
    if ft == fe:
        return "DAU"
    if lev1(ft, fe) and max(len(ft), len(fe)) >= 3:
        return "GAN"
    return None


def compare(text_toks, evid_toks):
    """Align two token lists; return [(kind, text_word, evidence_word)]."""
    sm = difflib.SequenceMatcher(None, [fold(t) for t in text_toks], [fold(t) for t in evid_toks], autojunk=False)
    flags = []
    # exact fold-equal tokens that differ only in diacritics land in 'equal' blocks
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                kind = classify(text_toks[i1 + k], evid_toks[j1 + k])
                if kind:
                    flags.append((kind, text_toks[i1 + k], evid_toks[j1 + k]))
        elif op == "replace":
            # pair each text word with the closest spelling inside the block,
            # not by position: ASR often adds words around the changed one
            for t in text_toks[i1:i2]:
                kinds = [(classify(t, e), e) for e in evid_toks[j1:j2]]
                hit = next((x for x in kinds if x[0] == "DAU"), None) or next((x for x in kinds if x[0] == "GAN"), None)
                if hit:
                    flags.append((hit[0], t, hit[1]))
    return flags, sm.ratio()


def load_items(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    items = data.get("items", data) if isinstance(data, dict) else data
    for i, it in enumerate(items):
        for key in ("start", "end", "text"):
            if key not in it:
                sys.exit("texts item %d has no %r" % (i, key))
        it.setdefault("id", "t%d" % i)
    return items


def load_asr(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    words = []
    for s in data.get("segments", data if isinstance(data, list) else []):
        for w in s.get("words", []):
            for t in tokens(w.get("word", "")):
                words.append((float(w["start"]), t))
    return words


def load_ref(paths):
    toks = []
    for p in paths:
        with open(p, encoding="utf-8", errors="replace") as fh:
            toks += tokens(re.sub(r"<[^>]+>|\\n", " ", fh.read()))
    return toks


def best_ref_window(text_toks, ref, index):
    """Best-matching passage of the reference for these tokens."""
    n = len(text_toks)
    starts = set()
    for k, t in enumerate(text_toks):
        for pos in index.get(fold(t), ()):
            starts.add(max(0, pos - k))
    best = (0.0, None)
    for s in starts:
        win = ref[s:s + n]
        hits = sum(fold(a) == fold(b) for a, b in zip(text_toks, win))
        if hits < max(1, (n + 1) // 2):
            continue
        r = difflib.SequenceMatcher(None, [fold(t) for t in text_toks], [fold(t) for t in win], autojunk=False).ratio()
        exact = sum(a == b for a, b in zip(text_toks, win))
        score = r + 0.001 * exact
        if score > best[0]:
            best = (score, win)
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--texts", required=True)
    ap.add_argument("--asr")
    ap.add_argument("--ref", nargs="*", default=[])
    ap.add_argument("--before", type=float, default=4.0)
    ap.add_argument("--after", type=float, default=2.0)
    ap.add_argument("--flicker", type=float, default=0.1)
    ap.add_argument("--min-ref", type=float, default=0.6, help="minimum match ratio of a script passage")
    ap.add_argument("--out")
    a = ap.parse_args()
    if not a.asr and not a.ref:
        print("give --asr and/or --ref", file=sys.stderr)
        return 2

    items = load_items(a.texts)
    words = load_asr(a.asr) if a.asr else []
    ref = load_ref(a.ref) if a.ref else []
    index = {}
    for pos, t in enumerate(ref):
        index.setdefault(fold(t), []).append(pos)

    flags = []
    for it in items:
        tt = tokens(it["text"])
        if not tt:
            continue
        for t in tt:
            if re.search(r"[^\w,.:%]", t, re.UNICODE):
                flags.append({"kind": "KY_TU", "id": it["id"], "start": it["start"], "text": it["text"],
                              "word": t, "evidence": None, "source": "text"})
        sources = []
        if words:
            lo, hi = it["start"] - a.before, it["end"] + a.after
            sources.append(("asr", [t for s, t in words if lo <= s <= hi]))
        if ref:
            sc, win = best_ref_window(tt, ref, index)
            if win and sc >= a.min_ref:
                sources.append(("ref", win))
        seen = set()
        for src, evid in sources:
            if not evid:
                continue
            fl, _ = compare(tt, evid)
            for kind, w, e in fl:
                if (w, e) in seen:
                    continue
                seen.add((w, e))
                flags.append({"kind": kind, "id": it["id"], "start": it["start"], "text": it["text"],
                              "word": w, "evidence": e, "source": src,
                              "context": " ".join(evid[:40])})

    warn = []
    by_track = {}
    for it in items:
        if "track" in it:
            by_track.setdefault(it["track"], []).append(it)
    for tr, lst in by_track.items():
        lst.sort(key=lambda x: x["start"])
        for p, q in zip(lst, lst[1:]):
            gap = q["start"] - p["end"]
            if 0.0005 < gap <= a.flicker + 1e-6:
                warn.append({"kind": "NHAY", "track": tr, "at": round(p["end"], 3), "gap": round(gap, 3),
                             "from": p["text"], "to": q["text"]})

    def tc(s):
        return "%d:%05.2f" % (s // 60, s % 60)

    for f in sorted(flags, key=lambda f: f["start"]):
        ev = " ~ %s (%s)" % (f["evidence"], f["source"]) if f["evidence"] else ""
        print("%-5s %s %s  \"%s\": %s%s" % (f["kind"], tc(f["start"]), f["id"], f["text"], f["word"], ev))
    for w in warn:
        print("NHAY  %s %s gap %.3fs  \"%s\" -> \"%s\"" % (tc(w["at"]), w["track"], w["gap"], w["from"], w["to"]))
    print("%d text items, %d word flags, %d flicker warnings" % (len(items), len(flags), len(warn)))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"flags": flags, "flicker": warn, "items": len(items)}, fh, ensure_ascii=False, indent=1)
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
