# Composition gate in Premiere

`scripts/composition_gate.py` checks, with numbers, that no overlay covers the
speaker's face or a protected area, and that every text, caption, callout and
inset B-roll box stays inside the platform safe zone. It supplements visual layout review after text, B-roll or effects are placed. Copied from
`oxi-auto-editor` on 2026-10-31; the Premiere copy also reads folders of
frames from `pr_export_frames.py`.

Run it after every placement pass that adds or moves overlays (text stage,
B-roll stage, effects stage), before showing the review sequence to Oxi. A
pass is evidence for the sampled frames only; the visual check of entry,
motion and exit in `effects.md` and `text-graphics.md` still applies.

## Inputs

- **Plan** (`--plan`, repeatable): JSON list, or a dict with `overlays`/`items`
  and an optional `protect` list. Each item: `start`, `end` in **sequence**
  seconds, optional `id`, `kind` (text | caption | callout | broll), `box`
  `[x, y, w, h]` as frame fractions, `full_frame` for B-roll that replaces
  the picture. Write it from the placed clips (track item start/end and the
  Motion position/scale), not from the intended plan alone.
- **Protect boxes** (`--frame-plan` with a `protect` list): UI elements,
  products, a logo the shot is about.
- **Captions** (`--srt`): every cue becomes a caption window.
- **Boxes**, in order of preference:
  1. `--overlay-layer`: frames of the overlay alone with alpha (a HyperFrames
     render, for example). Most exact.
  2. `--base`: the same times exported with the overlay tracks hidden. The
     box is the pixel difference, and the face is detected on the base, where
     no text hides it. This is the normal Premiere route.
  3. Declared `box` in the plan. Used when nothing can be measured.

  A box that is neither measured nor declared fails.

## Steps

1. Print the sample times:
   `python scripts/composition_gate.py --times --plan <job>/work/text_plan.json [--plan <job>/work/broll_plan.json] [--srt <job>/work/sub.srt]`
2. Export the review sequence at those times:
   `python scripts/pr_export_frames.py --sequence "<REVIEW>" --at <times> --out <job>/work/comp/render`
3. Hide the overlay tracks (text V6–V9, inset B-roll V2/V3, effects tracks;
   tool order per `premiere-mcp.md`), export again into a **new** folder
   (`pr_export_frames.py` never overwrites):
   `... --at <times> --out <job>/work/comp/base`
   Then turn the tracks back on and confirm they are visible again.
4. Run the gate:
   `python scripts/composition_gate.py <job>/work/comp/render <job>/work/comp/out --plan ... --base <job>/work/comp/base [--frame-plan ...]`
5. Read `out/composition_gate.json` and `out/sheet.jpg` (failures first). Fix
   each failing overlay, then repeat from step 1 for the changed windows.

Exit codes: 0 pass, 1 fail, 2 setup error (bad arguments, empty frame folder,
model or OpenCV missing). A window with no exported frame inside it fails
(`no frame sampled inside its window`), and so does a sample whose base frame
is missing: the gate never passes what it did not see.

`--face-every N` also checks that the face itself sits inside the zone on a
frame every N seconds outside full-frame B-roll. In a frame folder only the
exported times are checked, so export those times too.

## Zone and model

- `--zone 9x16` is top 12 %, bottom 25 %, left 0 %, right 15 % of the frame.
  **These margins were set by the assistant on 2026-10-31 and are not yet
  approved by Oxi.** For another platform or a 16:9 sequence pass
  `--zone T,B,L,R` and say which margins were used.
- Faces come from YuNet (`models/face_detection_yunet_2023mar.onnx`, source
  and licence in `models/README.md`), padded by 10 % of the face height.
  Faces shorter than half the tallest face are ignored. Needs
  `opencv-python-headless` and `numpy`; `--model` or `OXI_FACE_MODEL`
  points at another copy.

## Text spacing correction (Product D, 2026-10-31)

The legacy `9x16` preset allows zero left inset: text at 4.1% from the left passed on Product D and Oxi rejected its spacing. Do not use it to approve text placement. Use `--zone text_9x16` (top/bottom/left/right = 16/28/10/18%, assistant working defaults, not an official platform specification) or explicit job margins. The Product D correction uses 17/31/12/20%. These numbers are not universal approved presets.

Measure the whole visible block over entry, hold and exit, including shadows/glow; fit and place from the union of those bounds, not Motion Position alone or a character-count width estimate. Report minimum clearances to all four frame edges. A box barely inside the safe area still needs visual review for breathing room. Gate PASS is a geometry result only.

Oxi also rejected a global left shift on the same job. Side UI protection must not move all text off the full-frame center: constrain line width instead. The default visible hold block is horizontally centered at x=0.5; record any shot-specific exception.
