import tkinter as tk

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from gui.theme import ToolTip

from gui.theme import FONT_SMALL, FONT_TINY

from .process import _make_scrollable_tab


class BinauralTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = _make_scrollable_tab(notebook, "Binaural")

        self.binaural_var = tk.StringVar(value=self._config.get("binaural", "none"))
        self.binaural_volume_offset_var = tk.IntVar(
            value=self._config.get("binaural_volume_offset_db", 0)
        )
        self.binaural_pulse_var = tk.StringVar(value=self._config.get("binaural_pulse", "none"))
        self.binaural_pulse_organic_var = tk.BooleanVar(value=self._config.get("binaural_pulse_organic", True))

        bf = _tk_ttk.LabelFrame(tab, text="Binaural Beats", padding=10)
        bf.grid(sticky="ew", padx=14, pady=(14, 6))

        ttk.Label(bf,
                  text="Requires headphones. Has no effect through speakers. Optional feature — leave on None if unsure.",
                  font=FONT_SMALL, bootstyle="warning").pack(anchor="w", pady=(0, 8))

        for text, val, tip in [
            ("None",                        "none",        "No binaural layer added."),
            ("Alpha — relaxed focus",       "alpha",       "A gentle 10Hz layer. Promotes calm, clear-headed relaxation. Good for soft ASMR."),
            ("Theta — deep trance",         "theta",       "A 6Hz layer associated with deep meditation and trance states. Pairs well with hypnotic modes."),
            ("Theta→Delta ramp — sleep",    "theta_delta", "Starts at light relaxation and gradually ramps down toward deep sleep frequencies over the course of the audio."),
            ("Gamma pulses — captivating",  "gamma",       "40Hz pulses. Associated with intense focus and heightened engagement. Good for Deep Mesmerization mode."),
        ]:
            rb = ttk.Radiobutton(bf, text=text, variable=self.binaural_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        ttk.Label(bf, text="Relaxing Hypnosis defaults to Theta. Deep Mesmerization defaults to Gamma pulses.",
                  font=FONT_TINY, bootstyle="secondary").pack(anchor="w", pady=(8, 4))

        vol_row = ttk.Frame(bf)
        vol_row.pack(fill="x", pady=(6, 2))
        ttk.Label(vol_row, text="Beat Volume:", width=14).pack(side="left")
        vol_val_label = ttk.Label(vol_row, text=str(self.binaural_volume_offset_var.get()), width=4)
        vol_val_label.pack(side="right")

        def _on_volume_change(value, lbl=vol_val_label):
            v = int(float(value))
            self.binaural_volume_offset_var.set(v)
            lbl.config(text=str(v))
            self._app.on_setting_changed()

        vol_slider = ttk.Scale(vol_row, from_=-15, to=15, orient="horizontal",
                               variable=self.binaural_volume_offset_var,
                               command=_on_volume_change)
        vol_slider.pack(side="left", fill="x", expand=True, padx=(4, 4))
        ToolTip(vol_slider, text="Shifts the binaural layer louder (right) or quieter (left) relative to its default level. 0 is the recommended starting point.")

        ttk.Label(bf, text="Pulse / Wave:").pack(anchor="w", pady=(10, 2))
        for text, val, tip in [
            ("None",             "none",            "Binaural layer stays at a steady, constant level."),
            ("Slow swell",       "slow_swell",       "Beat layer gently rises and falls in volume over time, like slow waves."),
            ("Breathing waves",  "breathing_waves",  "A more noticeable rise and fall, like the beat is breathing."),
        ]:
            rb = ttk.Radiobutton(bf, text=text, variable=self.binaural_pulse_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        organic_cb = ttk.Checkbutton(
            bf, text="+ Add organic waviness",
            variable=self.binaural_pulse_organic_var,
            bootstyle="primary",
            command=self._app.on_setting_changed,
        )
        organic_cb.pack(anchor="w", pady=(4, 6), padx=(18, 0))
        ToolTip(organic_cb, text="Adds subtle irregularity to the wave rhythm so each swell is slightly different in length — less mechanical, more natural.")

        warning_lbl = ttk.Label(bf, text="Not recommended for people with epilepsy or pacemakers.",
                                font=(*FONT_TINY[:2], "italic"), bootstyle="danger")
        warning_lbl.pack(anchor="w", pady=(10, 0))
        ToolTip(warning_lbl,
                wraplength=500,
                text="Binaural beats are rhythmic audio pulses that can entrain brainwave activity. "
                     "In rare cases, rhythmic stimulation of this kind may trigger seizures in people with photosensitive or audiogenic epilepsy — similar to the caution on flashing lights. \n\n"
                     "For pacemakers: while the audio itself poses no electrical risk, "
                     "the deep relaxation and slowed breathing binaural beats can induce may be inadvisable for some cardiac conditions. \n\n"
                     "If in doubt, leave this set to None — the ASMR and hypnotic effects work perfectly well without it.")
