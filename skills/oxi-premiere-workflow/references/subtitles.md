# Vietnamese subtitles

For a new subtitle treatment/font/template choice, read [assets.md](assets.md):
readability and typography knowledge → `captions` techniques → OXI Assets font
or MOGRT candidates when the requested output needs them. Reuse the approved
subtitle treatment and brand fonts. Keep the meaning, timing, dedicated-track
and text-window rules below; library examples do not authorize kinetic text or
replace transcript checks. A plain SRT needs no template or asset download.

## Default deliverable

Produce a UTF-8 `.srt` and import it as a Premiere caption track when requested. Start at sequence time zero unless Oxi specifies another offset.

By default the sub covers the **whole sequence from its start**. Do not reuse an in/out range from an earlier job or an earlier request (Oxi, 2026-07-17: he wanted the sub from the very start, not only the earlier `00:06:14:11`–`00:07:36:01` range).

**Editing style (Oxi, 2026-11-12):** if the Style Card direction `chot` has
`phong_cach_dung` with `hormozi` or `podcast-clip`, the sub is the style's running
caption (word-by-word, uppercase or one coloured keyword): read
`oxi-visual-style/references/editing-styles/<slug>.md`, section Sub, and tell the
text stage to drop key text that would duplicate it. Otherwise use the condensed
style below.

## Oxi's condensed sub style (approved 2026-10-16)

Oxi corrected the `Job I` subtitle review: splitting the transcript into
fixed-size fragments made the sub feel disordered. For his edited sub style,
compose a short meaningful sentence or phrase. A long spoken sentence may lose
filler, repetition and nonessential words, or show only its main keywords.
Do not require every spoken word to appear. Keep the full transcript separately
as the source for checking meaning and timing. If a job explicitly requires
verbatim or accessibility captions, retain the full wording instead.

- Decide the meaning of each cue first, then its line break and duration.
  Character counts and word timestamps are layout/timing aids, not cut rules.
- Keep compounds and semantic units together: `<lời thoại>`, `<lời thoại>`,
  `<lời thoại>`, names, and fixed expressions. Never leave `<lời thoại>` at the end of one
  cue and `minh` at the start of the next.
- Oxi's supplied examples show a short cue `<lời thoại>`, followed by a
  two-line cue `<lời thoại>` / `<lời thoại>`. The line break follows
  meaning; it is not a fixed number of words or characters to reproduce.
- Prefer one short coherent cue over several rapid fragments. Use up to two
  lines when that makes the complete idea easier to read. Align the condensed
  cue to the spoken idea's span, not to arbitrary equal-duration slots.
- Remove words only when the central meaning remains true. Preserve negation,
  essential conditions, relationships, names, numbers and dates. Do not invent
  a claim or resolve an uncertain ASR phrase by guessing.
- Review the sequence of cues as readable ideas, then watch their rhythm with
  the actual picture and speech. SRT validation alone cannot certify semantic
  grouping, reading time or visual quality.

### Lessons from Oxi's revised sequence (read live 2026-10-16)

Oxi invited a read-only inspection of
`Job I_FULL_DIALOGUE_CLEAN_REVIEW_text_v1`, then explicitly asked to save
the lessons in this skill. These are examples of editorial decisions, not a
fixed wording, cue-count, font-size or timing preset:

| Before | Oxi's revision | Lesson |
|---|---|---|
| `<lời thoại>` | `<lời thoại>` | Keep the meaningful condition; remove the spoken scaffolding. |
| `<lời thoại>` | `<lời thoại>` | Keep the comparison and its key information. |
| `<lời thoại>` | `<lời thoại>` | Strip filler and the lead-in to the following idea. |
| `<lời thoại>` / `<lời thoại>` | `<lời thoại>` / `<lời thoại>` | Each cue is a meaningful phrase; the next completes its relationship without a dangling filler word. |
| `<lời thoại>` / `<lời thoại>` | `<lời thoại>`, then `<lời thoại>` / `<lời thoại>` within one two-line cue | Rebuild the cue boundaries around meaning; line wrapping alone cannot fix bad cue grouping. |
| Four fragments introducing why the series was made | `<lời thoại>` at about 242.71–248.23 s | A faithful short question can replace a long spoken setup and remain for the whole idea, about 5.5 s here. |
| `<lời thoại>` / `<lời thoại>` | `<lời thoại>` / `<lời thoại>` | Preserve the action and its outcome as coherent units. |

The inspected revision had 43 `SUB_FIX_` clips versus 68 in the previous pass.
This is evidence of selective summarizing and regrouping, not a target reduction
ratio. Do not infer from missing cues that every job should omit the same ideas
or stop subtitles at the same time. Oxi may still be editing a review sequence.

For typography, size the longest visible line and check the whole block on the
rendered frame. Do not shrink a two-line cue merely because its total character
count is larger. Keep spacing readable and placement consistent; exact font size,
Motion Scale, blank spacer runs and line-break encoding are implementation choices
to verify on the current template, not Oxi's editorial rule.

When invited to learn from Oxi's revision, inspect it read-only. Do not alter or
save his project, normalize his layout, fix discovered typos, or rerun an earlier
automation unless he also authorizes those changes. Updating this skill does not
authorize editing the example project.

## Spelling review and reporting

### Approved Apple subtitle treatment (Oxi, 2026-10-19)

Oxi reviewed `JOB_K_test_FULL_DIALOGUE_CLEAN_REVIEW_text_v1_SUB_APPLE_v3`
and asked to retain this approach in the skill. For this subtitle treatment,
prefer `Text pack A/Hoat anh phong cach Apple.mogrt` (catalog id 507 on the edit machine),
unless the current brief calls for another look. Resolve the installed template
by its path and text controls; the catalog id alone is not portable evidence.

- Prefer short, coherent one-line cues. When two lines sit too close together,
  split them into two successive subtitle clips, one meaningful line each,
  following the spoken phrase. Do not put the two clips on screen together.
  Preserve compounds, names, negation and the relationship between the ideas.
- If two lines are needed to preserve a complete idea, set readable leading
  and check the full block, including Vietnamese accents and descenders, on
  a rendered frame. Do not squeeze two lines together or keep shrinking them
  merely to fit. If a split would produce two unreadably short flashes, regroup
  the wording or retain the two-line block with adequate leading.
- Anchor the second cue to its spoken phrase using the edited timeline audio
  and word timings. A proportional or midpoint split is only a draft to review,
  not proof that the new boundary follows the voice. Keep approved timing when
  changing only the template or layout.
- Review when the letters actually become visible, not just the clip edge.
  If subtitles lead the voice, delay their onset slightly after checking the
  speech; keep the end before the next idea or emphasis-text window. This job
  used a five-frame delay at 30 fps (about 0.17 s), which Oxi accepted. That is
  a job-specific correction, not a universal subtitle offset.
- The Apple template reveals text progressively. Check short cues at entry,
  after the entry animation and near the end. Shorten its introductory portion
  when needed so all words appear with enough time to read; recheck rendering
  after changing source in/out. Do not add another long fade before the pop.
- A long line can be clipped by the template's internal text bounds even when
  reducing Motion Scale appears to make it fit. Adjust the editable text's
  internal font size first, then size and position the complete graphic; inspect
  both ends of the rendered line. Motion Scale alone cannot recover clipped
  glyphs. Use semantic splitting when it gives a more readable result.
- In this job, `UVNSaigonBold`, centered in the lower third above the TikTok
  interface, rendered correctly. Preserve the current job's approved font and
  placement; these font, size and coordinate values are examples, not presets.
  The 75 blocks became 114 one-line clips; this is not a target cue count.

Keep the dedicated-track and text-window hiding rules below. Before saving,
read back wording, font, cue boundaries and overlaps, compare untouched tracks
and audio against the pre-edit snapshot, and inspect rendered frames. Report
separately whether continuous playback with audio was reviewed; still-frame
checks and SRT validation do not establish speech synchronization.

### Job K revision: one-line rhythm and publishing space (2026-10-17)

Observed live, read-only, at Oxi's request on
`JOB_K_01_FULL_DIALOGUE_CLEAN_REVIEW_text_v1`; evidence is
`work/2026-10-16-job-k-01/_work/oxi-revision-learning-20261017.json`.

- For this pass Oxi turned many two-line blocks into successive one-line ideas.
  Example: `<lời thoại>` became
  `<lời thoại>` at 19.50–21.43 s, then
  `<lời thoại>` at 21.43–23.90 s.
  Use this as a remedy for sprawling blocks or excessive template line spacing,
  while preserving meaningful phrases. It does not forbid two-line subtitles.
- More cues can read better: V11 changed from 60 to 79 clips, with some former
  subtitles also promoted to V10 emphasis. There is no target cue count or
  requirement always to merge, shorten, or split every cue.
- Condense meaning, not arbitrary word counts: `<lời thoại>` became
  `<lời thoại>`; `<lời thoại>` became
  `<lời thoại>`; the closing invitation became
  `<lời thoại>`. Keep essential names, relationships and conditions.
- Oxi raised most V11 subtitles from normalized Motion Y 0.83 to about 0.7354,
  leaving room for TikTok's bottom title/interface. This is an example of safe
  placement in this edit, not a fixed platform-safe coordinate.
- Oxi refined many cue edges to the spoken phrase and edited shot; do not convert
  that observation into a rule to snap every cue to picture cuts.
- Check both tracks and actual text values: a clip still named SUB_ may now be
  emphasis or one half of a split cue. Clip labels are not the current wording.

Retain the existing read-only rule above when invited to learn: no project edits,
spelling repairs, layout normalization, or save operation without a separate request.

- Read the current live text, including titles and secondary graphics, before
  reporting. Previously reported mistakes may already be corrected.
- Distinguish definite typing/spelling errors, capitalization consistency,
  wording suggestions and uncertain transcription. A stylistic alternative is
  not automatically a spelling error.
- Report the current text, suggested correction and the clip's start/end time.
  If the text repeats across clips, identify all occurrences. Use track and time
  to disambiguate duplicate clip names; `SUB_FIX_025`, for example, occurred twice
  in the reviewed job.
- Do not mark dialect words, purposeful terminology or accepted spelling variants
  as errors merely because they are unfamiliar. In this job, `<lời thoại>`,
  `<lời thoại>` and `<lời thoại>` were not automatically treated as mistakes. Check intent,
  audio or an appropriate source when a correction depends on domain knowledge.
- Do not propagate ASR mistakes into the condensed sub or use condensation to
  silently invent an uncertain phrase. Flag the uncertain span for checking.
- A request to check or list spelling errors is read-only by default. Report
  findings; apply corrections only when the user asks for changes.

## Dedicated track for MOGRT subtitles (Oxi, 2026-10-16)

When delivering sub as MOGRT/text clips, use a dedicated video track that is
empty across its entire timeline before this subtitle pass. Do not share it
with images, footage, existing graphics, adjustment layers or transitions,
even if a requested cue's final time range looks empty. If no such track is
available, add a new dedicated track, preserving the existing track order and
contents. Confirm the live target index after creation, rather than assuming
a conventional V number is safe.

An MOGRT import can overwrite its full default duration before it is trimmed
to the cue. Trimming afterwards does not restore overwritten clips. Import
and trim each cue before placing the next; check the actual imported extent.
Snapshot existing clip identities, positions, source in/out and relevant
properties before placement, then compare them after placement. Any unexpected
change blocks a claim of completion until it is recovered and verified.
Keep the sub on the dedicated track during later corrections, too. Do not
work around a collision by spreading sub across tracks containing other media.

Verify actual frame rendering after any MOGRT relocation: correct start/end
values alone do not prove its animation or text renders at the new location.

## Workflow

For cue timing, read [speech-waveform-timing.md](speech-waveform-timing.md)
(Oxi approved 2026-10-20). Use the current edited voice, the spoken clause,
word times and measured waveform together; inspect actual letter visibility
and retain enough reading time. The corrected travel series sub was approved as nearly
aligned with speech; its per-cue offsets are calibration, not a global delay.

1. Use the edited timeline audio, not only the original source recording.
2. Probe the audio with `ffprobe` and verify duration and decoding.
3. Verify CUDA and run local Whisper `turbo` with Vietnamese transcription when available.
   If a VAD pass trims audio before ASR (2026-11-16, adapted from VideoLingo's
   `speech_edges.py`): trim only the outer edges of each window, keep about
   1 s of padding on both sides so soft first and last words survive, never
   remove pauses inside a window, and leave a window untouched when VAD finds
   no speech in it. Keep timestamps in the original audio's timeline.
4. Request word timestamps and retain working TXT, VTT, TSV, or JSON when useful for verification.
5. For Oxi's condensed sub, compose cues using the approved style above; for
   verbatim captions, reflow by Vietnamese sentence and clause boundaries:
   - split at punctuation or before clauses such as `mà`, `nhưng`, `vì`, `để`, and `khi`;
   - keep compound words, fixed phrases, domain terms, and proper names together;
   - use at most two lines per cue;
   - prefer natural meaning over rigid character counts.
6. Lightly correct obvious ASR errors. Never invent an uncertain proper name.
7. Run `scripts/validate_srt.py` and verify numbering, positive durations, order, overlap, UTF-8, line count, and final audio coverage.
   For **verbatim** captions only, add `--verbatim <transcript.txt>` (the
   corrected full transcript): it fails if regrouping dropped, added or changed
   any word, while allowing new line/cue breaks and punctuation. Never run it on
   Oxi's condensed sub, which removes words on purpose (2026-11-16, idea from
   VideoLingo mapping each AI split back to the original words).
8. Import the SRT, create the caption track at `0`, save, and report both the timeline result and clickable SRT path.
   **Revising a sub already in Premiere (Oxi, 2026-07-19):** fix the SRT you made, then in Premiere remove the old caption track or captions of that sub and import the revised one, so two versions never stack. Keep the old SRT file on disk. This covers only a sub you placed; a sub Oxi made or edited stays untouched unless he asks.

When the video also carries text on key lines, hide the sub while each text is on screen. Keep the full SRT as the original and import a copy with those cues removed or trimmed. The text stage (skill `oxi-text-graphics`) records which windows carry text.

## Domain terms and ASR bias

Oxi approved 2026-10-12, after a voice-clone job on `Cac lan dieu trong nghi thuc hau dong_FULL_DIALOGUE_CLEAN_REVIEW`.

A Whisper mismatch on a rare domain term is **not** proof that the audio is wrong. Whisper's language model pulls an unfamiliar term toward a common word, so a correct reading gets transcribed as the frequent neighbour. In that job 10 of 12 takes of `Phu chenh` came back as `Phu tranh`; after re-running the same files with the terms primed, all 24 takes read `Phu chenh` correctly. Discarding on the first transcript would have thrown away good audio and sent the job into pointless regeneration rounds.

Rule: before judging any take, cue, or clone candidate defective on a domain term, re-transcribe with the terms primed and compare.

1. Collect the domain terms of the job: names of tunes, rituals, places, products, people, model numbers.
2. Re-run Whisper on the same file with `--initial_prompt` carrying those terms as a short natural sentence, for example `Cac lan dieu chau van: Phu noi, Phu chinh, Phu chenh, Phu ru, Hat noi, ca tru, nhip ba.`
3. Treat the primed transcript as the verdict for those terms. Only a word that is still wrong when primed is a real defect.
4. Keep both transcripts in the job's check folder; the pair is the evidence that the reading was correct.

Priming steers decoding, so it can also push a term onto audio that does not contain it. Prime with the terms the line is supposed to contain, never with the whole target sentence, and keep the unprimed transcript as the control.

### Qwen3-ASR as a second opinion (tested on the edit machine, 2026-11-16)

Oxi asked to try the Qwen3-ASR path that VideoLingo uses. Test: one 129 s
Vietnamese documentary voice-over, Whisper `turbo` versus `Qwen/Qwen3-ASR-1.7B`
plus `Qwen/Qwen3-ForcedAligner-0.6B` (venv `<local path>`,
the edit machine only; evidence in `<local path>`).

- Word agreement 0.91. Qwen fixed several Whisper homophone errors (`<lời thoại>`→`<lời thoại>`,
  `lung`→`nung`, `<lời thoại>`→`<lời thoại>`, `<lời thoại>`→`<lời thoại>`, `<lời thoại>`→`<lời thoại>`) but
  introduced others (`<lời thoại>`→`<lời thoại>`, `<lời thoại>`→`<lời thoại>`, `<lời thoại>`→`<lời thoại>`), mangled a
  loanword (`saxophone`→`<lời thoại>`), misread `0,2 mm`, and spelled out every
  number. It also produced a long passage at about 71 s that Whisper did not;
  unverified by listening, so treat it as possible background speech or hallucination.
- **Its forced aligner is not usable for Vietnamese timing**: words drifted by up
  to about 20 s and runs of words shared one timestamp. Never take cue or cut
  times from it.
- Use: keep Whisper `turbo` with word timestamps as the timing source. When a
  word looks wrong, a Qwen3-ASR text pass on that stretch is one more opinion,
  like priming; a disagreement means listen, not swap. Whisper took about 22 s
  for this file on the RTX 3060; Qwen ASR plus alignment took several minutes
  (first run includes about 5 GB of model download).

## Windows reliability

- Set `PYTHONIOENCODING=utf-8` or disable verbose console output when Whisper prints Vietnamese through legacy PowerShell encodings.
- If a Vietnamese source path fails, copy the source to an ASCII-only temporary filename, preserve the original, and give the final output a natural Vietnamese name.
- If direct timeline export fails, export FCP XML and use `scripts/rebuild_timeline_audio.py` on the intended audio track.
