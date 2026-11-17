# Voice denoising and cleanup

Use this route when Oxi asks to `giảm ồn`, `khử ồn`, `khử noise`, `khử nois`, `làm sạch tiếng`, or improve spoken audio.

## Default

- Prefer DeepFilterNet3 with the compatible CUDA-enabled PyTorch runtime when an NVIDIA GPU is available.
- Use a conservative attenuation limit of 12 dB. Increase it only after Oxi requests stronger removal or approves an A/B sample; aggressive removal can smear consonants and make speech sound robotic.
- Normalize the cleaned result near -14 LUFS integrated with true peak capped at -1.5 dBTP for ordinary web/video review. Treat the peak value as a ceiling, not a required target.
- Export 48 kHz WAV. Prefer 24-bit PCM for the final imported stem.
- Keep the original audio intact. Never destructively replace source media.

## Premiere sequence pattern

1. Inspect the active sequence and audio tracks. Preserve the source sequence; duplicate it first unless it is already the intended review sequence.
2. Export the dialogue-only sequence mix before music/SFX, or mute all non-dialogue tracks before extraction.
3. Measure the original duration, integrated loudness, and true peak.
4. Run `scripts/denoise_deepfilter.py` into a uniquely named task-workspace output. Preserve its prepared and raw work files.
5. Import the cleaned WAV and place it from sequence start on the next verified-empty audio track.
6. Keep the original track and any FFmpeg comparison track. For a three-way review use:
   - A1: original
   - A2: light FFmpeg cleanup
   - A3: DeepFilterNet3 AI cleanup
7. Enable only one comparison track at a time. Never sum original and cleaned stems during A/B review.
8. Leave the AI version active by default after Oxi asks to try the AI workflow.

## Verification

- Confirm DeepFilterNet reports `cuda` when GPU acceleration is expected.
- Confirm the output file exists and its duration matches the dialogue mix within one sequence frame.
- Measure the final WAV and the exported Premiere mix; report integrated loudness and true peak.
- Re-read the active sequence and verify the exact imported item, target track, clip start/end, and mute state.
- Verify the picture and sequence duration remain unchanged, then save the project.

## Fallbacks and boundaries

- If DeepFilterNet cannot run, use a light FFmpeg chain: high-pass near 70 Hz, restrained broadband denoise, small presence EQ, light compression, then loudness normalization.
- Prefer the AI route for complex steady noise; prefer light FFmpeg cleanup when preserving the most natural timbre matters more than maximum noise removal.
- Do not use a cloud speech-enhancement service or upload private dialogue without Oxi's explicit approval.
- Do not delete alternate stems or intermediate renders. Oxi decides cleanup.
