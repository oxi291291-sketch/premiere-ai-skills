# Transcript analysis and cut-boundary QC

Use these companion tools to improve editorial decisions and verification. Premiere remains the editable source of truth. The tools must not choose takes, shorten content, burn subtitles, grade footage, or replace the review sequence.

## Packed transcript

Run `scripts/pack_transcripts.py` on word-level JSON from Whisper, WhisperX, or ElevenLabs-compatible output.

- Group words into phrases on a speaker change or a configurable silence, normally 0.5 seconds.
- Use the packed view to enumerate repeated attempts and scan forward after pauses for a later grammatical or semantic continuation.
- Treat timestamps as navigation anchors. Decide cuts from meaning, waveform, picture, and listening.
- Keep ASR provider optional. Do not require a paid transcription service when the verified local GPU path is suitable.
- Write a manifest containing transcript hashes and optional source-media size, modification time, and SHA-256. Reuse a transcript only when the source identity and ASR settings match; file existence alone is insufficient proof.

## Timeline view

For dialogue/breathing, subtitle and key-text timing, read
[speech-waveform-timing.md](speech-waveform-timing.md): it defines how spoken
meaning, the voice envelope and rendered/listened checks work together, and
how to record ASR anchors, onset candidates and reviewed overrides.

Run `scripts/timeline_view.py` only for a source range that benefits from visual inspection. It writes one self-contained SVG with sampled frames, waveform, word labels, and shaded silence gaps.

- Use it for ambiguous pauses, repeated-take comparisons, reaction checks, and cut-edge inspection.
- Do not infer sentence completion from silence alone.
- Do not cut inside a word. Preserve complete syllable attacks and word tails, then listen through the join.
- Keep generated SVG evidence in the task workspace. Do not delete it automatically.

## Cut-boundary QC

After the Premiere review sequence is assembled, export a low-resolution review video when practical and provide its output-timeline cut times to `scripts/qc_cut_boundaries.py`.

1. Generate a view covering about 1.5 seconds before and after every new dialogue cut.
2. Listen through each join and inspect the generated filmstrip/waveform evidence.
3. Check clipped phonemes, unresolved grammar, repeated wording, missing reactions, picture jumps, A/V sync, subtitle timing, and audible clicks.
4. Treat the script's discontinuity metric as a review flag only, never proof of a bad cut.
5. Allow at most three correction-and-QC passes. If uncertainty remains, keep the safer longer wording and ask Oxi to review.
6. Use a tiny equal-power or constant-power audio transition only when listening proves that a click or discontinuity exists. Do not apply a fixed fade to every cut.

The JSON cut input may be a list of output seconds, `{ "cuts": [...] }`, or an EDL object containing ordered `ranges`; range durations are accumulated to derive output cut times. This is an output-timeline QC tool, not a source EDL renderer.

## Edge report: a clean edge is not proof of a complete word

Run `scripts/edge_report.py --spec spec.json --plan plan.json` on every assembled cut plan. It applies two independent checks, because the first one alone passes edits that are audibly wrong.

1. **Mid-word.** Probe exactly one 10 ms frame outside each boundary and compare it against the chop gate defined in `dialogue-editing.md`. Probe the frame outside, not the boundary itself: a correctly tight head sits right on the first loud frame, so measuring at the boundary flags good cuts. Measure against the chop gate, not the placement gate; the placement gate sits just over the noise floor and every word's decay tail crosses it.
2. **Syllable bursts.** Vietnamese is syllable-timed, so each syllable appears as one run of above-gate frames. A cut can land in a deep inter-syllable dip, pass the mid-word test, and still have removed the whole last word of the line. Counting the bursts inside the kept range against the words the line must contain is the only thing that catches that. Pass `--expect` with the per-clip syllable count when the script gives it; otherwise read the printed counts against the intended line.

A small number of flagged boundaries is normal and can be correct — a deliberate mid-phrase entry will flag. Report them, name why each one is intended, and listen through every boundary that carries a number, a unit, or a product name.

If no sub-threshold frame exists anywhere in the span, there is no clean cut available. Do not manufacture one: either widen the selection to the next real pause or tell Oxi the line cannot be split there.

## Additional boundary evidence

Oxi approved these measurement refinements on 2026-10-30 after reviewing
`kajisho5/ffmpeg-skill` (`silence.py`, commit
`8b6c30528d70b262d8211c6ad0cf88b0de93d8c2`, MIT). No upstream code is copied.

- When a stereo source looks silent after mono analysis but listening disagrees,
  measure RMS separately on each channel and inspect the louder channel. Opposite
  polarity can cancel a mono fold-down. Use the actual MC channel; background
  music on another channel is not proof that a syllable crosses the boundary.
- A short neighbourhood, e.g. 50 ms on either side of a candidate cut, is useful
  extra evidence for breath/weak-tail risk. Record channel, window, gate,
  source time and output time with the flag. This does not replace `edge_report`
  or its independent syllable check, and is not a new fixed placement margin.
- Keep source-to-output mappings for retained and removed spans beside the cut
  plan. Derive times from the actual frame-aligned applied plan, including speed
  changes and source offsets; reconcile with live read-back. This lets feedback
  on the review render trace to the original take. A flattened mapping is a
  navigation aid, not a replacement for Premiere tracks or overlapping media.
- A duration-based silence detector, even one labelled `speech-aware`, does
  not establish sentence meaning. Keep the semantic pause classification in
  `speech-waveform-timing.md`; use detected gaps as candidates for review.

## External concept provenance

The packed-transcript, visual timeline, and boundary-review concepts were selectively adapted from Browser Use `video-use` at commit `92c2b34e44c205cbc2acae7f6ca7c1c219d5dd66` under the MIT License. The implementation here is provider-neutral, Windows-compatible, Premiere-first, and does not copy its FFmpeg rendering, automatic grading, mandatory fades, burned-subtitle, or separate-memory behavior.
