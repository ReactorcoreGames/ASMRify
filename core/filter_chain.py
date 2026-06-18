"""
FFmpeg filter string assembler — pure function, no I/O.
"""

from core.presets import (
    MAIN_PRESETS, INTENSITY_TABLES,
    VOICE_PITCH, AMBIENCE, WARMTH, TEMPO,
    WOBBLE_FILTERS,
)


def build_filter_chain(settings: dict) -> str:
    """
    Assemble the FFmpeg -af filter string from settings.

    Covers steps 1–5, 6 (pitch wobble via vibrato), 7 static (center width),
    8, 10, 12.  Dynamic steps 7 (panning sidechain) and 11 (binaural) are
    handled in process_file().

    Returns a comma-joined filter string (never empty).
    """
    preset_key = settings.get("main_preset", "soft_spoken_asmr")
    p = MAIN_PRESETS.get(preset_key, MAIN_PRESETS["soft_spoken_asmr"])

    intensity_key = settings.get("intensity", "no_change")
    preset_table = INTENSITY_TABLES.get(preset_key, INTENSITY_TABLES["soft_spoken_asmr"])
    overrides = preset_table.get(intensity_key, preset_table["no_change"])

    filters = []

    # Step 2 — noise gate
    filters.append(f"agate=threshold={overrides['gate_threshold']}:ratio=4:attack=5:release=100")

    # Step 3 — EQ / filtering
    filters.append(f"highpass=f={p['highpass_f']}")
    if p["lowpass_f"] is not None:
        filters.append(f"lowpass=f={p['lowpass_f']}")
    eq_gain = overrides.get("eq_gain")
    if p["eq_f"] is not None and eq_gain is not None:
        filters.append(
            f"equalizer=f={p['eq_f']}:width_type={p['eq_width_type']}"
            f":width={p['eq_width']}:g={eq_gain}"
        )

    # Step 4 — compression
    filters.append(
        f"acompressor=threshold={overrides['comp_threshold']}dB"
        f":ratio={overrides['comp_ratio']}"
        f":attack={p['comp_attack']}"
        f":release={p['comp_release']}"
        f":makeup={overrides['comp_makeup']}"
    )

    # Step 5 — voice pitch (rubberband)
    vp = VOICE_PITCH.get(settings.get("voice_pitch", "original"), "")
    if vp:
        filters.append(vp)

    # Step 7 static — center / no panning: add slight stereo width
    pan_type = settings.get("panning_type", "none")
    if pan_type == "none":
        filters.append("stereotools=mlev=1:slev=1.15")

    # Step 8 — preset echo taps, then ambience addon
    has_echo = bool(p["echo"])
    if has_echo:
        for i, (in_g, _out_g, _delay, _decay) in enumerate(p["echo"]):
            out_g  = overrides[f"echo{i}_out_gain"]
            delay  = overrides[f"echo{i}_delay_ms"]
            decay  = overrides[f"echo{i}_decay"]
            filters.append(f"aecho={in_g}:{out_g}:{delay}:{decay}")

    amb = AMBIENCE.get(settings.get("ambience", "dry"), "")
    if amb:
        filters.append(amb)

    # Step 10 — warmth / saturation
    warmth = WARMTH.get(settings.get("warmth", "clean"), "")
    if warmth:
        filters.append(warmth)

    # Tempo change (atempo)
    tempo = TEMPO.get(settings.get("tempo", "none"), "")
    if tempo:
        filters.append(tempo)

    # Step 12 — final limiter
    # afade suppresses filter-startup transients; longer fade for boost intensities
    # where the compressor takes more time to settle.
    fade_dur = 0.15 if intensity_key == "boost_heavy" else 0.08 if intensity_key == "boost_light" else 0.05
    filters.append(f"afade=t=in:st=0:d={fade_dur}")
    filters.append("alimiter=level_in=1:level_out=1:limit=1.0:attack=5:release=50")

    # Pitch wobble (vibrato) is NOT added here — it is applied as a separate
    # FFmpeg pass after peak normalisation in process_file(), so the transient
    # from vibrato's startup does not corrupt the peak measurement.

    return ",".join(filters)
