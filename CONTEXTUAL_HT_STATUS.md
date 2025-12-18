# Contextual Hold-Tap Module Status

## Problem to solve
Add a contextual hold-tap behavior for ZMK that switches flavor based on the most recent emitted keycode (e.g., whitespace → hold-preferred) with a timeout window, exposed as an out-of-tree module (`dario,behavior-contextual-hold-tap`). Must work without forking ZMK and be usable in existing keymaps (e.g., Magic mod-tap).

## Solution approach
- Implemented a new behavior module in `zmk/config/modules/dario/contextual-hold-tap`:
  - Behavior C (`contextual_hold_tap.c`):
    - On keydown, snapshots `selected_flavor` based on last emitted non-mod keycode and age:
      - If `now - last_key_time <= prior-timeout-ms` and `last_keycode ∈ prior-keycodes` → `after-flavor` else `normal-flavor`.
      - Defaults: `prior-keycodes = <SPACE>`, `prior-timeout-ms = 300`, `normal-flavor = balanced`, `after-flavor = hold-preferred`.
    - Uses upstream hold-tap state machine patterns:
      - Captures `position_state_changed`/`keycode_state_changed` events while undecided.
      - Respects quick-tap (`quick-tap-ms` / `require-prior-idle-ms`), retro-tap, hold-trigger-on-release, positional hold-trigger key positions.
      - Uses arrays for `tap-bindings` and `hold-bindings` (invoked in order).
      - Flavors supported: `balanced`, `tap-preferred`, `hold-preferred` (no TUI).
    - Work timer and captured event release mirror upstream behavior; maintains `last_tapped` to honor quick-tap/idle logic.
    - Split: relies on ZMK event propagation (no extra sync); tracks last key by keycode, not position; ignores modifier-only keycodes in the tracker.
  - Listener (`contextual_hold_tap_listener.c`): tracks last non-mod keycode + timestamp.
  - Binding YAML: `dario,behavior-contextual-hold-tap.yaml` with defaults (balanced→hold-preferred after SPACE within 300ms, tapping-term 200ms, quick-tap 0).
  - Kconfig/CMake/module.yml with `dts_root` settings and optional debug logging.
  - README with usage snippet and property list.
  - Debug logging (optional via `CONFIG_DARIO_CONTEXTUAL_HT_LOG`): logs last key, age, and selected flavor at press; logs decisions and captured event releases.
- Integrated into keymaps:
  - Added `cht_ak_primary`/`cht_ak_alt` behaviors (tap=adaptive key, hold=Shift) and replaced Magic mod-taps in `corne_dario` and `corneish_zen_dario`.
- Build script changes (`zmk/build_zmk.sh`):
  - Copies `config/modules` into the container.
  - Passes `-DZMK_EXTRA_MODULES` list to CMake; avoids overriding west manifest path to prevent board discovery issues.
  - Added `BOARD_ROOT=/workspaces/zmk/app` in the build command to ensure board defs are found.

## Current status / debugging
- Firmware build still failing at DTS stage: “binding controller … lacks binding” (first contextual HT, later adaptive-key guard nodes), meaning the custom bindings directory is not on the `bindings-dirs` list used by `gen_defines.py`.
- `bindings-dirs` observed in the log: `/workspaces/zmk/app/module/dts/bindings;/workspaces/zmk/app/dts/bindings;/workspaces/zmk/zephyr/dts/bindings` — missing `/tmp/zmk-config/modules/dario/contextual-hold-tap/dts/bindings` (and conditional-layers).
- CMake cache shows `ZMK_EXTRA_MODULES=/tmp/zmk-config/modules/dario/contextual-hold-tap;/tmp/zmk-config/modules/zmk/conditional-layers`, but Zephyr’s module discovery isn’t adding their bindings.
- Environment inside devcontainer does not show `ZEPHYR_EXTRA_MODULES`; we rely on the app `CMakeLists.txt` reading `ZMK_EXTRA_MODULES` into `ZEPHYR_EXTRA_MODULES`, but `gen_defines` still omits the paths.
- Board discovery is now fine (BOARD_ROOT added; board overlays found), but binding discovery for extra modules is not.

## Next debugging steps (planned)
1. Add contextual HT and conditional-layers as projects in `config/west.yml` (preferred, robust), then `west update` in the container to let Zephyr discover bindings normally.
2. If staying with `ZMK_EXTRA_MODULES`, ensure `ZEPHYR_EXTRA_MODULES` is set in CMake (or env) so `gen_defines` receives the bindings directories; verify by inspecting `zephyr_modules.txt` in the build dir.
3. As a quick check, run inside devcontainer: `ZEPHYR_EXTRA_MODULES="/tmp/zmk-config/modules/dario/contextual-hold-tap;/tmp/zmk-config/modules/zmk/conditional-layers;/workspaces/zmk/app/module;/workspaces/zmk/app/keymap-module" west build ...` to confirm bindings appear.

## Files of interest
- Module: `zmk/config/modules/dario/contextual-hold-tap/` (src, dts/bindings, Kconfig, CMakeLists.txt, zephyr/module.yml, README.md).
- Keymaps using the behavior: `zmk/keymaps/corne_dario/corne.keymap`, `zmk/keymaps/corneish_zen_dario/corneish_zen.keymap`.
- Build helper: `zmk/build_zmk.sh`.
- Notes: `contextual-hold-tap-notes.md`.
