# Editorial QC — final review before export

Oxi approved 2026-11-10 after the `Job J v2` review. Run it when Oxi
asks to check, approve, or "QC như biên tập viên" a finished cut, and as the
final-QC part of finishing, before `export.md`. `timeline-qc.md` proves the
timeline is mechanically sound; this route reads the cut the way a strict
broadcast editor does: every word on screen, every layout, every source shown,
every claim the picture makes.

The stage is **read-only**. Report findings; Oxi fixes them or approves named
fixes. Work in `<project>/6. AI/work/qc-<sequence>-<date>/` and record the job
in `TIEN-DO-CONG-VIEC.md` like any stage.

## Steps

1. **Live inventory.** Read sequence settings, In/Out and per-track clip ends.
   Done when the deliverable range is stated and any content outside it (a
   parked block, an adjustment layer past the end) is named with what an
   `Entire` export would contain.
2. **Every on-screen word, live.** For each MOGRT clip inside the range call
   `get_mogrt_component` and store `{id, track, start, end, text}` in
   `texts.json` with font, size and all-caps flag beside it. Premiere-authored
   Graphics refuse script reads; list them for the visual pass. Done when
   every text clip in range is either in `texts.json` or on the visual list.
3. **Review render and measurements.** `export_sequence` with `range:
   in_to_out` (H.264 Match Source) into the job folder, then:
   - `ebur128=peak=true` for integrated loudness, true peak and LRA;
   - `blackdetect`, `freezedetect` (1.5 s) and `silencedetect` (−45 dB, 0.8 s);
   - Whisper turbo with word timestamps (`asr.json`, a timed transcript).
   Done when each check has a number in the report.
4. **Text against voice and script.** Run
   `python scripts/text_voice_diff.py --texts texts.json --asr asr.json --ref <script.md> [source files] --out text_voice_diff.json`.
   Clear every `DAU`, `GAN`, `KY_TU` flag in writing as *lỗi chữ*, *ASR/script
   sai*, or *chủ ý*, and every `NHAY` blink as fix/keep. ASR agreeing with the
   text proves nothing: on v2 Whisper heard "<lời thoại>" too, and only the
   script held "<lời thoại>". A cited title, name or quotation that neither the voice
   nor the script settles gets checked against a primary source. Done when
   no flag is left without a verdict.
5. **Frame pass.** Export one frame per text window (about 1 s after it
   enters) plus every Graphic, every freeze on moving footage, and the last
   five seconds; build sheets and **read every sheet**. Then run
   `composition_gate.py --zone text_9x16` (or the job's margins) on the text
   windows. Apply the editor's checklist below to each frame. Done when every
   sheet is read and each item below has been asked of the whole cut.
6. **Report and stop.** Write `QC-BIEN-TAP.md` in the template below, record
   it in `TIEN-DO-CONG-VIEC.md`, then stop for Oxi.

## Editor's checklist

Ask each question of the whole cut, not a sample.

- **Spelling and diacritics** on the rendered frame. All-caps hides source
  capitalisation, so judge the rendered case; sentence-case layers show it.
- **Text says what the voice says**: same terms, same word order, no clipped
  phrase ("<lời thoại>"), a censored word only by decision.
- **Names, titles, dates** match the script and sources; one term spelled one
  way across the video (nhậm/nhận chức).
- **Readable on a phone**: contrast against the actual background (yellow on
  yellow roofs failed), size, and distance from the platform UI; no text on
  top of another text or the credit line.
- **Consistent system**: fonts, colours and placement follow one pattern;
  an outlier is either a deliberate accent or a fix.
- **Picture proves the claim**: a document screenshot shows the passage the
  voice cites, highlighted; an illustration belongs to the right country and
  period (Chinese hat charts are not Đại Ngu sources); a label sits on the
  thing it names.
- **Motion**: no frozen picture under running voice, no two- or three-frame
  blink between texts, no hard flash at a cut.
- **Ending**: the last line lands, picture and music end together, and the
  outro/CTA matches the channel.
- **Sources and rights**: file names from downloads (Facebook `_n.jpg`,
  `YTSave`), unlicensed music, a credit line placed only over its author's
  material.
- **Sound**: loudness numbers, music gaps, and ASR-suspect words to listen to.

## Report template (`QC-BIEN-TAP.md`)

1. What was checked, with counts (text clips read, frames read, ASR segments).
2. Numbers: LUFS, true peak, LRA, black/freeze/silence results, coverage.
3. **NẶNG** — must be fixed before export: wrong words, wrong facts or names,
   missing picture, wrong export range.
4. **TRUNG BÌNH** — should be fixed: proof/claim mismatch, legibility, safe
   zone, frozen footage, consistency that changes meaning.
5. **NHẸ** — polish: blinks, spacing, capitalisation, style outliers, ending.
6. Listening points and export/rights notes.

Each finding row: timecode, track and node id, what is on screen now, why it
is wrong (with evidence), and the proposed fix.
