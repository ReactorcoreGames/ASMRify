# Easy Audio ASMRifier & Hypnotiser — CLAUDE.md

## What This Program Does

Standalone Windows desktop app that batch-processes audio files (typically TTS voice clips) and transforms them into ASMR-style or hypnotic audio using automated effect chains. User picks input folder, selects presets across tabs, hits Start, gets processed files in the output folder. No audio knowledge required. Built for laypersons producing ASMR/hypnosis content in bulk.

**By Reactorcore** — https://reactorcore.itch.io/ | https://linktr.ee/reactorcore

---

## Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.11+ |
| GUI | ttkbootstrap with a fully custom registered theme ("asmrify") |
| Audio processing | FFmpeg via subprocess |
| Config | JSON (config.json, auto-created on first run) |
| Distribution | PyInstaller --onedir → ASMRifier.exe |

---

## Current State — Phase 4 complete (all phases done; exe build ready)

All processing phases are complete. Phase 4 (Polish & Release) is done:
- Error handling is layperson-friendly; corrupted/unreadable files are skipped with a clear message.
- `README.md`, `promo.md`, and `build_exe.bat` are present at the project root.
- `assets/icon.ico` is populated.
- `AUDIO_EXTENSIONS` is defined once in `core/batch.py` and imported where needed.

**Next action:** run `build_exe.bat` to produce `release\ASMRifier\`, zip it, upload to itch.io.

---

## Source Files

```
main.py                        — entry point
gui/
    app.py                     — main window, header, footer, notebook
    theme.py                   — PALETTE, font constants, _inject_asmrify_theme(), apply_theme()
    tabs/
        process.py             — Process tab + _make_scrollable_tab() helper
        main_preset.py         — Main Preset tab
        voice_pitch.py         — Voice & Pitch tab
        space_movement.py      — Space & Movement tab
        atmosphere.py          — Atmosphere tab
        tempo_intensity.py     — Tempo & Intensity tab
        binaural.py            — Binaural tab
        settings.py            — Settings tab
utils/
    config.py                  — load_config() / save_config()
    ffmpeg_check.py            — check_ffmpeg()
    audio_probe.py             — probe_audio() / to_temp_wav()
core/
    presets.py                 — numeric preset dicts for all main types and addons
    processor.py               — build_filter_chain() / process_file()
    batch.py                   — run_batch() / AUDIO_EXTENSIONS (canonical definition)
    noise_gen.py               — generate_noise()
    lfo.py                     — generate_pitch_wobble_wav() / generate_pan_envelope_wav()
    binaural.py                — generate_binaural_wav() / generate_binaural_filter()
assets/
    icon.ico                   — app icon (also present at project root for fallback)
```

---

## GUI Theme

Custom ttkbootstrap theme. Key facts:
- `_inject_asmrify_theme()` must be called before `ttk.Window()` — see `gui/app.py`
- All colors are in `PALETTE` in `gui/theme.py` — edit there, nowhere else
- Palette: deep violet-plum backgrounds, soft lavender accents, desaturated semantic colors
- Font: Georgia (serif) throughout; Consolas for the log/mono widget
- See `!standard python RC/ttkbootstrap_custom_theme.md` for the full pattern explanation

---

## Docs (in `docs/`)

| File | Contents |
|---|---|
| `build_phases.md` | Phase checklist — check this to see what's done and what's next |
| `gui_spec.md` | Full tab/control layout spec |
| `audio_effects.md` | Processing chain, preset FFmpeg values, binaural spec (Phase 2 reference) |
| `misc_notes.md` | FFmpeg, PyInstaller, release notes |

**To continue from where we left off:** read `CLAUDE.md` and `docs/build_phases.md`.
