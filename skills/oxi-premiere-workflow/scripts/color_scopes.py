"""Do mau bang so thay vi uoc bang mat: tag mau, waveform, parade, vectorscope.

Vi sao co script nay (Oxi duyet 2026-10-19): `color-grading.md` bat "xem
waveform, RGB parade, vectorscope" nhung AI khong doc duoc Lumetri Scopes qua
MCP. Khung da xu ly cua Premiere lay bang `pr_export_frames.py` (`premiere-mcp.md`).
Buoc kiem tra mau vi vay chi la AI nhin anh roi uoc. Script nay lay frame bang
ffmpeg tu file nguon hoac ban xuat review, tinh so do va ve trang scope de Oxi
xem cung. So do la tin hieu da ma hoa (giong scope that), khong phai do sang
ngoai canh.

Ba lenh:

    python color_scopes.py probe <file>...
        Doc tag mau (primaries, transfer, matrix, range), pix_fmt, bit depth.
        Bao TAGS_MISSING, FULL_RANGE, HDR_TRANSFER, WIDE_PRIMARIES, va LOG_TAG khi
        metadata rieng cua may quay ghi gamma log ma tag mau van la bt709.

    python color_scopes.py measure <file> [--at 1.5,10,20 | --samples 7]
                          [--skin x,y,w,h] [--neutral x,y,w,h] [--out dir]
        Do tung thoi diem: IRE p1/p50/p99, % ngoai 0-100 IRE, % chay/bet,
        am mau tren vung trung tinh, am mau rieng vung toi/sang (split toning), goc da so voi duong tong da 123 do,
        do bao hoa, mau sat mep gam. Vung la phan so cua khung (0-1).
        --out ghi color_scopes.json va scopes_NN.png (anh, waveform,
        parade, vectorscope).

    python color_scopes.py compare <file@giay> <file@giay>... [--skin ...]
        Shot dau la goc (anchor); bao chenh lech cua cac shot con lai.

Co ghi chu, khong phai phan quyet: CAST, SKIN_OFF_LINE, LOG_SUSPECT la "nghi".
Den mau co chu y, anh trang tren san khau, look da chot trong Style Card thi
khong phai loi. Khong co nguong chung cho moi canh; xem `color-grading.md`.

Thoat 0 khi chay xong. --strict: thoat 1 khi con co ILLEGAL_LOW/ILLEGAL_HIGH
hoac TAGS_MISSING (dung cho ban giao).
"""

import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

SKIN_LINE = 123.0          # truc I cua vectorscope NTSC; quy tac ngon tay cai
SKIN_TOL = 10.0            # do lech duoc coi la binh thuong
ILLEGAL_PCT = 0.5          # % diem anh ngoai 0-100 IRE truoc khi bao
CLIP_PCT = 2.0             # % diem anh dinh tran / day san truoc khi bao
CAST_LIMIT = 0.03          # chenh kenh (0-1) tren vung --neutral
CAST_AUTO = 0.06           # nguong khi tu tim diem trung tinh (do tin thap hon)
HDR_TRC = {"smpte2084": "PQ", "arib-std-b67": "HLG"}
W_THUMB = 480


def sh(args):
    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("%s\n%s" % (" ".join(args[:6]), p.stderr.decode("utf-8", "replace")[-800:]))
    return p.stdout


# --- probe -------------------------------------------------------------------

def probe(path):
    out = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
              "stream=width,height,pix_fmt,color_range,color_space,color_transfer,"
              "color_primaries,codec_name:stream_side_data=rotation:stream_tags:format=duration:format_tags",
              "-of", "json", path])
    js = json.loads(out)
    if not js.get("streams"):
        raise SystemExit("%s: khong co luong video" % path)
    s = js["streams"][0]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"]) % 360
    pf = s.get("pix_fmt", "")
    depth = 12 if "12" in pf else 10 if "10" in pf else 8
    dur = js.get("format", {}).get("duration")
    info = {
        "file": path, "codec": s.get("codec_name"), "width": s["width"], "height": s["height"],
        "pix_fmt": pf, "bit_depth": depth, "rotation": rot,
        "duration": float(dur) if dur not in (None, "N/A") else None,
        "range": s.get("color_range", "unknown"),
        "matrix": s.get("color_space", "unknown"),
        "transfer": s.get("color_transfer", "unknown"),
        "primaries": s.get("color_primaries", "unknown"),
    }
    flags = []
    tagged = [info[k] for k in ("matrix", "transfer", "primaries")]
    if any(v in ("unknown", "", None) for v in tagged):
        flags.append(["TAGS_MISSING", "warn", "thieu tag mau; trinh phat se tu doan (matrix=%s, transfer=%s, primaries=%s)" % tuple(tagged)])
    if info["range"] == "pc" and pf.startswith("yuv"):
        flags.append(["FULL_RANGE", "warn", "file video full range; nhieu trinh phat hieu sai, xem Bach khoa 04 muc 4.9"])
    if info["transfer"] in HDR_TRC:
        flags.append(["HDR_TRANSFER", "info", "nguon HDR %s; giao SDR phai tone map" % HDR_TRC[info["transfer"]]])
    if info["primaries"] == "bt2020":
        flags.append(["WIDE_PRIMARIES", "info", "mau goc bt2020; dua ve Rec.709 can nen gam"])
    hint = camera_gamma(js.get("format", {}).get("tags", {}), s.get("tags", {}))
    if hint:
        info["camera_gamma"] = hint
        if info["transfer"] not in HDR_TRC:
            flags.append(["LOG_TAG", "warn", "metadata may quay ghi %s = %s, nhung tag transfer = %s: "
                          "tin metadata may quay, file la log; buoc 0 phai chuyen dung profile" % (
                              hint["key"], hint["value"], info["transfer"])])
    info["flags"] = flags
    return info


LOG_WORDS = ("log", "filmlog", "film log", "v-log", "s-log", "slog", "c-log", "clog", "d-log", "dlog",
             "f-log", "flog", "n-log", "nlog", "logc", "bmdfilm", "blackmagic film")
GAMMA_KEYS = ("gamma", "transfer", "colorscience", "color_science", "picture_profile", "lut")


def camera_gamma(*tag_dicts):
    """Tim dau hieu log trong metadata rieng cua may quay (vd. Blackmagic ghi
    `com.apple.proapps.customgamma = com.blackmagic-design.camera.filmlog`
    trong khi tag mau van la bt709 - Job L / VIDEO EXAMPLE, 2026-10-19).
    Bo qua khoa LUT xem truoc (`look.LUTName`): do la LUT gan tren may, khong nuong vao file."""
    extra = {}
    for tags in tag_dicts:
        for k, v in (tags or {}).items():
            if "lutname" in k.lower():
                extra["monitor_lut"] = v
    for tags in tag_dicts:
        for k, v in (tags or {}).items():
            kl, vl = k.lower(), str(v).lower()
            if "lutname" in kl:
                continue
            if any(g in kl for g in GAMMA_KEYS) and any(w in vl for w in LOG_WORDS):
                hit = {"key": k, "value": v}
                for t in tag_dicts:
                    for k2, v2 in (t or {}).items():
                        k2l = k2.lower()
                        if k2l.endswith("cameratype") or k2l.endswith("colorscience"):
                            hit[k2.split(".")[-1]] = v2
                hit.update(extra)
                return hit
    return None


# --- frame capture -----------------------------------------------------------

def guess_matrix(info):
    m = info["matrix"]
    if m in ("bt709", "bt470bg", "smpte170m", "bt2020nc", "fcc", "smpte240m"):
        return {"bt470bg": "bt601", "smpte170m": "bt601", "bt2020nc": "bt2020"}.get(m, m)
    return "bt709" if max(info["width"], info["height"]) >= 1280 else "bt601"


def grab_rgb(info, t):
    """Khung hinh da xoay dung chieu, RGB 8-bit full range, rong W_THUMB*2."""
    rng = "pc" if info["range"] == "pc" else "tv"
    vf = "scale=%d:-2:flags=area:in_color_matrix=%s:in_range=%s:out_range=pc,format=rgb24" % (
        W_THUMB * 2, guess_matrix(info), rng)
    raw = sh(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", info["file"], "-frames:v", "1",
              "-vf", vf, "-f", "image2pipe", "-c:v", "png", "-"])
    if not raw:
        raise SystemExit("%s: khong lay duoc khung tai %.3fs (file dai %s s)" % (info["file"], t, info["duration"]))
    from io import BytesIO
    return np.asarray(Image.open(BytesIO(raw)).convert("RGB"), dtype=np.float32) / 255.0


def grab_luma_codes(info, t):
    """Mat phang Y nguyen ma (khong doi dai, khong xoay), quy ve thang 8-bit."""
    if not info["pix_fmt"].startswith(("yuv", "yuvj", "nv", "p0", "p2")):
        return None
    raw = sh(["ffmpeg", "-v", "error", "-noautorotate", "-ss", "%.3f" % t, "-i", info["file"],
              "-frames:v", "1", "-vf", "extractplanes=y", "-f", "rawvideo", "-"])
    w, h = info["width"], info["height"]
    if len(raw) == w * h:
        y = np.frombuffer(raw, np.uint8).astype(np.float32)
    elif len(raw) == w * h * 2:
        y = np.frombuffer(raw, "<u2").astype(np.float32) / (1 << (info["bit_depth"] - 8))
    else:
        return None
    return y.reshape(h, w)


def codes_to_ire(y, info):
    if info["range"] == "pc" or info["pix_fmt"].startswith("yuvj"):
        return y / 255.0 * 100.0
    return (y - 16.0) / 219.0 * 100.0


# --- measures ----------------------------------------------------------------

def uv_601(rgb):
    """Toa do vectorscope truyen thong: do ~103 do, duong da 123 do."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return 0.492 * (b - y), 0.877 * (r - y)


def luma_709(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def crop(rgb, box):
    if not box:
        return None
    h, w = rgb.shape[:2]
    x, y, bw, bh = box
    x0, y0 = int(x * w), int(y * h)
    x1, y1 = max(x0 + 1, int((x + bw) * w)), max(y0 + 1, int((y + bh) * h))
    return rgb[y0:y1, x0:x1]


def cast_of(px, trusted=False):
    """(R-G, B-G) trung binh tren cac diem trung tinh; None khi qua it diem.

    trusted: vung do Oxi/AI chi la trung tinh (--neutral), lay ca vung, chi bo
    diem chay/bet. Tu dong: lay diem bao hoa < 0.12; qua it diem thi noi toi
    0.30, vi am manh lam chinh mau xam lech toi ~0.25 (thu 2026-10-19, Cb/Cr
    lech 12 ma). Noi rong de lot ao hong, tuong kem vao, nen nguong bao cua
    che do tu dong cao hon (CAST_AUTO)."""
    px = px.reshape(-1, 3)
    if len(px) == 0:
        return None, 0
    mx, mn = px.max(1), px.min(1)
    lum = luma_709(px)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    need = max(200, 0.005 * len(px))
    if trusted:
        sel = px[(lum > 0.05) & (mx < 0.98)]
    else:
        mid = (lum > 0.2) & (lum < 0.85)
        sel = px[(sat < 0.12) & mid]
        if len(sel) < need:          # am manh day ca mau xam ra khoi nguong hep
            sel = px[(sat < 0.30) & mid]
    if len(sel) < need:
        return None, len(sel)
    m = sel.mean(0)
    return (float(m[0] - m[1]), float(m[2] - m[1])), len(sel)


def describe_cast(c):
    rg, bg = c
    words = []
    if rg < -CAST_LIMIT and bg < -CAST_LIMIT:
        words.append("am luc")
    elif rg > CAST_LIMIT and bg > CAST_LIMIT:
        words.append("am hong/tim")
    else:
        if bg - rg > 2 * CAST_LIMIT:
            words.append("am lanh (lam)")
        elif rg - bg > 2 * CAST_LIMIT:
            words.append("am nong (cam)")
    return ", ".join(words)


def hue_angle(px):
    u, v = uv_601(px.reshape(-1, 3))
    mag = np.hypot(u, v)
    keep = mag > 0.02
    if keep.sum() < 50:
        return None
    ang = (np.degrees(np.arctan2(v[keep].mean(), u[keep].mean())) + 360) % 360
    return float(ang)


def measure_frame(info, t, skin=None, neutral=None):
    rgb = grab_rgb(info, t)
    codes = grab_luma_codes(info, t)
    if codes is not None:
        ire = codes_to_ire(codes, info)
        ire_src = "Y nguyen ma"
    else:
        ire = luma_709(rgb) * 100.0
        ire_src = "luma tinh tu RGB"
    flat = ire.ravel()[:: max(1, ire.size // 400000)]
    p1, p50, p99 = (float(v) for v in np.percentile(flat, [1, 50, 99]))
    low = float((flat < -0.5).mean() * 100)
    high = float((flat > 100.5).mean() * 100)
    top = float((flat >= 99.5).mean() * 100)
    bot = float((flat <= 0.5).mean() * 100)

    u, v = uv_601(rgb)
    chroma = np.hypot(u, v)
    mx, mn = rgb.max(2), rgb.min(2)
    gamut_edge = float(((mx >= 0.995) & (mn <= 0.02) & (chroma > 0.25)).mean() * 100)

    m = {"t": round(t, 3), "ire_source": ire_src,
         "ire_p1": round(p1, 1), "ire_p50": round(p50, 1), "ire_p99": round(p99, 1),
         "pct_below_0": round(low, 2), "pct_above_100": round(high, 2),
         "pct_at_top": round(top, 2), "pct_at_bottom": round(bot, 2),
         "chroma_mean": round(float(chroma.mean()), 3),
         "chroma_p95": round(float(np.percentile(chroma, 95)), 3),
         "pct_gamut_edge": round(gamut_edge, 2)}

    # Am mau theo vung sang (split toning): toi = luma < 0.18, sang = luma > 0.70.
    lum = luma_709(rgb)
    for key, sel in (("shadow_rg_bg", lum < 0.18), ("highlight_rg_bg", lum > 0.70)):
        px = rgb[sel]
        if len(px) >= max(200, 0.005 * lum.size):
            mm = px.mean(0)
            m[key] = [round(float(mm[0] - mm[1]), 3), round(float(mm[2] - mm[1]), 3)]
        else:
            m[key] = None

    region = crop(rgb, neutral)
    c, n = cast_of(region if region is not None else rgb, trusted=region is not None)
    m["cast_source"] = "vung --neutral" if neutral else "diem trung tinh tu dong"
    m["neutral_px"] = n
    m["cast_rg_bg"] = [round(c[0], 3), round(c[1], 3)] if c else None

    if skin:
        ang = hue_angle(crop(rgb, skin))
        m["skin_angle"] = round(ang, 1) if ang is not None else None
        m["skin_off_line"] = round(((ang - SKIN_LINE + 180) % 360) - 180, 1) if ang is not None else None

    flags = []
    if low > ILLEGAL_PCT:
        flags.append(["ILLEGAL_LOW", "warn", "%.2f%% diem anh duoi 0 IRE" % low])
    if high > ILLEGAL_PCT:
        flags.append(["ILLEGAL_HIGH", "warn", "%.2f%% diem anh tren 100 IRE" % high])
    if top > CLIP_PCT:
        flags.append(["CLIP_HIGH", "warn", "%.1f%% diem anh dinh tran (chay)" % top])
    if bot > CLIP_PCT:
        flags.append(["CRUSH_LOW", "info", "%.1f%% diem anh day san (den bet); co the co chu y" % bot])
    lim = CAST_LIMIT if neutral else CAST_AUTO
    if c and (abs(c[0]) > lim or abs(c[1]) > lim):
        flags.append(["CAST", "nghi", "%s (R-G %+.3f, B-G %+.3f) tren %s" % (
            describe_cast(c) or "lech kenh", c[0], c[1], m["cast_source"])])
    if skin and m.get("skin_off_line") is not None and abs(m["skin_off_line"]) > SKIN_TOL:
        flags.append(["SKIN_OFF_LINE", "nghi", "goc da %.0f do, lech %+.0f do so voi duong 123 do" % (
            m["skin_angle"], m["skin_off_line"])])
    if p1 > 6 and p99 < 85 and m["chroma_mean"] < 0.06:
        flags.append(["LOG_SUSPECT", "nghi", "den nhac len, trang thap, it mau: giong log/flat chua doi"])
    if gamut_edge > 1.0:
        flags.append(["GAMUT_EDGE", "info", "%.1f%% diem anh sat mep gam (mau qua ruc bi cat)" % gamut_edge])
    m["flags"] = flags
    return m, rgb, ire


# --- scope sheet -------------------------------------------------------------

def waveform(vals, cols, height, lo=-10.0, hi=110.0):
    """vals: anh 2D thang IRE; tra ve anh xam height x cols. Rung +-0.25 IRE chi
    de ve (ma 8-bit cach nhau ~0.46 IRE, khong rung thi hinh soc ngang)."""
    vals = vals + np.random.default_rng(0).uniform(-0.25, 0.25, vals.shape).astype(np.float32)
    h, w = vals.shape
    xs = (np.arange(w) * cols // w).astype(int)
    xi = np.broadcast_to(xs, (h, w)).ravel()
    yi = np.clip(((hi - vals.ravel()) / (hi - lo) * (height - 1)).astype(int), 0, height - 1)
    img = np.zeros((height, cols), np.float32)
    np.add.at(img, (yi, xi), 1.0)
    img = np.log1p(img)
    return (img / max(img.max(), 1e-6) * 255).astype(np.uint8)


def ire_y(v, height, lo=-10.0, hi=110.0):
    return int((hi - v) / (hi - lo) * (height - 1))


def scope_sheet(path, rgb, ire, m, title):
    thumb = Image.fromarray((rgb * 255).astype(np.uint8))
    thumb.thumbnail((W_THUMB, 360))
    H = 256
    wf = Image.fromarray(waveform(ire, W_THUMB, H)).convert("RGB")
    d = ImageDraw.Draw(wf)
    for lvl in (0, 100):
        d.line([(0, ire_y(lvl, H)), (W_THUMB, ire_y(lvl, H))], fill=(200, 60, 60))
    d.text((4, 2), "luma waveform (IRE, red = 0/100)", fill=(255, 255, 0))

    parade = Image.new("RGB", (W_THUMB, H))
    for i, col in enumerate([(255, 70, 70), (70, 255, 70), (90, 140, 255)]):
        g = waveform(rgb[..., i] * 100.0, W_THUMB // 3, H)
        tint = np.stack([g * (c / 255.0) for c in col], 2).astype(np.uint8)
        parade.paste(Image.fromarray(tint), (i * (W_THUMB // 3), 0))
    ImageDraw.Draw(parade).text((4, 2), "RGB parade", fill=(255, 255, 0))

    S = 256
    u, v = uv_601(rgb.reshape(-1, 3))
    scale = (S / 2 - 8) / 0.65
    xi = np.clip((S / 2 + u * scale).astype(int), 0, S - 1)
    yi = np.clip((S / 2 - v * scale).astype(int), 0, S - 1)
    vs = np.zeros((S, S), np.float32)
    np.add.at(vs, (yi, xi), 1.0)
    vs = (np.log1p(vs) / max(np.log1p(vs).max(), 1e-6) * 255).astype(np.uint8)
    vimg = Image.fromarray(vs).convert("RGB")
    d = ImageDraw.Draw(vimg)
    c0 = S / 2
    d.ellipse([8, 8, S - 8, S - 8], outline=(90, 90, 90))
    a = math.radians(SKIN_LINE)
    d.line([(c0, c0), (c0 + math.cos(a) * (S / 2 - 8), c0 - math.sin(a) * (S / 2 - 8))], fill=(255, 170, 60))
    for name, col in [("R", (1, 0, 0)), ("Yl", (1, 1, 0)), ("G", (0, 1, 0)),
                      ("Cy", (0, 1, 1)), ("B", (0, 0, 1)), ("Mg", (1, 0, 1))]:
        uu, vv = uv_601(np.array([[c * 0.75 for c in col]], np.float32))
        x, y = c0 + float(uu[0]) * scale, c0 - float(vv[0]) * scale
        d.rectangle([x - 5, y - 5, x + 5, y + 5], outline=(160, 160, 160))
        d.text((x + 6, y - 6), name, fill=(160, 160, 160))
    d.text((4, 2), "vectorscope (orange = skin 123)", fill=(255, 255, 0))

    lines = [title,
             "IRE p1 %.1f  p50 %.1f  p99 %.1f  | <0: %.2f%%  >100: %.2f%%" % (
                 m["ire_p1"], m["ire_p50"], m["ire_p99"], m["pct_below_0"], m["pct_above_100"]),
             "chroma mean %.3f  p95 %.3f  | cast R-G,B-G %s" % (
                 m["chroma_mean"], m["chroma_p95"], m["cast_rg_bg"]),
             "shadows R-G,B-G %s  | highlights R-G,B-G %s" % (m.get("shadow_rg_bg"), m.get("highlight_rg_bg"))]
    if "skin_angle" in m:
        lines.append("skin angle %s (off %s)" % (m["skin_angle"], m["skin_off_line"]))
    lines += ["%s [%s] %s" % tuple(f) for f in m["flags"]]
    text_h = 14 * len(lines) + 8
    top = max(thumb.height, S)
    sheet = Image.new("RGB", (W_THUMB + S + 16, top + H + text_h + 16), (24, 24, 24))
    sheet.paste(thumb, (4, 4))
    sheet.paste(vimg, (W_THUMB + 12, 4))
    sheet.paste(wf, (4, top + 8))
    sheet.paste(parade.resize((S, H)), (W_THUMB + 12, top + 8))
    d = ImageDraw.Draw(sheet)
    for i, ln in enumerate(lines):
        d.text((6, top + H + 14 + 14 * i), ln.encode("ascii", "replace").decode(), fill=(230, 230, 230))
    sheet.save(path)


# --- commands ----------------------------------------------------------------

def parse_box(s):
    if not s:
        return None
    vals = [float(x) for x in s.split(",")]
    if len(vals) != 4 or not all(0 <= x <= 1 for x in vals):
        raise SystemExit("vung phai la x,y,w,h trong khoang 0-1: %s" % s)
    return vals


def check_time(info, t):
    """Thoi diem vuot do dai file la dau hieu file sai (vd. xuat nham nguon: render
    `_v2` cua Job L chi dai 5 s, 2026-10-19). Bao ro thay vi do khung den."""
    dur = info["duration"]
    if t < 0 or (dur and t > dur):
        raise SystemExit("%s: thoi diem %.3fs nam ngoai file (dai %s s); kiem lai file hoac nguon xuat" % (
            info["file"], t, dur))
    return t


def times_for(info, at, samples):
    if at:
        return [check_time(info, float(x)) for x in at.split(",")]
    dur = info["duration"]
    if not dur:
        return [0.0]
    n = max(1, samples)
    lo, hi = dur * 0.02, dur * 0.98
    return [lo + (hi - lo) * (i + 0.5) / n for i in range(n)]


def cmd_probe(a):
    res = [probe(f) for f in a.files]
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return any(fl[0] == "TAGS_MISSING" for r in res for fl in r["flags"])


def cmd_measure(a):
    info = probe(a.file)
    skin, neutral = parse_box(a.skin), parse_box(a.neutral)
    frames = []
    if a.out:
        os.makedirs(a.out, exist_ok=True)
    for i, t in enumerate(times_for(info, a.at, a.samples)):
        m, rgb, ire = measure_frame(info, t, skin, neutral)
        if a.out:
            m["sheet"] = os.path.join(a.out, "scopes_%02d.png" % (i + 1))
            scope_sheet(m["sheet"], rgb, ire, m, "%s @ %.2fs" % (os.path.basename(a.file), t))
        frames.append(m)
    temporal = []
    for prev, cur in zip(frames, frames[1:]):
        dp = cur["ire_p50"] - prev["ire_p50"]
        if abs(dp) > 8:
            temporal.append("%.2fs -> %.2fs: p50 doi %+.1f IRE (doi canh hay nhay sang?)" % (prev["t"], cur["t"], dp))
    rep = {"probe": info, "frames": frames, "temporal_notes": temporal}
    if a.out:
        with open(os.path.join(a.out, "color_scopes.json"), "w", encoding="utf-8") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    hard = [f for f in info["flags"] if f[0] == "TAGS_MISSING"]
    hard += [f for m in frames for f in m["flags"] if f[0] in ("ILLEGAL_LOW", "ILLEGAL_HIGH")]
    return bool(hard)


def cmd_compare(a):
    skin, neutral = parse_box(a.skin), parse_box(a.neutral)
    rows = []
    for spec in a.shots:
        f, _, t = spec.rpartition("@")
        if not f:
            raise SystemExit("can dang file@giay: %s" % spec)
        info = probe(f)
        m, rgb, ire = measure_frame(info, check_time(info, float(t)), skin, neutral)
        m["shot"] = spec
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            m["sheet"] = os.path.join(a.out, "compare_%02d.png" % (len(rows) + 1))
            scope_sheet(m["sheet"], rgb, ire, m, spec)
        rows.append(m)
    anchor = rows[0]
    for r in rows[1:]:
        dd = {k: round(r[k] - anchor[k], 2) for k in ("ire_p1", "ire_p50", "ire_p99", "chroma_mean")}
        if r["cast_rg_bg"] and anchor["cast_rg_bg"]:
            dd["cast_rg_bg"] = [round(r["cast_rg_bg"][i] - anchor["cast_rg_bg"][i], 3) for i in (0, 1)]
        if r.get("skin_angle") is not None and anchor.get("skin_angle") is not None:
            dd["skin_angle"] = round(r["skin_angle"] - anchor["skin_angle"], 1)
        r["vs_anchor"] = dd
    print(json.dumps({"anchor": anchor["shot"], "shots": rows}, ensure_ascii=False, indent=1))
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("files", nargs="+")
    p.add_argument("--strict", action="store_true")
    p = sub.add_parser("measure")
    p.add_argument("file")
    p.add_argument("--at")
    p.add_argument("--samples", type=int, default=5)
    p.add_argument("--skin")
    p.add_argument("--neutral")
    p.add_argument("--out")
    p.add_argument("--strict", action="store_true")
    p = sub.add_parser("compare")
    p.add_argument("shots", nargs="+")
    p.add_argument("--skin")
    p.add_argument("--neutral")
    p.add_argument("--out")
    p.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    bad = {"probe": cmd_probe, "measure": cmd_measure, "compare": cmd_compare}[a.cmd](a)
    return 1 if (a.strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
