"""
Binaural beat layer generator.

Constant presets (alpha, theta, gamma) are generated entirely via FFmpeg's
built-in sine source — no numpy needed.  The theta_delta ramp preset uses
numpy to produce a stereo float32 raw file with a time-varying beat frequency.

Public interface
----------------
BINAURAL_PRESETS : dict
    Parameters for each preset (carrier_hz, beat_hz, volume_db).
    beat_hz may be a (start, end) tuple for ramp presets.

generate_binaural_filter(preset_key, duration_sec) -> str | None
    Returns an FFmpeg filter_complex fragment string for constant presets, or
    None if the preset needs a numpy-generated temp file (theta_delta).

generate_binaural_wav(preset_key, duration_sec, sample_rate, output_path)
    Writes a stereo float32 raw file for the theta_delta ramp preset.
    Must be read with: -f f32le -ar <sample_rate> -ac 2 -i <output_path>
"""

import numpy as np


BINAURAL_PRESETS = {
    "alpha": {
        "carrier_hz": 200,
        "beat_hz":    10,    # constant
        "volume_db":  -5,
    },
    "theta": {
        "carrier_hz": 180,
        "beat_hz":    6,     # constant
        "volume_db":  -2,
    },
    "theta_delta": {
        "carrier_hz":    180,
        "beat_hz":       (12.0, 0.5),  # ramp start → end
        "volume_db":     4,
    },
    "gamma": {
        "carrier_hz": 200,
        "beat_hz":    40,    # constant
        "volume_db":  0,
    },
}

# Presets that use a numpy-generated temp WAV (non-constant beat frequency)
_NUMPY_PRESETS = {"theta_delta"}


def generate_binaural_filter(
    preset_key: str,
    duration_sec: float,
    volume_offset_db: float = 0,
) -> "str | None":
    """
    Return an FFmpeg filter_complex fragment for constant binaural presets.

    The fragment produces a labelled stereo stream [binaural] ready to amix
    with the processed voice.  Caller appends this fragment to their own
    filter_complex string and includes [binaural] in the amix inputs.

    Returns None for ramp presets (theta_delta) — those need a temp WAV.
    """
    if preset_key not in BINAURAL_PRESETS or preset_key in _NUMPY_PRESETS:
        return None

    p = BINAURAL_PRESETS[preset_key]
    carrier = p["carrier_hz"]
    beat = p["beat_hz"]
    vol_db = p["volume_db"] + volume_offset_db

    f_left  = carrier - beat / 2.0
    f_right = carrier + beat / 2.0
    dur = duration_sec

    fragment = (
        f"sine=f={f_left:.3f}:duration={dur:.3f}[bin_l];"
        f"sine=f={f_right:.3f}:duration={dur:.3f}[bin_r];"
        f"[bin_l][bin_r]amerge=inputs=2,volume={vol_db}dB[binaural]"
    )
    return fragment


def generate_binaural_wav(
    preset_key: str,
    duration_sec: float,
    sample_rate: int,
    output_path: str,
) -> None:
    """
    Write a stereo float32 raw file for ramp binaural presets (theta_delta).

    The beat frequency sweeps linearly from beat_hz[0] to beat_hz[1] over the
    full audio duration.  L channel lags, R channel leads — the difference
    between them is the perceived binaural beat.

    FFmpeg read: -f f32le -ar <sample_rate> -ac 2 -i <output_path>
    """
    p = BINAURAL_PRESETS[preset_key]
    carrier = float(p["carrier_hz"])
    beat_start, beat_end = p["beat_hz"]
    vol_db = float(p["volume_db"])
    amplitude = 10.0 ** (vol_db / 20.0)

    n = int(duration_sec * sample_rate)
    dt = 1.0 / sample_rate

    # Linearly-ramping beat frequency over time
    beat_f = np.linspace(beat_start, beat_end, n, dtype=np.float64)

    # Half-beat offset for each channel
    f_left  = carrier - beat_f / 2.0
    f_right = carrier + beat_f / 2.0

    # Integrate instantaneous frequency to get phase (avoids discontinuities)
    phase_left  = np.cumsum(f_left)  * dt * 2.0 * np.pi
    phase_right = np.cumsum(f_right) * dt * 2.0 * np.pi

    left  = (amplitude * np.cos(phase_left)).astype(np.float32)
    right = (amplitude * np.cos(phase_right)).astype(np.float32)

    stereo = np.empty(n * 2, dtype=np.float32)
    stereo[0::2] = left
    stereo[1::2] = right
    stereo.tofile(output_path)
