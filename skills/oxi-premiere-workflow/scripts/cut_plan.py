"""Turn rough selections into a cut plan whose edges are measured off the waveform.

Usage:
    python cut_plan.py --spec spec.json --out plan.json [--no-tighten]

The rough selections only have to be close: this walks each boundary onto the
real edge of the speech, pads it asymmetrically, refuses to let the padding
touch a neighbouring word, and optionally tightens the pauses that sit inside a
long take.  The output is the `plan` argument for `pr_assemble_edit`.

Three passes:
  1. measure every selection's real onset and offset in its own source file;
  2. share the silence when two selections sit close together;
  3. tighten interior pauses (the "khoang tho" pass), kept separate from any
     content decision.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _edl_common import FRAME, Spec  # noqa: E402


def build(spec, tighten_on=True):
    opt = spec.opt
    LEAD, TRAIL, MIDCUT = opt["lead"], opt["trail"], opt["midcut"]
    GUARD = opt["guard"]
    HOLD = int(round(opt["sil_hold"] / FRAME))
    SEL = spec.selections

    def find_onset(fi, s, floor_s):
        """Where the wanted speech really starts, as (time, lead_to_use)."""
        db, thr = spec.db[fi]
        i = min(len(db) - 1, max(0, int(round(s / FRAME))))
        lo = max(int(round(floor_s / FRAME)), i - int(round(opt["head_back"] / FRAME)), 0)
        if db[i] >= thr:                      # s landed inside a word: back up
            j = i
            while j > lo and (db[max(lo, j - HOLD):j] >= thr).any():
                j -= 1
            if j > lo:
                return j * FRAME, LEAD
            # No pause within reach - this is a deliberate mid-flow cut, so put
            # the splice on the least audible frame around it.  The window
            # reaches forward too: the dip between two syllables often sits just
            # past where the selection began.
            k = max(lo, i - 20)
            w = db[k:min(len(db), i + 16)]
            return (k + int(np.argmin(w))) * FRAME, MIDCUT
        hi = min(len(db) - 1, i + int(round(opt["head_fwd"] / FRAME)))
        j = i
        while j < hi and db[j] < thr:         # s landed in silence: skip dead air
            j += 1
        if db[j] >= thr:
            return j * FRAME, LEAD
        return i * FRAME, 0.0                 # only silence ahead: leave it alone

    def find_offset(fi, e, ceil_s):
        """Where the wanted speech really ends, as (time, trail_to_use)."""
        db, thr = spec.db[fi]
        i = min(len(db) - 1, max(0, int(round(e / FRAME))))
        hi = min(int(round(ceil_s / FRAME)), i + int(round(opt["tail_fwd"] / FRAME)),
                 len(db) - 1)
        if db[i] >= thr:                      # still talking: run on to the pause
            j = i
            while j < hi and (db[j + 1:min(hi, j + HOLD) + 1] >= thr).any():
                j += 1
            if j < hi:
                return j * FRAME, TRAIL
            k = min(len(db) - 1, i + 30)
            return (i + int(np.argmin(db[i:k]))) * FRAME, MIDCUT
        lo = max(0, i - int(round(opt["tail_back"] / FRAME)))
        j = i
        while j > lo and db[j] < thr:         # e landed in silence: drop dead air
            j -= 1
        if db[j] >= thr:
            return j * FRAME, TRAIL
        return i * FRAME, 0.0                 # only silence behind: leave it alone

    def room_before(fi, onset):
        db, thr = spec.db[fi]
        i = min(len(db) - 1, max(0, int(round(onset / FRAME))))
        j, lo = i - 1, max(0, i - int(round((LEAD + 0.5) / FRAME)))
        while j > lo and db[j] < thr:
            j -= 1
        return max(0.0, (i - j) * FRAME - GUARD) if j > lo else float("inf")

    def room_after(fi, offset):
        db, thr = spec.db[fi]
        i = min(len(db) - 1, max(0, int(round(offset / FRAME))))
        j = i + 1
        hi = min(len(db) - 1, i + int(round((TRAIL + 0.5) / FRAME)))
        while j < hi and db[j] < thr:
            j += 1
        return max(0.0, (j - i) * FRAME - GUARD) if j < hi else float("inf")

    # --- pass 1 -----------------------------------------------------------
    marks, prev_e = [], None
    for i, (s, e, label) in enumerate(SEL):
        if e <= s:
            raise ValueError("empty selection: " + label)
        if prev_e is not None and s < prev_e:
            raise ValueError("overlap/out-of-order: " + label)
        prev_e = e
        fi, off = spec.which(s)
        fj, _ = spec.which(e - 1e-6)
        if fi != fj:
            raise ValueError("selection straddles a source boundary: " + label)
        clip = spec.clips[fi]
        dur = clip["end"] - clip["start"]
        src_s, src_e = s - off, e - off
        # A hunt may never cross the midpoint of the gap to a neighbouring
        # selection; that is what stops two selections snapping onto the same
        # speech run.
        floor_s = 0.0
        if i > 0 and spec.which(SEL[i - 1][1] - 1e-6)[0] == fi:
            floor_s = (SEL[i - 1][1] + s) / 2.0 - off
        ceil_s = dur
        if i + 1 < len(SEL) and spec.which(SEL[i + 1][0])[0] == fi:
            ceil_s = (e + SEL[i + 1][0]) / 2.0 - off
        onset, lead = find_onset(fi, src_s, max(0.0, floor_s))
        offset, trail = find_offset(fi, src_e, min(dur, ceil_s))
        # Padding is allowed to eat silence, never a neighbouring word.
        lead = min(lead, room_before(fi, onset))
        trail = min(trail, room_after(fi, offset))
        marks.append({"fi": fi, "item": clip["item"], "label": label,
                      "onset": onset, "lead": lead,
                      "offset": offset, "trail": trail, "dur": dur})

    # --- pass 2 -----------------------------------------------------------
    for a, b in zip(marks, marks[1:]):
        if a["fi"] != b["fi"]:
            continue
        gap = b["onset"] - a["offset"]
        if gap < 0:
            raise ValueError("selections overlap after snapping: " + b["label"])
        want = a["trail"] + b["lead"]
        if want > 0 and gap < want:            # not enough silence for both
            share = gap / want
            a["trail"] *= share
            b["lead"] *= share
    marks[0]["lead"] = min(marks[0]["lead"], marks[0]["onset"])
    for m in marks:
        m["trail"] = min(m["trail"], m["dur"] - m["offset"])

    # --- pass 3 -----------------------------------------------------------
    def tighten(fi, a, b):
        """Split [a,b] into sub-ranges with every long interior pause shortened."""
        v = spec.voiced(fi, a, b)
        runs, j = [], 0
        while j < len(v):
            if v[j]:
                j += 1
                continue
            k = j
            while k < len(v) and not v[k]:
                k += 1
            # Interior only.  A run touching either end is the lead/trail
            # padding, which pass 1 already sized on purpose.
            if j > 0 and k < len(v) and (k - j) * FRAME >= opt["min_pause"]:
                runs.append((a + j * FRAME, a + k * FRAME))
            j = k
        if not runs:
            return [(a, b)], 0.0
        out, cur = [], a
        for ps, pe in runs:
            out.append((cur, ps + opt["keep_pause"] / 2.0))
            cur = pe - opt["keep_pause"] / 2.0
        out.append((cur, b))
        # A piece this short cannot hold a whole word: it is the decay of a
        # neighbour the selection did not want.  Dropping it beats shipping a
        # six-frame clip.
        out = [p for p in out if p[1] - p[0] >= opt["min_part"]]
        if not out:
            return [(a, b)], 0.0
        return out, (b - a) - sum(p[1] - p[0] for p in out)

    plan, rows, total, saved, n_tight = [], [], 0.0, 0.0, 0
    for m in marks:
        src_in = round(m["onset"] - m["lead"], 3)
        src_out = round(m["offset"] + m["trail"], 3)
        if tighten_on and opt.get("tighten", True):
            parts, got = tighten(m["fi"], src_in, src_out)
        else:
            parts, got = [(src_in, src_out)], 0.0
        if len(parts) > 1 or got > 0:
            n_tight += len(parts) - 1
            saved += got
        for pi, (pa, pb) in enumerate(parts):
            pa, pb = round(pa, 3), round(pb, 3)
            if pb <= pa:
                raise ValueError("degenerate part in " + m["label"])
            total += pb - pa
            # Only the first piece carries the real marker; the rest are the
            # same sentence continuing across a tightened breath.
            mk = m["label"] if pi == 0 else m["label"][:44] + " ~"
            plan.append({"item": m["item"], "in": pa, "out": pb,
                         "butt": True, "marker": mk})
        rows.append((m["label"], src_in, src_out, sum(p[1] - p[0] for p in parts),
                     len(parts), got))
    return plan, rows, total, saved, n_tight


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", default="plan.json")
    ap.add_argument("--no-tighten", action="store_true",
                    help="skip the breathing pass (keep selections whole)")
    a = ap.parse_args()

    spec = Spec(a.spec)
    print(spec.describe())
    print()
    plan, rows, total, saved, n_tight = build(spec, not a.no_tighten)

    print("%-56s %8s %8s %7s %4s %6s"
          % ("selection", "in", "out", "kept", "prt", "saved"))
    for label, si, so, kept, nparts, got in rows:
        print("%-56s %8.2f %8.2f %7.2f %4d %6.2f"
              % (label[:56], si, so, kept, nparts, got))
    print()
    print("clips: %d  total: %.2fs (%d:%05.2f)"
          % (len(plan), total, int(total // 60), total % 60))
    print("breathing pass: %d splices, %.2fs of pause removed" % (n_tight, saved))

    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=1)
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
