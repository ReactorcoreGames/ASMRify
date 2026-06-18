import tkinter as tk

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from gui.theme import ToolTip

from gui.theme import FONT_TINY, PALETTE

from .process import _make_scrollable_tab


class SpaceMovementTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = _make_scrollable_tab(notebook, "Space & Movement")

        self.panning_type_var         = tk.StringVar(value=self._config.get("panning_type", "none"))
        self.panning_cooldown_var     = tk.StringVar(value=self._config.get("panning_cooldown", "moderate"))
        self.panning_crossfade_var    = tk.StringVar(value=self._config.get("panning_crossfade", "xfade_short"))
        self.panning_ear_start_center_var = tk.BooleanVar(value=self._config.get("panning_ear_start_center", True))
        self.panning_bias_var         = tk.StringVar(value=self._config.get("panning_bias", "bias_equal"))
        self.panning_bias_weight_l_var = tk.IntVar(value=self._config.get("panning_bias_weight_l", 3))
        self.panning_bias_weight_c_var = tk.IntVar(value=self._config.get("panning_bias_weight_c", 1))
        self.panning_bias_weight_r_var = tk.IntVar(value=self._config.get("panning_bias_weight_r", 3))

        stf = _tk_ttk.LabelFrame(tab, text="Spatial Movement", padding=10)
        stf.grid(sticky="ew", padx=14, pady=(14, 6))
        ToolTip(stf, text="Controls how the voice moves between left and right. Use headphones for best effect.")

        for text, val, tip in [
            ("None / Center",            "none",
             "Voice stays centered. A little stereo width is still added."),
            ("Gentle L/R drift",         "gentle_lr",
             "Voice slowly drifts left and right at relaxed intervals."),
            ("Smooth rotational swirl",  "smooth_swirl",
             "Voice continuously rotates in a smooth circular motion."),
            ("Dynamic swirl",            "dynamic_swirl",
             "Movement speed follows the energy of the audio. Active sections move more."),
            ("Ear-to-ear",               "ear_to_ear",
             "Voice alternates between left and right ears. Set crossfade speed below."),
            ("Ear-to-ear + Front",       "ear_to_ear_front",
             "Voice cycles between left, front/center, and right ears in random order."),
        ]:
            rb = ttk.Radiobutton(stf, text=text, variable=self.panning_type_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        tsf = _tk_ttk.LabelFrame(tab, text="Transition Speed", padding=10)
        tsf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(tsf, text="Controls how often the voice changes position. Only applies when any movement type above is selected.")

        for text, val, tip in [
            ("Slow transitions (45–90s)", "slow",
             "Very gradual. Position shifts are rare and barely noticeable."),
            ("Moderate (15–45s)",         "moderate",
             "Comfortable pacing for most ASMR content."),
            ("Quick changes (3–15s)",     "quick",
             "More frequent movement. Better for energetic content."),
            ("Intensity-based (auto)",    "intensity_based",
             "Movement frequency is automatically driven by how loud/active the audio is."),
        ]:
            rb = ttk.Radiobutton(tsf, text=text, variable=self.panning_cooldown_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        ttk.Label(tsf, text="Transitions are always smooth — no sudden jumps.",
                  font=FONT_TINY, bootstyle="secondary").pack(anchor="w", pady=(6, 0))

        csf = _tk_ttk.LabelFrame(tab, text="Ear-to-Ear Crossfade Speed", padding=10)
        csf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(csf, text="How quickly the voice transitions between positions. Applicable only to Ear-to-ear modes.")

        for text, val, tip in [
            ("Snap (0.1s)",   "xfade_snap",
             "Near-instant switch. Very crisp and dramatic."),
            ("Short (0.3s)",  "xfade_short",
             "Quick but smooth transition. Default."),
            ("Smooth (0.8s)", "xfade_smooth",
             "Gradual fade between positions. Relaxing and natural."),
            ("Slow (2.0s)",   "xfade_slow",
             "Very slow glide. Dreamy and hypnotic."),
        ]:
            rb = ttk.Radiobutton(csf, text=text, variable=self.panning_crossfade_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        cb = ttk.Checkbutton(
            csf,
            text="Start from center before first switch",
            variable=self.panning_ear_start_center_var,
            bootstyle="primary",
            command=self._app.on_setting_changed,
        )
        cb.pack(anchor="w", pady=(8, 2))
        ToolTip(cb, text="When checked, the audio opens at center and moves to the first ear after a short hold. "
                         "Uncheck for an immediate jump to the first ear/position at the very start. "
                         "Applies only to Ear-to-ear and Ear-to-ear + Front modes.")

        # ── Position Bias ──────────────────────────────────────────────────────
        pbf = _tk_ttk.LabelFrame(tab, text="Ear-to-Ear + Front Position Bias", padding=10)
        pbf.grid(sticky="ew", padx=14, pady=6)
        ToolTip(pbf, text="Controls how long the voice lingers at each position. Only affects Ear-to-ear + Front mode.")

        for text, val, tip in [
            ("Equal time",    "bias_equal",
             "All three positions (left, front, right) hold for the same amount of time."),
            ("Sides-heavy",   "bias_sides",
             "Left and right ear positions hold twice as long as front/center."),
            ("Center-heavy",  "bias_center",
             "Front/center position holds twice as long as left and right."),
            ("Chaos",         "bias_chaos",
             "Each position gets a random hold weight (range 0.5–5.0) drawn independently per file — "
             "every processed file gets its own character. Sliders show a placeholder and are not used."),
            ("Custom",        "bias_custom",
             "Set your own weight for each position using the sliders below. "
             "Only the ratio between values matters — e.g. 3-1-3 makes the sides linger 3× longer than center. "
             "Setting all three equal (e.g. 5-5-5) is the same as Equal time."),
        ]:
            rb = ttk.Radiobutton(pbf, text=text, variable=self.panning_bias_var,
                                 value=val, bootstyle="primary",
                                 command=self._on_bias_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        # Position weight sliders — always visible; disabled unless Custom is active
        self._bias_sliders = []
        self._bias_val_labels = []
        self._bias_row_labels = []
        sliders_frame = ttk.Frame(pbf)
        sliders_frame.pack(fill="x", pady=(8, 0))

        for label, var, tip in [
            ("Left",   self.panning_bias_weight_l_var,
             "Relative hold weight for the left ear (1–10). Only the ratio between L/C/R matters — "
             "e.g. Left=6, Center=2, Right=6 makes the sides linger 3× longer than center."),
            ("Center", self.panning_bias_weight_c_var,
             "Relative hold weight for front/center (1–10). Only the ratio between L/C/R matters — "
             "e.g. Center=9, Left=3, Right=3 makes center linger 3× longer than the sides."),
            ("Right",  self.panning_bias_weight_r_var,
             "Relative hold weight for the right ear (1–10). Only the ratio between L/C/R matters — "
             "e.g. Right=6, Left=6, Center=2 makes the sides linger 3× longer than center."),
        ]:
            row = ttk.Frame(sliders_frame)
            row.pack(fill="x", pady=3)
            row_lbl = ttk.Label(row, text=f"{label}:", width=7)
            row_lbl.pack(side="left")
            self._bias_row_labels.append(row_lbl)
            val_label = ttk.Label(row, text=str(var.get()), width=3)
            val_label.pack(side="right")
            self._bias_val_labels.append(val_label)

            def _make_cmd(v=var, lbl=val_label):
                def _cmd(value):
                    v.set(int(float(value)))
                    lbl.config(text=str(int(float(value))))
                    self._app.on_setting_changed()
                return _cmd

            sl = ttk.Scale(row, from_=1, to=10, orient="horizontal",
                           variable=var, command=_make_cmd())
            sl.pack(side="left", fill="x", expand=True, padx=(4, 4))
            ToolTip(sl, text=tip)
            self._bias_sliders.append(sl)

        self._sync_bias_sliders()

    def _on_bias_changed(self):
        self._app.on_setting_changed()
        self._sync_bias_sliders()

    _BIAS_PRESET_VALUES = {
        "bias_equal":  (5, 5, 5),
        "bias_sides":  (7, 3, 7),
        "bias_center": (3, 7, 3),
        "bias_chaos":  (5, 5, 5),
    }

    def _sync_bias_sliders(self):
        bias = self.panning_bias_var.get()
        is_custom = bias == "bias_custom"
        fg_active  = PALETTE["text_primary"]
        fg_dim     = PALETTE["text_secondary"]
        for sl in self._bias_sliders:
            sl.configure(
                state="normal" if is_custom else "disabled",
                style="Horizontal.TScale" if is_custom else "Inactive.Horizontal.TScale",
            )
        for lbl in self._bias_row_labels + self._bias_val_labels:
            lbl.configure(foreground=fg_active if is_custom else fg_dim)
        if not is_custom and bias in self._BIAS_PRESET_VALUES:
            l, c, r = self._BIAS_PRESET_VALUES[bias]
            self.panning_bias_weight_l_var.set(l)
            self.panning_bias_weight_c_var.set(c)
            self.panning_bias_weight_r_var.set(r)
            for lbl, val in zip(self._bias_val_labels, [l, c, r]):
                lbl.config(text=str(val))
