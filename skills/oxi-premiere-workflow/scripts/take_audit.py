"""Take-selection audit.

Doi chieu mot cut plan voi transcript nguon de tra loi mot cau hoi duy nhat:
voi moi doan da giu, co lan doc lai NAO O SAU trong cung file nguon khong?

Ly do ton tai: quy tac "uu tien take cuoi" da nam trong dialogue-editing.md tu
2026-07-21 va van bi vi pham (Product C / C0001 "feature X", 2026-08-27: giu take 1
trong khi nguoi doc dung o take 8). Van xuoi khong chan duoc loi nay; can mot
buoc kiem tra co ket qua PASS/FAIL.

Cach dung:
    python take_audit.py --plan plan.json --asr asr_dir [--out report.json]
                         [--threshold 0.72] [--min-words 3]

plan.json: list cac phan tu {"item": "<ten file nguon>", "inp": <giay>,
"out": <giay>}; khoa "item" duoc khop voi <asr_dir>/<item>.json (bo duoi file).

asr_dir: cac file JSON Whisper co "segments" voi start/end/text.

Thoat 0 khi khong con co canh bao nao, 1 khi con - de dung lam cong tac chan
truoc khi ap plan vao Premiere.
"""

import argparse
import difflib
import json
import os
import re
import sys
import unicodedata

_TONE = re.compile(r"[\u0300-\u036f]")


def norm(text):
    """Bo dau, bo dau cau, gom khoang trang. Giup khop ca ASR sai chinh ta."""
    s = unicodedata.normalize("NFD", text or "").lower()
    s = _TONE.sub("", s)
    s = s.replace("\u0111", "d")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_segments(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    segs = data.get("segments") if isinstance(data, dict) else data
    out = []
    for s in segs or []:
        txt = (s.get("text") or "").strip()
        if txt:
            out.append({"start": float(s["start"]), "end": float(s["end"]), "text": txt})
    out.sort(key=lambda s: s["start"])
    return out


def text_between(segs, t0, t1):
    """Loi thoai co giao voi [t0, t1]."""
    parts = [s["text"] for s in segs if s["end"] > t0 and s["start"] < t1]
    return " ".join(parts).strip()


def windows(segs, lo, hi, target_words):
    """Sinh cac cua so segment lien tiep co do dai tu tuong duong doan da giu."""
    n = len(segs)
    for i in range(n):
        if segs[i]["start"] >= hi:
            break
        words = 0
        for j in range(i, n):
            if segs[j]["start"] < lo:
                break
            words += len(norm(segs[j]["text"]).split())
            yield i, j, segs[i]["start"], segs[j]["end"]
            if words >= target_words * 2 + 4:
                break


def audit(plan, asr_dir, threshold, min_words):
    cache = {}
    findings = []
    for idx, entry in enumerate(plan):
        item = str(entry.get("item", ""))
        stem = os.path.splitext(item)[0]
        path = os.path.join(asr_dir, stem + ".json")
        if not os.path.exists(path):
            findings.append({"index": idx, "item": item, "status": "NO_TRANSCRIPT"})
            continue
        if stem not in cache:
            cache[stem] = load_segments(path)
        segs = cache[stem]

        t0 = float(entry.get("inp", entry.get("in", 0.0)))
        t1 = float(entry.get("out", 0.0))
        kept = norm(text_between(segs, t0, t1))
        kw = kept.split()
        if len(kw) < min_words:
            continue

        later = []
        seen = set()
        # chi soi phan nguon nam SAU doan da giu
        for i, j, ws, we in windows(segs, t1, float("inf"), len(kw)):
            if ws < t1 - 0.001:
                continue
            cand = norm(" ".join(s["text"] for s in segs[i:j + 1]))
            if not cand:
                continue
            ratio = difflib.SequenceMatcher(None, kept, cand).ratio()
            if ratio >= threshold:
                key = (round(ws, 2), round(we, 2))
                if key in seen:
                    continue
                seen.add(key)
                later.append({"start": ws, "end": we, "ratio": round(ratio, 3),
                              "text": " ".join(s["text"] for s in segs[i:j + 1]).strip()})
        if not later:
            continue
        later.sort(key=lambda h: (-h["ratio"], h["start"]))
        best = later[:3]
        findings.append({
            "index": idx, "item": item, "kept_in": t0, "kept_out": t1,
            "kept_text": text_between(segs, t0, t1),
            "status": "LATER_TAKE_EXISTS",
            "later_attempts": best,
            "last_attempt_start": max(h["start"] for h in later),
        })
    return findings


def main():
    ap = argparse.ArgumentParser(description="Kiem tra plan co giu nham take dau khong.")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--asr", required=True)
    ap.add_argument("--out")
    ap.add_argument("--threshold", type=float, default=0.72)
    ap.add_argument("--min-words", type=int, default=3)
    args = ap.parse_args()

    with open(args.plan, encoding="utf-8") as fh:
        plan = json.load(fh)
    if isinstance(plan, dict):
        plan = plan.get("clips") or plan.get("plan") or []

    findings = audit(plan, args.asr, args.threshold, args.min_words)
    flagged = [f for f in findings if f["status"] == "LATER_TAKE_EXISTS"]
    missing = [f for f in findings if f["status"] == "NO_TRANSCRIPT"]

    for f in flagged:
        print("FLAG #%d %s  giu %.2f-%.2f  %s" % (
            f["index"], f["item"], f["kept_in"], f["kept_out"], f["kept_text"][:70]))
        for h in f["later_attempts"]:
            print("        lan doc sau  %.2f-%.2f  r=%.2f  %s" % (
                h["start"], h["end"], h["ratio"], h["text"][:70]))
    for f in missing:
        print("NO_TRANSCRIPT #%d %s" % (f["index"], f["item"]))

    print("\n%d doan duoc kiem tra, %d canh bao, %d thieu transcript" % (
        len(plan), len(flagged), len(missing)))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(findings, fh, ensure_ascii=False, indent=1)
        print("report: %s" % args.out)
    return 1 if (flagged or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
