# Easy Audio ASMRifier & Hypnotiser — User Guide

## The Most Important Thing to Know

This program applies audio effects to existing recordings. It cannot change the fundamental character of a voice. If your source audio is loud, energetic, or spoken at full volume, the processed output will still be loud and energetic — just with effects layered on top.

**For ASMR results, your recordings should already be soft.** Record whispers as whispers, gentle speech as gentle speech. The program enhances and deepens that quality; it doesn't create it.

However, you can apply a lot of cool effects; like ear-to-ear movement that you may have seen/heard some ASMRtists do where they have two microphones or a 3Dio Binaural Microphone and they move from one side to another, where you only hear their voice in one ear up close that feels amazingly tingly and intimate.

You *can* do that awesome thing plus many other neat audio effect things using any flat audio that was recorded from a single microphone or even text-to-speech audios!

---

## How the Tabs Work Together

Everything in the program builds on the **Main Preset** you choose. Think of it as the foundation — it sets the overall tone, EQ character, and base dynamics. Every other tab adds on top of that foundation.

### Main Preset
Sets the overall sound character. Four options:
- **Soft-Spoken ASMR** — natural, close, intimate. Good all-rounder for gentle voice content.
- **Whispered ASMR** — crisp highs, tight dynamics. The classic ASMR sound. Needs actual whisper recordings to shine.
- **Relaxing Hypnosis** — warm, dreamy, slightly warped. Echo tails and subtle pitch movement included.
- **Deep Mesmerization** — heavy, immersive, commanding. Maximum depth and echo. Best for long-form induction scripts.

### Voice & Pitch
Fine-tune the voice tone and add pitch movement:
- **Voice Pitch** — shift the voice up or down in semitones.
- **Pitch Wobble (LFO)** — adds a slow, gentle wobble to the pitch over time. Makes the voice feel floaty or hypnotic.

### Space & Movement
Controls where the voice sits in the stereo field and how it moves:
- **Spatial Movement** — from centered, to slow drift, to full ear-to-ear switching.
- **Transition Speed** — how often the voice changes position.
- **Crossfade Speed** — how smooth or snappy the transitions are.
- **Position Bias** — when using Ear-to-ear + Front, control how long the voice lingers at each position.

Use headphones. These effects are designed for headphone listening.

**How Ear-to-ear + Front picks its order.** It doesn't ping-pong left-center-right-center-left, and it doesn't pick a fresh random spot every time either (which could land on the same side twice in a row). Instead it shuffles the three positions, visits each one once in that shuffled order, then reshuffles for the next round. So you'll always hear all three positions before any repeat, but the order itself stays unpredictable.

**Position Bias and dwell time.** Bias controls how long the voice *lingers* at each stop, not how often it visits — all three positions still get picked equally often via the shuffle above. With **Custom** bias, the three sliders are normalized against each other (so 9/1/1 behaves the same as 90/10/10), and the result multiplies the dwell time at each position. As a rough guide, an extreme tilt like 9/1/1 can stretch the favored side's dwell to roughly 5–10x longer than the other two at Slow/Moderate transition speeds, while the de-emphasized positions can become quite brief — occasionally under a second on Quick speed. If a position feels like it's barely registering, pull that ratio back closer to even.

### Atmosphere
Adds background layers beneath the voice:
- **Background Noise** — white/pink/brown noise, or silence.
- **Ambience** — environmental textures (rain, fire, nature, etc.).
- **Warmth** — low-end body added to the overall mix.

### Tempo & Intensity
Adjusts the pacing and energy of the processing:
- **Tempo** — affects the speed of time-based effects like echo decay and LFO rate.
- **Intensity** — scales the overall depth of the effect chain. Higher intensity = more pronounced everything.

### Binaural Beats
Adds a subtle tone split between left and right ears to create a binaural beat frequency. The brain perceives the difference between the two tones as a low pulse. Associated with relaxation and focus depending on the frequency:
- **Delta (0.5–4 Hz)** — deep sleep, unconscious processing.
- **Theta (4–8 Hz)** — drowsiness, deep relaxation, hypnagogic states.
- **Alpha (8–14 Hz)** — calm alertness, light relaxation.
- **Beta (14–30 Hz)** — active thinking, focus.

Binaural beats require headphones to work. They are very subtle — they are not something you consciously hear as a beat.

---

## Tips for Best Results

- **Start with the preset, then layer.** Don't reach for sliders first. Pick the preset that matches your intended vibe, then add effects one tab at a time.
- **Less is more with pitch wobble and echo.** A small amount goes a long way. Heavy wobble can sound seasick; heavy echo can wash out intelligibility.
- **Preview before batch processing.** Use the Preview button in the Process tab to hear one file before committing the whole folder.
- **WAV in, WAV out for editing chains.** If you plan to do further processing after this program, save to WAV. Use MP3 only for final delivery.
- **Binaural + ear-to-ear is a powerful combination.** Spatial movement carries the binaural effect around the head, which amplifies the immersion.

---

## Settings

- **Output Format** — WAV (lossless), MP3 (compressed), or both.
- **Normalization** — Peak (loudest moment hits -1 dB) or Loudness (-16 LUFS, better for streaming consistency).
- **Reset to defaults** — delete `config.json` from the program folder and restart. All settings return to their original values.
