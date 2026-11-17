"""Xuat khung hinh da xu ly cua sequence Premiere qua MCP Bridge, roi do mau.

Vi sao co script nay (Oxi duyet 2026-10-19): moi vong chinh mau truoc day phai
render ca clip bang tab Export (vai chuc giay va nhieu buoc UI) chi de do vai
khung. Tren Premiere 26.3.2 `qeSeq.exportFramePNG` van chay, nhung chi khi:

  1. duong dan dung dau `\\` (dau `/` -> "Unknown error exception");
  2. khong ghi duoi `.png` (Premiere tu gan them: `b.png` -> `b.png.png`);
  3. cho file xuat hien - ham tra `true` truoc khi file duoc ghi xong.

Khung PNG nay la ket qua xu ly that cua Premiere (LUT, Lumetri tren V4/V5, do
hoa phia tren). Do tren no khop ban render H.264 (Job L / VIDEO EXAMPLE, giay
8.033: am mau giong het, IRE lech <= 0.2). PNG la RGB full range nen KHONG thay
duoc sieu trang/sieu den: kiem dai hop le (ILLEGAL_*) van can ban render cuoi.

Cach dung:
    python pr_export_frames.py --sequence "VIDEO EXAMPLE_COLOR_REVIEW" \\
        --at 0.533,3.033,8.033 --out <job>/color/frames_v5 [--measure]
        [--neutral x,y,w,h] [--skin x,y,w,h] [--timeout 30]

    --at       thoi diem tren sequence (giay); hoac --samples N chia deu.
    --sequence ten sequence phai dang mo; khac thi dung, khong xuat.
    --measure  do tung khung bang color_scopes.py, ghi scopes_NN.png va
               frames.json (ket qua do nam trong "measure").

Dau phat duoc tra ve cho cu sau khi xuat. Khong ghi de file da co.
Thoat 0 khi moi khung da xuat (va do neu co --measure), 1 khi co khung loi.
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def js_str(s):
    """Chuoi ExtendScript an toan: thoat `\\` va `"`, ky tu ngoai ASCII -> \\uXXXX
    (duong dan co chu Viet bi hong neu de nguyen, xem premiere-mcp.md)."""
    out = []
    for ch in str(s):
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ord(ch) < 32 or ord(ch) > 126:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def frame_base(out_dir, idx, t):
    """Duong dan goc (khong duoi, dau `\\`) dua cho exportFramePNG."""
    name = "frame_%02d_%07.3fs" % (idx, t)
    return os.path.normpath(os.path.join(os.path.abspath(out_dir), name)).replace("/", "\\")


def written_file(base):
    """File Premiere da ghi cho `base`: thuong la base + '.png'."""
    for cand in (base + ".png", base):
        if os.path.isfile(cand) and os.path.getsize(cand) > 0:
            return cand
    return None


def sample_times(start, end, n):
    n = max(1, n)
    span = end - start
    return [round(start + span * (i + 0.5) / n, 3) for i in range(n)]


def jsx_info():
    return """
var seq = app.project.activeSequence;
if (!seq) return __error("no active sequence");
var v1 = seq.videoTracks.numTracks ? seq.videoTracks[0].clips : null;
var lo = 0, hi = seq.end / 254016000000;
if (v1 && v1.numItems) { lo = v1[0].start.seconds; hi = v1[v1.numItems - 1].end.seconds; }
return __result(__kv([["name", __q(seq.name)], ["start", __num(lo)], ["end", __num(hi)],
  ["player", __q(seq.getPlayerPosition().ticks)]]));
"""


def jsx_frame(seq_name, t, base):
    return """
var seq = app.project.activeSequence;
if (!seq || seq.name != %s) return __error("active sequence is not the expected one");
var t = new Time(); t.seconds = %r; seq.setPlayerPosition(t.ticks);
app.enableQE();
var q = qe.project.getActiveSequence(), tc = q.CTI.timecode;
var r = q.exportFramePNG(tc, %s);
return __result(__kv([["timecode", __q(tc)], ["ret", __q(r)]]));
""" % (js_str(seq_name), float(t), js_str(base))


def jsx_restore(ticks):
    return 'var s = app.project.activeSequence; s.setPlayerPosition(%s); return __result(__q("ok"));' % js_str(ticks)


def wait_file(base, timeout):
    start, last = time.time(), -1
    while time.time() - start < timeout:
        f = written_file(base)
        if f:
            size = os.path.getsize(f)
            if size == last:
                return f
            last = size
        time.sleep(0.5)
    return written_file(base)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sequence", required=True)
    ap.add_argument("--at")
    ap.add_argument("--samples", type=int, default=5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--neutral")
    ap.add_argument("--skin")
    ap.add_argument("--timeout", type=float, default=30.0)
    a = ap.parse_args()

    from pr_file_bridge import ok, run
    info = ok(run(jsx_info()))
    if info["name"] != a.sequence:
        raise SystemExit("sequence dang mo la %r, khong phai %r" % (info["name"], a.sequence))
    times = [float(x) for x in a.at.split(",")] if a.at else sample_times(info["start"], info["end"], a.samples)
    for t in times:
        if t < info["start"] or t > info["end"]:
            raise SystemExit("thoi diem %.3fs nam ngoai phan hinh %.3f-%.3fs" % (t, info["start"], info["end"]))
    os.makedirs(a.out, exist_ok=True)

    rows, bad = [], 0
    try:
        for i, t in enumerate(times, 1):
            base = frame_base(a.out, i, t)
            if written_file(base):
                raise SystemExit("da co %s.png; chon thu muc moi, khong ghi de" % base)
            res = run(jsx_frame(a.sequence, t, base))
            f = wait_file(base, a.timeout) if res.get("success") else None
            row = {"t": t, "timecode": (res.get("data") or {}).get("timecode"), "file": f}
            if not f:
                row["error"] = res.get("error") or "Premiere khong ghi file sau %.0fs" % a.timeout
                bad += 1
            rows.append(row)
    finally:
        run(jsx_restore(info["player"]))

    if a.measure:
        import color_scopes as cs
        skin, neutral = cs.parse_box(a.skin), cs.parse_box(a.neutral)
        for i, row in enumerate(rows, 1):
            if not row["file"]:
                continue
            pi = cs.probe(row["file"])
            m, rgb, ire = cs.measure_frame(pi, 0.0, skin, neutral)
            m["t"] = row["t"]
            m["sheet"] = os.path.join(a.out, "scopes_%02d.png" % i)
            cs.scope_sheet(m["sheet"], rgb, ire, m, "%s @ %.3fs (Premiere frame)" % (a.sequence, row["t"]))
            row["measure"] = m

    rep = {"sequence": a.sequence, "frames": rows,
           "note": "PNG la RGB full range: khong kiem duoc ILLEGAL_*; dai hop le kiem tren ban render cuoi"}
    with open(os.path.join(a.out, "frames.json"), "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
