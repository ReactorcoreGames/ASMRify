"""
Background noise WAV generation via FFmpeg anoisesrc.
"""

import subprocess
import sys


def _startupinfo():
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None


# anoisesrc only natively supports white/pink/brown/blue/violet/velvet.
# green and gray are synthesized by EQ-shaping white noise.
_SYNTHESIZED_COLOR_FILTERS = {
    # Green noise: mid-band emphasis (rolloff outside ~300Hz-3kHz)
    "green": "equalizer=f=800:width_type=o:width=3:g=12,highpass=f=200,lowpass=f=4000",
    # Gray noise: equal-loudness weighted (boost lows/highs relative to mids, approximating inverse A-weighting)
    "gray": "equalizer=f=100:width_type=o:width=2:g=6,equalizer=f=8000:width_type=o:width=2:g=6,equalizer=f=2000:width_type=o:width=2:g=-4",
}


def generate_noise(color: str, duration_sec: float, sample_rate: int, output_path: str):
    """
    Generate a noise WAV using FFmpeg anoisesrc.

    color        — color name: white / pink / brown / green / gray
    duration_sec — length in seconds (should match the voice clip)
    sample_rate  — sample rate in Hz (e.g. 44100)
    output_path  — destination WAV path (will be overwritten)

    Raises RuntimeError on failure.
    """
    extra_filter = _SYNTHESIZED_COLOR_FILTERS.get(color)
    source_color = "white" if extra_filter else color

    args = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", f"anoisesrc=color={source_color}:sample_rate={sample_rate}:duration={duration_sec:.6f}",
    ]
    if extra_filter:
        args += ["-af", extra_filter]
    args += ["-ac", "2", "-y", output_path]

    try:
        result = subprocess.run(args, capture_output=True, text=True, startupinfo=_startupinfo())
        if result.returncode != 0:
            raise RuntimeError(f"Noise generation failed: {result.stderr}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found in PATH.")
