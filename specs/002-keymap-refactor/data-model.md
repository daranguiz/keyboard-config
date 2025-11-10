# Data Model: QMK Keymap Refactoring

**Feature**: 002-keymap-refactor
**Date**: 2025-11-09
**Status**: Phase 1

## Overview

This document defines the key entities and their relationships in the refactored QMK keymap system. The data model captures the structure of shared layouts, keyboard-specific configurations, and visualization metadata.

---

## Entity Definitions

### 1. Shared Base Layout

**Description**: The common 3x5_3 keymap definition (36 keys: 3 rows × 5 columns per hand + 3 thumb keys per hand) that applies identically across all keyboards.

**Location**: `users/dario/layers.h`

**Fields**:

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `layer_name` | Enum | Layer identifier | One of: BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON | `BASE` |
| `key_positions` | Array[36] of Keycode | Key assignments for 36-key layout | QMK keycodes, modifiers, layer taps | `[KC_Q, KC_W, ..., LT(NAV, KC_SPC), ...]` |
| `home_row_mods` | Object | Modifier-tap configuration for home row | GACS pattern (GUI/ALT/CTL/SFT) | `{A: LGUI_T, R: LALT_T, S: LCTL_T, T: LSFT_T}` |
| `layer_dependencies` | Array[Enum] | Other layers referenced by layer-tap keys | Valid layer names | `[NAV, SYM, NUM]` |

**Validation Rules**:
- Array must contain exactly 36 keycodes
- Home row modifiers must follow GACS pattern on left hand, mirrored on right
- Layer-tap references must point to valid layer names
- No circular layer dependencies

**State Transitions**:
N/A (static configuration)

**Example Structure**:

```c
// users/dario/layers.h
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

#define LAYER_BASE \
    KC_Q,              KC_W,              KC_F,              KC_P,              KC_G,              KC_J,              KC_L,              KC_U,              KC_Y,              KC_QUOT, \
    LGUI_T(KC_A),      LALT_T(KC_R),      LCTL_T(KC_S),      LSFT_T(KC_T),      KC_D,              KC_H,              LSFT_T(KC_N),      LCTL_T(KC_E),      LALT_T(KC_I),      LGUI_T(KC_O), \
    LT(BUTTON, KC_Z),  ALGR_T(KC_X),      KC_C,              KC_V,              KC_B,              KC_K,              KC_M,              KC_COMM,           ALGR_T(KC_DOT),    LT(BUTTON, KC_SLSH), \
                       LT(MEDIA, KC_ESC), LT(NAV, KC_SPC),   LT(MOUSE, KC_TAB), LT(SYM, KC_ENT),   LT(NUM, KC_BSPC),  LT(FUN, KC_DEL)
```

---

### 2. Layout Wrapper Macro

**Description**: Keyboard-specific C preprocessor macro that maps the 36-key shared layout to the keyboard's physical layout.

**Location**: `keyboards/<keyboard>/keymaps/dario/keymap_config.h` (per keyboard)

**Fields**:

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `macro_name` | Identifier | Wrapper macro name | Must be `LAYOUT_split_3x5_3` | `LAYOUT_split_3x5_3` |
| `input_params` | Array[36] of Param | 36 parameter slots for shared keys | K00-K09, K10-K19, K20-K29, K32-K37 | `K00, K01, ..., K37` |
| `physical_layout` | Macro invocation | Keyboard's native LAYOUT macro | Must match keyboard's actual layout | `LAYOUT(...)` for Lulu |
| `key_mapping` | Array of Position | Maps 36 input keys to physical positions | Must map all 36 keys, may add extras | See example below |
| `unused_positions` | Array of Position | Physical keys not part of 36-key core | Filled with KC_NO or XXX | Extra keys on 58-key boards |

**Validation Rules**:
- Must map all 36 input parameters to physical positions
- Extra physical positions must be explicitly handled (KC_NO or assigned)
- Macro must invoke keyboard's native LAYOUT macro
- Physical layout must match keyboard's `info.json` definition

**Example for Lulu (58-key)**:

```c
// keyboards/boardsource/lulu/keymaps/dario/keymap_config.h
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
```

**Example for Skeletyl (36-key)**:

```c
// keyboards/bastardkb/skeletyl/keymaps/dario/keymap_config.h
// No wrapper needed - keyboard natively supports LAYOUT_split_3x5_3
// Can use keyboard's LAYOUT_split_3x5_3 directly
```

---

### 3. Keyboard Profile

**Description**: Configuration specific to each keyboard model, including hardware capabilities and customizations.

**Location**: `keyboards/<keyboard>/keymaps/dario/` directory

**Fields**:

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `keyboard_path` | String | QMK keyboard identifier | Valid keyboard path in QMK | `boardsource/lulu/rp2040` |
| `keymap_name` | String | Keymap identifier | Always "dario" after refactor | `dario` |
| `physical_key_count` | Integer | Total number of keys | Positive integer | 58 (Lulu), 36 (Skeletyl) |
| `uses_wrapper_macro` | Boolean | Whether keyboard needs 3x5_3 wrapper | True if keys > 36 | True (Lulu), False (Skeletyl) |
| `hardware_features` | Object | Enabled hardware features | See Hardware Features entity | `{oled: true, rgb: false}` |
| `extra_layers` | Array of Layer | Keyboard-specific extra layers | Only for keyboards with extra keys | `[GAME]` (Lily58) |
| `build_command` | String | Make command to build firmware | Valid QMK build syntax | `make boardsource/lulu/rp2040:dario` |

**Relationships**:
- **Has** 1 Shared Base Layout (via userspace inclusion)
- **Has** 0-1 Layout Wrapper Macro (if physical_key_count > 36)
- **Has** 1+ Hardware Features
- **Has** 0+ Extra Layers

**Validation Rules**:
- `keyboard_path` must exist in QMK firmware repository
- `keymap_name` must be "dario" (per FR-008)
- If `physical_key_count` > 36, `uses_wrapper_macro` must be true
- `build_command` must successfully compile with QMK build system

**State Transitions**:
N/A (static configuration)

---

### 4. Hardware Features

**Description**: Hardware-specific capabilities and their configurations for each keyboard.

**Location**: `keyboards/<keyboard>/keymaps/dario/rules.mk` and `config.h`

**Fields**:

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `oled_enabled` | Boolean | OLED display present | True/False | True (Lulu, Lily58), False (Skeletyl) |
| `oled_implementation` | File path | Path to OLED code | Required if oled_enabled | `oled.c` |
| `rgb_matrix_enabled` | Boolean | RGB matrix lighting | True/False | False (all current boards) |
| `encoder_enabled` | Boolean | Rotary encoder present | True/False | False (all current boards) |
| `split_keyboard` | Boolean | Split keyboard layout | True/False | True (all current boards) |
| `nkro_enabled` | Boolean | N-Key Rollover | True/False | True (Lulu) |
| `feature_flags` | Object | QMK feature flags | Valid QMK feature names | See example below |

**Validation Rules**:
- If `oled_enabled` is true, `oled_implementation` file must exist
- Feature flags must correspond to valid QMK build options
- Conflicting features must not be enabled simultaneously (e.g., RGB_MATRIX + RGBLIGHT)

**Example**:

```makefile
# keyboards/boardsource/lulu/keymaps/dario/rules.mk
OLED_ENABLE = yes
SPLIT_KEYBOARD = yes
NKRO_ENABLE = yes
CONSOLE_ENABLE = no
COMMAND_ENABLE = no
BOOTMAGIC_ENABLE = yes
```

---

### 5. Keymap Visualization

**Description**: Visual representation of the keyboard layout showing all layers, key labels, modifiers, and tap/hold behaviors.

**Location**: `docs/keymaps/` directory (generated)

**Fields**:

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `keyboard_identifier` | String | Keyboard being visualized | Must match Keyboard Profile | `boardsource_lulu_rp2040` |
| `keymap_name` | String | Keymap being visualized | Must match Keyboard Profile | `dario` |
| `output_format` | Enum | Diagram file format | One of: SVG, PNG | `SVG` |
| `file_path` | Path | Location of generated diagram | In docs/keymaps/ | `docs/keymaps/lulu_dario.svg` |
| `layer_diagrams` | Array of Layer Diagram | Visual for each layer | One per layer in keymap | See example below |
| `custom_keycode_mappings` | Object | Display labels for custom keys | Maps keycode to display string | `{U_UND: "⎌ Undo"}` |
| `generation_timestamp` | Datetime | When diagram was generated | ISO 8601 format | `2025-11-09T12:34:56Z` |

**Relationships**:
- **Visualizes** 1 Keyboard Profile
- **Contains** 8 Layer Diagrams (one per layer)

**Validation Rules**:
- Must accurately represent all keys in all layers
- Custom keycodes must have visual representation (symbol or name)
- Output must be suitable for printing (FR-005)
- File must be regenerated when keymap changes

**Example Custom Keycode Mappings**:

```yaml
# keymap-drawer config
raw_binding_map:
  "U_NA": ""                    # Not available - blank
  "U_UND": "⎌ Undo"
  "U_RDO": "⟲ Redo"
  "U_CUT": "✂ Cut"
  "U_CPY": "⧉ Copy"
  "U_PST": "⎀ Paste"
  "MS_LEFT": "M ←"
  "MS_BTN1": "L-Clk"
```

---

### 6. Layer Diagram

**Description**: Visual representation of a single layer within a keymap visualization.

**Location**: Part of Keymap Visualization entity

**Fields**:

| Field | Type | Description | Constraints | Example |
|-------|------|-------------|-------------|---------|
| `layer_name` | Enum | Layer identifier | Must match Shared Base Layout | `BASE` |
| `key_labels` | Array[36+] of String | Display labels for each key | Human-readable labels | `["Q", "W", "F", ...]` |
| `modifier_indicators` | Array of Modifier | Visual indicators for modifiers | Tap/hold, layer-tap indicators | `[{key: 10, type: "GUI-tap"}]` |
| `legend_entries` | Array of Legend | Symbol explanations | Maps symbols to meanings | `[{symbol: "⎌", meaning: "Undo"}]` |

**Validation Rules**:
- Must contain label for every key in layout
- Modifier indicators must correspond to actual modifier-tap keys
- Legend must explain all custom symbols used

---

## Entity Relationships

```
Shared Base Layout (1)
    ↓ included by
Keyboard Profile (N) ──────────────┐
    ↓ has                          │
Layout Wrapper Macro (0-1)         │
    ↓ has                          │
Hardware Features (1+)             │
                                   │
                                   ↓ visualized in
                            Keymap Visualization (1)
                                   ↓ contains
                            Layer Diagram (8)
```

**Key relationships:**

1. **One Shared Base Layout** is included by **many Keyboard Profiles** (1:N)
2. **Each Keyboard Profile** has **zero or one Layout Wrapper Macro** (1:0..1)
3. **Each Keyboard Profile** has **one or more Hardware Features** (1:N)
4. **Each Keyboard Profile** is **visualized in one Keymap Visualization** (1:1)
5. **Each Keymap Visualization** contains **multiple Layer Diagrams** (1:N)

---

## File Structure Mapping

```
users/dario/                                  → Shared Base Layout
├── layers.h                                  → Layer definitions (LAYER_BASE, LAYER_NAV, etc.)
├── dario.h                                   → Enums, custom keycodes
├── dario.c                                   → Shared process_record_user
└── rules.mk                                  → Shared feature flags

keyboards/<keyboard>/keymaps/dario/           → Keyboard Profile
├── keymap_config.h                           → Layout Wrapper Macro
├── keymap.c                                  → Keymap arrays (uses shared layers)
├── config.h                                  → Hardware-specific config
├── rules.mk                                  → Hardware Features (feature flags)
├── oled.c                                    → Hardware Features (OLED implementation)
└── README.md                                 → Documentation with ASCII art

docs/keymaps/                                 → Keymap Visualization
├── lulu_dario.svg                            → SVG diagram for Lulu
├── lily58_dario.svg                          → SVG diagram for Lily58
└── skeletyl_dario.svg                        → SVG diagram for Skeletyl
```

---

## Data Flow

### Compilation Flow

```
1. User runs: make boardsource/lulu/rp2040:dario

2. QMK build system:
   - Includes users/dario/rules.mk (Shared Base Layout metadata)
   - Includes keyboards/boardsource/lulu/keymaps/dario/rules.mk (Hardware Features)
   - Compiles users/dario/*.c (Shared Base Layout code)

3. C Preprocessor:
   - Reads keymap.c
   - Expands #include "layers.h" (Shared Base Layout)
   - Expands LAYOUT_split_3x5_3(LAYER_BASE) using keymap_config.h (Layout Wrapper Macro)
   - Results in full keymaps[][] array with Lulu's 58-key layout

4. Compiler:
   - Compiles keymap arrays
   - Links shared code from users/dario/
   - Links keyboard-specific code (oled.c)

5. Output: firmware .uf2 file ready for flashing
```

### Visualization Flow

```
1. User runs: bash scripts/generate_keymap_diagram.sh boardsource/lulu/rp2040 dario

2. Script flow:
   - Runs qmk c2json (converts keymap.c → JSON)
   - Runs keymap parse (JSON → YAML with config)
   - Runs keymap draw (YAML → SVG)

3. keymap-drawer:
   - Reads Keyboard Profile info from JSON
   - Applies Custom Keycode Mappings from config
   - Generates Layer Diagram for each layer
   - Outputs Keymap Visualization as SVG

4. Output: docs/keymaps/lulu_dario.svg
```

---

## Summary

This data model defines six core entities:

1. **Shared Base Layout** - The single source of truth for 36-key layout
2. **Layout Wrapper Macro** - Keyboard-specific mapping to physical layout
3. **Keyboard Profile** - Per-keyboard configuration and metadata
4. **Hardware Features** - Hardware-specific capabilities
5. **Keymap Visualization** - Generated visual diagrams
6. **Layer Diagram** - Visual representation of individual layers

These entities work together to enable:
- Single source of truth for core layout (FR-001)
- Keyboard-specific customization (FR-002, FR-003)
- Automated visualization generation (FR-005)
- Clean separation of concerns (FR-011)

The relationships between entities ensure consistency while allowing flexibility for keyboard-specific features.
