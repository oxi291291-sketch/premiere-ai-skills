# Video profiles — taste per video type

**(Oxi, 2026-11-12)** Each video type Oxi edits gets one profile file. Stage skills
(dialogue, B-roll, text, effects, music) keep the process and the gates that hold for
every type; a profile keeps what changes between types: density, look, rhythm, which
moves Oxi used, and the numbers measured on his own versions. Oxi trains each type
through its profile.

## Profiles

The profiles themselves are not published: each one is measured on named
client jobs. This folder ships the method only. Create a profile when the first real job of a type is edited; never fill one by guessing.

The profile says **what** the video is; the editing style chosen in the Style Card
(`phong_cach_dung`, files in `oxi-visual-style/references/editing-styles/`) says **how**
it is cut. Each stage reads both: profile section for taste and Oxi's numbers, style
file section for the look.

## How a stage uses a profile

1. The video-type card (`../video-types.md`) names the genre. Open the matching profile.
   No profile for that genre: say so in the report and work from the stage skill alone.
2. Each stage reads only its own section of the profile, together with its own skill.
   The stage skill wins on process and gates; the profile wins on taste for this type.
3. Numbers in a profile are measured references from named jobs, not targets. Use them
   to judge whether a draft is in Oxi's range, and say in the report where it is not.

## Training loop

When Oxi finishes correcting a job, compare his version with the assistant's, read-only
(`../dialogue-editing.md`, "Reference-comparison method"). Sort each difference:

- **Holds for every type** → the stage skill.
- **Holds for this type** → this type's profile, in the stage section, labelled
  `(Oxi, <date>, <job>)` with the measured number.
- **Only this client or this job** → the job's own notes, nowhere else.

Propose the sorting to Oxi before writing; write after he approves. Keep one meaning in
one place: a profile points to a stage rule instead of copying it.

## Labels

- `(Oxi, date)`: Oxi said or approved it.
- `(measured, job)`: read from Oxi's own edit of that job; a reference, not yet a rule.
- `(open)`: not known yet; ask or measure on the next job of this type.
