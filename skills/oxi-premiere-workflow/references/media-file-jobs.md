# Media file jobs: plan, batch and verify

Oxi approved selective adoption on 2026-10-30. Premiere remains the editorial
source of truth. Use this reference for batch conversion/resize, extraction,
proxy creation, requested loudness normalization, or a saved execution plan.
This is a workflow reference, not an installed batch runner; create a small
job-local script only when needed, using the verified local tools.

## Plan before processing

1. Probe every source used to plan the job: stream indices, dimensions,
   rational fps/time base, duration, rotation, codecs, colour/HDR tags, audio
   channels and sample rate. Check GPU/encoder support on the actual machine;
   a listed encoder is not proof of a successful hardware encode.
2. Save a plan under `<project>/6. AI/work/<task>/`: requested operation,
   explicit source-to-output mapping, argv arrays (not shell command strings),
   output expectations, tool versions and verification steps. Source files
   remain unchanged; refuse source/output aliases and existing output paths.
   Preserve the request's scope: a resize request does not authorize a crop,
   fps conversion, loudness adjustment or content cut.
3. Give a job-local batch script `--dry-run`: validate the complete mapping and
   print the planned commands/expectations, without rendering, importing,
   attaching proxies or changing Premiere. Probes may run; a requested plan
   file may be written. Label it planned, not verified. A dry run cannot prove
   that filters will execute, captions are readable or hardware encoding works.
4. Execute only after checking freshness below. For an unfamiliar encoder or
   filter combination, test a short representative excerpt before the full
   batch. Reduce repeated re-encoding; retain an intermediate only when the
   operation needs one. Stream copy suits remux/audio extraction but is not a
   substitute for frame-exact dialogue cuts.

## Detect stale inputs and timelines

- Record resolved source paths, size, modification time and a content
  fingerprint. Use full SHA-256 for small plans/transcripts; for large media
  a size plus first/last-block hash is a cheap screening fingerprint, explicitly
  labelled sampled. It cannot prove the middle is unchanged. Use full hashing
  when replacement detection must cover the whole file, and avoid rehashing
  large unchanged sources at every small timeline operation.
- Fingerprint the cut plan, transcript, LUT, subtitle and other actual job
  dependencies too. Before running/resuming, compare them with the saved plan.
  A mismatch blocks the affected work until re-probed/replanned; do not quietly
  bless the new file by replacing its stored hash.
- A source fingerprint does not validate Premiere state. For timeline work,
  record project/sequence identity, sequence rate, track/clip identities,
  timeline starts/ends, source in/out, speed and relevant properties; include
  protected tracks and any text/effect state the operation depends on. Re-query
  live immediately before the mutation and compare these fields with the plan.
  A project path, sequence name, duration or `.prproj` hash alone is insufficient.
- Oxi's intervening edits invalidate dependent transcript/timing/B-roll plans
  even when the media files and overall sequence duration are unchanged.
  Refresh only the dependent analysis; preserve his latest sequence.
- Preflight reduces stale-plan mistakes; it is not a lock against edits during
  execution. Re-read changed and protected items after each mutation batch,
  using the existing Premiere verification/save rules.

## Batch operations and their acceptance criteria

| Operation | Decide from the source and request | Verify per output |
|---|---|---|
| Convert/remux | Stream copy when compatible; encode only for a required codec/filter. Keep explicit stream selection and HDR handling. | Expected streams/codecs, duration, decode and colour tags. |
| Resize/reframe | Keep aspect and fps unless asked otherwise; choose pad/crop from the brief. | Exact dimensions, orientation, subject framing and graphics placement on frames. |
| Extract audio | Choose the intended stream, channels and sample rate. | Audio-only output, duration, channel layout and listened excerpt. |
| Create proxies | Use Premiere's proxy workflow/preset and preserve source identity, rate, duration, orientation and audio layout. | Short encode test, then attach/test one proxy in a review context; verify proxy toggle and sync before batch attachment. Never relink originals to proxy files. |
| Normalize loudness | Only when requested, to an explicit agreed LUFS/true-peak target. Measure first; do not raise room tone as speech. | Re-measure actual integrated loudness and true peak after encode; listen for pumping/clipping. Keep video stream copy when compatible. |
| Stabilize shaky footage (fallback noted 2026-11-16) | Only when Oxi asks. Footage from a camera that records gyro data (Sony A7S III, FX3, ZV-E10/E1, A7 IV, a6700; GoPro HERO 5+; DJI Action/Avata; Insta360 — check the current list) can use Gyroflow (GPL-3.0, Premiere/AE plugin, no AI guessing, corrects rolling shutter). iPhone clips are not on its list: use Warp Stabilizer. Not installed on the edit machine; install it to `C:` only when such a job arrives. | Probe that the file still carries gyro metadata (re-encoded or exported files usually lose it). Compare a stabilized render with the original at the same frames: crop/zoom, warped edges, rolling-shutter wobble. Keep the original clip untouched. |

Process one representative file through all checks first, then the batch with
bounded concurrency appropriate to the machine. Keep a per-file result; report
`passed/total`, failures and skipped files separately. Resume by checking both
input fingerprints and the existing output's probe, not merely its filename.
Failed outputs remain labelled partial; a retry uses a new path unless replacing
that job's own intermediate is authorized. Do not attach/import an unverified file.

## Machine-readable evidence

Save a job-local JSON result beside the plan. Include `status` (planned,
passed, failed or partial), input fingerprints, tool/argv and exit code,
output path/size, expected versus measured properties, warnings, unverified
items and evidence paths. Give each check its own state: passed, failed,
not_measured or not_applicable. Missing measurement is never zero or a pass.
Keep output content hashes when useful for delivery/reuse; do not store secrets
or raw unrelated logs in the report.

A valid probe proves properties, not content: contact sheets still need opening,
audio still needs listening, and a successful tool exit cannot certify editorial
quality. For Premiere deliverables, follow [export.md](export.md) rather than
substituting a generic social-platform preset or remixing to a new target.

## Provenance and boundaries

Concepts adapted from `kajisho5/ffmpeg-skill` 2.22.1, MIT, commit
`8b6c30528d70b262d8211c6ad0cf88b0de93d8c2`:
https://github.com/kajisho5/ffmpeg-skill/tree/8b6c30528d70b262d8211c6ad0cf88b0de93d8c2
No upstream code is copied and no external skill is installed. Oxi's existing
editorial, subtitle wording, stage approval and export settings take precedence.
