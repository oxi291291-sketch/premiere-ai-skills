"""Shared pieces for the waveform-measured cut plan tools.

Every boundary in a dialogue edit is decided from the audio envelope, never from
ASR timestamps, so all of these tools start from the same energy curve and the
same per-take speech gate.

Spec file (JSON) shared by the tools:

    {
      "clips": [
        {"item": "000f4303",          # Premiere project-item nodeId or exact name
         "audio": "a0.wav",           # 16-bit PCM WAV of that clip's audio
         "timeline_start": 0.0,       # where the clip sits in the source assembly
         "timeline_end": 236.2}
      ],
      "selections": [[6.60, 13.66, "label"]],   # times in that same assembly
      "options": {"lead": 0.07, "trail": 0.10, "tighten": true}
    }

Paths inside the spec are resolved relative to the spec file. When the source is
one single file, use a single clip with timeline_start 0.
"""
import json
import os
import wave

import numpy as np

FRAME = 0.01      # analysis hop, seconds

DEFAULTS = {
    # Silence kept around the speech, added outside the placement gate.  The
    # gate already sits inside each word's decay, so this pad lands the result
    # at about 0.09 s before the first word and 0.25 s after the last one, the
    # margins of Oxi's own cut (Product F, 2026-10-26).  The result must stay
    # asymmetric: a symmetric margin makes the head late and the tail chopped.
    "lead": 0.07,
    "trail": 0.10,
    "sil_hold": 0.12,   # unbroken sub-threshold audio that counts as a real pause
    "guard": 0.05,      # padding may take silence, never a neighbouring word
    # Hunting a boundary INTO silence only ever throws dead air away, so it can
    # range freely.  Hunting INTO speech drags in words the selection meant to
    # drop, so it is capped hard.
    "head_back": 0.35,
    "head_fwd": 1.00,
    "tail_fwd": 0.50,
    "tail_back": 1.00,
    "midcut": 0.03,     # pad used when the cut has to land inside running speech
    # Breathing pass.
    "min_pause": 0.36,  # an interior pause this long reads as a stall
    "keep_pause": 0.16, # what survives the tightening, split across the splice
    "min_part": 0.40,   # shorter than this is a scrap of a word, not a phrase
    "floor_pct": 5,     # noise floor estimate
    "gate_over_floor": 8.0,     # placement gate, just over the noise floor
    "chop_under_speech": 10.0,  # chop gate, referenced to the real speech level
}


def load_db(path):
    """RMS energy of a WAV in dB, one value per FRAME."""
    w = wave.open(path, "rb")
    sr, n, width, ch = (w.getframerate(), w.getnframes(),
                        w.getsampwidth(), w.getnchannels())
    raw = w.readframes(n)
    w.close()
    if width != 2:
        raise ValueError("%s: expected 16-bit PCM, got %d-bit" % (path, width * 8))
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    hop = int(FRAME * sr)
    m = len(a) // hop
    rms = np.sqrt((a[:m * hop].reshape(m, hop) ** 2).mean(axis=1)) / 32768.0
    return 20 * np.log10(np.maximum(rms, 1e-9))


class Spec(object):
    """A loaded spec: energy curves, speech gates and the timeline->source map."""

    def __init__(self, path):
        self.path = os.path.abspath(path)
        base = os.path.dirname(self.path)
        with open(self.path, encoding="utf-8") as fh:
            raw = json.load(fh)
        self.opt = dict(DEFAULTS)
        self.opt.update(raw.get("options") or {})
        self.selections = [tuple(s) for s in raw.get("selections", [])]
        self.clips = []
        self.db = []
        self.speech_gate = []
        for c in raw["clips"]:
            wav = c["audio"]
            if not os.path.isabs(wav):
                wav = os.path.join(base, wav)
            db = load_db(wav)
            floor = float(np.percentile(db, self.opt["floor_pct"]))
            gate = floor + self.opt["gate_over_floor"]
            self.db.append((db, gate))
            # Two gates, for two different jobs.  The placement gate above sits
            # just over the noise floor so it catches the decay tail of every
            # word, which is what a boundary should be measured against.  It is
            # useless as a chop test: a chop is a boundary landing in the BODY
            # of a word, so that is measured against the actual speech level.
            voiced = db[db >= gate]
            speech = float(np.percentile(voiced, 60)) if len(voiced) else gate
            self.speech_gate.append(speech - self.opt["chop_under_speech"])
            self.clips.append({
                "item": c["item"],
                "audio": wav,
                "start": float(c.get("timeline_start", 0.0)),
                "end": float(c.get("timeline_end", len(db) * FRAME)),
                "floor": floor,
            })

    def describe(self):
        out = []
        for c, (db, thr), sp in zip(self.clips, self.db, self.speech_gate):
            out.append("%-24s %6d frames  floor %6.1f  place gate %6.1f  chop gate %6.1f"
                       % (os.path.basename(c["audio"]), len(db), c["floor"], thr, sp))
        return "\n".join(out)

    def index_of(self, item):
        for i, c in enumerate(self.clips):
            if c["item"] == item:
                return i
        raise KeyError(item)

    def which(self, t):
        """Clip index and its timeline offset for a time in the source assembly."""
        for i, c in enumerate(self.clips):
            if c["start"] <= t < c["end"]:
                return i, c["start"]
        raise ValueError("time %.3f is outside every clip" % t)

    def voiced(self, fi, a, b):
        """Boolean per-frame speech mask for a source range of clip fi."""
        db, thr = self.db[fi]
        i0, i1 = int(round(a / FRAME)), int(round(b / FRAME))
        return db[max(0, i0):max(0, i1)] >= thr

    def bursts(self, fi, a, b):
        """Syllable bursts in a source range, as (start, end) seconds.

        Vietnamese is syllable-timed, so each syllable shows up as one run of
        above-gate frames.  Counting these is the only way to prove a cut did
        not swallow a whole unit: an edge can sit in a deep inter-syllable dip,
        pass a mid-word test, and still have eaten the last word of the line.
        """
        v = self.voiced(fi, a, b)
        out, j = [], 0
        while j < len(v):
            if not v[j]:
                j += 1
                continue
            k = j
            while k < len(v) and v[k]:
                k += 1
            out.append((a + j * FRAME, a + k * FRAME))
            j = k
        return out


def hms(x):
    return "%d:%05.2f" % (int(x // 60), x % 60)


def load_plan(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def plan_bounds(plan):
    """Output-timeline (start, end, marker) for every plan entry."""
    out, t = [], 0.0
    for p in plan:
        d = p["out"] - p["in"]
        out.append((t, t + d, p.get("marker", "")))
        t += d
    return out
