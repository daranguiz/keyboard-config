# Contextual Hold-Tap module notes

## Decisions / clarifications
- Behavior name: contextual hold tap, vendor prefix `dario`.
- Flavors supported: `balanced`, `tap-preferred`, `hold-preferred`.
- Prior key tracking: ignore modifier-only keycodes.
- Split handling: treat as monoboard; rely on keycode events being shared.
- Defaults: `prior-keycodes = <SPACE>`, `prior-timeout-ms = 300`, `tapping-term-ms = 200`, `quick-tap-ms = 0`.
- Debug logging: add toggleable Kconfig option.

## Plan
1) Implement module: behavior, listener for last keycode/time, devicetree binding, Kconfig/CMake/module.yml. *(done)*
2) Documentation and usage: README/snippet and ensure config wiring supports use. *(done)*

## Progress log
- Reviewed repo layout and ZMK source (hold-tap behavior and binding) to mirror semantics.
- Implemented contextual hold-tap module (`zmk/config/modules/dario/contextual-hold-tap`), listener, binding YAML, Kconfig, CMake/module.yml, and README.
- Updated build script to copy modules and set `ZMK_EXTRA_MODULES` automatically when modules are present.
- Added usage example and property list to the module README.
- Swapped magic mod-taps in `zmk/keymaps/corne_dario/corne.keymap` and `zmk/keymaps/corneish_zen_dario/corneish_zen.keymap` to new contextual HT behaviors (`cht_ak_primary` / `cht_ak_alt`) with whitespace-triggered hold-preferred flavor.
- Build attempt still failing because devicetree binding lookup can't see the contextual HT binding (modules' bindings dirs not in the generated list yet); need to sort out module discovery (ZEPHYR_EXTRA_MODULES handling) before firmware builds.
