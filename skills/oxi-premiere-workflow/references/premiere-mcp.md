# Premiere MCP execution notes

## Current Premiere connector — Oxi decision 2026-11-05

MCP Bridge (`premiere-pro-mcp`, registered `premiere_pro` tools) is authorized again for normal Premiere work. Oxi reports that he traced the earlier lag to the graphics driver and that the bridge is usable again. This supersedes the Higgsfield-only restriction dated 2026-11-02; it is not a diagnosis for other machines.

Start with bounded `get_capabilities` discovery, then `verify_premiere_connection`. Use the registered tools and their supported backend, target guards, preview/apply and recovery contracts. Keep calls sharing Premiere state sequential. Preserve the source sequence, verify fresh timeline readback and save verified review edits. A connection check proves connectivity, not smooth playback or a completed edit.

Higgsfield remains an alternative when selected; check `get_host_status` before its `pr_*` calls. A failure never authorizes replaying an uncertain mutation through another transport. The retired job-local `pr_file_bridge.py` and `mcp_new_client.py` bypasses remain retired: use the registered connector rather than restoring them or enabling unsafe scripting. Do not uninstall packages, reset preferences or restart Premiere/the machine without authorization.

## Historical API notes — current routing is defined above

The dated API traps remain useful context. Any instruction below to prefer or
execute the job-local file bridge script is obsolete and is not an exception to
the current route. "MCP Bridge" names two different things in this file: the
registered connector (`premiere-pro-mcp`), which is the **current** route, and
the retired job-local script `scripts/pr_file_bridge.py`, which wrote commands
into the same panel's temp directory. Only the script is retired.

## Connection gate

Verify Premiere, project, active sequence, and narrow MCP tool availability before mutation. Report loaded/not-loaded and a tool count when checking MCP; avoid dumping the whole tool list.

Two independent bridges can be installed at once, each serving a different client and each with its own Premiere panel. They do not share state, and one being up says nothing about the other.

| | cloud host | file bridge |
|---|---|---|
| Premiere menu | `Higgsfield` | `MCP Bridge` |
| Transport | WebSocket to a cloud endpoint | files in a temp directory |
| Tool prefix | `pr_*`, plus `get_host_status` | `relink_media`, `set_offline`, `refresh_media`, `has_proxy`, `detach_proxy`, `scripting` |
| Raw ExtendScript | not exposed | yes |

Tool names in the stage skills: `oxi-broll-editor`, `oxi-text-graphics` and some lines of this skill (`pr_assemble_edit`, `pr_export_sequence`) name the cloud host's `pr_*` tools. On MCP Bridge take names and parameters from `get_capabilities` of the installed build; no verified name map exists yet (noted 2026-11-15), and machines can carry different `premiere-pro-mcp` builds. Each of those two skills has a "Connector" section with the behaviour that must hold on either connector.

Diagnose a connection claim empirically, never by argument. Oxi opening a panel he believes is the right one is not evidence the tool path is live; on 2026-08-10 the `MCP Bridge` panel was open and healthy while `get_host_status` stayed `{"ppro": false}`, because that status belongs to the *other* bridge. Call one cheap read tool and read the error text — it names which panel it wants.

**Historical transport notes:** direct job-local file execution is retired. The registered MCP Bridge connector is authorized again as of 2026-11-05; use its current tool contracts. The old helper recipes below are reference material, not an execution route.

## Safe sequence pattern

1. Locate the source by ID, not only name.
2. Duplicate it.
3. List sequences and identify the new ID.
4. Activate and rename the duplicate.
5. Make changes and verify through a custom read-back when needed.

## Known traps

- `sequence.end` may reflect long overlays rather than dialogue.
- Some imported SRT/audio items may be reported as type `sequence`; use node ID and media path evidence.
- `clear_sequence_in_out` and other helpers may pass an unsupported parameter type in some MCP versions. Prefer explicit in/out seconds and verify the result.
- Caption-track inspection may not be exposed by ExtendScript even when `create_caption_track` succeeds.
- Frame capture/export methods can be unavailable in the installed Premiere API.
- Adobe Media Encoder calls may queue without producing a file. Check the file and queue process; use FCP XML reconstruction as a fallback for timeline audio.
- Delete only artifacts created by the current correction and verify names/IDs first.
- Project-item node IDs are per-session. An ID that worked in an earlier session may address a different item or nothing at all. Re-list project items and re-resolve every ID at the start of each session, before building any plan that references them.
- An unsaved review sequence dies with the project. A 63-clip build was lost this way. Never close or let the project close with an unpushed or unsaved review sequence. Save through the bridge with `app.project.save()` as soon as the fresh re-read passes; Oxi granted standing auto-save permission on 2026-08-20, so do not ask first.
- `pr_assemble_edit` can return `fitted: 0` even when called with `fit: true`. Call `pr_fit_all_video` separately afterwards and check the returned count matches the clip count.
- `pr_list_sequences` end times and `pr_list_markers` times are offset from the clip starts reported by `pr_get_active_sequence` by the sequence's start-time origin — about 1.5 seconds on a sequence built here. This is the origin, not a broken build; markers line up correctly in the UI. Compare like with like before declaring a mismatch.

- `TrackItem.remove(true, true)` does **not** ripple and does **not** remove the linked audio clip on this Premiere build. It leaves a hole on V1 and orphans the A1 clip, so V1 and A1 silently desynchronise by one clip. `remove(false, false)` is the safe form. To retrim one clip in the middle of an assembled sequence, wipe the whole tail on **both** V1 and A1 with `remove(false, false)`, assert the surviving clip counts and that the last kept clip ends exactly at the cut point, then re-place the tail with `overwriteClip`. `insertClip(projectItem, at)` does ripple correctly on both tracks and is safe for a pure insertion. Observed on 2026-08-20 while lengthening `CLIP_2968_SHORT_3MIN`.

- `app.project.rootItem.type` is **3**, not 2. A tree walk guarded on `type == 2` stops at the root and returns a one-item result with no error raised. Descend on "has children" instead. This produced a silently empty project scan on 2026-08-10.

- Windows paths written into a bridge `.jsx` as backslash literals get processed twice on the way to Premiere: a literal like `"<asset library>\Sound\...\02_Bi_an..."` arrived mangled — the Vietnamese characters turned into `?`, a separator vanished, and `02_` collapsed into a control character. `File.exists` returned false and `importFiles` still returned `true` while importing nothing. Write every path with **forward slashes** (`"G:/t\u00e0i nguy\u00ean edit/Sound/..."`); ExtendScript accepts them on Windows and `\uXXXX` escapes for Vietnamese characters round-trip correctly. After any import, prove the item exists by name in a fresh project scan — never trust the boolean. Observed on 2026-09-06 while importing music for `Video 1_FULL_MUSIC_REVIEW`.

- `__kv` in `pr_file_bridge.py` takes an **array of `[key, value]` pairs**, not an object literal. `__kv({a: __num(1)})` leaves `pairs.length` undefined, the loop never runs, and the command returns `{"success": true, "data": {}}` — a silent empty success after the script has already run its mutations. If a bridge call reports success with an empty `data`, suspect this before re-running anything that mutates.

**Premiere 26.3.2 colour and export traps (home machine, `Job L` / `VIDEO EXAMPLE_COLOR_REVIEW`, 2026-10-19):**

- Lumetri `Input LUT` is a list index, not a path. `setValue("<path to .cube>")` throws `Illegal Parameter type`, so the npm tool `apply_lut` cannot set a custom LUT on this build. Pick it in the Lumetri panel: Input LUT › Browse…, then read back that the property is no longer `0`.
- `projectItem.setOverrideColorSpace()` needs a `ColorSpace` object. `ColorSpace` has no constructor, and fields of objects read from `getSettings()` or `getFootageInterpretation()` are silently read-only, so no log colour space can be built from script. An override on the project item would also change every sequence that uses the media.
- `qe.project.newAdjustmentLayer` does not exist; `qeSeq.addAdjustmentLayer` was removed in 2026. Create one with File › New › Adjustment Layer while the Project panel has focus (the item is greyed out otherwise); the dialog defaults to the active sequence's size. An existing adjustment-layer item can have the wrong size (one here was 2160×1214 in a 2160×3840 sequence): read `VideoInfo` from `getProjectMetadata()` before reusing one. Placing it with `track.overwriteClip(item, 0)` and setting `clip.end` works.
- `sequence.exportAsMediaDirect()`, `app.encoder.encodeSequence()` and `app.encoder.exportWithPresetObject()` fail with `Unknown Error` and write nothing, with three system `.epr` presets and an ASCII output path. Backslashes are no fix here: a backslash output path gives "OutputFilePath is in a folder that doesn't exist" and a backslash preset path "Preset file doesn't exist". Export video through Export mode (`export.md`); for colour checks export frames instead (`pr_export_frames.py`).
- `qe.project.getActiveSequence().addTracks(nVideo, afterIndex, 0)` adds video tracks without touching audio.

When writing custom ExtendScript, use ES3 syntax, `Time` objects for temporal APIs, and a final `return __result(...)` or `return __error(...)`.

## File-based fallback bridge — retired, history only

**Not a route.** `scripts/pr_file_bridge.py` is retired and refuses host execution (`SKILL.md`, Bundled utilities). Use the registered MCP Bridge connector. This section is kept only for the API facts it records (path escaping, the ES3 serializer, what the cloud host could not do in 2026-08).

`scripts/pr_file_bridge.py` drove Premiere through the `MCP Bridge` panel with no MCP server in the loop. The panel is a file-drop IPC and does not care which process writes the command:

1. write `<tempDir>/cmd_<id>.jsx`;
2. the panel polls every 100 ms, runs it, writes the returned string to `<tempDir>/res_<id>.json`;
3. read the response, then delete both files.

`tempDir` is `PREMIERE_TEMP_DIR` or `%TEMP%\premiere-mcp-bridge`. Default timeout 30 s in the npm client, 120 s here; scripts cap at 500 KB. Anyone who can write that directory can drive Premiere — treat it as a local trust boundary and never point it at a shared or synced location.

It was used when a needed operation had no MCP tool at all. Verified gaps in the cloud host as of 2026-08-10: relinking media, `setOffline`, refreshing a project item, proxy attach/detach, and raw ExtendScript. This is what made the 117-clip relink possible in one pass after Premiere's own Link Media could not batch it — the sources were HEVC Rext, which this Premiere build cannot decode, so auto-relink had no file properties to match on and demanded a manual locate per file.

Do not reuse the `HELPERS` block from inside the npm package. Its `__jsonStringify` fallback carries escaping that is only correct after JavaScript has parsed the template literal it is embedded in, and ExtendScript has no native `JSON` to skip that path with. `pr_file_bridge.py` ships its own ES3 serializer that escapes non-ASCII to `\uXXXX`, so Vietnamese bin, clip and folder names survive the round trip whatever encoding the panel writes with.

Every rule in "Mutation verification" applies unchanged. Snapshot the affected items to a file first, prove the operation on **one** reversible item and read it back, then batch, then re-read all of them in a FRESH query rather than trusting the per-item return values. Save as soon as that fresh re-read passes — standing auto-save applies here too.

## Mutation verification

- Prefer a dedicated MCP tool over raw QE or ExtendScript. Use a custom fallback only when the dedicated tool is unavailable, fails live verification, or cannot express the required operation.
- Capture a narrow live snapshot before each mutation: sequence ID, track index, clip node ID, start/end ticks, source in/out ticks, enabled state, and linked A/V boundaries. Read the same fields back afterwards and fail closed when the result differs from the intended edit.
- Treat QE references as disposable. Re-fetch the sequence, track, and clip after every sequence mutation before using them again.
- QE track enumeration may include empty gap items. Ignore entries with an empty name or an explicit empty-item identity before counting or mutating clips.
- For a razor operation, skip points that are already clip edges and verify the affected track's clip count before and after. Complete and verify all required cuts before moving or deleting fragments so a refused razor cannot leave a half-rearranged timeline.
- Prefer MCP track-move helpers. If a QE `moveToTrack` fallback is unavoidable, prove its argument behavior on one duplicated-sequence clip, treat the destination as an overwrite risk, and confirm the exact destination time range is empty before every move. Stop on a blocked/deadlock layout instead of looping.
- Do not guess whether a raw `TrackItem.move` argument is absolute or relative on the current host. Probe one reversible move on a duplicate, read the resulting start ticks, and continue only after the contract is proven.
- Project-state caches are hints, not evidence. Undo, panel reloads, and user edits can invalidate cached clip lengths, positions, or completion flags. Verify cached values against the live project before skipping work, and reset mutation-related caches when the engine reloads.
- When a difficult operation behaves inconsistently, log compact tick-level before/after snapshots for only the affected tracks and operation. Never log media contents, secrets, or unrelated project data.

## Effects and file safety

- Prefer live MCP effect tools. In a raw QE fallback, identify effects by a match name proven on the running Premiere build rather than by a localized display name, and target the clip by track plus start ticks instead of name alone.
- Do not assume a new component appears at the final component index. Diff the complete component list before and after applying an effect and verify the intended match name is present.
- Before ExtendScript reads any external file, inspect its size without loading its contents. Reject or stream unexpectedly large files rather than converting them into one in-memory string inside Premiere.
- Do not adopt a claimed Premiere API impossibility merely from an external reference. Check the live MCP surface first, then the running DOM/QE behavior; an MCP tool may provide a template, wrapper, or fallback even when the supported ExtendScript API lacks a direct method.

## Panel and extension boundary

- A panel is not required for ordinary Oxi editorial work while the Premiere MCP bridge already exposes the needed operation.
- For a new persistent Premiere extension on Premiere 25.6 or later, evaluate UXP first. Use CEP only for a verified legacy or QE-dependent requirement that UXP cannot yet satisfy.
- Treat panel scaffolds as platform-specific. Do not reuse macOS symlink paths, `defaults` commands, or signing/install instructions on Windows.
- Do not copy third-party panel boilerplate or bundled Adobe resources into a distributable extension until the source license and redistribution terms are verified.

## Traps found on 2026-09-28 (Premiere 26.3, MCP Bridge file panel)

- `audioTracks[0].overwriteClip(item, t)` with an A/V project item still lays the **video** on V1. For an audio-only placement, place it, then remove the video track item with `remove(false, false)` and verify A1 is unchanged.
- `videoTracks[1].overwriteClip` (V2) sends the linked audio to **A2**, not A1 — proven on a cloned sequence before a 92-clip batch. Strip A2+ afterwards and verify A1 clip-by-clip.
- Placing by seconds leaves 1–7 frame gaps between adjacent clips after frame rounding. Scan and close them (`outPoint` then `end` on the earlier clip), then re-read.
- `qe.project.getVideoEffectByName("Gaussian Blur")` resolves to `AE.Impact_Blur_FX`; its strength property is `Amount`, not `Blurriness`.
- `qe` sequence `exportFramePNG` **works** on Premiere 26.3.2 (corrected 2026-10-19; earlier notes said it was broken). It throws "Unknown error exception" only when the path uses forward slashes. Give it the playhead timecode (`CTI.timecode` of the QE sequence) and a path with backslash separators and **no extension**: it appends `.png` itself (`b.png` became `b.png.png`) and returns `true` a few seconds before the file exists, so wait for the file. Non-ASCII characters in the path go in as `uXXXX` escapes. `scripts/pr_export_frames.py` does all of this. `seq.renderVideoFrameAtTime()` returns `null`, and `exportFrameTIFF/JPEG` fail like PNG when given forward slashes.
- 16:9 brand footage in a 9:16 sequence: full-frame fill crops burned-in text. Put the fill-scaled copy on V2 with blur as background and a fit-width copy (scale 56.25) on V3.
- A reference cut in another project can be read without opening it: `scripts/prproj_dump.py <file.prproj>` decompresses the project and lists every sequence's track items (name, start, end, source in/out).

## Traps found on 2026-10-19 (MCP Bridge file panel, `JOB_K_test`)

- **29.97 fps media in a 30 fps sequence lands one frame early.** `projectItem.setInPoint(t, 4)` snaps to the *media's* frame grid, so `overwriteClip` places a piece whose source in-point is one sequence frame before the plan. The clip looks right and plays; only a tick-level read shows it. Fix that ran clean on 35/35 pieces: after `overwriteClip`, set the track item's `end`, then `inPoint`, then `outPoint` directly, for the video **and** the linked audio item. Re-fetch the item by its start ticks between setters, because a setter can leave the wrapper stale; none of the three moves `start`. Compare `projectItem` frame rate with `sequence.timebase` before any placement and expect this whenever they differ. `scripts/review_pair.py` does this on every piece.
- Clips placed through `overwriteClip` arrive with **default Motion** (Rotation 0, Scale 100), not the source clip's. Footage rotated in the source sequence comes out sideways. Copy the source clip's Motion values onto every placed video item and verify by reading them back.
- After `seq.clone()` the new sequence is not returned. Diff the set of `sequenceID`s before and after to find it, then rename it; refuse to run when a sequence with the target name already exists.
