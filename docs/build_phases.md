# Build Phases Checklist

Load this doc + INDEX.md every build session. Load audio_effects.md for Phase 2–3 work. Load gui_spec.md for Phase 1 and Phase 4 polish.

---

## Phase 1 — Scaffold & GUI Shell

**Goal**: App launches, all tabs are visible with correct controls, folder pickers work, settings persist.

- [x] Create project root folders: `gui/`, `core/`, `utils/`, `assets/`, `promo/`
- [x] `main.py` — entry point at project root, creates ttkbootstrap Window and launches app
- [x] `gui/app.py` — main application class; purple-themed ttkbootstrap window, maximized by default, minimum 900×650
- [x] All 8 tabs present in Notebook: Process, Main Preset, Voice & Pitch, Space & Movement, Atmosphere, Tempo & Intensity, Binaural, Settings
- [x] All controls present in each tab (radio buttons, labels, buttons) per gui_spec.md — non-functional but correctly laid out
- [x] Header (title + subtitle) and footer (Reactorcore + clickable link) present
- [x] `utils/config.py` — `load_config()`, `save_config()`, default values dict
- [x] `utils/ffmpeg_check.py` — `check_ffmpeg()` returns version string or None
- [x] FFmpeg missing warning on startup — status indicator in Settings tab + dialog or banner if not found
- [x] Folder picker buttons wired: select input folder, select output folder; paths shown in Entry fields and saved to config.json
- [x] "Open Program Folder" and "Open Output Folder" buttons functional
- [x] All tab selections saved to config.json on change and restored on next launch
- [x] `_apply_icon` pattern implemented (see gui_spec.md)
- [x] `_tk_ttk.LabelFrame` used everywhere (never `ttk.LabelFrame` with `padding=`)

**Done when**: App launches, tabs look correct, folder pickers work, changing any setting and restarting the app restores the previous selection.

---

## Phase 1.5 — GUI Cleanup (do before Phase 2)

**Goal**: Clean up the GUI layer before audio logic is added. No audio code touched.

- [x] **Split `gui/app.py` into per-tab files** — e.g. `gui/tabs/process.py`, `gui/tabs/main_preset.py`, etc.; `gui/app.py` becomes the orchestrator that imports and mounts each tab. Needs a full token-fresh session.
- [x] **Input folder file count label** — in the same session as the split: add a label below the Input Folder entry showing e.g. "12 audio files found (wav, mp3, flac)". Scans on folder select and on startup if path already saved.
- [x] **Theme complete overhaul** — own session. Create `gui/theme.py` with a single palette dict (all hex values in one place) and an `apply_theme(style)` function. Full visual redesign — current superhero base + purple clash to be scrapped entirely in favour of a cohesive palette with a colorful medium deep dreamy blue background with mysterious purple accents. Back-and-forth tweaking expected.

**Done when**: `gui/app.py` is a slim orchestrator, each tab lives in its own file, input folder shows a file count, and theme is a coherent single-palette design editable in one place.

---

## Phase 2 — Core Audio Chain

**Goal**: Basic ASMR processing works end-to-end. Start/Stop/Preview functional. First two main presets produce audibly different output.

- [x] `core/presets.py` — all preset parameter dicts for main types and addons (FFmpeg values from audio_effects.md)
- [x] `core/processor.py` — `build_filter_chain(settings) -> str` builds the FFmpeg `-af` string; `process_file(input_path, output_path, settings) -> (bool, error_str)` runs FFmpeg subprocess
- [x] Input normalization (Step 1) implemented: `dynaudnorm` pre-pass
- [x] Noise gate (Step 2): `agate` in chain
- [x] EQ/filtering (Step 3): `highpass`, `lowpass`, `equalizer` per main preset
- [x] Compression + limiting (Step 4): `acompressor`, `alimiter` per main preset
- [x] Ambience (Step 8): `aecho`, `chorus` per addon selection
- [x] Warmth/saturation (Step 10): `asoftclip` per addon selection
- [x] Final limiter + peak normalize (Step 12): `alimiter` + two-pass volumedetect/volume gain (pattern from `audio_generator.py` in reference folder)
- [x] `core/noise_gen.py` — `generate_noise(color, duration_sec, sample_rate, output_path)` uses FFmpeg `anoisesrc` to produce temp WAV; mixed at -50dB into chain
- [x] Background noise layer (Step 9) integrated into processor
- [x] `utils/audio_probe.py` — `probe_audio(path) -> dict` uses `ffprobe` to check if a file is a valid audio file and return its format/duration; `to_temp_wav(input_path) -> temp_path` converts any FFmpeg-compatible audio to a temp WAV (deleted by caller after use)
- [x] `core/batch.py` — `run_batch(input_folder, output_folder, settings, progress_callback, stop_event)` iterates all audio files in input folder (any FFmpeg-compatible format), auto-converts non-WAV to temp WAV before processing, deletes temp WAV after output is written
- [x] Output format: WAV, MP3, or both — driven by `output_format` config key; final export step re-encodes the processed WAV to MP3 via FFmpeg if needed
- [x] Output filenames: `originalname_asmr.wav` and/or `originalname_asmr.mp3`
- [x] Start button launches batch in thread; progress log updates in real time; file count and ETA shown
- [x] Stop button sets stop_event; processing aborts cleanly after current file finishes
- [x] Preview First File: processes first WAV alphabetically, opens result with `os.startfile()`
- [x] Tempo change (Step — `atempo`) integrated
- [x] Overall intensity multiplier applied to parameter values before building filter string

**Done when**: Soft-Spoken ASMR and Whispered ASMR presets produce clearly different output on a TTS WAV file. Stop aborts cleanly. Progress log updates during processing.

---

## Phase 3 — Advanced Effects

**Goal**: All 4 main presets and all addons work correctly. Binaural beats audible on headphones.

- [x] `core/lfo.py` — `generate_pitch_wobble_wav(deviation_hz, rate_hz, duration_sec, sample_rate, output_path)` and `generate_pan_envelope_wav(pan_type, cooldown_mode, duration_sec, sample_rate, audio_amplitude_array, output_path)` using numpy
- [x] Pitch wobble (Step 6) integrated: `vibrato` FFmpeg filter in build_filter_chain(); `generate_pitch_wobble_wav` available in lfo.py for sidechain use
- [x] Pitch wobble defaults wired per main preset (Relaxing Hypnosis = Subtle, Deep Mesmerization = Noticeable)
- [x] Voice pitch (Step 5): `rubberband=pitch=X` per addon selection (wired in Phase 2)
- [x] Panning — None/Center: slight stereo width only (`stereotools=mlev=0.015`)
- [x] Panning — Gentle L/R drift: numpy crossfade envelope, ±30%, smooth
- [x] Panning — Smooth rotational swirl: sine/cosine envelope, speed from cooldown selection
- [x] Panning — Dynamic swirl: amplitude analysis drives pan rate
- [x] All 4 panning cooldown modes implemented (Slow / Moderate / Quick / Intensity-based)
- [x] Randomization + tempo multiplier applied to cooldown timing
- [x] `core/binaural.py` — `generate_binaural_wav(preset, duration_sec, sample_rate, output_path)` for Alpha, Theta, Theta→Delta ramp, Gamma pulses
- [x] Binaural layer (Step 11) mixed into chain at correct volume per preset
- [x] Binaural defaults wired per main preset (Relaxing Hypnosis → Theta, Deep Mesmerization → Gamma pulses when binaural addon is not None)
- [x] Preset value labels wired in GUI: auto-update when main preset changes; visible only when `show_preset_values` is true

**Done when**: All 4 main presets produce distinctly different output. Panning movement is smooth with no jumps. Binaural is audible (as a very faint tone) on headphones. All addon combinations process without errors.

---

## Phase 4 — Polish & Release

**Goal**: Standalone exe ships clean on a fresh Windows machine with FFmpeg on PATH.

- [x] Error handling: skip corrupted/unreadable files with a log message; continue processing remaining files; report skipped files at end
- [x] Empty input folder: show informative message instead of silent failure
- [x] Non-audio files in input folder: silently ignored (ffprobe detects valid audio; anything else skipped)
- [x] All error messages use layperson-friendly language with actionable suggestions
- [x] `README.md` written at project root:
  - How to use the program (brief numbered steps)
  - FFmpeg requirement + installer link (https://reactorcore.itch.io/ffmpeg-to-path-installer)
  - What each tab does (one line each)
  - Binaural safety note (headphones required; not for epilepsy/pacemakers)
- [x] `CLAUDE.md` written at project root — session context doc (current status, key decisions, what to load) (full rewrite)
- [x] `promo.md` filled out at project root — title, subtitle, description, itch.io tags
- [x] `promo/` folder populated with screenshots — **manual step: capture screenshots and place in promo/**
- [x] `assets/icon.ico` present
- [x] `build_exe.bat` at project root:
  ```bat
  pyinstaller --onedir --windowed ^
    --icon "assets\icon.ico" ^
    --add-data "assets\icon.ico;." ^
    --name "ASMRifier" ^
    main.py
  ```
  Outputs to `release\ASMRifier\`. Copies README.md, promo.md, and promo/ folder into release folder. Cleans build/ and dist/ after.
- [x] Verify compiled exe launches without console window — **manual: run build_exe.bat then launch exe**
- [x] Verify config.json persists between runs when exe is used — **manual**
- [x] Verify `rubberband` filter works (test pitch shift on an audio file via the exe) — **manual**
- [x] Verify binaural generation works in compiled exe (numpy bundled correctly) — **manual**
- [x] Verify the .ico works in windows 11 taskbar, window titlebar of the compiled exe — **manual**


**Done when**: `ASMRifier.exe` runs standalone, processes files correctly with all effects, config persists, no console window appears, `release\ASMRifier\` is ready to zip and upload.
