"""How much of an edit is breathing room still sitting inside a clip.

Usage:
    python pause_budget.py --spec spec.json --plan plan.json [--keep 0.16]

Run this BEFORE agreeing to a target duration.  Trimming edges only touches the
ends of a selection; a pause in the middle of a long take survives untouched,
and this is the whole budget a tightening pass can ever recover.  If the budget
is far below the reduction Oxi asked for, say so and go straight to removing
whole ideas instead of shaving pauses.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _edl_common import FRAME, Spec, hms, load_plan  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--keep", type=float, default=None,
                    help="silence a tightened pause still has to hold")
    a = ap.parse_args()

    spec = Spec(a.spec)
    plan = load_plan(a.plan)
    keep = a.keep if a.keep is not None else spec.opt["keep_pause"]

    rows, total, tl = [], 0.0, 0.0
    for p in plan:
        fi = spec.index_of(p["item"])
        v = spec.voiced(fi, p["in"], p["out"])
        runs, j = [], 0
        while j < len(v):
            if v[j]:
                j += 1
                continue
            k = j
            while k < len(v) and not v[k]:
                k += 1
            # Interior only: a run touching either end is the trimmed padding.
            if j > 0 and k < len(v):
                runs.append((j * FRAME, k * FRAME))
            j = k
        dur = p["out"] - p["in"]
        gain = sum(max(0.0, (e - s) - keep) for s, e in runs)
        if gain > 0.05:
            rows.append((tl, p.get("marker", ""), dur, gain,
                         [(round(s, 2), round(e - s, 2)) for s, e in runs
                          if e - s > keep + 0.05]))
        total += gain
        tl += dur

    print("timeline %.2fs -> reclaimable inside clips: %.2fs (keep %.2fs per pause)"
          % (tl, total, keep))
    print()
    for t, m, dur, g, runs in sorted(rows, key=lambda r: -r[3]):
        print("%-8s %-52s dur %6.2f  gain %5.2f  %s"
              % (hms(t), m[:52], dur, g, runs[:6]))
    print()
    print("Anything beyond this budget has to come out of content, not pauses.")


if __name__ == "__main__":
    main()
