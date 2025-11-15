# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

Build all configured keyboards with visualization generation:
```bash
./build_all.sh
```

Build all keyboards without visualization:
```bash
qmk userspace-compile
```

Build a specific keyboard:
```bash
# Bastard Keyboards Skeletyl
qmk compile -kb bastardkb/skeletyl/promicro -km dario

# Boardsource Lulu (RP2040)
qmk compile -kb boardsource/lulu/rp2040 -km dario

# Lily58
qmk compile -kb lily58/rev1 -km dario
```

Alternatively, use make:
```bash
make bastardkb/skeletyl/promicro:dario
make boardsource/lulu/rp2040:dario
make lily58/rev1:dario
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
- **`dario.c`**: Custom keycode processing (currently minimal)
- **`config.h`**: Shared QMK settings (now migrated to `qmk/config/global/config.h`)
- **`rules.mk`**: Shared feature flags (now migrated to `qmk/config/global/rules.mk`)

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

### Tapping Term Configuration
- Base tapping term: 200ms
- Home row mods tapping term: 300ms (TAPPING_TERM_HRM)
- Uses `TAPPING_TERM_PER_KEY` for fine-grained control
- Chordal hold enabled with PERMISSIVE_HOLD

### Important QMK Features in Use
- `CHORDAL_HOLD`: Opposite hand rule for mod-tap keys
- `TAPPING_FORCE_HOLD`: Enables rapid tap-to-hold transitions
- `LTO_ENABLE`: Link-time optimization for smaller firmware
- `QMK_KEYS_PER_SCAN 4`: Optimized for heavy chording

## Making Changes

**Note**: All changes must comply with the [project constitution](.specify/memory/constitution.md), which defines mandatory principles for upstream modularity, 36-key layout consistency, extension modularity, keyboard inventory transparency, and visual keymap documentation.

### Adding a New Keyboard
1. Add board entry to `config/boards.yaml` with keyboard details (firmware, layout_size, features)
2. If needed, create board-specific config in `qmk/config/boards/<board>.mk` for QMK-specific features
3. If board has extensions, add them to layers in `config/keymap.yaml` under `extensions:`
4. Run `python3 scripts/generate.py` to generate keymap files
5. Add to build targets: `qmk userspace-add -kb <keyboard> -km dario`
6. Build and test: `qmk compile -kb <keyboard> -km dario`

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
│   └── aliases.yaml                  # Firmware-agnostic behavior aliases
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
├── build_all.sh                      # Build all keyboards (sets QMK_USERSPACE, runs generator)
├── qmk.json                          # Build targets
└── *.hex, *.uf2                      # Compiled firmware outputs
```

**Key Points:**
- **QMK userspace root is `qmk/`**: Set `QMK_USERSPACE` to this directory
- **Clear firmware separation**: QMK files in `qmk/`, ZMK files in `zmk/`
- **Unified config in `config/`**: Firmware-agnostic YAML configuration
- **Generated vs Manual**: Generated files are clearly marked with AUTO-GENERATED warnings

## GitHub Actions

Firmware builds automatically on push via `.github/workflows/build_binaries.yaml`. Compiled firmware appears in the Releases tab.

## Active Technologies
- Python 3.11+ (decision: Python over Bash per user direction) + PyYAML 6.0.3 (already installed), pytest (recommended addition for testing) (003-unified-keymap-codegen)
- File-based (YAML configuration files, generated C/header files for QMK, devicetree/keymap files for ZMK) (003-unified-keymap-codegen)

## Recent Changes
- 003-unified-keymap-codegen: Added Python 3.11+ (decision: Python over Bash per user direction) + PyYAML 6.0.3 (already installed), pytest (recommended addition for testing)
