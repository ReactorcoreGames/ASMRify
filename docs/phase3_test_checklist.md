# Phase 3 Test Checklist

---

## Pitch Wobble
- [x] Process a file with **Relaxing Hypnosis** preset — confirm audible slow wavering (subtle wobble applied automatically)
- [x] Process a file with **Deep Mesmerization** preset — confirm more pronounced wavering (noticeable wobble applied automatically)
- [x] Set wobble to **Subtle** on Soft-Spoken ASMR — confirm wobble is audible (preset doesn't default to it, so this is a pure GUI override)
- [x] Set wobble to **Noticeable** on Soft-Spoken ASMR — confirm the pitch wavering is clearly more pronounced than Subtle (listen for ~10–20 seconds to catch a full cycle)

## Panning
- [x] **None/Center** — process any file, open in a stereo editor, confirm slight width (not perfectly mono)
- [x] **Gentle L/R drift** — listen on headphones, confirm smooth slow side-to-side movement, no sudden jumps
- [x] **Smooth rotational swirl** — headphones, confirm continuous circular movement
- [x] **Dynamic swirl** — headphones on a voice clip with varied loudness, confirm movement speeds up on louder sections
- [x] Try each cooldown mode (Slow / Moderate / Quick) with Smooth Swirl and confirm noticeably different speeds
- [x] **Intensity-based cooldown** — confirm it processes without errors

## Binaural
- [x] Enable **Alpha** — headphones, confirm faint tone, output not clipped
- [x] Enable **Theta** — headphones, confirm different (lower) tone than Alpha
- [x] Enable **Gamma** — headphones, confirm noticeably higher-frequency pulse than Theta
- [x] Enable **Theta→Delta ramp** — confirm output file duration matches input (no truncation), tone gradually deepens over full length
- [x] Enable binaural with **None/Center panning + noise layer simultaneously** — confirm all three sidechains compose without error

## Combination stress tests
- [x] All effects on at once: Deep Mesmerization + Noticeable wobble + Dynamic swirl + Brown noise + Binaural Theta→Delta — confirm it completes without FFmpeg errors
- [x] Run a batch of 3–5 files with the above settings — confirm no temp file leaks in `%TEMP%` after completion
- [x] Stop mid-batch — confirm stop is clean and no temp files are left behind

## Preset value labels
- [x] Toggle "Show preset values" in Settings — confirm labels appear/disappear on the Main Preset tab
- [x] Confirm the setting persists after restarting the app

## Regression (Phase 2 still works)
- [x] **Soft-Spoken ASMR** with all addons set to their defaults (no wobble, no panning, no binaural) — confirm output is identical in character to Phase 2
- [x] **WAV + MP3 both** output format — confirm both files appear in the output folder
