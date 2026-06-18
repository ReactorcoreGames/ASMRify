"""
Per-file processor — orchestrates the full processing pipeline.
"""

import os
import subprocess
import sys
import tempfile

import numpy as np

from core.filter_chain import build_filter_chain
from core.normalize import peak_normalize, loudness_normalize
from core.presets import (
    BACKGROUND_NOISE_COLORS,
    BACKGROUND_NOISE_BASE_DB, NOISE_PULSE_PRESETS,
    WOBBLE_FILTERS,
)
from core.noise_gen import generate_noise
from core.lfo import generate_pan_envelope_wav, generate_noise_pulse_envelope_wav, generate_binaural_pulse_envelope_wav
from core.binaural import BINAURAL_PRESETS, generate_binaural_filter, generate_binaural_wav
from utils.audio_probe import probe_audio, to_temp_wav

def _startupinfo():
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None


def _probe_amplitude(wav_path: str, sample_rate: int = 44100) -> "np.ndarray | None":
    """
    Read a WAV file and return a normalised float32 amplitude envelope
    (one sample per audio sample).  Returns None on failure.
    Used by dynamic_swirl panning.
    """
    si = _startupinfo()
    try:
        fd, raw_path = tempfile.mkstemp(suffix=".f32")
        os.close(fd)
        result = subprocess.run([
            "ffmpeg", "-i", wav_path,
            "-ac", "1",
            "-ar", str(sample_rate),
            "-f", "f32le",
            "-y", raw_path,
        ], capture_output=True, text=True, startupinfo=si)
        if result.returncode != 0:
            return None
        arr = np.fromfile(raw_path, dtype=np.float32)
        return arr
    except Exception:
        return None
    finally:
        try:
            os.unlink(raw_path)
        except Exception:
            pass


def process_file(
    input_path: str,
    output_wav: str,
    settings: dict,
) -> tuple[bool, str]:
    """
    Process one audio file through the full chain.

    input_path  — source audio (any FFmpeg-compatible format)
    output_wav  — destination WAV path (always written)
    settings    — config dict snapshot

    Also writes an MP3 alongside output_wav when output_format is "mp3" or "both".

    Returns (success, error_string).
    """
    si = _startupinfo()
    tmp_input        = None
    tmp_noise        = None
    tmp_noise_pulse  = None
    tmp_pan          = None
    tmp_binaural     = None
    tmp_bin_pulse    = None

    try:
        # ── Ensure we have a WAV to work from ────────────────────────────────
        src = str(input_path)
        if not src.lower().endswith(".wav"):
            try:
                tmp_input = to_temp_wav(src)
                src = tmp_input
            except RuntimeError as e:
                return False, str(e)

        # Probe for duration (needed for noise/binaural generation)
        info = probe_audio(src)
        if info is None:
            return False, f"Could not read audio from: {input_path}"
        duration = info["duration"]

        # ── Build base filter chain (steps 1–6, 7-static, 8, 10, 12) ────────
        af_chain = build_filter_chain(settings)

        # ── Step 9 — background noise temp file ──────────────────────────────
        noise_key = settings.get("background_noise", "none")
        if noise_key != "none":
            color = BACKGROUND_NOISE_COLORS.get(noise_key, "white")
            fd, tmp_noise = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            try:
                generate_noise(color, duration, 44100, tmp_noise)
            except RuntimeError as e:
                return False, str(e)

            pulse_key = settings.get("noise_pulse", "none")
            pulse_params = NOISE_PULSE_PRESETS.get(pulse_key)
            if pulse_params is not None:
                rate_hz, depth = pulse_params
                fd, tmp_noise_pulse = tempfile.mkstemp(suffix=".f32")
                os.close(fd)
                generate_noise_pulse_envelope_wav(
                    rate_hz, depth, duration, 44100, tmp_noise_pulse,
                    organic=settings.get("noise_pulse_organic", True),
                )

        # ── Step 7 dynamic — panning sidechain ───────────────────────────────
        pan_type = settings.get("panning_type", "none")
        if pan_type != "none":
            amp_array = None
            if pan_type == "dynamic_swirl":
                amp_array = _probe_amplitude(src)

            _xfade_lookup = {
                "xfade_snap":   0.1,
                "xfade_short":  0.3,
                "xfade_smooth": 0.8,
                "xfade_slow":   2.0,
            }
            crossfade_sec = _xfade_lookup.get(
                settings.get("panning_crossfade", "xfade_short"), 0.3
            )

            fd, tmp_pan = tempfile.mkstemp(suffix=".f32")
            os.close(fd)
            wrote = generate_pan_envelope_wav(
                pan_type,
                settings.get("panning_cooldown", "moderate"),
                duration,
                44100,
                amp_array,
                tmp_pan,
                crossfade_sec=crossfade_sec,
                start_center=settings.get("panning_ear_start_center", True),
                bias=settings.get("panning_bias", "bias_equal"),
                weight_l=settings.get("panning_bias_weight_l", 3),
                weight_c=settings.get("panning_bias_weight_c", 1),
                weight_r=settings.get("panning_bias_weight_r", 3),
            )
            if not wrote:
                os.unlink(tmp_pan)
                tmp_pan = None

        # ── Step 11 — binaural layer ──────────────────────────────────────────
        binaural_key = settings.get("binaural", "none")
        binaural_fragment = None  # inline FFmpeg filter fragment (constant presets)
        binaural_vol_offset_db = settings.get("binaural_volume_offset_db", 0)
        binaural_pulse_key = settings.get("binaural_pulse", "none")
        if binaural_key != "none" and binaural_key in BINAURAL_PRESETS:
            frag = generate_binaural_filter(binaural_key, duration, binaural_vol_offset_db)
            if frag is not None:
                binaural_fragment = frag
            else:
                # Ramp preset — needs numpy-generated temp WAV
                fd, tmp_binaural = tempfile.mkstemp(suffix=".f32")
                os.close(fd)
                generate_binaural_wav(binaural_key, duration, 44100, tmp_binaural)

            pulse_params = NOISE_PULSE_PRESETS.get(binaural_pulse_key)
            if pulse_params is not None:
                rate_hz, depth = pulse_params
                fd, tmp_bin_pulse = tempfile.mkstemp(suffix=".f32")
                os.close(fd)
                generate_binaural_pulse_envelope_wav(
                    rate_hz, depth, duration, 44100, tmp_bin_pulse,
                    organic=settings.get("binaural_pulse_organic", True),
                )

        # ── Compose filter_complex — voice chain, panning, noise, binaural ─────
        #
        # Input index allocation:
        #   [0:a] — main audio (src)
        #   [1:a] — pan envelope raw f32 (if tmp_pan)
        #   [N:a] — noise WAV (if noise_key != "none")
        #   [M:a] — binaural raw f32 / inline sine (if binaural)

        fc_parts = [f"[0:a]{af_chain}[voice]"]
        current_label = "[voice]"
        input_idx = 1
        cmd_inputs = ["ffmpeg", "-i", src]

        # ── panning sidechain ─────────────────────────────────────────────────
        if tmp_pan:
            cmd_inputs += ["-f", "f32le", "-ar", "44100", "-ac", "2", "-i", tmp_pan]
            fc_parts += [
                f"[{input_idx}:a]channelsplit=channel_layout=stereo[env_l_raw][env_r_raw]",
                "[env_l_raw]afade=t=in:st=0:d=0.4[env_l]",
                "[env_r_raw]afade=t=in:st=0:d=0.4[env_r]",
                f"{current_label}channelsplit=channel_layout=stereo[aud_l][aud_r]",
                "[aud_l][env_l]amultiply[pan_l]",
                "[aud_r][env_r]amultiply[pan_r]",
                "[pan_l][pan_r]amerge=inputs=2[after_pan]",
            ]
            current_label = "[after_pan]"
            input_idx += 1

        # ── noise mix ─────────────────────────────────────────────────────────
        if tmp_noise:
            base_db = BACKGROUND_NOISE_BASE_DB.get(
                BACKGROUND_NOISE_COLORS.get(noise_key, "white"), -55
            )
            offset_db = settings.get("background_noise_volume_offset_db", 0)
            noise_db = base_db + offset_db
            cmd_inputs += ["-i", tmp_noise]
            fc_parts.append(f"[{input_idx}:a]volume={noise_db}dB[noise_atten]")
            input_idx += 1
            noise_label = "[noise_atten]"

            if tmp_noise_pulse:
                cmd_inputs += ["-f", "f32le", "-ar", "44100", "-ac", "1", "-i", tmp_noise_pulse]
                fc_parts.append(f"[{input_idx}:a]afade=t=in:st=0:d=0.4[noise_pulse_env]")
                fc_parts += [
                    "[noise_pulse_env]asplit=2[npenv_l][npenv_r]",
                    "[noise_atten]channelsplit=channel_layout=stereo[natt_l][natt_r]",
                    "[natt_l][npenv_l]amultiply[npulse_l]",
                    "[natt_r][npenv_r]amultiply[npulse_r]",
                    "[npulse_l][npulse_r]amerge=inputs=2[noise_pulsed]",
                ]
                noise_label = "[noise_pulsed]"
                input_idx += 1

            fc_parts.append(
                f"{current_label}{noise_label}amix=inputs=2:normalize=0:dropout_transition=0[after_noise]"
            )
            current_label = "[after_noise]"

        # ── binaural ──────────────────────────────────────────────────────────
        if binaural_fragment:
            fc_parts.append(binaural_fragment)
            fc_parts.append("[binaural]afade=t=in:st=0:d=0.4[binaural_faded]")
            bin_label = "[binaural_faded]"
            if tmp_bin_pulse:
                cmd_inputs += ["-f", "f32le", "-ar", "44100", "-ac", "1", "-i", tmp_bin_pulse]
                fc_parts.append(f"[{input_idx}:a]afade=t=in:st=0:d=0.4[bin_pulse_env]")
                fc_parts += [
                    "[bin_pulse_env]asplit=2[bpenv_l][bpenv_r]",
                    "[binaural_faded]channelsplit=channel_layout=stereo[bin_l_ch][bin_r_ch]",
                    "[bin_l_ch][bpenv_l]amultiply[binp_l]",
                    "[bin_r_ch][bpenv_r]amultiply[binp_r]",
                    "[binp_l][binp_r]amerge=inputs=2[binaural_pulsed]",
                ]
                bin_label = "[binaural_pulsed]"
                input_idx += 1
            fc_parts.append(
                f"{current_label}{bin_label}amix=inputs=2:normalize=0:dropout_transition=0[after_bin]"
            )
            current_label = "[after_bin]"
        elif tmp_binaural:
            cmd_inputs += ["-f", "f32le", "-ar", "44100", "-ac", "2", "-i", tmp_binaural]
            p_bin = BINAURAL_PRESETS[binaural_key]
            vol_db = p_bin["volume_db"] + binaural_vol_offset_db
            fc_parts.append(
                f"[{input_idx}:a]volume={vol_db}dB,afade=t=in:st=0:d=0.4[bin_sc]"
            )
            input_idx += 1
            bin_label = "[bin_sc]"
            if tmp_bin_pulse:
                cmd_inputs += ["-f", "f32le", "-ar", "44100", "-ac", "1", "-i", tmp_bin_pulse]
                fc_parts.append(f"[{input_idx}:a]afade=t=in:st=0:d=0.4[bin_pulse_env]")
                fc_parts += [
                    "[bin_pulse_env]asplit=2[bpenv_l][bpenv_r]",
                    "[bin_sc]channelsplit=channel_layout=stereo[bin_l_ch][bin_r_ch]",
                    "[bin_l_ch][bpenv_l]amultiply[binp_l]",
                    "[bin_r_ch][bpenv_r]amultiply[binp_r]",
                    "[binp_l][binp_r]amerge=inputs=2[binaural_pulsed]",
                ]
                bin_label = "[binaural_pulsed]"
                input_idx += 1
            fc_parts.append(
                f"{current_label}{bin_label}amix=inputs=2:normalize=0:dropout_transition=0[after_bin]"
            )
            current_label = "[after_bin]"

        # ── assemble and run pass 1 ───────────────────────────────────────────
        trimmed_label = current_label.strip("[]") + "_trimmed"
        fc_parts.append(
            f"{current_label}atrim=start_sample=10,asetpts=PTS-STARTPTS[{trimmed_label}]"
        )

        use_filter_complex = tmp_pan or tmp_noise or binaural_fragment or tmp_binaural or tmp_bin_pulse
        if use_filter_complex:
            cmd = cmd_inputs + [
                "-filter_complex", ";".join(fc_parts),
                "-map", f"[{trimmed_label}]",
                "-y", output_wav,
            ]
        else:
            cmd = ["ffmpeg", "-i", src, "-af", af_chain, "-y", output_wav]

        result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=si)
        if result.returncode != 0:
            detail = result.stderr.strip() or "FFmpeg returned a non-zero exit code with no additional detail."
            return False, f"FFmpeg processing failed:\n{detail}"

        # ── Normalisation ─────────────────────────────────────────────────────
        norm_mode = settings.get("normalization_mode", "peak")
        loudnorm_wav = None

        if norm_mode in ("peak", "both"):
            ok, err = peak_normalize(output_wav, output_wav)
            if not ok:
                return False, err
        elif norm_mode == "loudness":
            ok, err = loudness_normalize(output_wav, output_wav)
            if not ok:
                return False, err

        # ── Pitch wobble (post-normalize) ─────────────────────────────────────
        wobble_key = settings.get("pitch_wobble", "none")
        wobble_filter = WOBBLE_FILTERS.get(wobble_key, "")
        if wobble_filter:
            fd, tmp_wobble_out = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            try:
                wob = subprocess.run([
                    "ffmpeg", "-i", output_wav,
                    "-af", (f"{wobble_filter},"
                            "atrim=start_sample=10,asetpts=PTS-STARTPTS,"
                            "afade=t=in:st=0:d=0.4"),
                    "-y", tmp_wobble_out,
                ], capture_output=True, text=True, startupinfo=si)
                if wob.returncode != 0:
                    return False, f"Pitch wobble pass failed:\n{wob.stderr}"
                os.replace(tmp_wobble_out, output_wav)
            except Exception as e:
                try:
                    os.unlink(tmp_wobble_out)
                except Exception:
                    pass
                return False, f"Pitch wobble pass error: {e}"

        # ── Loudnorm companion (both mode) ────────────────────────────────────
        if norm_mode == "both":
            _base, _ext = os.path.splitext(output_wav)
            loudnorm_wav = _base + "-ld_norm" + _ext
            ok, err = loudness_normalize(output_wav, loudnorm_wav)
            if not ok:
                return False, err

        # ── Output format — re-encode to MP3 if requested ─────────────────────
        fmt = settings.get("output_format", "wav")
        if fmt in ("mp3", "both"):
            mp3_path = os.path.splitext(output_wav)[0] + ".mp3"
            enc = subprocess.run([
                "ffmpeg", "-i", output_wav,
                "-codec:a", "libmp3lame", "-q:a", "2",
                "-y", mp3_path,
            ], capture_output=True, text=True, startupinfo=si)
            if enc.returncode != 0:
                return False, f"MP3 encoding failed:\n{enc.stderr}"
            if fmt == "mp3":
                try:
                    os.unlink(output_wav)
                except Exception:
                    pass

            if loudnorm_wav is not None:
                loudnorm_mp3 = os.path.splitext(loudnorm_wav)[0] + ".mp3"
                enc2 = subprocess.run([
                    "ffmpeg", "-i", loudnorm_wav,
                    "-codec:a", "libmp3lame", "-q:a", "2",
                    "-y", loudnorm_mp3,
                ], capture_output=True, text=True, startupinfo=si)
                if enc2.returncode != 0:
                    return False, f"MP3 encoding (loudnorm) failed:\n{enc2.stderr}"
                if fmt == "mp3":
                    try:
                        os.unlink(loudnorm_wav)
                    except Exception:
                        pass

        return True, ""

    except FileNotFoundError:
        return False, "FFmpeg not found in PATH."
    except Exception as e:
        return False, f"Unexpected error: {e}"
    finally:
        for tmp in (tmp_input, tmp_noise, tmp_noise_pulse, tmp_pan, tmp_binaural, tmp_bin_pulse):
            if tmp:
                try:
                    os.unlink(tmp)
                except Exception:
                    pass
