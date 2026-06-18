import shutil
import subprocess
import sys


def _startupinfo():
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None


def check_ffmpeg():
    """Return version string if FFmpeg is on PATH, else None."""
    if not shutil.which("ffmpeg"):
        return None
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            startupinfo=_startupinfo(),
            timeout=10,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        # Extract version e.g. "ffmpeg version 6.0 ..."
        parts = first_line.split()
        if len(parts) >= 3:
            return parts[2]
        return first_line or "found"
    except Exception:
        return None
