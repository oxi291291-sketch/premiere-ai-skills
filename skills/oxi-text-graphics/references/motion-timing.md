# Motion timing — judging a template's built-in animation

Read this in Step 3 when two or more templates fit the line and you must pick one by how
it moves, or when Oxi asks why a text feels slow, cheap or jumpy.

**Scope stays as Oxi set it (2026-10-01): use only the animation already inside a
template; do not build effects.** Everything below is a yardstick for *choosing and
timing* templates, not permission to keyframe new motion. If Oxi asks for custom motion,
that is a separate request (`motion-graphics` / HyperFrames or After Effects), not this
stage.

All rules here are **(default)**: general motion-design practice, not yet tested on
Oxi's videos. Oxi's own rules in `SKILL.md` win on any conflict.

## 1. Match the template's speed to the video's personality

Scrub the template's entrance and estimate how long it takes to settle. Prefer the
template whose entrance falls in the band for the video's feel (the style card's `chot`
direction, `oxi-visual-style/references/style-card.md`):

| Feel of the video | Entrance settles in | Source's examples |
|---|---|---|
| Energetic | 100–250 ms | gaming |
| Playful | 150–300 ms | social media, children's content |
| Corporate / clear | 200–400 ms | enterprise software, healthcare (calm) |
| Premium / calm | 350–600 ms | editorial, finance |

Which band each of Oxi's series belongs to is not recorded; take it from the style card
or ask Oxi once.

A big headline or chapter title may run longer (600–1200 ms reads as a "reveal").
Anything slower than the band feels sluggish under speech; anything faster than
~100 ms reads as a cut, not motion.

## 2. Entrance vs exit

- The exit should be shorter than the entrance, roughly two thirds of it. A template
  whose exit is as long as its entrance leaves text lingering after the voice moves on;
  trim its tail (allowed in `SKILL.md` Step 4) rather than holding through the next line.
- Entrances decelerate (ease-out), exits accelerate (ease-in). A template that slides at
  constant speed (linear) on position or scale looks mechanical; prefer another one.
  This repeats `oxi-visual-style/references/cam-nang.md` ("không dùng linear").
- Opacity-only fades are the weakest choice for a key line; prefer a template that also
  moves or scales a little.

## 3. Multi-part templates (title + secondary, word-by-word)

- Parts should arrive one after another, not all at once. Keep the whole sequence of
  arrivals under about half a second, so the line is fully readable while the speaker
  is still on it.
- One thing moves at a time on screen. Do not let a text entrance collide with a B-roll
  cut or another text entrance in the same 0.3 s (matches the `staging-anim` term in
  `oxi-visual-style/data/14-chuyen-dong.json`).

## 4. Pace to speech

- One visual change per spoken beat, about 0.4–1.2 s apart. A template that keeps
  animating (looping sparkles, wiggles) after it has settled competes with the voice.
- Word times from Whisper `.json` or an SRT are estimates, off by up to about 0.2 s.
  `SKILL.md` lets text enter up to ~0.2 s before the keyword's onset; when a hit must
  land exactly (a number, a punchline), confirm the onset on the A1 waveform instead of
  trusting the word time alone.

## 5. What to avoid when choosing

- Bouncy or elastic easing on informational text (a tiny overshoot is fine; a visible
  bounce is not), particle bursts, glows, gradient-filled UI boxes.
- Any number, quote, price or result that the speaker did not say. This repeats
  `SKILL.md` Step 2 item 4: never put a made-up figure on screen; ask Oxi.

## Sources

Selectively adapted, in the assistant's own words, from:

- LottieFiles `motion-design-skill` (MIT, Copyright (c) 2025 LottieFiles), commit
  `f9a8a04`, files `reference/timing-easing-tables.md`, `director/motion-personality.md`,
  `director/disney-principles.md`, `patterns/multi-element.md`. The source's per-element
  UI timings and its advice to always add secondary and ambient layers were left out:
  they are for app interfaces, and extra layers fight Oxi's "one thing moves at a time".
- Barty-Bart `motion-graphics`, skill `motion-broll` (MIT, Copyright (c) 2026 Bart),
  commit `3d83d98`: pacing to speech, ±0.2 s word times, the banned list, and the rule
  never to invent figures.

Read on 2026-10-16 without installing either repo; see
(internal note, not published).
