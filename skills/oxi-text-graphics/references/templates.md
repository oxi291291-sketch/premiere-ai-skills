# Choosing the template

Read in full before choosing a template. Markers **(Oxi)** and **(default)** mean the
same as in `SKILL.md`.

## The library

**(Oxi)** the assistant chooses, from any of these folders under
`%APPDATA%\Adobe\Common\Motion Graphics Templates` on the edit machine, whichever looks good:

- `Text pack A` (47, Oxi's curated set, look here first)
- `CallOuts_AE_Mogrt` (350, in Center / Left / Right)
- `Series templates` (85; 25 of them are shape transitions with no text)

**(Oxi)** If nothing fits, the assistant may build the text herself, with Premiere text or
Essential Graphics, or in AE.

The library is not in the synced folder. Counts above are the edit machine on 2026-10-01; another machine
must run the catalog on its own library.

## Catalog, then choose by eye

Do not open templates one by one. Run:

```
python -B scripts/mogrt_catalog.py "%APPDATA%\Adobe\Common\Motion Graphics Templates" --out <job>/_work/mogrt_catalog.json --seq <WxH of live seq> --sheets <job>/_work/mogrt_sheets --only-text
```

The script reads only `definition.json` and `thumb.png` inside each `.mogrt` and never
writes into the library. Look at the numbered sheets, then map a number back to a path
through the catalog. Flags:

| Flag | Meaning | Action |
|---|---|---|
| `no_text` | no text control; `pr_set_mogrt_text` has nothing to write | do not use for text |
| `api_too_new` | `apiVersion` above what the installed AE opens (the edit machine AE 2026 opens 2.2) | skip, or ask Oxi to update AE |
| `bad_mogrt` | unreadable zip or definition | skip |
| `orientation` | landscape template on a portrait sequence, or the reverse | warning only; 545 of 561 templates on the edit machine are landscape, so check crop and size on the exported frame |

## Style

- **(Oxi, 2026-10-01)** Use many templates from the library, not one for every text.
  This replaces the earlier default "one main style plus one accent". How to keep the
  variety coherent (one look per role) is in `SKILL.md` "Look and layout".
- **(default)** Prefer a template whose default duration covers the hold without
  trimming its ends.

## Fonts: OXI Design System

**(Oxi, 2026-11-11) Superseded for the assistant's work:** Oxi chooses fonts himself, and
texts stay in the template's own font (`SKILL.md`, "Look and layout"). The notes below
record Oxi's type set and the font-control facts for when Oxi asks for a bulk swap.

**(Oxi, 2026-10-01)** Default fonts are the ones in Oxi's "OXI Design System"
(claude.ai artifact <private artifact> files
`project/tokens.json` and `project/README.md`; read on 2026-10-01). When a client
needs other fonts, Oxi makes a separate template or asks the assistant to swap them in bulk.

| Family (as Premiere lists it) | Design System role | Use in video text |
|---|---|---|
| `SVN-Gilroy` (Bold / SemiBold; installed on the edit machine also XBold, Heavy, Black, Medium, Regular, Light, Thin and italics) | all titles and body | main line, keyword, number, name: Bold/XBold/Heavy; small running words: Medium/Regular |
| `1FTV VIP Betterlett` (script) | secondary title right under a title; not under 20 px, never paragraphs | the small secondary line of a main + secondary pair ("Muốn thay") |
| `1FTV VIP Carien` (decor) | one decorative word or short phrase on a cover/thumbnail; role still awaiting Oxi in the Design System | an occasional single accent word, sparingly |

- **(Oxi, 2026-10-01)** Templates let the text be changed, so set every text to these
  fonts, whatever the template ships with. A bad default font (no Vietnamese glyphs)
  is therefore not a reason to drop a template. The catalog field
  `text_fields[].font_editable` (from `fonteditinfo.capPropFontEdit` in the
  definition) shows whether a template allows this. On the edit machine (2026-10-01), 472 of the
  532 templates with text allow it. Most of the other 60 are Adobe's stock Premiere
  templates (Basic Title, Captions, Credits), which store the font differently;
  that has not been checked. A template that truly cannot change font is used only
  if its font already is one of these.
- **(default)** The Design System's colours (one blue accent, no gold) are a brand
  proposal for pages and thumbnails. Oxi adopted its **fonts** for video, not its
  colours. **(Oxi, 2026-10-01)** Video text colour is chosen from the frame so the
  text does not sink into the picture; see `SKILL.md` "Look and layout".
- Installed on the edit machine (per-user fonts, checked 2026-10-01): all three families. Another
  machine must check its own font list; fonts are not in the synced folder and are not copied
  into the vault.
- Not yet proven: Vietnamese diacritics in the two 1FTV fonts inside a MOGRT (1FTV
  is a Vietnamese foundry, so likely fine), and setting a MOGRT font control by
  script. Check the first frame by eye; until scripting is proven, a bulk swap is
  done clip by clip from the `text_plan` font column.

## Layout from Oxi's reference videos

Oxi sent four portrait (1080×1920) reference videos on 2026-10-01 as "the ways to
place text". Analysed from frames every 2 s, plus closer looks at some moments. The videos are in Oxi's
`Downloads` on the edit machine and are not copied into the vault.

| # | Video | What to take from it |
|---|---|---|
| A | AE caption tutorial (dark room, man at desk) | Word-by-word captions in one heavy sans, white; big word + smaller word stacked, set in the empty part of the frame (wall, dark space beside the person), never on the face; blur-and-fade in |
| B | "Nên mua ATK X1 hay ATK F1?" (Vietnamese tech review) | Closest to Oxi's jobs. Hook title at top above the head: big white "ATK" + outlined "X1 HAY F1?". Running sub in small bold white caps at chest height. A **keyword gets a coloured box** (blue fill) inside the sub line. A short label sits **on the product itself** ("X1" on the mouse). |
| C | Real-estate listing (Vancouver Island) | Text only in the first ~20 s (the spoken intro), then pure picture. Mixes a bold sans, a handwritten script word and a serif in one phrase; one accent colour (mint or yellow) on one word; text in sky or driveway; once the video shrinks into a rounded card with text around it |
| D | Real-estate agent reel (woman in black dress) | Small thin italic white for the running words + one **huge bold coloured keyword** (NOT, $1M, $300K, Events, the same, hard work, STEP); **the colour changes almost every keyword** (red, yellow, pink, mint, blue, orange, purple); outline word behind a filled word (MAX / Exposure); big keywords sit **behind the person's head** |

**Rules taken from all four (Oxi, through the references):**

- Two layers of text: small, light running words + a big, bold, coloured keyword.
  The keyword is 3–5× the height of the small words.
- Text goes into empty space: above the head, beside the body, sky, wall, floor. Small
  running words go at chest/waist height; big keywords go above or behind the head.
  Never across the eyes or mouth.
- Mix 2–3 fonts in one phrase (heavy sans + thin italic or handwritten script, or a
  serif for a number or address).
- Colour: white for small words; keywords take an accent colour that changes over the
  video (D changes almost every keyword; C keeps one accent). This agrees with the
  2026-10-01 rule "change the look now and then" in `SKILL.md`.
- Numbers and prices are the biggest text on screen ($1M, $345K, 430).
- A word can be marked inside a line with a filled box (B) instead of a separate text.
- Label an object by putting its name on the object (B: "X1" on the mouse).

**Feasibility on the edit machine** (not yet proven). **(Oxi, 2026-10-01)** the assistant does only the
"doable now" rows; the effect rows (word-by-word, behind the subject, card) are out of
scope unless Oxi asks for one by name:

| Technique | Route | Status |
|---|---|---|
| Position, size, colour, font per text; main + secondary pair | MOGRT controls + Motion | doable now |
| Keyword in a filled box | MOGRT with a box/shape layer, or Premiere shape + text | doable now; find a box template in the catalog |
| Label on an object | position on the frame; static shots only unless tracked | doable now for static shots |
| Word-by-word captions (A, D) | Whisper word times exist; needs one clip per word or an AE script | possible, untested; this is sub-style and replaces the sub, so ask Oxi per video |
| Text behind the head/body (D, A) | needs a subject matte (AE Roto Brush, or Premiere object masking if available) | untested, costly per shot: use for the hook and 1–3 key moments only |
| Video shrunk into a rounded card (C) | Premiere Motion scale + rounded mask, or a template | untested |

## Speech-led text from Oxi's revision **(Oxi approved, 2026-10-29)**

Source: read-only comparison of Oxi's revised `Product D_text_v1` against
the assistant's text handoff; Oxi approved recording these lessons on 2026-10-29.
Local evidence: `<local path> ULT Tower 5/6. AI/music-sfx-20261029/`
(`comparison.json`, `revision-full.json`, `OXI-REVIEW-1.jpg` through `-5.jpg`,
`BAN-GIAO-NHAC-SFX.md`). Structure and sampled frames were checked; continuous
playback was not reviewed. The principles below were approved, not every setting
or spelling in that project.

- **Meaning and delivery before template.** Read the spoken stress, joke/reaction
  and action in the shot, then choose the words, grouping and readable reveal;
  choose the template last. A technically correct label at a sentence boundary
  can still flatten the performance.
- **Reveal a thought in short phrases.** The hook advances through the complaint,
  question and reaction, with separate "<chữ trên hình>" and "<chữ trên hình>" cues. Use that approach
  where the delivery changes; do not turn every spoken word into an animated
  caption or build custom effects under this text-only scope.
- **One clear hierarchy per group.** Name/category can be secondary to the product
  or key number: "SONY / ULT TOWER 5", "WOOFER / 230mm". Related layers may enter
  separately and remain visible together. Choose their spacing, size and reveal
  from this shot and voice; the observed roughly 0.3 s stagger is an example,
  not a preset. Make the important number easy to catch, with its unit/context
  readable, while preserving the face, hands and product.
- **Attach a label to the evidence.** Put distance labels on the corresponding
  listening position, mode labels on the actual test and an Echo label on its
  controls. For a claim or number, keep the existing Script Map/audio fact check;
  a label must not imply an unrecorded test or prove an unsupported specification.
- **Sequence an explanation as it is spoken.** A charging-time/result pair can
  reveal the input first and result second. Do not show both results early just
  because a two-line template has room.
- **Colour supports roles and contrast.** This revision uses cyan/purple/white
  with yellow on price. Keep a coherent distinction between supporting text,
  keyword and number, but select the palette for the approved job and background.
  Do not make this project's colours or font sizes universal defaults.

Record related layers and their spoken/picture anchors in the same plan group.
Check the whole group at entry and hold, not just each clip in isolation. Use the
shared speech/waveform timing route for the readable reveal and report the actual
playback coverage separately from still-frame inspection.

## Default position: lower third **(Oxi, 2026-10-19)**

Oxi, in the chat: "thường anh sẽ đặt 1/3 bên dưới khung hình, nếu nó che mất vật thể
các thứ ở chỗ đó thì anh mới đặt text chỗ khác".

- Start every text in the lower third, centred (normalised Motion x 0.5). On a
  1080×1920 talking shot that put the main line at about y 0.69–0.72 and its
  secondary line just under it (≈0.76).
- Only move it when, at that spot, it would cover something in the picture: hands,
  a held object, the product. Then pick the nearest empty band, not the face.
- Keep the whole block, secondary line and animated extent included, above the
  TikTok bottom interface (roughly y 0.80 and below).
- Worked example (`JOB_K_test`, #26): at the lower third the closing pair
  sat on the MC's clasped hands, and lower still was the interface, so the pair
  went up to y 0.54 / 0.607, above the hands and under the chin.
- What went wrong first: the run before this rule copied the off-centre high
  example from Oxi's 10-17 revision (x 0.57, y 0.33–0.41) to every text. On a
  medium shot the mouth is near y 0.30 and the chin near 0.35, so the text sat on
  the face, and the frame check wrongly passed it. The 10-17 coordinates are one
  shot's choice; this rule is the default.

## MOGRT traps on the edit machine

### Learning from Oxi's Job K revision (2026-10-17)

Read live, read-only, at Oxi's request on
`JOB_K_01_FULL_DIALOGUE_CLEAN_REVIEW_text_v1`. Evidence:
`work/2026-10-16-job-k-01/_work/oxi-revision-learning-20261017.json`.
These are observed choices for this video, not fixed settings for later jobs.

- Read the picture's existing titles before adding another. Oxi removed the added
  `18/10`, `<chữ trên hình>`, and `<chữ trên hình>` clips; do not infer their information
  should disappear when the picture already carries it.
- A subtitle can become emphasis text: `<chữ trên hình>` and the shortened
  `<chữ trên hình>` moved to V10 with Bagel and All Caps. Choose the role from
  meaning; do not preserve the original SUB_/T label as a design decision.
- Keep a main/secondary pair readable as a pair. Oxi enlarged `<chữ trên hình>`
  from font size 64 to about 88 and `<chữ trên hình>` to about 98, and tightened
  the pair's spacing. Exact values depend on the template and Motion Scale.
- Position from the shot, including off-centre or higher empty space. For example,
  `<chữ trên hình>` moved from normalized Motion (0.5, 0.64) to about
  (0.576, 0.366), Scale 69. Never turn these coordinates into a universal preset;
  the default is the lower third (section above).
- Split emphasis as the spoken thought changes: `<chữ trên hình>` is followed
  by a separate future-development phrase; `<chữ trên hình>` is followed by
  `<chữ trên hình>`. Inspect actual text controls, not duplicate clip names.
- Oxi's direct correction in this conversation: leave room for TikTok's bottom
  title/interface, not merely for subtitles. Check the complete rendered block,
  including secondary text and animated extents, against the publishing layout.

The revised example contains a probable typing error (`<chữ trên hình>`). It is not a
spelling preference to learn, and a read-only learning request does not authorize
correcting it in the project.

- **Hang on `Loading Motion Graphics Template...`**: the background `AfterFX.exe`
  launched by Dynamic Link is stuck. Measure CPU of AfterFX, dynamiclinkmanager and
  Premiere over 6–8 s; if all three stay at zero, end `AfterFX` and
  `dynamiclinkmanager` only. **Never end Premiere** while the project is unsaved; it
  comes back out of the dialog by itself. (JobM.prproj, 2026-08-29)
- **`please install After Effects 2026.0`** does not mean AE is missing. The mogrt's
  `apiVersion` is newer than the installed AE can open; the catalog's `api_too_new`
  flag predicts it. In August 2026, AE 26.3 failed on api 2.2. After Oxi updated AE,
  api 2.2 opened.
- Whether a template was authored in AE or in Premiere (`authorApp`) does not decide
  this. `apiVersion` does.
- **Digits turn into an "HF" badge** in font `BirdsofParadise-PersonaluseOnly`
  (the script line of `504 Giau co dien`, also used in `534 chu gach chan`). It is
  a personal-use demo font: every digit renders as a watermark glyph, so `thứ 2`
  showed a badge on the frame. Write numbers in words (`thứ hai`) or switch that
  line to a full font, then check the frame. Personal-use also means a paid
  booking may need a licensed font; ask Oxi. (JOB_K_test text, 2026-10-19)

## Proven on the first real run

Job G, sequence `JOBG_text_v1` (1080×1920, 23.976), 29 texts on V6, 2026-10-01.

**Templates tried**

| Template | Result |
|---|---|
| `Text pack A/Chu Apple` (font Mytupi-Bold) | Its default font lacks Đ/Ồ; those letters fall back to a thin, different font. The template lets the font be changed (Oxi set it to SVN-Gilroy on 2026-10-01; since 2026-11-11 font changes are Oxi's, so list it for him rather than swapping). Its definition has `capPropFontEdit: true`, like Huynh quang. The note written here earlier, "font cannot be changed", was wrong: it was based on the two named controls (text, colour) and missed the font edit inside the text control. A Gilroy Chu Apple has not yet been checked on a frame. |
| `Text pack A/Huynh quang` (font SVN-GilroyXBold) | Works. All diacritics render in one font. 7.6 s long, no protected region, ~0.3 s fade/glow in and **no exit animation** (the last frame still shows the full text), so trimming the tail is safe. Text field `param_name` is `"fluorescent  "` (two trailing spaces). Controls (Properties panel): text, font family (SVN-Gilroy), font style (XBold), Font Size (124), gradient start/end colour, glow strength/radius. |

The `SVN-*` fonts were built for Vietnamese; check the font name in the catalog first.

**Placing**

- `pr_import_mogrt` / `seq.importMGT` is an **overwrite** edit. Importing onto a
  stretch that already holds a clip cuts that clip's tail. Import all texts in time
  order in one ExtendScript call, then set each `clip.end`; never fire imports in
  parallel on one track.
- `pr_set_mogrt_text` with `param_name` works on a real job; ten calls in parallel are
  fine (they touch different clips).
- Trimming the tail: allowed only when the template has no exit animation (look at its
  last frame). The rule in `SKILL.md` step 4 still holds for templates that animate out.

**Landscape template on a portrait sequence**

- Premiere places the 1920-wide template at its own size in the centre (Position 0.5,
  0.5; Scale 100); nothing is fitted.
- Huynh quang at Scale 100 is about 69 px per character, so a 15-character line is
  ~1036 px on a 1080 frame. Set Motion Scale per clip:
  `scale = min(100, 900 / (69.3 × characters) × 100)`. (900 px, not 920: at 920
  "<chữ trên hình>" came within ~10 px of both edges.)
- Centred text sits at chest height on a medium shot, under the face. It crossed the
  welder's hands on one B-roll shot; for a final, move it up or down there.
- Yellow-gold text on brass instruments is readable but low contrast. For a final,
  raise the glow or add a darker gradient on those shots.

**Checking frames**

Preferred on the edit machine (2026-10-19): export the frame from the active sequence through
the QE DOM over `pr_file_bridge`:
`app.enableQE(); qe.project.getActiveSequence().exportFramePNG(tc, path)`, where
`tc` comes from `Time.getFormatted(settings.videoFrameRate,
settings.videoDisplayFormat)` and `path` has no extension. The path must use
Windows backslashes; forward slashes fail with "Unknown error exception". Put the
frames into a contact sheet and look at each one. `pr_export_frames.py` in
`oxi-premiere-workflow/scripts` wraps this call; use it for the composition gate
(`oxi-premiere-workflow/references/composition-gate.md`), which measures face,
protect-box and 9:16 safe-zone collisions instead of judging them by eye.

`pr_export_sequence_frame` failed on the edit machine. Fallback, the Program Monitor:
`pr_set_playhead_position` to the middle of the hold, click the Program tab, press
`` ` `` to maximize the panel, zoom the screenshot on the frame, press `` ` `` again.
Needs computer-use access to Adobe Premiere Pro 2026.

## Margin and centering correction (Oxi, 2026-10-31)

Oxi rejected Product D text_v2 for hugging edges and drifting left. Start from the visible block centered on the full video frame (x=0.5); do not center the entire job on an asymmetric app-UI rectangle. Constrain width within both side insets while keeping readable type. Motion Position is the template anchor, not proof that its glyphs are centered: check the rendered block. Prefer size or a meaningful line break over a global horizontal shift. Report edge distances and inspect the full frame. Gate geometry PASS alone is not visual layout approval. Job-specific numbers do not become universal presets.

Oxi correction (2026-10-31, reaffirmed 2026-11-11): if the two visible lines look too far apart in the rendered frame, put each line in its own text layer. In Premiere, use adjacent graphics tracks when a template exposes only one usable text layer. Keep one cue group in the plan, with the font, scale, position and reveal of each layer. Center each visible line on the full frame unless the shot requires a documented exception. Measure the gap from the bottom of the upper glyphs (including descenders) to the top of the lower glyphs (including Vietnamese diacritics), then check that the lines read as one unit at phone size. Adjust each layer independently and recheck the combined block against safe margins at entry and hold. Keep the main line dominant and preserve readable type size. Choose the gap for the actual font pair and shot.

### Approved result (Oxi, 2026-10-31)

After reviewing the corrected Product D text_v2, Oxi said "chữ căn giữa đặt vậy là okey"
and explicitly asked to record it in this skill. Approved reusable approach:
- Center the visible text block on the full frame, with balanced side spacing.
- For two-line groups, use two text layers when the template leading is too large;
  center each line and control their visible gap and main/secondary hierarchy.
- Keep long lines readable by splitting meaningful phrases, then choose their size.
- Check actual exported frames; template anchors and a geometry PASS alone do not
  establish visual centering or comfortable spacing.

This approves the centering and two-layer spacing approach. It does not approve
Product D's exact coordinates, scales, colors, 56% width cap or gate margins as universal
presets, nor does it certify continuous playback. Local evidence:
`<local path> ULT Tower 5/6. AI/work/text-v2/TEXT-V2-SPLIT-QC.jpg`
and `verification-spacing.json`.
