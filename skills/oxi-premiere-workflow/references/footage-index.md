# Footage index — look at the shoot once, carefully

One job, one `index/manifest.json`. Stage 1 (dialogue cut) builds it and looks at
every segment; stage 3 (`oxi-broll-editor`) reuses it and only indexes files added
since. This file is the single home of the manifest fields; `oxi-broll-editor`
points here.

Why stage 1: the footage is evidence about what the shoot considered important,
and that evidence is needed **before** the dialogue plan (the feature X lesson
below). Stage 3 reuses this overview, then inspects shortlisted source ranges
against the current script and spoken audio before placement. Keep those
observations in the same job index; do not build a competing catalogue.

## Run

```
python scripts/segment_sheets.py --from-bin bin_items.json --out <job>/index
python scripts/segment_sheets.py --from-dir D:/job/footage --out <job>/index
```

`bin_items.json` is `pr_list_project_items(bin_path: ...)` saved to a file; the bin is
the source of truth, not a disk scan. Put `index/` in the job's working folder, never
in temp: the next session and stage 3 open it again.

Rerunning the same command is cheap and safe. A file already in the manifest, with
the same schema, sampling settings and its sheets still on disk, is kept as it is:
sheet, metrics and every field filled by eye. Only new or changed profiles are
decoded. `--force` redoes all files and keeps filled fields only where both source
bounds and rotation match. When migrating an old 5-second index, back up the index
first: changed windows need fresh judgments and old segment IDs may refer to
different ranges. Rebuild any affected B-roll plan.

Portrait footage recorded lying on its side: `--rotate 90` (or `-90`, `180`) for the
whole job, or edit one source's `rotate` in the manifest and rerun with `--force`.

## Handed to a separate AI ("lọc source")

Oxi often gives this stage to Codex while Claude cuts dialogue, in a short message
such as *"lọc source, phân theo kịch bản, bỏ qua CLIP_1183-1185"*. That message means
this file, not a free-form review. Learned on Job E (culture explainer) (2026-11-11): Codex built
its own sampler and handed over three frames per clip plus a 23-row CSV of picks;
no manifest existed, so the B-roll stage had to look at the footage again.

1. **Source list, not a folder scan.** List the files Oxi included: right
   orientation only, without the files he excluded by name, without stills. Write
   that list as `<job>/6. AI/work/index/sources.json`:
   `[{"name": ..., "media_path": ...}]`. Then run
   `segment_sheets.py --from-bin sources.json --out "<job>/6. AI/work/index"`.
   Excluded footage stays out of the list, so it is never indexed.
2. **Rotation.** Portrait footage stored on its side (Canon often is) gets the
   per-source `rotate`; check one frame per file before filling anything.
3. **Look at everything; pick nothing.** Fill every field in the table below for
   every segment, and do the action map. Do not choose shots or write In/Out picks:
   shots are chosen against the dialogue Oxi locks later, which differs from the
   original script.
4. **Script coverage.** Put Script Map line ids in `ideas`. Also write
   `<job>/6. AI/work/index/script-coverage.md`: each script idea with the segment ids
   that show it, and every idea with **no** footage. Never fill a gap with a
   look-alike (Job E: water puppets are not Ổi Lỗi or Thẩm Rộc).
5. **Bounds.** Do not open or save the Premiere project. Write only under
   `<job>/6. AI/work`. Keep `TIEN-DO-CONG-VIEC.md` current with looked/total and
   the count command.
6. **Done when:** `not_looked` is empty across the manifest, no segment has `look`
   without `description` (or `uncertain: true`), `script-coverage.md` exists, and
   the report gives files, segments, rotated files and excluded files with reasons.
   Batch the open questions into that one report.

## What the script does

- Splits each file into observation windows of **at most 2 seconds**, with scene-cut
  detection plus an even split of longer stretches. These windows are sampling
  units, not semantic scenes or edit durations. A continuous take can change
  action many times without a scene cut. Do not treat zero detected cuts as one
  action, or force every chosen B-roll clip to last 2 seconds.
- Draws a sheet per file: one row per segment, three frames at 15 / 50 / 85 %, each
  labelled with its second on the source. Landscape: 1 segment per row, 6 rows per
  sheet. Portrait: 2 segments per row, 4 rows. Frames are 400 px on the long side,
  enough to judge sharpness and composition, not only content.
- Measures, in the same single decode: `luma` (mean Y, 0-255), `blur` (blurdetect,
  higher = softer) and `motion` (mean scene score, higher = shakier or busier).
- Sets `flags` **relative to this job's own footage**: `dark` (luma < 45), `bright`
  (luma > 210), `soft` (blur at or above the job's 85th percentile and 1.3x its
  median), `busy` (motion at or above the 85th percentile and 2x its median).

A flag says *look harder here*, never *reject*. A dark segment may be the intended
night shot; a busy one may be the whip pan that sells the energy. The eye decides.

## Then look, and fill

Open every sheet with the Read tool. Row number = segment `index`. For each segment:

| Field | What goes in |
|---|---|
| `description` | One sentence of what is actually visible. Text readable on a screen or on the product is copied verbatim: it is the most precise link between a shot and a spoken line. |
| `subject` | Main subject, 1-3 keywords |
| `shot` | `wide` / `medium` / `close` / `macro` / `detail` |
| `camera` | `static` / `pan` / `tilt` / `push` / `pull` / `handheld` / `drone` |
| `energy` | 0.0-1.0. Slow static shot ~0.2, lots of motion ~0.8 |
| `look` | 0.0-1.0, how good the frame is **as a picture**: focus on the subject, exposure, composition, clean background, steadiness. 0.8+ could open the video; 0.5 is fine as cover; under 0.3 only if nothing else shows the idea. |
| `best_in` / `best_out` | Seconds **on the source** of the best stretch inside the segment (focus landed, pan settled, no one walking through). Leave `null` when the whole segment is equally good. |
| `issues` | Short, concrete: `focus hunts 0-1s`, `hand enters right 3.2s`, `reflection of crew`. Empty if none. |
| `roles` | Which of the six B-roll roles this shot can carry: `establish`, `illustrate`, `evidence`, `consequence`, `contrast`, `reveal` (defined in `oxi-broll-editor/references/matching.md`). |
| `ideas` | Script Map line ids this shot plainly shows, when a Script Map exists. |
| `usable` | `false` if out of focus, ruined by shake, clipped, or showing someone or something that must not appear |
| `uncertain` | `true` when the sheet is not clear enough to decide |

When a segment looks promising but the sheet is too small to judge focus or text, render
it large before filling `look`:

```
python scripts/segment_sheets.py --out <job>/index --detail C9705-03 C9719-01
```

That writes `index/detail/<id>.jpg`, four 800 px frames inside `best_in`-`best_out`
(or the whole segment).

## Inspect motion, then map actions

Approved by Oxi on 2026-09-30 after inspecting `CLIP_2170.MP4.mp4`: the 159.45-second
take had zero detected scene cuts but multiple changes of action. Use this sequence:

1. Read the entire 2-second overview, three frames per window, in source order.
2. At a hand movement, object change, camera move, focus hunt or uncertain action
   boundary, render **1-second windows, three frames each**, including context on
   both sides. This reads the existing manifest and writes separate inspection
   sheets with absolute source seconds; it does not replace the overview.

   ```
   python scripts/segment_sheets.py --out <job>/index --inspect CLIP_2170.MP4.mp4 --range 9 17 --max-seg 1 --size 800
   ```

3. Group adjoining windows into complete observed actions. Save
   `<job>/index/action_map.json` with `media_path`, `source_in`, `source_out`,
   `segment_ids`, `action`, `phase` (preparation / execution / result), `camera`,
   `issues`, `review_basis` (sampled_frames / playback), and `evidence` paths.
   Record only phases actually visible; a preparation need not have a filmed result.
   Source range can span many overview windows. Mark provisional bounds explicitly.
4. Compare these actions with the Script Map and the approved spoken audio. If
   the edit already exists, current sequence audio supplies timing and what is
   actually said; the script supplies content requirements. Resolve conflicts
   explicitly rather than placing a scene for a line removed from the edit.
5. For each intended use, compare 2-3 available candidates, inspect large images,
   and watch the exact chosen video range whenever movement, continuity, focus or
   cut boundaries matter. Listen where a claim depends on sound. Record why the
   winner fits the line and its neighbours before sending the plan to Premiere.
   If fewer candidates exist, state that instead of inventing alternatives.

Three frames reveal sampled positions, not continuous motion. They cannot prove
what happens next, that the unshown frames stay sharp, or the technical purpose of
a tool. Exact motion-dependent in/out points require playback; unresolved claims
stay `uncertain`. Do not turn a plausible prediction into an observed action.

Do not guess. If the sheet does not settle it, leave the field empty and set
`"uncertain": true` rather than writing a description that merely sounds right: a
wrong line is trusted by the scoring step and pulls the whole edit off course.

The manifest reports `looked` and `not_looked`. Stage 1 is not finished while
`not_looked` is non-empty. There is no "could not matter" exemption: footage the user
excluded (e.g. karaoke takes the user said to ignore) stays out of `bin_items.json` so it is
never indexed, instead of being indexed and left unlooked. `oxi-broll-editor`
`validate` blocks the whole plan while any segment in the manifest has empty `look`,
blocks a clip whose `segment_id` has no `detail/<segment_id>.jpg`, and refuses a
chosen range if any overview window it crosses has empty `look`, is unusable, or is
missing from the manifest. It also blocks a plan with no manifest at all, a clip
without `segment_id`, and any segment whose `look` is set while `description` is empty
and `uncertain` is not true: a score typed without reading the sheet is not a look.
Five or more segments sharing one description raise a batch-fill warning. Resolving content and motion uncertainty is a manual gate;
the validator cannot prove semantic fit from a score.

Why the whole-manifest gate (Product D, 2026-10-21): stage 1 built the index
and the session ran out of tokens; the next AI filled 82/1321 looks (15/59 files),
picked shots from those, and the old per-clip check passed. If stage 1 stops early,
write the looked count and the remaining files into the job's progress file (shared
rules `QUY-TAC-CHUNG-AI.md`, "Việc dài và bàn giao") so whoever continues keeps looking
instead of moving on.

## What sheets can read

Verified on the Product C shoot: on-screen LCD text (`Mode A`, `<chữ trên hình>`, a fill counter
running 77 mL → 121 mL, `3°C / -15°C / 3°C`), ThinQ app screens down to
`AI Saving Mode`, `Balanced Saving / Max Saving` and `<chữ trên hình>`, and lettering
moulded into the cabinet (`feature X`, `Fresh Converter+`, `Hygiene Fresh`,
`<feature name>`). Enough to match a shot to a spoken line with confidence.
No vision model is needed: ffmpeg input-side seeking makes a 3 GB file cost the same as
a 60 MB one.

## The manifest is evidence of intent, not only a catalogue

On the Product C job the assistant cut the feature X passage as an NG cluster, while
`C9719` and `C9705` were close-ups shot specifically of the words *feature X* on
the cabinet. A subject with purpose-shot footage is a subject the shoot considered
important.

So: **index before the dialogue plan, not after.** Never classify a passage as NG or
low-value while purpose-shot footage for it exists. At stage 3, if a cluster of shots
was made for an idea the current cut has dropped, tell Oxi; the B-roll skill cannot
restore dialogue, but he can, and he needs to know before the cut is locked.

Node ids inside the manifest are worthless in a later session; resolve by `media_path`.
