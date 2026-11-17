# Speech, waveform and picture timing

Approved by Oxi on 2026-10-20 for dialogue cuts, breathing/pacing, subtitles and
key text. Oxi reviewed the corrected travel series subtitle pass as nearly aligned with
the MC. That is a successful subtitle calibration; the broader cut/text method
is approved guidance, not a claim that a new cut or text pass was tested then.

## Shared method

1. Read the current sequence and snapshot clip identities, timing, source in/out,
   text and relevant properties. Reuse an earlier transcript only after proving
   its dialogue still matches. Analyse the edited MC/VO track separately from
   music and SFX; use the complete mix for the final viewing/listening check.
2. Identify a complete spoken idea and its role in the scene. ASR word times
   locate the phrase; check what the speaker actually says, including filler,
   negation, names and the continuation after a pause. Condensed captions can
   paraphrase a clause: record the spoken clause that anchors each cue.
3. Measure the voice envelope and inspect the phrase neighbourhood. An RMS
   curve in dB at 5-10 ms hops is useful; choose the window for the signal.
   Optional speech-band filtering and smoothing must be recorded. An envelope
   shows energy, not a phoneme boundary or a sentence ending. Keep the audio
   available to check weak consonants, breaths and word tails.
4. Combine meaning, voice, the waveform and picture to select each boundary.
   A low-energy valley can be *inside* a word, or precede the next syllable.
   Selecting the deepest valley in an ASR word span can therefore move the
   boundary too late. Treat automatic onset candidates as proposals, review
   them against the spoken phrase and retain any manual override with a reason.
5. Snap the chosen times to the live sequence frame grid, respecting its actual
   rate and timecode origin (23.976 is not 24). Check the rendered result:
   a graphic's clip start and the first visibly readable letters can differ.
6. Read back every changed item in a fresh query. Compare protected tracks and
   properties, check overlaps and duration, inspect affected frames, then save
   the verified edit. Review connected phrases with audio and picture for pace;
   separately report whether continuous playback was actually reviewed. A plot,
   an SRT pass or a timestamp match alone does not prove listening sync.

ASR can stretch a word over the silence before it. If alignment is ambiguous,
re-transcribe a short contextual window or compare a stronger locally available
model, retaining the original as a control. A bigger model can still produce the
same early boundary; it does not replace waveform and listening review.

## Dialogue and breathing

- Determine sentence/idea completion before trimming. Keep full syllable attacks
  and word tails, using the measured boundary method in `dialogue-editing.md`.
- Classify a pause: dead air/retry, natural breathing/transition, or a deliberate
  rest for emphasis, reaction, action or natural sound. Tighten the first, retain
  enough of the second, and preserve the third according to the video's intent.
  A duration threshold is a flag to review, not an instruction to delete.
- Cut and breathing passes stay separate. Defaults for lead, trail, pause length
  and residual breathing are starting values to tune for the current delivery.
  Avoid making every pause identical; listen to several joined phrases together
  to judge acceleration, rest and the setup/payoff. Keep action sound intact when
  a speaker talks during a demonstration. A short silent edge alone is not proof
  of a natural join.

## Subtitles

- Anchor each condensed cue to its corresponding spoken phrase, checking whether
  omitted lead-in words are merely filler or are the start of a new thought.
  Do not put the next idea on screen during a pause or the previous idea.
- Inspect when the template actually reveals its letters. Correct each cue from
  its own voice/waveform evidence; keep already-correct cues. Any small onset
  delay is job-specific, never a global offset learned from another sequence.
- Keep enough time to read, extending a tail only while the idea still holds and
  before the next cue or emphasis-text window. Preserve meaningful phrase units,
  the approved font/layout, and the dedicated empty subtitle track policy.
- For timing-only corrections, preserve wording and appearance. Update a separate
  SRT/plan alongside the verified timeline; keep previous files as evidence.

## Key text / emphasis

- Choose the key from the content first. Anchor numbers, names and payoff words
  to the relevant spoken word or stress, using the voice envelope to refine it.
- Align the *visible emphasis* with the spoken emphasis. A template's clip may
  need to begin earlier to accommodate its intro, but a readable keyword should
  not pre-empt the MC by default. Check the actual intro/hold/outro on frames and
  with speech. A deliberate anticipatory reveal requires the agreed style/brief.
- If the template cannot fit the phrase and reading time, select another suitable
  template or adjust its supported controls; keep the text-stage effect limits.
  Hide subtitles for the actual on-screen text window.

## Evidence and reusable views

Use `scripts/timeline_view.py` for a local filmstrip/waveform/word view and
`scripts/qc_cut_boundaries.py` for joined-cut checks. For a detailed RMS plot,
NumPy/SciPy can measure the envelope and Pillow can render PNGs. A useful legend
is old boundary (red), ASR word boundary (grey), reviewed voice onset (yellow),
and proposed/new boundary (green); show the time origin and units clearly.

Keep a per-cue record of spoken anchor, ASR span, measured/reviewed onset, old/new
frame times, reading duration, manual override reason and render/listening checks.
Store job data outside the skill. The real 2026-10-20 calibration and example
scripts are in `work/2026-10-20-speech-waveform-workflow/`; those scripts contain
job-specific anchors and overrides and are not a generic automatic retimer.
The inspected subtitle near 00:02:44 moved 11 frames at 23.976 fps (about 0.46 s).
Neither that shift, the example font, nor the 38-cue count is a preset for other jobs.
