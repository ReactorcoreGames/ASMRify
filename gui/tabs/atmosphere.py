import tkinter as tk

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from gui.theme import ToolTip

from .process import _make_scrollable_tab


class AtmosphereTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = _make_scrollable_tab(notebook, "Atmosphere")

        self.bg_noise_var = tk.StringVar(value=self._config.get("background_noise", "none"))
        self.bg_noise_volume_offset_var = tk.IntVar(
            value=self._config.get("background_noise_volume_offset_db", 0)
        )
        self.noise_pulse_var = tk.StringVar(value=self._config.get("noise_pulse", "none"))
        self.noise_pulse_organic_var = tk.BooleanVar(value=self._config.get("noise_pulse_organic", True))
        self.ambience_var = tk.StringVar(value=self._config.get("ambience", "dry"))
        self.warmth_var   = tk.StringVar(value=self._config.get("warmth", "clean"))

        bnf = _tk_ttk.LabelFrame(tab, text="Background Noise", padding=10)
        bnf.grid(sticky="ew", padx=14, pady=(14, 6))
        ToolTip(bnf, text="Adds a soft noise layer beneath the voice. Helps mask TTS artifacts and adds warmth. Kept very quiet so it doesn't overpower the voice.")

        for text, val, tip in [
            ("None",        "none",  "No background noise."),
            ("White noise", "white", "Neutral hiss across all frequencies."),
            ("Pink noise",  "pink",  "Warmer, more natural — like a gentle waterfall."),
            ("Brown noise", "brown", "Deep, low rumble — very calming."),
            ("Green noise", "green", "Mid-range focus, like distant outdoors ambience."),
            ("Gray noise",  "gray",  "Perceptually balanced — sounds equally loud across all frequencies."),
        ]:
            rb = ttk.Radiobutton(bnf, text=text, variable=self.bg_noise_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        vol_row = ttk.Frame(bnf)
        vol_row.pack(fill="x", pady=(10, 2))
        ttk.Label(vol_row, text="Noise Volume:", width=14).pack(side="left")
        vol_val_label = ttk.Label(vol_row, text=str(self.bg_noise_volume_offset_var.get()), width=4)
        vol_val_label.pack(side="right")

        def _on_volume_change(value, lbl=vol_val_label):
            v = int(float(value))
            self.bg_noise_volume_offset_var.set(v)
            lbl.config(text=str(v))
            self._app.on_setting_changed()

        vol_slider = ttk.Scale(vol_row, from_=-15, to=15, orient="horizontal",
                                variable=self.bg_noise_volume_offset_var,
                                command=_on_volume_change)
        vol_slider.pack(side="left", fill="x", expand=True, padx=(4, 4))
        ToolTip(vol_slider, text="Shifts the background noise louder (right) or quieter (left) relative to the default level. 0 is the recommended starting point.")

        ttk.Label(bnf, text="Pulse / Wave:").pack(anchor="w", pady=(10, 2))
        for text, val, tip in [
            ("None",             "none",            "Noise stays at a steady, constant level."),
            ("Slow swell",       "slow_swell",       "Noise gently rises and falls in volume over time, like slow waves."),
            ("Breathing waves",  "breathing_waves",  "A more noticeable rise and fall, like the noise is breathing."),
        ]:
            rb = ttk.Radiobutton(bnf, text=text, variable=self.noise_pulse_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        organic_cb = ttk.Checkbutton(
            bnf, text="+ Add organic waviness",
            variable=self.noise_pulse_organic_var,
            bootstyle="primary",
            command=self._app.on_setting_changed,
        )
        organic_cb.pack(anchor="w", pady=(4, 0), padx=(18, 0))
        ToolTip(organic_cb, text="Adds subtle irregularity to the wave rhythm so each swell is slightly different in length — less mechanical, more natural.")

        amf = _tk_ttk.LabelFrame(tab, text="Ambience", padding=10)
        amf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(amf, text="Adds room or space effects to make the voice feel like it exists in an environment.")

        for text, val, tip in [
            ("Dry",                "dry",           "No room effect. Voice is close and direct."),
            ("Subtle room reverb", "subtle_reverb", "Small room feel. Adds natural space without being obvious."),
            ("Dreamy space",       "dreamy_space",  "Larger, softer reverb. Floaty and immersive."),
            ("Ethereal",           "ethereal",      "Wide, lush reverb with chorus. Very spacious and otherworldly."),
        ]:
            rb = ttk.Radiobutton(amf, text=text, variable=self.ambience_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        wf = _tk_ttk.LabelFrame(tab, text="Warmth", padding=10)
        wf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(wf, text="Adds a subtle analog warmth. Makes TTS voices feel less digital and more natural.")

        for text, val, tip in [
            ("Clean",            "clean",     "No saturation. Keeps the original character."),
            ("Light saturation", "light_sat", "A touch of warmth. Barely noticeable but smooths harshness."),
            ("Warm saturation",  "warm_sat",  "Noticeably warmer. Good for voices that sound thin or tinny."),
        ]:
            rb = ttk.Radiobutton(wf, text=text, variable=self.warmth_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)
