# QMK ↔ ZMK Alignment Plan

Goal: bring QMK behavior in line with the ZMK gold standard (Flow Tap already confirmed working). Focus areas: LT flavor, generic MT flavor, HRM tuning, hand detection, combos, macro robustness, and layout parity.

- **Layer-tap flavor to “balanced”**  
  - Remove the global `PERMISSIVE_HOLD` bias from layer taps in `qmk/users/dario/config.h` (or gate it behind per-key logic).  
  - Keep `HOLD_ON_OTHER_KEY_PRESS_PER_KEY` enabled. In `qmk/users/dario/dario.c`, make `get_hold_on_other_key_press()` return true only for keys you explicitly want hold-preferred (Tab/Del), leaving LTs neutral to approximate ZMK’s balanced flavor plus hold-on-release.  
  - Verify LT tap/hold feel on all boards.

- **Generic mod-taps to hold-preferred where ZMK uses `&mt`**  
  - Keep Tab/Del as hold-preferred; extend per-key handling if any other `&mt` mappings are added.  
  - Ensure other mod-taps ride the neutral path (no global permissive hold) so they are not more hold-eager than ZMK.

- **HRM timing parity**  
  - Add `get_quick_tap_term()` in `qmk/users/dario/dario.c` to return 175 ms for all HRM keycodes; leave 200 ms default elsewhere.  
  - Keep existing HRM tap term 280 ms and Flow Tap idle guard (150 ms) as-is.  
  - Check for any HRM keycode drift if layouts change.

- **Opposite-hand and thumb detection parity**  
  - Keep the column-split heuristic in `get_chordal_hold()` as the default.  
  - Add explicit thumb overrides (by keycode) so thumb keys are never penalized—matches ZMK’s thumb exemptions.  
  - Optionally add per-board key-position overrides if a given matrix needs finer control (e.g., a future asymmetric layout), but not required for current boards.

- **Combo idle guard**  
  - Track the timestamp of the last non-combo keypress. In `combo_should_trigger()`, block DFU (and any sensitive) combos unless `timer_elapsed32(last_keypress_ms) >= 150`.  
  - Leave `COMBO_TERM=100` unchanged.  
  - Optionally make the idle guard opt-in per combo for future flexibility.

- **Macro robustness**  
  - Replace `SEND_STRING` for `MACRO_GITHUB_URL` with a helper that iterates a PROGMEM string and uses `tap_code_delay(… , 10)` per character to mirror ZMK’s 10 ms waits and avoid dropped characters.  
  - Keep the string in one place to avoid drift with ZMK’s macro text.

- **Layer-tap vs mod-tap bias sanity**  
  - After the above, confirm: layer taps are neutral/balanced, HRMs are balanced with 175 quick-tap + idle guard, and only the intended `&mt` keys (Tab/Del) are hold-preferred.  
  - Adjust per-key overrides if any new thumb mod-taps are added later.

- **Corne QMK layout parity (optional but recommended)**  
  - Regenerate `qmk/keyboards/crkbd/rev1/keymaps/dario/keymap.c` from `config/keymap.yaml` so its layers match the ZMK baseline. This removes behavioral drift stemming from mismatched key placement.

Validation checklist:
- HRM taps register reliably with fast double taps (175 ms quick-tap) and do not mis-hold during rolls (Flow Tap + cross-hand lists).  
- Layer-taps no longer over-hold relative to ZMK.  
- DFU combo requires idle time like ZMK; no false positives during fast rolls.  
- GitHub macro types cleanly end-to-end.  
- Corne keymap matches the unified layout if regenerated.
