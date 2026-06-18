import os
import sys
import threading
import webbrowser
import tkinter as tk
from pathlib import Path

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from utils.config import load_config, save_config
from utils.ffmpeg_check import check_ffmpeg
from gui.theme import apply_theme, _inject_asmrify_theme, register_inactive_scale_style, PALETTE, FONT_TITLE, FONT_SMALL, FONT_TINY, FONT_HEADING, FONT_BODY

from gui.tabs.process import ProcessTab
from gui.tabs.main_preset import MainPresetTab
from gui.tabs.voice_pitch import VoicePitchTab
from gui.tabs.space_movement import SpaceMovementTab
from gui.tabs.atmosphere import AtmosphereTab
from gui.tabs.binaural import BinauralTab
from gui.tabs.settings import SettingsTab


class ASMRifyApp:
    def __init__(self):
        self.config = load_config()

        _inject_asmrify_theme()
        self.root = ttk.Window(themename="asmrify")
        self.root.title("Easy Audio ASMRifier & Hypnotiser")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        self.root.state("zoomed")

        style = ttk.Style()
        apply_theme(style, root=self.root)
        register_inactive_scale_style(self.root)
        self._apply_dark_titlebar()

        self._apply_icon(self.root)
        self._build_ui()

        self._ffmpeg_version = check_ffmpeg()
        if self._ffmpeg_version is None:
            self._show_ffmpeg_warning()
        self._update_ffmpeg_status()

    # ------------------------------------------------------------------ #
    #  Dark title bar (Windows 11)                                        #
    # ------------------------------------------------------------------ #

    def _apply_dark_titlebar(self):
        if sys.platform != "win32":
            return
        try:
            import ctypes
            # Set AppUserModelID so Windows uses our icon for the taskbar button
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Reactorcore.ASMRify.1"
            )
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            if hwnd == 0:
                hwnd = self.root.winfo_id()
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value), ctypes.sizeof(value),
            )
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  Icon                                                                #
    # ------------------------------------------------------------------ #

    def _apply_icon(self, window):
        icon_paths = [
            Path("assets/icon.ico"),
            Path(__file__).resolve().parent.parent / "assets" / "icon.ico",
            Path(sys.executable).parent / "icon.ico",
            Path.cwd() / "icon.ico",
        ]
        if hasattr(sys, "_MEIPASS"):
            icon_paths.insert(0, Path(sys._MEIPASS) / "icon.ico")
        for p in icon_paths:
            if p.exists():
                try:
                    window.iconbitmap(str(p))
                    return
                except Exception:
                    continue

    # ------------------------------------------------------------------ #
    #  Public helpers called by tab classes                                #
    # ------------------------------------------------------------------ #

    def attach_context_menu(self, entry_widget):
        menu = tk.Menu(entry_widget, tearoff=0)
        menu.add_command(label="Cut",        command=lambda: entry_widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy",       command=lambda: entry_widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste",      command=lambda: entry_widget.event_generate("<<Paste>>"))
        menu.add_command(label="Select All", command=lambda: entry_widget.event_generate("<<SelectAll>>"))

        def _show(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        entry_widget.bind("<Button-3>", _show)

    def save_config(self):
        save_config(self.config)

    def open_program_folder(self):
        if getattr(sys, "frozen", False):
            folder = str(Path(sys.executable).parent)
        else:
            folder = str(Path(__file__).resolve().parent.parent)
        os.startfile(folder)

    def log_append(self, message: str):
        self.process_tab.log_text.configure(state="normal")
        self.process_tab.log_text.insert("end", message + "\n")
        self.process_tab.log_text.see("end")
        self.process_tab.log_text.configure(state="disabled")

    # ------------------------------------------------------------------ #
    #  Start / Stop / Preview                                             #
    # ------------------------------------------------------------------ #

    def on_start(self):
        from core.batch import run_batch, _collect_files

        input_folder = self.config.get("input_folder", "")
        output_folder = self.config.get("output_folder", "")

        if not input_folder or not os.path.isdir(input_folder):
            self.log_append("Error: please select a valid input folder first.")
            return
        if not output_folder:
            self.log_append("Error: please select an output folder first.")
            return

        files = _collect_files(input_folder)
        if not files:
            self.log_append(
                "No audio files found in the selected input folder.\n"
                "Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC, WMA, OPUS."
            )
            return

        self.process_tab.btn_start.config(state="disabled")
        self.process_tab.btn_stop.config(state="normal")
        self.process_tab.progress_bar.config(value=0, maximum=len(files))
        self.process_tab.status_var.set(f"Starting — {len(files)} file(s) to process…")

        self.process_tab.log_text.configure(state="normal")
        self.process_tab.log_text.delete("1.0", "end")
        self.process_tab.log_text.configure(state="disabled")

        self._stop_event = threading.Event()
        settings_snapshot = dict(self.config)

        def _callback(i, total, filename, success, error, eta):
            def _update():
                self.process_tab.progress_bar.config(value=i)
                if success:
                    self.log_append(f"[{i}/{total}] {filename} — done")
                else:
                    self.log_append(f"[{i}/{total}] {filename} — FAILED: {error}")
                eta_str = f"  ETA: {eta:.0f}s" if eta is not None else ""
                self.process_tab.status_var.set(
                    f"Processing {i}/{total}: {filename}{eta_str}"
                )
            self.root.after(0, _update)

        def _run():
            processed, skipped, errors = run_batch(
                input_folder, output_folder, settings_snapshot,
                _callback, self._stop_event,
            )
            def _done():
                self.process_tab.btn_start.config(state="normal")
                self.process_tab.btn_stop.config(state="disabled")
                self.process_tab.progress_bar.config(value=len(files))
                stopped = self._stop_event.is_set()
                if processed == 0 and skipped > 0 and not stopped:
                    summary = "All files failed — see the log below for details."
                else:
                    summary = (
                        f"{'Stopped. ' if stopped else ''}Done — "
                        f"{processed} processed, {skipped} skipped."
                    )
                self.process_tab.status_var.set(summary)
                self.log_append(f"\n{summary}")
                if errors:
                    self.log_append("Failed files:")
                    for e in errors:
                        self.log_append(f"  ⚠ {e}")
            self.root.after(0, _done)

        threading.Thread(target=_run, daemon=True).start()

    def on_stop(self):
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
            self.process_tab.status_var.set("Stopping after current file…")

    def on_preview(self):
        from core.batch import _collect_files, AUDIO_EXTENSIONS
        from core.processor import process_file

        input_folder = self.config.get("input_folder", "")
        output_folder = self.config.get("output_folder", "")

        if not input_folder or not os.path.isdir(input_folder):
            self.log_append("Error: please select a valid input folder first.")
            return
        if not output_folder:
            self.log_append("Error: please select an output folder first.")
            return

        files = _collect_files(input_folder)
        if not files:
            self.log_append(
                "No audio files found in the selected input folder.\n"
                "Supported formats: WAV, MP3, FLAC, OGG, M4A, AAC, WMA, OPUS."
            )
            return

        src = files[0]
        os.makedirs(output_folder, exist_ok=True)
        from core.batch import _PRESET_ABBREV, _NORM_SUFFIX, _unique_path
        preset_key = self.config.get("main_preset", "soft_spoken_asmr")
        norm_mode = self.config.get("normalization_mode", "loudness")
        preset_abbrev = _PRESET_ABBREV.get(preset_key, preset_key[:5])
        norm_suffix = _NORM_SUFFIX.get(norm_mode, norm_mode)
        stem = f"{src.stem}-{preset_abbrev}-{norm_suffix}"
        output_wav = str(_unique_path(Path(output_folder), stem, ".wav"))
        settings_snapshot = dict(self.config)

        self.process_tab.btn_start.config(state="disabled")
        self.process_tab.status_var.set(f"Previewing: {src.name}…")
        self.log_append(f"Preview: processing {src.name}…")

        def _run():
            ok, err = process_file(str(src), output_wav, settings_snapshot)
            def _done():
                self.process_tab.btn_start.config(state="normal")
                if ok:
                    fmt = settings_snapshot.get("output_format", "wav")
                    open_path = output_wav
                    if fmt == "mp3":
                        mp3 = os.path.splitext(output_wav)[0] + ".mp3"
                        if os.path.exists(mp3):
                            open_path = mp3
                    self.process_tab.status_var.set(f"Preview ready: {src.name}")
                    self.log_append(f"Preview done — opening {Path(open_path).name}")
                    os.startfile(open_path)
                else:
                    self.process_tab.status_var.set("Preview failed.")
                    self.log_append(f"Preview failed: {err}")
            self.root.after(0, _done)

        threading.Thread(target=_run, daemon=True).start()

    # ------------------------------------------------------------------ #
    #  UI Build                                                            #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=0)
        self.root.rowconfigure(4, weight=0)
        self.root.columnconfigure(0, weight=1)

        self._build_header()
        ttk.Separator(self.root, orient="horizontal").grid(row=1, column=0, sticky="ew")
        self._build_notebook()
        ttk.Separator(self.root, orient="horizontal").grid(row=3, column=0, sticky="ew")
        self._build_footer()

    def _build_header(self):
        hf = ttk.Frame(self.root, padding=(12, 8))
        hf.grid(row=0, column=0, sticky="ew")

        ttk.Label(hf, text="Easy Audio ASMRifier & Hypnotiser",
                  font=FONT_TITLE, background=PALETTE["bg_base"]).pack(anchor="w")
        ttk.Label(hf, text="Transform your voice clips into ASMR or hypnotic audio",
                  font=FONT_SMALL, bootstyle="secondary",
                  background=PALETTE["bg_base"]).pack(anchor="w")

    def _build_footer(self):
        ff = ttk.Frame(self.root, padding=(8, 4))
        ff.grid(row=4, column=0, sticky="ew")

        ttk.Label(ff, text="Made by Reactorcore", font=FONT_TINY,
                  background=PALETTE["bg_base"]).pack(side="left", padx=(4, 2))
        link = ttk.Label(ff, text="https://linktr.ee/reactorcore",
                         font=FONT_TINY, foreground=PALETTE["accent_soft"],
                         background=PALETTE["bg_base"], cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: webbrowser.open("https://linktr.ee/reactorcore"))

    def _build_notebook(self):
        nb = ttk.Notebook(self.root)
        nb.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)

        self.process_tab        = ProcessTab(nb, self.config, self)
        self.main_preset_tab    = MainPresetTab(nb, self.config, self)
        self.voice_pitch_tab    = VoicePitchTab(nb, self.config, self)
        self.space_movement_tab = SpaceMovementTab(nb, self.config, self)
        self.atmosphere_tab     = AtmosphereTab(nb, self.config, self)
        self.binaural_tab       = BinauralTab(nb, self.config, self)
        self.settings_tab       = SettingsTab(nb, self.config, self)

    # ------------------------------------------------------------------ #
    #  FFmpeg helpers                                                      #
    # ------------------------------------------------------------------ #

    def _update_ffmpeg_status(self):
        lbl = self.settings_tab.ffmpeg_status_label
        if self._ffmpeg_version:
            lbl.config(text=f"FFmpeg found: version {self._ffmpeg_version}", bootstyle="success")
        else:
            lbl.config(text="FFmpeg not found — please install it", bootstyle="danger")

    def _show_ffmpeg_warning(self):
        win = tk.Toplevel(self.root)
        win.title("FFmpeg Not Found")
        win.geometry("460x200")
        win.resizable(False, False)
        win.transient(self.root)
        win.focus_force()
        self._apply_icon(win)

        ttk.Label(win, text="FFmpeg Not Found", font=FONT_HEADING).pack(pady=(18, 4))
        ttk.Label(win,
                  text="FFmpeg is required to process audio files.\n"
                       "Please install it and make sure it is on your system PATH.",
                  font=FONT_BODY, justify="center").pack(pady=4)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Download FFmpeg Installer", bootstyle="primary",
                   command=lambda: webbrowser.open("https://reactorcore.itch.io/ffmpeg-to-path-installer")
                   ).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Close", bootstyle="secondary",
                   command=win.destroy).pack(side="left", padx=6)

    # ------------------------------------------------------------------ #
    #  Settings persistence                                                #
    # ------------------------------------------------------------------ #

    def on_setting_changed(self):
        self.config["main_preset"]      = self.main_preset_tab.main_preset_var.get()
        self.config["voice_pitch"]      = self.voice_pitch_tab.voice_pitch_var.get()
        self.config["pitch_wobble"]     = self.voice_pitch_tab.pitch_wobble_var.get()
        self.config["panning_type"]             = self.space_movement_tab.panning_type_var.get()
        self.config["panning_cooldown"]         = self.space_movement_tab.panning_cooldown_var.get()
        self.config["panning_crossfade"]        = self.space_movement_tab.panning_crossfade_var.get()
        self.config["panning_ear_start_center"] = self.space_movement_tab.panning_ear_start_center_var.get()
        self.config["panning_bias"]             = self.space_movement_tab.panning_bias_var.get()
        self.config["panning_bias_weight_l"]    = self.space_movement_tab.panning_bias_weight_l_var.get()
        self.config["panning_bias_weight_c"]    = self.space_movement_tab.panning_bias_weight_c_var.get()
        self.config["panning_bias_weight_r"]    = self.space_movement_tab.panning_bias_weight_r_var.get()
        self.config["background_noise"]  = self.atmosphere_tab.bg_noise_var.get()
        self.config["background_noise_volume_offset_db"] = self.atmosphere_tab.bg_noise_volume_offset_var.get()
        self.config["noise_pulse"]         = self.atmosphere_tab.noise_pulse_var.get()
        self.config["noise_pulse_organic"] = self.atmosphere_tab.noise_pulse_organic_var.get()
        self.config["ambience"]         = self.atmosphere_tab.ambience_var.get()
        self.config["warmth"]           = self.atmosphere_tab.warmth_var.get()
        self.config["tempo"]            = self.voice_pitch_tab.tempo_var.get()
        self.config["intensity"]        = self.main_preset_tab.intensity_var.get()
        self.config["binaural"]                 = self.binaural_tab.binaural_var.get()
        self.config["binaural_volume_offset_db"] = self.binaural_tab.binaural_volume_offset_var.get()
        self.config["binaural_pulse"]            = self.binaural_tab.binaural_pulse_var.get()
        self.config["binaural_pulse_organic"]    = self.binaural_tab.binaural_pulse_organic_var.get()
        self.config["output_format"]      = self.settings_tab.output_format_var.get()
        self.config["normalization_mode"] = self.settings_tab.normalization_var.get()
        save_config(self.config)

    def on_show_preset_values_changed(self):
        show = self.settings_tab.show_preset_vals_var.get()
        self.config["show_preset_values"] = show
        save_config(self.config)
        self.main_preset_tab.set_preset_values_visible(show)

    # ------------------------------------------------------------------ #
    #  Run                                                                 #
    # ------------------------------------------------------------------ #

    def run(self):
        self.root.mainloop()
