# After Effects (AE): MCP, export, speed, MOGRT, scripting traps

Use this for any After Effects job on Oxi's machines: building or fixing a comp, expressions,
a slow comp, rendering from AE, or authoring a MOGRT for Premiere. This file is the detail
behind skill `oxi-after-effects` (split out of `oxi-premiere-workflow` on 2026-10-22). It is
reference material, not a reviewed step-by-step workflow; work from it and from live state.

Files named `export.md` and `music.md` below live in the Premiere skill:
`../../oxi-premiere-workflow/references/export.md` and `../../oxi-premiere-workflow/references/music.md`.

Marks used below:

- **observed**: seen live on the edit machine (date given).
- **(default)**: general AE practice adapted from an outside skill, not yet tested on Oxi's jobs.

AE on the edit machine: `C:\Program Files\Adobe\Adobe After Effects 2026`, version **26.3** (read live
2026-10-16). Preference folders for 26.0, 26.2 and 26.3 all exist under
`%APPDATA%\Adobe\After Effects\`; the newest one is the live one.

## 1. Which channel drives AE

Three MCP channels can reach AE. Pick one per job and stay on it.

| Channel | Tools | Needs |
|---|---|---|
| AfterEffectsMCP (file bridge) | `execute-script`, `inspect-comp`, `see-frame`, `render-queue`… | Panel `mcp-bridge-auto.jsx` open in AE |
| Higgsfield | `ae_*` | Higgsfield plugin connected (`get_host_status`) |
| Magnific | `after_effects_*` | AE open with a project (`local_status`); read `after_effects_get_skill` first |

Recovery, all **observed**:

- **Panel missing after an AE update.** A new version gets a new prefs folder, so the panel is
  gone. Reinstall with `node install-bridge.js` into
  `%APPDATA%\Adobe\After Effects\<version>\Scripts\ScriptUI Panels\`, then reopen AE.
- **Bridge stops answering mid-job** (the panel's scheduleTask got cancelled): close the panel,
  wait 3–4 s, reopen it.
- **Two `AfterFX.exe` processes** (one is Premiere's background Dynamic Link copy): `run_jsx`
  style calls break; use `execute-script` on the file bridge instead.
- **`see-frame` lies in three ways**: an old `__mcp_*.png` can be returned instead of the new
  frame (check the file time); it does not show 3D extrusion; a transparent background shows
  as black or white. Judge alpha from a real render, not from `see-frame`.
- A test render that comes out on a **plain white background** usually means a layer is
  **soloed**. Check solo switches before debugging anything else.

Details: memory notes `ae-mcp-setup.md` and `ae-toComp-tung-diem-rat-nang.md` (Claude
memory on the edit machine).

## 2. Export from AE

### Which route

- **Render Queue (RQ)** for masters and anything with alpha: ProRes, image sequences,
  lossless intermediates. One RQ item can carry several output modules (for example a ProRes
  master and an H.264 review in one pass). **(default)**
- **Media Encoder (AME)** for delivery files when you want AME's presets, NVENC or a batch.
  Oxi's only AE renders on record went this way: 4K UHD, NVENC, VBR 1-pass target 35 Mbps,
  AAC 320 kbps 48 kHz, written next to the `.aep` in `*.aep_AME\` (**observed** 2026-07-25,
  see `export.md`).

### H.264 in the Render Queue (correction)

Older guides, including the source repo below, say H.264 was removed from AE's Render Queue
around CC 2014/2015 and can only come from AME. **That is out of date.** AE 26.3 on the edit machine
has H.264 output-module templates in its preferences: `H.264 - Match Render Settings - 5 / 15
/ 40 Mbps` (**observed** 2026-10-16, in `Adobe After Effects 26.3 Prefs-indep-output.txt`).
Native H.264 came back to the RQ in AE 2023.

Still, H.264 is a delivery codec. Do not use it for a master, and never for anything that
needs alpha. Delivery settings (frame size, fps, bitrate, audio) follow `export.md`; this
file adds nothing there.

### Alpha (transparent background)

Decide by where the file goes next. **(default)**

| Destination | Format |
|---|---|
| Premiere or another editor | QuickTime ProRes 4444, channels **RGB + Alpha** |
| Frames for compositing | PNG or TIFF sequence, RGB + Alpha |
| Web page | Two files: HEVC with alpha for Safari, VP9 WebM for others |

- In older output-module dialogs alpha appears as **Millions of Colors+**; the `+` is the
  alpha. Plain "Millions of Colors" has none.
- Leave alpha **Premultiplied** (the default) unless the receiving app asks for Straight.
- A black background in the result almost always means the codec has no alpha (H.264,
  ProRes 422). Fix the output module, not the comp.
- WebM from a ProRes 4444 master, run in the scratch or job folder:
  `ffmpeg -i master.mov -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 30 out.webm`.

### Avoid

- **Compressing twice.** Render a master once, then encode deliveries from it. Do not encode
  an H.264 from another H.264.
- **AME "Match Source" silently downscaling.** Check the output frame size in the queue
  before starting.
- Trusting the AE preview as the result: measure the rendered file with ffprobe, as in
  `export.md`.

## 3. A slow comp

### Measure first

Time one frame with the expression engine, not by feel. Inside an undo group:

```javascript
// ExtendScript: time how long a property takes to evaluate at one frame
var t0 = $.hiresTimer;              // reading resets the timer
var v = prop.valueAtTime(t, false); // false = evaluate with expressions
var ms = $.hiresTimer / 1000;       // microseconds -> ms
```

Compare before and after on the same frames. Accept an optimisation only if the result moves
by less than **0.5 px** at every frame tested. **observed** method.

### toComp per point is very slow (warning)

Calling `toComp()` (or `toWorld()` + camera) **once per path point** inside an expression cost
about **1,100 ms per frame** for the A02 line in comp `A03 Scene`, TVC A
(74 expressions; **observed** 2026-10-10).

Fix: project once per frame, not once per point.

1. Once per frame, get the layer's origin and its three axis vectors in camera space:
   `cam.fromWorld(L.toWorld([0,0,0]))`, and the same for `[1,0,0]`, `[0,1,0]`, `[0,0,1]`
   minus the origin.
2. For each point, build its camera-space position from those four values (plain
   multiply-add), then project: `[w/2 + zoom*X/Z, h/2 + zoom*Y/Z]`, with
   `zoom = cam.cameraOption.zoom`, `w, h` = comp size.
3. Read sliders and effect values **once**, lazily, outside the point loop.

Result: about **350 ms per frame**, 0 px error. Same day, shot C018 (helix rays): its
centreline never changes over time, so its points were written into the expression as
constants, used only while the controls still hold their original values. 308 ms to **44 ms**
per frame. Rewriting the loop with flat arrays did **not** help: cost follows the number of
operations, not memory allocation.

### Bake what only depends on time

If an expression depends only on `time` (no sliders that Oxi will change), bake it to
keyframes: keep the expression text but disable it. The A06 city comp (1,874 expressions,
each re-reading `footage().sourceData`) went from 2.3 s to **121 ms** per frame, max 2/255
difference on a 4K still (**observed** 2026-10-10).

Traps when baking:

- Inside a **time-remapped precomp**, key at the master comp's sample times **and** at the
  precomp's own frame grid, or motion steps.
- `app.project.activeItem.saveFrameToPng()` is **asynchronous**; wait for the file before
  reading it, and set `comp.resolutionFactor = [1,1]` first, because it saves at viewer
  resolution.

### Machine-side checks (default)

Read-only checks first; anything that changes AE or the machine needs Oxi's OK (section 8).

- Multi-Frame Rendering on; RAM for other apps about 6 GB, the rest to AE.
- Disk cache on an NVMe drive, 50–150 GB.
- Hardware decoding on; proxies for heavy long-GOP footage.
- NVIDIA Studio driver rather than Game Ready; check the GPU live first.
- To test whether a GPU effect is the problem, switch the project to Mercury Software Only
  and compare.

## 4. MOGRT for Premiere

### Authoring (default)

1. Build the template comp with a **Controls** layer (`CTRL_`) holding the sliders,
   checkboxes, colour and text controls; drive everything else from it by expression.
2. Add those controls to the **Essential Graphics** panel, name them in plain words, and set
   the poster frame.
3. Export Motion Graphics Template to the Local Templates folder, then test in Premiere on a
   copy of a sequence: change every control once and play it through.

Text, timing and choosing among existing templates belong to the sibling skill
`oxi-text-graphics`.

### Trap: "please install After Effects 2026.0" (apiVersion)

This message means the MOGRT was saved by an AE **newer than the one installed**, not that AE
is missing. **observed** 2026-08-29, project `JobM.prproj`:

- A `.mogrt` is a zip. Read `definition.json` inside it and look at `apiVersion`. Do not guess
  from `authorApp`.
- The AE installed then opened apiVersion 1.4, 1.7 and 2.1, and failed on **2.2** (49 files,
  almost all of `Text pack A`). Oxi updated AE through Creative Cloud and they worked.
- Fix: update AE (Oxi's call), or use a different template. Do not edit `definition.json`.
- To list installed Adobe versions, read the exe's ProductVersion; do not query
  `Win32_Product` (slow, and it can trigger MSI repairs).

### Trap: stuck at "Loading Motion Graphics Template"

The background AE process that Premiere uses (Dynamic Link) has died. **observed**:

- Check by sampling CPU time of `AfterFX.exe` over 6–8 s; no change means it is dead.
- Fix: end `AfterFX.exe` (the background one) and `dynamiclinkmanager.exe`. **Never end
  Premiere.** Ending processes needs Oxi's OK if AE has unsaved work open.

Details: memory note `mogrt-treo-va-api-version.md`.

## 5. ExtendScript traps (observed)

- Property handles go **invalid** after you add shape properties or reorder layers. Get the
  property again by matchName after every such change.
- 2D rotation's matchName is `ADBE Rotate Z`.
- Shape path points are relative to the layer. To use absolute comp coordinates, set the
  layer's anchor point and position to `[0,0]`.
- `OR` is a reserved word in this parser; do not use it as a variable name.
- Logo tracing with potrace: the bitmap comes out inverted; pass `mask == 0`.
- A soft glow is a solid with a feathered mask, not a blurred ellipse shape layer.
- Sample scripts from real jobs: `G:\job\TVC A\AI_A04_A06\`.

Details: memory note `vector-hoa-logo-vao-ae.md`.

**External** (seen on another machine's AE 2025, from the `ocean-city-hook` and
`adaptive-video-editor` skills Oxi sent 2026-11-10; not yet seen on the edit machine):

- Drop Shadow **Opacity** has `maxValue` **255**, not 100. Set `maxValue * ratio`
  (72 % = 183.6); a raw `45` gives an almost invisible shadow.
- `transform.scale.value` can come back with **3** elements even on a 2D layer. Size
  every keyframe value and `KeyframeEase` array from `scale.value.length`, never a fixed 2.
- A property that already has keyframes: change keys with `setValueAtKey` / key times;
  a static `setValue` on it can throw. Wrap each stage in `try/catch` and log the stage.
- The importer can misread an MP3's length (a 2.112 s file read as 1.551 s, tail cut).
  Decode it to WAV 48 kHz with ffmpeg, check the sample count, import the WAV.
- ExtendScript has no `File.flush()`; write logs with open/write/close.
- `AfterFX.exe -r script.jsx` returns before the script finishes and did not reliably
  reach an AE window already open. Judge by the script's own log and the finished file,
  not the launcher's exit code.

## 6. Expression snippets (default)

Rewritten in the assistant's words; test on a copy of the layer.

**Bounce after the last keyframe** (inertial overshoot):

```javascript
var amp = 0.06, freq = 2.5, decay = 6;
var n = (numKeys > 0) ? nearestKey(time).index : 0;
if (n > 0 && key(n).time > time) n--;
if (n > 0 && n == numKeys) {
  var t = time - key(n).time;
  var v = velocityAtTime(key(n).time - thisComp.frameDuration / 10);
  value + v * amp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);
} else value;
```

**Loop keyframes**: `loopOut("cycle")` repeats, `loopOut("pingpong")` goes back and forth,
`loopIn()` loops before the first key.

**Wiggle on one axis only**:

```javascript
var w = wiggle(2, 30);
[w[0], value[1]];
```

**Wiggle that loops seamlessly** (period `loopTime` seconds):

```javascript
var freq = 1, amp = 40, loopTime = 4;
var t = time % loopTime;
var a = wiggle(freq, amp, 1, 0.5, t);
var b = wiggle(freq, amp, 1, 0.5, t - loopTime);
linear(t, 0, loopTime, a, b);
```

**Random value fixed per layer**: `seedRandom(index, true); random(0, 100);`
(`true` = same value every frame).

**Echo of the layer above, delayed**:
`thisComp.layer(index - 1).transform.position.valueAtTime(time - 0.1)`.

**Stagger by layer index**: offset each layer's timing by `(index - 1) * delay`, with `delay`
from a slider on the Controls layer. Keep the whole group under 600–800 ms, each step
40–80 ms (matches `../../oxi-text-graphics/references/motion-timing.md`). The source repo's
stagger snippet multiplied by a hard 0/1 step and did not stagger anything; it was not
copied.

**Cut on the beat**: frames per beat = `(60 / BPM) * fps`; put changes on 2-, 4- or 8-beat
phrases. Beat-grid checking is in `music.md`.

## 7. Project hygiene (default)

- Numbered bins: `01_Comps`, `02_Precomps`, `03_Footage`, `04_Audio`, `05_Solids`…
- Comp names `PROJ_section_v##`; prefixes `PRE_` (precomp), `CTRL_` (controls), `ADJ_`
  (adjustment). One meaning per label colour.
- Save as a new version (`_v02`) rather than over the old one before big changes.
- Relink missing footage from the Project panel; when handing a project over, use
  **Collect Files** into a new folder.
- `Allow Scripts to Write Files and Access Network` is already on in the edit machine's AE 26.3
  (**observed**).
- **(Oxi, 2026-10-05)** Oxi makes effects in AE himself and does not want AI-generated
  effects; AI generators are only for loose images. AI help means building the effect
  inside AE so he can adjust it.
- **(Oxi, 2026-10-07)** Give him one control for it: put the values he will want to tune
  (timing, size, amount, colour) as sliders on a `CTRL_` layer and drive the effect from
  them, instead of hard-coding numbers in keyframes or expressions.
- **(Oxi, 2026-10-09, 2026-10-17)** Oxi's asset library is `G:\03_Edit_Assets` (he likens it
  to his NAS store); look there for assets he points to, e.g.
  `03_Assets\PNG\Bộ stock vân mây mang phong cách phương Đông`. G is a portable drive, so
  check it is mounted first. **Copy every asset you take into the project folder** before
  importing, so the project never links into the library.

## 8. Ask Oxi first

Each of these changes AE, the project or the machine in a way that is hard to undo:

- Reduce Project, Remove Unused Footage, or deleting comps or layers.
- Resetting preferences, emptying the disk or media cache, moving plugins out.
- Updating or rolling back AE.
- Ending an AE or Dynamic Link process while unsaved work may be open.
- Overwriting a saved `.aep` instead of saving a new version.

## 9. Guard rails for AI-driven edits

Five patterns taken from the AE GPT 1.3.1 panel's ExtendScript backend (`jsx/index.js`, read
2026-10-22 without installing). They are **(default)**: not yet run on Oxi's jobs. Apply them
to every mutating call, whichever channel from section 1 is in use.

1. **One undo group per AI step.** Wrap each script or batch in
   `app.beginUndoGroup("the assistant: <step>")` ... `app.endUndoGroup()`, with the end call in a
   `finally`, so one Ctrl+Z reverts the whole step. Check whether the channel's tool already
   opens a group before adding a nested one.
2. **Checkpoint before each stage.** Before a big editing stage, save a backup copy of the
   `.aep` (`_v##` or `_bak_<stage>`), never over Oxi's file (section 8). To roll back, reopen
   that copy; tell Oxi first if unsaved work would be lost.
3. **Project guard.** Read `app.project.file.fsName` at the start of the job. Before each
   mutating call, compare it again (and the target comp's name and id); if Oxi switched
   projects or comps, stop and ask instead of editing whatever is now active.
4. **Inspect after any raw script.** A script that returns without error has not been
   verified. Read back the affected layers or properties (`inspect-comp`, `inspect-layer`,
   `ae_get_layer_info`) and look at a frame before saying it worked.
5. **Target by layer id, not index.** `layer.index` shifts after reorder, precompose or delete;
   resolve layers by `layer.id` (or by name plus id) right before each change, as in section 5
   for property handles. In one script, keep the ids of objects created earlier and reuse
   them instead of making a second round trip. After setting expressions, scan the touched
   properties for `expressionError` and report any that fail.

Not copied from AE GPT: its free `script.run` (unrestricted `new Function`, with file and
network access through the panel's Node context) and its obfuscated UI. Its frame-preview
tool already exists here as `see-frame` / `ae_export_frame` (section 1 traps apply).

## 10. Rebuild a code-built asset in AE

**(Oxi, 2026-11-01)** "HyperFrames làm chính xong quăng vào Pr, AE có thể code xong vẽ lại
trên nó vì anh cần chỉnh sửa." HyperFrames is the main path for B-roll and element assets;
an asset is rebuilt in AE only when Oxi wants to adjust it himself. The decision and its
scope live in `oxi-broll-editor/references/generated-broll.md`, section 3.

The approved HyperFrames render is the reference for timing, layout and colour. The AE
rebuild must be editable: shape and text layers, keyframes and expressions, no pre-rendered
HTML footage standing in for the scene. Tunable values go on a `CTRL_` layer (section 7).

Translating the code techniques **(default, not yet tried on a job)**:

| In the HyperFrames scene | In AE |
|---|---|
| Closed-form spring, one per target change | Spring/overshoot expression on the property, frequency and damping read from `CTRL_` sliders |
| One world layer, one camera, log-space zoom | Every layer parented to a `CAM_CTRL` null (or a 3D camera with a parent null); zoom = null scale, interpolated in log space by expression |
| Object handoff between scenes | Shared layer kept across the cut at the same position, or a precomp handed over on the same frame |
| Colour flood transition | Shape layer scaled past the corners (about 150 %), about 0.3 s |
| Subframe motion blur (`ffmpeg tmix`) | AE motion blur, shutter 180°, on the moving layers only |
| Cursor driving the UI | Cursor layer with Auto-Orient along path, scale-up on hover, short squash on click |
| Beat grid | Comp markers on each beat (section 6, "Cut on the beat") |

Check: export one still per beat marker from the AE comp and from the HyperFrames render
and compare them side by side; differences in position, timing or colour are rebuild errors
unless Oxi asked for them. Judge alpha from a real render (section 1). Apply the guard rails
in section 9 to every mutating call.

Higgsfield lists `ae_build_scene_from_html` and `ae_html_to_spec`, which may convert an
HTML scene into AE layers. **Not tested**: before relying on either, try it on one short
scene and inspect the result for editable layers, not a flattened image.

## 11. Talking-head hook: soft text shadow, word-led zoom, face lock (external)

From the Codex skill `ocean-city-hook` (a real-estate talking-head hook, 1080×1920,
built on another machine), sent by Oxi 2026-11-10. **Not tested on the edit machine and not
reviewed by Oxi**: the person on that machine approved V4 as "tạm ổn"; V5 zoom was
never approved. Use it as a starting look when Oxi asks for this kind of hook, then
adjust to his corrections. Scale pixel values by `comp.height / 1920`.

### Soft text shadow (V4)

- **No stroke on any text.** The stroked V3 was rejected as hard and ugly; contrast
  comes from shadow, not an outline.
- Two native `ADBE Drop Shadow`, black, direction 135°:

  | Layer | Contact: opacity / distance / softness | Soft depth |
  |---|---|---|
  | Bold text | 72 % / 6 px / 10 px | 30 % / 12 px / 30 px |
  | Script (handwritten) text | 80 % / 4 px / 7 px | 30 % / 12 px / 30 px |

- Optional glow on bold text only, placed before the shadows: native `ADBE Glo2`, core
  radius 8 / intensity 0.08, wide radius 24 / intensity 0.02, Glow Colors = A & B with
  both colours set to the text's fill (avoids a dark halo). No glow on script text.
  Deep Glow 2 failed there (`IrisBlurSDK DLL Cannot be Loaded!`); check the plugin live
  and say which glow was actually used.
- Type pairing on that job: Montserrat Black title, SVN DancingScript script line,
  UTM Bebas for the big stressed word. On Oxi's jobs fonts still come from the OXI
  Design System (`oxi-text-graphics/references/templates.md`).
- `../scripts/apply_soft_text.jsx` applies this to the **selected** text layers in the
  active comp (one undo group; no save or render). Script layers are detected by a
  layer name containing `script` or the DancingScript font; text with keyframed Source
  Text is refused. The values are written straight into Effect Controls, where Oxi can
  tune them; there is no `CTRL_` layer (section 7).

### Zoom on the words

Scale the A-roll at stressed words and at changes of idea, not on a timer: a gentle
push in at the hook's start, a punch-in on the key word, a zoom-out when the speaker
lists several items, push in again for the payoff. That job ran 118 → 130 % with ease
influence 65, speed 0, and motion blur on. Take the moments from the new voice; never
copy another video's timecodes.

### Face lock

The frame follows the centre of the face; no tracking box is drawn.

1. Detect the face on an intermediate already normalised for rotation and size. That
   job used OpenCV YuNet every 3rd frame, interpolated between, Gaussian-smoothed
   (25 samples, sigma 5). Re-check the lag before reusing that smoothing at another fps.
2. With several people, choose the presenter and keep that person; do not take the
   largest face per frame. Review frames with no detection, turns and occlusion.
3. Bake the per-frame face centre (source pixels) into a guide null
   `FACE TRACK | source pixels`; add a guide null `LOCKON TARGET | move to reframe`
   (that job: `[540,490]`). A-roll anchor `[540,960]`, no parenting, no rotation.
   Position expression:

   ```javascript
   var f = thisComp.layer('FACE TRACK | source pixels').transform.position;
   var target = thisComp.layer('LOCKON TARGET | move to reframe').transform.position;
   var s = transform.scale[0] / 100;
   target - (f - transform.anchorPoint) * s;
   ```

4. Check that the footage covers all four edges on every frame, worst at zoom-out;
   raise the minimum scale rather than show an edge. Keep headroom and do not cut the
   hands mid-gesture.

### Sound on that hook

Every SFX different (deduplicated by checksum, not by name), each file played in
full at 0 dB with its whole tail: on a clash with the voice, move the cue, change the
sound or drop a layer rather than lower it. That was the job owner's rule; on Oxi's
jobs the sound pass in `music.md` applies.

## Source

Sections 2, 3 (machine-side checks), 4 (authoring), 6 and 7 are selectively adapted, in the
assistant's own words, from `iart-ai/motion-design-skills`, skill `after-effects`, files
`export-recipes.md`, `expressions.md`, `expression-library.md`, `performance-triage.md`,
`project-hygiene.md` (MIT, Copyright (c) 2026 iart.ai), commit `3c129f7`. Read 2026-10-16
without installing; safety check in (internal note, not published)
motion - kiem tra an toan va so voi skill dang co.md`.

Changed from the source: the H.264 claim (corrected above from live prefs); the broken
stagger snippet (dropped); delivery bitrates (left to `export.md`, which holds Oxi's measured
values). Everything marked **observed** comes from Oxi's own jobs and the Claude memory notes
named in each section, not from the repo.

Section 9 comes from reading AE GPT 1.3.1 (SUZA, ae-gpt.com), `jsx/index.js`, on 2026-10-22,
at Oxi's request; only the patterns are kept, no code was copied or run.

The section 5 "External" traps and section 11 come from two Codex skills in zip files Oxi
sent on 2026-11-10 (`typo-bds.zip` → `ocean-city-hook`, `minimalism-motion-graphic.zip` →
`adaptive-video-editor`), written on another machine (user folder `Computer`, drive `E:`).
Kept: the shadow recipe, face-lock method, zoom idea, AE traps and `apply_soft_text.jsx`
(copied unchanged apart from a header). Left out: that machine's paths, client names,
sample timecodes, plugin inventory and the "full permission for every plugin" rule.
