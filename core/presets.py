"""
Preset parameter dicts for all main types and addons.

Main preset dicts store the fixed structural parameters for each preset.
Intensity-sensitive parameters (comp_threshold, comp_ratio, comp_makeup,
eq_gain, gate_threshold, and echo tap values for echo presets) live in
INTENSITY_TABLES — build_filter_chain() merges them at runtime.

Addon dicts store ready-made filter fragments (no numeric scaling needed).
"""

# ── Main type presets ────────────────────────────────────────────────────────
# Keys used by build_filter_chain():
#   highpass_f       — highpass cutoff Hz (always present)
#   lowpass_f        — lowpass cutoff Hz, or None to skip
#   eq_f / eq_width_type / eq_width  — equalizer band shape, or all None
#   comp_attack      — acompressor attack ms
#   comp_release     — acompressor release ms
#   echo             — list of (in_gain, out_gain, delay_ms, decay) tuples, or []
#                      out_gain / delay_ms / decay are overridden per intensity level
#                      for echo presets; in_gain stays fixed
#   (alimiter always uses level_in=1:level_out=1:limit=1.0 — no per-preset params)
#
# Intensity-driven params (comp_threshold, comp_ratio, comp_makeup, eq_gain,
# gate_threshold, echo tap overrides) come from INTENSITY_TABLES below.

MAIN_PRESETS = {
    "soft_spoken_asmr": {
        "highpass_f": 80,
        "lowpass_f": None,
        "eq_f": 6000, "eq_width_type": "o", "eq_width": 2,
        "comp_attack": 10, "comp_release": 100,
        "echo": [],
    },
    "whispered_asmr": {
        "highpass_f": 100,
        "lowpass_f": None,
        "eq_f": 8000, "eq_width_type": "o", "eq_width": 1.5,
        "comp_attack": 5, "comp_release": 80,
        "echo": [],
    },
    "relaxing_hypnosis": {
        "highpass_f": 60,
        "lowpass_f": 12000,
        "eq_f": None, "eq_width_type": None, "eq_width": None,
        "comp_attack": 15, "comp_release": 150,
        # echo in_gain is fixed; out_gain/delay_ms/decay come from INTENSITY_TABLES
        "echo": [(0.8, None, None, None)],
    },
    "deep_mesmerization": {
        "highpass_f": 60,
        "lowpass_f": 10000,
        "eq_f": None, "eq_width_type": None, "eq_width": None,
        "comp_attack": 8, "comp_release": 120,
        # two echo taps; out_gain/delay_ms/decay come from INTENSITY_TABLES
        "echo": [(0.8, None, None, None), (0.8, None, None, None)],
    },
}

# ── Intensity tables ──────────────────────────────────────────────────────────
# Per-preset, per-intensity-level final parameter values (not multipliers).
# Keys present in every row:
#   comp_threshold  — acompressor threshold dB
#   comp_ratio      — acompressor ratio
#   comp_makeup     — acompressor makeup gain (linear, ≥1.0)
#   gate_threshold  — agate threshold (linear amplitude, 0–1)
#   eq_gain         — equalizer band gain dB, or None for presets with no EQ band
# Echo presets also carry per-tap overrides:
#   echo0_out_gain, echo0_delay_ms, echo0_decay
#   echo1_out_gain, echo1_delay_ms, echo1_decay  (deep_mesmerization only)
#
# Reduce direction: raise threshold (less signal compressed), lower ratio and
#   makeup toward 1.0 — avoids lifting the noise floor; gate threshold rises.
# Boost direction: lower threshold, higher ratio/makeup; echo presets get
#   longer delay and higher decay for a more washed/spacious tail.

INTENSITY_TABLES = {
    "soft_spoken_asmr": {
        #                             threshold  ratio  makeup  gate    eq_gain
        "reduce_heavy": {"comp_threshold": -10, "comp_ratio": 1.8, "comp_makeup": 1.0, "gate_threshold": 0.018, "eq_gain":  0.5},
        "reduce_light": {"comp_threshold": -14, "comp_ratio": 2.5, "comp_makeup": 1.5, "gate_threshold": 0.013, "eq_gain":  1.2},
        "no_change":    {"comp_threshold": -18, "comp_ratio": 3.0, "comp_makeup": 2.0, "gate_threshold": 0.010, "eq_gain":  2.0},
        "boost_light":  {"comp_threshold": -21, "comp_ratio": 3.8, "comp_makeup": 3.0, "gate_threshold": 0.008, "eq_gain":  3.5},
        "boost_heavy":  {"comp_threshold": -24, "comp_ratio": 5.0, "comp_makeup": 4.5, "gate_threshold": 0.006, "eq_gain":  5.0},
    },
    "whispered_asmr": {
        # eq_gain is the high-shelf air boost — the defining character of this preset.
        # Boost cranks it for extra crispness; reduce pulls it toward neutral.
        "reduce_heavy": {"comp_threshold":  -12, "comp_ratio": 2.0, "comp_makeup": 1.0, "gate_threshold": 0.018, "eq_gain":  1.0},
        "reduce_light": {"comp_threshold":  -16, "comp_ratio": 3.0, "comp_makeup": 2.0, "gate_threshold": 0.013, "eq_gain":  2.5},
        "no_change":    {"comp_threshold":  -20, "comp_ratio": 4.0, "comp_makeup": 3.0, "gate_threshold": 0.010, "eq_gain":  4.0},
        "boost_light":  {"comp_threshold":  -23, "comp_ratio": 5.0, "comp_makeup": 4.5, "gate_threshold": 0.008, "eq_gain":  6.0},
        "boost_heavy":  {"comp_threshold":  -26, "comp_ratio": 6.5, "comp_makeup": 6.0, "gate_threshold": 0.006, "eq_gain":  9.0},
    },
    "relaxing_hypnosis": {
        # Echo: reduce = shorter/quieter tail; boost = longer/more diffuse wash.
        # out_gain kept below 0.9 at all levels to prevent feedback buildup.
        "reduce_heavy": {"comp_threshold":  -8,  "comp_ratio": 2.0, "comp_makeup": 1.0, "gate_threshold": 0.018, "eq_gain": None,
                         "echo0_out_gain": 0.55, "echo0_delay_ms":  60, "echo0_decay": 0.20},
        "reduce_light": {"comp_threshold": -12,  "comp_ratio": 2.8, "comp_makeup": 1.5, "gate_threshold": 0.013, "eq_gain": None,
                         "echo0_out_gain": 0.72, "echo0_delay_ms":  90, "echo0_decay": 0.30},
        "no_change":    {"comp_threshold": -16,  "comp_ratio": 3.5, "comp_makeup": 2.0, "gate_threshold": 0.010, "eq_gain": None,
                         "echo0_out_gain": 0.88, "echo0_delay_ms": 120, "echo0_decay": 0.40},
        "boost_light":  {"comp_threshold": -19,  "comp_ratio": 4.0, "comp_makeup": 3.0, "gate_threshold": 0.008, "eq_gain": None,
                         "echo0_out_gain": 0.88, "echo0_delay_ms": 160, "echo0_decay": 0.55},
        "boost_heavy":  {"comp_threshold": -22,  "comp_ratio": 5.0, "comp_makeup": 4.0, "gate_threshold": 0.006, "eq_gain": None,
                         "echo0_out_gain": 0.88, "echo0_delay_ms": 220, "echo0_decay": 0.68},
    },
    "deep_mesmerization": {
        # Two echo taps. Reduce: both taps shorten/quieten toward near-reverb territory.
        # Boost: both taps lengthen; first tap drives the main wash, second adds depth.
        "reduce_heavy": {"comp_threshold":  -6,  "comp_ratio": 2.5, "comp_makeup": 1.0, "gate_threshold": 0.018, "eq_gain": None,
                         "echo0_out_gain": 0.55, "echo0_delay_ms":  80, "echo0_decay": 0.22,
                         "echo1_out_gain": 0.45, "echo1_delay_ms": 160, "echo1_decay": 0.14},
        "reduce_light": {"comp_threshold": -10,  "comp_ratio": 3.5, "comp_makeup": 2.0, "gate_threshold": 0.013, "eq_gain": None,
                         "echo0_out_gain": 0.72, "echo0_delay_ms": 140, "echo0_decay": 0.35,
                         "echo1_out_gain": 0.60, "echo1_delay_ms": 280, "echo1_decay": 0.22},
        "no_change":    {"comp_threshold": -14,  "comp_ratio": 5.0, "comp_makeup": 4.0, "gate_threshold": 0.010, "eq_gain": None,
                         "echo0_out_gain": 0.88, "echo0_delay_ms": 200, "echo0_decay": 0.50,
                         "echo1_out_gain": 0.88, "echo1_delay_ms": 400, "echo1_decay": 0.30},
        "boost_light":  {"comp_threshold": -17,  "comp_ratio": 6.0, "comp_makeup": 5.5, "gate_threshold": 0.008, "eq_gain": None,
                         "echo0_out_gain": 0.88, "echo0_delay_ms": 260, "echo0_decay": 0.62,
                         "echo1_out_gain": 0.88, "echo1_delay_ms": 520, "echo1_decay": 0.42},
        "boost_heavy":  {"comp_threshold": -20,  "comp_ratio": 7.5, "comp_makeup": 7.0, "gate_threshold": 0.006, "eq_gain": None,
                         "echo0_out_gain": 0.88, "echo0_delay_ms": 340, "echo0_decay": 0.72,
                         "echo1_out_gain": 0.88, "echo1_delay_ms": 650, "echo1_decay": 0.52},
    },
}

# ── Voice pitch (rubberband) ──────────────────────────────────────────────────
VOICE_PITCH = {
    "original":        "",
    "slightly_deeper": "rubberband=pitch=0.87",
    "much_deeper":     "rubberband=pitch=0.75",
    "slightly_higher": "rubberband=pitch=1.12",
}

# ── Ambience ──────────────────────────────────────────────────────────────────
AMBIENCE = {
    "dry":           "",
    "subtle_reverb": "aecho=0.8:0.9:40:0.3",
    "dreamy_space":  "chorus=0.6:0.8:75:0.5:0.3:1.5,aecho=0.7:0.6:90:0.25",
    "ethereal":      "chorus=0.7:0.9:55:0.4:0.25:2,aecho=0.8:0.88:80:0.4",
}

# ── Warmth / saturation ───────────────────────────────────────────────────────
WARMTH = {
    "clean":       "",
    "light_sat":   "equalizer=f=250:width_type=o:width=2:g=9,asoftclip=type=tanh,asoftclip=type=tanh",
    "warm_sat":    "equalizer=f=280:width_type=o:width=2.5:g=15,asoftclip=type=quintic,asoftclip=type=quintic,asoftclip=type=tanh",
}

# ── Tempo change ──────────────────────────────────────────────────────────────
TEMPO = {
    "none":          "",
    "faster_light":  "atempo=1.15",
    "faster_heavy":  "atempo=1.35",
    "slower_light":  "atempo=0.87",
    "slower_heavy":  "atempo=0.72",
}

# ── Background noise ──────────────────────────────────────────────────────────
# Maps config value → FFmpeg anoisesrc color name
BACKGROUND_NOISE_COLORS = {
    "white": "white",
    "pink":  "pink",
    "brown": "brown",
    "green": "green",
    "gray":  "gray",
}

# Per-color baseline attenuation (dB) applied before mixing with the voice.
# Tuned by ear: white/green/gray read as perceptually louder/harsher than
# pink/brown at the same nominal level, so they get a lower baseline.
BACKGROUND_NOISE_BASE_DB = {
    "white": -28,
    "pink":  -22,
    "brown": -22,
    "green": -28,
    "gray":  -26,
}

# ── Background noise pulse / wave envelope ─────────────────────────────────────
# (rate_hz, depth) — depth is the fraction the gain dips below 1.0 at the
# trough of the wave. "none" disables the envelope (static noise level).
NOISE_PULSE_PRESETS = {
    "none":            None,
    "slow_swell":      (0.045, 0.35),
    "breathing_waves": (0.12,  0.55),
}

# ── Pitch wobble (FFmpeg vibrato filter) ──────────────────────────────────────
WOBBLE_FILTERS = {
    "subtle":      "vibrato=f=3.5:d=0.8",
    "noticeable":  "vibrato=f=5.0:d=0.6",
    "deep_trance": "vibrato=f=6.5:d=0.4",
    "eerie":       "vibrato=f=8.0:d=0.5",
}

# ── Preset value label helper ─────────────────────────────────────────────────

def preset_label(preset_key: str) -> str:
    """
    Return a compact one-line summary of key FFmpeg parameters for a main
    preset. Used by the GUI when show_preset_values is enabled.
    """
    p = MAIN_PRESETS.get(preset_key)
    t = INTENSITY_TABLES.get(preset_key, {}).get("no_change", {})
    if p is None:
        return ""
    parts = [f"highpass f={p['highpass_f']}"]
    if p["lowpass_f"] is not None:
        parts.append(f"lowpass f={p['lowpass_f']}")
    eq_gain = t.get("eq_gain")
    if p["eq_f"] is not None and eq_gain is not None:
        sign = "+" if eq_gain >= 0 else ""
        parts.append(f"{sign}{eq_gain}dB@{p['eq_f']}Hz")
    ratio = t.get("comp_ratio")
    if ratio is not None:
        parts.append(f"ratio={ratio}:1")
    if p["echo"]:
        parts.append(f"echo ×{len(p['echo'])}")
    return ",  ".join(parts)
