# Audio Effects Specification

## Processing Chain Order

Each file is processed through the following stages in order. All processing is done via FFmpeg subprocess. Steps marked (LFO) require a numpy-generated temp WAV sidechain (see LFO Note below).

| Step | Stage | FFmpeg mechanism |
|---|---|---|
| 1 | Input normalization | `loudnorm` or `dynaudnorm` |
| 2 | Noise gate | `agate` |
| 3 | EQ / filtering | `highpass`, `lowpass`, `equalizer` |
| 4 | Compression + soft limiting | `acompressor`, `alimiter` |
| 5 | Pitch shift (duration-preserving) | `rubberband=pitch=X` |
| 6 | Pitch wobble (LFO) | numpy sidechain → `amix` |
| 7 | Spatial panning / swirl (LFO) | numpy panning envelope → `pan` sidechain |
| 8 | Ambience (reverb / delay / chorus) | `aecho`, `chorus` |
| 9 | Background noise layer | `anoisesrc` mixed at -50dB |
| 10 | Warmth / saturation | `asoftclip` |
| 11 | Binaural beats layer | two `sine` sources via `filter_complex` |
| 12 | Final limiter + peak normalize | `alimiter`, volumedetect + volume gain |

### LFO Note (Steps 6 & 7)

FFmpeg static `-af` filter chains cannot vary parameters over time. For pitch wobble and smooth panning swirl, the approach is:
1. Use numpy to generate a float32 array representing the time-varying modulation envelope at the audio sample rate
2. Write it to a temp WAV file
3. Feed it as a sidechain input to FFmpeg `amix` (wobble) or use it as the pan position signal
4. Delete the temp WAV after processing

numpy is the only non-stdlib Python dependency beyond FFmpeg. Only small float32 arrays are generated — no ML models.

---

## Main Type Presets

These set the baseline character of the processing. All addons are applied on top of whichever main preset is selected.

### (1) Soft-Spoken ASMR
Natural, gentle processing. Preserves the original voice character.
```
highpass=f=80
equalizer=f=6000:width_type=o:width=2:g=2
acompressor=threshold=-18dB:ratio=3:attack=10:release=100:makeup=2
alimiter=level=1:attack=5:release=50
```

### (2) Whispered ASMR
Crisp highs, tight dynamics, intimate feeling. The high-shelf boost is the defining characteristic.
```
highpass=f=100
equalizer=f=8000:width_type=h:width=4000:g=8
acompressor=threshold=-20dB:ratio=4:attack=5:release=80:makeup=3
alimiter=level=1:attack=3:release=40
```

### (3) Relaxing Hypnosis
Dreamy, smooth, slightly spacious. Designed to feel calming and immersive. Echo tail length and decay scale with intensity (see Overall Intensity below).
```
highpass=f=60
lowpass=f=12000
acompressor=threshold=-16dB:ratio=3.5:attack=15:release=150:makeup=2   ← no_change values
aecho=0.8:0.88:120:0.4   ← no_change values
```

### (4) Deep Mesmerization
Heavy processing, psychoacoustic character. Designed to feel pervasive and captivating. Both echo taps scale with intensity.
```
highpass=f=60
lowpass=f=10000
acompressor=threshold=-14dB:ratio=5:attack=8:release=120:makeup=4   ← no_change values
aecho=0.8:0.88:200:0.5,aecho=0.8:0.88:400:0.3   ← no_change values
```

---

## Addons

### Voice Pitch
Duration-preserving pitch shift via rubberband. Does not change audio length.

| Option | FFmpeg filter |
|---|---|
| Original (no change) | *(skip step)* |
| Slightly deeper | `rubberband=pitch=0.87` |
| Much deeper | `rubberband=pitch=0.75` |
| Slightly higher | `rubberband=pitch=1.12` |

Requires rubberband filter in FFmpeg build (included in gyan.dev full build).

### Pitch Wobble
LFO-based slow modulation of pitch. Creates a dreamy, slightly unstable quality. Primarily for hypnotic modes but can be applied to any.

| Option | LFO parameters |
|---|---|
| None | *(skip step)* |
| Subtle | ±5Hz deviation, 0.1Hz rate |
| Noticeable | ±10Hz deviation, 0.2Hz rate |

Implementation: numpy generates a sine-wave modulation envelope at audio sample rate. Envelope is written to temp WAV and mixed as sidechain.

### Spatial Panning — Type
Controls how the voice moves in the stereo field. All transitions must be smooth — no sudden jumps.

| Option | Behavior |
|---|---|
| None / Center | Mono-like center; slight stereo width only |
| Gentle L/R drift | Smooth crossfade between ±30% L and R at random intervals within cooldown constraints |
| Smooth rotational swirl | Continuous circular panning via sine/cosine envelope. Speed set by cooldown selection. |
| Dynamic swirl | Pan rate driven by audio amplitude. Loud sections move faster; quiet sections barely move. |

All panning uses a numpy-generated envelope written to a temp WAV sidechain. Panning interpolates smoothly over time.

### Spatial Panning — Cooldown
Controls how frequently panning position changes occur. Only applies when Panning Type is not None/Center.

| Option | Min/max interval | Notes |
|---|---|---|
| Slow transitions | 45–90s | + random factor (×0.5 to ×2.0) + tempo multiplier |
| Moderate | 15–45s | + random factor + tempo multiplier |
| Quick changes | 3–15s | + random factor + tempo multiplier |
| Intensity-based | Min 2s cooldown | Maps audio amplitude to pan rate; high energy = shorter cooldown |

Tempo multiplier: faster-tempo audio shortens the cooldown baseline; slower-tempo lengthens it. Average tempo = no change.
Random factor: applied as a multiplier drawn from uniform distribution [0.5, 2.0] so panning is not fully predictable.

### Background Noise Layer
Generates a noise floor mixed at low volume beneath the voice. Helps mask TTS artifacts and adds warmth.

| Option | FFmpeg source | Notes |
|---|---|---|
| None | *(skip)* | |
| White noise | `anoisesrc=color=white` | Equal energy all frequencies |
| Pink noise | `anoisesrc=color=pink` | More low-frequency energy, warmer |
| Brown noise | `anoisesrc=color=brown` | Heavy low-frequency, very warm |
| Green noise | `anoisesrc=color=white` + EQ (mid-band boost, hi/lo rolloff) | Mid-band emphasis. anoisesrc has no native green color, so it's synthesized by EQ-shaping white noise. |
| Gray noise | `anoisesrc=color=white` + EQ (low/high boost, mid dip) | Perceptually flat (equal loudness weighted). Synthesized the same way, since anoisesrc has no native gray color. |

All noise: generated to match input audio length. Same EQ/filtering applied as voice for consistency.

**Baseline volume per color** (`core/presets.py: BACKGROUND_NOISE_BASE_DB`), tuned by ear since white/green/gray read as louder/harsher than pink/brown at the same nominal level:

| Color | Baseline | Notes |
|---|---|---|
| White | -58dB | Perceptually the loudest/harshest color |
| Pink | -52dB | |
| Brown | -52dB | |
| Green | -58dB | |
| Gray | -56dB | |

A GUI slider ("Noise Volume", -15 to +15) lets the user shift all colors up/down from their baseline together: `final_db = base_db + offset_db` (offset stored as `background_noise_volume_offset_db`, default 0).

### Background Noise Pulse / Wave
Optional slow amplitude envelope applied to the noise track only (not the voice), so the noise bed swells and recedes instead of staying perfectly static. Implemented as a numpy-generated mono gain envelope (`core/lfo.py: generate_noise_pulse_envelope_wav`), fed to FFmpeg as an `-f f32le` sidechain and applied via `amultiply` before the noise is mixed with the voice — same pattern as the panning sidechain.

| Option | Rate | Depth |
|---|---|---|
| None | — | Noise stays at a constant level |
| Slow swell | 0.045 Hz | 0.35 (gentle dip) |
| Breathing waves | 0.12 Hz | 0.55 (more noticeable dip) |

Depth is clamped so the envelope never reaches 0 — the noise fades down, it never cuts out completely. Stored as `noise_pulse` in config (`core/presets.py: NOISE_PULSE_PRESETS`).

### Ambience
Room and space effects applied to the voice.

| Option | FFmpeg filter |
|---|---|
| Dry | *(skip)* |
| Subtle room reverb | `aecho=0.8:0.9:40:0.3` |
| Dreamy space | `aecho=0.8:0.88:120:0.5,aecho=0.8:0.88:250:0.3` |
| Ethereal | `chorus=0.7:0.9:55:0.4:0.25:2,aecho=0.8:0.88:80:0.4` |

### Warmth / Saturation
Adds analog-like harmonic character. Subtle but effective on TTS voices.

| Option | FFmpeg filter |
|---|---|
| Clean | *(skip)* |
| Light saturation | `asoftclip=type=tanh,volume=0.95` |
| Warm saturation | `asoftclip=type=atan,volume=0.92` |

### Tempo Change
Changes playback speed without affecting pitch. Uses `atempo`; for values outside 0.5–2.0 range, chain multiple `atempo` filters.

| Option | FFmpeg filter |
|---|---|
| None | *(skip)* |
| Faster lightly | `atempo=1.15` |
| Faster heavily | `atempo=1.35` |
| Slower lightly | `atempo=0.87` |
| Slower heavily | `atempo=0.72` |

### Overall Intensity
Per-preset parameter tables that adjust the compressor operating point and (for echo presets) the echo tail character. Each preset has its own table of five intensity levels — the values are final, not multipliers.

**Reduce direction:** raises compressor threshold (less signal gets compressed), lowers ratio and makeup toward 1.0. Stops the compressor from lifting the noise floor. For echo presets: shorter delay and lower decay → drier, more intimate sound.

**Boost direction:** lowers threshold, raises ratio and makeup for more aggressive compression. For echo presets: longer delay and higher decay → more washed, more diffuse space.

| Option | Effect |
|---|---|
| No change | Preset's baseline character (matches the values shown in the preset descriptions above) |
| Boost lightly | Moderately more compressed; echo presets slightly longer tail |
| Boost heavily | Heavily compressed, prominent character; echo presets wide spacious wash |
| Reduce lightly | Lighter compression, cleaner sound; echo presets shorter/quieter tail |
| Reduce heavily | Minimal compression, near-dry; echo presets very short tail |

Parameters adjusted per level: `comp_threshold`, `comp_ratio`, `comp_makeup`, `gate_threshold`, `eq_gain` (EQ presets), `echo_out_gain` / `echo_delay_ms` / `echo_decay` (echo presets). Implemented in `core/presets.py: INTENSITY_TABLES`.

---

## Binaural Beats

Binaural beats are generated as two sine waves at slightly different frequencies (carrier ± beat_freq/2 Hz), one in each stereo channel. The perceived "beat" frequency is the difference between the two tones and entrains brainwaves toward that frequency. Requires headphones to work.

Generated to match the input audio length. Mixed at ≤-30dB (well below the voice). Always applied at Step 11, before the final limiter.

### GUI Addon Options

| Option | Intended effect | Frequency | Carrier | Volume |
|---|---|---|---|---|
| None | Off | — | — | — |
| Alpha (relaxed focus) | Light relaxation, calm alertness | 10Hz | 200Hz | -35dB |
| Theta (deep trance) | Deep meditation, trance state | 6Hz | 180Hz | -32dB |
| Theta→Delta ramp (sleep) | Progressive deepening toward sleep | 12Hz→0.5Hz over audio duration | 180Hz | -32dB |
| Gamma pulses (captivating) | Intense focus, heightened engagement | 40Hz | 200Hz | -30dB |

### Per-Main-Preset Defaults (when Binaural addon is not set to None)

| Main Preset | Default binaural option |
|---|---|
| Soft-Spoken ASMR | Alpha |
| Whispered ASMR | Alpha |
| Relaxing Hypnosis | Theta (with alpha→theta transition over first 25% of audio) |
| Deep Mesmerization | Gamma pulses during high-amplitude peaks, Theta otherwise |

### Implementation

Generate binaural layer using FFmpeg `filter_complex`:
```
sine=f=<carrier - beat/2>:duration=<audio_length>[L];
sine=f=<carrier + beat/2>:duration=<audio_length>[R];
[L][R]amerge=inputs=2,volume=<vol>dB[binaural]
```
Then mix `[binaural]` with the processed voice using `amix=normalize=0`.

For Theta→Delta ramp: use numpy to generate a frequency-sweep sine pair (frequency varies over time) written to a temp stereo WAV, same pattern as LFO sidechains.

### Safety Note (include in Quickstart.txt)
Not recommended for people with epilepsy, heart conditions, or pacemakers. Use headphones — binaural beats have no effect through speakers. Limit sessions to 25 minutes for theta/delta content.

---

## Preset Label Display Feature

Optional setting (`show_preset_values: true` in config.json). When enabled, each radio button in the GUI shows a compact auto-updating label with the key FFmpeg parameter values for that preset. Example:

```
(●) Whispered ASMR — highpass f=100, ratio=4:1, +8dB@8kHz
```

Labels update whenever the Main Preset selection changes, reflecting how the main preset influences addon defaults.
