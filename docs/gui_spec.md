# GUI Specification

## Window

- Framework: ttkbootstrap
- Base theme: `superhero`
- Default state: maximized on launch (`root.state("zoomed")`)
- Minimum size: 900×650
- Resizable: yes
- Title bar: "Easy Audio ASMRifier & Hypnotiser"

## Purple Theme

Override the superhero theme's accent colors post-init using `ttkbootstrap.Style`:
- Primary accent: purple/violet (`#7B2FBE` or similar)
- Keep semantic bootstyle conventions: `success`=green (Start), `danger`=red (Stop), `info`=blue (Preview), `secondary`=grey (utility buttons)
- Override only the primary/accent color; leave semantic colors intact so button intent remains visually clear

## Required Patterns (from utility docs)

- **Icon**: apply `_apply_icon(window)` to main window and all Toplevels. Icon lives at `assets/icon.ico` in the source tree; the multi-path search in the pattern covers script, frozen exe, and CWD. Call after `geometry()`/`title()`, before `mainloop()`.
- **LabelFrame**: use `_tk_ttk.LabelFrame` (stdlib ttk) everywhere, never `ttk.LabelFrame`. Add `from tkinter import ttk as _tk_ttk` after `import ttkbootstrap as ttk`.
- **Entry context menu**: attach Cut/Copy/Paste/Select All right-click menu to every Entry the user types into.
- **No drag-and-drop**: use button-based file/folder selection only (`filedialog.askdirectory()`).

---

## Layout Structure

### Header (always visible, above tabs)

```
┌─────────────────────────────────────────────────────────────┐
│  Easy Audio ASMRifier & Hypnotiser          [large, bold]   │
│  Transform your voice clips into ASMR or hypnotic audio     │
├─────────────────────────────────────────────────────────────┤
│  [Tab: Process] [Tab: Main Preset] [Tab: Voice & Pitch] ... │
```

- Title: font `("Arial", 18, "bold")`
- Subtitle: font `("Arial", 10)`, muted color

### Footer (always visible, below tabs)

```
│  Made by Reactorcore   https://linktr.ee/reactorcore (clickable) │
```

- Font: `("Arial", 8)`
- Link opens in browser via `webbrowser.open()`

---

## Tabs

### Tab 1 — Process

The primary operational tab. User always starts here.

**Input folder section** (`_tk_ttk.LabelFrame`, label "Input Folder"):
- Entry field (read-only display of selected path, expands horizontally)
- Button: "Select Input Folder" (primary style)
- Tooltip on button: "Choose the folder containing your .wav files to process"

**Output folder section** (`_tk_ttk.LabelFrame`, label "Output Folder"):
- Entry field (read-only display of selected path, expands horizontally)
- Button: "Select Output Folder" (primary style)
- Button: "Open Output Folder" (secondary style) — opens folder in Windows Explorer via `os.startfile()`
- Tooltip on "Open Output Folder": "Open the output folder in File Explorer to access your processed files"

**Action buttons** (large, row layout):
- "Start" (success/green, width=20) — begins batch processing all WAVs in input folder
- "Stop" (danger/red, width=20) — aborts current batch; disabled until processing starts
- "Preview First File" (info/blue, width=22) — processes first WAV alphabetically and opens in default audio player
- Tooltip on Preview: "Processes only the first file in your input folder so you can hear the result before running the full batch"

**Progress area** (`_tk_ttk.LabelFrame`, label "Progress"):
- Scrollable text log (read-only) — shows per-file status messages as processing runs
- Status line below log: "File 3 of 12 — Estimated time remaining: 1m 24s"
- Progress bar (ttkbootstrap `Progressbar`, striped, animated while running)

### Tab 2 — Main Preset

The most important tab. Sets the baseline character for all processing.

**Section**: 4 large radio buttons, each in its own visual block with a title, description, and optional value label.

```
(●) Soft-Spoken ASMR
    Gentle, natural processing. Keeps the voice feeling real and close.
    [Value label: highpass f=80, ratio=3:1, +2dB@6kHz]  ← only shown if setting enabled

( ) Whispered ASMR
    Crisp highs, tight dynamics. That classic tingly ASMR quality.
    [Value label: highpass f=100, ratio=4:1, +8dB@8kHz]

( ) Relaxing Hypnosis
    Dreamy, smooth, softly warped. Makes the listener feel calm and spacious.
    [Value label: lowpass f=12kHz, ratio=3.5:1, echo tails]

( ) Deep Mesmerization
    Heavy, pervasive, captivating. Designed to hold attention completely.
    [Value label: lowpass f=10kHz, ratio=5:1, heavy echo, binaural on]
```

- Tooltip on each: plain-English description of intended listener experience
- Value labels: auto-update when preset changes; hidden unless `show_preset_values` is enabled in Settings

### Tab 3 — Voice & Pitch

Two sections side by side or stacked, each in a LabelFrame.

**Voice Pitch** (`_tk_ttk.LabelFrame`, label "Voice Pitch"):
- Tooltip on section: "Changes how deep or high the voice sounds. Duration stays the same — audio length is unaffected."
- Radio buttons:
  - Original (no change)
  - Slightly deeper
  - Much deeper
  - Slightly higher

**Pitch Wobble** (`_tk_ttk.LabelFrame`, label "Pitch Wobble"):
- Tooltip on section: "Adds a slow, gentle wavering to the pitch. Creates a dreamy, hypnotic quality."
- Radio buttons:
  - None
  - Subtle
  - Noticeable
- Small note label below: "Relaxing Hypnosis and Deep Mesmerization enable Subtle wobble by default."

### Tab 4 — Space & Movement

**Spatial Movement — Type** (`_tk_ttk.LabelFrame`, label "Spatial Movement"):
- Tooltip on section: "Controls how the voice moves between left and right. Use headphones for best effect."
- Radio buttons:
  - None / Center — "Voice stays centered. A little stereo width is still added."
  - Gentle L/R drift — "Voice slowly drifts left and right at relaxed intervals."
  - Smooth rotational swirl — "Voice continuously rotates in a smooth circular motion."
  - Dynamic swirl — "Movement speed follows the energy of the audio. Active sections move more."

**Spatial Movement — Transition Speed** (`_tk_ttk.LabelFrame`, label "Transition Speed"):
- Tooltip on section: "Controls how often the voice changes position. Only active when a movement type above is selected."
- Radio buttons:
  - Slow transitions (45–90s) — "Very gradual. Position shifts are rare and barely noticeable."
  - Moderate (15–45s) — "Comfortable pacing for most ASMR content."
  - Quick changes (3–15s) — "More frequent movement. Better for energetic content."
  - Intensity-based (auto) — "Movement frequency is automatically driven by how loud/active the audio is."
- Note label: "Transitions are always smooth — no sudden jumps."

### Tab 5 — Atmosphere

Three sections stacked.

**Background Noise** (`_tk_ttk.LabelFrame`, label "Background Noise"):
- Tooltip: "Adds a soft noise layer beneath the voice. Helps mask TTS artifacts and adds warmth. Kept very quiet so it doesn't overpower the voice."
- Radio buttons: None / White noise / Pink noise / Brown noise / Green noise / Gray noise
- Tooltip per option:
  - White: "Neutral hiss across all frequencies."
  - Pink: "Warmer, more natural — like a gentle waterfall."
  - Brown: "Deep, low rumble — very calming."
  - Green: "Mid-range focus, like distant outdoors ambience."
  - Gray: "Perceptually balanced — sounds equally loud across all frequencies."
- Slider "Noise Volume" (range -15 to +15, default 0) with live value label. Tooltip: "Shifts the background noise louder (right) or quieter (left) relative to the default level. 0 is the recommended starting point."
- Radio buttons "Pulse / Wave": None / Slow swell / Breathing waves
  - None: "Noise stays at a steady, constant level."
  - Slow swell: "Noise gently rises and falls in volume over time, like slow waves."
  - Breathing waves: "A more noticeable rise and fall, like the noise is breathing."

**Ambience** (`_tk_ttk.LabelFrame`, label "Ambience"):
- Tooltip: "Adds room or space effects to make the voice feel like it exists in an environment."
- Radio buttons:
  - Dry — "No room effect. Voice is close and direct."
  - Subtle room reverb — "Small room feel. Adds natural space without being obvious."
  - Dreamy space — "Larger, softer reverb. Floaty and immersive."
  - Ethereal — "Wide, lush reverb with chorus. Very spacious and otherworldly."

**Warmth / Saturation** (`_tk_ttk.LabelFrame`, label "Warmth"):
- Tooltip: "Adds a subtle analog warmth. Makes TTS voices feel less digital and more natural."
- Radio buttons:
  - Clean — "No saturation. Keeps the original character."
  - Light saturation — "A touch of warmth. Barely noticeable but smooths harshness."
  - Warm saturation — "Noticeably warmer. Good for voices that sound thin or tinny."

### Tab 6 — Tempo & Intensity

**Tempo Change** (`_tk_ttk.LabelFrame`, label "Tempo Change"):
- Tooltip: "Speeds up or slows down the audio without changing the pitch. Good for adjusting pacing."
- Radio buttons: None / Faster lightly / Faster heavily / Slower lightly / Slower heavily

**Overall Intensity** (`_tk_ttk.LabelFrame`, label "Overall Effect Intensity"):
- Tooltip: "Scales all effects up or down globally. Use this to dial in the overall strength of everything at once."
- Radio buttons:
  - No change
  - Boost lightly — "All effects are 20% stronger."
  - Boost heavily — "All effects are 50% stronger. Can get intense."
  - Reduce lightly — "All effects are 20% softer. More natural result."
  - Reduce heavily — "All effects are 40% softer. Very subtle processing."

### Tab 7 — Binaural

**Binaural Beats** (`_tk_ttk.LabelFrame`, label "Binaural Beats"):
- Section header note (small label): "Requires headphones. Has no effect through speakers. Optional feature — leave on None if unsure."
- Radio buttons:
  - None — "No binaural layer added."
  - Alpha — relaxed focus. "A gentle 10Hz layer. Promotes calm, clear-headed relaxation. Good for soft ASMR."
  - Theta — deep trance. "A 6Hz layer associated with deep meditation and trance states. Pairs well with hypnotic modes."
  - Theta→Delta ramp — sleep. "Starts at light relaxation and gradually ramps down toward deep sleep frequencies over the course of the audio."
  - Gamma pulses — captivating. "40Hz pulses. Associated with intense focus and heightened engagement. Good for Deep Mesmerization mode."
- Note label below: "Relaxing Hypnosis defaults to Theta. Deep Mesmerization defaults to Gamma pulses."
- Safety note (small italic label at bottom of section): "Not recommended for people with epilepsy or pacemakers."

### Tab 8 — Settings

**Output Format** (`_tk_ttk.LabelFrame`, label "Output Format"):
- Tooltip on section: "Choose what file format(s) your processed audio will be saved as."
- Radio buttons:
  - WAV only — "Lossless quality. Larger file size. Best if you plan to edit or chain the files further."
  - MP3 only — "Compressed. Smaller file size. Good for final listening or sharing."
  - Both WAV and MP3 — "Saves two copies of each processed file. Takes more space but gives you both options."
- Note label: "Input files can be any format FFmpeg supports (mp3, wav, flac, ogg, m4a, etc.). They are auto-converted internally — no manual prep needed."

**Display** (`_tk_ttk.LabelFrame`, label "Display"):
- Checkbutton: "Show preset values next to each option" — toggles `show_preset_values` in config.json. Tooltip: "When enabled, each preset shows the technical audio parameters it uses, like filter frequencies and compression ratios."

**FFmpeg** (`_tk_ttk.LabelFrame`, label "FFmpeg Status"):
- Status label: "FFmpeg found: version X.X.X" (success color) or "FFmpeg not found — please install it" (danger color)
- Button: "How to install FFmpeg" — opens https://reactorcore.itch.io/ffmpeg-to-path-installer in browser

**Program** (`_tk_ttk.LabelFrame`, label "Program"):
- Button: "Open Program Folder" (secondary) — opens the folder containing ASMRifier.exe in Explorer

---

## Config Keys (config.json)

```json
{
  "input_folder": "",
  "output_folder": "",
  "main_preset": "soft_spoken_asmr",
  "voice_pitch": "original",
  "pitch_wobble": "none",
  "panning_type": "none",
  "panning_cooldown": "moderate",
  "background_noise": "none",
  "ambience": "dry",
  "warmth": "clean",
  "tempo": "none",
  "intensity": "no_change",
  "binaural": "none",
  "output_format": "wav",
  "show_preset_values": false
}
```

All values are saved on every change (not just on exit). Loaded on program start. If config.json is missing or malformed, defaults above are used and file is rewritten.

---

## ttkbootstrap Pitfalls (from utility docs)

1. **LabelFrame padding crash**: `ttk.LabelFrame(padding=X)` crashes on ttkbootstrap >=1.20.2. Always use `_tk_ttk.LabelFrame(padding=X)` instead. `ttk.Frame` is not affected.
2. **grab_set() softlock**: avoid `grab_set()` on Toplevels unless critical. Use `window.transient(parent)` + `window.focus_force()` instead. If `grab_set()` is needed, always add `window.protocol("WM_DELETE_WINDOW", on_close)` with `grab_release()` in handler.
3. **Don't mix grid and pack** in the same parent container.
4. **Always specify sticky** in grid layouts (`"nsew"`, `"ew"`, `"w"`, etc.).
5. **Configure row/column weights** before placing widgets for correct resize behavior.
