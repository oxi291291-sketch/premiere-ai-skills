#!/usr/bin/env python3
"""Doc footage: bang tong 2 giay, xem day 1 giay, do hinh va mo manifest.

    python segment_sheets.py --from-bin bin_items.json --out <job>/index
    python segment_sheets.py --from-dir D:/job/footage --out <job>/index
    python segment_sheets.py --out <job>/index --detail C9705-03 C9719-01
    python segment_sheets.py --out <job>/index --inspect SOURCE.MP4 --range 9 17 --max-seg 1

Chay o chang 1 (truoc khi len plan cat thoai) cho toan bo footage cua job.
Chang do B-roll chay lai dung lenh do tren bin cua job: file da co trong
manifest voi cung cau hinh duoc giu nguyen; file moi hoac cau hinh doi duoc
index. Mot job, mot manifest. Doc kem references/footage-index.md.

Moi segment len sheet thanh mot hang 3 khung (15% / 50% / 85%) co ghi giay
tren source, de loc noi dung va tim cho can xem ky hon. Anh mau khong chung minh
chuyen dong lien tuc; can xem video de chot diem cat phu thuoc dong tac.

So lieu tu dong (mot lan giai ma moi file, cung luot do chuyen canh):
  luma       do sang trung binh (signalstats YAVG, 0-255)
  blur       do mo (blurdetect, cao = mo hon)
  motion     trung binh scene score, cao = may rung / chuyen dong nhieu
Co `flags` (dark, bright, soft, busy) tinh TUONG DOI trong chinh job nay. Co
chi la goi y de nhin ky hon, khong phai ket luan; mat nguoi van quyet.

--detail ve anh lon 2x2 cho vai segment ung vien (trong khoang best_in-best_out
neu da dien) vao <out>/detail/<id>.jpg, de chon canh cuoi cung o chang B-roll.

Xoay hinh: footage doc client co the nam ngang khong co metadata. Dung --rotate 90
(hoac -90, 180) cho ca job, hoac sua truong `rotate` cua tung source trong
manifest roi chay lai voi --force.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

SCHEMA = 2
FRAMES_AT = (0.15, 0.50, 0.85)      # vi tri 3 khung trong moi segment
DETAIL_AT = (0.10, 0.37, 0.63, 0.90)
STATS_FPS = 2                       # so khung/giay dem so lieu sang/mo
STATS_W = 480                       # be ngang ban do mo; nho qua thi blur vo nghia

# Phan mat nguoi dien. Giu qua moi lan chay lai.
FILLED = {"description": "", "subject": "", "shot": "", "camera": "",
          "energy": None, "usable": True, "uncertain": False,
          "look": None, "best_in": None, "best_out": None, "issues": "",
          "ideas": [], "roles": []}

ROTATE_VF = {0: "", 90: "transpose=1", -90: "transpose=2", 270: "transpose=2",
             180: "hflip,vflip"}


def run(cmd, timeout=900, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          errors="replace", cwd=cwd)


def probe(path):
    """(duration, width, height) cua luong hinh dau tien; 0 neu khong doc duoc."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height:format=duration",
               "-of", "json", path], timeout=60).stdout
    try:
        data = json.loads(out)
        dur = float(data.get("format", {}).get("duration", 0) or 0)
        st = (data.get("streams") or [{}])[0]
        return dur, int(st.get("width") or 0), int(st.get("height") or 0)
    except (ValueError, TypeError, IndexError):
        return 0.0, 0, 0


def have_filter(name):
    out = run(["ffmpeg", "-hide_banner", "-filters"], timeout=60).stdout
    return any(len(p) > 1 and p[1] == name
               for p in (line.split() for line in out.splitlines()))


def font_arg(font):
    """Escape duong dan font cho filtergraph: dau hai cham trong C:/ phai thoat."""
    return font.replace("\\", "/").replace(":", "\\:")


# ------------------------------------------------------- phan tich (mot luot)

def _parse_metadata(path, keys):
    """Doc file metadata=print thanh [(t, {key: float})]."""
    rows, cur = [], None
    if not os.path.exists(path):
        return rows
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line.startswith("frame:") and "pts_time:" in line:
            try:
                cur = (float(line.split("pts_time:")[1].split()[0]), {})
                rows.append(cur)
            except (IndexError, ValueError):
                cur = None
        elif cur is not None and "=" in line:
            k, _, v = line.partition("=")
            if k in keys:
                try:
                    val = float(v)
                    if not math.isnan(val):
                        cur[1][keys[k]] = val
                except ValueError:
                    pass
    return rows


def analyse(path, scene_scale, blur_ok):
    """Mot lan giai ma: scene score moi khung + sang/mo o STATS_FPS.

    Tra ve (scene_rows, stats_rows). File metadata ghi vao thu muc tam va goi
    ffmpeg voi cwd o do, vi duong dan Windows co dau hai cham pha filtergraph.
    """
    tmp = tempfile.mkdtemp(prefix="segan_")
    try:
        stats = "fps=%d,scale=%d:-2,signalstats" % (STATS_FPS, STATS_W)
        if blur_ok:
            stats += ",blurdetect"
        graph = ("[0:v]split=2[a][b];"
                 "[a]scale=%d:-2,select='gte(scene,0)',"
                 "metadata=print:key=lavfi.scene_score:file=scene.txt[o1];"
                 "[b]%s,metadata=print:file=stats.txt[o2]" % (scene_scale, stats))
        run(["ffmpeg", "-hide_banner", "-v", "error", "-i", os.path.abspath(path),
             "-filter_complex", graph, "-map", "[o1]", "-f", "null", "-",
             "-map", "[o2]", "-f", "null", "-"], timeout=3600, cwd=tmp)
        scene = _parse_metadata(os.path.join(tmp, "scene.txt"),
                                {"lavfi.scene_score": "scene"})
        stat = _parse_metadata(os.path.join(tmp, "stats.txt"),
                               {"lavfi.signalstats.YAVG": "luma",
                                "lavfi.blur": "blur"})
        return scene, stat
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def split(duration, cuts, max_seg, min_seg):
    """Bien moc chuyen canh thanh danh sach segment [start, end)."""
    bounds = [0.0]
    bounds += [c for c in cuts if min_seg < c < duration - min_seg]
    bounds += [duration]

    # doan nao dai hon max_seg thi chia deu: take quay tay van doi y hinh khi
    # may lia hoac day vao, nen chia deu la dung chu khong phai bo cuoc
    dense = []
    for lo, hi in zip(bounds, bounds[1:]):
        span = hi - lo
        parts = max(1, math.ceil(span / max_seg)) if span > max_seg else 1
        step = span / parts
        for i in range(parts):
            dense.append((lo + i * step, lo + (i + 1) * step))

    # gop cac manh vun vao segment lien truoc
    merged = []
    for lo, hi in dense:
        if merged and hi - lo < min_seg and hi - merged[-1][0] <= max_seg:
            merged[-1] = (merged[-1][0], hi)
        else:
            merged.append((lo, hi))
    if (len(merged) > 1 and merged[-1][1] - merged[-1][0] < min_seg
            and merged[-1][1] - merged[-2][0] <= max_seg):
        merged[-2] = (merged[-2][0], merged[-1][1])
        merged.pop()
    return merged


def seg_metrics(lo, hi, scene_rows, stat_rows):
    def mean(rows, key):
        vals = [r[key] for t, r in rows if lo <= t < hi and key in r]
        return round(sum(vals) / len(vals), 4) if vals else None
    return {"luma": mean(stat_rows, "luma"), "blur": mean(stat_rows, "blur"),
            "motion": mean(scene_rows, "scene")}


def set_flags(sources):
    """Co tuong doi trong job: so voi trung vi cua chinh bo footage nay."""
    segs = [g for s in sources for g in s["segments"]]

    def dist(key):
        vals = sorted(g["metrics"][key] for g in segs
                      if g.get("metrics") and g["metrics"].get(key) is not None)
        if len(vals) < 4:
            return None, None
        return statistics.median(vals), vals[int(0.85 * (len(vals) - 1))]

    blur_med, blur_hi = dist("blur")
    mot_med, mot_hi = dist("motion")
    for g in segs:
        m, flags = g.get("metrics") or {}, []
        if m.get("luma") is not None and m["luma"] < 45:
            flags.append("dark")
        if m.get("luma") is not None and m["luma"] > 210:
            flags.append("bright")
        if blur_med and m.get("blur") is not None \
                and m["blur"] >= blur_hi and m["blur"] >= 1.3 * blur_med:
            flags.append("soft")
        if mot_med and m.get("motion") is not None \
                and m["motion"] >= mot_hi and m["motion"] >= 2.0 * mot_med:
            flags.append("busy")
        g["flags"] = flags


# ------------------------------------------------------------------------ sheet

def _scale(max_dim):
    """Canh dai nhat = max_dim, giu ty le, ca ngang lan doc."""
    return ("scale='if(gte(iw,ih),%d,-2)':'if(gte(iw,ih),-2,%d)'"
            % (max_dim, max_dim))


def _frame(path, at, dest, max_dim, rotate, font, label):
    vf = ",".join(x for x in (ROTATE_VF.get(rotate, ""), _scale(max_dim)) if x)
    if label and font:
        vf += (",drawtext=fontfile='%s':text='%s':x=6:y=6:fontsize=%d"
               ":fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=4"
               % (font_arg(font), label.replace(":", "\\:"), max(16, max_dim // 18)))
    res = run(["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % at, "-i", path,
               "-frames:v", "1", "-vf", vf, "-q:v", "3", dest], timeout=180)
    if res.returncode != 0 and label and font:
        return _frame(path, at, dest, max_dim, rotate, None, None)
    return res


def _tile(pattern, cols, rows, dest):
    return run(["ffmpeg", "-v", "error", "-y", "-i", pattern,
                "-filter_complex", "tile=%dx%d:padding=4:margin=4" % (cols, rows),
                "-frames:v", "1", "-q:v", "3", dest], timeout=600)


def build_sheets(path, stem, segments, out_dir, rotate, portrait, font, max_dim):
    """Moi segment mot hang 3 khung. Ngang: 1 segment/hang, 6 hang/sheet.
    Doc: 2 segment/hang, 4 hang/sheet. Tra ve [(sheet, row)] theo segment."""
    per_row = 2 if portrait else 1
    rows_max = 4 if portrait else 6
    per_sheet = per_row * rows_max
    pages = [segments[i:i + per_sheet] for i in range(0, len(segments), per_sheet)]
    placed = []
    for page_no, page in enumerate(pages, start=1):
        name = "%s.jpg" % stem if len(pages) == 1 else "%s_p%02d.jpg" % (stem, page_no)
        tmp = tempfile.mkdtemp(prefix="seg_")
        try:
            n = 0
            for i, (lo, hi) in enumerate(page):
                index = (page_no - 1) * per_sheet + i + 1
                for j, frac in enumerate(FRAMES_AT):
                    at = lo + frac * (hi - lo)
                    label = ("%02d  %.1fs" % (index, at)) if j == 0 else "%.1fs" % at
                    _frame(path, at, os.path.join(tmp, "%04d.jpg" % n),
                           max_dim, rotate, font, label)
                    n += 1
                placed.append((name, i // per_row + 1))
            # trang chi co 1 segment doc thi khong ve cot trong ben phai
            cols = min(per_row, len(page)) * len(FRAMES_AT)
            rows = math.ceil(n / cols)
            if n and os.path.exists(os.path.join(tmp, "0000.jpg")):
                _tile(os.path.join(tmp, "%04d.jpg"), cols, rows,
                      os.path.join(out_dir, "sheets", name))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return placed


# ------------------------------------------------------------------------ nguon

def sources_from_bin(bin_path):
    data = json.loads(open(bin_path, encoding="utf-8").read())
    found = []

    def walk(node):
        if isinstance(node, dict):
            media = (node.get("media_path") or node.get("mediaPath")
                     or node.get("path") or node.get("filePath"))
            if isinstance(media, str) and media.strip():
                found.append({"name": node.get("name") or os.path.basename(media),
                              "media_path": media})
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)
    seen, out = set(), []
    for item in found:
        key = os.path.normcase(item["media_path"])
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def sources_from_dir(root, exts):
    return [{"name": name, "media_path": os.path.join(root, name)}
            for name in sorted(os.listdir(root)) if name.upper().endswith(exts)]


def load_manifest(path):
    if not os.path.exists(path):
        return None
    try:
        return json.loads(open(path, encoding="utf-8").read())
    except ValueError:
        print("canh bao: manifest cu doc khong duoc, dung lai tu dau", file=sys.stderr)
        return None


# ---------------------------------------------------------------------- detail

def cmd_detail(args, font):
    man = load_manifest(os.path.join(args.out, "manifest.json"))
    if not man:
        print("ERROR: chua co manifest trong %s. Chay index truoc." % args.out,
              file=sys.stderr)
        return 1
    index = {g["id"]: (s, g) for s in man.get("sources", []) for g in s["segments"]}
    os.makedirs(os.path.join(args.out, "detail"), exist_ok=True)
    rc = 0
    for sid in args.detail:
        if sid not in index:
            print("ERROR: khong co segment %s trong manifest" % sid, file=sys.stderr)
            rc = 1
            continue
        src, seg = index[sid]
        lo = seg["best_in"] if seg.get("best_in") is not None else seg["start"]
        hi = seg["best_out"] if seg.get("best_out") is not None else seg["end"]
        tmp = tempfile.mkdtemp(prefix="det_")
        try:
            for j, frac in enumerate(DETAIL_AT):
                at = lo + frac * (hi - lo)
                _frame(src["media_path"], at, os.path.join(tmp, "%04d.jpg" % j),
                       args.detail_size, src.get("rotate", 0), font,
                       "%s  %.2fs" % (sid, at))
            dest = os.path.join(args.out, "detail", "%s.jpg" % sid)
            _tile(os.path.join(tmp, "%04d.jpg"), 2, 2, dest)
            print("detail: %s  (%.2f-%.2fs)" % (dest, lo, hi))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return rc


# ------------------------------------------------------------------------- main

def cmd_inspect(args, font):
    """Render a dense source window without changing the overview or its reviews."""
    man = load_manifest(os.path.join(args.out, "manifest.json"))
    matches = [s for s in (man or {}).get("sources", [])
               if args.inspect in (s.get("name"), s.get("media_path"))]
    if len(matches) != 1 or not args.range:
        print("ERROR: --inspect needs one exact source name/path and --range START END",
              file=sys.stderr)
        return 1
    source = matches[0]
    lo, hi = args.range
    if not 0 <= lo < hi <= source["duration"]:
        print("ERROR: inspection range is outside the source", file=sys.stderr)
        return 1
    spans = [(lo + a, lo + b) for a, b in
             split(hi - lo, [], args.max_seg, args.min_seg)]
    stem = os.path.splitext(os.path.basename(source["media_path"]))[0]
    target = os.path.join(args.out, "inspection", "%s_%.2f-%.2f" % (stem, lo, hi))
    os.makedirs(os.path.join(target, "sheets"), exist_ok=True)
    placed = build_sheets(source["media_path"], stem, spans, target,
                          source.get("rotate", 0), source["portrait"], font, args.size)
    evidence = {"media_path": source["media_path"], "start": lo, "end": hi,
                "max_seg": args.max_seg, "review_basis": "sampled_frames_only",
                "windows": [{"start": round(a, 2), "end": round(b, 2),
                             "frames": [round(a + f * (b - a), 2) for f in FRAMES_AT],
                             "sheet": sheet, "row": row}
                            for (a, b), (sheet, row) in zip(spans, placed)]}
    with open(os.path.join(target, "inspection.json"), "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, ensure_ascii=False, indent=1)
    print("inspection: %s (%d windows, overview unchanged)" % (target, len(spans)))
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--from-bin", help="bin_items.json tu pr_list_project_items")
    src.add_argument("--from-dir", help="thu muc footage cua job")
    ap.add_argument("--out", required=True, help="<job>/index, khong de trong temp")
    ap.add_argument("--detail", nargs="+", metavar="SEG_ID",
                    help="ve anh lon 2x2 cho cac segment ung vien")
    ap.add_argument("--detail-size", type=int, default=800)
    ap.add_argument("--inspect", help="exact source name/path in the existing manifest")
    ap.add_argument("--range", nargs=2, type=float, metavar=("START", "END"),
                    help="absolute source seconds for --inspect; use --max-seg 1")
    ap.add_argument("--max-seg", type=float, default=2.0)
    ap.add_argument("--min-seg", type=float, default=0.5)
    ap.add_argument("--scene-threshold", type=float, default=0.30)
    ap.add_argument("--scene-scale", type=int, default=192)
    ap.add_argument("--no-scene", action="store_true",
                    help="bo do chuyen canh, chia deu theo --max-seg")
    ap.add_argument("--size", type=int, default=400,
                    help="canh dai nhat cua moi khung tren sheet")
    ap.add_argument("--rotate", type=int, choices=(0, 90, -90, 180),
                    help="xoay ca job; bo trong thi giu `rotate` trong manifest cu")
    ap.add_argument("--force", action="store_true",
                    help="index lai ca file da co trong manifest")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--ext", default=".MP4,.MOV,.MTS,.MKV,.MXF")
    ap.add_argument("--font", default="C:/Windows/Fonts/arial.ttf")
    args = ap.parse_args()
    if not 0 < args.min_seg <= args.max_seg or args.jobs < 1:
        ap.error("need 0 < --min-seg <= --max-seg and --jobs >= 1")
    if args.detail and args.inspect:
        ap.error("choose --detail or --inspect")
    if args.range and not args.inspect:
        ap.error("--range requires --inspect")

    font = args.font if (have_filter("drawtext") and os.path.exists(args.font)) else None
    if font is None:
        print("canh bao: khong ve duoc nhan len khung (thieu drawtext hoac font). "
              "Doc theo vi tri: moi hang la mot segment, tren xuong duoi.",
              file=sys.stderr)

    if args.detail:
        return cmd_detail(args, font)
    if args.inspect:
        return cmd_inspect(args, font)

    if args.from_bin:
        sources = sources_from_bin(args.from_bin)
        if not sources:
            print("ERROR: khong doc duoc media_path nao trong " + args.from_bin,
                  file=sys.stderr)
            return 1
    elif args.from_dir:
        exts = tuple(e.strip().upper() for e in args.ext.split(","))
        sources = sources_from_dir(args.from_dir, exts)
        if not sources:
            print("ERROR: khong co file media nao trong " + args.from_dir,
                  file=sys.stderr)
            return 1
    else:
        print("ERROR: can --from-bin, --from-dir, --detail hoac --inspect", file=sys.stderr)
        return 1

    os.makedirs(os.path.join(args.out, "sheets"), exist_ok=True)
    man_path = os.path.join(args.out, "manifest.json")
    previous = load_manifest(man_path) or {}
    old_src = {os.path.normcase(s.get("media_path", "")): s
               for s in previous.get("sources", [])}
    sampling = {"max_seg": args.max_seg, "min_seg": args.min_seg,
                "scene_threshold": args.scene_threshold, "scene_scale": args.scene_scale,
                "no_scene": args.no_scene, "size": args.size}
    blur_ok = have_filter("blurdetect")
    if not blur_ok:
        print("canh bao: ffmpeg nay khong co blurdetect, bo so do mo", file=sys.stderr)

    def reusable(item):
        """File da index o lan truoc, sheet con do, khong bi ep lam lai."""
        prev = old_src.get(os.path.normcase(item["media_path"]))
        if args.force or not prev or prev.get("schema") != SCHEMA:
            return None
        if prev.get("sampling") != sampling:
            return None
        if args.rotate is not None and args.rotate != prev.get("rotate", 0):
            return None
        sheets = {g.get("sheet") for g in prev.get("segments", [])}
        if not all(os.path.exists(os.path.join(args.out, "sheets", s or "")) for s in sheets):
            return None
        return prev

    def work(item):
        prev = reusable(item)
        if prev is not None:
            return item, prev, True
        path = item["media_path"]
        if not os.path.exists(path):
            return item, None, False
        duration, w, h = probe(path)
        if duration <= 0:
            return item, None, False
        before = old_src.get(os.path.normcase(path)) or {}
        rotate = args.rotate if args.rotate is not None else before.get("rotate", 0)
        portrait = (h > w) != (rotate in (90, -90))
        scene_rows, stat_rows = analyse(path, args.scene_scale, blur_ok)
        cuts = [] if args.no_scene else sorted(
            t for t, r in scene_rows if r.get("scene", 0) > args.scene_threshold)
        spans = split(duration, cuts, args.max_seg, args.min_seg)
        stem = os.path.splitext(os.path.basename(path))[0]
        placed = build_sheets(path, stem, spans, args.out, rotate, portrait,
                              font, args.size)
        kept = {(round(float(g.get("start", -1)), 2), round(float(g.get("end", -1)), 2)): g
                for g in before.get("segments", [])
                if before.get("rotate", 0) == rotate}
        segments = []
        for i, ((lo, hi), (sheet, row)) in enumerate(zip(spans, placed), 1):
            seg = {"id": "%s-%02d" % (stem, i), "index": i,
                   "start": round(lo, 2), "end": round(hi, 2),
                   "duration": round(hi - lo, 2), "sheet": sheet, "row": row,
                   "frames": [round(lo + f * (hi - lo), 2) for f in FRAMES_AT],
                   "metrics": seg_metrics(lo, hi, scene_rows, stat_rows)}
            prior = kept.get((round(lo, 2), round(hi, 2)), {})
            seg.update({k: prior.get(k, v) for k, v in FILLED.items()})
            segments.append(seg)
        entry = {"schema": SCHEMA, "name": item["name"], "media_path": path,
                 "duration": round(duration, 2), "width": w, "height": h,
                 "rotate": rotate, "portrait": portrait,
                 "sampling": sampling,
                 "scene_cuts": len(cuts), "segments": segments}
        return item, entry, False

    results, missing, done = {}, [], 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for item, entry, reused in pool.map(work, sources):
            done += 1
            if entry is None:
                missing.append(item["media_path"])
                print("[%d/%d] BO QUA %s" % (done, len(sources), item["name"]), flush=True)
                continue
            results[os.path.normcase(item["media_path"])] = entry
            print("[%d/%d] %s -> %d segment%s"
                  % (done, len(sources), item["name"], len(entry["segments"]),
                     "  (giu tu manifest cu)" if reused else ""), flush=True)

    out_sources = [results[os.path.normcase(s["media_path"])] for s in sources
                   if os.path.normcase(s["media_path"]) in results]
    set_flags(out_sources)
    segs = [g for s in out_sources for g in s["segments"]]
    manifest = {
        "schema": SCHEMA,
        "sources": out_sources,
        "total_segments": len(segs),
        "looked": sum(1 for g in segs if g.get("look") is not None),
        "not_looked": [g["id"] for g in segs if g.get("look") is None],
        "missing_media": missing,
    }
    with open(man_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=1)

    print("manifest: %s  (%d segment, %d da nhin, %d chua nhin)"
          % (man_path, len(segs), manifest["looked"], len(manifest["not_looked"])))
    if missing:
        print("KHONG MO DUOC (bao Oxi, dung tu suy dien): " + ", ".join(missing),
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
