"""Clean-pass gate: block a dialogue cut plan until it is as tight as Oxi's own cuts.

Why this exists: on Product F (2026-10-26) and again on Job E (culture explainer) (2026-11-11)
Oxi recut the assistant's clean pass and removed the same kinds of material
both times, all of it already forbidden by prose in `dialogue-editing.md` 5b
and "Edge margins".  Prose did not stop it; this script does.  It reads the
plan, the source WAVs and the source word timestamps, and flags:

  HEAD      silence before the first word of a piece over --max-head
  TAIL      silence after the last word of a piece over --max-tail
            (both on the skill meter: 10 ms RMS dB, threshold
            p10 + 0.5 * (p90 - p10) of the piece)
  JOIN      silence across a join (tail of one piece + head of the next)
            of --max-join or more, on the floor gate (file p10 + 18 dB)
  PAUSE     a quiet run of --max-pause or more inside a piece: split it
  DANGLING  a piece ends on a lone short burst after a pause: usually the
            first word of the next attempt (`<lời thoại>`)
  EDGE_WORD a piece starts on a warm-up word or ends on a connector
            (`Đây...`, `<lời thoại>`)
  RETRY     two neighbouring clauses with the same frame (same first 3
            words, or same first 2 and same last word): one idea said
            twice in other words; keep the later one
  ECHO      a question answered at once by a clause that repeats its words
            (`<lời thoại>`)

Every flag blocks (exit 1) until it is fixed in the plan or written into the
--accept file with a reason, e.g. {"P12 ECHO": "câu hỏi mở chương, anh muốn giữ"}.
`thì` in mid-sentence is listed as THI for reading but never blocks.

Usage:
    python clean_pass_gate.py --plan plan.json --wav wav_dir --asr asr_dir
        [--shift 0.2] [--accept accept.json] [--out report.json]

wav_dir: <stem>.wav, 16-bit PCM, same time origin as the source.
asr_dir: <stem>.json with word timestamps, either Whisper-shaped
         (segments[].words) or sherpa-shaped (top-level "words").  Sherpa
         word starts run about 0.2 s early: pass --shift 0.2 for them.
Plan rows need item and in/out seconds ("in" or "inp").

Calibration (2026-11-11, Job E (culture explainer), both episodes): Oxi's own cut measured
head 0.10-0.11 s, tail 0.27-0.29 s (median), 2 and 0 joins of 0.5 s or more,
2 and 16 interior runs of 0.36 s or more.  Defaults are set just above the
upper quartile of his cut, so his cut passes the timing checks with only a
few flags left for judgement.
"""
import argparse
import json
import math
import os
import sys
import unicodedata
import wave

WIN = 0.01
HEAD_WORDS = {"đây", "rồi", "thì", "mà", "được", "chính", "à", "ờ", "ừ", "ừm", "ơ"}
TAIL_WORDS = {"thì", "mà", "à", "ờ", "ừ", "ừm"}
QUESTION_WORDS = {"ai", "gì", "sao", "nào", "đâu", "không", "chưa", "nhỉ"}


def low(w):
    return unicodedata.normalize("NFC", w.lower().strip(".,?!:;\"'…"))


def fold(w):
    w = unicodedata.normalize("NFD", w.lower().strip(".,?!:;\"'…"))
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return w.replace("đ", "d")


def load_db(path):
    with wave.open(path, "rb") as wf:
        sr, ch, n = wf.getframerate(), wf.getnchannels(), wf.getnframes()
        raw = wf.readframes(n)
    import array
    a = array.array("h")
    a.frombytes(raw)
    if ch > 1:
        a = a[::ch]
    step = int(sr * WIN)
    out = []
    for i in range(0, len(a) - step + 1, step):
        s = 0.0
        for v in a[i:i + step]:
            s += v * v
        out.append(10 * math.log10(s / step / (32768.0 ** 2) + 1e-12))
    return out


def pct(vals, q):
    v = sorted(vals)
    if not v:
        return -120.0
    k = (len(v) - 1) * q
    f = int(k)
    c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def load_words(path, shift):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    ws = d.get("words")
    if ws is None:
        ws = [w for s in d.get("segments", []) for w in s.get("words", [])]
    out = []
    for w in ws:
        t = (w.get("word") or w.get("text") or "").strip()
        if t:
            out.append((float(w["start"]) + shift, t))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--wav", required=True)
    ap.add_argument("--asr", required=True)
    ap.add_argument("--shift", type=float, default=0.0)
    ap.add_argument("--max-head", type=float, default=0.18)
    ap.add_argument("--max-tail", type=float, default=0.45)
    ap.add_argument("--max-join", type=float, default=0.50)
    ap.add_argument("--max-pause", type=float, default=0.45)
    ap.add_argument("--retry-window", type=float, default=10.0)
    ap.add_argument("--accept")
    ap.add_argument("--out")
    a = ap.parse_args()

    with open(a.plan, encoding="utf-8") as fh:
        plan = json.load(fh)
    accept = {}
    if a.accept:
        with open(a.accept, encoding="utf-8") as fh:
            accept = json.load(fh)

    dbs, floors, words = {}, {}, {}
    pieces = []
    t = 0.0
    for n, p in enumerate(plan, 1):
        stem = os.path.splitext(os.path.basename(p["item"]))[0]
        s, e = float(p.get("in", p.get("inp"))), float(p["out"])
        if stem not in dbs:
            dbs[stem] = load_db(os.path.join(a.wav, stem + ".wav"))
            floors[stem] = pct(dbs[stem], 0.10) + 18.0
            words[stem] = load_words(os.path.join(a.asr, stem + ".json"), a.shift)
        seg = dbs[stem][int(round(s / WIN)):int(round(e / WIN))]
        rec = {"n": n, "item": stem, "in": s, "out": e, "tl": round(t, 2)}
        t += e - s
        if not seg:
            rec.update(head=0, tail=0, qh=0, qt=0, runs=[], last_burst=None, words=[])
            pieces.append(rec)
            continue
        # skill meter: per-piece speech threshold
        p10, p90 = pct(seg, 0.10), pct(seg, 0.90)
        thr = p10 + 0.5 * (p90 - p10)
        loud = [i for i, v in enumerate(seg) if v > thr]
        rec["head"] = loud[0] * WIN if loud else (e - s)
        rec["tail"] = (len(seg) - 1 - loud[-1]) * WIN if loud else (e - s)
        # floor gate: quiet runs
        g = floors[stem]
        on = [v > g for v in seg]
        idx = [i for i, v in enumerate(on) if v]
        if idx:
            rec["qh"], rec["qt"] = idx[0] * WIN, (len(on) - 1 - idx[-1]) * WIN
            runs, start = [], None
            bursts, bstart = [], idx[0]
            for i in range(idx[0], idx[-1] + 2):
                quiet = i > idx[-1] or not on[i]
                if quiet and start is None:
                    start = i
                elif not quiet and start is not None:
                    if (i - start) * WIN >= 0.05:
                        bursts.append((bstart, start))
                        bstart = i
                    if (i - start) * WIN >= 0.25:
                        runs.append((round(s + start * WIN, 2), round((i - start) * WIN, 2)))
                    start = None
            bursts.append((bstart, idx[-1] + 1))
            rec["runs"] = runs
            # last burst after a pause of >= 0.30 s
            if len(bursts) >= 2:
                gap = (bursts[-1][0] - bursts[-2][1]) * WIN
                blen = (bursts[-1][1] - bursts[-1][0]) * WIN
                rec["last_burst"] = (round(gap, 2), round(blen, 2), round(s + bursts[-1][0] * WIN, 2))
            else:
                rec["last_burst"] = None
        else:
            rec.update(qh=e - s, qt=0, runs=[], last_burst=None)
        rec["words"] = [(wt, w) for wt, w in words[stem] if s <= wt < e]
        pieces.append(rec)

    flags = []

    def flag(p, code, msg):
        key = "P%02d %s" % (p["n"], code)
        flags.append({"key": key, "piece": p["n"], "code": code, "tl": p["tl"], "item": p["item"],
                      "msg": msg, "accepted": accept.get(key)})

    for i, p in enumerate(pieces):
        ws = p["words"]
        if p["head"] > a.max_head:
            flag(p, "HEAD", "%.2f s trước chữ đầu (src %.2f)" % (p["head"], p["in"]))
        if p["tail"] > a.max_tail:
            flag(p, "TAIL", "%.2f s sau chữ cuối (src %.2f)" % (p["tail"], p["out"]))
        if i + 1 < len(pieces):
            j = p["qt"] + pieces[i + 1]["qh"]
            if j >= a.max_join:
                flag(p, "JOIN", "nối P%02d→P%02d lặng %.2f s (tl %.2f)" % (p["n"], p["n"] + 1, j, pieces[i + 1]["tl"]))
        for at, dur in p["runs"]:
            if dur >= a.max_pause:
                flag(p, "PAUSE", "lặng %.2f s giữa đoạn tại src %.2f (tl %.2f) — tách đoạn" % (dur, at, p["tl"] + at - p["in"]))
        lb = p.get("last_burst")
        if lb and lb[0] >= 0.30 and lb[1] <= 0.60:
            tail_ws = [w for wt, w in ws if wt >= lb[2] - 0.15]
            if len(tail_ws) <= 1:
                flag(p, "DANGLING", "cụt cuối đoạn: '%s' đứng riêng sau %.2f s lặng (src %.2f)" % (
                    " ".join(tail_ws) or "?", lb[0], lb[2]))
        if ws:
            first, last = low(ws[0][1]), low(ws[-1][1])
            if first in HEAD_WORDS:
                flag(p, "EDGE_WORD", "mở đoạn bằng '%s' (src %.2f)" % (ws[0][1], ws[0][0]))
            if last in TAIL_WORDS:
                flag(p, "EDGE_WORD", "kết đoạn bằng chữ nối '%s' (src %.2f)" % (ws[-1][1], ws[-1][0]))
            for k in range(1, len(ws) - 1):
                if low(ws[k][1]) == "thì":
                    flags.append({"key": "P%02d THI" % p["n"], "piece": p["n"], "code": "THI", "tl": p["tl"],
                                  "item": p["item"], "msg": "'%s thì %s' (src %.2f)" % (
                                      ws[k - 1][1], ws[k + 1][1], ws[k][0]), "accepted": "info"})

    # clauses over the edit, in timeline order: break at a piece edge or a word gap > 0.55 s
    clauses, cur = [], []
    for p in pieces:
        prev = None
        for wt, w in p["words"]:
            tl = p["tl"] + wt - p["in"]
            if cur and (prev is None or wt - prev > 0.55):
                clauses.append(cur)
                cur = []
            cur.append((tl, fold(w), w, p))
            prev = wt
        if cur:
            clauses.append(cur)
            cur = []
    for x, y in zip(clauses, clauses[1:]):
        if y[0][0] - x[-1][0] > a.retry_window or len(x) < 3 or len(y) < 3:
            continue
        fx, fy = [c[1] for c in x], [c[1] for c in y]
        same3 = fx[:3] == fy[:3]
        restart = any(fx[i:i + 3] == fy[:3] and y[0][0] - x[i][0] <= 8.0
                      for i in range(max(1, len(fx) - 12), len(fx) - 2))
        same2_last = fx[:2] == fy[:2] and fx[-1] == fy[-1]
        if fx[-1] in {fold(q) for q in QUESTION_WORDS}:
            grams = {tuple(fx[i:i + 3]) for i in range(len(fx) - 2)}
            if any(tuple(fy[i:i + 3]) in grams for i in range(min(3, len(fy) - 2))):
                flag(x[0][3], "ECHO", "hỏi rồi đáp lặp chữ: '%s' → '%s' (tl %.1f)" % (
                    " ".join(c[2] for c in x[-8:]), " ".join(c[2] for c in y[:6]), x[0][0]))
                continue
        if (same3 or same2_last) and y[0][0] - x[0][0] <= a.retry_window or restart:
            flag(x[0][3], "RETRY", "'%s' ~ '%s' (tl %.1f / %.1f) — giữ lần sau" % (
                " ".join(c[2] for c in x[-10:]), " ".join(c[2] for c in y), x[0][0], y[0][0]))

    blocking = [f for f in flags if f["code"] != "THI" and not f["accepted"]]
    heads = sorted(p["head"] for p in pieces)
    tails = sorted(p["tail"] for p in pieces)
    summary = {"pieces": len(pieces), "seconds": round(t, 2),
               "head_median": round(pct(heads, 0.5), 2), "tail_median": round(pct(tails, 0.5), 2),
               "flags": len([f for f in flags if f["code"] != "THI"]), "blocking": len(blocking)}
    by_code = {}
    for f in flags:
        by_code[f["code"]] = by_code.get(f["code"], 0) + 1
    summary["by_code"] = by_code
    for f in flags:
        state = "INFO" if f["code"] == "THI" else ("OK  " if f["accepted"] else "FLAG")
        print("%s %-14s tl %7.2f  %s %s" % (state, f["key"], f["tl"], f["item"], f["msg"]))
    print(json.dumps(summary, ensure_ascii=False))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "flags": flags}, fh, ensure_ascii=False, indent=1)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
