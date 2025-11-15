# Unified Keymap Configuration

This directory contains the **single source of truth** for all keyboard keymaps. Edit these files to update keymaps across all keyboards (QMK and ZMK).

## Files

### `keymap.yaml` - Core Keymap Definition
**This is the main file you'll edit most often.**

Defines all layers with a 36-key core layout (3x5_3) plus optional extensions for larger boards.

**Structure:**
```yaml
layers:
  BASE:
    core:  # 36-key layout (required for all layers)
      # Left hand (3x5)
      - [Q, W, F, P, G]
      - [hrm:LGUI:A, hrm:LALT:R, hrm:LCTL:S, hrm:LSFT:T, D]
      - [Z, lt:FUN:X, C, V, B]
      # Right hand (3x5)
      - [J, L, U, Y, QUOT]
      - [H, hrm:RSFT:N, hrm:RCTL:E, hrm:RALT:I, hrm:RGUI:O]
      - [K, M, COMM, DOT, SLSH]
      # Thumbs (3+3)
      - [ENT, lt:NAV:SPC, lt:MEDIA:TAB]
      - [lt:SYM:DEL, LSFT, lt:NUM:BSPC]

    extensions:  # Optional extra keys for larger boards
      3x6_3:  # 42-key boards (Corne)
        outer_pinky_left: [TAB, GRV, CAPS]
        outer_pinky_right: [QUOT, BSLS, ENT]
```

**Keycode Syntax:**
- Simple: `A`, `SPC`, `ENT`, `BSPC`, `LEFT`, `DOWN`, etc.
- Homerow mods: `hrm:LGUI:A` (hold for modifier, tap for key)
- Layer-tap: `lt:NAV:SPC` (hold for layer, tap for key)
- Bluetooth (ZMK only): `bt:next`, `bt:prev`, `bt:clear`
- Special: `NONE` (no key), `QK_BOOT` (bootloader)

### `boards.yaml` - Board Inventory
**Edit this when adding a new keyboard.**

Maps physical keyboards to their firmware type and layout size.

**Structure:**
```yaml
boards:
  skeletyl:
    name: "Bastard Keyboards Skeletyl"
    firmware: qmk
    qmk_keyboard: "bastardkb/skeletyl/promicro"
    layout_size: "3x5_3"  # 36-key base

  lulu:
    name: "Boardsource Lulu (RP2040)"
    firmware: qmk
    qmk_keyboard: "boardsource/lulu/rp2040"
    layout_size: "custom_58"  # Custom 58-key layout
    extra_layers: ["GAME"]  # Board-specific layers
```

**Layout Sizes:**
- `3x5_3` - 36-key (3x5 fingers + 3 thumbs per hand)
- `3x6_3` - 42-key (3x6 fingers + 3 thumbs per hand) - auto-applies `3x6_3` extension
- `custom_*` - Custom layouts (uses board-specific wrappers)

**Note:** Feature flags (OLED, RGB, mousekey, etc.) are **NOT** configured here. They belong in firmware-specific files:
- QMK: `qmk/config/boards/<board>.mk`
- ZMK: `zmk/config/boards/<board>.conf`

### `aliases.yaml` - Behavior Aliases
**Rarely needs editing unless adding custom behaviors.**

Defines firmware-agnostic aliases that translate to QMK/ZMK syntax.

**Example:**
```yaml
behaviors:
  hrm:
    description: "Homerow mod (hold for modifier, tap for key)"
    qmk_pattern: "{mod}_T(KC_{key})"
    zmk_pattern: "&hrm {mod} {key}"
    params: [mod, key]
    firmware_support: [qmk, zmk]

  bt:
    description: "Bluetooth control (ZMK-only)"
    qmk_pattern: "KC_NO"  # Filtered in QMK
    zmk_pattern: "&bt BT_{action}"
    params: [action]
    firmware_support: [zmk]  # ZMK-only
```

## Workflow

### 1. Edit Keymap
```bash
vim config/keymap.yaml
```

### 2. Generate Keymaps
```bash
python3 scripts/generate.py
```

This creates:
- `keyboards/*/keymaps/dario/keymap.c` (QMK - auto-generated, do not edit)
- `zmk/keymaps/*/keymap` (ZMK - auto-generated, do not edit)
- `docs/keymaps/*.svg` (Visual diagrams)

### 3. Build Firmware
```bash
./build_all.sh
```

### 4. Flash to Keyboard
```bash
qmk flash -kb <keyboard> -km dario
```

## Adding a New Keyboard

### Option 1: Manual (Full Control)
1. Add board entry to `config/boards.yaml`
2. Create board-specific config:
   - QMK: `qmk/config/boards/<board>.mk`
   - ZMK: `zmk/config/boards/<board>.conf`
3. If board has extensions, add them to layers in `config/keymap.yaml`
4. Run `python3 scripts/generate.py`
5. Build and test

### Option 2: Helper Script (Quick)
```bash
bash scripts/add_board.sh <board_id> <firmware> <keyboard_path> <layout_size>
```

Example:
```bash
bash scripts/add_board.sh \
  corne \
  zmk \
  corne \
  3x6_3
```

## Key Principles

1. **Core 36-key layout is IDENTICAL across all keyboards**
   - Enforced by code generation
   - Cannot be different between boards

2. **Extensions are per-layer, applied automatically**
   - Based on `layout_size` in `boards.yaml`
   - Only boards with matching size get the extension

3. **Firmware-specific features are automatically filtered**
   - Bluetooth keys (`bt:*`) → ZMK only, filtered to `KC_NO` in QMK
   - QMK-specific keys → filtered to `&none` in ZMK

4. **Generated files are NEVER edited manually**
   - All customization happens in this `config/` directory
   - Generated files have "AUTO-GENERATED - DO NOT EDIT" warnings

## Tips

- **Testing changes:** Use `qmk compile -kb <keyboard> -km dario` to verify generated keymaps compile
- **Debugging:** Check generated files in `keyboards/*/keymaps/dario/keymap.c` to see what was produced
- **Layer count:** Most firmwares support 8-10 layers max
- **Extension conflicts:** If a board doesn't match any extension, it uses the 36-key core only

## Files You Should NEVER Edit

These are auto-generated - your changes will be overwritten:

- `keyboards/*/keymaps/dario/keymap.c`
- `keyboards/*/keymaps/dario/config.h`
- `keyboards/*/keymaps/dario/rules.mk`
- `keyboards/*/keymaps/dario/README.md`
- `zmk/keymaps/*/keymap`
- `docs/keymaps/*.svg`

## Common Tasks

### Change a single key
1. Edit `config/keymap.yaml` - find the layer and position
2. Run `python3 scripts/generate.py`
3. Build with `./build_all.sh`

### Add a new layer
1. Add layer definition to `config/keymap.yaml` (with `core:` and optional `extensions:`)
2. Run `python3 scripts/generate.py`
3. Build and test

### Add number row to larger boards
1. Add extension to layers in `config/keymap.yaml`:
   ```yaml
   extensions:
     3x6_3:
       outer_pinky_left: [1, 2, 3]
       outer_pinky_right: [8, 9, 0]
   ```
2. Ensure board has `layout_size: "3x6_3"` in `boards.yaml`
3. Generate and build

### Create gaming layer (board-specific)
1. Add layer to `config/keymap.yaml` (e.g., `GAME:`)
2. Add layer name to board's `extra_layers` in `boards.yaml`:
   ```yaml
   lulu:
     extra_layers: ["GAME"]
   ```
3. Generate and build - only Lulu will have GAME layer

## Troubleshooting

**Keymap doesn't compile:**
- Check syntax in `config/keymap.yaml` (valid YAML)
- Verify layer names are uppercase (BASE, NAV, not base, nav)
- Check for typos in keycodes

**Extensions not applied:**
- Verify `layout_size` in `boards.yaml` matches extension name
- Check extension exists in layer definition
- Ensure extension keys match expected format (single key vs list)

**Key does the wrong thing:**
- Check keymap.yaml - make sure you're editing the right layer and position
- Remember: row order is [left hand rows, right hand rows, left thumbs, right thumbs]
- Run generator and check generated `keymap.c` to see what was produced

## Further Reading

- Main documentation: `CLAUDE.md` (root of repo)
- Implementation plan: `specs/003-unified-keymap-codegen/plan.md`
- Project constitution: `.specify/memory/constitution.md`
