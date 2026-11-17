# oxi Premiere skills

Agent skills for editing video in Adobe Premiere Pro with an AI coding agent
(Claude Code, Codex, or anything that reads the `SKILL.md` format). They cover a
full post-production pipeline, written down and refined on real paid jobs:

| Skill | Stage |
|---|---|
| [`oxi-agent-brief`](skills/oxi-agent-brief) | Pin down the brief, scope and acceptance before any cut |
| [`oxi-premiere-workflow`](skills/oxi-premiere-workflow) | Dialogue edit, denoise, subtitles/SRT, music and SFX, color, timeline and editorial QC |
| [`oxi-broll-editor`](skills/oxi-broll-editor) | B-roll stage on an approved dialogue cut |
| [`oxi-text-graphics`](skills/oxi-text-graphics) | Key text / MOGRT stage after B-roll |
| [`oxi-after-effects`](skills/oxi-after-effects) | After Effects comps, expressions, renders, MOGRT authoring |

## What you need

- Adobe Premiere Pro, and After Effects for `oxi-after-effects`.
- A Premiere Pro MCP server connected to your agent. The skills were written against
  `premiere-pro-mcp`; tool names in the text refer to it.
- Python 3.10+ and ffmpeg for the scripts in each `scripts/` folder. Some scripts need
  extra packages (numpy, Pillow, opencv); each script's `-h` says what it uses.
  On Windows set `PYTHONUTF8=1` first: several scripts print Vietnamese and crash on
  the default console encoding without it.

## Install

Copy or link the skill folders into your agent's skills directory, for example
`~/.claude/skills/` for Claude Code or `~/.codex/skills/` for Codex.

## Read before using

- Much of the text is in Vietnamese, the language these skills were written in.
- **Oxi** is the editor who taught these rules; lines marked `(Oxi, date)` are his
  decisions, `(default)` lines are untested defaults, `(measured, job)` lines are
  numbers from one real edit. Calibrations stay in because they explain *why* a rule
  exists.
- Client, product and job names were replaced with placeholders (`Product A`,
  `Job E`, `CLIP_1234`...). Local paths appear as `<local path>`; references to private
  notes appear as `(internal note, not published)`. Words quoted from client videos
  appear as `<lời thoại>` (speech) or `<chữ trên hình>` (on-screen text); the rule
  around each one still stands.
- The per-genre video profiles and some worked examples are not published; the
  method to build your own is in `skills/oxi-premiere-workflow/references/video-profiles/`.
- The text mentions companion skills that are **not** in this repository, mainly
  `oxi-visual-style` (a visual-art vocabulary and style cards) and `oxi-script-craft`
  (reading client scripts), plus a few others (`oxi-explore-vlog`, `oxi-clip-affiliate`,
  ...). They hold one editor's taste and client process, not Premiere operation. When a
  step asks for one, skip it or plug in your own equivalent.
- The skills tell the agent to save, verify and keep the source sequence untouched,
  but they edit real projects. Work on a copy until you trust them.

## License

MIT for this repository's own text and code (see `LICENSE`). Third-party sources and
their licences are listed in `NOTICE.md`.
