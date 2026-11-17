# Music selection and review mix

## Select music

1. Read the script or timeline transcript before searching. Read `<job>/style_card.json`, direction `chot`, field `nhac` and the Âm/nhạc part of its `phong_cach_dung` style files (`oxi-visual-style/references/style-card.md` section 5); if `chot` is empty, ask one question to pick a direction. Sound terms: `oxi-visual-style/references/tu-dien-visual-art.md#12-am-thanh`.
2. Define documentary, emotional, pacing, instrumentation, vocal, and licensing constraints.
3. For new music/SFX choices, read [assets.md](assets.md): sound/rhythm knowledge
   → `audio` techniques → OXI Assets music by mood/section, ambience, foley and SFX.
   Reuse approved job audio; record asset IDs and the choice/evidence with the
   audio plan. If MCP is unavailable or no candidate fits, state which and search
   Oxi's verified local libraries when available:
   - `<asset library>\Sound\Thu_vien_nhac_nen_Suno`
   - `<asset library>\Sound\Nhạc Nền Xịn`
4. Narrow candidates by folder, filename, duration, metadata, dynamic density, and spectrogram.
5. State honestly whether selection is technical or based on human listening. Do not claim to have heard music when only metadata and spectral evidence were inspected.

For educational narration, prefer instrumental, sparse midrange, restrained percussion, and a bed that does not compete with speech. Avoid vocals and misleading religious or cinematic cues unless the content requires them.

## Build a review mix

1. Duplicate the source to `<sequence>_MUSIC_REVIEW`.
2. Import shortlisted tracks and place them on unused audio tracks.
3. Align changes to topic boundaries, not arbitrary song durations.
4. Start around `-24 dB` as a test bed, fade in/out, and crossfade changes. Adjust after listening.
5. Trim timeline clip ends to the dialogue or intended visual boundary.
6. Verify the source sequence contains no added music.
7. Leave the review sequence active at a useful listening point and save.

## Music structure and SFX accents **(Oxi, 2026-10-26, KAIYO reference comparison)**

1. **Change track by section**, not one bed for the whole video: on KAIYO a groove track for the intro, a separate track for the test/challenge segment, and the main track for the rest. Changes land on topic boundaries (step 3 above).
2. **Drop the music out under key lines** for about 2-13 s (the claim or verdict the video turns on), then bring it back. Silence under a line is emphasis.
3. **Accent a reveal or result with a "wow"-type SFX** (a real recorded file from Oxi's library, per the Sound pass below).
4. Levels and fades were not measured in this comparison; keep the test-bed level and fades from "Build a review mix" until they are.

## Protect listening tests and use selective accents **(Oxi approved, 2026-10-29)**

Source: Oxi's speaker-review revision and his instruction that apparent dialogue
gaps are reserved for test music, followed by approval to record the lessons.
Evidence: `<local path> ULT Tower 5/6. AI/music-sfx-20261029/`
(`revision-full.json`, `audio_plan.json`, `BAN-GIAO-NHAC-SFX.md`). The later added
music/SFX pass is a review, not proof of Oxi's final listening approval.

- Treat real speaker, microphone, karaoke and mode-comparison audio as content.
  Read every existing audio track: a gap on A1 may contain the test on another
  track, or a listening interval Oxi deliberately reserved. Map these intervals
  before adding a bed. Keep their duration, source audio and existing automation;
  do not tighten them or fill them with new music/SFX unless Oxi asks.
- New music belongs under the surrounding presentation. Leave the protected
  listening interval free of added sound so viewers can judge the device. An
  intentional unfilled interval is not permission to choose its test song.
- Use music withdrawals and selective SFX for delivery: a joke/reaction, reveal
  or important number. Do not put a whoosh on every text or mode change. The
  existing key-line dropout rule applies; there is no fixed SFX count or gain.
- Preserve Oxi's existing track ownership, transitions and swooshes. Put the new
  layers on verified empty tracks in the review clone; do not move his tracks
  just to match the standard layout. Verify the protected audio and all picture
  tracks after placement, and distinguish measurements/reconstruction from a
  listened native export.

## Premiere Level keyframes

Premiere's `Volume > Level` component parameter is linear amplitude with +15 dB of headroom: an untouched clip (0 dB in the UI) reads `0.17782794` (verified live on the edit machine, 2026-10-12). Convert with `value = 10^((dB-15)/20)`; examples: `0 dB = 0.1778279`, `+3 dB = 0.2511886`, `-24 dB = 0.0112202`. Read the clip's current value first and refuse to write if it is not the value you expect. The older note here used `10^(dB/20)`, which lands 15 dB too loud.

Use `ComponentParam.addKey(Time)` and `setValueAtKey(Time, linearValue, true)`. Verify `getKeys()` and `getValueAtKey()` afterward.

Do not trust a tool success message alone. In the observed MCP version, `adjust_audio_levels` passed negative dB directly and could clamp Level to silence, while `add_audio_keyframes` called nonexistent `addKeyframe`. Also verify `trim_clip`: it may change the source out-point without shortening the timeline TrackItem. Set and verify `clip.end` with a `Time` object when necessary.

## Sound pass: SFX, beat and licences

All rules here are **(default)**: adapted from outside skills, not yet tested on Oxi's videos. Where SFX sit on the timeline (A2/A3, `Swoosh_*.wav` on the V10 transition pairs) is in `finishing-layout.md`; loudness is measured and reported per `export.md`, with no new target. For cue placement or studying a video reference, read [sound-cue-placement.md](sound-cue-placement.md).

1. **Audit the full audiovisual mix.** When Earshot is available, use its local `timeline` over the full playback range and inspect the picture at the reported cue times. For dense passages use short `detail: high` windows. Keep predictions about layered stereo audio qualified. With waveform or meters alone, report technical findings only. Give Oxi up to five listening checkpoints for the largest beat error, long effects, the main reveal, or cues under dialogue.
2. **Real recorded files only.** Never generate a beep, sine or oscillator sound in code as an SFX or music stand-in. Search Oxi's library through the MCP `oxi-assets` first (the common library workflow in `assets.md`) and keep each SFX's asset id in the plan so the licence line below can name it.
3. **Beat grid, when cuts or reveals should land on the music** (intro, montage, a reveal under music; not dialogue cuts): beat trackers can lock onto the off-beat (hi-hats) and put every cut half a beat late. Low-pass the music below about 120 Hz, compare the kicks with the detected beat lines over the first few bars, and if they disagree shift the whole grid by the median offset. Report whether it was shifted and by how much, and the cut-to-beat error of each cut in ms. A music-driven reel usually cuts on a 120–130 BPM grid; that is a reference, not a requirement.
4. **Licence check before the final export.** List every SFX and music source actually used, one line each: source, licence, link or folder, and whether it allows this use (where the video will be published). If a licence is unknown, name that sound and do not call it fine; files from Oxi's own libraries take whatever Oxi has recorded, or one question to Oxi.
5. **`CREDITS.txt` next to the export**, listing the sounds and music actually used, ready to paste into a description.
6. **Measure the exported file**, never an intermediate WAV or the sequence preview. Also run the `export.md` loudness command with `-ac 1` to check that the mix still holds up in mono.
7. **One hit per cue.** Library packs (e.g. Boom Library Casual UI) often hold 4–5 variations in one 4–25 s file, split by silence. Never drop the whole file on the timeline: list the hits first (`ffmpeg -i <file> -af silencedetect=noise=-45dB:d=0.15 -f null -`), extract one into the job folder, and record which hit (index, source in/out) in the plan. Keep its attack and whole tail; a click or pop starts on its first sample, a transition whoosh is placed by its loudest point. If the tail does not fit before the next cue, choose a shorter sound instead of cutting it.
8. **Deduplicate SFX by checksum**, not by file name: libraries ship the same sound under several names.
9. **Measure each SFX against this speaker's voice, and report it.** Take the voice's peak as the 95th percentile of 50 ms windows over kept words, render or export the SFX tracks alone, and give each hit's peak in dB relative to that voice peak. Yardstick by role from `ghost-editor` (2026-11-10): UI −14, whoosh −12, impact −8, meme −3 dB. Flag any hit louder than the voice or too quiet to register. This is a measurement for the report; the gain itself stays per job, as "Protect listening tests" above says. Never lift the finished mix to fix a level.
10. **A reaction or meme sound sits in air.** Place it on or just after the punchline, in a pause, never over a spoken word; when the cut leaves no pause, ask before opening one. One meme sound is never used twice in a video. Sounds ripped from YouTube or other people's videos are a Content ID risk on YouTube; name them in the licence line (item 4).

Sources, adapted in the assistant's own words: Barty-Bart `motion-graphics`, skill `sound-effects` (MIT, Copyright (c) 2026 Bart), commit `3d83d98`; nateherkai `herk-edit-kit`, skill `motion-showreel` (MIT, Copyright (c) 2026 Nate Herk), commit `10511e5`. Not copied: Barty's `-16 LUFS` / `-4 dBFS` mix target (conflicts with `export.md` and `audio-cleanup.md`), his bundled SFX library and Python mixer, and herk's paid music generation. Read 2026-10-16 without installing; see (internal note, not published). Items 9–10 are adapted from `kurbaitaev/ghost-editor` (MIT), commit `ce17272`, `references/sound-and-memes.md` and `SKILL.md`, read 2026-11-10 without installing. Items 7–8 come from the Codex skill `adaptive-video-editor` (zip Oxi sent 2026-11-10, written on another machine); its Python slicer was not copied because it fades the first 15 ms of every hit, which softens a click's attack.
