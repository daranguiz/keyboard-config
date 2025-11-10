# File Structure Contract

**Feature**: 002-keymap-refactor
**Date**: 2025-11-09
**Status**: Phase 1

## Overview

This contract defines the mandatory file structure and naming conventions for the refactored keymap system. All keyboards must adhere to this structure to ensure consistency and maintainability.

---

## Userspace Structure (Shared Code)

**Location**: `users/dario/`

### Required Files

| File | Purpose | Required | Format |
|------|---------|----------|--------|
| `dario.h` | Shared enums, layer names, custom keycodes | ✅ Yes | C header |
| `dario.c` | Shared process_record_user, helper functions | ✅ Yes | C source |
| `layers.h` | Layer content definitions (LAYER_BASE, etc.) | ✅ Yes | C header with macros |
| `mods.c` | Shared mod-tap logic | ⚠️ Optional | C source |
| `rules.mk` | Shared build flags | ✅ Yes | Makefile |
| `config.h` | Shared configuration | ⚠️ Optional | C header |

### File Contracts

#### `dario.h`

**Purpose**: Define layer enums and custom keycodes shared across all keyboards

**Required Content**:
```c
#pragma once
#include QMK_KEYBOARD_H

// Layer definitions
enum layers {
    BASE,
    NAV,
    MOUSE,
    MEDIA,
    NUM,
    SYM,
    FUN,
    BUTTON
};

// Custom keycodes
enum custom_keycodes {
    U_NA = SAFE_RANGE,  // Not available
    U_NU,               // Not used
    U_UND,              // Undo
    U_CUT,              // Cut
    U_CPY,              // Copy
    U_PST,              // Paste
    U_RDO               // Redo
};

// Home row mod aliases
#define HOME_A LGUI_T(KC_A)
#define HOME_R LALT_T(KC_R)
#define HOME_S LCTL_T(KC_S)
#define HOME_T LSFT_T(KC_T)
// ... (right hand mirror)
```

**Constraints**:
- Must use `#pragma once` include guard
- Layer enum must start at 0 (BASE = 0)
- Custom keycodes must start at SAFE_RANGE
- Must include QMK_KEYBOARD_H

---

#### `layers.h`

**Purpose**: Define 36-key layer content as C preprocessor macros

**Required Content**:
```c
#pragma once

// Each layer must be a macro with exactly 36 keycodes
#define LAYER_BASE \
    KC_Q,    KC_W,    KC_F,    KC_P,    KC_G,    \
    KC_J,    KC_L,    KC_U,    KC_Y,    KC_QUOT, \
    HOME_A,  HOME_R,  HOME_S,  HOME_T,  KC_D,    \
    KC_H,    HOME_N,  HOME_E,  HOME_I,  HOME_O,  \
    LT(BUTTON, KC_Z),  ALGR_T(KC_X),  KC_C,   KC_V,   KC_B,    \
    KC_K,    KC_M,    KC_COMM, ALGR_T(KC_DOT), LT(BUTTON, KC_SLSH), \
             LT(MEDIA, KC_ESC), LT(NAV, KC_SPC),  LT(MOUSE, KC_TAB), \
                                LT(SYM, KC_ENT),  LT(NUM, KC_BSPC),  LT(FUN, KC_DEL)

// Repeat for all layers: LAYER_NAV, LAYER_MOUSE, etc.
```

**Constraints**:
- Each LAYER_* macro must expand to exactly 36 comma-separated keycodes
- Formatting: 5 keys per row (left hand), 5 keys per row (right hand), 3 thumb keys per hand
- Must use backslash line continuation for readability
- No trailing comma after last keycode

---

#### `dario.c`

**Purpose**: Implement shared keymap logic

**Required Content**:
```c
#include "dario.h"

// Custom keycode handlers
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case U_UND:
            if (record->event.pressed) {
                SEND_STRING(SS_LCTL("z"));
            }
            return false;
        // ... other custom keycodes
    }
    return true;
}

// Optional: Additional helper functions
```

**Constraints**:
- Must include `dario.h`
- Must define `process_record_user` if custom keycodes are used
- Should use `__attribute__((weak))` for functions intended to be overridable

---

#### `rules.mk`

**Purpose**: Define shared build rules

**Required Content**:
```makefile
# Enable features common to all keyboards
MOUSEKEY_ENABLE = yes
EXTRAKEY_ENABLE = yes

# Add shared source files
SRC += dario.c
SRC += mods.c  # If mods.c exists
```

**Constraints**:
- Must use valid QMK feature flags
- Must add all .c files in userspace to SRC
- Should not enable keyboard-specific features (OLED, RGB, etc.)

---

## Keyboard Keymap Structure

**Location**: `keyboards/<manufacturer>/<model>/keymaps/dario/`

### Required Files

| File | Purpose | Required | Format |
|------|---------|----------|--------|
| `keymap.c` | Keymap array definitions | ✅ Yes | C source |
| `keymap_config.h` | Layout wrapper macro (if needed) | ⚠️ Conditional | C header |
| `config.h` | Keyboard-specific config | ⚠️ Optional | C header |
| `rules.mk` | Keyboard-specific build flags | ✅ Yes | Makefile |
| `README.md` | Keymap documentation with ASCII art | ✅ Yes | Markdown |

### Conditional Requirements

- **`keymap_config.h`**: Required if keyboard has >36 keys (needs wrapper macro)
- **`oled.c`** / **`oled.h`**: Required if OLED_ENABLE = yes in rules.mk
- **`features/`** directory: Optional for modular feature organization

### File Contracts

#### `keymap.c`

**Purpose**: Define keymap arrays using shared layer content

**Required Content**:
```c
#include "keymap_config.h"  // If wrapper macro exists
#include "dario.h"          // From userspace
#include "layers.h"         // From userspace

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [BASE]   = LAYOUT_split_3x5_3(LAYER_BASE),
  [NAV]    = LAYOUT_split_3x5_3(LAYER_NAV),
  [MOUSE]  = LAYOUT_split_3x5_3(LAYER_MOUSE),
  [MEDIA]  = LAYOUT_split_3x5_3(LAYER_MEDIA),
  [NUM]    = LAYOUT_split_3x5_3(LAYER_NUM),
  [SYM]    = LAYOUT_split_3x5_3(LAYER_SYM),
  [FUN]    = LAYOUT_split_3x5_3(LAYER_FUN),
  [BUTTON] = LAYOUT_split_3x5_3(LAYER_BUTTON)
};
```

**Constraints**:
- Must use shared LAYER_* macros from `layers.h`
- Must use `LAYOUT_split_3x5_3` macro (from wrapper or keyboard native)
- Array must be named `keymaps` and marked `PROGMEM`
- All 8 base layers must be defined
- Keyboard-specific extra layers (e.g., GAME) can be added after base layers

---

#### `keymap_config.h` (for 58-key boards)

**Purpose**: Define wrapper macro to map 36-key layout to physical keyboard

**Required Content for Lulu (58-key)**:
```c
#pragma once
#include QMK_KEYBOARD_H

// Map 36-key layout to Lulu's 58-key physical layout
#define LAYOUT_split_3x5_3(\
     K00, K01, K02, K03, K04,    K05, K06, K07, K08, K09,\
     K10, K11, K12, K13, K14,    K15, K16, K17, K18, K19,\
     K20, K21, K22, K23, K24,    K25, K26, K27, K28, K29,\
               K32, K33, K34,    K35, K36, K37           \
)\
LAYOUT(\
XXX, XXX, XXX, XXX, XXX, XXX,    XXX, XXX, XXX, XXX, XXX, XXX,\
XXX, K00, K01, K02, K03, K04,    K05, K06, K07, K08, K09, XXX,\
XXX, K10, K11, K12, K13, K14,    K15, K16, K17, K18, K19, XXX,\
XXX, K20, K21, K22, K23, K24, XXX,    XXX, K25, K26, K27, K28, K29, XXX,\
          XXX, K32, K33, K34,    K35, K36, K37, XXX\
)

// Define XXX for unused positions
#define XXX KC_NO
```

**Constraints**:
- Macro name must be `LAYOUT_split_3x5_3`
- Must accept exactly 36 parameters (K00-K09, K10-K19, K20-K29, K32-K37)
- Must invoke keyboard's native LAYOUT macro
- All 36 parameters must be mapped to physical positions
- Extra positions should use `XXX` (KC_NO) unless assigned to specific keys
- Wrapper must match keyboard's physical layout from info.json

---

#### `rules.mk`

**Purpose**: Enable keyboard-specific features

**Required Content**:
```makefile
# Set userspace name (if keymap name != userspace name)
USER_NAME := dario

# Enable keyboard-specific features
OLED_ENABLE = yes        # For Lulu, Lily58
RGB_MATRIX_ENABLE = no   # Disable if not used

# Add keyboard-specific source files
SRC += oled.c            # If OLED_ENABLE = yes
```

**Constraints**:
- Must set `USER_NAME := dario` to link to userspace
- Feature flags must be valid QMK options
- If OLED_ENABLE = yes, must add oled.c to SRC
- Should not duplicate flags from users/dario/rules.mk

---

#### `README.md`

**Purpose**: Document keymap with ASCII art layer visualizations

**Required Content**:

```markdown
# Dario's Keymap for <Keyboard Name>

## Features

- Core 3x5_3 layout shared across all keyboards
- [List keyboard-specific features: OLED, extra keys, etc.]

## Layers

### BASE Layer (Colemak-DH)

[ASCII art diagram - see Constitution Principle V for format]

### NAV Layer

[ASCII art diagram]

[... repeat for all layers ...]

## Build

```bash
make <keyboard>:dario
```

## Flash

```bash
make <keyboard>:dario:flash
```
```

**Constraints**:
- Must include ASCII art for all layers (per Constitution Principle V)
- ASCII art must follow constitutional format (box-drawing characters)
- Must include build and flash commands
- Should list keyboard-specific features

---

## Visualization Output Structure

**Location**: `docs/keymaps/`

### Generated Files

| File Pattern | Purpose | Generated By |
|--------------|---------|--------------|
| `<keyboard>_dario.svg` | SVG keymap diagram | keymap-drawer |
| `<keyboard>_dario.png` | PNG keymap diagram (optional) | cairosvg |

**Example**:
```
docs/keymaps/
├── boardsource_lulu_rp2040_dario.svg
├── lily58_rev1_dario.svg
└── bastardkb_skeletyl_dario.svg
```

**Constraints**:
- Filename must use underscores (not slashes) for keyboard path
- Must be regenerated when keymap changes
- SVG is required, PNG is optional

---

## Build Scripts Structure

**Location**: Repository root

### Script Naming Convention

| Script | Purpose | Keyboard |
|--------|---------|----------|
| `build_lulu.sh` | Build Lulu firmware | boardsource/lulu/rp2040 |
| `build_lily58.sh` | Build Lily58 firmware | lily58/rev1 |
| `build_skeletyl.sh` | Build Skeletyl firmware | bastardkb/skeletyl |

**Script Template**:
```bash
#!/bin/bash
set -e

KEYBOARD="boardsource/lulu/rp2040"
KEYMAP="dario"

echo "Building $KEYBOARD:$KEYMAP..."
make "$KEYBOARD:$KEYMAP"

echo "Firmware ready: .build/${KEYBOARD/\//_}_${KEYMAP}.uf2"
```

**Constraints**:
- Must be executable (`chmod +x`)
- Must use `set -e` for error handling
- Should echo progress messages
- Keyboard path must match QMK directory structure

---

## Validation Checklist

Before committing changes to a keyboard keymap, verify:

### Shared Code (users/dario/)
- [ ] `layers.h` defines all 8 layers with exactly 36 keycodes each
- [ ] `dario.h` includes all layer enums and custom keycodes
- [ ] `dario.c` implements all custom keycode handlers
- [ ] `rules.mk` adds all .c files to SRC

### Keyboard Keymap
- [ ] Keymap directory is named exactly `dario` (not daranguiz, daranguiz_miryoku, etc.)
- [ ] `keymap.c` includes `dario.h` and `layers.h` from userspace
- [ ] `keymap.c` uses LAYOUT_split_3x5_3 with shared LAYER_* macros
- [ ] `keymap_config.h` exists if keyboard has >36 keys
- [ ] `rules.mk` sets `USER_NAME := dario`
- [ ] `rules.mk` enables correct hardware features
- [ ] `README.md` includes ASCII art for all layers
- [ ] Build command succeeds: `make <keyboard>:dario`

### Visualization
- [ ] Diagram generated: `docs/keymaps/<keyboard>_dario.svg`
- [ ] Diagram accurately represents all layers
- [ ] Custom keycodes display correctly

### Documentation
- [ ] KEYBOARDS.md lists keyboard with correct information
- [ ] Build script created (if new keyboard)
- [ ] Git commit includes all related files together

---

## Migration Guide

For converting existing keymaps to this structure:

### Step 1: Rename Keymap Directory
```bash
cd keyboards/<keyboard>/keymaps
mv daranguiz_miryoku dario  # Or whatever old name was
```

### Step 2: Create/Update `keymap.c`
1. Extract layer arrays from old keymap.c
2. Convert to 36-key format (if needed)
3. Move layer content to `users/dario/layers.h` as LAYER_* macros
4. Update keymap.c to use shared macros

### Step 3: Create Wrapper Macro (if needed)
1. Create `keymap_config.h`
2. Define LAYOUT_split_3x5_3 wrapper
3. Map 36 keys to physical layout

### Step 4: Update rules.mk
1. Add `USER_NAME := dario`
2. Enable keyboard-specific features
3. Add keyboard-specific source files

### Step 5: Create README.md
1. Add ASCII art for all layers
2. Document build commands

### Step 6: Update KEYBOARDS.md
1. Change keymap path to `dario`
2. Update build command

### Step 7: Test
```bash
make clean
make <keyboard>:dario
```

---

## File Structure Summary

```
users/dario/                                          # Shared userspace
├── dario.h                                           # Required: enums, keycodes
├── dario.c                                           # Required: shared logic
├── layers.h                                          # Required: layer content
├── mods.c                                            # Optional: mod-tap logic
├── rules.mk                                          # Required: shared flags
└── config.h                                          # Optional: shared config

keyboards/<manufacturer>/<model>/keymaps/dario/       # Per-keyboard keymap
├── keymap.c                                          # Required: keymap arrays
├── keymap_config.h                                   # Conditional: wrapper macro
├── config.h                                          # Optional: kb-specific config
├── rules.mk                                          # Required: kb-specific flags
├── README.md                                         # Required: documentation
├── oled.c                                            # Conditional: if OLED enabled
└── features/                                         # Optional: modular features

docs/keymaps/                                         # Generated visualizations
├── boardsource_lulu_rp2040_dario.svg
├── lily58_rev1_dario.svg
└── bastardkb_skeletyl_dario.svg

Repository root:
├── build_lulu.sh                                     # Build scripts
├── build_lily58.sh
├── build_skeletyl.sh
└── scripts/
    └── generate_keymap_diagram.sh                    # Visualization script
```

---

## Contract Versioning

**Version**: 1.0.0
**Date**: 2025-11-09

Changes to this contract require:
1. Version bump (major if breaking, minor if additive)
2. Migration guide for existing keymaps
3. Update to all affected keymaps
