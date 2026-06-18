import os
import tkinter as tk
from pathlib import Path

import ttkbootstrap as ttk
from tkinter import ttk as _tk_ttk
from tkinter import filedialog
from gui.theme import ToolTip

from gui.theme import FONT_SMALL, FONT_BODY, FONT_ENTRY, FONT_MONO, PALETTE
from core.batch import AUDIO_EXTENSIONS


def _make_scrollable_tab(notebook, label):
    outer = ttk.Frame(notebook, style="ScrollInner.TFrame")
    notebook.add(outer, text=label)
    outer.rowconfigure(0, weight=1)
    outer.columnconfigure(0, weight=1)

    canvas = tk.Canvas(outer, highlightthickness=0, background=PALETTE["bg_base"],
                       borderwidth=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    inner = ttk.Frame(canvas, style="ScrollInner.TFrame")
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_frame_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(e):
        canvas.itemconfig(inner_id, width=e.width)

    inner.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)

    def _on_mousewheel(e):
        if inner.winfo_reqheight() > canvas.winfo_height():
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    # Bind on outer (the real tab boundary). Moving between child widgets inside
    # the tab does NOT fire outer's <Leave>, so scrolling stays active everywhere
    # over the tab content, including over cards and radio buttons.
    outer.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    outer.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    inner.columnconfigure(0, weight=1)
    return inner


class ProcessTab:
    def __init__(self, notebook, config, app):
        self._config = config
        self._app = app
        self._build(notebook)

    def _build(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Process")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(3, weight=1)

        # Input folder
        inf = _tk_ttk.LabelFrame(tab, text="Input Folder", padding=10)
        inf.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        inf.columnconfigure(0, weight=1)

        self.input_var = tk.StringVar(value=self._config.get("input_folder", ""))
        input_entry = ttk.Entry(inf, textvariable=self.input_var, state="readonly", font=FONT_ENTRY)
        input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._app.attach_context_menu(input_entry)

        btn_in = ttk.Button(inf, text="Select Input Folder", style="Folder.TButton",
                            command=self._select_input_folder)
        btn_in.grid(row=0, column=1)
        ToolTip(btn_in, text="Choose the folder containing your .wav files to process")

        self._file_count_var = tk.StringVar(value="")
        self._file_count_label = ttk.Label(inf, textvariable=self._file_count_var,
                                           font=FONT_SMALL, bootstyle="secondary")
        self._file_count_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))
        ToolTip(self._file_count_label,
                text="Supported input formats: WAV, MP3, FLAC, OGG, M4A, AAC, WMA, OPUS")

        # Output folder
        outf = _tk_ttk.LabelFrame(tab, text="Output Folder", padding=10)
        outf.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        outf.columnconfigure(0, weight=1)

        self.output_var = tk.StringVar(value=self._config.get("output_folder", ""))
        output_entry = ttk.Entry(outf, textvariable=self.output_var, state="readonly", font=FONT_ENTRY)
        output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._app.attach_context_menu(output_entry)

        btn_out = ttk.Button(outf, text="Select Output Folder", style="Folder.TButton",
                             command=self._select_output_folder)
        btn_out.grid(row=0, column=1, padx=(0, 6))

        btn_open_out = ttk.Button(outf, text="Open Output Folder", bootstyle="secondary",
                                  command=self._open_output_folder)
        btn_open_out.grid(row=0, column=2)
        ToolTip(btn_open_out, text="Open the output folder in File Explorer to access your processed files")

        # Action buttons
        act = ttk.Frame(tab, padding=(10, 6))
        act.grid(row=2, column=0, sticky="ew")

        self.btn_start = ttk.Button(act, text="Start", bootstyle="success", width=20,
                                    command=self._app.on_start)
        self.btn_start.pack(side="left", padx=(0, 6))

        self.btn_stop = ttk.Button(act, text="Stop", bootstyle="danger", width=20,
                                   state="disabled", command=self._app.on_stop)
        self.btn_stop.pack(side="left", padx=(0, 6))

        btn_preview = ttk.Button(act, text="Preview First File", bootstyle="info", width=22,
                                 command=self._app.on_preview)
        btn_preview.pack(side="left")
        ToolTip(btn_preview, text="Processes only the first file in your input folder so you can hear the result before running the full batch")

        # Progress area
        progf = _tk_ttk.LabelFrame(tab, text="Progress", padding=10)
        progf.grid(row=3, column=0, sticky="nsew", padx=10, pady=(4, 10))
        progf.columnconfigure(0, weight=1)
        progf.rowconfigure(0, weight=1)

        self.log_text = tk.Text(progf, state="disabled", height=10, wrap="word",
                                font=FONT_MONO, background=PALETTE["bg_input"],
                                foreground=PALETTE["text_primary"], insertbackground=PALETTE["text_primary"],
                                relief="flat", borderwidth=0)
        self.log_text.grid(row=0, column=0, sticky="nsew")

        log_scroll = ttk.Scrollbar(progf, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(progf, textvariable=self.status_var, font=FONT_BODY).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.progress_bar = ttk.Progressbar(progf, bootstyle="striped", mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 0))

        # Populate file count if folder already saved
        if self._config.get("input_folder"):
            self._refresh_file_count()

    def _refresh_file_count(self):
        folder = self.input_var.get()
        if not folder or not os.path.isdir(folder):
            self._file_count_var.set("")
            return
        count = sum(1 for f in Path(folder).iterdir() if f.suffix.lower() in AUDIO_EXTENSIONS)
        if count == 0:
            self._file_count_var.set("No audio files found")
        elif count == 1:
            self._file_count_var.set("1 audio file found (wav, mp3, flac, ogg, m4a…)")
        else:
            self._file_count_var.set(f"{count} audio files found (wav, mp3, flac, ogg, m4a…)")

    def _select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_var.set(folder)
            self._config["input_folder"] = folder
            self._app.save_config()
            self._refresh_file_count()

    def _select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_var.set(folder)
            self._config["output_folder"] = folder
            self._app.save_config()

    def _open_output_folder(self):
        folder = self.output_var.get()
        if folder and os.path.isdir(folder):
            os.startfile(folder)
