"""Prove that no cut in a plan chopped a word or swallowed a syllable.

Usage:
    python edge_report.py --spec spec.json --plan plan.json [--expect expect.json]

Two independent checks, because the first one alone is not enough:

  1. MID-WORD - the frame just outside the boundary is still at speech level,
     so the cut landed in the body of a word.  This is measured against the
     real speech level, not the placement gate: the placement gate sits just
     over the noise floor and every word's decay tail crosses it.
  2. SYLLABLE COUNT - Vietnamese is syllable-timed, so each syllable is one
     burst of above-gate frames.  A cut can land in a deep inter-syllable dip,
     pass check 1, and still have removed a whole trailing word.  Counting the
     bursts inside the kept range against the words the line must contain is
     the only thing that catches that.

`--expect` is an optional JSON list, one entry per plan clip, giving the number
of syllables that clip is supposed to contain (or null to skip it).  Without it
the burst counts are printed for a human to compare against the script.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _edl_common import FRAME, Spec, load_plan  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--expect")
    a = ap.parse_args()

    spec = Spec(a.spec)
    plan = load_plan(a.plan)
    expect = json.load(open(a.expect, encoding="utf-8")) if a.expect else None

    bad = 0
    for i, p in enumerate(plan):
        fi = spec.index_of(p["item"])
        db = spec.db[fi][0]
        thr = spec.speech_gate[fi]
        n = len(db)

        def at(t):
            return db[min(n - 1, max(0, int(round(t / FRAME))))]

        # A chop is speech left OUTSIDE the cut, not speech at the boundary
        # itself: a tight head sits right on the first loud frame, and that is
        # correct.  So probe exactly one frame beyond each edge.
        head = at(p["in"] - FRAME)
        tail = at(p["out"])
        marker = p.get("marker", "")
        flags = []
        if head >= thr:
            flags.append("HEAD chopped, %.1f dB outside (speech gate %.1f)" % (head, thr))
        if tail >= thr:
            flags.append("TAIL chopped, %.1f dB outside (speech gate %.1f)" % (tail, thr))

        bursts = spec.bursts(fi, p["in"], p["out"])
        want = expect[i] if expect and i < len(expect) else None
        if want is not None and len(bursts) < want:
            flags.append("only %d syllable bursts, expected %d - a unit was eaten"
                         % (len(bursts), want))

        if flags:
            bad += 1
            print("%-3d %-52s %s" % (i, marker[:52], "; ".join(flags)))
        elif expect is None:
            print("%-3d %-52s %2d bursts  %.2f-%.2f"
                  % (i, marker[:52], len(bursts), p["in"], p["out"]))

    print()
    print("%d of %d clips flagged" % (bad, len(plan)))
    print("A clean edge is not proof of a complete word: read the burst counts "
          "against the line the clip is supposed to say, and listen through "
          "every boundary that carries a number, a unit or a product name.")


if __name__ == "__main__":
    main()
