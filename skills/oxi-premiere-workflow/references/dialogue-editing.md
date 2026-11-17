# Dialogue editing

Follow this order for every new video whose type card puts it on the **thoại**
axis, and for the voiceover and speech of the other axes as `video-types.md`
routes them. Settle the type card at step 3, before the content map.

0. Start with `oxi-agent-brief`: understand the intended deliverable and why it
   is needed, the sources/current stage, scope/locked parts, direction,
   constraints and acceptance. Use existing answers rather than interviewing
   Oxi again. Analyze the authorized sources before planning cuts, then execute
   the stages he requested. A direct editing request is not merely a request
   for a prompt. Do not introduce another approval when the brief is already clear.
1. Preserve the untouched source sequence and read the approved script when available.
   Load `oxi-script-craft` to read it. A booking sheet's script tab holds several
   revisions side by side and only the rightmost populated column is approved;
   on 2026-08-27 the leftmost column produced an on-screen spec the client had
   already deleted. Turn the approved column into a script map and treat its
   facts, payoff lines and CTA as must-keep for every pass below.
2. Transcribe the new source at word level using a verified accelerated path.
   - For multi-take footage, use `scripts/pack_transcripts.py` when a compact phrase map will make repeated attempts and later continuations easier to compare. Keep the raw transcript and cache manifest.
   - **Verbatim pass for repeats.** Whisper large-v3 collapses repetitions and stretches words across silences of 0.5-2 s, so a Whisper transcript cannot prove that a word, clause or take was *not* repeated. Use Whisper for meaning and spelling only, and find repeats from a second, verbatim transcript:
     - Vietnamese: `sherpa-onnx` with `sherpa-onnx-zipformer-vi-int8-2025-04-20` (`OfflineRecognizer.from_transducer`, `decoding_method="modified_beam_search"`).
     - English, French, German and about 25 other European languages: `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` (same call with `model_type="nemo_transducer"`). Not yet proven on one of Oxi's jobs.
     - Any other language: Whisper run separately on each VAD chunk with `condition_on_previous_text=False`. It keeps repeats separated by a pause but still merges back-to-back ones; report that lower confidence.
     - Install `sherpa-onnx` into a job- or kit-local folder (`pip install --target <kit>\asr\pylib`), never into the system Python, and download models from the `k2-fsa/sherpa-onnx` GitHub release tag `asr-models`. Not installed on the edit machine as of 2026-10-26.
     - Decode per VAD chunk: merge chunks whose gap is under 1.0 s while the merged chunk stays under 15 s, pad each by 0.25 s. A token that starts with a space or `▁` starts a new word. Write each chunk as a Whisper-shaped segment (`start`, `end`, `text`) so `take_audit.py --asr` reads it unchanged, and keep a word list beside it.
     - Sherpa word timestamps run about 0.2 s early. Use them to navigate; take real boundaries from VAD and energy (`speech-waveform-timing.md`).
     - Where a repeat is suspected, re-recognize each piece on its own to confirm it. Report it as measured (re-recognized, energy), never as "heard".
     - Calibration (external skill `roughcut-video`, Vietnamese job, 2026-10-17): Whisper dropped `<lời thoại>` (said twice) and `<lời thoại>`; the zipformer pass caught `<lời thoại>`, `<lời thoại>`, both `<lời thoại>`, and `<lời thoại>` / `<lời thoại>` once each piece was re-recognized separately. Oxi approved adopting it on 2026-10-26.
2b. Index the whole shoot with `scripts/segment_sheets.py` into `<job>/index/` and read every sheet, filling the manifest and action map as `footage-index.md` describes. Stage 3 B-roll reuses the overview and examines shortlisted ranges against the current spoken audio before placement. Footage shot specifically for a subject is evidence that the subject matters; never classify a passage as NG or low-value while purpose-shot B-roll for it exists.
3. Settle the type card (`video-types.md`) from the Script Map, transcript and footage index; if the axis is not thoại, leave this file for the route it names. Identify purpose, audience, topic structure, must-keep facts, sponsor language, CTA, speaking style, and the presenter's useful reactions or personality beats.
4. Build a fresh content map. Never reuse another video's EDL or exact cut decisions.
5. Create a clean full-content edit first. This deliverable is `FULL_DIALOGUE_CLEAN_REVIEW`: a conservative mechanical cleanup, never a content-selection or shortening pass. Five rules govern it.

   **5a. Scope.** Do not target a shorter duration, a lower word count, or fewer clips in this pass. When Oxi asks only to `cắt video`, this cleanup is what he means, unless the type card names a genre whose first pass is selection (phóng sự, phỏng vấn in `video-types.md`). A stronger edit may well contain *more* timeline fragments than the rough selection, provided every join survives rule 5e.

   **5b. Removable — a closed list.** Remove only these, and keep everything else:
   - dead air and silence that does not serve delivery;
   - a false start, incomplete attempt, repeated word, repeated clause, or repeated take, **only** when the same meaning is clearly delivered again as a complete usable take;
   - the stumble, duplicated wording, breath, or excess pause sitting between two useful fragments;
   - production chatter that is unmistakably off-camera coordination with no reaction, personality, demonstration, continuity, or review value.

   When uncertain about any of the four, keep it for Oxi's first review.

   **Stumbles go in this pass, not later (Oxi, 2026-10-26, Product F reference comparison).** A stutter (`<lời thoại>`), a retry (`<lời thoại>`), a false start at the head of a sentence, and an abandoned sentence the MC says again in full are all removable under the second bullet above. Cut them in the clean pass and keep the later complete reading. Do not defer them to the Condensed pass: they are cleanup, not shortening, and leaving them means Oxi trims them by hand. On Product F the assistant left three such items in the QC report as "for the shortening pass" and Oxi cut all three in his own first pass, along with about 9 s of false starts and abandoned tails the assistant had not flagged. Two limits still hold: an abandoned run that carries a clause the final take dropped is spliced back per 5d ("Compare takes idea by idea"), and a deliberate repetition (an action the MC demonstrates, a comic `<lời thoại>`) stays.

   **Clean-pass QC list — check every piece before building (Oxi, 2026-11-11, Job E (culture explainer) reference comparison).** Run `scripts/clean_pass_gate.py --plan <plan.json> --wav <wav_dir> --asr <sherpa_dir> --shift 0.2` on every clean-pass plan, next to `take_audit.py` and `level_audit.py`, before the review pair is built. A non-zero exit blocks the edit. Clear each flag by fixing the plan, or write it into `--accept` with a reason. It flags `HEAD`, `TAIL`, `JOIN`, `PAUSE`, `DANGLING`, `EDGE_WORD`, `RETRY` and `ECHO`; `THI` is listed for reading and never blocks. On Job E the gate raised 74 and 41 flags on the assistant's P1 and P2 plans, and 19 and 7 on Oxi's own cuts of the same episodes; those 26 are left for judgement. The checks behind it:
   - **Reworded retry.** Two adjacent clauses with the same frame, the same opening words and the same closing word, said a few seconds apart, are one idea said twice. Keep the later one. Example: `<lời thoại>` → `<lời thoại>`. `take_audit.py` matches whole lines, so a reworded retry passes it; compare the first 3 words and the last word of neighbouring clauses.
   - **Rhetorical question echoed by its answer.** `<lời thoại>`: Oxi cut the question because the answer repeats its words. Flag it for judgement (one instance so far, not yet a rule).
   - **Edge words.** A piece must not end on a connector or on the first word of the next attempt (`<lời thoại>`, `<lời thoại>`). It must not start on a warm-up word or a broken-off word (`Đây…`, `Rồi`, `được`, `chính`). Oxi keeps a sentence-opening `Và`, `Thế`, `Còn`; those are not flagged. Read the first and last word of every piece.
   - **Filler `thì` mid-sentence.** Cut a `thì` before the predicate when a micro-gap lets it out cleanly (`<lời thoại>`, `<lời thoại>`).
   - **Interior pauses.** Split any piece at a quiet run of 0.45 s or more and close the gap. Oxi's own Job E cut still holds 18 runs of 0.36 s or more, mostly natural sentence breaths, but only 6 of 0.45 s or more; the assistant's plans held 17 runs at 0.45 s or more.
   - **Edge margins** are measured with the meter under "Edge margins", before the review pair is built. They are a gate, not advice.

   **5c. Finding where a take really ends.** A pause is not proof the take ended.
   - Never treat a brief pause, hesitation, breath, or Whisper segment boundary as an ending. If the grammar or meaning is still open, scan forward through the continuation and judge the whole phrase family before choosing.
   - A phrase that sounds locally fluent is still incomplete when it leaves a setup, connector, subject, comparison, or promise unresolved. Check what follows before accepting it as the retained ending.
   - When the presenter pauses and then continues the same sentence, prefer the final continuation that completes the thought; drop the earlier incomplete wording and join the later fragments with complete syllables and a natural internal beat.
   - Enumerate every repeated attempt in chronological order before choosing. Prefer the final complete take when it is factually and phonetically sound. Never choose the first attempt merely because it is easier to cut.
   - **Take audit gate — mechanical, not optional.** Before any plan reaches Premiere, run `scripts/take_audit.py --plan <plan.json> --asr <asr_dir>`. It reports every retained span that has a later near-duplicate reading in the same source file, and exits non-zero while any flag stands. A flagged span may only be applied after the later attempts have actually been read and one of two things is written into the report: `LATER_TAKE_DEFECTIVE: <reason>` or `SWITCHED_TO <start>-<end>`. Never wave a flag through because the earlier span "sounds fine" — the flag exists precisely because the earlier span sounds fine and is still the wrong take.
   - Point `--asr` at the verbatim transcript from step 2, not at Whisper's. The audit can only flag a reading the transcript contains, and Whisper silently drops repeated ones.
   - The gate exists because prose did not hold. This rule was already written on 2026-07-21 and the first take was still chosen on `Product C` (`C0001`, `feature X`) on 2026-08-26. Treat an unrun audit as an unfinished edit.
   - ASR spells the same foreign term differently across attempts (`Clearance` / `Clarence`), so plain string matching will not group the attempts. The audit normalizes diacritics and matches fuzzily; do the same when grouping attempts by hand.
   - When no single take completes the idea cleanly, assemble it from the best meaningful fragments of the last repeated attempts; prefer the later fragment when delivery quality is equal.
   - In multi-take footage, a quiet waveform pocket between clearly projected readings is usually a prompt, under-the-breath rehearsal, or self-correction rather than the approved delivery. Treat the amplitude contrast as a routing clue, then confirm with the script, grammar, surrounding attempts, and listening; do not promote the quiet words into the retained sentence merely because ASR transcribed them.
   - When the presenter never lands one complete projected take, build the sentence from the final compatible high-amplitude phrase fragments. Preserve their original order and meaning, remove the quiet prompt or mutter between them, and keep complete syllable attacks, word tails, and a natural internal pause at every join.
   - Do not assume a long take is clean because its broad transcript follows the script. Inspect inside every long retained span for retries, repeated clauses, incomplete first attempts, and removable pauses.

   **5d. Always keep.** The script is the narrative spine, not a whitelist of sentences.
   - Keep every unique complete line, fact, product feature, specification, opinion, reaction, demonstration cue, joke, transition, alternate phrasing with new nuance, and setup-payoff beat — including ones absent from the script.
   - Use the script to identify structure, intended order, repeated attempts, and must-keep points; never to justify removing complete useful content for length.
   - Do not remove a useful reaction merely because the script lacks it, and do not isolate every script line into its own beat — that is what makes the presenter feel chopped up.
   - Prefer a continuous complete thought with its setup, reaction, and payoff over the shortest possible assembly.
   - If uncertain whether two lines duplicate each other, or whether a line carries value, keep both.
   - **The person outranks the script** (Oxi, 2026-10-12): *<lời thoại>* A line the MC says differently from the script is kept, because it is the MC's knowledge or intent. A script line the MC never said is never added — no assembled, synthesized or borrowed substitute; report it as missing instead.
   - **Compare takes idea by idea, not take by take.** The last complete take wins only for the ideas it actually contains. When an earlier complete take or an abandoned run (*<lời thoại>*) holds a clause the final take dropped, splice that clause back in at its natural place. A restart does not throw away the first attempt's ideas. Calibration: `Job H` v1 (2026-10-12) lost three of these — *<lời thoại>* versus *<lời thoại>*, *<lời thoại>*, and the abandoned conclusion's *<lời thoại>* and *<lời thoại>*. Oxi had them put back.

   **5e. Join quality.** Protect opening and ending phonemes. Preserve full syllable attacks and word tails; use a short natural internal pause of about 0.1-0.25 seconds where appropriate, and keep about 0.3-0.5 seconds after the final sentence when needed. Edge margins on each retained piece follow "Edge margins" under "Waveform boundary method": about 0.05-0.1 seconds before the first word, about 0.2-0.25 seconds after the last word. Reject any join that becomes broken, abrupt, redundant, or dependent on removed context. Decide every final join from the waveform and from listening — transcript timestamps are navigation anchors only.
   **5f. Level gate — the on-mic rule.** Oxi set this on 2026-09-06 and it is a number, not a judgement call.
   - The presenter's real, approved delivery peaks roughly between **−10 dBFS and 0 dBFS**. Anything peaking **below −10 dBFS is tạp âm** — an off-mic reader, a prompt, a rehearsal, room noise — no matter how clean the words look in the transcript.
   - Run `scripts/level_audit.py --plan <plan.json> --wav <wav_dir> --asr <asr_dir>` on every cut plan built from multi-take footage, alongside `take_audit.py`. A non-zero exit is a blocked edit, not a warning.
   - `OFF_MIC` means part of a retained span is a quieter voice than the rest of that same span. Move the boundary, or switch to the on-mic reading of that sentence.
   - `SPAN_LOW` means the whole retained span peaks under the floor. **If no take of that line anywhere in the footage reaches −10 dBFS, stop and ask Oxi before using it.** Em không được tự quyết định giữ tiếng ngoài mic — hỏi anh ấy để anh nghe lại.
   - The gate is per-word, referenced against the span's own 90th-percentile word peak, because a span-wide peak hides the defect: on `CLIP_3493` the whole span peaked −2.9 dBFS and passed while its last 1.78 s was an off-mic reader.
   - Calibration, 2026-09-06, `video 3` / `<episode title>`. `CLIP_3493` alternates an off-mic prompt reading and the on-mic take for each sentence: `55.02–56.46` “<lời thoại>” peaks −18.4 dBFS while the on-mic reading of the same sentence sits immediately after at `56.46–58.34`, −4.0 dBFS. The delivered cut kept the quiet one — `take_audit.py` is text-based and cannot see level, and prose rule 5c about “a quiet waveform pocket” did not stop it either. Oxi heard it in one pass. That is why this rule is a script. Checked in both directions on 2026-09-06: the 21 clean spans of that plan exit 0, and `CLIP_3493 51.61–56.89` alone exits 1 with the off-mic run located at `55.02–56.89`, −18.4 dBFS.
6. Tighten breathing and pauses in a separate pass.
7. Retranscribe or reconstruct the edited timeline and inspect the actual result.
   - when the edit introduces many dialogue joins, use `scripts/qc_cut_boundaries.py` as described in `analysis-qc.md`, then listen through every flagged boundary;
   - build a spoken-content audit from the source transcript: every source phrase must be either retained or tagged with one allowed removal reason (`silence/dead air`, `duplicated failed/repeated speech`, or `unmistakable no-value production chatter`);
   - fail the review if any unique complete line is missing without Oxi's explicit shortening instruction;
   - compare all repeated attempts before approving take selection and verify that the retained take is the last complete sound take unless a documented quality or factual defect justifies another choice. Re-run `scripts/take_audit.py` against the final plan and report its exit status as part of the QC evidence;
   - run `scripts/scan_repeats.py` on the reconstructed audio of the clean pass as well. A real stutter, retry, false start or abandoned sentence it finds is fixed in this same pass (rule 5b), then rebuilt and rescanned; only a flag that sits exactly on a transcript-chunk join, or a deliberate repetition, is left with its reason written in the QC report;
   - **(default, from `ghost-editor`, 2026-11-10)** Whisper over a long stretch merges a restart into one clean sentence, so a scan of the whole reconstruction can miss it. For each retained piece longer than one sentence, split it at its internal silences, transcribe the parts separately, and compare their openings: an opening that repeats (`<lời thoại>`) is a false start the transcript hid. The source repo found 8 in one batch this way. A stretch of voice with few words in the transcript, or a word lasting over 1 s, is the same signal;
   - flag any retained boundary that ends on an unresolved connector or setup such as `và`, `nhưng`, `thì`, `để`, `tức là`, `<lời thoại>`, or a subject that still needs its predicate. These are review signals, not automatic cuts; locate the later spoken continuation and listen to the assembled sentence;
8. Deliver the clean full-content review for Oxi to watch and make his own first editorial pass, always as the review pair described in "Review pair" below. Do not perform narrative shortening yet.
9. Enter the condensed pass only after Oxi explicitly asks to `rút gọn`, `rút ngắn`, or gives an equivalent clear instruction. Create a separate condensed version and remove whole low-value ideas instead of shaving words to hit a duration.
10. Keep clearly named clean and condensed review sequences and wait for Oxi's listening review before calling the edit final. Save the project as soon as the build verifies — waiting for his review is not a reason to leave the work unsaved.

Do not combine semantic cleanup and narrative shortening in one pass. Lack of an explicit shortening request means the deliverable is the clean full-content version, not a condensed edit. Removing stutters, retries, false starts and abandoned sentences is cleanup, not shortening (rule 5b): it belongs to the clean pass.

When imperfect repeated takes must be assembled, treat the phrase or idea as the editing unit. Do not splice isolated words unless there is no semantically complete alternative. Listen through every join and retranscribe the assembled sentence before approval.

## Review pair: condensed + in-place compare

Oxi set this on 2026-10-19: every dialogue cut is delivered as **two sequences built from the same cut plan**, so he can check what was dropped without listening through the whole edit.

| Sequence | Layout | Job |
|---|---|---|
| `<base>_FULL_DIALOGUE_CLEAN_REVIEW` | Retained pieces back to back on V1/A1, zero gaps, in script order. | The deliverable. Oxi watches it once the compare check passes. |
| `<base>_FULL_DIALOGUE_CLEAN_COMPARE` | The untouched source on V1/A1, every source file end to end in shooting order. The retained pieces on **V2/A2 at the exact timeline position of their source time**, not rippled. | The missing-content check. |

How the compare sequence is read:

- A gap on V2 over dense A1 waveform is removed speech; that is where to look for a dropped line.
- A V2 piece followed by later uncovered readings of the same line means an early take was kept; this is the `feature X` failure made visible.
- Because each V2 piece sits on its own source frames, a clipped syllable is fixed by dragging the V2 edge out; no source search is needed.
- A1 and A2 play the same audio over retained pieces. Mute A1 to listen to the cut, unmute it to hear a gap.
- Breathing, pacing and script order cannot be judged here; they are judged only in the condensed sequence.

Build, check and rebuild with `scripts/review_pair.py`, not by hand:

- `build --source <seq> --plan cut-plan.json` clones the source twice, places every piece in both, names each `Pnn <file>` in both so piece *n* can be cross-checked, re-reads all three sequences frame by frame and saves only when the check passes. `--from-review <seq>` takes the pieces from an existing condensed sequence instead of a plan.
- `rebuild --base <base>` is the step after Oxi edits the compare sequence. A piece he added has no `Pnn` name, so the run stops and lists it; name it, or pass `--order time` to renumber in shooting order.
- `verify --base <base>` re-checks a pair without changing it.

Rules:

- Build both from one plan in the same pass, and verify each against the plan (clip count, source in/out per piece). The compare sequence's V2 piece *n* and the condensed sequence's piece *n* must carry the same source in/out.
- Media whose frame rate differs from the sequence (29.97 fps footage in a 30 fps sequence) lands each piece one frame early unless the track item's in/out are set after placement; see the 2026-10-19 traps in `premiere-mcp.md`. A placement that skips this passes a visual check and fails the frame check.
- Through the bridge, `videoTracks[1].overwriteClip` already sends linked audio to A2 (`premiere-mcp.md`). In the compare sequence that A2 is wanted: do not strip it.
- **The compare sequence is the source of truth once Oxi edits it.** When he drags an edge or adds a piece there, the condensed sequence is stale. Re-read the compare V2/A2 source in/out and rebuild the condensed sequence from them; never patch the two by hand in parallel.
- The condensed sequence follows script order; the compare sequence can only show shooting order. When they differ, the order decision belongs to the condensed rebuild.

## Picture is not part of the dialogue decision

Read [finishing-layout.md](finishing-layout.md) before assembling anything meant to be a finished deliverable.

Dialogue lives on A1 and is cut on its own. Picture is placed afterwards on V1/V2/V3 and is allowed to have gaps where B-roll covers. A dialogue cut therefore never has to land on a usable picture boundary, and must not be snapped to one.

This invalidates the instinct to keep an original clip boundary "so the visual survives". Cut the sentence where the sentence should be cut. Whether that frame shows the presenter is a separate, later decision.

A pass that produces one audio clip per video clip has let the picture constrain the dialogue. In Oxi's finished work audio is cut about twice as finely as picture.

## Waveform boundary method

Read [speech-waveform-timing.md](speech-waveform-timing.md) for the shared
voice/waveform/picture process and pause classification approved 2026-10-20.
Use it for both the cut and the separate breathing pass; a quiet valley alone
does not establish sentence completion or the desired pace.

Every in and out point is measured from the audio envelope. ASR word timestamps are navigation anchors only: on a verified Vietnamese turbo transcription they drifted up to 0.45 seconds routinely and 0.67 seconds at worst, which is enough to start a clip inside the decay of the previous word. Never take a cut point from a transcript.

Build the curve with `scripts/cut_plan.py` (shared logic in `scripts/_edl_common.py`), which measures RMS energy in 10 ms frames, in dB, per source clip.

- Two gates, for two different jobs. The **placement gate** is the 5th-percentile noise floor plus 8 dB; it deliberately catches the decay tail of every word, which is what a boundary must be measured against. The **chop gate** is the 60th percentile of above-placement-gate frames minus 10 dB; it sits at the real speech level and is the only correct reference for asking whether a cut landed in the body of a word. Using the placement gate as a chop test flags most of a good edit as broken.
- Pad outside the placement gate: about 0.07 seconds before the first frame over the gate, about 0.10 seconds after the last one (the `cut_plan.py` defaults since 2026-10-26). The gate already sits inside each word's decay, so the result stays asymmetric: about 0.09 seconds before the first word and 0.25 seconds after the last on the meter in the next bullet. A symmetric margin is exactly what makes an edit sound like the head is late and the tail is chopped; Oxi reports this as `đuôi cắt cụt quá mà đầu thì thừa nhiều quá`. Keep a guard of about 0.05 seconds so padding may occupy silence but never a neighbouring word.
- **Edge margins — the target is measured on the result (Oxi, 2026-10-26, Product F reference comparison).** Keep about **0.05-0.1 seconds before the first word** and about **0.2-0.25 seconds after the last word** of every retained piece. Measure on the audio energy of the edit, never on ASR timestamps: sherpa word times are point-like and often land 0.1-0.2 seconds before the real onset, so they make a word look cut when it is not. The meter used: 10 ms RMS frames in dB, speech threshold = p10 + 0.5 × (p90 − p10) of the clip. On that meter, measured per retained piece on the source audio, Oxi's Product F cut kept a median 0.09 s before onset (interquartile 0.08-0.10) and 0.23 s after offset (0.19-0.30). The assistant's plan, built with the old defaults (`lead 0.08`, `trail 0.32` over the floor+8 dB placement gate), kept 0.10 s and 0.46 s: the head was already right and the tail ran about twice as long. An earlier same-day reading of 0.275 s at the head came from an unsaved script and did not reproduce. The defaults were then retuned to `lead 0.07`, `trail 0.10`, which rebuilds that job at 0.09 s and 0.25 s. Only two ASR words fell out of the rebuild, and both sat in sub-gate silence where Oxi's cut also ends. Raising `gate_over_floor` to 12 matched the spread better but dropped the middle of 9-10 ASR words, so the gate stays at 8 dB. Oxi trimmed about 7.5 s of breath and silence at heads and tails across 40 clips. This is the second job pointing the same way: Product A 2026-09-28 measured Oxi's head at 0.06 s and join median 0.13 s, and its second pass with `gate_over_floor 14, lead 0.03, trail 0.05` measured 0.17 s per join. Still check the margins of every plan on this meter before building, and tighten any piece outside the range while still protecting syllable attacks and word tails. Third job, same direction (Job E (culture explainer), 2026-11-11). On this meter Oxi's cut measured 0.10-0.11 s before onset and 0.27-0.29 s after offset. The assistant's plan, built with `lead 0.07, trail 0.10` plus frame snapping, measured 0.18-0.22 s and 0.35-0.38 s, because nobody ran the check before building. With the silence at a join measured over a floor+18 dB gate, Oxi's median was 0.18-0.25 s against the assistant's 0.37-0.38 s. Oxi had 2 joins of 0.5 s or more in P1 and 0 in P2; the assistant had 20 and 16.
- Hunting a boundary into silence and hunting it into speech are not symmetric operations. Walking into silence only ever discards dead air, so it can range about 1.0 second. Walking into speech drags in words the selection meant to drop, so cap it at about 0.35 seconds at the head and 0.50 seconds at the tail; when neither direction finds a quiet frame, place the cut on the quietest nearby frame with a 0.03-second pad and mark the boundary for listening.
- Drop any resulting piece shorter than about 0.40 seconds. A piece that short cannot hold a whole word; it is the decay of a neighbour the selection did not want, and shipping it produces a visible 6-frame clip on the timeline.
- When a fragment like that appears, fix the selection, not the output. Move the selection start into the silence before the word so the onset hunt walks forward onto the word itself. Post-filtering alone hides the symptom and leaves the same mistake in the spec.

## Condensed pass

Enter this only after Oxi explicitly asks to shorten, and treat the target duration as a budget to be spent deliberately.

1. Measure the pause budget first with `scripts/pause_budget.py`. Trimming edges only touches the ends of a selection; a pause inside a long take survives untouched, and that interior silence is the entire budget a tightening pass can ever recover. If the budget is far below the requested reduction — 0.57 seconds against a 100-second target is typical — say so and go straight to removing whole ideas. Do not shave words to reach a number.
2. Use the duplicate scan as the editorial guide for what to remove. `scripts/scan_repeats.py` separates three problems that all live under Oxi's `câu trùng lặp`: a stutter or restart, a filler tic standing alone between pauses, and the same selling point landing twice minutes apart. A stutter or restart should already be gone, because it belongs to the clean pass (rule 5b); if one is still here, cut it and note that the clean pass missed it. Judge each pair; a deliberate hook and its payoff score as a duplicate and must stay.
3. Run the scan on the **reconstructed** audio, never on the source transcript. Rebuild the edit with `scripts/render_edit_audio.py`, transcribe that file, then scan. Removing content creates new adjacencies, and the repetition that matters is usually one the edit itself just built across a join.
4. Rebuild, retranscribe and re-scan after every removal round. A scan over the previous plan cannot hear what the newest join created.
5. Keep breathing as a separate final pass. About 0.36 seconds is a candidate threshold for inspecting a pause, not proof it is a stall. Classify its purpose with the voice, meaning and picture using `speech-waveform-timing.md`. For a pause judged to be dead air, about 0.16 seconds retained across the splice is a working starting value; tune it to the speaker and connected passage, preserving attacks, tails, deliberate rests and action sound.
6. Record every trim that was reverted, with its reason, so the same fragment is not re-proposed on the next round.

## Spine tightening moves **(Oxi, 2026-10-26, KAIYO reference comparison)**

Oxi's finished KAIYO cut ran 280.6 s against the assistant's 313.4 s spine, with the clip order unchanged. The difference came from these moves, made inside the spine and not by restructuring it:

1. **Cut lead-in words at the head of a sentence.** Words that only hand over to the line (a connector or warm-up before the real subject) go when the sentence stands without them. Keep them where the meaning or the presenter's rhythm depends on them.
2. **Drop off-topic asides.** A side remark that does not serve the product story goes, even when it is clean and well spoken.
3. **Say each product claim once.** When the same selling point lands twice, keep the stronger or better-placed reading; the duplicate scan in the Condensed pass finds the pairs.
4. **Never reserve silence for graphics.** The assistant spine held 18.5 s of A1 gaps left for spec cards and labels; Oxi's held 1.7 s. Text, labels and spec cards are laid over speech (`oxi-text-graphics`, Step 2). A gap on A1 must be a deliberate rest (natural sound, a reaction, a beat before a reveal), never a placeholder.
5. **Small tail extensions are fine** where a thought needs to finish. Tightening is not only removal.

These numbers come from one job; treat them as calibration, not targets.

## Structure moves in a presenter explainer **(Oxi, 2026-11-02, Job J reference comparison)**

Oxi's finished cut (92 A1 pieces, 463.4 s) was close in length to the assistant's (67 pieces, 455.8 s), but Oxi had reshaped the structure:

1. **Open on a hypothetical hook.** A presenter line that puts the viewer in the scene ("imagine you lived at the end of the 14th century…") goes first, even when it was recorded later in the source. Check that the hook does not say the same fact as the payoff line right after it; here the build time was said three times within 20 s.
2. **Put technical detail after the main argument.** A close-up technical passage (column bases, joinery) moves to the point where it supports the section's argument. It does not stay where it first appears in the source.
3. **Split long takes to remove internal stalls.** About 16 pieces became 2-4 pieces each. Trimming only the edges leaves the interior pauses untouched (see Condensed pass, step 1).
4. **Drop the weaker reading of a repeated idea**, as in Spine tightening move 3.
5. **Close in a fixed order:** the significance or heritage statement, an invitation to visit, the channel sign-off, then the sponsor line. Keep this outro block whole.

This is one job; treat it as calibration for presenter-led history or travel explainers, not a template.

## Reference-comparison method

When Oxi provides his corrected sequence beside an assistant review sequence:

1. Compare sequence IDs, duration, clip count, source in/out intervals, gaps, and edited-timeline transcripts without changing either sequence. A sequence Oxi says he has finished (e.g. `Video_cut`, `ProductC_5-6PHUT` on 2026-08-27: "em chỉ xem cách anh làm và không chỉnh sửa gì") is read-only: no trims, no moves, no save over it.
2. Classify each difference as an edge trim, internal pause, stumble or retry, repeated clause or idea, alternate take, or deliberate content removal.
3. Learn only the repeatable editorial principle. Never copy the reference EDL or exact source timecodes into another video.
4. Treat Oxi's corrected sequence as the stronger calibration reference after structural and semantic QC, while keeping ASR text as evidence that still requires listening at uncertain joins.
5. When Oxi asks what is still worth tightening, report suggestions only, each tied to a timeline position:
   - interior quiet runs of 0.36 s or more;
   - A1 gaps;
   - a repeated word at a join;
   - repeated ideas;
   - V1 pieces whose source in/out no longer matches the A1 piece under them.

   Fill pieces where Whisper returns no words from the sherpa transcript before judging them.

## Screen-recorded feedback video

When Oxi sends a screen recording of himself reviewing a cut instead of written notes:

1. Extract the audio and transcribe it to get what he says. Ignore Whisper text on short or noisy chunks that reads like an outro (`Cảm ơn các bạn đã theo dõi`, `Hãy subscribe…`); it is invented.
2. Crop the timeline area every 3-5 s and read the frames to see what he points at or changes: clip count, a clip that got shorter, where playback stops. The crop depends on the screen; on a 2560×1440 capture the timeline was `crop=1620:330:0:770`. Measure it from the first frame each time.
3. Write every complaint as a numbered list, each tied to a timeline position, before changing anything.
4. Re-measure each spot he criticises (the silence between two words, a level, a boundary) so the fix is checked against a number, not against the description.
5. Apply the fixes to a new sequence. Never overwrite the version he reviewed; he often edits it while recording, and that version is then a reference under the read-only rule above.
6. Report each item as fixed with its measured before/after, or as not fixed with the reason.

Source: external skill `roughcut-video` (calibration 2026-10-17), adopted with Oxi's approval on 2026-10-26.

Calibration observed on 2026-07-19: `Video_SCRIPT_CUT_REVIEW` was the assistant cut and `Video_cut` was Oxi's correction. Oxi kept the same broad script spine but changed 10 broad clips into 20 tighter fragments, reduced duration from 127.940 seconds to 107.649 seconds, and retained zero timeline gaps. Only about 0.864 seconds of the 20.291-second reduction was additional detected silence at the tested threshold, so the main improvement came from removing spoken retries or redundant material and choosing better phrase boundaries, not silence removal alone. The transcript comparison exposed one repeated full clause in the assistant cut and showed that a small ending-boundary shift could preserve a more complete final phrase. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-07-20: Oxi recut `Product L_SCRIPT_CUT_REVIEW` over the assistant's first version. Oxi's version was longer (243.033 seconds versus 169.633), contained more words in the edited-timeline transcript (1040 versus 622), and used more A/V clip pairs (67 versus 44), yet contained fewer detected pauses of at least 0.3 seconds (15 / 6.94 seconds versus 24 / 14.72 seconds). The improvement came from preserving presenter reactions, demonstrations, reasons, and natural setup-payoff bridges while removing dead air and retries. The assistant's shorter version was weaker because it treated the script too much like a sentence whitelist and removed the MC's character and connective tissue. Clip count alone does not measure whether an edit feels chopped; judge continuity of complete ideas and reactions. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-07-21: Oxi corrected `Product M_SCRIPT_CLEAN_REVIEW` into `Product M_SCRIPT_CLEAN_REVIEW anh check`. Oxi's review was longer (293.067 seconds versus 265.500), used more A/V clip pairs (36 versus 33), and contained more transcribed words (988 versus 913). The assistant had removed about 75 useful words, including complete product information about touch controls, remote control, and AI behavior, plus presenter reactions and connective lines. It also selected some earlier clean attempts without exhaustively comparing later complete takes. This proves that a first-pass clean review must use a phrase-level retained-or-allowed-removal audit, must prefer the last complete repeated take, and must keep uncertain or unique content for Oxi to judge later. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-07-22: Oxi's corrected `Product N cat` was compared read-only with the assistant's `Product N_FULL_DIALOGUE_CLEAN_REVIEW`. The reference was 363.033 seconds with 54 A/V clip pairs, while the assistant review was 434.867 seconds with 42 pairs; both had zero timeline gaps. The reference was 71.833 seconds shorter despite using more fragments. The assistant repeatedly accepted broad spans that looked complete but still contained an earlier attempt, an unresolved setup, or wording that the presenter completed after a slight pause. Oxi instead kept the later spoken continuation and joined phrase-level fragments, including a conclusion that carries `<lời thoại>` into the later predicate `<lời thoại>`. Treat a pause as a possible internal sentence boundary, not proof that the take ended; determine completion from grammar, meaning, waveform, and the later continuation. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-08-27: Oxi rebuilt `ProductC_5-6PHUT` on top of the assistant's 69-clip dialogue spine and the result was structurally different in kind, not degree. The assistant had delivered 343.74 s as 69 linked V1+A1 pairs on a single picture track, with no B-roll, graphics, SFX or music. Oxi's finished version was 323.29 s with **A1 at 89 contiguous clips** and **V1 at only 45 clips totalling 178.21 s over 6 gaps** — the presenter is on screen 55 % of the time, the rest covered by 47 B-roll clips on V2 and 3 on V3. He also added 105 graphics clips across V6-V9, 28 adjustment-layer transition clips on V10 in back-to-back pairs, 7 `Swoosh_*.wav` SFX on A2/A3, and a near wall-to-wall music bed on A4 (303.5 s of 323.3 s). He used 11 MC files and about 15 B-roll files where the assistant plan had read only 7. There were zero dissolve transitions on V1/A1. Two lessons: the assistant's hardest problem in the previous pass — snapping dialogue cuts to clip boundaries so the picture would not jump — was self-inflicted, because Oxi does not link picture to dialogue at all; and a delivered dialogue spine is roughly one third of the finished object, so report it as a spine and not as a finished cut. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-08-27 (take selection): Oxi reported that the `feature X` idea in `Product C` had eight readings and the assistant had cut the first one. Verified against the source transcript of `C0001`: the presenter attempts the line from 46.18 s and immediately fumbles it (`<lời thoại>`, `<lời thoại>`), retries at 60.52, 65.84, 66.28, 71.56, then lands it at 83.84 and again at 96.12-103.02. The assistant's `plan_6min.json` retained 40.81-51.29 — the fumbled first attempt. Oxi's finished A1 retained 84.18-85.65 plus 96.70-97.86 — the last two. The rule against this was already in 5c and in the 2026-07-21 calibration, so the failure was enforcement, not documentation; `scripts/take_audit.py` was written in response and flags this exact span while raising no false positive across the other 68 spans of the same plan. Two mechanical details worth keeping: the first attempt is the most dangerous one because it reads as clean in a broad transcript, and Whisper wrote the term as both `Clearance` and `Clarence`, so attempts must be grouped by fuzzy diacritic-insensitive matching, never by string equality. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-09-28/29 (Product A, Product B): Oxi reviewed the assistant's 9:04 clean pass and said the audio was *chưa cắt liền mạch*, that some places should rest and others be cut *dồn dập*. His own finished cut of the same job (read-only from his `.prproj` with `scripts/prproj_dump.py`) measured, with the same meter on both: median silence across a join **0.13 s** (head 0.06 s, tail 0.06 s above a floor+18 dB gate) against the assistant's **0.45 s** (tail 0.37 s — the 0.32 s trail pad); long pauses ≥0.6 s at 3.1/min against 5.7/min. His long pauses are deliberate: 3–8 s of the test's own natural sound (machine under a chair, eggs cracking, steam, a button beep) placed on A1 as a rest before the next line. He ran 5:17 for a script that asked for about 5 minutes — this booking was edited condensed, not full-length. Editorial moves worth reusing: drop an idea when an in-scene line already says it (keep the in-scene line, drop the VO duplicate); drop a line with no footage to show it; say the framing once (the budget clause appeared three times); splice single words across takes to fix a fact or a brand name (`<lời thoại>` → `<lời thoại>`; `<model name>` → `<model name>` from another take); move a setup next to its payoff. A second assistant pass built with `cut_plan.py` options `gate_over_floor 14, lead 0.03, trail 0.05, min_pause 0.25, keep_pause 0.12` plus verbatim natural-sound rows measured 0.17 s per join at 5:52 with take and level audits clean. Those options are a calibration pending Oxi's listening, not yet the default. Two traps found on the way: the MC recorded his in-scene openings and reactions **inside the B-roll files**, so B-roll must be transcribed too (Whisper hallucinates on near-silent B-roll, so re-transcribe a short window before trusting a line there); and the breathing pass chops a line spoken during an action into pieces and deletes the action sound between them — place such a line verbatim. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-10-26 (Product F, product review with a comic presenter): Oxi approved the assistant's clean pass (`nói chung là okey rồi`, `chỉ có vài cái thừa nhỏ nhỏ đầu câu thôi`), then recut the REVIEW sequence himself; compared read-only. The assistant's cut was 252.90 s in 39 pieces; Oxi's was 232.90 s in 40 A1 clips, 20.00 s shorter with the beat order unchanged. About 7.5 s came from edge margins: breath and silence at the head and tail of nearly every piece (measured medians in "Edge margins" under "Waveform boundary method"). About 12.5 s came from content the clean pass should already have removed: false starts at sentence heads (`<lời thoại>`, `<lời thoại>`, single warm-up words), stutters and retries inside a sentence (`<lời thoại>`, `<lời thoại>`), a 3.75 s abandoned sentence that the presenter says again in full 8 s later, and trailing fillers (`đấy`). The assistant's QC report had found three of these and deferred them to the Condensed pass on the reading that repetition belongs to shortening; Oxi cut all three in his first pass, plus the ones the scan missed. Oxi also extended one piece by 0.65 s where a thought needed to finish. This is the source of the "Stumbles go in this pass" note under 5b and of the "Edge margins" target. Treat these measurements as dated calibration evidence, not target numbers.

Calibration observed on 2026-11-11 (Job E (culture explainer), two presenter-led culture explainers, MC reading from a phone): Oxi recut both `_FULL_DIALOGUE_CLEAN_REVIEW` sequences in place; compared read-only through FCP XML export, a rebuilt edit audio and a sherpa transcript of each version. He kept every idea and did not reorder, add or restore anything, so the content selection, including leaving out a lone sub −10 dBFS line, stood. P1 went from 487.47 s in 70 pieces to 460.80 s in 86 A1 clips; P2 went from 311.47 s in 38 pieces to 293.20 s in 51 A1 clips. Of the 26.9 s removed in P1, about 13 s was quiet head, tail and interior. The rest was speech the clean pass should have caught: a reworded retry (2.0 s), a rhetorical question answered by an echo (1.8 s), a warm-up `Đây` at the opening (1.5 s), a dangling first word of the next attempt (0.9 s), fillers `thì / và / khi / được` at joins, and in the sponsor block one location restatement (2.7 s). In P2 he ended the episode on `<lời thoại>` and cut the CTA tail `<lời thoại>`; that is his content call for this booking. He also removed MC picture from V1 over 61-65 % of each episode. In P1 the MC stays on screen for the hook, a few chapter turns and the sponsor block; in P2, for the hook, a few lines and the closing block. The rest is left for B-roll, which repeats the Product C 2026-08-27 lesson: read V1 gaps as B-roll slots. All the speech removals were already covered by 5b; the miss was enforcement again, which is why the "Clean-pass QC list" under 5b exists. Treat these measurements as dated calibration evidence, not target numbers.
