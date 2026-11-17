#!/usr/bin/env python3
"""Ban do lo tren V1, kiem tra va cham diem mot broll plan.

    python broll_plan.py gapmap sequence.json --out gapmap.json
    python broll_plan.py lines gapmap.json --transcript edited.json --out lines.json
    python broll_plan.py validate broll_plan.json --gapmap gapmap.json --manifest index/manifest.json
    python broll_plan.py score broll_plan.json --min 80

`sequence.json` la ket qua cua pr_get_active_sequence luu ra file. Hinh dang cua
no thay doi theo phien ban MCP host, nen phan doc duoc viet de chiu: no di tim
danh sach track o nhieu ten truong khac nhau va noi ro no tim thay gi. Doan nao
khong doc duoc thi bao loi va dung, khong doan.

`validate` va `score` la cong truoc mutation dau tien, khong chi truoc khi giao.
Kiem dung y cau thoai va chuyen dong bang mat/nghe van bat buoc.

Manifest la cua chang 1 (oxi-premiere-workflow/scripts/segment_sheets.py). Clip
nao phai co `segment_id` khi dung manifest. Kiem moi cua so ma khoang source
di qua: chua nhin (`look` rong), `usable: false`, thieu do phu hoac `quality`
cao hon `look` da ghi luc nhin thi khong duoc dung.

Hai cong them (Oxi chot 2026-10-22): manifest con segment chua nhin thi ca plan
bi chan, vi chon tren phan da nhin la bo sot phan con lai; va clip nao cung phai
co anh lon `index/detail/<segment_id>.jpg` da xuat truoc khi chot.

Ba cong nua (Oxi chot 2026-10-22, "fix not cho ho"): plan khong co manifest thi
bi chan, khong con chi canh bao; clip thieu `segment_id` luon bi chan; segment
co `look` ma `description` rong va khong `uncertain` bi coi la chua nhin that.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

TOL = 0.05                      # dung sai thoi gian, giay
MIN_CLIP = 1.0                  # san do dai mot canh B-roll
MAX_CLIP = 10.0                 # tran mot canh (Oxi 2026-11-11: cau dai qua 5-10s chia 2-3 canh)
MOTION_CLIP = 8.0               # tu day canh phai co chuyen dong ben trong khung
CUT_KINDS = ("hard", "j", "l", "action", "match", "beat", "montage")
REPEAT_WINDOW = 20.0            # khong dung lai cung source trong bao nhieu giay
MAX_SAME_SHOT = 3               # khong qua bao nhieu lan lien tiep cung co canh
TRACK_INDEX = {"V1": 0, "V2": 1, "V3": 2}

# Oxi duyet 2026-09-29: canh tram phai dep va dung muc dich, nen quality 10 -> 20,
# lay tu content (25 -> 20) va camera (10 -> 5).
WEIGHTS = {
    "role": 30,
    "content": 20,
    "quality": 20,
    "shot_flow": 15,
    "energy": 10,
    "camera": 5,
}
LOOK_SLACK = 0.15               # quality cham trong plan duoc cao hon look toi da bay nhieu
REPEAT_DESC = 5                 # tu chung nay segment cung description thi nghi dien hang loat


# ---------------------------------------------------------------- doc sequence

def _num(value):
    """Doi mot truong thoi gian sang giay, chap nhan so, chuoi, hoac {seconds:}."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    if isinstance(value, dict):
        for key in ("seconds", "sec", "value", "time"):
            if key in value:
                return _num(value[key])
    return None


def _pick(node, *names):
    for name in names:
        if isinstance(node, dict) and name in node:
            got = _num(node[name])
            if got is not None:
                return got
    return None


def _clips(track):
    """Lay danh sach clip cua mot track, bo qua muc gap rong."""
    items = None
    if isinstance(track, list):
        items = track
    elif isinstance(track, dict):
        for key in ("clips", "items", "trackItems", "track_items"):
            if isinstance(track.get(key), list):
                items = track[key]
                break
    if items is None:
        return []

    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name and not item.get("mediaPath") and not item.get("media_path"):
            continue                                  # muc gap rong cua QE
        start = _pick(item, "start", "startSeconds", "start_seconds", "inPoint")
        end = _pick(item, "end", "endSeconds", "end_seconds", "outPoint")
        if start is None or end is None or end <= start:
            continue
        out.append({"name": name, "start": start, "end": end})
    return sorted(out, key=lambda c: c["start"])


def _tracks(seq, kind):
    """Tim danh sach video hoac audio track trong mot cay JSON tuy hinh dang."""
    keys = {
        "video": ("videoTracks", "video_tracks", "video"),
        "audio": ("audioTracks", "audio_tracks", "audio"),
    }[kind]

    def walk(node):
        if isinstance(node, dict):
            for key in keys:
                if isinstance(node.get(key), list):
                    return node[key]
            for value in node.values():
                found = walk(value)
                if found is not None:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = walk(value)
                if found is not None:
                    return found
        return None

    return walk(seq)


def _gaps(clips, end, floor=0.0):
    gaps, cursor = [], floor
    for clip in clips:
        if clip["start"] - cursor > TOL:
            gaps.append({"start": round(cursor, 3), "end": round(clip["start"], 3)})
        cursor = max(cursor, clip["end"])
    if end - cursor > TOL:
        gaps.append({"start": round(cursor, 3), "end": round(end, 3)})
    return gaps


def cmd_gapmap(args):
    seq = json.loads(open(args.sequence, encoding="utf-8").read())
    video = _tracks(seq, "video")
    audio = _tracks(seq, "audio")
    if video is None:
        print("ERROR: khong tim thay danh sach video track trong file sequence. "
              "Kiem tra lai ket qua pr_get_active_sequence da luu dung chua.",
              file=sys.stderr)
        return 1

    v1 = _clips(video[0]) if len(video) > 0 else []
    v2 = _clips(video[1]) if len(video) > 1 else []
    v3 = _clips(video[2]) if len(video) > 2 else []
    a1 = _clips(audio[0]) if audio else []

    if not a1:
        print("ERROR: A1 rong. Spine thoai chua co thi chua toi luot chang do B-roll.",
              file=sys.stderr)
        return 1

    duration = max([c["end"] for c in a1 + v1 + v2 + v3] or [0.0])
    a1_gaps = _gaps(a1, max(c["end"] for c in a1), floor=a1[0]["start"])
    if a1_gaps:
        print(json.dumps({"status": "blocked", "reason": "A1 con lo", "a1_gaps": a1_gaps},
                         ensure_ascii=False, indent=2))
        print("ERROR: A1 phai lien mach truoc khi do hinh. Tra ve chang cat thoai.",
              file=sys.stderr)
        return 1

    v1_gaps = _gaps(v1, duration)
    covered = sum(c["end"] - c["start"] for c in v2 + v3)
    on_cam = sum(c["end"] - c["start"] for c in v1)
    must = sum(g["end"] - g["start"] for g in v1_gaps)

    result = {
        "duration": round(duration, 3),
        "v1_clips": len(v1),
        "v1_on_camera": round(on_cam, 3),
        "v1_on_camera_pct": round(100 * on_cam / duration, 1) if duration else 0.0,
        "v1_gaps": v1_gaps,
        "must_cover": round(must, 3),
        "broll_existing": round(covered, 3),
        "broll_existing_pct": round(100 * covered / duration, 1) if duration else 0.0,
        "a1_clips": len(a1),
        "a1_end": round(max(c["end"] for c in a1), 3),
        "spine_lock": {"v1_clips": len(v1),
                       "v1_end": round(max([c["end"] for c in v1] or [0.0]), 3),
                       "a1_clips": len(a1),
                       "a1_end": round(max(c["end"] for c in a1), 3)},
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text + "\n")
    print(text)
    return 0


# ----------------------------------------------------------------------- lines

SRT_TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d+)\s*-->\s*(\d+):(\d\d):(\d\d)[,.](\d+)")


def _srt_seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")[:3]) / 1000.0


def _read_transcript(path):
    """Doc transcript Whisper (JSON) hoac SRT ra danh sach {start, end, text}."""
    raw = open(path, encoding="utf-8-sig").read()
    stripped = raw.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        data = json.loads(raw)
        segs = data.get("segments") if isinstance(data, dict) else data
        if not isinstance(segs, list):
            raise ValueError("khong tim thay 'segments' trong file JSON transcript")
        out = []
        for seg in segs:
            start, end = _num(_pick(seg, "start")), _num(_pick(seg, "end"))
            text = str(seg.get("text", "")).strip()
            if start is None or end is None or not text:
                continue
            out.append({"start": start, "end": end, "text": text})
        return out

    out, block = [], None
    for line in raw.splitlines():
        hit = SRT_TIME.search(line)
        if hit:
            g = hit.groups()
            block = {"start": _srt_seconds(*g[:4]), "end": _srt_seconds(*g[4:]), "text": ""}
            out.append(block)
        elif not line.strip():
            # Dong trong dong cue. Dong ngay, neu khong so thu tu cue sau se bi
            # nuot vao cuoi cau cua cue truoc.
            block = None
        elif block is not None:
            block["text"] = (block["text"] + " " + line.strip()).strip()
    return [b for b in out if b["text"]]


def _overlap(a_start, a_end, b_start, b_end):
    return min(a_end, b_end) - max(a_start, b_start)


def cmd_lines(args):
    gapmap = json.loads(open(args.gapmap, encoding="utf-8").read())
    try:
        lines = _read_transcript(args.transcript)
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1
    if not lines:
        print("ERROR: transcript rong hoac khong doc duoc dinh dang. "
              "Can JSON cua Whisper (co 'segments') hoac file SRT.", file=sys.stderr)
        return 1

    a1_end = _num(gapmap.get("a1_end")) or 0.0
    t_end = max(l["end"] for l in lines)
    drift = abs(t_end - a1_end)

    result = {
        "transcript_lines": len(lines),
        "transcript_end": round(t_end, 3),
        "a1_end": round(a1_end, 3),
        "drift": round(drift, 3),
        "gaps": [],
        "silent_gaps": [],
    }

    for gap in gapmap.get("v1_gaps", []):
        g_start, g_end = _num(gap["start"]), _num(gap["end"])
        covering = [{"start": round(l["start"], 3), "end": round(l["end"], 3),
                     "text": l["text"],
                     "overlap": round(_overlap(g_start, g_end, l["start"], l["end"]), 3)}
                    for l in lines
                    if _overlap(g_start, g_end, l["start"], l["end"]) > TOL]
        entry = {"start": round(g_start, 3), "end": round(g_end, 3),
                 "duration": round(g_end - g_start, 3), "lines": covering}
        result["gaps"].append(entry)
        if not covering:
            result["silent_gaps"].append(entry)

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text + "\n")
    print(text)

    if drift > args.max_drift:
        print("ERROR: transcript lech %.2fs so voi A1 (nguong %.2fs). Nhieu kha nang day la "
              "ban chep loi cua source goc chu khong phai cua timeline da dung. Xuat lai "
              "audio tu sequence dang mo roi chep loi lai." % (drift, args.max_drift),
              file=sys.stderr)
        return 1
    if result["silent_gaps"]:
        print("CANH BAO: %d khoang V1 ho khong co loi thoai nao phu len. Do la khoang lang - "
              "hoi Oxi muon de hinh gi, dung tu chon." % len(result["silent_gaps"]),
              file=sys.stderr)
    return 0


# -------------------------------------------------------------------- validate

REQUIRED = ("source", "role", "shot", "source_in", "source_out",
            "timeline_in", "timeline_out", "track")


def cmd_validate(args):
    plan = json.loads(open(args.plan, encoding="utf-8").read())
    errors, warnings = [], []
    clips = plan.get("clips")
    if not isinstance(clips, list) or not clips:
        print("ERROR: plan khong co clip nao.", file=sys.stderr)
        return 1

    for i, clip in enumerate(clips):
        tag = f"clip[{i}] {clip.get('source', '?')}"
        for field in REQUIRED:
            if clip.get(field) in (None, ""):
                errors.append(f"{tag}: thieu truong `{field}`")
        si, so = _num(clip.get("source_in")), _num(clip.get("source_out"))
        ti, to = _num(clip.get("timeline_in")), _num(clip.get("timeline_out"))
        if None in (si, so, ti, to):
            continue
        if so <= si or to <= ti:
            errors.append(f"{tag}: diem ra khong lon hon diem vao")
            continue
        if to - ti < MIN_CLIP:
            errors.append(f"{tag}: dai {to - ti:.2f}s, duoi san {MIN_CLIP}s")
        if to - ti > MAX_CLIP + TOL and not clip.get("long_ok"):
            errors.append(f"{tag}: dai {to - ti:.2f}s, qua tran {MAX_CLIP}s - chia 2-3 canh "
                          f"theo y cau (placement.md), hoac ghi ly do vao `long_ok`")
        elif to - ti > MOTION_CLIP:
            warnings.append(f"{tag}: dai {to - ti:.2f}s - canh tu {MOTION_CLIP}s phai co "
                            f"chuyen dong ben trong khung")
        cut = clip.get("cut")
        if cut is None:
            warnings.append(f"{tag}: thieu truong `cut` (kieu cat: {', '.join(CUT_KINDS)})")
        elif cut not in CUT_KINDS:
            errors.append(f"{tag}: `cut` = `{cut}` khong thuoc {', '.join(CUT_KINDS)}")
        if abs((so - si) - (to - ti)) > TOL:
            errors.append(f"{tag}: do dai source {so - si:.2f}s khac timeline "
                          f"{to - ti:.2f}s - plan nay doi toc do clip, khong duoc")
        track = clip.get("track")
        if track not in ("V2", "V3"):
            errors.append(f"{tag}: track `{track}` - chang nay chi duoc cham V2/V3")
        elif "track_index" in clip and clip["track_index"] != TRACK_INDEX[track]:
            errors.append(f"{tag}: track_index {clip['track_index']} khong khop "
                          f"{track} (phai la {TRACK_INDEX[track]})")

    # chong lan tren cung mot track
    for track in ("V2", "V3"):
        rows = sorted((c for c in clips if c.get("track") == track),
                      key=lambda c: _num(c.get("timeline_in")) or 0.0)
        for a, b in zip(rows, rows[1:]):
            if (_num(b["timeline_in"]) or 0) < (_num(a["timeline_out"]) or 0) - TOL:
                errors.append(f"{track}: {a.get('source')} va {b.get('source')} chong lan")

    ordered = sorted(clips, key=lambda c: _num(c.get("timeline_in")) or 0.0)

    # lap nguon trong cua so.
    # Cat tiep ve phia sau trong cung mot take (source_in moi >= source_out cu) la
    # chuoi cat nhay qua mot hanh dong, KHONG phai lap: ban dung that cua Oxi
    # (Product A, 2026-08) cat 5 lan lien trong CLIP_2137 va 5 lan trong CLIP_2156.
    # Chi loi khi quay lai dung mot khoanh khac da dung (source lui ve / chong lan).
    def forward(a, b):
        return (a.get("source") == b.get("source")
                and (_num(b.get("source_in")) or 0) >= (_num(a.get("source_out")) or 0) - TOL)

    for i, clip in enumerate(ordered):
        for other in ordered[i + 1:]:
            gap = (_num(other.get("timeline_in")) or 0) - (_num(clip.get("timeline_out")) or 0)
            if gap > REPEAT_WINDOW:
                break
            if other.get("source") == clip.get("source") and not forward(clip, other):
                errors.append(f"lap nguon: {clip.get('source')} dung lai o "
                              f"{_num(other.get('timeline_in')):.1f}s, cach lan truoc "
                              f"{gap:.1f}s (nguong {REPEAT_WINDOW}s) va quay lai khoanh khac da dung")

    # co canh lien tiep - mot chuoi cat tiep trong cung take tinh la mot canh
    run, last, prev = 1, None, None
    for clip in ordered:
        shot = clip.get("shot")
        if prev is not None and forward(prev, clip):
            prev = clip
            continue
        prev = clip
        run = run + 1 if shot == last else 1
        last = shot
        if run >= MAX_SAME_SHOT:
            errors.append(f"{MAX_SAME_SHOT} canh lien tiep cung co `{shot}` quanh "
                          f"{_num(clip.get('timeline_in')):.1f}s")

    # J/L cut: bao nhieu clip bat dau dung bien cau thoai
    snapped = sum(1 for c in ordered if c.get("line_start") is not None
                  and abs((_num(c.get("timeline_in")) or 0)
                          - (_num(c.get("line_start")) or 0)) < TOL)
    if ordered and snapped == len(ordered):
        warnings.append("moi clip deu bat dau dung bien cau thoai - day la ban dung "
                        "kieu trinh chieu, xem lai muc Kieu cat trong placement.md")
    # Oxi 2026-11-11: kieu cat tu phan tich tung cho; ca bai mot kieu la ap cong thuc
    leads = [round((_num(c.get("line_start")) or 0) - (_num(c.get("timeline_in")) or 0), 1)
             for c in ordered if c.get("line_start") is not None]
    if len(leads) >= 6 and snapped < len(leads) and max(leads) - min(leads) < 0.15:
        warnings.append(f"moi clip deu vao som nhu nhau (~{leads[0]:.1f}s truoc cau) - "
                        "ap mot cong thuc, xem lai muc Kieu cat trong placement.md")
    kinds = [c.get("cut") for c in ordered if c.get("cut")]
    if len(kinds) >= 6 and len(set(kinds)) == 1:
        warnings.append(f"ca {len(kinds)} clip cung kieu cat `{kinds[0]}` - tu phan tich "
                        "tung cho, xem muc Kieu cat trong placement.md")

    # phu het khoang V1 ho
    if args.gapmap:
        gm = json.loads(open(args.gapmap, encoding="utf-8").read())
        for gap in gm.get("v1_gaps", []):
            need = gap["end"] - gap["start"]
            if need < MIN_CLIP:
                continue
            have = 0.0
            for clip in clips:
                lo = max(gap["start"], _num(clip.get("timeline_in")) or 0)
                hi = min(gap["end"], _num(clip.get("timeline_out")) or 0)
                have += max(0.0, hi - lo)
            if need - have > TOL:
                errors.append(f"khoang V1 ho {gap['start']:.1f}-{gap['end']:.1f}s "
                              f"con trong {need - have:.2f}s")

    _check_manifest(args, plan, clips, errors, warnings)

    report = {"clips": len(clips), "errors": errors, "warnings": warnings,
              "status": "clean" if not errors else "blocked"}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def _manifest_path(args, plan):
    if args.manifest:
        return args.manifest
    declared = plan.get("manifest")
    if declared:
        return os.path.join(os.path.dirname(os.path.abspath(args.plan)), declared)
    return None


def _check_manifest(args, plan, clips, errors, warnings):
    """Doi chieu clip voi manifest chang 1: chua nhin thi chua dung."""
    tagged = [c for c in clips if c.get("segment_id")]
    path = _manifest_path(args, plan)
    for c in clips:
        if not c.get("segment_id"):
            errors.append(
                f"{c.get('source', '?')} @ {_num(c.get('timeline_in')) or 0:.1f}s: "
                "khong co segment_id, khong doi chieu duoc voi manifest")
    if not clips:
        return
    # A plan without a manifest used to pass with warnings only, so the
    # whole-footage gate below could be skipped by leaving the field out.
    if not path or not os.path.exists(path):
        errors.append(f"khong mo duoc manifest ({path}). Khai `manifest` trong plan "
                      "hoac dua --manifest <job>/index/manifest.json")
        return
    man = json.loads(open(path, encoding="utf-8").read())
    index = {g["id"]: (s, g) for s in man.get("sources", []) for g in s.get("segments", [])}
    # Product D (2026-10-21): plan chon tren 82/1321 segment da nhin
    # (15/59 file) van pass vi cong cu chi kiem segment duoc chon.
    blind = [(s, g) for s, g in index.values() if g.get("look") is None]
    if blind:
        files = sorted({s.get("name") or os.path.basename(s.get("media_path", ""))
                        for s, _ in blind})
        errors.append(f"manifest con {len(blind)}/{len(index)} segment chua nhin tren "
                      f"{len(files)} file ({', '.join(files[:8])}"
                      f"{', ...' if len(files) > 8 else ''}). Nhin het footage roi moi chon canh")
    # A look score with no description and no `uncertain` flag is a number
    # typed without reading the sheet: the gate above only proves a field was set.
    hollow = sorted(g["id"] for _, g in index.values() if g.get("look") is not None
                    and not str(g.get("description") or "").strip() and not g.get("uncertain"))
    if hollow:
        errors.append(f"{len(hollow)} segment co look nhung description rong va khong "
                      f"uncertain ({', '.join(hollow[:8])}{', ...' if len(hollow) > 8 else ''}). "
                      "Nhin sheet roi ghi dieu thay duoc, chua chac thi uncertain: true")
    seen = {}
    for _, g in index.values():
        text = " ".join(str(g.get("description") or "").lower().split())
        if text:
            seen.setdefault(text, []).append(g["id"])
    for text, ids in seen.items():
        if len(ids) >= REPEAT_DESC:
            warnings.append(f"{len(ids)} segment cung mot description \"{text[:60]}\" "
                            f"({', '.join(ids[:5])}, ...). Nghi dien hang loat - mo lai sheet")
    detail_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "detail")
    for c in tagged:
        sid = c["segment_id"]
        tag = f"{c.get('source', '?')} [{sid}]"
        if sid not in index:
            errors.append(f"{tag}: segment khong co trong manifest")
            continue
        if not os.path.exists(os.path.join(detail_dir, f"{sid}.jpg")):
            errors.append(f"{tag}: chua xuat anh lon detail/{sid}.jpg. Sheet nho chi de loc - "
                          "chay segment_sheets.py --detail va doc anh truoc khi chot")
        src, seg = index[sid]
        media = c.get("media_path")
        if media and os.path.normcase(os.path.abspath(media)) != \
                os.path.normcase(os.path.abspath(src.get("media_path", ""))):
            errors.append(f"{tag}: media_path khac file cua segment ({src.get('media_path')})")
        if c.get("source") and c["source"] != src.get("name") \
                and c["source"] != os.path.basename(src.get("media_path", "")):
            errors.append(f"{tag}: source khac ten file cua segment ({src.get('name')})")
        si, so = _num(c.get("source_in")), _num(c.get("source_out"))
        if si is None or so is None:
            continue
        if so <= seg["start"] or si >= seg["end"]:
            errors.append(f"{tag}: doan source {si:.1f}-{so:.1f}s nam ngoai segment "
                          f"{seg['start']:.1f}-{seg['end']:.1f}s")
            continue
        # A usable action may cross several 2-second observation windows.
        # The primary id cannot authorize adjacent footage nobody reviewed.
        crossed = sorted((g for g in src.get("segments", [])
                          if g["end"] > si and g["start"] < so),
                         key=lambda g: g["start"])
        cursor = si
        for window in crossed:
            wtag = f"{tag} / {window['id']}"
            if window["start"] > cursor + TOL:
                errors.append(f"{wtag}: manifest khong phu du doan source {cursor:.2f}-{window['start']:.2f}s")
            cursor = max(cursor, window["end"])
            if window.get("usable") is False:
                errors.append(f"{wtag}: manifest ghi usable=false ({window.get('issues') or 'khong ghi ly do'})")
            look = window.get("look")
            if look is None:
                errors.append(f"{wtag}: segment chua duoc nhin (look rong). Chua nhin thi chua dung - "
                              "mo sheet hoac --detail roi dien look")
            else:
                quality = (c.get("scores") or {}).get("quality")
                if quality is not None and float(quality) > float(look) + LOOK_SLACK:
                    errors.append(f"{wtag}: cham quality {float(quality):.2f} cao hon look "
                                  f"{float(look):.2f} da ghi luc nhin")
            bi, bo = window.get("best_in"), window.get("best_out")
            used_in, used_out = max(si, window["start"]), min(so, window["end"])
            if bi is not None and bo is not None and (used_in < bi - TOL or used_out > bo + TOL):
                warnings.append(f"{wtag}: doan {used_in:.1f}-{used_out:.1f}s ra ngoai khoang dep "
                                f"{bi:.1f}-{bo:.1f}s - ghi ly do vao `why`")
        if cursor < so - TOL:
            errors.append(f"{tag}: manifest khong phu du doan source {cursor:.2f}-{so:.2f}s")


# ----------------------------------------------------------------------- score

def cmd_score(args):
    plan = json.loads(open(args.plan, encoding="utf-8").read())
    rows, missing = [], []
    for i, clip in enumerate(plan.get("clips", [])):
        scores = clip.get("scores")
        if not isinstance(scores, dict) or set(WEIGHTS) - set(scores):
            missing.append(f"clip[{i}] {clip.get('source', '?')}: thieu diem "
                           f"{sorted(set(WEIGHTS) - set(scores or {}))}")
            continue
        total = sum(WEIGHTS[k] * max(0.0, min(1.0, float(scores[k]))) for k in WEIGHTS)
        rows.append({"source": clip.get("source"),
                     "timeline_in": _num(clip.get("timeline_in")),
                     "role": clip.get("role"),
                     "score": round(total, 1)})

    if missing:
        print(json.dumps({"status": "blocked", "missing": missing},
                         ensure_ascii=False, indent=2))
        print("ERROR: moi clip phai co `scores` voi du sau tieu chi. "
              "Thang diem o references/matching.md.", file=sys.stderr)
        return 1

    below = [r for r in rows if r["score"] < args.min]
    mean = round(sum(r["score"] for r in rows) / len(rows), 1) if rows else 0.0
    print(json.dumps({"clips": len(rows), "mean": mean, "min_required": args.min,
                      "below": below, "scores": rows,
                      "status": "pass" if not below else "blocked"},
                     ensure_ascii=False, indent=2))
    return 0 if not below else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("gapmap", help="ban do lo V1 tu sequence live")
    p.add_argument("sequence")
    p.add_argument("--out")
    p.set_defaults(func=cmd_gapmap)

    p = sub.add_parser("lines", help="ghep loi thoai vao tung khoang V1 ho")
    p.add_argument("gapmap")
    p.add_argument("--transcript", required=True)
    p.add_argument("--out")
    p.add_argument("--max-drift", type=float, default=1.0)
    p.set_defaults(func=cmd_lines)

    p = sub.add_parser("validate", help="kiem tra cau truc va rang buoc cung")
    p.add_argument("plan")
    p.add_argument("--gapmap")
    p.add_argument("--manifest", help="mac dinh: truong `manifest` trong plan, tinh tu thu muc plan")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("score", help="cham diem theo thang trong matching.md")
    p.add_argument("plan")
    p.add_argument("--min", type=float, default=80.0)
    p.set_defaults(func=cmd_score)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
