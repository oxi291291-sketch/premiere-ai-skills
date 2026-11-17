#!/usr/bin/env python3
"""Catalog Oxi's Motion Graphics Templates (.mogrt) so text can be picked by eye.

Oxi, 2026-10-01: text sits only on key lines; the assistant chooses the template
herself from "Text pack A" (first choice), CallOuts_AE_Mogrt or Series templates.
Opening 561 templates one by one in Premiere is not workable, and some of them
cannot carry a word at all (shape transitions with no text control).

Reads only definition.json and thumb.png inside each .mogrt (a zip). Never
writes into the template folder.

    python mogrt_catalog.py ROOT --out catalog.json [--seq 1080x1920]
                            [--max-api 2.2] [--sheets DIR] [--only-text]

Each entry: rel path, folder, name, api, author_app, duration_s, framesize,
text_fields [{name, default, font, size}], fonts, flags.

Flags:
  no_text        no text control (type 6); pr_set_mogrt_text has nothing to write
  api_too_new    apiVersion above --max-api; Premiere asks to install After Effects
  orientation    template is landscape and the sequence is portrait (or the
                 reverse). A warning, not a block: 545 of 561 templates on
                 the edit machine are landscape, so check the exported frame for crop
                 and size instead of skipping them
  bad_mogrt      zip or definition.json unreadable

--sheets writes numbered contact sheets (thumb.png, 4x4 per page) plus the
same numbers in catalog.json, so a look at a sheet maps back to a path.
Messages are ASCII because the Windows console here is cp1252.
"""
import argparse
import json
import os
import sys
import zipfile

TEXT_CONTROL = 6
BLOCKING = {"no_text", "api_too_new", "bad_mogrt"}


def loc_str(obj):
    """strDB -> en_US string (or the first one)."""
    if not isinstance(obj, dict):
        return ""
    db = obj.get("strDB") or []
    for s in db:
        if s.get("localeString") == "en_US":
            return s.get("str", "")
    return db[0].get("str", "") if db else ""


def api_tuple(v):
    try:
        return tuple(int(x) for x in str(v).split("."))
    except ValueError:
        return (99,)


def read_mogrt(path):
    with zipfile.ZipFile(path) as z:
        d = json.loads(z.read("definition.json").decode("utf-8-sig"))
        thumb = z.read("thumb.png") if "thumb.png" in z.namelist() else None
    src = d.get("sourceInfoLocalized") or {}
    src = src.get("en_US") or (next(iter(src.values())) if src else {})
    dur = src.get("duration") or {}
    dur_s = round(dur["value"] / dur["scale"], 3) if dur.get("scale") else None
    size = (src.get("framesize") or {}).get("size") or {}
    fields = []
    for c in d.get("clientControls") or []:
        if c.get("type") != TEXT_CONTROL:
            continue
        fi = c.get("fonteditinfo") or {}
        fields.append({
            "name": loc_str(c.get("uiName")),
            "default": loc_str(c.get("value")),
            "font": fi.get("fontEditValue") or None,
            "size": fi.get("fontSizeEditValue"),
            "font_editable": bool(fi.get("capPropFontEdit")),
        })
    fonts = (d.get("usedFontsLocalized") or {}).get("en_US") or []
    return {
        "name": loc_str(d.get("capsuleNameLocalized")) or d.get("capsuleName", ""),
        "api": str(d.get("apiVersion", "")),
        "author_app": d.get("authorApp", ""),
        "duration_s": dur_s,
        "framesize": [size.get("x"), size.get("y")],
        "text_fields": fields,
        "fonts": fonts,
    }, thumb


def orientation(w, h):
    if not w or not h:
        return None
    return "portrait" if h > w else ("landscape" if w > h else "square")


def scan(root, seq, max_api):
    seq_or = orientation(*seq) if seq else None
    out = []
    for dp, dns, fns in os.walk(root):
        dns.sort()
        for fn in sorted(fns):
            if not fn.lower().endswith(".mogrt"):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root)
            e = {"rel": rel.replace("\\", "/"),
                 "folder": os.path.dirname(rel).replace("\\", "/") or "."}
            try:
                info, thumb = read_mogrt(p)
            except (zipfile.BadZipFile, KeyError, ValueError, OSError) as exc:
                e.update(name=os.path.splitext(fn)[0], flags=["bad_mogrt"],
                         error=type(exc).__name__)
                out.append((e, None))
                continue
            e.update(info)
            flags = []
            if not info["text_fields"]:
                flags.append("no_text")
            if max_api and api_tuple(info["api"]) > api_tuple(max_api):
                flags.append("api_too_new")
            t_or = orientation(*info["framesize"])
            if seq_or and t_or and "square" not in (seq_or, t_or) and t_or != seq_or:
                flags.append("orientation")
            e["flags"] = flags
            out.append((e, thumb))
    return out


def write_sheets(items, sheet_dir, font_path, per_page=16, cols=4, cell=(384, 216)):
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(sheet_dir, exist_ok=True)
    try:
        font = ImageFont.truetype(font_path, 18)
    except OSError:
        font = ImageFont.load_default()
    label_h = 46
    rows = (per_page + cols - 1) // cols
    pages = []
    for start in range(0, len(items), per_page):
        chunk = items[start:start + per_page]
        sheet = Image.new("RGB", (cols * cell[0], rows * (cell[1] + label_h)), (32, 32, 32))
        draw = ImageDraw.Draw(sheet)
        for i, (e, thumb) in enumerate(chunk):
            x, y = (i % cols) * cell[0], (i // cols) * (cell[1] + label_h)
            if thumb:
                try:
                    im = Image.open(BytesIO(thumb)).convert("RGB")
                    im.thumbnail(cell)
                    sheet.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
                except OSError:
                    pass
            tag = "#%d %s" % (e["id"], e["name"])
            draw.text((x + 6, y + cell[1] + 2), tag[:38], fill=(255, 255, 255), font=font)
            if e.get("flags"):
                draw.text((x + 6, y + cell[1] + 23), ",".join(e["flags"])[:38],
                          fill=(255, 140, 0), font=font)
        name = os.path.join(sheet_dir, "sheet_%03d.png" % (start // per_page + 1))
        sheet.save(name)
        pages.append(name)
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="template folder, e.g. %%APPDATA%%/Adobe/Common/Motion Graphics Templates")
    ap.add_argument("--out", required=True, help="catalog.json to write")
    ap.add_argument("--seq", help="live sequence size WxH, e.g. 1080x1920")
    ap.add_argument("--max-api", default="2.2",
                    help="highest apiVersion the installed AE opens (the edit machine AE 2026: 2.2)")
    ap.add_argument("--sheets", help="folder for numbered contact sheets")
    ap.add_argument("--only-text", action="store_true",
                    help="leave templates with a blocking flag out of the sheets")
    ap.add_argument("--font", default="C:/Windows/Fonts/arial.ttf")
    a = ap.parse_args()

    seq = None
    if a.seq:
        try:
            seq = tuple(int(v) for v in a.seq.lower().split("x"))
            assert len(seq) == 2
        except (ValueError, AssertionError):
            ap.error("--seq must look like 1080x1920")
    if not os.path.isdir(a.root):
        print("ERROR: not a folder: %s" % a.root.encode("ascii", "replace").decode())
        return 2

    items = scan(a.root, seq, a.max_api)
    for i, (e, _) in enumerate(items, 1):
        e["id"] = i
    if a.sheets:
        show = [(e, t) for e, t in items
                if not (a.only_text and BLOCKING & set(e["flags"]))]
        pages = write_sheets(show, a.sheets, a.font)
        print("sheets: %d page(s) in %s" % (len(pages), a.sheets.encode("ascii", "replace").decode()))
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"root": os.path.abspath(a.root), "seq": a.seq, "max_api": a.max_api,
                   "templates": [e for e, _ in items]}, fh, ensure_ascii=False, indent=1)

    counts = {}
    for e, _ in items:
        for f in e["flags"]:
            counts[f] = counts.get(f, 0) + 1
    usable = sum(1 for e, _ in items if not BLOCKING & set(e["flags"]))
    print("templates: %d, no blocking flag: %d (orientation only warns)" % (len(items), usable))
    for f in sorted(counts):
        print("  %-12s %d" % (f, counts[f]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
