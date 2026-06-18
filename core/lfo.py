"""
LFO (low-frequency oscillator) envelope generators for pitch wobble and panning.

All output is written as raw float32 little-endian binary files so FFmpeg can
read them with: -f f32le -ar <sample_rate> -ac <channels> -i <path>
"""

import os
import random
import numpy as np


# ── Pitch wobble ──────────────────────────────────────────────────────────────

def generate_pitch_wobble_wav(
    deviation_hz: float,
    rate_hz: float,
    duration_sec: float,
    sample_rate: int,
    output_path: str,
) -> None:
    """
    Write a mono float32 raw file: sine wave at rate_hz with amplitude scaled
    so that deviation_hz maps to the normalised float range.

    amplitude = deviation_hz / (sample_rate / 2)

    Used as a sidechain for pitch-modulation experiments; the primary wobble
    path in the processing chain uses FFmpeg's built-in vibrato filter instead.
    """
    n = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n, endpoint=False, dtype=np.float64)
    amplitude = deviation_hz / (sample_rate / 2.0)
    envelope = (amplitude * np.sin(2.0 * np.pi * rate_hz * t)).astype(np.float32)
    envelope.tofile(output_path)


def generate_noise_pulse_envelope_wav(
    rate_hz: float,
    depth: float,
    duration_sec: float,
    sample_rate: int,
    output_path: str,
    organic: bool = False,
) -> None:
    """
    Write a mono float32 raw gain envelope that slowly swells and recedes,
    centred at 1.0, dipping to (1.0 - depth) at the trough of each cycle.

    When organic=True the base rate is slowly modulated by a secondary LFO
    (≈1/7th the main rate) with a random phase, making each wave slightly
    different in length — an irregular, breathing quality rather than a
    mechanical metronome.
    """
    depth = min(max(depth, 0.0), 0.85)
    n = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n, endpoint=False, dtype=np.float64)

    if organic:
        # Modulate the instantaneous rate: ±40% variation at ~1/7 of the base rate
        mod_rate  = rate_hz / 7.0
        mod_depth = 0.4
        mod_phase = random.uniform(0.0, 2.0 * np.pi)
        inst_rate = rate_hz * (1.0 + mod_depth * np.sin(2.0 * np.pi * mod_rate * t + mod_phase))
        phase = np.cumsum(inst_rate) / sample_rate * 2.0 * np.pi
        wave = 0.5 - 0.5 * np.cos(phase)
    else:
        wave = 0.5 - 0.5 * np.cos(2.0 * np.pi * rate_hz * t)  # 0 → 1 → 0, smooth

    envelope = (1.0 - depth * wave).astype(np.float32)
    envelope.tofile(output_path)


# Binaural pulse uses the same envelope shape as noise pulse
generate_binaural_pulse_envelope_wav = generate_noise_pulse_envelope_wav


# ── Panning envelope ──────────────────────────────────────────────────────────

# Cooldown-mode → base swirl frequency (Hz)
_COOLDOWN_FREQ = {
    "slow":            0.015,
    "moderate":        0.033,
    "quick":           0.11,
    "intensity_based": 0.033,  # overridden dynamically for dynamic_swirl
}

# Cooldown-mode → (min_interval_sec, max_interval_sec) for gentle_lr transitions
_COOLDOWN_INTERVALS = {
    "slow":            (45.0, 90.0),
    "moderate":        (15.0, 45.0),
    "quick":           (3.0, 15.0),
    "intensity_based": (2.0, 15.0),
}

# Cooldown-mode → (min_hold_sec, max_hold_sec) for ear-to-ear modes
_COOLDOWN_INTERVALS_EAR = {
    "slow":            (8.0,  15.0),
    "moderate":        (3.0,   8.0),
    "quick":           (1.0,   3.0),
    "intensity_based": (1.0,   3.0),
}


def generate_pan_envelope_wav(
    pan_type: str,
    cooldown_mode: str,
    duration_sec: float,
    sample_rate: int,
    audio_amplitude_array: "np.ndarray | None",
    output_path: str,
    crossfade_sec: float = 0.3,
    start_center: bool = True,
    bias: str = "bias_equal",
    weight_l: float = 3,
    weight_c: float = 1,
    weight_r: float = 3,
) -> bool:
    """
    Write a stereo float32 raw file (2-channel interleaved): left and right
    gain curves for panning.

    Returns True if a file was written, False if pan_type is "none" (caller
    should skip the sidechain entirely).

    FFmpeg read command: -f f32le -ar <sample_rate> -ac 2 -i <output_path>
    """
    if pan_type == "none":
        return False

    n = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, n, endpoint=False, dtype=np.float64)

    if pan_type == "smooth_swirl":
        left, right = _smooth_swirl(t, cooldown_mode, sample_rate)

    elif pan_type == "gentle_lr":
        left, right = _gentle_lr(t, cooldown_mode, duration_sec, sample_rate)

    elif pan_type == "dynamic_swirl":
        left, right = _dynamic_swirl(t, cooldown_mode, audio_amplitude_array, sample_rate)

    elif pan_type == "ear_to_ear":
        left, right = _ear_to_ear(t, cooldown_mode, crossfade_sec, sample_rate, start_center)

    elif pan_type == "ear_to_ear_front":
        hold_weights = _bias_weights(bias, weight_l, weight_c, weight_r)
        left, right = _ear_to_ear_front(t, cooldown_mode, crossfade_sec, sample_rate, start_center, hold_weights)

    else:
        # Fallback: center
        left = np.ones(n, dtype=np.float32)
        right = np.ones(n, dtype=np.float32)

    left = np.clip(left, 0.0, 1.0).astype(np.float32)
    right = np.clip(right, 0.0, 1.0).astype(np.float32)

    # Pre-pad with unity samples so FFmpeg decoder timing skew (typically 1–2
    # audio frames / ~1024 samples) lands in the silent guard region, not the ramp.
    PAD = 2048
    left  = np.concatenate([np.ones(PAD, dtype=np.float32), left])
    right = np.concatenate([np.ones(PAD, dtype=np.float32), right])

    # Interleave L/R into stereo
    total = len(left)
    stereo = np.empty(total * 2, dtype=np.float32)
    stereo[0::2] = left
    stereo[1::2] = right
    stereo.tofile(output_path)
    return True


# ── Panning helpers ───────────────────────────────────────────────────────────

def _constant_power_gains(pos: np.ndarray) -> tuple:
    """
    Convert a pan position array in [-1, +1] to constant-power L/R gain arrays.

    pos = -1  →  left=1.0,  right=0.0   (full left)
    pos =  0  →  left=0.707, right=0.707 (center, -3 dB each)
    pos = +1  →  left=0.0,  right=1.0   (full right)

    Satisfies left² + right² = 1 for all pos values.
    """
    angle = (pos + 1.0) / 2.0 * (np.pi / 2.0)
    return np.cos(angle), np.sin(angle)


def _fade_in_envelope(
    left: np.ndarray,
    right: np.ndarray,
    sample_rate: int,
    fade_sec: float = 0.1,
) -> tuple:
    """
    Ramp L and R gains from the constant-power center (√0.5 ≈ 0.707) to their
    envelope values over the first fade_sec seconds using cosine ease-in.

    Prevents click transients caused by decoder startup timing mismatches when
    the envelope file begins at a non-center position.
    """
    n_fade = min(int(fade_sec * sample_rate), len(left))
    if n_fade <= 0:
        return left, right

    t_norm = np.linspace(0.0, 1.0, n_fade, endpoint=False)
    ramp   = 0.5 - 0.5 * np.cos(np.pi * t_norm)  # 0 → 1, cosine ease-in

    # Start from 1.0/1.0 (unity pass-through) so amultiply has no effect at t=0.
    # Ramping from 0.707 would still attenuate the audio on the first sample,
    # which causes a click on whichever channel the envelope starts biased toward.
    left  = left.copy()
    right = right.copy()
    left[:n_fade]  = 1.0 + (left[:n_fade]  - 1.0) * ramp
    right[:n_fade] = 1.0 + (right[:n_fade] - 1.0) * ramp

    return left, right


# ── Panning helpers ───────────────────────────────────────────────────────────

_E2E_BIAS = 0.85  # shared constant for bias weight keys

def _bias_weights(
    bias: str,
    weight_l: float,
    weight_c: float,
    weight_r: float,
) -> dict:
    """
    Resolve bias setting to a {stop_position: hold_multiplier} dict for
    _ear_to_ear_front. Multipliers scale the hold duration at each stop.
    """
    B = _E2E_BIAS
    if bias == "bias_sides":
        return {-B: 2.0, 0.0: 1.0, B: 2.0}
    if bias == "bias_center":
        return {-B: 1.0, 0.0: 2.0, B: 1.0}
    if bias == "bias_chaos":
        return {-B: random.uniform(0.5, 5.0), 0.0: random.uniform(0.5, 5.0), B: random.uniform(0.5, 5.0)}
    if bias == "bias_custom":
        total = weight_l + weight_c + weight_r
        if total <= 0:
            total = 1.0
        norm = 3.0 / total
        return {-B: weight_l * norm, 0.0: weight_c * norm, B: weight_r * norm}
    # bias_equal and fallback
    return {-B: 1.0, 0.0: 1.0, B: 1.0}


# ── Panning mode functions ────────────────────────────────────────────────────

def _smooth_swirl(t: np.ndarray, cooldown_mode: str, sample_rate: int = 44100) -> tuple:
    """
    Continuous constant-power circular panning.

    pos(t) = sin(2π*f*t) oscillates between -1 (full left) and +1 (full right).
    Converted to L/R via _constant_power_gains so L²+R²=1 at every sample.
    A random speed factor keeps the rotation slightly unpredictable.
    """
    base_f = _COOLDOWN_FREQ.get(cooldown_mode, 0.033)
    f      = base_f * random.uniform(0.5, 2.0)

    pos         = np.sin(2.0 * np.pi * f * t)
    left, right = _constant_power_gains(pos)
    left, right = _fade_in_envelope(left, right, sample_rate)
    return left, right


def _gentle_lr(
    t: np.ndarray,
    cooldown_mode: str,
    duration_sec: float,
    sample_rate: int,
) -> tuple:
    """
    Smooth crossfade between random L/R positions (±0.75 from centre) at
    intervals drawn from the cooldown distribution. Uses constant-power gains.
    """
    min_iv, max_iv = _COOLDOWN_INTERVALS.get(cooldown_mode, (15.0, 45.0))
    n = len(t)

    # Build list of (sample_index, pan_position) keyframes
    # pan_position: -0.75 = strong left bias, +0.75 = strong right bias, 0 = centre
    keyframes = [(0, 0.0)]
    pos = 0
    while pos < n:
        interval_sec = random.uniform(min_iv, max_iv) * random.uniform(0.5, 2.0)
        pos += int(interval_sec * sample_rate)
        target = random.uniform(-0.75, 0.75)
        keyframes.append((min(pos, n - 1), target))

    if keyframes[-1][0] < n - 1:
        keyframes.append((n - 1, 0.0))

    # Build pan position curve via cosine interpolation between keyframes
    pan = np.zeros(n, dtype=np.float64)
    for i in range(len(keyframes) - 1):
        i0, p0 = keyframes[i]
        i1, p1 = keyframes[i + 1]
        seg_len = i1 - i0
        if seg_len <= 0:
            continue
        frac = np.linspace(0.0, 1.0, seg_len, endpoint=False)
        smooth = 0.5 - 0.5 * np.cos(np.pi * frac)  # cosine ease
        pan[i0:i1] = p0 + (p1 - p0) * smooth

    # Constant-power gains (no fade-in needed: keyframes start at pos=0 = center)
    left, right = _constant_power_gains(pan)
    return left, right


def _dynamic_swirl(
    t: np.ndarray,
    cooldown_mode: str,
    audio_amplitude_array: "np.ndarray | None",
    sample_rate: int,
) -> tuple:
    """
    Pan rate driven by audio amplitude. Loud sections rotate faster; quiet
    sections barely move. Falls back to smooth_swirl if no amplitude data.
    """
    if audio_amplitude_array is None or len(audio_amplitude_array) == 0:
        return _smooth_swirl(t, cooldown_mode, sample_rate)

    n = len(t)

    # Resample amplitude envelope to match output length
    amp = np.abs(audio_amplitude_array).astype(np.float64)
    if len(amp) != n:
        indices = np.linspace(0, len(amp) - 1, n)
        amp = np.interp(indices, np.arange(len(amp)), amp)

    # Normalise amplitude to [0, 1]
    peak = amp.max()
    if peak > 0:
        amp /= peak

    # Base rotation frequency scaled by amplitude
    base_f = _COOLDOWN_FREQ.get(cooldown_mode, 0.033)
    min_f  = base_f * 0.2
    max_f  = base_f * 3.0
    inst_f = min_f + (max_f - min_f) * amp

    # Integrate instantaneous frequency to get phase
    dt    = 1.0 / sample_rate
    phase = np.cumsum(inst_f) * dt * 2.0 * np.pi

    pos         = np.sin(phase)
    left, right = _constant_power_gains(pos)
    left, right = _fade_in_envelope(left, right, sample_rate)
    return left, right


def _ear_to_ear(
    t: np.ndarray,
    cooldown_mode: str,
    crossfade_sec: float,
    sample_rate: int,
    start_center: bool = True,
) -> tuple:
    """
    Alternates audio between left and right ear at ±0.85 bias.

    crossfade_sec — duration of the L→R transition (from panning_crossfade setting)
    start_center  — if True, opens at center then switches after one hold period;
                    if False, jumps immediately to the first ear at t=0

    Each segment is [flat hold at current position] + [cosine ramp to next].
    Hold durations are randomized with a ×[0.5, 2.0] factor for organic pacing.
    """
    BIAS              = 0.85
    n                 = len(t)
    min_hold, max_hold = _COOLDOWN_INTERVALS_EAR.get(cooldown_mode, (3.0, 8.0))
    crossfade_samples  = int(crossfade_sec * sample_rate)

    side = random.choice([-1, 1])

    if start_center:
        events = [(0, 0.0)]
        hold_sec   = random.uniform(min_hold, max_hold) * random.uniform(0.5, 2.0)
        cur_sample = int(hold_sec * sample_rate)
    else:
        events = [(0, side * BIAS)]
        side = -side
        hold_sec   = random.uniform(min_hold, max_hold) * random.uniform(0.5, 2.0)
        cur_sample = int(hold_sec * sample_rate)

    while cur_sample < n:
        events.append((min(cur_sample, n - 1), side * BIAS))
        hold_sec    = random.uniform(min_hold, max_hold) * random.uniform(0.5, 2.0)
        cur_sample += int(hold_sec * sample_rate)
        side        = -side

    if events[-1][0] < n - 1:
        events.append((n - 1, 0.0))

    # Build pan-position curve: flat hold then cosine crossfade at tail
    pan = np.zeros(n, dtype=np.float64)

    for i in range(len(events) - 1):
        i0, p0 = events[i]
        i1, p1 = events[i + 1]
        seg_len = i1 - i0
        if seg_len <= 0:
            pan[i0] = p0
            continue

        cf       = min(crossfade_samples, seg_len)
        hold_end = i0 + (seg_len - cf)

        if hold_end > i0:
            pan[i0:hold_end] = p0

        frac   = np.linspace(0.0, 1.0, cf, endpoint=False)
        smooth = 0.5 - 0.5 * np.cos(np.pi * frac)
        pan[hold_end:i1] = p0 + (p1 - p0) * smooth

    pan[n - 1] = events[-1][1]

    left, right = _constant_power_gains(pan)
    left, right = _fade_in_envelope(left, right, sample_rate)
    return left, right


def _ear_to_ear_front(
    t: np.ndarray,
    cooldown_mode: str,
    crossfade_sec: float,
    sample_rate: int,
    start_center: bool = True,
    hold_weights: "dict | None" = None,
) -> tuple:
    """
    Like _ear_to_ear but cycles through left (−0.85), front (0.0), and right
    (+0.85) as three distinct stops, in a randomised non-repeating order.

    start_center  — if True, opens at center before first stop; if False, opens
                    immediately at the first stop in the shuffled cycle
    hold_weights  — dict mapping each stop position to a hold-duration multiplier,
                    from _bias_weights(). None falls back to equal weighting.
    """
    BIAS = _E2E_BIAS
    STOPS = [-BIAS, 0.0, BIAS]

    n = len(t)
    min_hold, max_hold = _COOLDOWN_INTERVALS_EAR.get(cooldown_mode, (3.0, 8.0))
    crossfade_samples = int(crossfade_sec * sample_rate)

    if hold_weights is None:
        hold_weights = {-BIAS: 1.0, 0.0: 1.0, BIAS: 1.0}

    cycle = random.sample(STOPS, len(STOPS))
    cycle_idx = 0

    if start_center:
        events = [(0, 0.0)]
        hold_sec = random.uniform(min_hold, max_hold) * random.uniform(0.5, 2.0)
        cur_sample = int(hold_sec * sample_rate)
    else:
        events = [(0, cycle[cycle_idx])]
        cycle_idx = 1
        first_pos = events[0][1]
        hold_sec = random.uniform(min_hold, max_hold) * random.uniform(0.5, 2.0) * hold_weights.get(first_pos, 1.0)
        cur_sample = int(hold_sec * sample_rate)

    while cur_sample < n:
        pos = cycle[cycle_idx]
        events.append((min(cur_sample, n - 1), pos))
        weight = hold_weights.get(pos, 1.0)
        hold_sec = random.uniform(min_hold, max_hold) * random.uniform(0.5, 2.0) * weight
        cur_sample += int(hold_sec * sample_rate)
        cycle_idx += 1
        if cycle_idx >= len(cycle):
            cycle = random.sample(STOPS, len(STOPS))
            cycle_idx = 0

    if events[-1][0] < n - 1:
        events.append((n - 1, 0.0))

    pan = np.zeros(n, dtype=np.float64)
    for i in range(len(events) - 1):
        i0, p0 = events[i]
        i1, p1 = events[i + 1]
        seg_len = i1 - i0
        if seg_len <= 0:
            pan[i0] = p0
            continue

        cf = min(crossfade_samples, seg_len)
        hold_end = i0 + (seg_len - cf)

        if hold_end > i0:
            pan[i0:hold_end] = p0

        frac = np.linspace(0.0, 1.0, cf, endpoint=False)
        smooth = 0.5 - 0.5 * np.cos(np.pi * frac)
        pan[hold_end:i1] = p0 + (p1 - p0) * smooth

    pan[n - 1] = events[-1][1]

    left, right = _constant_power_gains(pan)
    left, right = _fade_in_envelope(left, right, sample_rate)
    return left, right
