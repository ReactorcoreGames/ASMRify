import tkinter as tk

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from gui.theme import ToolTip

from gui.theme import FONT_SMALL, FONT_TINY

from .process import _make_scrollable_tab


class MainPresetTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = _make_scrollable_tab(notebook, "Main Preset")

        self.main_preset_var = tk.StringVar(value=self._config.get("main_preset", "soft_spoken_asmr"))
        self.intensity_var   = tk.StringVar(value=self._config.get("intensity", "no_change"))

        PRESETS = [
            ("soft_spoken_asmr",   "Soft-Spoken ASMR",
             "Gentle, natural processing. Keeps the voice feeling real and close.",
             "Built-in: highpass f=80, ratio=3:1, +2dB@6kHz  |  No wobble/echo by default",
             "Close, intimate natural voice — like someone quietly talking to you."),
            ("whispered_asmr",     "Whispered ASMR",
             "Crisp highs, tight dynamics. That classic tingly ASMR quality.",
             "Built-in: highpass f=100, ratio=4:1, +8dB@8kHz  |  No wobble/echo by default",
             "Classic ASMR tingles — bright, crisp, and immersive."),
            ("relaxing_hypnosis",  "Relaxing Hypnosis",
             "Dreamy, smooth, softly warped. Makes the listener feel calm and spacious.",
             "Built-in: lowpass f=12kHz, ratio=3.5:1, echo tails, subtle pitch wobble",
             "Calm and floaty — designed to guide the listener into deep relaxation."),
            ("deep_mesmerization", "Deep Mesmerization",
             "Heavy, pervasive, captivating. Designed to hold attention completely.",
             "Built-in: lowpass f=10kHz, ratio=5:1, heavy echo ×2, noticeable pitch wobble",
             "Immersive and commanding — holds attention with rich, layered depth."),
        ]

        ttk.Label(
            tab,
            text="Each preset has its own built-in EQ, compression, echo, and wobble. Everything in the other tabs adds on top.",
            font=FONT_TINY, bootstyle="secondary", wraplength=600,
        ).grid(sticky="ew", padx=14, pady=(10, 2))

        show_vals = self._config.get("show_preset_values", False)
        self.preset_value_labels = []

        for value, title, desc, vals, tooltip in PRESETS:
            card = _tk_ttk.LabelFrame(tab, padding=10)
            card.grid(sticky="ew", padx=14, pady=6)
            card.columnconfigure(1, weight=1)

            rb = ttk.Radiobutton(
                card,
                text=title,
                variable=self.main_preset_var,
                value=value,
                bootstyle="primary",
                command=self._app.on_setting_changed,
            )
            rb.grid(row=0, column=0, columnspan=2, sticky="w")
            ToolTip(rb, text=tooltip)

            ttk.Label(card, text=desc, font=FONT_SMALL, bootstyle="secondary").grid(
                row=1, column=0, columnspan=2, sticky="w", padx=(20, 0))

            val_lbl = ttk.Label(card, text=f"  {vals}", font=FONT_TINY, bootstyle="info")
            val_lbl.grid(row=2, column=0, columnspan=2, sticky="w", padx=(20, 0))
            if not show_vals:
                val_lbl.grid_remove()
            self.preset_value_labels.append(val_lbl)

        intf = _tk_ttk.LabelFrame(tab, text="Overall Effect Intensity", padding=10)
        intf.grid(sticky="ew", padx=14, pady=(4, 6))
        ToolTip(intf, text=(
            "Scales the EQ boost, compressor makeup gain, and echo wetness of the active Main Preset. "
            "Has no effect on pitch, panning, binaural, background noise, warmth, or tempo."
        ))

        for col, (text, val, tip) in enumerate([
            ("No change",   "no_change",   "Preset effects run at their default strengths."),
            ("+Boost light", "boost_light", "EQ, compression, and echo are 60% stronger than default."),
            ("++Boost heavy", "boost_heavy", "EQ, compression, and echo are 150% stronger. Expect a dramatic, wet sound."),
            ("-Reduce light","reduce_light","EQ, compression, and echo are 40% softer. More natural result."),
            ("--Reduce heavy","reduce_heavy","EQ, compression, and echo are 70% softer. Very subtle, near-dry processing."),
        ]):
            rb = ttk.Radiobutton(intf, text=text, variable=self.intensity_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.grid(row=0, column=col, padx=(0, 16), sticky="w")
            ToolTip(rb, text=tip)

        guide_frame = _tk_ttk.LabelFrame(tab, text="Quick Guide", padding=10)
        guide_frame.grid(sticky="ew", padx=14, pady=(4, 14))
        guide_frame.columnconfigure(0, weight=1)

        self._guide_visible = False
        self._guide_toggle_btn = ttk.Button(
            guide_frame,
            text="Show guide ▾",
            bootstyle="link-info",
            command=self._toggle_guide,
        )
        self._guide_toggle_btn.grid(row=0, column=0, sticky="w")

        GUIDE_TEXT = (
            "⚠  This program cannot turn a loud or clearly-spoken recording into a whisper. "
            "If your source audio is energetic, it will stay energetic — the effects layer on top of whatever is already there.\n\n"
            "✦  What it can do: shape tone (EQ, warmth, compression), add space and movement "
            "(stereo panning, ear-to-ear, binaural beats), layer atmosphere (background noise, ambience), "
            "introduce hypnotic texture (echo, pitch wobble, LFO modulation), and control dynamics and tempo. "
            "All tabs work together — the preset sets the base character, everything else builds on it.\n\n"
            "→  For a full breakdown of every effect and how to use them, see guide.md in the program folder."
        )

        self._guide_label = ttk.Label(guide_frame, text=GUIDE_TEXT, font=FONT_TINY, bootstyle="secondary",
                                      justify="left", wraplength=800)
        self._guide_label.grid(row=1, column=0, sticky="w")
        self._guide_label.grid_remove()

    def _toggle_guide(self):
        self._guide_visible = not self._guide_visible
        if self._guide_visible:
            self._guide_label.grid()
            self._guide_toggle_btn.config(text="Hide guide ▴")
        else:
            self._guide_label.grid_remove()
            self._guide_toggle_btn.config(text="Show guide ▾")

    def set_preset_values_visible(self, show: bool):
        for lbl in self.preset_value_labels:
            if show:
                lbl.grid()
            else:
                lbl.grid_remove()
