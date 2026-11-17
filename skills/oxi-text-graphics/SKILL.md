---
name: oxi-text-graphics
description: Chặng text (chữ nổi bật) cho một sequence Premiere đã đổ B-roll và được Oxi sửa xong — chọn câu key, số liệu, tên, câu chốt trong timeline live, chọn mẫu MOGRT đẹp trong Graphics Templates (Text pack A, CallOuts, Series templates) hoặc tự làm chữ, đặt lên V6–V9, ẩn sub ở đoạn có text, kiểm dấu tiếng Việt trên frame xuất ra. Dùng khi Oxi nói làm text, làm chữ, chèn chữ, chữ nổi bật, text key, title, tiêu đề mở đầu, callout, lower third, tên nhân vật, highlight từ khóa, mogrt, Graphics Templates, Essential Graphics, hoặc bảo B-roll xong rồi giờ làm chữ — kể cả khi anh không gọi tên skill. Chạy lại sau mỗi lần Oxi sửa cut. Không phải phụ đề/SRT (sub) — phần đó là oxi-premiere-workflow.
---

# OXI Text Graphics — chặng chữ nổi bật

Taught by Oxi on 2026-10-01 on job Job G. Lines marked **(Oxi)** are his
decisions. Lines marked **(default)** are the assistant's working defaults that Oxi has
not reviewed yet; change them when he corrects one.

Where this stage sits:

```
oxi-script-craft / oxi-explore-vlog        (content contract, Script Map)
            │
            ▼
oxi-premiere-workflow                      (dialogue cut → spine A1 + V1)
            │
            ▼
      OXI CORRECTS
            │
            ▼
oxi-broll-editor                           (B-roll on V2/V3)
            │
            ▼
      OXI CORRECTS
            │
            ▼
      THIS SKILL   ──►  text_plan  +  MOGRT/text on V6–V9  (+ trimmed SRT copy)
            │
            ▼
      OXI CORRECTS
            │
            ▼
oxi-premiere-workflow                      (sub, colour, music, transitions, final QC;
                                            Oxi checks after each part)
```

**(Oxi, 2026-10-01) Stop at the end of this stage.** Save, report with evidence, and
wait for Oxi to check and correct the text. Do not go on to sub, colour or music in
the same run. The stage rule lives in
`oxi-agent-brief/references/video-editing.md` section 4.

The input is always the live sequence Oxi last corrected. His corrections moved the
timecodes, so a plan or transcript from an earlier stage is expired. Read the
sequence fresh on every run.

## Text is not sub

- **(Oxi)** Text and sub are one family, but they do different jobs. A sub shows the
  spoken words for viewers who watch without sound; it is basic, and some videos skip
  it. Sub belongs to `oxi-premiere-workflow/references/subtitles.md`.
- **(Oxi)** Text sits only on the key, standout lines and the important information.
- **(Oxi, corrected 2026-10-01)** How many texts, and where, comes from the content,
  not from the clock. Read the transcript of the cut Oxi approved and put a text on
  every line that is a key, standout point, and on nothing else. There is no fixed
  interval and no target count; two key lines close together both get text, a long
  stretch with no key line gets none. (The first draft said "one text every 10–15 s";
  Oxi replaced it.)
- **(Oxi)** Too many texts is fine; Oxi trims afterwards. When unsure whether a line is
  key, give it a text. Place straight from the plan; no approval round before placing.
- **(Oxi)** When a text and a sub would be on screen together, hide the sub for that
  stretch.
- **(Oxi, 2026-10-01 review of the first run)** Key text is not only numbers and names.
  Any word the speaker leans on is a key: a single word or a short phrase is enough
  ("đo đạc", "tính toán", "hoàn toàn bằng tay"). The first run missed many of these.
- **(default)** Put the keyword on screen (1–6 words), not the whole spoken sentence.
  The reference edit Oxi chose for Job G highlights only the keyword.

## Look and layout **(Oxi, 2026-10-01 review of the first run)**

- Use the variety in Oxi's Graphics Templates library; do not put one template on every
  text. Each template's own controls (text, font, colour, size; see the Essential
  Graphics / Properties panel) may be changed to fit.
- Look at the frame **before** placing each text and choose where it goes and how big:
  never over a face or the main subject, and not so big it dominates the shot.
- **(Oxi, 2026-10-19) Default position is the lower third of the frame.** Move a
  text elsewhere only when, at that spot, it would cover an object, hands or the
  subject; keep it above the TikTok bottom interface. **(Oxi, 2026-10-17)** Also keep
  clear of the subtitle zone: a text sitting so low it nearly touches the sub must move
  up ("chữ hơi thấp sợ dính vào phụ đề"). Details and a worked example
  in `references/templates.md`, "Default position: lower third".
- A main + secondary pair is a valid design: a small secondary line (often a script
  font) above or beside a big bold main line, e.g. "Muốn thay" + "<chữ trên hình>",
  placed off-centre in empty space.
- **(Oxi, 2026-10-26, KAIYO reference comparison) Size follows length.** A long
  phrase is set small (about 72-91 % scale on KAIYO); a short punchy word is set big
  (about 132-235 %). One size for every text is wrong in both directions.
- **(Oxi, 2026-10-01)** Variety by role, so the video does not look random: each role
  (name/title, number, emphasis word, main + secondary pair) has its own look.
- **(Oxi, 2026-10-01)** But change the look now and then so it stays fresh; one colour
  for the whole video is too flat (the first run used one template and one gold for
  all 29 texts).
- **(default, not yet reviewed)** How to change it: give each role 2–3 variants
  (another template, or the same template with another colour) and switch
  variant at a new section of the story, not on every text. Never use the same
  variant on more than ~4 texts in a row.
- **(Oxi, 2026-10-01) Scope: place the text right, no effects work.** the assistant's job
  is choosing the key words, the template, colour, size and position. Use only
  the animation already inside a template. Do not build effects: text behind the
  subject, word-by-word captions, shrinking the video into a card, custom keyframed
  animation. Oxi does those himself if he wants them.
- **(Oxi, 2026-11-11) Oxi chooses fonts himself.** Leave every text in the font its
  template ships with; do not set, swap or propose fonts. Font is decided by Oxi
  after placement. Template choice still matters: when a template's font breaks
  Vietnamese diacritics on the frame, choose another template or list that text for
  Oxi (step 6). Record the font of every text in `text_plan` (step 2) so Oxi can swap
  them in bulk. This replaces the 2026-10-01 rule that set every text to the OXI
  Design System fonts.
- **(Oxi, 2026-10-01) Text colour is chosen from the frame so the text never sinks
  into the picture.** Look at the area where the text will sit for the whole hold and
  pick a colour that stands out from it. **(default)** How:
  - Read the region's brightness and dominant colour on a frame from the middle of
    the hold (and the first/last frame if the shot moves).
  - Bright region → dark text, or white with the template's stroke/shadow. Dark
    region → white or a bright accent. Never a colour close to the background's own
    (the first run's gold on brass was the failure case).
  - Aim for a clear contrast: about 4.5:1 for small running words, 3:1 for big bold
    keywords. Busy background where no colour reaches it → move the text into
    calmer space, or use a template with a box behind the text.
  - Within that, keep the role looks and "change the look now and then"; contrast
    decides between variants, it does not make every text a random colour.
- Layout rules from Oxi's four reference videos (two layers of text: small light
  running words + big bold coloured keyword; empty space only; mixed fonts; numbers
  biggest; keyword box; label on object; what is feasible on the edit machine) are in
  `references/templates.md` "Layout from Oxi's reference videos". Read it before
  choosing positions.
- **(Oxi approved, 2026-10-29)** Plan the spoken beats, picture and main/secondary
  hierarchy before choosing a template. Use successive short phrases for a hook
  or a changing thought, and group related layers as one design. See
  `references/templates.md`, "Speech-led text from Oxi's revision". This uses
  existing template animation; it does not expand the effects scope above.
- **(Oxi, 2026-11-11)** For look ideas (keyword accent colour, font pairs, size by
  weight) see `references/idea-board.md`, nine reference pins Oxi chose, with what
  fits this stage and what belongs to effects.

## What this skill protects

1. **V1, V2/V3 and A1 do not move.** Oxi approved the dialogue and the B-roll. Clip
   counts and starts on V1, V2, V3 and A1 must be identical before and after. This is
   an acceptance condition, not a promise.
2. **No wrong fact on screen.** A wrong number or name on screen is worse than none.

## Track map — read it, do not copy it

Oxi's track layout lives in `oxi-premiere-workflow/references/finishing-layout.md`.
Read that file; do not copy the table here (one fact, one home).

This skill may touch **V6–V9** only. `pr_import_mogrt` takes a 0-based
`track_index`: V6 = `5`, V9 = `8`. Getting this wrong puts text inside the grade
layers on V4/V5 or over the picture tracks.

## Connector — the `pr_*` names in this skill are Higgsfield's

The primary connector is **MCP Bridge** (`premiere-pro-mcp`; Oxi, 2026-11-05,
confirmed 2026-11-15). The connector rule lives only in
`oxi-premiere-workflow/SKILL.md`, "Current Premiere connector"; read it there.

`pr_ensure_tracks`, `pr_import_mogrt`, `pr_set_mogrt_text`, `pr_get_active_sequence`
and `pr_export_sequence_frame` are **Higgsfield** tools, written when Higgsfield was
the only connector. Use them verbatim only when Oxi selects Higgsfield for the job.
On MCP Bridge take tool names and parameters from `get_capabilities` of the installed
build. **No verified name map exists yet** (noted 2026-11-15), and machines may carry
different `premiere-pro-mcp` builds with different tools: check the installed build,
do not guess names from this skill. `editorial-qc.md` in the sibling Premiere skill
reads MOGRT text on MCP Bridge with `get_mogrt_component`.

Whichever connector runs, prove these on **one** text in a duplicated sequence before
the batch:

1. A MOGRT import is an overwrite edit at the template's full default duration: the
   target range on V6–V9 is empty first, and nothing on any other track changes
   (same trap as "Dedicated track for MOGRT subtitles" in
   `oxi-premiere-workflow/references/subtitles.md`).
2. The track index is 0-based and lands on V6–V9.
3. The text field holds the planned words when read back from the clip, not merely in
   the call's return value.
4. A fresh timeline read after each batch shows V1, V2, V3 and A1 identical.

An uncertain mutation is never replayed through the other connector
(`oxi-premiere-workflow/SKILL.md`).

## Mandatory preflight

1. Run `scripts/verify_current.py` if `Skills/_versions/oxi-text-graphics/CURRENT.json`
   exists. Continue only on `validated-match`.
2. Say `Đã nạp workflow: oxi-text-graphics` before the first action. Start from
   `oxi-agent-brief` for the deliverable, scope and job state; reuse an agreed brief
   and only update what changed. Handed over at the text stage, keep dialogue and
   B-roll as locked; do not send the job back to an earlier stage.
3. Read `oxi-premiere-workflow/references/finishing-layout.md` (track map) and
   `oxi-premiere-workflow/references/premiere-mcp.md` (mutation verification,
   per-session node IDs, safe sequence pattern). This skill does not repeat them.
3a. Read the Text section of the job's video-type profile (`<job>/video-type.md`, row
   "Hồ sơ" → `oxi-premiere-workflow/references/video-profiles/`): density, hierarchy and
   Oxi's measured numbers for that type. No profile: say so in the report.
3b. Read `<job>/style_card.json`, direction `chot`: fields `chu`, `palette` and the
   text-group `terms` (`oxi-visual-style/references/style-card.md` section 5). Look
   terms up in `oxi-visual-style/references/tu-dien-visual-art.md#09-chu`. If `chot`
   is empty, ask one question to pick a direction before placing text. When the
   direction has `phong_cach_dung`, read the Text section of those style files in
   `oxi-visual-style/references/editing-styles/`; animated parts (kinetic, masks)
   stay with the effects stage, and a running-caption style (`hormozi`) means
   key text must not duplicate the sub.
4. Check live: Premiere open, which project, which sequence is active, its frame size.
   Synced notes are not evidence.

## Process

### Step 1 — Transcript of the cut Oxi approved after B-roll **(Oxi)**

Export the audio of the sequence Oxi signed off after correcting the B-roll, and
transcribe it with Whisper turbo `vi` with word timestamps (the approved settings
from the `Subtitle / SRT` route in your workflow index; `--output_format all`). Keep
the timecoded text file (`.srt`) for reading and the `.json` for word times, in
`<job>/_work/`. Reuse an earlier transcript only after confirming A1 still matches it
clip by clip; Oxi's B-roll corrections can touch A1 too.

### Step 2 — Choose the moments

1. **(Oxi)** Read the whole timecoded text file, start to end. Mark each line that is
   a key, standout point: a number, a name, a payoff, the important information. The
   choice is made by what the line says, never by spacing it out over time.
2. Take the word times of each marked line from the `.json` as navigation anchors.
   **(Oxi, 2026-10-20)** Read
   `../oxi-premiere-workflow/references/speech-waveform-timing.md` and refine
   each key's timing from the actual voice and measured waveform. Record its
   spoken anchor and any reviewed timing override in the plan.
3. Separate unrelated messages so they do not compete on screen. A deliberate
   main/secondary group may overlap on different tracks: plan its positions,
   hierarchy and per-part reveals together. Moving a competing message one track
   higher does not solve a visual collision; shorten or sequence its hold instead.
   Never overwrite a clip on the same track to make room.
4. **(default)** A fact on screen (number, record, price, name, title) must be said in
   the audio **and** appear in the script (Script Map from `oxi-script-craft`, the
   **rightmost populated feedback column**), spelled the same. If it is only spoken, the
   two disagree, or the transcript is unsure of a digit, ask Oxi before showing it.
5. Write the plan as a table: time in, time out, on-screen words, template, font
   (family + style), track, reason (why the line is key). The font column is what a
   bulk font swap for a client works from. Save it as `<job>/_work/text_plan.md` (or `.json`);
   it is the ledger for a rerun.
6. **(Oxi, 2026-10-26, KAIYO reference comparison) Fewer, shorter, tied to the picture.**
   - A text must add something. Drop a label that repeats the speech in the same words
     or tells nothing the voice and picture do not already give; Oxi removed about 12
     of the assistant's KAIYO texts, spec cards among them. Marking a line as key
     (item 1) is not enough on its own.
   - Hold about 1-3 s (the assistant held 2.5-4.4 s).
   - When a B-roll cut on V2/V3 lies close to the spoken anchor, start or end the text
     on that cut so text and picture change together. The voice alignment in Step 4
     decides what counts as close.
   - A label may be reused later, or split across beats (one part per beat).
   - Texts sit over speech. No gap is left in the dialogue for them
     (`oxi-premiere-workflow/references/dialogue-editing.md`, Spine tightening moves).

### Step 3 — Choose the template

**(Oxi approved, 2026-11-05)** Read the
[common library workflow](../oxi-premiere-workflow/references/assets.md): use
typography/layout knowledge, search `motion` typography techniques and source
new MOGRT candidates through OXI Assets. Reuse approved job templates; fonts are
Oxi's (see "Look and layout"); keep this stage's baked-animation scope.
Download only selected candidates into the job, inspect them with the catalog
and the checks below, and record asset IDs/technique slugs beside `text_plan`.

**(Oxi)** the assistant chooses whichever looks good from Oxi's Graphics Templates library,
or builds the text herself if nothing fits. Library folders, the catalog command,
flags, style rules and MOGRT traps: read `references/templates.md` in full. Never open
templates one by one; run `scripts/mogrt_catalog.py` and look at the numbered sheets.
When several templates fit and the choice comes down to how they move (speed for the
video's feel, exit length, easing), use `references/motion-timing.md`; it is a yardstick
for choosing, not a licence to build effects.

### Step 4 — Place on V6–V9

- Duplicate the corrected sequence and name the copy `<job>_text_v<N>`. The sequence
  Oxi corrected stays untouched.
- Confirm the track exists (`pr_ensure_tracks`), then `pr_import_mogrt` at the start
  time with `track_index` 5–8.
- **(Oxi, 2026-10-20)** Align the visibly readable key with the spoken word or
  stress, following `speech-waveform-timing.md` in the sibling Premiere skill.
  Allow for the template's intro when choosing its clip start. Review the actual
  reveal against the voice/waveform; a readable lead is not the default.
- **(Oxi)** Before placing, look at the frame under each text window (Program Monitor
  route in `references/templates.md`) and set position and size from what is in the
  picture, not one centred default for all.
- A MOGRT's intro and outro are baked in. Never trim its ends to fit a window: that
  cuts into the entrance or exit. Pick a template whose length fits, or shorten the
  hold in the middle. Exception: a template with no exit animation (its last frame
  still shows the full text) may have its tail trimmed; `references/templates.md`
  lists the ones proven.
- Import is an overwrite edit: import every text in time order in one call, then set
  the ends. Parallel imports on one track cut each other.
- Call `pr_set_mogrt_text` with the clip's `node_id`. With several text fields, name
  the field with `param_name`, from the import result's `textParams` or the catalog.
- Two texts never overlap on the same track. A main text plus an accent at the same
  moment goes one track higher.

### Step 5 — Sub during a text

**(Oxi)** Hide the sub while a text is on screen. Keep the full SRT as the original.
Make a copy with the overlapping cues removed or trimmed, run
`oxi-premiere-workflow/scripts/validate_srt.py` on the copy, and import the copy. If
the job has no sub yet, record the text windows in the plan so the sub stage can skip
them.

### Step 6 — Check, then save

Look at a frame in the middle of each text's hold. `pr_export_sequence_frame` failed
on the edit machine; use the Program Monitor route in `references/templates.md`. Check every
template and every line with unusual letters, plus a sample of the rest:

1. **Vietnamese diacritics render.** Most templates were built for English. A font
   without Vietnamese glyphs shows boxes, drops marks, or swaps single letters to
   another font. Choose another template whose font renders, or keep it and list the
   text in the report for Oxi's font pass; do not change the font yourself.
   the edit machine has no automatic glyph check (no `fontTools`), so the frame is the check.
2. **Not cropped**, and readable at phone size on a portrait sequence.
3. **Not covering** a face, the product, or the subject's hands mid-action. Judge
   it on an exported frame where the mouth and chin are visible, not on a guess
   from the coordinates; a block whose top edge reaches the chin covers the face.
   **(Oxi approved, 2026-10-31, Product D text_v2)** Center the visible text block
   horizontally on the full frame. For two-line groups, use separate text layers when the template newline creates excessive leading; center each line and adjust their visible gap as a group. Default horizontal alignment is the center of the full frame (visible text block center x=0.5). Keep equal visual left/right spacing; do not shift every title left to compensate for platform buttons. Fit long lines by size or line breaks. An off-center layout needs a shot-specific reason recorded in the plan. Measure the complete rendered block, including shadows and animation, against nonzero left AND right insets. Use `--zone text_9x16` (working default, refine per job), or explicit job margins; the legacy `9x16` preset has zero left inset and cannot approve text layout. A technical gate PASS does not establish comfortable spacing. Record the minimum edge distances and inspect the full frame at phone size. Then measure it: run the composition gate
   (`oxi-premiere-workflow/references/composition-gate.md`) on the review
   sequence with `--plan` built from the placed text and `--base` exported with
   V6–V9 hidden. Any failing window blocks the save until the text is moved.
4. **The words match** what is said at that moment.
5. **The visible reveal follows the spoken key.** Check entry frames as well as
   the hold, and review connected phrases with voice and picture for rhythm.
   Report whether continuous playback was reviewed; stills alone do not prove
   speech synchronization. Keep deliberate anticipatory reveals within the
   agreed brief/style.

Then read the timeline with a **fresh** `pr_get_active_sequence` and compare V1, V2,
V3 and A1 clip counts and starts with the snapshot taken before step 4 (simplest:
compare clip by clip, in ticks, with the source sequence, which stays untouched). Identical:
save (standing auto-save permission from 2026-08-20; never save a half-placed state).
Any change: undo, do not patch.

Report the plan table, the sequence name, the tracks used, the templates chosen, and
every fact that is waiting on Oxi.

## Rerun after Oxi corrects

Premiere has no place to mark "this clip is mine", so the ledger is the previous
`text_plan`:

- a MOGRT on V6–V9 that matches a plan row (template, start, words) → placed by this
  skill; may be removed and placed again
- anything else on V6–V9 → Oxi's own; keep it, and treat that window as taken

No previous plan: ask before removing anything on V6–V9.

## This skill does not

- Cut dialogue, change duration, or touch V1/A1 → `oxi-premiere-workflow`
- Place or move B-roll on V2/V3 → `oxi-broll-editor`
- Make the sub/SRT itself, colour, music, transitions on V10 → `oxi-premiere-workflow`
- Decide what content stays → `oxi-script-craft`, `oxi-explore-vlog`
- Copy templates, fonts or client footage into the vault

## Updating this skill

Core rules go in this file, detail in **one** reference, repeatable code in
`scripts/` and it must run. Then
run skill-creator's `quick_validate.py`, `scripts/publish_version.py`, and require
`verify_current.py` to return `validated-match` before reporting done.
