# Miscellaneous Notes

## FFmpeg Build Requirement

The program requires the **full** FFmpeg build from gyan.dev (not the "essentials" build). Required filters included in the full build:
- `rubberband` — duration-preserving pitch shift and tempo change
- `loudnorm` / `dynaudnorm` — input normalization
- `agate` — noise gate
- `asoftclip` — saturation

**Installer**: https://reactorcore.itch.io/ffmpeg-to-path-installer installs the correct build automatically.

The program checks for FFmpeg on startup via `shutil.which("ffmpeg")` and shows a warning if not found. It does not attempt to install FFmpeg itself.

---

## PyInstaller Notes

Use `--onedir` (not `--onefile`):
- Faster startup (no extraction step)
- Easier to debug distribution issues
- Users see the exe alongside its support folder, which is fine for a desktop tool

**Build command**:
```bat
pyinstaller --onedir --windowed --icon "icon.ico" --add-data "icon.ico;." --name "ASMRifier" main.py
```

`--windowed` suppresses the console window (important for a GUI app).

**numpy**: will be auto-detected and bundled by PyInstaller. No special flags needed. Adds ~20MB to the bundle — acceptable.

**ttkbootstrap**: may require `--hidden-import ttkbootstrap` if auto-detection misses it.

**icon.ico**: must be included both as the exe icon (`--icon`) and as bundled data (`--add-data`) so the `_apply_icon` runtime loader can find it inside the frozen exe.

---

## numpy Usage

numpy is used only for LFO and panning envelope generation — small float32 arrays at audio sample rate. No ML models, no large data. Typical array size: a few MB for a 10-minute audio file at 44100Hz.

If bundle size ever becomes a concern, `scipy` should be avoided (large) — stick to numpy only.

---

## itch.io Release Plan

- **This program** (desktop exe): paid release on itch.io
- **Future web version**: one-file-at-a-time, browser-based, free. Separate project — not part of this codebase.
- itch.io description should mention the FFmpeg installer and link to it
- Quickstart.txt doubles as the basic usage guide; keep it short (under 1 page)

---

## Purple Theme Implementation

ttkbootstrap does not have a built-in purple theme. Approach:

```python
import ttkbootstrap as ttk

root = ttk.Window(themename="superhero")
style = ttk.Style()

# Override primary accent color to purple after theme loads
style.configure("TButton", ...)
style.map("primary.TButton", background=[("active", "#6A1FA8"), ("!active", "#7B2FBE")])
# etc.
```

Keep semantic bootstyle conventions intact:
- `bootstyle="success"` → green (Start button)
- `bootstyle="danger"` → red (Stop button)  
- `bootstyle="info"` → blue (Preview button)
- `bootstyle="secondary"` → muted (utility buttons)
- `bootstyle="primary"` → purple (folder pickers, main actions)

Only override `primary` to purple; leave the semantic colors as-is so button intent stays visually clear.

---

## FFmpeg Pre-Roll Click Bug (fixed 2026-06-17)

Two FFmpeg filters emit exactly `-1.0` in 1–4 samples before their first real audio frame — `amerge` (stream sync race) and `vibrato` (delay buffer init). Both are fixed with the same pattern: `atrim=start_sample=10,asetpts=PTS-STARTPTS` immediately after the offending filter.

**filter_complex output** (`core/processor.py`): `atrim=start_sample=10,asetpts=PTS-STARTPTS` is appended to the final label of every filter_complex before `-map`, trimming 0.23ms off the start.

**Wobble pass** (`core/processor.py`): the vibrato filter string is:
```
vibrato=f=X:d=Y,atrim=start_sample=10,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.4
```
`asetpts` must come before `afade` — otherwise afade's `st=0` reference is wrong and the corruption survives.

Diagnostic scripts in project root: `diag_full_chain.py` (regression test), `diag_stages.py` (stage-by-stage isolation), `diag_pan_click.py` (pan-only).

---

## Audio Reference Code

`code from another audio program, maybe useful, maybe not/audio_merger.py` and `audio_generator.py` contain proven patterns for:
- FFmpeg subprocess calls with `_get_subprocess_startupinfo()` (hides console on Windows)
- Two-pass peak normalization (volumedetect → volume gain)
- FFmpeg filter_complex for mixing multiple audio streams
- Temp file handling pattern (mkstemp → process → os.replace)
- FFmpeg not found error message pointing to the itch.io installer

These patterns should be reused directly in `src/core/processor.py` and `src/core/batch.py`.
