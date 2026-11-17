# Timeline QC

Read [assets.md](assets.md), QC/export row and choice-record section: reconcile
the stage plans/library choices with the assets actually used, including font,
template/dependency, missing media, licence and unresolved evidence. Consult
`delivery` techniques only for a relevant delivery question. This is a source
and quality check, not a new creative-selection or asset-insertion pass.

Verify the actual review sequence before delivery. This is the mechanical
check; reading the finished cut as an editor (words, layout, proof, sources)
is [editorial-qc.md](editorial-qc.md).

- Confirm active sequence name and ID.
- Compare source and review sequences; prove source preservation.
- Inspect every affected track and clip start/end.
- Confirm linked audio/video boundaries and synchronization.
- Check for unintended gaps and one-to-two-frame microgaps.
- Audit every new dialogue boundary for clipped syllables, repeated language, broken grammar, factual drift, and unintended silence.
- Confirm music, captions, overlays, and adjustment layers end at their intended boundaries.
- Retranscribe or reconstruct edited audio when semantic accuracy matters.
- For a sequence with many new dialogue joins, use the companion process in [analysis-qc.md](analysis-qc.md) to preserve per-cut filmstrip/waveform evidence and a listening checklist. Treat automated discontinuity scores as review flags only.
- Re-trim full-length adjustment layers whenever the timeline shortens. A Lumetri layer left at its old length hangs past the last clip; verified on `ProductC_5-6PHUT` at 343.74 s over a 323.29 s timeline.
- Report per-track clip counts and end times, not only the sequence duration.
- Allow no more than three automatic correction-and-QC passes. Keep the safer longer edit and request Oxi's review when a join remains uncertain.
- Save immediately once verification passes, without asking, and report evidence concisely.

Do not use top-level `sequence.end` as the spoken-content boundary without checking tracks. An adjustment layer or overlay can extend far beyond the last dialogue clip. Compute maximum clip ends per relevant audio/video track.
