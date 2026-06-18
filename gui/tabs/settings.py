import webbrowser
import tkinter as tk

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from gui.theme import ToolTip

from gui.theme import FONT_SMALL, FONT_TINY, FONT_BODY

from .process import _make_scrollable_tab


class SettingsTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = _make_scrollable_tab(notebook, "Settings")

        self.output_format_var    = tk.StringVar(value=self._config.get("output_format", "wav"))
        self.normalization_var    = tk.StringVar(value=self._config.get("normalization_mode", "loudness"))
        self.show_preset_vals_var = tk.BooleanVar(value=self._config.get("show_preset_values", False))

        # Output Format
        off = _tk_ttk.LabelFrame(tab, text="Output Format", padding=10)
        off.grid(sticky="ew", padx=14, pady=(14, 6))
        ToolTip(off, text="Choose what file format(s) your processed audio will be saved as.")

        for text, val, tip in [
            ("WAV only",         "wav",  "Lossless quality. Larger file size. Best if you plan to edit or chain the files further."),
            ("MP3 only",         "mp3",  "Compressed. Smaller file size. Good for final listening or sharing."),
            ("Both WAV and MP3", "both", "Saves two copies of each processed file. Takes more space but gives you both options."),
        ]:
            rb = ttk.Radiobutton(off, text=text, variable=self.output_format_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        ttk.Label(off,
                  text="Input files can be any format FFmpeg supports (mp3, wav, flac, ogg, m4a, etc.).\nThey are auto-converted internally — no manual prep needed.",
                  font=FONT_TINY, bootstyle="secondary").pack(anchor="w", pady=(6, 0))

        # Normalization Mode
        normf = _tk_ttk.LabelFrame(tab, text="Normalization Mode", padding=10)
        normf.grid(sticky="ew", padx=14, pady=6)

        for text, val, tip in [
            ("Peak",                "peak",     "Adjusts volume so the loudest moment hits -1 dB. Leaves headroom to avoid clipping on lossy encode."),
            ("Loudness (-16 LUFS)", "loudness", "Normalizes perceived loudness to -16 LUFS. More consistent across files and better for streaming platforms."),
            ("Both",                "both",     "Saves two files: one peak-normalized, one loudness-normalized. The loudnorm file gets a _loudnorm suffix."),
            ("None (raw output)",   "none",     "Skips all normalization. Volume is whatever the effect chain produces — files may be inconsistently loud, and some effect combinations can cause clipping. Use this if you plan to normalize or master the files yourself in a DAW, or for A/B testing effect levels."),
        ]:
            rb = ttk.Radiobutton(normf, text=text, variable=self.normalization_var,
                                 value=val, bootstyle="primary",
                                 command=self._app.on_setting_changed)
            rb.pack(anchor="w", pady=2)
            ToolTip(rb, text=tip)

        # Display
        dispf = _tk_ttk.LabelFrame(tab, text="Display", padding=10)
        dispf.grid(sticky="ew", padx=14, pady=6)

        cb = ttk.Checkbutton(
            dispf,
            text="Show preset values next to each option",
            variable=self.show_preset_vals_var,
            bootstyle="primary",
            command=self._app.on_show_preset_values_changed,
        )
        cb.pack(anchor="w")
        ToolTip(cb, text="When enabled, each preset shows the technical audio parameters it uses, like filter frequencies and compression ratios.")

        # FFmpeg Status
        ffframe = _tk_ttk.LabelFrame(tab, text="FFmpeg Status", padding=10)
        ffframe.grid(sticky="ew", padx=14, pady=6)

        self.ffmpeg_status_label = ttk.Label(ffframe, text="Checking FFmpeg...", font=FONT_BODY)
        self.ffmpeg_status_label.pack(anchor="w")

        btn_ffmpeg = ttk.Button(
            ffframe,
            text="How to install FFmpeg",
            bootstyle="info",
            command=lambda: webbrowser.open("https://reactorcore.itch.io/ffmpeg-to-path-installer"),
        )
        btn_ffmpeg.pack(anchor="w", pady=(6, 0))

        # Program
        pgf = _tk_ttk.LabelFrame(tab, text="Program", padding=10)
        pgf.grid(sticky="ew", padx=14, pady=6)

        ttk.Button(pgf, text="Open Program Folder", bootstyle="secondary",
                   command=self._app.open_program_folder).pack(anchor="w")

        ttk.Label(pgf,
                  text="To reset all settings to defaults, delete config.json from the program folder and restart.",
                  font=FONT_TINY, bootstyle="secondary", wraplength=800).pack(anchor="w", pady=(6, 0))
