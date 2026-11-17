#!/usr/bin/env python3
"""Conservative DeepFilterNet3 speech cleanup with preserved work files."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import types
import wave


def require_program(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Required program not found: {name}")
    return path


def reserve_outputs(output: Path) -> tuple[Path, Path]:
    prepared = output.with_name(f"{output.stem}_work_pcm48.wav")
    raw = output.with_name(f"{output.stem}_work_deepfilter_raw.wav")
    collisions = [path for path in (output, prepared, raw) if path.exists()]
    if collisions:
        joined = ", ".join(str(path) for path in collisions)
        raise SystemExit(f"Refusing to overwrite existing file(s): {joined}")
    output.parent.mkdir(parents=True, exist_ok=True)
    return prepared, raw


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def read_pcm16(path: Path):
    import numpy as np
    import torch

    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        sample_rate = source.getframerate()
        sample_width = source.getsampwidth()
        frames = source.readframes(source.getnframes())
    if sample_width != 2 or sample_rate != 48000:
        raise SystemExit(
            f"Expected 48 kHz PCM16 work input; got {sample_rate} Hz, "
            f"{sample_width * 8}-bit"
        )
    audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    return torch.from_numpy(audio.reshape(-1, channels).T), sample_rate


def write_pcm16(path: Path, audio, sample_rate: int) -> None:
    import numpy as np

    samples = audio.detach().cpu().clamp(-1.0, 1.0).numpy().T
    pcm = np.rint(samples * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as target:
        target.setnchannels(pcm.shape[1])
        target.setsampwidth(2)
        target.setframerate(sample_rate)
        target.writeframes(pcm.tobytes())


def load_deepfilter():
    try:
        import torch
        import torchaudio
    except ImportError as exc:
        raise SystemExit(
            "Install compatible CUDA PyTorch, torchaudio, and deepfilternet "
            "in an isolated environment before running this script."
        ) from exc

    try:
        from torchaudio.backend.common import AudioMetaData  # noqa: F401
    except ImportError:
        backend = types.ModuleType("torchaudio.backend")
        common = types.ModuleType("torchaudio.backend.common")
        common.AudioMetaData = object
        backend.common = common
        sys.modules["torchaudio.backend"] = backend
        sys.modules["torchaudio.backend.common"] = common
        torchaudio.backend = backend

    try:
        from df.enhance import enhance, init_df
    except ImportError as exc:
        raise SystemExit(
            "DeepFilterNet is unavailable. Install the deepfilternet package "
            "in the active isolated environment."
        ) from exc
    return torch, enhance, init_df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--atten-limit-db", type=float, default=12.0)
    parser.add_argument("--lufs", type=float, default=-14.0)
    parser.add_argument("--true-peak", type=float, default=-1.5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if not source.is_file():
        raise SystemExit(f"Source file not found: {source}")
    if args.atten_limit_db <= 0:
        raise SystemExit("--atten-limit-db must be greater than zero")

    ffmpeg = require_program("ffmpeg")
    prepared, raw = reserve_outputs(output)
    run(
        [
            ffmpeg,
            "-n",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(prepared),
        ]
    )

    torch, enhance, init_df = load_deepfilter()
    audio, sample_rate = read_pcm16(prepared)
    model, state, _ = init_df(log_level="INFO")
    cleaned = enhance(
        model,
        state,
        audio,
        pad=True,
        atten_lim_db=args.atten_limit_db,
    )
    write_pcm16(raw, cleaned, sample_rate)

    run(
        [
            ffmpeg,
            "-n",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(raw),
            "-af",
            f"loudnorm=I={args.lufs}:TP={args.true_peak}:LRA=7",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s24le",
            str(output),
        ]
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(
        f"status=ok device={device} attenuation_db={args.atten_limit_db:g} "
        f"output={output} prepared={prepared} raw={raw}"
    )


if __name__ == "__main__":
    main()
