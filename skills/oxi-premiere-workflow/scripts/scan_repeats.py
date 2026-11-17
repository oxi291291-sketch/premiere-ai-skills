"""Find stutters, filler and repeated ideas in a reconstructed edit.

Usage:
    python scan_repeats.py --transcript edited.json --plan plan.json

Run this on the transcript of the RECONSTRUCTED audio (render_edit_audio.py),
never on the source transcript: removing content creates new adjacencies, and
the repetition that matters is usually one the edit itself just built across a
join.

Three separate problems live under Oxi's "cau trung lap":

  STUTTER   the same word or short phrase twice back to back, including one
            created by a cut ("<cum tu>" butted against "<cum tu> la...")
  FILLER    a hesitation sound standing alone between two pauses
  DUPLICATE the same selling point landing twice, minutes apart

The transcript must be word-level JSON in Whisper's shape: segments with
`start`, `end`, `text` and a `words` list.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _edl_common import hms, load_plan, plan_bounds  # noqa: E402

FILLER = {"à", "ừ", "ờ", "ừm", "ơ", "ê", "hả", "nhé", "ấy"}
# Words that legitimately double in Vietnamese, or that repeat for emphasis.
DOUBLE_OK = {"rất", "rất rất", "từng", "vừa", "càng", "mỗi", "nào", "ai", "đâu",
             "luôn", "nữa", "xong", "vâng", "dạ", "không", "có"}
STOP = set("""là và của thì mà nó cái các những một có được cho với ra vào lên xuống
đi đến từ trong ngoài trên dưới rất quá cũng đã sẽ đang bị này kia đó ấy nào ai
gì sao thế nên nếu khi lúc để về theo như bằng hay hoặc nhưng còn chỉ vẫn phải
bạn mình tôi chúng ta các bác nha nhé luôn ạ à thôi đây""".split())


def norm(w):
    w = unicodedata.normalize("NFC", w).strip().lower()
    return re.sub(r"[^\w\sàáâãèéêìíòóôõùúýăđĩũơưạ-ỹ]", "", w, flags=re.UNICODE)


def key(txt):
    txt = unicodedata.normalize("NFC", txt).lower()
    ws = re.findall(r"[0-9a-zà-ỹăâêôơưđ]+", txt)
    return set(w for w in ws if w not in STOP and len(w) > 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--jaccard", type=float, default=0.55)
    a = ap.parse_args()

    d = json.load(open(a.transcript, encoding="utf-8"))
    bounds = plan_bounds(load_plan(a.plan))

    def clip_of(x):
        for i, (s, e, m) in enumerate(bounds):
            if s <= x < e:
                return i, m
        return len(bounds) - 1, bounds[-1][2] if bounds else ""

    # Flat word stream: Whisper splits mid-restart as often as at a real break.
    W = []
    for s in d["segments"]:
        for w in s.get("words", []):
            n = norm(w["word"])
            if n:
                W.append({"w": n, "raw": w["word"].strip(),
                          "s": w["start"], "e": w["end"]})

    stut, i = [], 0
    while i < len(W):
        hit = None
        for n in (4, 3, 2, 1):                     # longest repeat wins
            if i + 2 * n > len(W):
                continue
            x = [t["w"] for t in W[i:i + n]]
            y = [t["w"] for t in W[i + n:i + 2 * n]]
            if x != y:
                continue
            gap = W[i + n]["s"] - W[i + n - 1]["e"]
            if gap > 1.2:                          # a real pause: not a stutter
                continue
            if n == 1 and (x[0] in DOUBLE_OK or len(x[0]) > 6):
                continue
            hit = (n, x, gap)
            break
        if hit:
            n, x, gap = hit
            ci, cm = clip_of(W[i]["s"])
            ctx = " ".join(t["raw"] for t in W[max(0, i - 5):i + 2 * n + 5])
            stut.append((W[i]["s"], ci, cm, " ".join(x), gap, ctx))
            i += 2 * n
        else:
            i += 1

    fill = []
    for j, x in enumerate(W):
        if x["w"] not in FILLER:
            continue
        # A tic stands alone between pauses; the same syllable inside a phrase
        # is a word.
        pre = x["s"] - W[j - 1]["e"] if j else 9
        post = W[j + 1]["s"] - x["e"] if j + 1 < len(W) else 9
        if pre < 0.25 and post < 0.25:
            continue
        ci, cm = clip_of(x["s"])
        fill.append((x["s"], ci, cm, x["raw"],
                     " ".join(t["raw"] for t in W[max(0, j - 5):j + 6])))

    S = []
    for s in d["segments"]:
        k = key(s["text"])
        if len(k) >= 4:
            S.append({"s": s["start"], "t": s["text"].strip(), "k": k})
    pairs = []
    for x, y in combinations(range(len(S)), 2):
        kx, ky = S[x]["k"], S[y]["k"]
        j = len(kx & ky) / float(len(kx | ky))
        if j >= a.jaccard:
            pairs.append((j, x, y))
    pairs.sort(reverse=True)

    print("=== STUTTER / RESTART (%d) ===" % len(stut))
    for st, ci, cm, x, gap, ctx in stut:
        print("%s  #%02d %-40s  [%s] gap %.2fs" % (hms(st), ci, cm[:40], x, gap))
        print("        ...%s..." % ctx)

    print("\n=== FILLER (%d) ===" % len(fill))
    for st, ci, cm, x, ctx in fill:
        print("%s  #%02d %-40s  [%s]" % (hms(st), ci, cm[:40], x))
        print("        ...%s..." % ctx)

    print("\n=== REPEATED IDEA (Jaccard >= %.2f): %d pairs ===" % (a.jaccard, len(pairs)))
    for j, x, y in pairs:
        cx, mx = clip_of(S[x]["s"])
        cy, my = clip_of(S[y]["s"])
        print("\n%.2f  %s  #%02d %s" % (j, hms(S[x]["s"]), cx, mx[:44]))
        print("        %s" % S[x]["t"])
        print("      %s  #%02d %s" % (hms(S[y]["s"]), cy, my[:44]))
        print("        %s" % S[y]["t"])

    print("\nA deliberate hook and its payoff will show up here as a duplicate. "
          "Judge each pair, do not cut on the score.")


if __name__ == "__main__":
    main()
