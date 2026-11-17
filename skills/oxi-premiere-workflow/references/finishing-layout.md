# Finishing layout

How Oxi's own finished sequences are built. Read this before assembling any deliverable that is meant to look like a published video, and before judging whether a dialogue cut is "done".

**Finishing order (Oxi, 2026-10-14):** denoise → music → transitions → colour → sub → final QC → export (`export.md`). Each part is its own stage; stop for Oxi after each. Skip a part outside the agreed scope, never reorder.

**Effects/element (Oxi, 2026-10-27):** after reviewed key text and before this
finishing order, run the separate graphics stage in [effects.md](effects.md)
when in scope. Create HyperFrames/Remotion companion assets, import and verify
them over the live edit, then stop for Oxi's review. Cut transitions remain
their own finishing stage below.

A dialogue cut is a **spine**, not a deliverable. Oxi's finished sequence carries roughly three times as many timeline objects as the dialogue spine that started it, spread over a fixed track layout. Building the spine on V1+A1 alone and calling it finished is the single largest gap between an assistant cut and Oxi's own.

## Track map

Observed on `ProductC_5-6PHUT` (2026-08-27) and consistent with earlier finished work. Use these indices when placing anything; do not invent a new layout.

| Track | Content |
|---|---|
| V1 | Presenter / MC camera. **Does not need to cover the timeline.** |
| V2 | Primary B-roll — product, detail, demonstration shots. |
| V3 | Secondary B-roll, nested sequences, reference footage. |
| V4, V5 | Full-length adjustment layers carrying Lumetri Color: V4 `COLOR_BASE` (base grade), V5 `COLOR_LOOK_LUT` (look). Rules: `color-grading.md`. |
| V6-V9 | Motion graphics and text: `Chu Apple` callouts (with double Drop Shadow; its default Mytupi-Bold lacks Đ/Ồ, and fonts are Oxi's choice since 2026-11-11, so list it for him), `Bong bong` bubbles, `Truot vao tu tren` / `Truot vao tu phai` slide-ins, arrow makers. Which lines get text, and how: skill `oxi-text-graphics`. New HyperFrames/Remotion elements use free graphics space under `effects.md`, preserving existing text. |
| V10 | Adjustment layers used as transitions — placed in **back-to-back pairs** across a cut. |
| A1 | Dialogue. Contiguous, no gaps. |
| A2, A3 | SFX, mostly `Swoosh_*.wav`, aligned to the V10 transition pairs. |
| A4 | Music bed, 2-3 tracks with a crossfade at the change. |

## Cut dialogue independently of picture

This is the rule that changes the whole method.

- **A1 is the spine and must be contiguous** — every dialogue decision is made on audio alone.
- **V1 is placed separately and is allowed to have gaps.** On `ProductC_5-6PHUT`, A1 ran 89 clips across the full 323.29 s with zero gaps, while V1 was 45 clips totalling 178.21 s with 6 gaps: the presenter is on screen barely 55 % of the time. The rest is B-roll on V2/V3.
- Because picture is independent, a dialogue join never has to preserve a usable picture boundary. **Stop snapping dialogue cuts to original clip boundaries to protect the visual.** Cut the sentence where the sentence should be cut, then decide separately whether that moment shows the MC or a cutaway.
- Audio is cut far finer than picture. Expect roughly **2 audio clips per video clip** (89 vs 45). A dialogue pass that produces exactly one audio clip per video clip has been constrained by the picture and is under-edited.
- Cut audio and picture at different moments on purpose (J/L cuts). Matching every A cut to a V cut is what makes an edit feel like a slideshow.
- Practical consequence: build A1 first and verify it end to end by listening, **then** lay picture over it.

## Transitions

For a new transition choice, read [assets.md](assets.md): rhythm and motion
knowledge → `transition` techniques → compatible library transitions/plates and
SFX. Reuse the approved Style Card and preserve the topic-change placement rules
below. A template does not authorize installing a dependency or adding SFX out
of scope; verify its actual motion and cue against the adjacent shots.

- Oxi uses **zero** dissolve transitions on V1/A1. Verified: `transitions.numItems` = 0 on both.
- A transition is instead a **pair of adjacent adjustment layers on V10**, about 1.6-1.8 s each, straddling the cut, carrying Motion and Opacity keyframes (whip / zoom style), usually with a `Swoosh_*.wav` on A2 or A3 at the same frame.
- Do not add cross dissolves to a sequence being finished in this style.
- **(Oxi, 2026-10-26, KAIYO reference comparison)** Transitions go **only at topic changes**, never on every cut: about 9 in a 4.7-minute video. The pair is split exactly at the topic cut; on KAIYO the halves were about 2.17 s and 2.83 s, so pair length varies by job and the 1.6-1.8 s above is not fixed. The effect read from the `.prproj` was Film Impact Cross Zoom / Whip (inferred from the project file, not confirmed in the UI). The swoosh starts about 0.25 s **before** the cut, not on the same frame.
- Transition style comes from `<job>/style_card.json`, direction `chot`, field `chuyen_canh` and the transition part of its `phong_cach_dung` style files (e.g. `beat-sync` whips only on music-led passages) (`oxi-visual-style/references/style-card.md` section 5); terms in `oxi-visual-style/references/tu-dien-visual-art.md#10-dung-nhip` and `#14-chuyen-dong`. If `chot` is empty, ask one question to pick a direction first.

## Seeing the footage

There is no excuse for planning a picture edit blind. Index the shoot once with `scripts/segment_sheets.py` and look at every sheet, as `footage-index.md` describes. That file also holds the feature X lesson: index before the dialogue plan, and never drop an idea that has purpose-shot footage.

For a fast overview of many clips at once, tile one mid-point frame per file into a single 7x3 grid — 21 clips per image — and use the per-file sheets only where the overview looks promising.

## Source inventory

Inventory the **whole project bin** before planning, not only the files that contain dialogue.

`ProductC_5-6PHUT` drew on 11 MC files (C9756-C9769) plus roughly 15 separate B-roll files (C9709-C9754) and 3 downloaded reference clips. A plan built from the 7 files that happened to contain the script's spoken lines is missing over half the material Oxi will actually use, and will silently under-serve the picture edit.

Two things to check in that inventory, both found on the Product A job (2026-09-28):

- **Rotation.** client vertical footage can arrive as 1920×1080 with no rotation metadata, the picture lying on its side. Build a 1080×1920 sequence and set Motion Rotation 90° (scale 100 fills the frame); a few files may lie the other way and need −90°. Render contact sheets with `transpose=1`, or they are unreadable.
- **Dialogue hiding in B-roll.** The presenter may record the reads off-camera on one file (holding a phone) and say the test openings and reactions live, on the B-roll takes. Transcribe the B-roll too; the in-scene line is usually the one Oxi keeps.

## Clip length calibration

From the finished A1: median dialogue clip 3.64 s; only 4 of 89 clips under 1 s; 10 over 6 s. Treat **1.0 s** as the practical floor for a dialogue fragment, not 0.40 s — a sub-second dialogue clip in a finished edit is rare and deliberate.

## Music

Two tracks, 6 clips, 303.5 s of a 323.3 s timeline — about **94 % coverage**, with an audio transition at the track change. Music is not decoration added at the end; a finished deliverable is scored nearly wall to wall.

Coverage is not the goal on its own: change tracks by section and drop the music out under key lines (`music.md`, Music structure and SFX accents).

## Finishing QC additions

Beyond the checks in `timeline-qc.md`:

- **Re-trim every full-length adjustment layer after the final duration is set.** On `ProductC_5-6PHUT` the V4/V5 Lumetri layers still ran to 343.74 s over a 323.29 s timeline — 20.45 s of grade hanging past the last clip. Trim them whenever the timeline shortens.
- Confirm each V10 transition pair actually straddles a V1/V2 cut at a topic change, and that its SFX starts at or just before the cut (about 0.25 s early on KAIYO).
- Confirm the music bed ends with the picture, not before or after it.
- Report per-track clip counts and end times, not just the sequence duration.
