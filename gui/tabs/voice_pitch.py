import tkinter as tk

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from gui.theme import ToolTip

from gui.theme import FONT_TINY

from .process import _make_scrollable_tab


class VoicePitchTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = _make_scrollable_tab(notebook, "Voice & Pitch")

        self.voice_pitch_var = tk.StringVar(value=self._config.get("voice_pitch", "original"))
        self.pitch_wobble_var = tk.StringVar(value=self._config.get("pitch_wobble", "none"))

        vpf = _tk_ttk.LabelFrame(tab, text="Voice Pitch", padding=10)
        vpf.grid(sticky="ew", padx=14, pady=(14, 6))
        ToolTip(vpf, text="Changes how deep or high the voice sounds. Duration stays the same — audio length is unaffected.")

        for text, val in [
            ("Original (no change)", "original"),
            ("Slightly deeper",      "slightly_deeper"),
            ("Much deeper",          "much_deeper"),
            ("Slightly higher",      "slightly_higher"),
        ]:
            ttk.Radiobutton(vpf, text=text, variable=self.voice_pitch_var,
                            value=val, bootstyle="primary",
                            command=self._app.on_setting_changed).pack(anchor="w", pady=2)

        pwf = _tk_ttk.LabelFrame(tab, text="Pitch Wobble", padding=10)
        pwf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(pwf, text="Adds a slow, gentle wavering to the pitch. Creates a dreamy, hypnotic quality.")

        WOBBLE_OPTIONS = [
            ("None",        "none",        None),
            ("Subtle",      "subtle",      "Very slow pitch drift — one full cycle every ~10 seconds, barely perceptible depth. Listen to a clip of at least 20 seconds to hear it clearly."),
            ("Noticeable",  "noticeable",  "Twice as fast and twice as deep as Subtle — one cycle every ~5 seconds. Clearly audible on headphones."),
            ("Deep Trance", "deep_trance", "Slower than Noticeable but near-maximum depth — voice sinks and rises like it's being pulled underwater. Dissociative and highly hypnotic."),
            ("Eerie",       "eerie",       "Fast wobble at high depth — crosses into tremolo/warble territory. The voice sounds glitched, warped, or wrong. Suits horror ASMR, dark hypnosis, and surreal content."),
        ]
        for text, val, tip in WOBBLE_OPTIONS:
            rb = ttk.Radiobutton(pwf, text=text, variable=self.pitch_wobble_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            if tip:
                ToolTip(rb, text=tip)

        ttk.Label(pwf, text="Relaxing Hypnosis defaults to Subtle wobble; Deep Mesmerization defaults to Noticeable. Setting either option above overrides the preset.",
                  font=FONT_TINY, bootstyle="secondary").pack(anchor="w", pady=(6, 0))

        self.tempo_var = tk.StringVar(value=self._config.get("tempo", "none"))

        tf = _tk_ttk.LabelFrame(tab, text="Tempo Change", padding=10)
        tf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(tf, text="Speeds up or slows down the audio without changing the pitch. Good for adjusting pacing.")

        for text, val in [
            ("None",           "none"),
            ("Faster lightly", "faster_light"),
            ("Faster heavily", "faster_heavy"),
            ("Slower lightly", "slower_light"),
            ("Slower heavily", "slower_heavy"),
        ]:
            ttk.Radiobutton(tf, text=text, variable=self.tempo_var,
                            value=val, bootstyle="primary",
                            command=self._app.on_setting_changed).pack(anchor="w", pady=2)
