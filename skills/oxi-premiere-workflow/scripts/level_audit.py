"""Kiem tra muc thu (level) cua tung doan da giu trong mot cut plan.

Cau hoi duy nhat: trong doan da giu, co tieng noi nao KHONG phai giong thu
tren mic khong?

Quy tac do Oxi chot ngay 2026-09-06 khi nghe ban cat `video 3` (JobN.prproj):
giong nguoi doc chinh tren mic roi vao khoang **-10 dBFS den 0 dBFS**; bat cu
tieng noi nao **duoi -10 dBFS** la tap am - tieng nhac bai ngoai khung hinh,
tieng doc thu duoi hoi, tieng doan phim noi chuyen. Neu ban thu goc cua mot
cau CHI co ban duoi -10 dBFS thi khong duoc tu chon: phai hoi Oxi truoc.

Vi sao can script nay du `dialogue-editing.md` 5c da co doan van "a quiet
waveform pocket ... is usually a prompt": van xuoi khong chan duoc. Ngay
2026-09-06, plan cua `video 3` van giu ban doc ngoai mic cua cau "<loi thoai>"
 (CLIP_3493 55.02-56.46, dinh -18.4 dBFS) trong khi ban
tren mic nam ngay sau no (56.46-58.34, dinh -4.0 dBFS). Doan giu do co dinh
tong the -2.9 dBFS nen kiem tra theo CA DOAN se bo lot: phai do THEO TUNG TU.

Cach dung:
    python level_audit.py --plan plan.json --wav wav_dir --asr asr_dir
                          [--floor -10.0] [--min-run 0.30] [--out report.json]

wav_dir: <stem>.wav, PCM 16-bit, cung goc thoi gian voi file nguon.
asr_dir: <stem>.json kieu Whisper, can word timestamps.

Thoat 0 khi khong con canh bao, 1 khi con - dung lam cong tac chan truoc khi
ap plan vao Premiere, giong `take_audit.py`.
"""

import argparse
import json
import math
import os
import sys
import wave


def load_peaks(path, win=0.01):
    """Tra ve (danh sach dinh dBFS moi khung `win` giay, so khung/giay)."""
    with wave.open(path, "rb") as wf:
        if wf.getsampwidth() != 2:
            raise SystemExit("%s: can PCM 16-bit" % path)
        ch = wf.getnchannels()
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    import struct
    a = struct.unpack("<%dh" % (len(raw) // 2), raw)
    if ch > 1:
        a = [max(a[i:i + ch], key=abs) for i in range(0, len(a), ch)]
    step = max(1, int(sr * win))
    out = []
    for i in range(0, len(a), step):
        m = 0
        for v in a[i:i + step]:
            if v < 0:
                v = -v
            if v > m:
                m = v
        out.append(20.0 * math.log10(m / 32768.0) if m else -99.0)
    return out, 1.0 / win


def peak_db(peaks, fps, t0, t1):
    i0 = max(0, int(t0 * fps))
    i1 = min(len(peaks), int(math.ceil(t1 * fps)))
    return max(peaks[i0:i1]) if i1 > i0 else -99.0


def load_words(path):
    """Danh sach {w, s, e} tu file ASR. Nhan ca 'word/start/end' lan 'w/s/e'."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    segs = data.get("segments") if isinstance(data, dict) else data
    out = []
    for s in segs or []:
        for w in s.get("words") or []:
            txt = (w.get("word") if "word" in w else w.get("w")) or ""
            txt = txt.strip()
            if not txt:
                continue
            st = w.get("start", w.get("s"))
            en = w.get("end", w.get("e"))
            if st is None or en is None:
                continue
            out.append({"w": txt, "s": float(st), "e": float(en)})
    out.sort(key=lambda x: x["s"])
    return out


def entry_span(e):
    return float(e.get("inp", e.get("in"))), float(e["out"])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--wav", required=True, help="thu muc chua <stem>.wav")
    ap.add_argument("--asr", required=True, help="thu muc chua <stem>.json")
    ap.add_argument("--floor", type=float, default=-10.0,
                    help="nguong giong tren mic, dBFS (mac dinh -10)")
    ap.add_argument("--min-run", type=float, default=0.50,
                    help="do dai toi thieu cua mot chuoi tu duoi nguong, giay")
    ap.add_argument("--min-words", type=int, default=2,
                    help="so tu toi thieu trong mot chuoi duoi nguong")
    ap.add_argument("--delta", type=float, default=8.0,
                    help="chuoi phai thap hon muc tren mic cua chinh doan do it nhat bay nhieu dB")
    ap.add_argument("--out")
    a = ap.parse_args()

    with open(a.plan, encoding="utf-8") as fh:
        plan = json.load(fh)
    if isinstance(plan, dict):
        plan = plan.get("clips") or plan.get("entries") or []

    cache = {}
    flags, rows = [], []
    for i, e in enumerate(plan):
        stem = os.path.splitext(os.path.basename(e["item"]))[0]
        t0, t1 = entry_span(e)
        wav = os.path.join(a.wav, stem + ".wav")
        if not os.path.exists(wav):
            rows.append({"i": i, "item": stem, "in": t0, "out": t1,
                         "status": "NO_WAV"})
            continue
        if stem not in cache:
            cache[stem] = (load_peaks(wav), load_words(os.path.join(a.asr, stem + ".json"))
                           if os.path.exists(os.path.join(a.asr, stem + ".json")) else [])
        (peaks, fps), words = cache[stem]
        span_pk = peak_db(peaks, fps, t0, t1)

        inside = [w for w in words if w["e"] > t0 and w["s"] < t1]
        wpk = [(w, peak_db(peaks, fps, max(w["s"], t0), min(w["e"], t1))) for w in inside]

        # Muc tren mic cua chinh doan nay: phan vi 90 cua dinh tung tu.
        # Mot am tiet nhe trong cau van doc to khong phai la giong khac;
        # chi chuoi thap HAN so voi chinh cau do moi la nguon am khac.
        ref = span_pk
        if wpk:
            srt = sorted(p for _, p in wpk)
            ref = srt[min(len(srt) - 1, int(len(srt) * 0.9))]

        low, run = [], []
        for w, pk in wpk:
            if pk < a.floor:
                run.append((w, pk))
            else:
                if run:
                    low.append(run)
                run = []
        if run:
            low.append(run)
        runs = []
        for r in low:
            dur = min(r[-1][0]["e"], t1) - max(r[0][0]["s"], t0)
            top = max(p for _, p in r)
            if dur >= a.min_run and len(r) >= a.min_words and (ref - top) >= a.delta:
                runs.append({"start": round(max(r[0][0]["s"], t0), 3),
                             "end": round(min(r[-1][0]["e"], t1), 3),
                             "peak": round(top, 1), "ref": round(ref, 1),
                             "text": " ".join(w["w"] for w, _ in r)})

        row = {"i": i, "item": stem, "in": t0, "out": t1,
               "span_peak": round(span_pk, 1), "ref": round(ref, 1),
               "words": len(inside), "marker": e.get("marker", "")}
        if span_pk < a.floor:
            # Ca doan nam duoi nguong: khong co giong tren mic nao trong do.
            row["status"] = "SPAN_LOW"
            flags.append(row)
        elif runs:
            row["status"] = "OFF_MIC"
            row["runs"] = runs
            flags.append(row)
        else:
            row["status"] = "OK"
        rows.append(row)

    print("LEVEL AUDIT  nguong giong tren mic >= %.1f dBFS" % a.floor)
    print("%-3s %-14s %-14s %7s %-13s %s" %
          ("#", "file", "in-out", "peak", "trang thai", "marker"))
    for r in rows:
        print("%-3d %-14s %-14s %7s %-13s %s" %
              (r["i"], r["item"], "%.2f-%.2f" % (r["in"], r["out"]),
               r.get("span_peak", "-"), r.get("status", "?"), (r.get("marker") or "")[:38]))
        for run in r.get("runs", []):
            print("      >>> NGOAI MIC %.2f-%.2f dinh %.1f dBFS (cau nay doc o %.1f): %s"
                  % (run["start"], run["end"], run["peak"], run["ref"], run["text"]))

    print()
    if flags:
        print("CANH BAO: %d doan co tieng noi duoi %.1f dBFS." % (len(flags), a.floor))
        print("Doi voi tung cai: tim ban doc cung cau co dinh >= %.1f dBFS trong cung file" % a.floor)
        print("va chuyen sang ban do. Neu KHONG co ban nao dat nguong, PHAI HOI OXI truoc,")
        print("khong duoc tu quyet dinh giu tieng ngoai mic.")
    else:
        print("Khong co doan nao duoi nguong.")

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump({"floor": a.floor, "min_run": a.min_run, "rows": rows},
                      fh, ensure_ascii=False, indent=1)
        print("report: %s" % a.out)

    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
