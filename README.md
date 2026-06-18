# Easy Audio ASMRifier & Hypnotiser

<img width="1264" height="848" alt="asmr promo" src="https://github.com/user-attachments/assets/33e855fc-9322-4b42-894c-7d102ae4fa1d" />

Transform your TTS voice clips into ASMR or hypnotic audio in bulk — no audio knowledge required.

**By Reactorcore** — https://reactorcore.itch.io/

---

<img width="1920" height="1020" alt="ASMRifier Screenshot (1)" src="https://github.com/user-attachments/assets/99b4067b-ecd0-4af8-b1b2-fc8cee1c6dc6" />
<img width="1920" height="1020" alt="ASMRifier Screenshot (2)" src="https://github.com/user-attachments/assets/dab8c6f9-51cb-4165-b417-93a1e70762cb" />
<img width="1920" height="1020" alt="ASMRifier Screenshot (4)" src="https://github.com/user-attachments/assets/2a9bb831-62fb-4f92-94c9-c6900444bd64" />

## How to Use

1. **Install FFmpeg** and make sure it is on your system PATH.
   Easy installer: https://reactorcore.itch.io/ffmpeg-to-path-installer
2. **Run `ASMRifier.exe`**.
3. In the **Process** tab, select your **Input Folder** (folder containing your voice clips) and your **Output Folder** (where processed files will be saved).
4. Choose your settings across the other tabs (or leave the defaults — they work great out of the box).
5. Click **Start**. Processed files appear in the output folder as they complete.

Use **Preview First File** to process just the first clip and hear the result before running the full batch.

---

## Tabs

| Tab | What it does |
|---|---|
| **Process** | Select folders, start/stop/preview the batch, watch the progress log |
| **Main Preset** | Choose the overall sound style: Soft-Spoken ASMR, Whispered ASMR, Relaxing Hypnosis, or Deep Mesmerization |
| **Voice & Pitch** | Adjust pitch shifting and pitch wobble (LFO) depth |
| **Space & Movement** | Control stereo panning style and movement speed |
| **Atmosphere** | Add echo, reverb, chorus, background noise, and noise pulsing |
| **Tempo & Intensity** | Speed up or slow down the audio; adjust the overall effect intensity |
| **Binaural** | Add binaural beats (Alpha, Theta, Gamma) mixed into the output |
| **Settings** | Output format (WAV/MP3/both), normalization mode, FFmpeg status |

---

## Requirements

- Windows 10 or 11
- **FFmpeg** installed and on PATH — https://reactorcore.itch.io/ffmpeg-to-path-installer
- Headphones recommended for listening to spacial effects, binaural beats and to hear the smaller cool details in the enhanced audio

---

## Safety Note — Binaural Beats

The Binaural tab generates low-frequency audio tones mixed into the output. **Headphones are required** for binaural beats to work as intended.

**Do not use binaural beats if you have epilepsy, a pacemaker, or other conditions sensitive to rhythmic audio stimulation.** If you experience discomfort, stop immediately.

---

## Output Files

Processed files are saved to your chosen output folder with a suffix indicating the preset and normalization mode used (e.g. `myfile-softs-pk_norm.wav`). The original files are never modified.
