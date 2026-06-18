import json
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "input_folder": "",
    "output_folder": "",
    "main_preset": "soft_spoken_asmr",
    "voice_pitch": "original",
    "pitch_wobble": "none",
    "panning_type": "none",
    "panning_cooldown": "moderate",
    "panning_crossfade": "xfade_short",
    "panning_ear_start_center": True,
    "panning_bias": "bias_equal",
    "panning_bias_weight_l": 3,
    "panning_bias_weight_c": 1,
    "panning_bias_weight_r": 3,
    "background_noise": "none",
    "background_noise_volume_offset_db": 0,
    "noise_pulse": "none",
    "ambience": "dry",
    "warmth": "clean",
    "tempo": "none",
    "intensity": "no_change",
    "binaural": "none",
    "binaural_volume_offset_db": 0,
    "binaural_pulse": "none",
    "output_format": "wav",
    "normalization_mode": "loudness",
    "show_preset_values": False,
}


def _config_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config.json"
    return Path(__file__).resolve().parent.parent / "config.json"


def load_config():
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **data}
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(data):
    _config_path().write_text(json.dumps(data, indent=2), encoding="utf-8")
