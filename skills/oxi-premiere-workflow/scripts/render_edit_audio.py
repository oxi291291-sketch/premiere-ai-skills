"""Reconstruct the edited audio from a cut plan, without touching Premiere.

Usage:
    python render_edit_audio.py --spec spec.json --plan plan.json --out edited.wav

Retranscribing this file is how the edit is actually verified: a scan over the
cut plan cannot hear a repetition that only exists across a new join, and a
plan that reads correctly can still sound wrong.  Build this, transcribe it,
then run scan_repeats.py on the result.
"""
import argparse
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _edl_common import Spec, load_plan  # noqa: E402


def read_wav(path):
    w = wave.open(path, "rb")
    sr, n, width, ch = (w.getframerate(), w.getnframes(),
                        w.getsampwidth(), w.getnchannels())
    a = np.frombuffer(w.readframes(n), dtype=np.int16)
    w.close()
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1).astype(np.int16)
    return a, sr


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", default="edited.wav")
    a = ap.parse_args()

    spec = Spec(a.spec)
    plan = load_plan(a.plan)

    cache, sr = {}, None
    for c in spec.clips:
        buf, s = read_wav(c["audio"])
        if sr is None:
            sr = s
        elif s != sr:
            raise ValueError("sample-rate mismatch: %s is %d, expected %d"
                             % (c["audio"], s, sr))
        cache[c["item"]] = buf

    parts = []
    for p in plan:
        buf = cache[p["item"]]
        i0, i1 = int(round(p["in"] * sr)), int(round(p["out"] * sr))
        parts.append(buf[max(0, i0):min(len(buf), i1)])
    out = np.concatenate(parts) if parts else np.zeros(0, dtype=np.int16)

    w = wave.open(a.out, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(out.astype(np.int16).tobytes())
    w.close()

    dur = len(out) / float(sr)
    print("%s  %.6fs  %d joins" % (a.out, dur, len(plan)))
    print("Transcribe this file and run scan_repeats.py against the same plan.")


if __name__ == "__main__":
    main()
