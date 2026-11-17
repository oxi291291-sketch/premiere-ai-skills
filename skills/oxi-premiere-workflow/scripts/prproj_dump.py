"""Read-only dump of every sequence's track items from a Premiere project file.

    python prproj_dump.py project.prproj [--out seqs.json]

Accepts the gzip-compressed .prproj as saved by Premiere, or an already
decompressed XML. Never writes to the project. Use it for the reference-comparison
method in dialogue-editing.md: Oxi's finished cut can be measured without opening
his project in Premiere.

Output JSON: {seq_name: {"video": [[clip, ...], ...], "audio": [...]}} with
clip = {name, start, end, in, out} in seconds (254016000000 ticks per second).
Adjustment layers, graphics and nested sequences appear by name; filter them out
before counting picture coverage.
"""
import argparse, gzip, json, sys
import xml.etree.ElementTree as ET

TPS = 254016000000.0
ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--out", default="prproj_seqs.json")
args = ap.parse_args()
with open(args.project, "rb") as fh:
    raw = fh.read()
if raw[:2] == b"\x1f\x8b":
    raw = gzip.decompress(raw)
try:
    root = ET.fromstring(raw)
except ET.ParseError as exc:
    sys.exit("not a Premiere project (gzip XML expected): %s" % exc)
byid, byuid = {}, {}
for el in root:
    if "ObjectID" in el.attrib:
        byid[el.attrib["ObjectID"]] = el
    if "ObjectUID" in el.attrib:
        byuid[el.attrib["ObjectUID"]] = el


def ref(el):
    if el is None:
        return None
    if "ObjectRef" in el.attrib:
        return byid.get(el.attrib["ObjectRef"])
    if "ObjectURef" in el.attrib:
        return byuid.get(el.attrib["ObjectURef"])
    return None


def num(el, path, default=0):
    f = el.find(path)
    return int(f.text) if f is not None and f.text else default


def item(ti):
    cti = ti.find("ClipTrackItem")
    start = num(cti, "TrackItem/Start") / TPS
    end = num(cti, "TrackItem/End") / TPS
    sub = ref(cti.find("SubClip"))
    name, inp, out = "", 0, 0
    if sub is not None:
        n = sub.find("Name")
        name = n.text if n is not None else ""
        clip = ref(sub.find("Clip"))
        if clip is not None:
            c = clip.find("Clip")
            inp = num(c, "InPoint") / TPS
            out = num(c, "OutPoint") / TPS
    return {"name": name, "start": round(start, 3), "end": round(end, 3), "in": round(inp, 3), "out": round(out, 3)}


out = {}
for el in root:
    if el.tag != "Sequence":
        continue
    nm = el.find("Name")
    seqname = nm.text if nm is not None else el.attrib.get("ObjectUID")
    res = {"video": [], "audio": []}
    for tg in el.findall("TrackGroups/TrackGroup"):
        grp = ref(tg.find("Second"))
        if grp is None:
            continue
        kind = "video" if grp.tag == "VideoTrackGroup" else "audio" if grp.tag == "AudioTrackGroup" else None
        if not kind:
            continue
        for tr in grp.findall("TrackGroup/Tracks/Track"):
            track = ref(tr)
            clips = []
            if track is not None:
                for t in track.findall("ClipTrack/ClipItems/TrackItems/TrackItem"):
                    ti = ref(t)
                    if ti is not None and ti.find("ClipTrackItem") is not None:
                        clips.append(item(ti))
            res[kind].append(sorted(clips, key=lambda c: c["start"]))
    out[seqname] = res
json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in out.items():
    ends = [max([c["end"] for c in t] or [0]) for t in v["video"]]
    line = "%s V: %s A: %s end %.1f\n" % (k, [len(t) for t in v["video"]],
                                         [len(t) for t in v["audio"]], max(ends or [0]))
    sys.stdout.buffer.write(line.encode("utf-8"))
