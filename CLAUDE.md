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
