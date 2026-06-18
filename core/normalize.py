"""
Audio normalisation helpers — peak and loudness.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile


def _startupinfo():
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None


def peak_normalize(input_path: str, output_path: str) -> tuple[bool, str]:
    """Two-pass peak normalisation. input and output may be the same path."""
    si = _startupinfo()
    try:
        result = subprocess.run([
            "ffmpeg", "-i", input_path,
            "-af", "volumedetect",
            "-f", "null", "-",
        ], capture_output=True, text=True, startupinfo=si)

        m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", result.stderr)
        if not m:
            return False, "Peak normalize: could not read max_volume from ffmpeg output."

        max_db = float(m.group(1))
        if max_db >= 0.0:
            if input_path != output_path:
                shutil.copy2(input_path, output_path)
            return True, ""

        gain_db = -max_db - 1.0
        in_place = (input_path == output_path)
        if in_place:
            fd, tmp = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            actual_out = tmp
        else:
            actual_out = output_path

        try:
            subprocess.run([
                "ffmpeg", "-i", input_path,
                "-af", f"volume={gain_db}dB",
                "-y", actual_out,
            ], check=True, capture_output=True, text=True, startupinfo=si)
            if in_place:
                os.replace(actual_out, output_path)
        except subprocess.CalledProcessError as e:
            if in_place:
                try:
                    os.unlink(actual_out)
                except Exception:
                    pass
            return False, f"Peak normalize gain pass failed: {e.stderr}"

        return True, ""
    except subprocess.CalledProcessError as e:
        return False, f"Peak normalize measure pass failed: {e.stderr}"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH."


def loudness_normalize(input_path: str, output_path: str) -> tuple[bool, str]:
    """Single-pass loudness normalisation to -16 LUFS. input and output may be the same path."""
    si = _startupinfo()
    in_place = (input_path == output_path)
    if in_place:
        fd, tmp = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        actual_out = tmp
    else:
        actual_out = output_path
    try:
        subprocess.run([
            "ffmpeg", "-i", input_path,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-y", actual_out,
        ], check=True, capture_output=True, text=True, startupinfo=si)
        if in_place:
            os.replace(actual_out, output_path)
        return True, ""
    except subprocess.CalledProcessError as e:
        if in_place:
            try:
                os.unlink(actual_out)
            except Exception:
                pass
        return False, f"Loudness normalize failed: {e.stderr}"
    except FileNotFoundError:
        return False, "FFmpeg not found in PATH."
