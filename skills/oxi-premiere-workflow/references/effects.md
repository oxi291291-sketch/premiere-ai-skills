# Effects and graphic elements

Oxi approved a separate **Hiệu ứng / element** stage on 2026-10-27: create
graphic elements with HyperFrames or Remotion, render importable assets, place
them over the current Premiere edit and verify the composite. Premiere remains
the editorial source of truth. This stage follows reviewed key text and comes
before finishing; a request to start here uses the current edit without
repeating completed stages. Stop after delivery for Oxi to review.

## Scope and tool choice

**Tracking is opt-in (Oxi, 2026-10-27).** Run object, planar or camera tracking
only when Oxi explicitly requests it or explicitly selects a tracking option
for a named shot/range. Default to screen-fixed graphics or standalone graphics
without footage tracking. A request to add elements/B-roll, a general style or
storyboard approval, or the earlier table-tracking test does not authorize
tracking other shots. If a proposed design needs it, describe that option and
wait for Oxi to choose it before measuring tracks or running tracking tests.
Keep the approved tracking scope local to that shot/range; do not extend it to
the rest of a sequence merely because tracking is available.

Elements include animated icons, arrows, circles/highlights, connecting lines,
diagrams/charts, counters, badges and graphic reveals. Each element must help
explain a spoken idea or direct attention to something visible. Key-line text
belongs to `oxi-text-graphics`; subtitles and cut transitions keep their own
routes. Do not add those stages merely because effects were requested.

- Respect Oxi's named engine and an existing asset project's engine.
- For a new code-built element with no engine specified, use `hyperframes`
  according to the shared router; load its actual selected workflow and the
  core/animation/CLI domains needed for this asset. Describe the deliverable
  as a standalone companion asset, not a replacement edit of the footage.
- For Remotion/React assets, load `remotion:remotion-best-practices`, then
  create/markup/render as needed. If its local skill or runtime is absent,
  report the missing capability; do not pretend a render was made or silently
  migrate an existing project to another engine.
- AE-specific work uses `oxi-after-effects` when requested or needed. Existing
  video-brand-kit helpers remain an optional legacy source in `assets.md`;
  they are not a prerequisite for the HyperFrames/Remotion path.

This is an authoring/import contract, not evidence that either renderer has
been tested on the current host. Inspect installed tools and GPU before use;
verify alpha/export support with a short asset using the selected runtime.
Keep engine-specific API/codec flags in its owning skill/current docs.

## 1. Read the current edit and plan the elements

Read the live sequence after Oxi's latest changes: sequence ID/name, frame
size, FPS/timebase, duration, track contents, current text/subtitle windows
and approved Style Card, including the effects parts of its `phong_cach_dung`
styles (`oxi-visual-style/references/editing-styles/<slug>.md`; only where the
card's `cho_dung` places them). Watch the actual shot and listen to the relevant
line; use timeline audio/transcript timing rather than raw-source or script
timecodes. Refresh any map invalidated by a later edit.

Create `<job>/effects/effects_plan.json`. Each entry records an ID, purpose
and evidence (spoken line or visible action), timeline in/out and cue point,
engine/source project, intended render path, destination track, screen region
or subject anchor, alpha requirement, and optional SFX requirement. Also
record sequence ID, FPS and frame size. Snap placement and duration to frames;
check occupied tracks and overlaps before placement. Use the approved style
and brief rather than reopening them. Do not invent statistics for a chart or
counter; label an illustrative schematic and never present it as measurement.

### Reference, design and compositing (Oxi, 2026-10-27)

Read [assets.md](assets.md) before selecting a new treatment: dictionary and
knowledge → `motion`/`vfx` techniques → OXI Assets icons, arrows, overlays and
compatible presets/templates. Check suitable library resources before building
from scratch. Keep the chosen engine, tracking scope and existing review gates;
record term/technique/asset sources alongside the effects plan.

Before building, choose a visual treatment for the actual shot, not just an
element type. Use `shot-reference-library` for relevant motion references and
inspect the selected preview/demo; use `hyperframes-registry` to discover
reusable components when using HyperFrames. Record the reference and what is
being adapted. Neither a catalog listing nor an unread demo proves a good fit.
If no reference fits, design an original treatment and say so. Reference assets
remain references unless their reuse rights have been verified.

Use `oxi-visual-style` and, when relevant, `oxi-brand-guidelines` to carry the
approved style into stroke weight, shape, palette, typography, material and
depth. Define entry, readable hold and exit, cue, motion hierarchy and easing;
load `hyperframes-animation`/`hyperframes-keyframes` or the corresponding
Remotion guidance for execution. Avoid giving unrelated ideas the same generic
fade/slide. Judge the design on a frame of the actual footage, with adjacent
elements visible. Show alternatives only when a consequential design choice
is still open; reuse the style Oxi already approved.

Classify every planned element as screen-fixed, object-attached or a separate
full-frame graphic, applying the opt-in rule above before selecting an
object-attached treatment. Record the anchor and whether the shot needs position/
scale/rotation tracking, perspective tracking, foreground occlusion, motion
blur or lighting/grain matching. Intentional screen-fixed graphics need no
tracking; an object-attached graphic must follow its anchor across the shot.

Choose tools from those needs: HyperFrames/Remotion for graphic authoring;
`oxi-after-effects` when tracking, masks/rotoscoping, perspective or compositing
requires it; `blender-mcp` only when real 3D geometry, camera or lighting is
needed. Check available capabilities and test a short section on the real shot
before committing. A skill name is not evidence of working automated tracking.
For code-rendered graphics, tracking data must be measured from the footage
and mapped to the current timeline, not guessed as decorative keyframes.

Render either a verified transparent asset or a composite against a derived
copy of the exact approved shot. Record that choice, source range and any
colour transforms so the footage is neither baked twice nor graded twice.
Keep the original edit underneath unchanged. If a required track/mask or
composite cannot be verified, report that element as blocked and show the
limitation; do not silently substitute a drifting sticker or change the design.

Extend each effects-plan entry with the chosen reference/treatment, motion
beats, attachment mode, required compositing operations, responsible tool and
test evidence. Whole-shot graphics that fill missing B-roll belong to
`oxi-broll-editor/references/generated-broll.md` and its storyboard approval
gate, even when built with the same engine.

## 2. Build and render the asset

Keep editable source under `<job>/effects/<element-id>/` and renders under
`<job>/effects/renders/`. Carry over the sequence's frame size, FPS, duration,
fonts, colours and safe regions. Preserve existing source and alternate renders.

Use a transparent background for an overlay that must reveal footage. Verify
the actual output has usable transparency; a `.mov` extension alone does not
prove alpha. Use a compatible alpha-capable format or image sequence supported
by both the renderer and Premiere, and test the import before batch rendering.
Use an opaque render only for a planned full-frame graphic. Do not substitute
a black background or unapproved chroma key for transparency.

Preview the start, active motion and exit; then render the importable output
when the assigned stage includes placement in Premiere. A browser/Studio
preview alone is not delivery of that stage. A request only to create or
preview an element stops at that requested output and does not authorize
timeline placement. External generation, paid stock and publishing require
their own authorization; code-based local rendering is not AI generation.

## 3. Import and place without changing the approved edit

Use the Premiere execution/verification contract and `premiere-mcp.md`.
Preserve the source sequence and work in a named effects review sequence
unless Oxi already authorized the intended sequence. Import renders into a
clearly named effects bin. Use available V6–V9 graphics lanes after reading
their contents; keep existing key text intact. If those lanes cannot fit the
element, resolve the track choice before writing rather than overwriting text
or repurposing colour/transition/subtitle tracks.

Place with overwrite semantics on the chosen graphics track, with audio
excluded unless an SFX was explicitly planned. Do not use a ripple insert.
Trim to the planned frame boundaries; do not speed up an asset by accident to
fit. Keep source anchoring aligned through subject/camera movement for shots
whose tracking Oxi explicitly requested; otherwise use the default screen-fixed
layout.

The stage preserves all pre-existing clips, timing, effects, text and audio
on every track, plus sequence duration. Only the planned new elements (and
SFX if in scope, on free A2/A3 space) may be added. Re-read the live timeline
after placement and compare those invariants. Audio/SFX must not leak from
an asset import or overwrite existing sound.

## 4. QC and handoff

Verify the rendered composite in Premiere across entry, active motion and
exit: cue matches the actual spoken word/action, enough reading time, clean
alpha edges, no black plate or unintended full-screen cover, correct font and
colour, no clipping or jitter, and no collision with face/product/text/subs
or platform UI. Inspect motion in a short review render when stills cannot
establish anchoring or timing. A renderer's standalone preview is not proof
that the Premiere composite is correct. Measure face, protected-box and
safe-zone collisions with `composition-gate.md` on the placed composite.

For object-attached elements, also inspect the fastest camera/subject motion,
perspective changes, occlusion boundaries and frame edges. Check drift, scale,
mask chatter, foreground ordering and integration with footage texture/blur.
Save the review range and result as evidence; a correct first frame is not a
passing composite.

Deliver the review sequence, editable element sources, renders and
`effects_plan.json`, with QC evidence and unresolved limits. Save once the
timeline verification passes, report tracks/timecodes and source preservation,
update the job progress file, and **stop for Oxi to review the effects stage**.
Do not continue automatically to denoise, music, transitions, colour or sub.
