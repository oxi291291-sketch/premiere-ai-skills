# Export (xuất file)

Use this for `xuất file`, `xuất video`, `render`, `export`, `bản giao`, `xuất bản final`. Export is the **last finishing part** (Oxi, 2026-10-14): denoise → music → transitions → colour → sub → final QC → export. Run it only after final QC on the live timeline has passed. It is its own stage: export, verify, report, stop for Oxi.

## What Oxi's own exports look like (observed)

Measured with ffprobe on the edit machine, 2026-10-14. These are Oxi's delivered files, not a recommendation from a course.

| Job | Files | Frame | fps | Video | Audio | Where / name |
|---|---|---|---|---|---|---|
| Vertical series `Series H` (2026-09-16 → 10-13) | 16 | 1080×1920 | = sequence: 30 (early `Video 1–3`), 24, 23.976 (from 10-06) | H.264 Main, yuv420p, VBR, average 22–31 Mbps | AAC-LC 48 kHz stereo ≈320 kbps (≈192 kbps on the 30 fps `Video 1–3`, `sửa 1`) | `<project>/render/`, `<số>. <Tiêu đề>.mp4`; revision as a new file (`3.1 …`, `Video 3_bo xung`, `sửa 1`) |
| TVC A v2/v3`, `TVC B v2` (2026-10-09/10) | 3 | 3840×2160 | 29.97 | H.264 Main, yuv420p, ≈52.5 Mbps | AAC-LC 48 kHz stereo ≈320 kbps | Desktop, `<Tên> vN.mp4`; each version a new file |
| AE comps via Media Encoder (2026-07-25) | 4 | 4K UHD preset | source | NVENC hardware, VBR 1-pass target 35 Mbps | AAC 320 kbps 48 kHz stereo | next to the `.aep` in `*.aep_AME\` |

Other facts from the same check:

- No custom export preset (`.epr`) is saved; only Adobe's placeholder preset exists in AME 26.0 and PPro 26.0. Settings are chosen per export.
- `AMEEncodingLog.txt` holds 249 proxy encodes and only those 4 AE renders, so the Premiere deliverables above were exported from Premiere's own Export mode, not queued to Media Encoder (inferred from their absence in the log).
- The files carry no colour tags (`color_primaries=unknown`); they are untagged Rec.709 SDR.
- One slip seen: `<số>. <Tiêu đề>.mp4.mp4`, a doubled extension.
- A review render (`…_FULL_DIALOGUE_CLEAN_REVIEW.mp4`) sits in the same `render/` folder as the finals.

## Default settings

Values marked **observed** follow the table above. Values marked **proposed** are the assistant's defaults that Oxi has not confirmed yet; state them as proposed in the report.

1. Frame size and fps: **match the sequence** (observed). Never conform 23.976 to 24 or 30 at export; if the sequence fps is wrong, that is a timeline fix before export.
2. Container and codec: `.mp4`, H.264, yuv420p (observed). Profile Main or High.
3. Bitrate, VBR: vertical 1080×1920 target ≈25–30 Mbps; 3840×2160 target ≈50 Mbps (observed averages; the exact preset target is proposed).
4. Hardware encoding (NVENC) is fine (observed in AME); check the GPU live first, per the media defaults.
5. Audio: AAC-LC, 48 kHz, stereo, 320 kbps (observed on 14 of 19 files; the five 30 fps files, `Video 1–3`, `Video 3_bo xung` and `sửa 1`, used ≈192 kbps).
6. Range: the whole sequence, In to Out of the picture. Clear stale In/Out marks first and confirm the export duration equals the sequence duration.
7. Use Maximum Render Quality only when the sequence scales footage (4K source in a 1080 sequence, 1920×1080 rotated into 1080×1920) (proposed).
8. No colour tag change, no loudness normalization at export (proposed). Measure loudness and report it; do not re-mix to hit a number Oxi has not set.

## Name and place

1. Folder: `<project>/render/` (observed for series). For a one-off client spot without a project folder, ask once where it goes; Oxi's TVC versions landed on Desktop.
2. Series: `<số>. <Tiêu đề>.mp4`. Client spot: `<Tên> vN.mp4` (observed).
3. **Never overwrite a delivered file.** A revision is a new name: `vN+1` for spots, `<số>.1` or `sửa N` for series (observed). Check the target path does not exist before export.
4. One extension only. Do not type `.mp4` into a name field that already appends it.
5. Review renders carry a `_REVIEW` suffix (observed), so they are never mistaken for the final.

## Running the export

- Through MCP: `pr_export_sequence` or a render-queue tool. Media Encoder calls may queue without producing a file (`premiere-mcp.md`, known traps): after the call, prove the file exists, its size has stopped growing, and ffprobe opens it. Never report an export from the tool's success boolean.
- On Premiere 26.3.2 (home machine, 2026-10-19) script export does not work: `exportAsMediaDirect` and `app.encoder.encodeSequence` return `Unknown Error` and produce no file. Use Export mode in the UI.
- **Export mode takes its source from the panel that had focus.** With an item selected in the Project panel it exports that item: a review render came out as the 5-second black adjustment layer. Click the sequence's timeline first, then check the `Source:` line at the top left and in the summary reads the sequence name before pressing Export.
- In the Save As dialog, select the whole File name field with Ctrl+A before typing a full path; a triple click left the old name in place and Windows refused the result.
- Save the project before exporting.
- Do not delete earlier renders or intermediates; ask first (SKILL.md safety rule).

## Verify the file

Reconcile [assets.md](assets.md)'s QC/export checks with the actual output and
job source record: assets/fonts render, required credits/licences are recorded,
and unresolved checks are reported. `delivery` library guidance can explain a
delivery issue but does not override the brief or prove conformance; run the
file checks below. No new creative asset is added during export.

Run on the exported file, never on the timeline:

1. `ffprobe`: width/height, fps equal to the sequence, H.264, yuv420p, one AAC stream at 48 kHz stereo.
2. Duration equals the sequence duration within one frame.
3. Bitrate in the expected range for its frame size.
4. Pull frames at start, 25 %, 50 %, 75 % and the last second: no black tail, graphics and sub present where the timeline has them, grade on (V4/V5 not disabled).
5. Loudness: `ffmpeg -i <file> -af ebur128=peak=true -f null -`; report integrated LUFS and true peak. Flag a true peak above −1 dBTP (proposed threshold).
6. Listen to the first and last 10 s and one transition: no clipped start or tail.

### Reusable export evidence (Oxi approved 2026-10-30)

- Save the expected sequence identity, frame size, rational fps, duration and
  relevant track state before export; re-query live before starting. If Oxi
  changed the sequence after final QC, refresh the affected QC and expectations.
  A source-file fingerprint cannot prove that the timeline still matches.
- Keep a job-local `export_check.json` under `<project>/6. AI/work/<task>/`
  with expected and measured properties, file path/size, probe and measurement
  command exit codes, warning list and explicit unverified checks. Use
  `not_measured` when loudness, fps or another value could not be read; report
  partial/failed verification rather than treating missing values as a pass.
- Save the sampled frames as a labelled contact sheet with output timecodes,
  open it and inspect the pixels. Add exact times where text, subtitles or an
  effect should appear: the five generic samples may miss those moments.
  Distinguish an unreviewed sheet from an inspected one. A black frame is a
  review flag; the timeline may intentionally contain black.
- Reconcile the report with this reference's settings and current brief.
  Report WARNs for Oxi to judge; a platform check alone does not authorize
  cropping, shortening, changing fps or normalizing the mix.
- For batch exports report checked/total, failed and skipped files separately.
  Read [media-file-jobs.md](media-file-jobs.md) for saved-plan freshness,
  dry runs and per-file batch evidence. These are workflow instructions;
  no new export checker CLI is bundled by this update.

## Report

Path and name, frame size, fps, duration (vs sequence), video and audio bitrate, loudness figures, which values were proposed rather than observed, and that no earlier render was overwritten. Then stop for Oxi.
