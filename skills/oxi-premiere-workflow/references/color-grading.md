# Premiere color-grading workflow

Use this workflow for `chỉnh màu`, `cân màu`, `color correction`, `color grading`, `match màu`, `Lumetri`, `LUT`, and `look`, and whenever the finishing order reaches the colour step (denoise → music → transitions → **colour** → sub → final QC → export).

## What the colour stage loads (Oxi, 2026-10-19)

Oxi asked that every colour stage, once the rest of the Premiere work is done, pull in what was learned on 2026-10-19. Work through this file top to bottom; it is the single entry point:

1. **Step 0, pipeline**: what colour space each source really is, and exactly one conversion per source.
2. **Style Card and protected colours**: the agreed direction and the colours the look must not move.
3. **Measure before**: `scripts/color_scopes.py` on the sources.
4. **Diagnose** with the table below, separating faults from intended looks.
5. **Build**: V4 base, per-clip fixes, shot matching, then the V5 look, using the feel recipes in the dictionary.
6. **Measure after** on a review render, then Final QC.

Background on why colour goes wrong (six stages, colour management, HDR): (internal note, not published). Read it only when a diagnosis needs the "why".

## Core separation

**(Oxi, 2026-10-14) Colour lives on two stacked adjustment layers, V4 then V5**, matching the track map in `finishing-layout.md`:

1. **V4, base grade** (`COLOR_BASE`): one full-length adjustment layer carrying the shared technical base for the whole sequence: source color-space handling, overall white balance, exposure, contrast, saturation normalization.
2. **V5, look** (`COLOR_LOOK_LUT`): one full-length adjustment layer carrying the creative LUT or shared Lumetri look. Do not attach the shared creative LUT to source clips.
3. **Per clip, only for a shot-specific fault**: a shot whose white balance or exposure differs from its neighbours, highlight/shadow recovery, matching an odd shot to the base. Do not repeat the shared base on every clip.

A LUT is not a substitute for correcting exposure or white balance. Establish a neutral, matched base (V4 plus any per-clip fixes) first, then add the look on V5. Graphics on V6–V9 sit above both layers and stay ungraded.

## Step 0: colour pipeline

Do this before touching any Lumetri control. Most "the colour looks wrong" problems are a pipeline fault, not a grading fault.

1. Run `python -B scripts/color_scopes.py probe <one file per camera/profile>`. Note codec, bit depth, range, matrix/transfer/primaries, rotation and the flags (`TAGS_MISSING`, `FULL_RANGE`, `HDR_TRANSFER`, `WIDE_PRIMARIES`).
2. Ask or read what profile each camera shot (Standard, HLG, S-Log3, D-Log...). File colour tags rarely say "log". `probe` also reads the camera's own metadata and raises `LOG_TAG` when it names a log gamma: on 2026-10-19 a Blackmagic Pocket 4K ProRes file was tagged bt709/bt709/bt709 while `com.apple.proapps.customgamma` said `filmlog` (Gen 5), so Premiere treated it as Rec.709 and showed a flat image. **`LOG_TAG` outranks the colour tags.** A flat picture with only `LOG_SUSPECT` from `measure` is a suspicion, never proof. A `monitor_lut` in the hint is the LUT the camera displayed while shooting; it is not baked into the file.
3. Read Premiere's live colour settings: Project Settings › Color Management (auto-detect log/RAW, input tone mapping), the sequence's colour settings (working space preset, output), and Display Color Management. Option names change between versions; record what this install actually shows.
4. Choose **exactly one** path per source and write it down:
   - (a) Premiere's colour management converts the log/HDR source → no technical LUT anywhere;
   - (b) a technical LUT or CST for that exact camera profile on the clip's Input LUT → auto conversion off for those clips;
   - (c) the source is already Rec.709 SDR → nothing.
   Two conversions on one source (auto + LUT) is the most common cause of a harsh, clipped image.

   How (b) is done on Premiere 26.3.2 (2026-10-19), because script cannot do it (`premiere-mcp.md`):
   - Put the technical LUT on the clip **in the review sequence** (Lumetri › Basic Correction › Input LUT › Browse…), never as a colour-space override on the project item: that would change the source sequence too.
   - Use the camera maker's LUT for the exact profile. Blackmagic's LUTs ship with DaVinci Resolve (`C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\Blackmagic Design\`); for Color Science Gen 5 use `Blackmagic Gen 5 Film to Video.cube`, not the `Pocket 4K … v4` ones (Gen 4).
   - Premiere refuses a `.cube` containing Resolve's private `BMD_TITLE` line ("Invalid file – Unable to load selected file"). Copy the LUT into `<job>/color/`, drop the `BMD_TITLE` line, keep `LUT_3D_SIZE` and every data row unchanged (diff the rows), and browse to the copy. Never edit Resolve's own file.
   - Read back that `Input LUT` is no longer `0` and that the clip carries exactly one Lumetri.
5. Deliverable colour space comes from the brief. If the brief is silent, deliver SDR Rec.709 and state that assumption in the stage report; HDR sources are tone-mapped to SDR.
6. Record per source in the job's `TIEN_DO_*.md`: file/camera, tags, profile, chosen path (a/b/c), deliverable space.

## Style Card, protected colours and terms

For an explicitly assigned colour stage only, use [assets.md](assets.md):
dictionary/colour knowledge → `color` techniques → suitable OXI Assets LUTs.
Record source IDs and input/output spaces; a technical LUT must match the exact
camera profile and a creative LUT belongs after the neutral base. A library
label does not prove a transform is correct; Step 0 and measured QC still apply.

1. Read `<job>/style_card.json`, direction `chot`: fields `anh_sang_mau`, `palette` and `mau_bao_ve` (`oxi-visual-style/references/style-card.md` section 5). If `chot` is empty, inspect representative footage and recommend a direction using the procedure below; reuse any direction Oxi already chose in the conversation.
2. **Protected colours** (term `protected-colors`): product and packaging, logo, the brand's KV palette, costume or objects whose colour carries meaning (ritual costume such as hầu đồng, uniforms), and skin. Take them from `mau_bao_ve`, the brief's `rang_buoc` and the script; list them in `TIEN_DO_*.md` before grading. The look must not move them: hold them with an HSL qualifier or mask before pushing the look, and measure them before/after. Changing a protected colour needs Oxi's approval.
3. Translate the card's feel words into Lumetri with the dictionary's feel terms: `lifted-blacks`, `deep-blacks`, `creamy-highlights`, `highlight-rolloff`, `faded-look`, `punchy-colors`, `rich-colors`, `dusty-colors`, `milky-colors`, `soft-colors`, `gritty-look`, `dreamy-look`, `halation`, `organic-color`, `memory-colors`. Each term's `dung` field holds a mild-strength recipe for V5. Search with `python -B oxi-visual-style/scripts/visual_style.py find <word>`.
4. Other colour terms (Lumetri sections, vectorscope, RGB parade, legal range, qualifier/mask, bleach bypass, day for night, vignette) live in `oxi-visual-style/references/tu-dien-visual-art.md#05-mau-sac`, light in `#06-anh-sang`; figures in `oxi-visual-style/assets/tu-dien-visual-art.html#<id>`. Term `lumetri-panel` maps each Lumetri section to "fix on clip" or "look on Adjustment Layer".

## Recommend a colour direction from the footage (Oxi, 2026-10-19)

When Oxi has not supplied a look, inspect representative frames and the pipeline first, then recommend one direction with 2–3 concrete reasons: existing light colours, subject/background separation, exposure headroom, noise, skin/product colours and the video purpose if known. Offer alternatives only when useful. Do not infer the purpose from the project filename; `Job L / VIDEO EXAMPLE` was a colour test, not a travel vlog.

State how the recommendation maps to V5: shadow/highlight tint, black level, contrast, saturation and protected colours. A screenshot alone cannot establish exact IRE, camera profile or noise performance; label observation versus measurement. Use a mild reversible preview when Oxi has delegated the creative choice; otherwise present the recommendation for selection. A direction already chosen in chat is sufficient authorization; record it and proceed without asking again for a Style Card.

Oxi may provide a preferred style or reference later. Record an explicit preference with its scope and date; one choice for one test is not his global taste. Evaluate a reference's lighting, palette and tone structure before matching; scene content and lighting limit the match.

### Neon-night example and split-tone LUT

`VIDEO EXAMPLE_COLOR_REVIEW`, 2026-10-19: Oxi chose mild teal-orange for an indoor LED-lit game room. V1 retains the technical Gen 5 conversion, V4 retains WB, V5 carries the creative look. `scripts/split_tone_lut.py` generates a creative Rec.709 RGB LUT for the V5 Creative Look slot when wheel/curve data cannot be edited reliably through the bridge. It preserves encoded luma before RGB clipping; it cannot guarantee luma preservation for clipped colours and is not a technical input transform.

Tested settings for this shot only: `--teal 0.12 --orange 0.015 --top 0.50 --floor 0.025`, V5 Contrast +6, Highlights -5, Blacks 0, Vibrance +12, Vignette Amount -0.6. Stronger Blacks/Contrast caused crushed shadows; ease those before increasing the look. Measure `shadow_rg_bg` and `highlight_rg_bg` as descriptive channel differences, not universal targets (the subject colours affect them). This is a tested preview recipe, not Oxi's final aesthetic approval.

When editing Lumetri by script, display names repeat across sections (Basic Temperature/Tint and HSL Secondary Temperature/Tint). Resolve the intended section/property, assert it, modify only that property, and read back nearby controls. A loop over every matching display name accidentally changed HSL Secondary too; those values were reset and the exported frame verified unchanged.

## Measuring

The agent cannot read Lumetri Scopes through MCP. Measure with `scripts/color_scopes.py` on files: the sources (ffmpeg takes the frames) and frames Premiere itself renders (`scripts/pr_export_frames.py`).

- **Before**: `measure <source> --samples 5 --out <job>/color/before/<clip>` for each camera/scene, or `--at` with chosen times. The output is `color_scopes.json` plus `scopes_NN.png` sheets (picture, luma waveform, RGB parade, vectorscope with the 123° skin line).
- **(Oxi, 2026-10-19) While tuning, export a few frames, not a render.** After each change run `python -B scripts/pr_export_frames.py --sequence <review sequence> --at <3–5 sequence times> --out <job>/color/frames_<round> --measure [--neutral ...]`. It exports Premiere's own processed frames through the MCP Bridge and measures them: three frames took about 9 seconds on 2026-10-19, against a UI render per round before. On `VIDEO EXAMPLE_COLOR_REVIEW` its numbers matched the H.264 review render at the same moment (same cast, IRE within 0.2). Pick moments that show the problem: the neutral object, the face, each camera or light change. One output folder per round; the script refuses to overwrite.
- **After, once at the end**: export one review render (`_REVIEW` suffix, `export.md`) of the graded range, then `measure` it at the same moments plus every scene and light change. This is the only check for motion (flicker, masks slipping) and for legal range: exported PNG frames are full-range RGB and cannot show super-white or super-black (`ILLEGAL_*`). Do not judge from a Program Monitor screenshot. Check the render's duration first: a time past the end makes `measure` stop with "nam ngoai file", which usually means the wrong source was exported (`export.md`). Each correction round is a new render name (`_v2`, `_v3`…); never overwrite one.
- **Map the moments**: render time = source time − the clip's source in-point + its sequence start.
- **Skin**: `--skin x,y,w,h` (fractions of the frame) only when the face is inside that box at that time; look at the sheet first and give one box per timestamp (`--at` one time per run). The skin line is a rule of thumb: about ±10° is normal.
- **Neutral**: `--neutral x,y,w,h` on something known to be grey or white (paper, wall, shirt). Without it the script guesses neutral pixels, which is weaker; treat its `CAST` as a lead.
- **Matching**: `compare <anchor@t> <shot@t>...` reports each shot against the anchor (exposure, cast, saturation, skin angle). **(default, from `ghost-editor`, 2026-11-10)** In a presenter video the anchor is the presenter's A-roll: inserts are matched to the face, never the face regraded to fit an insert. The source repo measured stock inserts 15–44 b* units colder than the presenter plate when nobody conformed them.
- **Delivery**: `--strict` exits 1 on `ILLEGAL_LOW/HIGH` or `TAGS_MISSING`.

Flags marked `nghi` (`CAST`, `SKIN_OFF_LINE`, `LOG_SUSPECT`) are leads, not verdicts. Every colour claim in a report says whether it was **measured** (script, with the number) or **eyeballed**; an eyeballed estimate is never reported as a measurement.

## Diagnosis table

Find the symptom, check first, then fix in the place given. "Pipeline" means Step 0.

| Symptom | Check first | Fix where | Do not |
|---|---|---|---|
| Log looks grey and flat | Camera profile; Step 0 path; `LOG_SUSPECT` | Pipeline: one conversion | Add contrast by hand or stack a second LUT |
| Harsh, clipped after a LUT | Is Premiere already converting? Which profile is the LUT for? | Pipeline: remove the duplicate; exposure before the LUT | Lower LUT intensity to hide a wrong input |
| Whole clip milky or crushed | `probe` range; `ILLEGAL_*`, p1/p99 | Pipeline or export settings | Crush blacks to compensate |
| Face dark, window bright | p99 and `CLIP_HIGH` on the window; intended silhouette? | Per clip: Shadows/Highlights, or a mask on the face | Promise detail back from a clipped sky |
| Sky blown white | `CLIP_HIGH` in the source frame | Per clip: Highlights/Whites, curve shoulder | Claim recovery of clipped data; say it is lost |
| Flat, no depth | Luma separation of subject vs background (check in black and white) | V4 contrast; per clip local contrast | Default to a strong S-curve or teal-orange |
| Green or magenta cast | `CAST` on a `--neutral` box; light source; green set or wardrobe? | V4 if global, per clip if one shot: Temperature **and** Tint | Neutralise motivated or deliberate coloured light |
| Skin too yellow or orange | `--skin` angle; light; is the look pushing it? | Per clip WB; HSL secondary on skin | Force every face onto 123° |
| Warm lamp plus blue window | Two light sources | Balance for the face; mask the other area or accept it | One global WB to neutralise both |
| Red product or costume too loud | Protected? `GAMUT_EDGE` | HSL secondary on that hue only | Hue-shift a logo, product or ritual colour |
| Sky turned cyan | Input conversion, Hue vs Hue, mask spill | Pipeline, or Hue vs Hue on blue only | Global hue shift |
| Two angles do not match | `compare` against a chosen anchor | Per clip: exposure, WB, contrast, then skin | Demand identical histograms; erase lighting that is really different |
| AI clips each a different tone | `compare` across clips; colour changing within a clip? | Per clip match, shared V5 look | Promise to fix generation flicker with grading |
| "Make it cinematic" / a feel word | Style Card direction and its feel terms | V5 recipe from the term's `dung` | Treat "cinematic" as one fixed preset |
| Export looks different from Premiere | `probe` the export: tags, range; the player | Export settings, not the grade | Add a compensating LUT for one screen |
| Banding in sky or walls | Bit depth of source and export; strength of curves | Ease the curves; light grain; higher export bitrate | Push 8-bit log hard |

Decision order: is the source interpreted correctly → is the "problem" intended (reference, Style Card, motivated light) → global or local → is the information still there → can it be done and verified with the tools here → is it consistent through the clip.

## Working rules

1. **Scope**: grade only what Oxi asked for. One shot asked means one shot changed; a whole-timeline change needs that scope stated.
2. **One group at a time**: change one family of controls (exposure, then balance, then contrast, then saturation), re-measure, then the next. Do not move many sliders at once and judge the sum.
3. **Protect before pushing**: hold skin and protected colours with a qualifier or mask before strengthening the look.
4. **Fault versus intent**: a warm café lamp, blue night, a green stage light or a look in the Style Card is not a defect. When unsure, ask one question or show an A/B.
5. **Mild by default**: start a look at the recipe's low end; Oxi pushes it further if he wants.
6. **Per-clip Lumetri on B-roll is conditional (Oxi, 2026-10-26, KAIYO reference comparison).** Add it only when a B-roll clip's exposure or colour visibly mismatches the talking-head A-roll; on KAIYO the B-roll was slightly off in exposure against the presenter, so Oxi corrected those clips one by one. It is not a default step: clips that already match stay untouched. This is technical matching only; the shared look still goes on the Adjustment Layer (contract item 5).

## Safe sequence setup

1. Preserve the source sequence and create a clearly named review duplicate.
2. Run Step 0 and record the pipeline before grading.
3. Measure representative source frames (`Measuring`): waveform, RGB parade, vectorscope, clipping, skin tone, shot-to-shot consistency.
4. Build the V4 base grade, then make conservative per-clip corrections only on shots that still differ (B-roll against the A-roll: Working rules item 6).
5. Match adjacent shots (`compare` against an anchor) before adding the look.

## Adjustment Layer contract

1. Create or reuse the two dedicated Adjustment Layers: V4 base, V5 look, both above all footage (V1–V3) and below graphics (V6–V9). The adjustment-layer item must match the sequence frame size (check `VideoInfo`); an item made for another sequence covers only part of the frame. Add missing tracks first. On 26.3.2 create the item through the UI (`premiere-mcp.md`).
2. Name them `COLOR_BASE` and `COLOR_LOOK_LUT`.
3. Set their in/out points to the timeline's picture range. Do not extend the sequence, and re-trim both whenever the timeline shortens (`finishing-layout.md`, Finishing QC additions).
4. Verify the target track and time range are free before placement.
5. Apply the creative LUT or shared Lumetri look to this Adjustment Layer, not to the source clips.
6. Default to one creative LUT/look per Adjustment Layer. Do not stack LUTs unless Oxi explicitly approves it.
7. Keep the look conservative by default and independently toggleable for A/B review.
8. If separate scenes need different looks, use clearly named, non-overlapping Adjustment Layers for those scenes.

## MCP execution

1. Use `add_adjustment_layer` at the intended playhead and video-track index. On Premiere 26.3.2 it cannot create the item; create it in the UI, then place it with `overwriteClip` through the file bridge.
2. Re-read the timeline and identify the newly created node.
3. Use `get_clip_adjustment_layer` to prove the node is an Adjustment Layer.
4. Set and verify the layer start, end, track, and name before applying the LUT.
5. Use `apply_lut` with the Adjustment Layer node ID. On Premiere 26.3.2 `apply_lut` cannot set a custom path (`Illegal Parameter type`); choose the LUT in the Lumetri panel (Look or Input LUT › Browse…). Lumetri sliders such as Temperature and Tint can be set by script with `setValue(number, true)` and read back.
6. Read back the Adjustment Layer effects and Lumetri state. Verify the LUT did not land on a source clip.

Some Lumetri operations may report `Invalid parameter` after Premiere has already applied the change. Before retrying, reacquire timeline/QE references and inspect the live component/effect state. Do not stack duplicate Lumetri effects because an API response looked like a failure.

When QE is used to add Lumetri, reacquire QE references after timeline mutations and verify the resulting component by match name, including `AE.ADBE Lumetri`, before continuing.

## Final QC

1. Compare the review sequence with the source using the Adjustment Layer visibility toggle.
2. Measure the review render at the same moments as the "before" set. Sample every scene and every camera or light change, not one hero frame; a single still never passes a whole clip.
3. Mark each item `pass`, `fail`, `not_verified` or `n/a`:
   - pipeline: one conversion per source, matches Step 0;
   - exposure and contrast match the intent; no new `CLIP_HIGH`; `ILLEGAL_*` clean for delivery;
   - white balance and coloured light handled on purpose;
   - skin and protected colours unchanged or changed with approval (`compare` before/after);
   - adjacent shots cohesive (`compare` against the anchor);
   - no new banding, halos or mask edges, checked through motion;
   - titles, logos, overlays and graphics not graded.
4. Confirm sequence duration and audio are unchanged.
5. Save as soon as the live timeline verifies; do not ask first.
6. Report the review sequence, the Step 0 pipeline per source, corrected clips, Adjustment Layer name/track/range, LUT path or look used, the QC list with measured numbers, what stayed `not_verified`, and source preservation.
