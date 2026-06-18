"""
Audio probing and format conversion utilities.
"""

import os
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


def probe_audio(path) -> dict | None:
    """
    Return {duration: float, format: str} for a valid audio file, or None.
    Uses ffprobe — returns None if the file is not valid audio or ffprobe fails.
    """
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,format_name",
            "-of", "default=noprint_wrappers=1",
            str(path),
        ], capture_output=True, text=True, startupinfo=_startupinfo())
        if result.returncode != 0:
            return None
        info = {}
        for line in result.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                info[k.strip()] = v.strip()
        duration = float(info.get("duration", 0) or 0)
        fmt = info.get("format_name", "")
        if duration <= 0 or not fmt:
            return None
        return {"duration": duration, "format": fmt}
    except (FileNotFoundError, ValueError):
        return None


def to_temp_wav(input_path) -> str:
    """
    Convert any FFmpeg-compatible audio file to a temporary WAV.
    Returns the temp file path — caller is responsible for deleting it.
    Raises RuntimeError on failure.
    """
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        result = subprocess.run([
            "ffmpeg", "-i", str(input_path),
            "-ar", "44100", "-ac", "2",
            "-y", tmp_path,
        ], capture_output=True, text=True, startupinfo=_startupinfo())
        if result.returncode != 0:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
        return tmp_path
    except FileNotFoundError:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise RuntimeError("FFmpeg not found in PATH.")
