---
name: oxi-after-effects
description: Làm việc trong Adobe After Effects cho Oxi qua MCP (AfterEffectsMCP file bridge, Higgsfield ae_*, Magnific after_effects_*) — dựng hoặc sửa comp, viết expression, comp chạy nặng/toComp/bake keyframe, render AE và xuất nền trong suốt (alpha, ProRes 4444, PNG sequence, WebM), làm MOGRT cho Premiere, sửa lỗi "please install After Effects" hay treo "Loading Motion Graphics Template", bẫy ExtendScript, rào an toàn khi AI sửa project AE, hook talking head có bóng chữ mềm, zoom theo lời và khóa mặt (face lock). Dùng khi Oxi nói After Effects, AE, comp, precomp, expression, bóng chữ, drop shadow, face lock, khóa mặt, AE chạy nặng, AE giật, toComp, render AE, xuất nền trong suốt, alpha, ProRes 4444, làm mogrt, Essential Graphics trong AE, panel mcp-bridge mất, hoặc nhờ dựng hiệu ứng trong AE — kể cả khi anh không gọi tên skill. Không phải đặt MOGRT lên timeline Premiere hay chọn mẫu chữ (đó là oxi-text-graphics), không phải dựng thoại/sub/màu trong Premiere (đó là oxi-premiere-workflow).
---

# OXI After Effects

Split out of `oxi-premiere-workflow` on 2026-10-22 at Oxi's request ("cái này ở AE nên chắc
nó là skill AE"). Lines marked **(Oxi)** in the reference are his decisions. Lines marked
**observed** were seen live on the edit machine. Lines marked **(default)** are general practice not yet
tested on Oxi's jobs; change them when he corrects one.

There is no reviewed step-by-step AE workflow yet. Say so when a job starts, then work from
[references/after-effects.md](references/after-effects.md) and live state.

## Before the first AE action

1. Read [references/after-effects.md](references/after-effects.md) in full.
2. Check live: AE version and project open, and which MCP channel answers (section 1 of the
   reference). Pick one channel per job and stay on it.
3. Record the project path and target comp (guard rail 3, section 9) before any edit.

## How to work

- **(Oxi)** Oxi builds effects in AE himself and does not want AI-generated effects; help
  means building the effect inside AE so he can adjust it, with tunable values on a `CTRL_`
  layer (reference section 7).
- **(Oxi, 2026-11-01)** HyperFrames is the main path for B-roll assets. When Oxi wants to
  adjust one himself, rebuild that scene in AE as editable layers (reference section 10).
- Apply the five guard rails in section 9 to every mutating call: one undo group per step,
  backup `.aep` before each stage, project guard, read back after raw scripts, target layers
  by id.
- A talking-head hook with soft text shadow, zoom on the stressed words or face lock:
  section 11 and `scripts/apply_soft_text.jsx`. It is an external look, untested on
  the edit machine and not yet reviewed by Oxi; say so when using it.
- Measure a slow comp before optimising it (section 3); accept a change only if the result
  moves less than 0.5 px.
- Render masters with alpha through the Render Queue; delivery settings follow the Premiere
  skill's `references/export.md` (section 2).
- Stop and ask Oxi before anything in section 8 (Reduce Project, deleting, resetting prefs or
  caches, updating AE, ending AE or Dynamic Link processes, overwriting a saved `.aep`).
- Stop after each stage and let Oxi check it before the next one.

## Related skills

- `oxi-text-graphics`: choosing MOGRT templates and placing text on the Premiere timeline.
- `oxi-premiere-workflow`: Premiere editing, subtitles, audio, colour, and export settings.

## Versioning

Published snapshots live in `Skills/_versions/oxi-after-effects/`. After any change, run
`python scripts/publish_version.py`, then `python scripts/verify_current.py`; continue only on
`validated-match`.
