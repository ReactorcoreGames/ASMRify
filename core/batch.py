"""
Batch processor — iterates all audio files in a folder and processes each one.
"""

import os
import time
from pathlib import Path

from core.processor import process_file

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".opus"}

_PRESET_ABBREV = {
    "soft_spoken_asmr":    "softs",
    "whispered_asmr":      "whisp",
    "relaxing_hypnosis":   "hypno",
    "deep_mesmerization":  "mesmr",
}

_NORM_SUFFIX = {
    "peak":    "pk_norm",
    "loudness": "ld_norm",
    # "both" mode produces two files; the WAV passed to process_file gets pk_norm,
    # and process_file appends -ld_norm for the companion.
    "both":    "pk_norm",
}


def _unique_path(folder: Path, stem: str, ext: str) -> Path:
    """Return folder/stem.ext, appending -2, -3, … until the path is free."""
    candidate = folder / f"{stem}{ext}"
    if not candidate.exists():
        return candidate
    n = 2
    while True:
        candidate = folder / f"{stem}-{n}{ext}"
        if not candidate.exists():
            return candidate
        n += 1


def _friendly_error(err: str) -> str:
    """Convert raw FFmpeg error text into a layperson-readable message."""
    low = err.lower()
    if "no such file" in low or "cannot open" in low:
        return "File could not be read — it may have moved or been deleted."
    if any(k in low for k in ("invalid data", "moov atom not found", "broken", "corrupt", "not a valid")):
        return "File appears to be corrupted or is not a valid audio file."
    if "no such filter" in low or "unknown encoder" in low:
        return "A required audio filter or encoder is missing — please check your FFmpeg installation."
    if "ffmpeg" in low and "not found" in low:
        return "FFmpeg was not found. Please install FFmpeg and make sure it is on your PATH."
    # Fallback: strip the first 120 chars of raw output so it's at least bounded
    first_line = err.strip().splitlines()[0] if err.strip() else "Unknown error."
    return first_line[:120]


def _collect_files(input_folder: str) -> list[Path]:
    folder = Path(input_folder)
    files = sorted(
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    )
    return files


def run_batch(
    input_folder: str,
    output_folder: str,
    settings: dict,
    progress_callback,
    stop_event,
) -> tuple[int, int, list[str]]:
    """
    Process all audio files in input_folder.

    progress_callback(i, total, filename, success, error, eta_seconds)
        Called after each file completes (including failures).
        i is 1-based.  eta_seconds is a float (may be None on first file).

    stop_event — threading.Event; checked before each file starts.

    Returns (processed_count, skipped_count, error_messages).
    """
    files = _collect_files(input_folder)
    total = len(files)
    if total == 0:
        return 0, 0, []

    os.makedirs(output_folder, exist_ok=True)

    out_dir = Path(output_folder)
    preset_key = settings.get("main_preset", "soft_spoken_asmr")
    preset_abbrev = _PRESET_ABBREV.get(preset_key, preset_key[:5])
    norm_mode = settings.get("normalization_mode", "loudness")
    norm_suffix = _NORM_SUFFIX.get(norm_mode, norm_mode)

    processed = 0
    skipped = 0
    errors = []
    durations = []

    for i, src in enumerate(files, start=1):
        if stop_event.is_set():
            skipped += total - i + 1
            break

        stem = f"{src.stem}-{preset_abbrev}-{norm_suffix}"
        output_wav = str(_unique_path(out_dir, stem, ".wav"))

        t0 = time.monotonic()
        ok, err = process_file(str(src), output_wav, settings)
        elapsed = time.monotonic() - t0

        if ok:
            processed += 1
            durations.append(elapsed)
        else:
            skipped += 1
            msg = f"{src.name}: {_friendly_error(err)}"
            errors.append(msg)

        # ETA estimate: average of completed files × remaining
        if durations:
            avg = sum(durations) / len(durations)
            remaining = total - i
            eta = avg * remaining
        else:
            eta = None

        progress_callback(i, total, src.name, ok, err, eta)

    return processed, skipped, errors
