# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About This Project

This is a QMK External Userspace repository for custom keyboard firmware. It contains keymaps for multiple split ergonomic keyboards using a modular, shared keymap system based on Miryoku principles with Mac-specific clipboard shortcuts.

**IMPORTANT**: For governance principles and mandatory project rules, see [.specify/memory/constitution.md](.specify/memory/constitution.md). This file provides operational guidance; the constitution defines the non-negotiable architectural principles that must be followed.

## Build Commands

### Setup (First Time)
```bash
# From the main qmk_firmware directory (not this repo)
qmk setup

# Point QMK to this userspace (run from within this repo)
qmk config user.overlay_dir="$(realpath .)"
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

#### Core Files in `users/dario/`:
- **`layers.h`**: Central layer definitions as macros (LAYER_BASE, LAYER_NAV, etc.)
  - Defines the canonical 3x5_3 (36-key) layout used across all boards
  - Contains 8 layers: BASE (Colemak), NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON
- **`dario.h`**: Layer enum, shared keycodes, and aliases
  - U_NA, U_NU, U_NP constants for unavailable/unused/non-present keys
  - Mac clipboard shortcuts (U_UND, U_RDO, U_CUT, U_CPY, U_PST)
  - Mouse and RGB control aliases
- **`dario.c`**: Custom keycode processing (currently minimal)
- **`rules.mk`**: Shared feature flags for all keyboards
  - Enables: Bootmagic, Mousekey, NKRO, Split keyboard support, LTO

#### Per-Keyboard Files in `keyboards/*/keymaps/dario/`:
- **`keymap.c`**: Instantiates the layers using keyboard-specific LAYOUT macros
  - Skeletyl/Lulu: Use `LAYOUT_split_3x5_3` directly
  - Lily58: Uses custom `LAYOUT_miryoku` and `LAYOUT_miryoku_with_grv` wrappers to map 36-key layouts to the full Lily58 matrix, includes GAME layer
- **`config.h`**: Keyboard-specific configuration (tapping terms, features)
- **`keymap_config.h`**: Layer definitions and clipboard macro choices
- **`rules.mk`**: Optional keyboard-specific feature overrides

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
1. Create keymap directory: `mkdir -p keyboards/<keyboard>/keymaps/dario`
2. Create `keymap.c` that includes `"keymap_config.h"` (if wrapper needed), `"dario.h"`, and `"layers.h"`
3. Create `keymap_config.h` with `LAYOUT_wrapper` and `LAYOUT_split_3x5_3` macros if keyboard has >36 keys
4. Create `rules.mk` with `USER_NAME := dario` and keyboard-specific features
5. Add to build targets: `qmk userspace-add -kb <keyboard> -km dario`
6. **REQUIRED**: Add ASCII art layer visualizations to keymap documentation (Principle V)

### Modifying the Shared Keymap
- Edit `users/dario/layers.h` to change the 36-key layout
- **CRITICAL**: Changes automatically apply to ALL keyboards that use the layer macros (Principle II)
- **REQUIRED**: Update ASCII art visualizations in all affected keymaps (Principle V)
- Rebuild all keyboards with `qmk userspace-compile` to verify

### Keyboard-Specific Customizations
- Extra keys (number row, extra thumb keys): Define in keyboard's keymap.c
- Keyboard-specific features (OLED, encoders, RGB): Add to keyboard's config.h and rules.mk
- Layout wrappers: Define LAYOUT_* macros in keyboard's config.h (see Lily58 example)

## File Organization
```
qmk_userspace/
├── users/dario/                      # Shared userspace code
│   ├── layers.h                      # Single source of truth for 36-key layouts
│   ├── dario.h                       # Shared constants and layer enums
│   ├── dario.c                       # Custom keycode handlers
│   ├── config.h                      # Shared config
│   └── rules.mk                      # Shared features
├── keyboards/                        # Per-keyboard keymaps
│   ├── bastardkb/skeletyl/keymaps/dario/
│   │   ├── keymap.c                  # Uses LAYOUT_wrapper(LAYER_*)
│   │   ├── keymap_config.h           # LAYOUT_wrapper macro
│   │   └── rules.mk                  # USER_NAME := dario
│   ├── boardsource/lulu/keymaps/dario/
│   │   ├── keymap.c                  # Uses LAYOUT_wrapper(LAYER_*)
│   │   ├── keymap_config.h           # 36→58 key wrapper
│   │   ├── oled.c                    # OLED display implementation
│   │   └── rules.mk                  # OLED_ENABLE, RGB_MATRIX_ENABLE
│   └── lily58/keymaps/dario/
│       ├── keymap.c                  # Uses LAYOUT_wrapper(LAYER_*)
│       ├── keymap_config.h           # 36→58 key wrapper
│       ├── oled.c                    # Luna pet animation
│       ├── oled.h                    # OLED header
│       └── rules.mk                  # OLED_ENABLE, WPM_ENABLE
├── scripts/
│   └── generate_keymap_diagram.sh    # Keymap visualization generator
├── docs/keymaps/                     # Generated keymap SVGs
│   └── *.svg                         # Visualization outputs
├── qmk.json                          # Build targets (managed by qmk CLI)
├── build_all.sh                      # Build all + generate visualizations
├── .keymap-drawer-config.yaml        # Keymap visualization config
└── *.hex, *.uf2                      # Compiled firmware outputs
```

## GitHub Actions

Firmware builds automatically on push via `.github/workflows/build_binaries.yaml`. Compiled firmware appears in the Releases tab.

## Active Technologies
- Python 3.11+ (decision: Python over Bash per user direction) + PyYAML 6.0.3 (already installed), pytest (recommended addition for testing) (003-unified-keymap-codegen)
- File-based (YAML configuration files, generated C/header files for QMK, devicetree/keymap files for ZMK) (003-unified-keymap-codegen)

## Recent Changes
- 003-unified-keymap-codegen: Added Python 3.11+ (decision: Python over Bash per user direction) + PyYAML 6.0.3 (already installed), pytest (recommended addition for testing)
