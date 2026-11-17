"""Build, verify and rebuild the dialogue review pair through the MCP Bridge panel.

The pair is defined in `dialogue-editing.md` ("Review pair"):

  <base>_FULL_DIALOGUE_CLEAN_COMPARE  untouched source on V1/A1, every retained
                                      piece on V2/A2 at its own source position;
  <base>_FULL_DIALOGUE_CLEAN_REVIEW   the same pieces butt-joined on V1/A1, in
                                      plan (script) order.

Both are clones of the source sequence, so they keep its settings. The source
sequence is never written to.

Usage:
    python review_pair.py build   --source "<seq name|id>" --plan cut-plan.json [--base NAME]
    python review_pair.py build   --source "<seq>" --from-review "<old review seq>"
    python review_pair.py rebuild --base NAME [--order plan|time]
    python review_pair.py verify  --base NAME

`--plan` takes the `cut_plan.py` output: a list of {"item", "in", "out"} with
in/out in seconds of the media file. `--from-review` instead reads the pieces off
an existing condensed sequence's A1.

`rebuild` is the step after Oxi edits the compare sequence: it re-reads V2/A2
there and rebuilds the condensed sequence from them. Pieces keep the plan order
by their `Pnn` name; a piece Oxi added has no `Pnn` name, so the run stops and
lists it unless `--order time` is given (that also renumbers the compare clips).

Every build ends with a fresh read of all three sequences and a frame-exact
check. The project is saved only when the check passes (`--no-save` to skip).
Each run writes a JSON report (`--out`, default `review-pair-<base>.json`).

Known trap this script exists to absorb (`premiere-mcp.md`): with 29.97 fps
media in a 30 fps sequence, `projectItem.setInPoint` snaps to the media frame
and `overwriteClip` lands the piece one frame early. The track item's `end`,
`inPoint` and `outPoint` are therefore set directly after placement.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TICKS_PER_SECOND = 254016000000
SUFFIX_CMP = "_FULL_DIALOGUE_CLEAN_COMPARE"
SUFFIX_REV = "_FULL_DIALOGUE_CLEAN_REVIEW"
NAME_RE = re.compile(r"^P(\d+) ")


# --- pure logic (no Premiere) ---------------------------------------------

def piece_name(n, total, item):
    width = max(2, len(str(total)))
    return "P%0*d %s" % (width, n, os.path.splitext(item)[0])


def plan_to_pieces(plan, fps):
    """cut_plan.py rows -> [(item, inF, outF)] on the sequence frame grid."""
    out = []
    for row in plan:
        i, o = int(round(row["in"] * fps)), int(round(row["out"] * fps))
        if o <= i:
            raise ValueError("empty piece: %r" % (row,))
        out.append((row["item"], i, o))
    return out


def layout(pieces, src_v1, names=None):
    """Where each piece goes in both sequences.

    src_v1: the source sequence's V1 clips as dicts {item, s, e, i, o} in
    sequence frames. A piece must sit inside the used range of one V1 clip of
    the same item; its compare start is that clip's start plus the offset.
    `names` overrides the generated Pnn names (verify reads what is there).
    """
    total, cum, rows = len(pieces), 0, []
    for n, (item, i, o) in enumerate(pieces, 1):
        if not (isinstance(i, int) and isinstance(o, int)):
            raise ValueError("P%d %s: in/out %s-%s is off the sequence frame grid" % (n, item, i, o))
        host = [c for c in src_v1 if c["item"] == item and c["i"] <= i and o <= c["o"]]
        if len(host) != 1:
            raise ValueError("P%d %s %d-%d: %d source V1 clips cover it (need exactly 1)"
                             % (n, item, i, o, len(host)))
        h = host[0]
        rows.append({"n": n, "name": names[n - 1] if names else piece_name(n, total, item), "item": item,
                     "i": i, "o": o, "cmp": h["s"] + (i - h["i"]), "rev": cum,
                     "host": src_v1.index(h)})
        cum += o - i
    return rows


def fr(c, ft):
    return tuple(int(c[k]) // ft if int(c[k]) % ft == 0 else int(c[k]) / ft
                 for k in ("s", "e", "i", "o"))


def check(rows, src, cmp_, rev, ft):
    """Frame-exact comparison of three fresh dumps against the layout.

    Pieces are matched by name in the compare sequence (it is in shooting
    order, the plan is in script order) and by index in the condensed one.
    """
    err = []

    def chk(cond, msg):
        if not cond:
            err.append(msg)

    def clips(seq, kind, k):
        t = seq[kind]
        return t[k] if k < len(t) else []

    src_v = [fr(c, ft) for c in clips(src, "V", 0)]
    src_a = [fr(c, ft) for c in clips(src, "A", 0)]
    for label, q in (("compare", cmp_),):
        chk([fr(c, ft) for c in clips(q, "V", 0)] == src_v, label + " V1 differs from source V1")
        chk([fr(c, ft) for c in clips(q, "A", 0)] == src_a, label + " A1 differs from source A1")
    chk(all(not t for t in src["V"][1:] + src["A"][1:]), "source has clips beyond V1/A1")
    chk(all(not t for t in cmp_["V"][2:] + cmp_["A"][2:]), "compare has clips beyond V2/A2")
    chk(all(not t for t in rev["V"][1:] + rev["A"][1:]), "review has clips beyond V1/A1")

    cv, ca = clips(cmp_, "V", 1), clips(cmp_, "A", 1)
    rv, ra = clips(rev, "V", 0), clips(rev, "A", 0)
    chk(len(cv) == len(ca) == len(rv) == len(ra) == len(rows),
        "clip counts cmpV2=%d cmpA2=%d revV1=%d revA1=%d plan=%d"
        % (len(cv), len(ca), len(rv), len(ra), len(rows)))
    src_clip = clips(src, "V", 0)
    for r in rows:
        d = r["o"] - r["i"]
        for tn, tr in (("cmpV2", cv), ("cmpA2", ca)):
            m = [c for c in tr if c["n"] == r["name"]]
            if len(m) != 1:
                err.append("%s %s: %d clips with that name" % (tn, r["name"], len(m)))
                continue
            got = fr(m[0], ft)
            chk(got == (r["cmp"], r["cmp"] + d, r["i"], r["o"]),
                "%s %s %s != %s" % (tn, r["name"], got, (r["cmp"], r["cmp"] + d, r["i"], r["o"])))
        for tn, tr in (("revV1", rv), ("revA1", ra)):
            if r["n"] > len(tr):
                continue
            c = tr[r["n"] - 1]
            got = fr(c, ft)
            chk(c["n"] == r["name"], "%s #%d named %r, want %r" % (tn, r["n"], c["n"], r["name"]))
            chk(got == (r["rev"], r["rev"] + d, r["i"], r["o"]),
                "%s %s %s != %s" % (tn, r["name"], got, (r["rev"], r["rev"] + d, r["i"], r["o"])))
        want_m = src_clip[r["host"]].get("m") if r["host"] < len(src_clip) else None
        for tn, tr in (("cmpV2", cv), ("revV1", rv)):
            for c in tr:
                if c["n"] == r["name"]:
                    chk(c.get("m") == want_m, "%s %s motion %s != source %s"
                        % (tn, r["name"], c.get("m"), want_m))
                    chk(c["item"] == r["item"], "%s %s item %s" % (tn, r["name"], c["item"]))
    for tn, tr in (("cmpV2", cv), ("cmpA2", ca), ("revV1", rv), ("revA1", ra)):
        sp = sorted((fr(c, ft)[0], fr(c, ft)[1]) for c in tr)
        for a, b in zip(sp, sp[1:]):
            chk(b[0] >= a[1], "%s overlap at frame %s" % (tn, b[0]))
    for tn, tr in (("revV1", rv), ("revA1", ra)):
        sp = [fr(c, ft) for c in tr]
        for a, b in zip(sp, sp[1:]):
            chk(b[0] == a[1], "%s gap/overlap between frames %s and %s" % (tn, a[1], b[0]))
    return err


def pieces_from_compare(cmp_, ft, order="plan"):
    """Read Oxi's edited compare V2/A2 back into [(item, inF, outF)] + renames."""
    cv, ca = cmp_["V"][1], cmp_["A"][1]
    bykey = {}
    for kind, tr in (("V", cv), ("A", ca)):
        for c in tr:
            bykey.setdefault((fr(c, ft)[0], c["item"]), {})[kind] = c
    pairs, errs = [], []
    for (s, item), d in sorted(bykey.items(), key=lambda kv: kv[0][0]):
        if set(d) != {"V", "A"}:
            errs.append("frame %s %s: only %s on compare V2/A2" % (s, item, "".join(d)))
            continue
        v, a = fr(d["V"], ft), fr(d["A"], ft)
        if v != a:
            errs.append("frame %s %s: V2 %s and A2 %s differ (split edit?)" % (s, item, v, a))
            continue
        m = NAME_RE.match(d["V"]["n"])
        pairs.append({"num": int(m.group(1)) if m else None, "item": item,
                      "i": v[2], "o": v[3], "s": s, "names": (d["V"]["n"], d["A"]["n"])})
    if order == "plan":
        unnamed = [p for p in pairs if p["num"] is None]
        for p in unnamed:
            errs.append("frame %s %s: no Pnn name, plan position unknown - name it or use --order time"
                        % (p["s"], p["item"]))
        nums = [p["num"] for p in pairs if p["num"] is not None]
        dup = sorted({x for x in nums if nums.count(x) > 1})
        if dup:
            errs.append("duplicate Pnn numbers on compare V2: %s" % dup)
        pairs.sort(key=lambda p: (p["num"] is None, p["num"]))
    if errs:
        raise ValueError("\n".join(errs))
    return [(p["item"], p["i"], p["o"]) for p in pairs], pairs


# --- Premiere side ------------------------------------------------------------

JSX_COMMON = r"""
var FT = %FT%;
function seqBy(key) { var s = app.project.sequences, i, hit = []; for (i = 0; i < s.numSequences; i++) if (s[i].sequenceID == key || s[i].name == key) hit.push(s[i]); return hit; }
function tm(fr) { var t = new Time(); t.ticks = String(fr * FT); return t; }
function motion(c) { var cs = c.components, j, k; for (j = 0; j < cs.numItems; j++) if (cs[j].matchName == "AE.ADBE Motion") return cs[j]; return null; }
function motionDump(c) { var m = motion(c), o = [], k, v; if (!m) return "null"; for (k = 0; k < m.properties.numItems; k++) { try { v = m.properties[k].getValue(); } catch (e) { continue; } o.push(__q(m.properties[k].displayName) + ":" + __q(String(v))); } return "{" + o.join(",") + "}"; }
function dumpTrack(tr, v) { var o = [], k, c; for (k = 0; k < tr.clips.numItems; k++) { c = tr.clips[k]; var f = [["s", __q(c.start.ticks)], ["e", __q(c.end.ticks)], ["i", __q(c.inPoint.ticks)], ["o", __q(c.outPoint.ticks)], ["n", __q(c.name)], ["item", __q(c.projectItem ? c.projectItem.name : "")]]; if (v) f.push(["m", motionDump(c)]); o.push(__kv(f)); } return __arr(o); }
function dumpSeq(q) { var vt = [], at = [], k; for (k = 0; k < q.videoTracks.numTracks; k++) vt.push(dumpTrack(q.videoTracks[k], true)); for (k = 0; k < q.audioTracks.numTracks; k++) at.push(dumpTrack(q.audioTracks[k], false)); return __kv([["name", __q(q.name)], ["id", __q(q.sequenceID)], ["timebase", __q(q.timebase)], ["V", __arr(vt)], ["A", __arr(at)]]); }
"""

JSX_PROBE = r"""
var KEYS = %KEYS%, out = [], i, h;
for (i = 0; i < KEYS.length; i++) { h = seqBy(KEYS[i]); if (h.length > 1) return __error("ambiguous sequence: " + KEYS[i]); out.push(h.length ? dumpSeq(h[0]) : "null"); }
return __result(__arr(out));
"""

JSX_CLONE = r"""
var src = seqBy(%SRC%)[0], NAMES = %NAMES%, out = [], n, j;
if (!src) return __error("source not found");
for (n = 0; n < NAMES.length; n++) if (seqBy(NAMES[n]).length) return __error("already exists: " + NAMES[n]);
for (n = 0; n < NAMES.length; n++) {
  var before = {}, s = app.project.sequences, nw = null;
  for (j = 0; j < s.numSequences; j++) before[s[j].sequenceID] = 1;
  src.clone();
  s = app.project.sequences;
  for (j = 0; j < s.numSequences; j++) if (!before[s[j].sequenceID]) nw = s[j];
  if (!nw) return __error("clone failed: " + NAMES[n]);
  nw.name = NAMES[n];
  out.push(__q(nw.sequenceID));
}
return __result(__arr(out));
"""

# One sequence per call. P rows: [inF, outF, startF, name, hostIndex].
JSX_PLACE = r"""
var seq = seqBy(%SEQ%)[0], src = seqBy(%SRC%)[0], T = %TRACK%, P = %P%;
if (!seq || !src) return __error("sequence not found");
app.project.activeSequence = seq;
var vt = seq.videoTracks[T], at_ = seq.audioTracks[T];
while (vt.clips.numItems) vt.clips[0].remove(false, false);
while (at_.clips.numItems) at_.clips[0].remove(false, false);
function at(tr, fr) { for (var k = 0; k < tr.clips.numItems; k++) if (tr.clips[k].start.ticks == String(fr * FT)) return tr.clips[k]; return null; }
function copyMotion(from, to) { var a = motion(from), b = motion(to), k; if (!a || !b) return; for (k = 0; k < a.properties.numItems && k < b.properties.numItems; k++) { try { var v = a.properties[k].getValue(); if (String(v) != String(b.properties[k].getValue())) b.properties[k].setValue(v, true); } catch (e) {} } }
var miss = [], used = {}, n, q;
for (n = 0; n < P.length; n++) {
  var inF = P[n][0], outF = P[n][1], s = P[n][2], host = src.videoTracks[0].clips[P[n][4]], pi = host.projectItem;
  used[P[n][4]] = pi;
  pi.setInPoint(tm(inF), 4); pi.setOutPoint(tm(outF), 4);
  vt.overwriteClip(pi, tm(s));
  for (q = 0; q < 2; q++) {
    var tr = q ? at_ : vt, c = at(tr, s);
    if (!c) { miss.push(P[n][3] + (q ? " A" : " V")); continue; }
    // Re-fetch between setters: each one can hand back a stale wrapper.
    c.end = tm(s + outF - inF); c = at(tr, s);
    c.inPoint = tm(inF); c = at(tr, s);
    c.outPoint = tm(outF); c = at(tr, s);
    c.name = P[n][3];
    if (!q) copyMotion(host, c);
  }
}
for (n in used) { used[n].clearInPoint(4); used[n].clearOutPoint(4); }
return __result(__kv([["V", __num(vt.clips.numItems)], ["A", __num(at_.clips.numItems)], ["miss", __q(miss.join(","))]]));
"""

JSX_RENAME = r"""
var seq = seqBy(%SEQ%)[0], R = %R%, n, q, k;
for (n = 0; n < R.length; n++) for (q = 0; q < 2; q++) { var tr = q ? seq.audioTracks[1] : seq.videoTracks[1]; for (k = 0; k < tr.clips.numItems; k++) if (tr.clips[k].start.ticks == String(R[n][0] * FT)) tr.clips[k].name = R[n][1]; }
return __result(__num(R.length));
"""

JSX_SAVE = r"""
var seq = seqBy(%SEQ%)[0];
app.project.activeSequence = seq;
seq.setPlayerPosition(String(%AT% * FT));
var ok = app.project.save();
return __result(__kv([["active", __q(app.project.activeSequence.name)], ["saved", __bool(ok !== false)]]));
"""


def jsx(body, ft, **kw):
    code = JSX_COMMON.replace("%FT%", str(ft)) + body
    for k, v in kw.items():
        code = code.replace("%" + k + "%", v)
    return code


def call(code, timeout=600):
    from pr_file_bridge import run, ok
    return ok(run(code, timeout=timeout))


def probe(keys, ft=8467200000):
    return call(jsx(JSX_PROBE, ft, KEYS=json.dumps(keys)))


def ticks_per_frame(seq):
    return int(seq["timebase"])


def src_v1_frames(src, ft):
    return [dict(zip("seio", fr(c, ft)), item=c["item"]) for c in src["V"][0]]


def place(seq_id, src_id, track, rows, key, ft):
    p = [[r["i"], r["o"], r[key], r["name"], r["host"]] for r in rows]
    res = call(jsx(JSX_PLACE, ft, SEQ=json.dumps(seq_id), SRC=json.dumps(src_id),
                   TRACK=str(track), P=json.dumps(p, ensure_ascii=False)))
    if res["miss"]:
        raise RuntimeError("placement lost clips: " + res["miss"])
    return res


def verify_and_report(base, src_key, rows, args, extra):
    src, cmp_, rev = probe([src_key, base + SUFFIX_CMP, base + SUFFIX_REV])
    if not (src and cmp_ and rev):
        raise RuntimeError("missing sequence after build")
    ft = ticks_per_frame(src)
    err = check(rows, src, cmp_, rev, ft)
    fps = TICKS_PER_SECOND / ft
    kept = sum(r["o"] - r["i"] for r in rows)
    src_len = max([fr(c, ft)[1] for c in src["V"][0]] or [0])
    report = dict(extra, base=base, source={"name": src["name"], "id": src["id"]},
                  compare={"name": cmp_["name"], "id": cmp_["id"]},
                  review={"name": rev["name"], "id": rev["id"]},
                  fps=fps, pieces=[[r["item"], r["i"], r["o"]] for r in rows],
                  review_frames=kept, review_seconds=round(kept / fps, 3),
                  kept_percent=round(100.0 * kept / src_len, 1) if src_len else None,
                  errors=err, saved=False)
    if not err and not args.no_save:
        first = min(rows, key=lambda r: r["cmp"])["cmp"] if rows else 0
        report["saved"] = call(jsx(JSX_SAVE, ft, SEQ=json.dumps(cmp_["id"]), AT=str(first)))["saved"]
    out = args.out or "review-pair-%s.json" % base
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("pieces %d  review %.3f s (%s%% of source)  errors %d  saved %s  report %s"
          % (len(rows), kept / fps, report["kept_percent"], len(err), report["saved"], out))
    for e in err[:30]:
        print("  " + e)
    return 1 if err else 0


def cmd_build(a):
    src = probe([a.source])[0]
    if not src:
        raise SystemExit("source sequence not found: " + a.source)
    ft = ticks_per_frame(src)
    fps = TICKS_PER_SECOND / ft
    if any(src["V"][1:]) or any(src["A"][1:]):
        raise SystemExit("source has clips beyond V1/A1; the pair needs a raw source")
    if a.plan:
        with open(a.plan, encoding="utf-8-sig") as fh:
            pieces = plan_to_pieces(json.load(fh), fps)
        origin = {"plan": os.path.abspath(a.plan)}
    else:
        old = probe([a.from_review])[0]
        if not old:
            raise SystemExit("review sequence not found: " + a.from_review)
        # An old review may carry the 29.97 snap; put it back on the grid.
        pieces = [(c["item"], int(round(int(c["i"]) / ft)), int(round(int(c["o"]) / ft)))
                  for c in old["A"][0]]
        origin = {"from_review": {"name": old["name"], "id": old["id"]}}
    rows = layout(pieces, src_v1_frames(src, ft))
    base = a.base or src["name"]
    ids = call(jsx(JSX_CLONE, ft, SRC=json.dumps(src["id"]),
                   NAMES=json.dumps([base + SUFFIX_CMP, base + SUFFIX_REV], ensure_ascii=False)))
    place(ids[0], src["id"], 1, rows, "cmp", ft)
    place(ids[1], src["id"], 0, rows, "rev", ft)
    return verify_and_report(base, src["id"], rows, a, {"mode": "build", "origin": origin})


def source_of(base, cmp_key):
    # The compare V1 is a clone of the source; find the source by name first.
    hit = probe([base])[0]
    if not hit:
        raise SystemExit("source sequence %r not found; pass --source" % base)
    return hit


def cmd_rebuild(a):
    cmp_ = probe([a.base + SUFFIX_CMP])[0]
    if not cmp_:
        raise SystemExit("compare sequence not found")
    src = probe([a.source])[0] if a.source else source_of(a.base, cmp_)
    ft = ticks_per_frame(src)
    pieces, pairs = pieces_from_compare(cmp_, ft, a.order)
    rows = layout(pieces, src_v1_frames(src, ft))
    # Renumber the compare clips so both sequences carry the same Pnn names
    # (a deleted or added piece shifts the numbers). Names only, no timing.
    ren = [[p["s"], r["name"]] for p, r in zip(pairs, rows) if p["names"] != (r["name"], r["name"])]
    if ren:
        call(jsx(JSX_RENAME, ft, SEQ=json.dumps(cmp_["id"]), R=json.dumps(ren, ensure_ascii=False)))
    rev = probe([a.base + SUFFIX_REV])[0]
    if not rev:
        raise SystemExit("review sequence not found")
    place(rev["id"], src["id"], 0, rows, "rev", ft)
    return verify_and_report(a.base, src["id"], rows, a,
                             {"mode": "rebuild", "order": a.order, "renamed": len(ren)})


def cmd_verify(a):
    cmp_ = probe([a.base + SUFFIX_CMP])[0]
    src = probe([a.source])[0] if a.source else source_of(a.base, cmp_)
    ft = ticks_per_frame(src)
    pieces, pairs = pieces_from_compare(cmp_, ft, "plan")
    rows = layout(pieces, src_v1_frames(src, ft), names=[p["names"][0] for p in pairs])
    a.no_save = True
    return verify_and_report(a.base, src["id"], rows, a, {"mode": "verify"})


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", required=True, help="source sequence name or ID")
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", help="cut_plan.py output JSON")
    g.add_argument("--from-review", help="take pieces from this condensed sequence's A1")
    b.add_argument("--base", help="name prefix (default: source name)")
    r = sub.add_parser("rebuild")
    r.add_argument("--base", required=True)
    r.add_argument("--source", help="source sequence (default: the one named --base)")
    r.add_argument("--order", choices=("plan", "time"), default="plan")
    v = sub.add_parser("verify")
    v.add_argument("--base", required=True)
    v.add_argument("--source")
    for p in (b, r, v):
        p.add_argument("--out", help="report JSON path")
        p.add_argument("--no-save", action="store_true")
    a = ap.parse_args()
    return {"build": cmd_build, "rebuild": cmd_rebuild, "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
