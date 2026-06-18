# Easy Audio ASMRifier & Hypnotiser — Project Index

## What This Program Does

A standalone Windows desktop app that batch-processes audio files — typically TTS voice clips — and transforms them into ASMR-style or hypnotic audio using automated audio effect chains. The user picks their input folder, selects presets across several tabs, hits Start, and gets processed audio files in their output folder. No technical audio knowledge required. Built for laypersons who want to produce ASMR or hypnosis content from voice recordings quickly and in bulk.

**By Reactorcore** — https://reactorcore.itch.io/ | https://linktr.ee/reactorcore

---

## Tech Stack

| Component | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| GUI | ttkbootstrap (superhero base, purple theme override) | |
| Audio processing | FFmpeg via subprocess | All effects: EQ, compression, pitch, reverb, panning, noise, binaural |
| LFO / panning envelopes | numpy (float32 arrays → temp WAV) | Only non-stdlib dep beyond FFmpeg |
| Config persistence | JSON (config.json) | Auto-created on first run |
| Distribution | PyInstaller --onedir → ASMRifier.exe | |

---

## FFmpeg Dependency

FFmpeg must be installed and on the system PATH. The program checks for FFmpeg on startup and shows a warning if it is missing.

**Install FFmpeg:** https://reactorcore.itch.io/ffmpeg-to-path-installer (installs the correct full gyan.dev build which includes rubberband, loudnorm, and agate filters)

---

## Compiled Program Folder Structure

```
ASMRifier/
├── ASMRifier.exe
├── icon.ico
├── Quickstart.txt
└── config.json          (auto-created on first run)
```

- **Input/output**: user selects folders via folder picker dialogs; paths saved to config.json
- **Supported input formats**: any FFmpeg-compatible audio file (mp3, wav, flac, ogg, m4a, aac, etc.). Non-WAV files are auto-converted to a temp WAV internally before processing; the temp file is deleted silently after the output is written.
- **Output format**: user chooses in Settings — WAV, MP3, or both
- **Output filename**: `originalname_asmr.wav` and/or `originalname_asmr.mp3`
- **Preview**: "Preview First File" button processes only the first audio file in the input folder (alphabetically) and opens it in the default audio player

---

## Source Code Structure

```
ASMRify/                    ← project root (git repo root)
├── main.py                 ← entry point
├── gui/
│   └── app.py
├── core/
│   ├── processor.py
│   ├── presets.py
│   ├── batch.py
│   ├── noise_gen.py
│   ├── lfo.py
│   └── binaural.py
├── utils/
│   ├── config.py
│   ├── ffmpeg_check.py
│   └── audio_probe.py
├── assets/
│   └── icon.ico
├── promo/                  ← screenshots
├── docs/                   ← these design docs
├── build_exe.bat
├── README.md
├── CLAUDE.md
└── promo.md
```

No `src/` wrapper — `main.py` sits at project root, subfolders are the module names. All imports use relative notation (`.` prefix).

---

## Design Docs — What to Load Per Build Session

| Doc | Contents | Load for |
|---|---|---|
| `INDEX.md` (this file) | Overview, tech stack, structure | Every session |
| `audio_effects.md` | Full processing chain, all preset FFmpeg values, binaural spec | Phase 2, 3 |
| `gui_spec.md` | Tab layout, every control, tooltips, purple theme, config keys | Phase 1, polish |
| `build_phases.md` | Phase checklist (1–4) with done criteria | Every session |
| `misc_notes.md` | FFmpeg notes, PyInstaller notes, itch.io release info | Phase 4, release |

**Typical session prompt:**
> "Load INDEX.md, build_phases.md, and audio_effects.md. Check the phase checklist and continue from where we left off."
