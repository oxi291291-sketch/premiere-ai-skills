---
name: oxi-premiere-workflow
description: Operate Adobe Premiere Pro for Oxi through premiere-pro-mcp using approved, reversible workflows for dialogue editing, review sequences, AI voice denoising and cleanup, Vietnamese subtitles/SRT, music selection, test mixes and SFX placement, color correction, Lumetri grading and LUT looks, timeline QC, and an effects/element stage with HyperFrames or Remotion companion assets. After Effects work (AE MCP, comps, expressions, AE render/alpha, MOGRT authoring and MOGRT import errors) lives in the separate skill oxi-after-effects. Use when Oxi mentions Premiere, PR, sequence, cắt thoại, dựng thoại, rút gọn video, giảm ồn/khử ồn/khử noise/khử nois/làm sạch tiếng/sửa âm thanh người nói, sub/phụ đề/SRT/Whisper, chọn hoặc thử nhạc, đặt SFX, color grading/chỉnh màu/cân màu/match màu/Lumetri/LUT/look, music review, gap/A-V sync/QC, final editorial QC/duyệt bản cuối/soát chính tả, overlay, thêm element/hiệu ứng đồ họa vào video, or Premiere workflow updates.
---

# OXI Premiere Workflow

Use Premiere as the editorial source of truth and MCP as the execution layer. Apply judgment only after loading the relevant workflow below.

## Current Premiere connector — Oxi decision 2026-11-05

MCP Bridge (`premiere-pro-mcp`, registered `premiere_pro` tools) is authorized again for normal Premiere work. Oxi reports that he traced the earlier lag to the graphics driver and that the bridge is usable again. This supersedes the Higgsfield-only restriction dated 2026-11-02; it is not a diagnosis for other machines.

Start with bounded `get_capabilities` discovery, then `verify_premiere_connection`. Use the registered tools and their supported backend, target guards, preview/apply and recovery contracts. Keep calls sharing Premiere state sequential. Preserve the source sequence, verify fresh timeline readback and save verified review edits. A connection check proves connectivity, not smooth playback or a completed edit.

Higgsfield remains an alternative when selected; check `get_host_status` before its `pr_*` calls. A failure never authorizes replaying an uncertain mutation through another transport. The retired job-local `pr_file_bridge.py` and `mcp_new_client.py` bypasses remain retired: use the registered connector rather than restoring them or enabling unsafe scripting. Do not uninstall packages, reset preferences or restart Premiere/the machine without authorization.

## Mandatory preflight

0. If `Skills/_versions/oxi-premiere-workflow/CURRENT.json` exists, run `scripts/verify_current.py`. Continue only when it reports `validated-match`; a mismatch means sync or an update is incomplete and must not be treated as stable.

1. Announce `Đã nạp workflow: oxi-premiere-workflow/<route>` before the first task action.
   For every Premiere editorial request, **start with `oxi-agent-brief`**.
   (Oxi, 2026-10-13) Order: intake of sources and deliverable → read the sources
   and the script → settle purpose, scope/locks, acceptance and style from the
   script (brief + type card + Style Card from `oxi-visual-style`, one combined
   report) → **stop once for Oxi to approve the brief and pick a style** → cut.
   A job whose brief and style Oxi already approved skips that stop. Reuse
   decisions already made; only ask what the script and sources do not answer.
   Purely technical maintenance is exempt. See that skill's `references/video-editing.md`.
   **(Oxi, 2026-10-01) Stop at the end of every stage** (dialogue cut, and each
   finishing part): save, report with evidence, wait for Oxi to check. Never run
   several stages in one go. **(Oxi, 2026-10-27) Effects/element is a separate
   stage after reviewed key text and before finishing; see `references/effects.md`.**
   **(Oxi, 2026-10-14) Finishing order:** denoise →
   music → transitions → colour → sub → final QC → export; skip a part outside
   the agreed scope, never reorder. The stage rule lives in
   `oxi-agent-brief/references/video-editing.md` section 4.
2. Inspect the live project, active sequence, track state, media availability, and GPU/runtime required by the task.
3. **Load `oxi-script-craft` alongside this skill on every editorial task.** Oxi's
   videos are paid bookings, so a script almost always exists. If he supplied a
   script link or file, build the Script Map before planning any cut. If he did
   not and the brief has not already answered this, ask one short question —
   *job này có kịch bản không anh?* — and if the
   answer is no, proceed but say plainly in the report that the edit was made
   without a content contract. Never silently cut a booking as though no script
   existed. Purely technical tasks — denoising, relinking media, MCP
   reconnection, a codec probe — are exempt.
3b. **Identify the video type before any cut plan.** Oxi edits many genres and
   the genre is read from the script, not from the request. Draft the type card
   from the Script Map, settle it after transcribing and indexing the source,
   and take the route from its editing axis (thoại, lời bình, thao tác, nhạc).
   The dialogue-spine process applies only to the thoại axis. See
   [references/video-types.md](references/video-types.md). Purely technical
   tasks are exempt.
4. Treat synced notes as context, not live proof.
5. Interpret `sub` as subtitle/SRT by default. Use subsequence only when Oxi explicitly says `subsequence`, `sequence con`, or an equivalent clear phrase.
6. Preserve the source sequence. Make changes in a clearly named review sequence unless Oxi explicitly asks to edit the active source. A dialogue cut is delivered as a pair — condensed plus in-place compare (cuts on V2/A2 over the untouched source) — per "Review pair" in [references/dialogue-editing.md](references/dialogue-editing.md).
7. Ask before destructive, public, privacy-sensitive, or hard-to-reverse actions. Ask before deleting intermediate renders, alternate assets, PNG sequences, or working files. Saving the project is **not** one of these; see execution contract item 10.

## Creative libraries — Oxi approved 2026-11-05

Before settling a new creative direction, choosing a treatment or sourcing an
asset, read [references/assets.md](references/assets.md): Visual Art dictionary
and knowledge → editing technique → OXI Assets → build and verify. That reference
owns the per-stage map, search/download checks and choice record. Reuse approved
Style Card and assets; consult only the relevant knowledge for a new decision.
Pure technical work and existing approved choices do not reopen style selection.

## Route the task

- Dialogue cut/breathing, subtitle timing and key-text timing share
  [references/speech-waveform-timing.md](references/speech-waveform-timing.md).
  Read it with the relevant route: meaning and actual voice guide the edit,
  the waveform refines boundaries, and rendered/listened QC verifies the result
  (Oxi approved 2026-10-20).

- Genre, editing axis, and which cutting route a video takes (review, vlog, phóng sự, phỏng vấn, tutorial, montage…): read [references/video-types.md](references/video-types.md).
- Dialogue cleanup, take selection, shortening, breathing space: read [references/dialogue-editing.md](references/dialogue-editing.md).
- Oxi sends a screen-recorded feedback video (quay màn hình góp ý): read "Screen-recorded feedback video" in [references/dialogue-editing.md](references/dialogue-editing.md).
- Voice denoising, noise reduction, speech cleanup, and A/B audio review: read [references/audio-cleanup.md](references/audio-cleanup.md).
- Subtitle, SRT, Whisper, caption track: read [references/subtitles.md](references/subtitles.md).
  This includes Oxi's condensed meaning-first sub style and the mandatory
  dedicated, previously empty video track for MOGRT sub (approved 2026-10-16).
  The same reference includes Oxi's approved Apple treatment: readable spacing,
  successive one-line cues when two lines crowd, and checking visible entry
  timing against speech (2026-10-19).
- Text on key lines (chữ nổi bật, title, callout, MOGRT from Graphics Templates), the stage after Oxi corrects the B-roll, is the sibling skill `oxi-text-graphics`. It is not sub; its text windows tell the sub stage which cues to hide.
- Music search, shortlist, test mix, fades, ducking, SFX sound pass, beat grid, music/SFX licences: read [references/music.md](references/music.md). Choosing an SFX for a cut, camera move or graphic entrance and anchoring it to picture, or studying the SFX of a reference video: also read [references/sound-cue-placement.md](references/sound-cue-placement.md).
- Asset sourcing and technique selection across stages: read [references/assets.md](references/assets.md), including OXI Assets first, approved fonts/templates, music, subtitles, conditional LUT selection and QC/export source checks.
- Color correction, shot matching, Lumetri, LUT, and creative look: read [references/color-grading.md](references/color-grading.md). Oxi does the colour grade personally (2026-10-31): colour is out of scope by default, so skip the colour step of the finishing order and do not ask or remind Oxi about colour; run this route only when Oxi asks to balance colour or to clone/match the colour of another video. When it runs, it is the single entry point for colour: pipeline check, protected colours, measured QC with `scripts/color_scopes.py`, diagnosis table, and the feel recipes in `oxi-visual-style` (Oxi, 2026-10-19).
- Indexing and judging the shoot's footage (sheets, frame quality, the shared manifest): read [references/footage-index.md](references/footage-index.md).
- Missing B-roll that could be illustrated with HyperFrames/Remotion: use
  `oxi-broll-editor/references/generated-broll.md`. Inspect all job footage
  first, then present a visual storyboard and wait for Oxi's approval before
  producing the new scenes; rendered B-roll still passes the existing manifest
  and placement gates. This belongs to B-roll, before reviewed key text.
- Track layout, B-roll, graphics, transitions, music placement, and what a finished deliverable contains: read [references/finishing-layout.md](references/finishing-layout.md).
- Timeline verification, gaps, A/V sync, duration: read [references/timeline-qc.md](references/timeline-qc.md).
- Final editorial review (QC biên tập, duyệt bản cuối, soát chính tả/bố cục như biên tập viên): read [references/editorial-qc.md](references/editorial-qc.md). It is the final-QC part of finishing, read-only: report, then stop for Oxi.
- Export, render, deliverable file (`xuất file`): read [references/export.md](references/export.md). Last finishing part, after final QC.
- Batch conversion/resize, audio extraction, proxies, requested loudness normalization, or saved execution plans: read [references/media-file-jobs.md](references/media-file-jobs.md). Check file and live-timeline freshness before executing a saved plan; this route supports Premiere rather than replacing its editorial workflow.
- Packed transcripts, transcript cache manifests, waveform/filmstrip views, and cut-boundary review exports: read [references/analysis-qc.md](references/analysis-qc.md).
- MCP behavior, fallbacks, and known API traps: read [references/premiere-mcp.md](references/premiere-mcp.md).
- After Effects (AE comp, expressions, slow comp or toComp, AE render/alpha, MOGRT authoring or `please install After Effects` / stuck "Loading Motion Graphics Template"): load the separate skill `oxi-after-effects` (split out on 2026-10-22); its detail is in `../oxi-after-effects/references/after-effects.md`.
- Effects/element stage (hiệu ứng, element, animated icon, arrow, circle/highlight, chart/counter, HyperFrames or Remotion assets imported into Premiere): read [references/effects.md](references/effects.md). This follows reviewed key text and stops for Oxi to review before finishing. Optional legacy video-brand-kit helpers are documented after the common library workflow in [references/assets.md](references/assets.md).
- A script, booking sheet, brief, or client feedback column is involved: load the companion skill `oxi-script-craft` first and build the script map there. Do not read a booking sheet with this skill's rules.

Read only the references needed for the current task, but read each selected file completely.

## Execution contract

1. Establish the intended source sequence and deliverable name.
2. Prefer reversible operations: duplicate, import, place, keyframe, verify, then save.
3. Keep editorial and semantic decisions separate from mechanical tightening.
4. A dialogue cut is a spine on A1, not a finished video. Cut dialogue independently of picture; never snap a dialogue boundary to a clip boundary to protect the visual. Report the deliverable as a spine unless B-roll, graphics, transitions and music were also built.
5. For an ordinary first-pass dialogue cut on the thoại axis, default to a conservative full-dialogue cleanup: remove silence and clearly duplicated failed/repeated speech only. Keep every unique complete line, fact, feature, opinion, reaction, demonstration cue, joke, and transition until Oxi explicitly asks to shorten content. Genres whose first pass is selection rather than cleanup (phóng sự, phỏng vấn) are listed in `video-types.md`.
6. **A script is a contract, not context.** When Oxi supplies a script link, build the script map with `oxi-script-craft` before planning any cut, and take must-keep facts, payoff lines and the CTA from the **rightmost populated feedback column**, never from the original `KỊCH BẢN` column. Earlier columns hold requirements the client has already removed.
7. **Take selection is gated, not judged.** When a source contains repeated attempts at the same line, run `scripts/take_audit.py` on the cut plan before applying it and clear every flag in writing. Feed it a verbatim transcript (sherpa-onnx), not Whisper's: Whisper collapses repeats, so the audit cannot see them (`dialogue-editing.md` step 2). Oxi's presenters land the line on the last reading; the first reading is the one that fools a broad transcript. See `dialogue-editing.md` 5c. Run `scripts/level_audit.py` on the same plan: on-mic delivery peaks −10 dBFS to 0 dBFS, below −10 dBFS is tạp âm, and a line whose only take is under the floor must be brought to Oxi before it is used.
8. Verify tool claims against the live timeline. Check actual clip starts, ends, track indices, keyframe values, and sequence names.
9. Leave the requested review sequence active and move the playhead to a useful review point.
10. **Save automatically as soon as the requested change is verified.** Oxi granted standing auto-save permission on 2026-08-20: do not ask first, and never hand back a verified edit that is still unsaved. The gate is verification, not permission — never save a half-applied or unverified state.
11. Report the sequence name, tracks changed, timing, source preservation, and save result.

## Bundled utilities

- Use `scripts/rebuild_timeline_audio.py` when Premiere cannot directly export timeline audio but can export FCP XML.
- Use `scripts/denoise_deepfilter.py` for conservative DeepFilterNet3 cleanup with preserved work files and loudness normalization.
- Use `scripts/validate_srt.py` before delivering or importing an SRT.
- Use `scripts/pack_transcripts.py` to create a compact phrase-level transcript and source/cache manifest without requiring a specific ASR provider.
- Use `scripts/timeline_view.py` to create an SVG filmstrip, waveform, word-label, and silence view for an ambiguous source range.
- Use `scripts/qc_cut_boundaries.py` on a review export plus output-timeline cut times to preserve per-cut SVG evidence and a listening checklist.
- Use `scripts/cut_plan.py` to turn a selection spec into a waveform-measured cut plan ready for `pr_assemble_edit`. Shared energy, gate, and syllable-burst logic lives in `scripts/_edl_common.py`; the spec format is documented in its module docstring.
- Use `scripts/edge_report.py` to prove no boundary chopped a word or swallowed a syllable, as described in `analysis-qc.md`.
- Use `scripts/render_edit_audio.py` to reconstruct the edited audio from a cut plan without touching Premiere, then transcribe that file for verification.
- Use `scripts/take_audit.py` on every cut plan built from multi-take footage. It flags each retained span that has a later near-duplicate reading in the same source file and exits non-zero while any flag stands; treat a non-zero exit as a blocked edit, not a warning.
- Use `scripts/level_audit.py` on the same plan to enforce Oxi's on-mic level rule: on-mic delivery peaks −10 dBFS to 0 dBFS, anything under −10 dBFS is tạp âm. It exits non-zero on any `OFF_MIC` or `SPAN_LOW` span; when no take of a line anywhere reaches the floor, ask Oxi before using it. See `dialogue-editing.md` 5f.
- Use `scripts/clean_pass_gate.py` on every clean-pass plan, alongside `take_audit.py` and `level_audit.py`. It blocks the plan until it is as tight as Oxi's own cuts: edge margins, long joins, interior pauses, dangling words, warm-up words, reworded retries, and questions echoed by their answer. Clear each flag by fixing the plan or writing it into `--accept` with a reason. See `dialogue-editing.md` 5b, "Clean-pass QC list".
- Use `scripts/scan_repeats.py` on the reconstructed transcript to find stutters, filler, and repeated ideas, including ones the edit itself created across a new join.
- Use `scripts/pause_budget.py` before agreeing to a target duration, to measure how much interior breathing room a tightening pass can actually recover.
- Use `scripts/segment_sheets.py` to index the whole shoot into `<job>/index/manifest.json`: at most 2 seconds × 3 frames per window, sheets, luma/blur/motion flags. **Read every sheet**, inspect action changes at 1 second × 3 frames, and map complete actions before planning the dialogue cut. `oxi-broll-editor` reuses the index, compares shortlisted actions with the script/current spoken audio, and verifies chosen motion before placement. See `references/footage-index.md`.
- Use `scripts/prproj_dump.py` to read every sequence of another `.prproj` read-only (Oxi's own finished cut is the reference for the comparison method in `dialogue-editing.md`).
- Use `scripts/review_pair.py` to build the dialogue review pair (condensed + in-place compare) from a cut plan, rebuild the condensed sequence after Oxi edits the compare one, and verify both frame by frame. It absorbs the 29.97 fps one-frame trap and the default-Motion trap; see "Review pair" in `dialogue-editing.md`.
- Use `scripts/color_scopes.py` for every colour stage: `probe` reads colour tags and the camera's own log metadata (`LOG_TAG`), `measure` gives waveform/parade/vectorscope numbers and sheets from source files or a review render, `compare` checks shots against an anchor. The agent cannot read Lumetri Scopes, so colour QC is measured here, not eyeballed. See `color-grading.md`.
- Use `scripts/split_tone_lut.py` for a measured creative split-tone LUT on V5 when needed; use the shot-specific example and footage-based direction procedure in `color-grading.md`.
- Use `scripts/pr_export_frames.py` during colour tuning: it exports a few of Premiere's own processed frames through the MCP Bridge and measures them with `color_scopes.py`, so a round costs seconds instead of a full render (Oxi, 2026-10-19). One review render at the end still covers motion and legal range. See `color-grading.md`.
- Use `scripts/composition_gate.py` after every pass that places or moves text, captions, B-roll or effects: it reads frames from `pr_export_frames.py` (plus a base export with the overlay tracks hidden) and fails, with numbers, any overlay on the face or a protected box and any box outside the safe zone. Its 9:16 margins are not yet approved by Oxi. See `composition-gate.md`.
- Use `scripts/text_voice_diff.py` in editorial QC: it compares every live on-screen text with the spoken words (ASR) and the script, flags words that differ only in diacritics or one letter, odd characters and 2–3 frame text blinks, and exits non-zero until each flag gets a written verdict. See `editorial-qc.md`.
- Use `scripts/cue_probe.py` to study the SFX of a reference video or to check one cue in a review mix: `frames` shows every native-rate frame around a cue with real timestamps, `cuts` lists candidate cuts and flashes, `onsets` and `envelope` measure rises (mid and side apart) and level drops, and `ab` renders a stretch with and without one SFX on its anchor for audition outside Premiere. It measures where picture and energy change; naming the sound still takes a listening tool or ears. See `sound-cue-placement.md`.
- `scripts/pr_file_bridge.py` is retired and refuses host execution. Use the registered MCP Bridge connector or authorized UI; do not restore the job-local bypass to make a legacy helper run.

Run scripts with `python`. Put task scripts, logs, tests and intermediates under
`<project>/6. AI/work/<task>` (Oxi, 2026-10-30), unless Oxi specifies another
location. Keep `TIEN-DO-CONG-VIEC.md` at the project root and deliverables in
their agreed output folders; do not create a root-level `work` folder.

## Update this skill

When Oxi approves a repeatable workflow or correction:

1. Put core routing or safety rules in this file.
2. Put detailed task behavior in one reference file; avoid duplication.
3. Put deterministic repeated code in `scripts/` and test it.
4. Regenerate `agents/openai.yaml` if the skill description or UI prompt changes.
5. Run the skill creator's `quick_validate.py` against this folder. It is not bundled here; on Windows it lives at `%USERPROFILE%\.codex\skills\.system\skill-creator\scripts\quick_validate.py`. Set `PYTHONUTF8=1` first on Windows; without it the validator reads `SKILL.md` as cp1252 and crashes on the Vietnamese text (seen on the edit machine, 2026-09-29). Skip the step explicitly, and say so in the report, when that tool is not installed on the current machine.
6. Re-run the script you changed on a real or synthetic case and check its output.
7. Run `scripts/publish_version.py`; it keeps only the promoted snapshot and aborts cleanup if any `sync-conflict` exists. Then require `scripts/verify_current.py` to report `validated-match`.
