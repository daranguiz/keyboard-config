# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Principles for Claude

**CRITICAL - Testing and Verification Standards**:
- **A test failure is NEVER success**: If a build fails, a command errors, or a test doesn't run to completion successfully, the task is NOT complete
- **"Verified" means it actually worked**: You cannot claim verification without seeing successful execution and output
- **No assumptions or "probably works"**: If Docker isn't running, the network is down, or a dependency is missing, you MUST report the actual failure - not mark the task as complete
- **Honest reporting required**: Report what actually happened, not what you hoped would happen
- When a test cannot run due to external factors (missing dependencies, services down, etc.), clearly state: "Cannot complete test - [specific blocker]" and leave the task incomplete

**CRITICAL - Local Build Requirements**:
- **ALWAYS support local builds**: Local build capability is MANDATORY for all firmware (QMK, ZMK, etc.)
- **GitHub Actions is NOT a development tool**: CI/CD is for artifacts and automation, NOT for development workflow
- **Follow official tooling**: Use the official dev container approach for each firmware (e.g., ZMK's devcontainer setup)
- **Never suggest "just use GitHub Actions"**: This is never an acceptable answer for local development

**CRITICAL - Documentation Standards**:
- **ALWAYS update README.md**: When adding new keymaps, layouts, boards, or features, you MUST update the README.md to include them
- **Keep documentation in sync**: The README is the user-facing entry point - if a feature exists but isn't documented there, it effectively doesn't exist for users
- **Include visualizations**: When adding new row-stagger layouts or split keyboard keymaps, add the corresponding visualization images to the README

## About This Project

This is a QMK External Userspace repository for custom keyboard firmware. It contains keymaps for multiple split ergonomic keyboards using a **unified keymap code generation system** based on Miryoku principles with Mac-specific clipboard shortcuts.

**IMPORTANT**: For governance principles and mandatory project rules, see [.specify/memory/constitution.md](.specify/memory/constitution.md). This file provides operational guidance; the constitution defines the non-negotiable architectural principles that must be followed.

### Unified Keymap System

The repository uses a code generation approach where all keymaps are defined in a single YAML configuration file ([config/keymap.yaml](config/keymap.yaml)) and automatically generated for each keyboard:

- **Single source of truth**: Edit `config/keymap.yaml` to update all keyboards at once
- **Firmware-agnostic**: Supports both QMK and ZMK from the same config
- **Board-specific extensions**: Larger boards automatically get appropriate extensions
- **Generated files**: `keyboards/*/keymaps/dario/` contains auto-generated code (DO NOT EDIT)

**Workflow**:
1. Edit `config/keymap.yaml` (unified keymap definition)
2. Run `python3 scripts/generate.py` to generate keymaps
3. Build with `./build_all.sh` or `qmk userspace-compile`

### Row-Staggered Keyboard Support (macOS .keylayout)

In addition to split ergonomic keyboards, the repository supports **row-staggered** (traditional) keyboard layouts with macOS `.keylayout` file generation:

- **Separate config directory**: `config/rowstagger/` contains YAML files for row-stagger layouts
- **macOS OS-level remapping**: Generates `.keylayout` XML files that can be installed in macOS
- **Multiple layout support**: Each YAML file generates one `.keylayout` for easy experimentation
- **Auto-generated shift layer**: Shift mappings are automatically inferred from base layer

**Workflow**:
1. Create or edit YAML file in `config/rowstagger/` (e.g., `nightlife.yaml`)
2. Define 3 rows mapping to QWERTY physical positions
3. Run `./build_all.sh` or `python3 scripts/generate.py`
4. Install generated `.keylayout` from `out/keylayout/` to macOS

**Example YAML (config/rowstagger/nightlife.yaml)**:
```yaml
name: "Nightlife"
id: "-12407"
group: "126"

layout:
  # QWERTY positions: q w e r t y u i o p [ ]
  - [f, d, l, g, v, q, r, u, o, ",", "[", "]"]

  # QWERTY positions: a s d f g h j k l ; '
  - [s, t, h, c, y, j, n, e, a, i, "'"]

  # QWERTY positions: z x c v b n m , . /
  - [z, k, m, p, w, x, b, ";", ".", /]
```

**Notes**:
- Only customize alpha keys (3 rows) + brackets `[]`
- Number row stays as QWERTY (1234567890-=)
- All other keys (modifiers, space, enter, etc.) stay standard ANSI
- Shift layer is auto-inferred: letters → uppercase, symbols → shifted (`,` → `<`, `[` → `{`, etc.)
- Each `.keylayout` file appears as a separate keyboard layout in macOS System Preferences → Keyboard → Input Sources

## Build Commands

### Setup (First Time)
```bash
# From the main qmk_firmware directory (not this repo)
qmk setup

# Point QMK to the qmk/ subdirectory (run from within this repo)
qmk config user.overlay_dir="$(realpath qmk)"

# Or use environment variable (recommended for build scripts)
export QMK_USERSPACE="$(realpath qmk)"
```

### Building Firmware

**IMPORTANT**: Due to the unified config system structure, you **MUST** use `build_all.sh` to build firmware. This script sets the required `QMK_USERSPACE` environment variable and ensures the build environment is configured correctly. Running `qmk compile` or `make` directly will fail.

Build all configured keyboards (QMK + ZMK) with visualization generation:
```bash
./build_all.sh
```

This script:
1. Cleans and creates the `out/` directory for build artifacts
2. Sets `QMK_USERSPACE` to the correct path (`qmk/` subdirectory)
3. Runs `python3 scripts/generate.py` to generate all keymaps
4. Builds all QMK keyboards using `qmk compile`
5. Builds all ZMK keyboards using Docker
6. Generates visual keymap diagrams (SVG)
7. Collects all build artifacts in the `out/` directory:
   - `out/qmk/` - QMK firmware files (.hex, .uf2)
   - `out/zmk/` - ZMK firmware files (.uf2)
   - `out/visualizations/` - Keymap visualizations (.svg)

**Do NOT use these commands directly** (they will fail without proper environment setup):
```bash
# ❌ DON'T USE - will fail
qmk userspace-compile
qmk compile -kb bastardkb/skeletyl/promicro -km dario
make bastardkb/skeletyl/promicro:dario
```

If you need to build manually, you must set the environment variable first:
```bash
export QMK_USERSPACE="$(realpath qmk)"
qmk compile -kb bastardkb/skeletyl/promicro -km dario
```

### Managing Build Targets

View current build targets:
```bash
qmk userspace-list
```

Add a new keyboard:
```bash
qmk userspace-add -kb <keyboard> -km <keymap>
```

Remove a keyboard:
```bash
qmk userspace-remove -kb <keyboard> -km <keymap>
```

## Code Architecture

### Modular Keymap System

The codebase uses a **single source of truth** approach for keymap definitions to avoid duplication across keyboards:

#### Core Files in `qmk/users/dario/`:
- **`dario.h`**: Layer enum, shared keycodes, and aliases
  - U_NA, U_NU, U_NP constants for unavailable/unused/non-present keys
  - Mac clipboard shortcuts (U_UND, U_RDO, U_CUT, U_CPY, U_PST)
  - Mouse and RGB control aliases
  - Layer enums exported for generated keymaps
- **`dario.c`**: Custom keycode processing with per-key tapping term function
- **`config.h`**: Shared QMK settings including timeless home row mods configuration
- **`rules.mk`**: Shared feature flags

#### Generated Files in `qmk/keyboards/*/keymaps/dario/` (AUTO-GENERATED - DO NOT EDIT):
- **`keymap.c`**: Auto-generated from `config/keymap.yaml`
  - Uses board-appropriate LAYOUT macros (LAYOUT_split_3x5_3, LAYOUT, etc.)
  - Includes "dario.h" for layer enums and shared constants
  - Contains complete layer definitions for the specific board size
- **`config.h`**: Generated keyboard-specific configuration
- **`rules.mk`**: Generated rules with USER_NAME := dario
- **`README.md`**: Generated documentation with ASCII art visualizations

### Key Design Principles

1. **Home Row Mods**: Modifier keys on home row (LGUI/LALT/LCTL/LSFT on both hands)
2. **Chordal Hold**: Uses QMK's chordal hold feature (opposite hand rule for tap-hold keys)
3. **Layer-Tap Keys**: Thumb keys activate layers while held
4. **Mac-Optimized**: Clipboard shortcuts use Cmd key (LCMD/SCMD)
5. **Colemak Base Layer**: Default alphas layout

### Behavior Syntax

The keymap YAML uses special prefixed syntax for complex key behaviors. These are firmware-agnostic and translate to both QMK and ZMK:

| Syntax | Description | Example | QMK Output | ZMK Output |
|--------|-------------|---------|------------|------------|
| `hrm:MOD:KEY` | Home row mod (tap=key, hold=mod) | `hrm:LGUI:A` | `LGUI_T(KC_A)` | `&hml LGUI A` |
| `mt:MOD:KEY` | Mod-tap (simpler than hrm) | `mt:LSFT:TAB` | `LSFT_T(KC_TAB)` | `&mt LSFT TAB` |
| `lt:LAYER:KEY` | Layer-tap (tap=key, hold=layer) | `lt:NAV:SPC` | `LT(NAV, KC_SPC)` | `&lt NAV SPC` |
| `df:LAYER` | Set default layer | `df:BASE_ALT` | `DF(BASE_ALT)` | `&to BASE_ALT` |
| `sm:BASE:SHIFTED` | Shift-morph (shift produces different key) | `sm:COMM:AT` | Key override | Mod-morph behavior |

**Shift-Morph (`sm:`)**: Overrides what a key produces when shift is held. For example, `sm:COMM:AT` makes the comma key produce `@` when shifted (instead of `<`). This is implemented via QMK's Key Override feature and ZMK's mod-morph behavior.

### Key Position Numbering (Row-Wise)

The codebase uses a **consistent row-wise numbering scheme** for all key positions. This applies to combo definitions, L36 references, and internal data structures.

**36-Key Base Layout (3x5_3):**
```
┌────┬────┬────┬────┬────┐   ┌────┬────┬────┬────┬────┐
│  0 │  1 │  2 │  3 │  4 │   │  5 │  6 │  7 │  8 │  9 │  
├────┼────┼────┼────┼────┤   ├────┼────┼────┼────┼────┤
│ 10 │ 11 │ 12 │ 13 │ 14 │   │ 15 │ 16 │ 17 │ 18 │ 19 │  
├────┼────┼────┼────┼────┤   ├────┼────┼────┼────┼────┤
│ 20 │ 21 │ 22 │ 23 │ 24 │   │ 25 │ 26 │ 27 │ 28 │ 29 │  
└────┴────┼────┼────┼────┤   ├────┼────┼────┼────┴────┘
          │ 30 │ 31 │ 32 │   │ 33 │ 34 │ 35 │            
          └────┴────┴────┘   └────┴────┴────┘
```

**Position Ranges:**
- `0-9`: Top row (0-4 left, 5-9 right)
- `10-19`: Home row (10-14 left, 15-19 right)
- `20-29`: Bottom row (20-24 left, 25-29 right)
- `30-35`: Thumbs (30-32 left, 33-35 right)

**42-Key Extended Layout (3x6_3)** - adds outer pinky columns:
```
┌────┬────┬────┬────┬────┬────┐   ┌────┬────┬────┬────┬────┬────┐
│  0 │  1 │  2 │  3 │  4 │  5 │   │  6 │  7 │  8 │  9 │ 10 │ 11 │
├────┼────┼────┼────┼────┼────┤   ├────┼────┼────┼────┼────┼────┤
│ 12 │ 13 │ 14 │ 15 │ 16 │ 17 │   │ 18 │ 19 │ 20 │ 21 │ 22 │ 23 │
├────┼────┼────┼────┼────┼────┤   ├────┼────┼────┼────┼────┼────┤
│ 24 │ 25 │ 26 │ 27 │ 28 │ 29 │   │ 30 │ 31 │ 32 │ 33 │ 34 │ 35 │
└────┴────┴────┼────┼────┼────┤   ├────┼────┼────┼────┴────┴────┘
               │ 36 │ 37 │ 38 │   │ 39 │ 40 │ 41 │
               └────┴────┴────┘   └────┴────┴────┘
```

**38-Key TOTEM Layout (totem_38)** - 3x5 with single pinky key on bottom row:
```
┌────┬────┬────┬────┬────┐   ┌────┬────┬────┬────┬────┐
│  0 │  1 │  2 │  3 │  4 │   │  5 │  6 │  7 │  8 │  9 │
├────┼────┼────┼────┼────┤   ├────┼────┼────┼────┼────┤
│ 10 │ 11 │ 12 │ 13 │ 14 │   │ 15 │ 16 │ 17 │ 18 │ 19 │
├────┼────┼────┼────┼────┼────┐   ┌────┼────┼────┼────┼────┼────┤
│ 20 │ 21 │ 22 │ 23 │ 24 │ 25 │   │ 26 │ 27 │ 28 │ 29 │ 30 │ 31 │
└────┴────┴────┼────┼────┼────┤   ├────┼────┼────┼────┴────┴────┘
               │ 32 │ 33 │ 34 │   │ 35 │ 36 │ 37 │
               └────┴────┴────┘   └────┴────┴────┘
```

The TOTEM uses the **home row value** (index 1) from the `3x6_3` extension for its pinky keys at positions 20 and 31.

**Architecture:**
```
config/keymap.yaml (row-wise positions)
         │
         ▼
   Python scripts (row-wise internally)
         │
         ▼
   ┌─────┴─────┐
   ▼           ▼
QMK Generator  ZMK Generator
   │           │
   ▼           ▼
Physical       Physical
positions      positions
(LAYOUT_*)     (devicetree)
```

Combo positions in `config/keymap.yaml` use the canonical 36-key row-wise scheme. The generators translate these to each board's physical layout positions at code generation time.

### Layer System

- **BASE**: Colemak with home row mods
- **NAV**: Arrow keys, page up/down, home/end, caps lock
- **MOUSE**: Mouse movement, wheel scrolling, button clicks
- **MEDIA**: Media controls, RGB controls, volume
- **NUM**: Number row, brackets, punctuation (numpad-style on left)
- **SYM**: Symbols layer (shifted number row characters)
- **FUN**: Function keys (F1-F12)
- **BUTTON**: Clipboard shortcuts and mouse buttons on both hands
- **GAME** (Lily58 only): Full QWERTY gaming layer with number row

### Special Keyboard Features

**Lily58**:
- Has 6x4 matrix with extra keys beyond 3x5_3
- Includes OLED display support (`oled.h`)
- GAME layer toggle available on top-right key
- Custom LAYOUT_miryoku wrapper maps 36-key defs to full matrix

**Lulu/Lily58**:
- Have number rows that can be utilized for gaming/special layouts
- Currently number row keys are marked XXX (not used) except in GAME layer

## Configuration Details

### Timeless Home Row Mods Configuration

The firmware implements "timeless home row mods" - a configuration philosophy that minimizes dependency on timing for reliable home row mod operation. This matches the ZMK configuration in `zmk/config/dario_behaviors.dtsi`.

**Tapping Terms**:
- Base tapping term: 200ms (for layer-tap keys)
- Home row mods tapping term: 280ms (TAPPING_TERM_HRM)
- Per-key tapping term via `get_tapping_term()` function in `dario.c`

**Core Features**:
1. **Flow Tap** (150ms): Disables holds during fast typing (equivalent to ZMK's `require-prior-idle-ms`)
   - Prevents accidental mod triggers when typing quickly
   - Only affects alpha keys and space
2. **Speculative Hold**: Applies modifiers immediately on key press for zero-delay mouse interactions
   - Enabled via QMK Community Modules (`getreuer/speculative_hold`)
   - Eliminates lag for Ctrl+click, Shift+click, etc.
3. **Chordal Hold**: Opposite hands rule for tap-hold keys
   - Same-hand rolls don't trigger mods (instant tap settlement)
   - Opposite-hand chords activate holds quickly
4. **Permissive Hold**: Fast chords settle before tapping term
   - Enabled for layer-tap keys to allow quick sequences

**Additional Settings**:
- `TAPPING_FORCE_HOLD`: Enables rapid tap-to-hold transitions
- `LTO_ENABLE`: Link-time optimization for smaller firmware
- `QMK_KEYS_PER_SCAN 4`: Optimized for heavy chording

### QMK Community Modules

The firmware uses QMK Community Modules for advanced features:
- **Speculative Hold**: Located in `qmk_firmware/modules/getreuer/speculative_hold`
- Configured per-keymap via `keymap.json` files
- See https://getreuer.info/posts/keyboards/qmk-community-modules for setup details

### Magic Key Training

Magic training is a learning aid that helps build muscle memory for using the magic (alternate repeat) key instead of typing common bigrams directly.

**How It Works**:
- When you type a key followed by its magic alternate (e.g., `1` then `:` when `"1": ":"` is configured), training outputs `#` instead of the alternate character
- This "punishment" encourages you to use the magic key for these bigrams
- Training only activates for bigrams that have magic mappings defined

**Configuration**:
Training is enabled by default. To disable it, pass `--no-magic-training` to the generator:
```bash
python3 scripts/generate.py --no-magic-training
```

**Implementation Details**:

*QMK*: Training logic is in `qmk/users/dario/magic.c`. It intercepts keypresses via `magic_process_record()` and compares the current key against `magic_training_first_keycode()` to detect direct bigrams.

*ZMK*: Training uses adaptive-key behaviors (`ak_train_*`) that replace magic alternate keys in the keymap. Each training behavior checks if the previous key was a magic trigger; if so, it outputs `#` instead of the normal character.

**Technical Notes**:
- Non-alpha triggers use `strict-modifiers` to prevent base keys (e.g., `COMMA`) from matching shifted variants (e.g., `LT` = Shift+Comma)
- Overlay layers (NUM, SYM, etc.) also get training behaviors applied to magic alternate keys
- Alpha keys don't use strict-modifiers since shifted alphas (capitals) should still trigger the unshifted magic mapping

## Making Changes

**Note**: All changes must comply with the [project constitution](.specify/memory/constitution.md), which defines mandatory principles for upstream modularity, 36-key layout consistency, extension modularity, keyboard inventory transparency, and visual keymap documentation.

### Adding a New Keyboard

**Note**: `config/boards.yaml` is the single source of truth for keyboard inventory (per Constitution Principle IV).

1. Add board entry to `config/boards.yaml` with keyboard details:
   ```yaml
   <board_id>:
     name: "Board Name"
     firmware: qmk  # or zmk
     qmk_keyboard: "manufacturer/board/variant"  # for QMK
     # OR
     zmk_shield: "shield_name"  # for ZMK shields
     zmk_board: "board_name"    # for ZMK integrated boards
     layout_size: "3x5_3"  # or 3x6_3, custom_*, etc.
     extra_layers: []  # optional board-specific layers like GAME
   ```
2. If needed, create board-specific config:
   - **QMK**: `qmk/config/boards/<board_id>.mk` for feature flags
   - **ZMK**: `zmk/config/boards/<board_id>.conf` for ZMK settings
3. If board has extensions, add them to layers in `config/keymap.yaml` under `extensions:`
4. Run `python3 scripts/generate.py` to generate keymap files
5. For QMK boards, add to build targets: `qmk userspace-add -kb <keyboard> -km dario`
6. Build and test with `./build_all.sh`

### Modifying the Shared Keymap
- Edit `config/keymap.yaml` to change layer definitions
- **CRITICAL**: Changes automatically apply to ALL keyboards (Principle II)
- Run `python3 scripts/generate.py` to regenerate all keymaps
- **AUTOMATIC**: ASCII art visualizations are automatically regenerated (Principle V)
- Rebuild all keyboards with `./build_all.sh` or `qmk userspace-compile` to verify

### Keyboard-Specific Customizations
- Extra keys (number row, extra thumb keys): Add extensions in `config/keymap.yaml` under layer `extensions:`
- Keyboard-specific features (OLED, encoders, RGB): Add to `qmk/config/boards/<board>.mk`
- Board-specific layers (like GAME): Define in `config/keymap.yaml` and reference in `config/boards.yaml` under `extra_layers`

### Adding a New Split Keyboard Layout (36-key base)

When adding a new base layer layout (e.g., a new alpha layout like Dusk, Gallium, Night):

1. **Add base layer metadata** in `config/keymap.yaml`:
   ```yaml
   base_layers:
     BASE_NEWLAYOUT:
       display_name: "NEWLAYOUT"
       description: "Description of the layout"
   ```

2. **Define the layer** in `config/keymap.yaml` under `layers:`:
   ```yaml
   BASE_NEWLAYOUT:
     core: # (3x5)
       left:
         - [key1, key2, key3, key4, key5]
         - [hrm:LGUI:key6, hrm:LALT:key7, hrm:LCTL:key8, hrm:LSFT:key9, key10]
         - [key11, key12, key13, key14, key15]
       right:
         - [key16, key17, key18, key19, key20]
         - [key21, hrm:LSFT:key22, hrm:LCTL:key23, hrm:LALT:key24, hrm:LGUI:key25]
         - [key26, key27, key28, key29, key30]
       thumbs:
         - [lt:NUM_NIGHT:BSPC, lt:SYM_NIGHT:MAGIC, mt:LSFT:DEL]
         - [mt:LSFT:TAB, lt:NAV_NIGHT:SPC, lt:MEDIA_NIGHT:ENT]
     extensions:
       3x6_3:
         outer_pinky_left: [NONE, NONE, NONE]
         outer_pinky_right: [NONE, NONE, NONE]
   ```

3. **Add to layer switching** in `MEDIA_NIGHT` layer:
   ```yaml
   MEDIA_NIGHT:
     core:
       left:
         - [df:BASE_NIGHT, df:BASE_GALLIUM, df:BASE_NEWLAYOUT, NONE, NONE]
   ```

4. **Add to combo definitions** for all combos that should work on the new layer:
   ```yaml
   combos:
     - name: dfu_left
       layers: [BASE_NIGHT, BASE_GALLIUM, BASE_NEWLAYOUT]
     - name: dfu_right
       layers: [BASE_NIGHT, BASE_GALLIUM, BASE_NEWLAYOUT]
     - name: github_url
       layers: [BASE_NIGHT, BASE_GALLIUM, BASE_NEWLAYOUT]
   ```

5. **Add magic key configuration** (optional, can start with just symbols):
   ```yaml
   magic_keys:
     BASE_NEWLAYOUT:
       timeout_ms: 0
       mappings:
         " ": THE
         ",": " BUT"
         ".": "/"
       default_repeat: true
   ```

6. **Update QMK layer enum** in `qmk/users/dario/dario.h`:
   ```c
   enum layers {
       BASE_NIGHT,
       BASE_GALLIUM,
       BASE_NEWLAYOUT,  // Add in correct order
       FUN,
       NUM_NIGHT,
       // ... rest of layers
   };
   ```
   **CRITICAL**: The order must match the order in `config/keymap.yaml`

7. **Update custom board configs** (if you have custom layouts like Boaty):
   Add the layer definition to `config/boaty.yaml` (or other board-specific config files):
   ```yaml
   BASE_NEWLAYOUT:
     full_layout: [
       # ... same pattern as other base layers
       L36_0, L36_1, L36_2, ...  # References to 36-key core
     ]
   ```

8. **Build and test**:
   ```bash
   ./build_all.sh
   ```

**Notes**:
- Use existing base layers (like `BASE_NIGHT`) as templates
- Keep home row mods consistent across layouts unless there's a specific reason to change
- Thumb keys typically stay consistent across layouts
- Magic key mappings can be refined over time based on usage
- Visualizations are automatically generated for all base layers

### Adding New Features

When adding new features to the generator, you MUST:

1. **Update tests**: Add test cases to the appropriate test file
   - Unit tests for new syntax/behaviors in `tests/unit/test_*_translator.py`
   - Integration tests for end-to-end generation in `tests/integration/`
   - Update `tests/integration/test_full_keymap_generation.py` if the feature uses production config

2. **Update golden files** if output format changes:
   ```bash
   pytest tests/integration/test_golden_snapshots.py --snapshot-update
   git add tests/fixtures/golden/
   ```

3. **Verify all tests pass**:
   ```bash
   pytest                    # Tier 1 (fast, < 30s)
   pytest --tier2            # Tier 2 (comprehensive, optional locally)
   ```

4. **Update documentation**:
   - Update syntax table in CLAUDE.md if adding new behavior prefix
   - Update README.md if user-facing feature
   - Add test documentation in tests/README.md if needed

**Testing Philosophy**:
- **Tier 1 tests** (< 30s) run on every commit - catch regressions fast
- **Tier 2 tests** (5-15min) run in CI - validate firmware builds
- Golden files catch unintended changes in generated code
- Full-featured keymap test ensures all features work together

## Testing

The project uses a comprehensive tiered testing approach:

### Quick Regression Tests (Tier 1)
```bash
pytest                    # < 30 seconds, runs by default
```

Tier 1 tests include:
- Unit tests for all Python modules
- Integration tests for code generation (no compilation)
- Golden file snapshot comparisons
- Full-featured keymap generation test (validates all real-world features)

### Comprehensive Tests (Tier 2)
```bash
pytest --tier2            # 5-15 minutes, requires QMK/ZMK setup
```

Tier 2 tests include:
- Actual QMK firmware compilation (all boards)
- Actual ZMK firmware compilation (all boards)
- Full build_all.sh pipeline validation

### Coverage Report
```bash
pytest --cov=scripts --cov-report=html
open htmlcov/index.html
```

**Test Organization**:
- `tests/unit/` - Unit tests for individual modules
- `tests/integration/` - Integration tests (codegen without compilation)
- `tests/e2e/` - End-to-end tests (with firmware compilation)
- `tests/fixtures/` - Test data and golden files
- `tests/helpers.py` - Shared test utilities

**Running Specific Tests**:
```bash
# Single test file
pytest tests/unit/test_validator.py -v

# Single test function
pytest tests/unit/test_validator.py::test_production_config_is_valid -v

# Update golden snapshots
pytest tests/integration/test_golden_snapshots.py --snapshot-update
```

## File Organization

### New Architecture (Post-Migration)
```
qmk_userspace/
├── config/                           # ✨ Unified configuration (user-editable)
│   ├── keymap.yaml                   # Single source of truth for all keymaps
│   ├── boards.yaml                   # Board inventory and configuration
│   ├── aliases.yaml                  # Firmware-agnostic behavior aliases
│   └── rowstagger/                   # Row-staggered keyboard layouts (macOS)
│       ├── nightlife.yaml            # Example: "nightlife" layout
│       └── *.yaml                    # Additional custom layouts
│
├── qmk/                              # QMK userspace root (QMK_USERSPACE points here)
│   ├── config/                       # QMK-specific settings (user-editable)
│   │   ├── global/
│   │   │   ├── config.h              # Global QMK settings (chordal hold, tapping)
│   │   │   └── rules.mk              # Global feature flags
│   │   └── boards/
│   │       ├── skeletyl.mk           # Board-specific features
│   │       ├── lulu.mk               # OLED, RGB settings
│   │       └── lily58.mk             # OLED, WPM settings
│   │
│   ├── keyboards/                    # QMK keymaps (AUTO-GENERATED - DO NOT EDIT)
│   │   ├── bastardkb/skeletyl/promicro/keymaps/dario/
│   │   │   ├── keymap.c              # Generated from config/keymap.yaml
│   │   │   ├── config.h              # Generated config
│   │   │   ├── rules.mk              # Generated rules
│   │   │   └── README.md             # Generated documentation
│   │   ├── boardsource/lulu/rp2040/keymaps/dario/
│   │   ├── lily58/rev1/keymaps/dario/
│   │   └── crkbd/rev1/keymaps/dario/
│   │
│   └── users/dario/                  # Shared userspace code (for QMK integration)
│       ├── dario.h                   # Layer enums and shared constants
│       ├── dario.c                   # Custom keycode processing
│       ├── config.h                  # Shared settings
│       └── rules.mk                  # Shared features
│
├── zmk/                              # ZMK firmware files
│   ├── keymaps/                      # ZMK keymaps (AUTO-GENERATED - DO NOT EDIT)
│   │   └── corne_dario/
│   │       ├── corne.keymap          # Generated from config/keymap.yaml
│   │       └── README.md             # Generated documentation
│   └── config/                       # ZMK-specific settings (user-editable)
│       └── boards/                   # Board-specific ZMK settings
│
├── scripts/                          # Code generation and build tools
│   ├── generate.py                   # Main generator (Python)
│   ├── migrate_layers.py             # Migration tool (one-time use)
│   ├── config_parser.py              # YAML parser
│   ├── qmk_generator.py              # QMK code generator
│   ├── qmk_translator.py             # QMK keycode translator
│   ├── zmk_generator.py              # ZMK code generator
│   ├── zmk_translator.py             # ZMK keycode translator
│   ├── layer_compiler.py             # Layer compilation logic
│   └── data_model.py                 # Data structures
│
├── out/                              # Build artifacts (cleaned on each build)
│   ├── qmk/                          # QMK firmware (.hex, .uf2)
│   ├── zmk/                          # ZMK firmware (.uf2)
│   ├── keylayout/                    # macOS .keylayout files (row-stagger)
│   └── visualizations/               # Keymap diagrams (.svg)
│
├── build_all.sh                      # Build all keyboards (sets QMK_USERSPACE, runs generator)
└── qmk.json                          # QMK build targets
```

**Key Points:**
- **QMK userspace root is `qmk/`**: Set `QMK_USERSPACE` to this directory
- **Clear firmware separation**: QMK files in `qmk/`, ZMK files in `zmk/`
- **Unified config in `config/`**: Firmware-agnostic YAML configuration
  - **`config/boards.yaml`**: Single source of truth for keyboard inventory (Constitution Principle IV)
  - **`config/keymap.yaml`**: Single source of truth for keymap definitions
- **Generated vs Manual**: Generated files are clearly marked with AUTO-GENERATED warnings
- **Build artifacts in `out/`**: All firmware and visualizations collected in one place, cleaned on each build

## GitHub Actions

Firmware builds automatically on push via `.github/workflows/build_binaries.yaml`. Compiled firmware appears in the Releases tab.

## Active Technologies
- Python 3.11+ (decision: Python over Bash per user direction) + PyYAML 6.0.3 (already installed), pytest (recommended addition for testing) (003-unified-keymap-codegen)
- File-based (YAML configuration files, generated C/header files for QMK, devicetree/keymap files for ZMK) (003-unified-keymap-codegen)

## Recent Changes
- 003-unified-keymap-codegen: Added Python 3.11+ (decision: Python over Bash per user direction) + PyYAML 6.0.3 (already installed), pytest (recommended addition for testing)
