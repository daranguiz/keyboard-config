# Research Findings: QMK Keymap Refactoring

**Feature**: 002-keymap-refactor
**Date**: 2025-11-09
**Status**: Phase 0 Complete

## Overview

This document consolidates research findings for two critical technical decisions in the keymap refactoring project:

1. **Architecture approach** for sharing keymap code across keyboards
2. **Visualization tooling** for generating keymap diagrams

---

## Decision 1: Shared Keymap Architecture

### Question

How should we create a single source of truth for the core 3x5_3 keymap across three keyboards (Lulu 58-key, Lily58 58-key, Skeletyl 36-key) while supporting keyboard-specific extensions?

### Options Evaluated

Three standard QMK mechanisms were evaluated:

#### Option A: Community Layouts (`layouts/community/split_3x5_3/dario/`)

**How it works:**
- Keyboards declare supported layouts via `info.json`: `"community_layouts": ["split_3x5_3"]`
- Build system searches `layouts/community/<layout>/` for matching keymaps
- Single keymap directory shared by all compatible keyboards

**Pros:**
- ✅ Most elegant conceptually - truly keyboard-agnostic
- ✅ Single keymap source tree for all keyboards
- ✅ Standard QMK pattern

**Cons:**
- ❌ Lulu and Lily58 don't currently declare `split_3x5_3` support
- ❌ Cannot handle keyboard-specific extensions natively (OLED, extra keys)
- ❌ Would require `#ifdef KEYBOARD_*` preprocessor blocks throughout
- ❌ No straightforward way to add keyboard-specific .c files

**Verdict:** ❌ Not recommended - The 58-key keyboards have extensions that break the pure 3x5_3 abstraction

---

#### Option B: Userspace (`users/dario/`)

**How it works:**
- QMK automatically includes `users/<keymap_name>/` in build path
- Userspace `rules.mk` and `config.h` processed before keymap files
- Supports `__attribute__((weak))` functions for keyboard-specific overrides

**Pros:**
- ✅ Excellent for shared C code (process_record_user, helper functions)
- ✅ Supports keyboard-specific overrides elegantly
- ✅ Conditional compilation via `#ifdef KEYBOARD_*`
- ✅ Works with any keyboard (no keyboard modifications needed)
- ✅ Existing `users/daranguiz/` demonstrates this pattern

**Cons:**
- ❌ Keymap files still per-keyboard (must duplicate keymap.c)
- ❌ Layout arrays must be duplicated across keymaps
- ⚠️ Naming constraint: keymap name must match username (or use `USER_NAME` override)

**Verdict:** ✅ Good for shared C code, but needs combination with another approach

---

#### Option C: Layout Wrapper Macros (Header Files)

**How it works:**
- Create header files with C preprocessor macros that map compact 3x5_3 definitions to full layouts
- Each keyboard has a wrapper macro that places 36 keys into its physical layout

**Example:**
```c
// keyboards/boardsource/lulu/keymaps/dario/keymap_config.h
#define LAYOUT_split_3x5_3(\
     K00, K01, K02, K03, K04,    K05, K06, K07, K08, K09,\
     /* ... 36 keys total ... */\
)\
LAYOUT(\
XXX, XXX, XXX, XXX, XXX, XXX,    XXX, XXX, XXX, XXX, XXX, XXX,\
XXX, K00, K01, K02, K03, K04,    K05, K06, K07, K08, K09, XXX,\
/* ... maps to full 58-key Lulu layout ... */\
)
```

**Pros:**
- ✅ Allows identical layer definitions across keyboards
- ✅ Full control over key mapping
- ✅ Can extend for keyboard-specific variants
- ✅ Works with ANY keyboard
- ✅ Can be combined with userspace
- ✅ Very flexible for irregular layouts

**Cons:**
- ❌ Wrapper macros are verbose and keyboard-specific
- ❌ Must manually maintain wrapper for each keyboard
- ⚠️ Harder to visualize physical layout when reading code

**Verdict:** ✅ Best for allowing identical layer definitions while handling keyboard differences

---

### Decision: Hybrid Approach (Userspace + Layout Wrappers)

**Architecture:**

```
users/dario/                          # Shared code via QMK userspace
├── rules.mk                          # Shared build rules
├── config.h                          # Global configuration
├── dario.h                           # Shared enums, layer names, custom keycodes
├── dario.c                           # Shared process_record_user, custom keycodes
├── mods.c                            # Shared mod-tap logic
└── layers.h                          # NEW: 3x5_3 layer content definitions

keyboards/boardsource/lulu/keymaps/dario/
├── keymap_config.h                   # LAYOUT_split_3x5_3 wrapper for Lulu
├── keymap.c                          # Uses LAYOUT_split_3x5_3 + includes layers.h
├── rules.mk                          # OLED_ENABLE = yes, USER_NAME := dario
├── README.md                         # Keymap documentation with ASCII art
└── oled.c                            # Lulu-specific OLED code

keyboards/lily58/keymaps/dario/       # Renamed from daranguiz_miryoku
├── keymap_config.h                   # LAYOUT_split_3x5_3 wrapper for Lily58
├── keymap.c                          # Uses LAYOUT_split_3x5_3 + includes layers.h
├── rules.mk                          # OLED_ENABLE = yes, USER_NAME := dario
├── README.md                         # Keymap documentation with ASCII art
└── oled.c                            # Lily58-specific OLED code

keyboards/bastardkb/skeletyl/keymaps/dario/  # Renamed from daranguiz_miryoku
├── keymap_config.h                   # Optional helper defines
├── keymap.c                          # Uses native LAYOUT_split_3x5_3 + includes layers.h
├── rules.mk                          # USER_NAME := dario
└── README.md                         # Keymap documentation with ASCII art
```

**Shared Layer Definition Example:**

```c
// users/dario/layers.h
#define LAYER_BASE \
    KC_Q,    KC_W,    KC_F,    KC_P,    KC_G,    KC_J,    KC_L,    KC_U,    KC_Y,    KC_QUOT, \
    HOME_A,  HOME_R,  HOME_S,  HOME_T,  KC_D,    KC_H,    HOME_N,  HOME_E,  HOME_I,  HOME_O,  \
    KC_Z,    KC_X,    KC_C,    KC_V,    KC_B,    KC_K,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH, \
             LT(MEDIA, KC_ESC), LT(NAV, KC_SPC), LT(MOUSE, KC_TAB), \
                                LT(SYM, KC_ENT), LT(NUM, KC_BSPC), LT(FUN, KC_DEL)
```

**Usage in Keymap:**

```c
// keyboards/lulu/keymaps/dario/keymap.c
#include "keymap_config.h"  // Contains LAYOUT_split_3x5_3 wrapper
#include "dario.h"          // From userspace
#include "layers.h"         // From userspace

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [BASE] = LAYOUT_split_3x5_3(LAYER_BASE),
  [NAV]  = LAYOUT_split_3x5_3(LAYER_NAV),
  // ... all layers use shared definitions
};
```

### Rationale

1. **Layer content is shared** via `users/dario/layers.h` - single source of truth ✅
2. **Layout wrappers are local** - each keyboard maps 3x5_3 to its physical layout ✅
3. **Keyboard-specific features stay local** - OLED, RGB, encoders ✅
4. **Userspace handles shared logic** - custom keycodes, process_record_user ✅
5. **Build commands are standard** - `make <keyboard>:dario` for all boards ✅
6. **No keyboard modifications required** - doesn't need community layout declarations ✅
7. **Follows Constitution Principle I** - all changes in `keyboards/*/keymaps/dario/` or `users/dario/` ✅

### Alternatives Considered

- **Pure community layouts**: Rejected due to incompatibility with 58-key keyboards with extensions
- **Git submodules/symlinks**: Rejected as non-standard, fragile
- **Separate shared header files**: Rejected in favor of userspace (standard QMK mechanism)

---

## Decision 2: Keymap Visualization Tool

### Question

What tool should we use to implement FR-005 (generate visual keymap diagrams)?

### Options Evaluated

| Tool | Input | Output | Custom Keycodes | Maturity | Recommendation |
|------|-------|--------|-----------------|----------|----------------|
| **keymap-drawer** | QMK JSON | SVG (→PNG) | Excellent (config-based) | Production ★★★★★ | ✅ **RECOMMENDED** |
| **keymapviz** | keymap.c | ASCII, JSON | Basic | Mature ★★★★☆ | ⚠️ ASCII only |
| **go-qmk-keymap** | keymap.c + config | SVG (experimental) | Via config | Alpha ★★☆☆☆ | ❌ Too immature |
| **QMK_KeymapToAsciiTable** | keymap.c | ASCII | Pass-through | Basic ★★★☆☆ | ⚠️ Limited features |
| **Custom script** | Various | Various | Full control | N/A | ⚠️ High effort |

---

### Decision: keymap-drawer

**Tool**: [keymap-drawer](https://github.com/caksoylar/keymap-drawer)
**Language**: Python
**Status**: Production-ready, actively maintained

#### Installation

```bash
# Recommended: pipx (isolated environment)
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install keymap-drawer

# Alternative: Direct pip install
python3 -m pip install --user keymap-drawer

# Optional: SVG → PNG converter
python3 -m pip install --user cairosvg
```

#### Workflow

```bash
# Step 1: Convert keymap.c to JSON
qmk c2json -kb boardsource/lulu/rp2040 -km dario --no-cpp > keymap.json

# Step 2: Parse JSON to YAML with configuration
keymap parse -c config.yaml \
  --layer-names "Base,Nav,Mouse,Media,Num,Sym,Fun,Button" \
  keymap.json > keymap.yaml

# Step 3: Generate SVG diagram
keymap draw -c config.yaml keymap.yaml > keymap.svg

# Step 4 (optional): Convert to PNG
cairosvg keymap.svg -o keymap.png
```

#### Custom Keycode Handling

**Configuration file** (`~/.config/keymap-drawer/config.yaml`):

```yaml
parse_config:
  qmk_remove_keycode_prefix:
    - "KC_"

  raw_binding_map:
    # Miryoku-style custom keycodes
    "U_NA": ""                    # Not available - blank
    "U_NU": ""                    # Not used - blank
    "U_UND": "⎌ Undo"
    "U_RDO": "⟲ Redo"
    "U_CUT": "✂ Cut"
    "U_CPY": "⧉ Copy"
    "U_PST": "⎀ Paste"

    # Mouse keycodes
    "MS_LEFT": "M ←"
    "MS_DOWN": "M ↓"
    "MS_UP": "M ↑"
    "MS_RGHT": "M →"
    "MS_BTN1": "L-Clk"
    "MS_BTN2": "R-Clk"
    "MS_BTN3": "M-Clk"

    # RGB controls
    "RM_TOGG": "RGB"
    "RM_NEXT": "Mode"
    "RM_HUEU": "Hue+"

draw_config:
  ortho_layout:
    split: true
    rows: 3
    columns: 5
    thumbs: 3
```

#### Integration with Build System

**Automation script** (`scripts/generate_keymap_diagram.sh`):

```bash
#!/bin/bash
set -e

KEYBOARD="${1:-boardsource/lulu/rp2040}"
KEYMAP="${2:-dario}"
OUTPUT_DIR="docs/keymaps"
CONFIG="${HOME}/.config/keymap-drawer/config.yaml"

mkdir -p "$OUTPUT_DIR"

# Convert and generate
qmk c2json -kb "$KEYBOARD" -km "$KEYMAP" --no-cpp | \
  keymap parse -c "$CONFIG" | \
  keymap draw -c "$CONFIG" - > "$OUTPUT_DIR/${KEYBOARD//\//_}_${KEYMAP}.svg"

echo "✓ Generated: $OUTPUT_DIR/${KEYBOARD//\//_}_${KEYMAP}.svg"
```

**Makefile integration:**

```makefile
.PHONY: visualize
visualize:
	@bash scripts/generate_keymap_diagram.sh boardsource/lulu/rp2040 dario
	@bash scripts/generate_keymap_diagram.sh lily58/rev1 dario
	@bash scripts/generate_keymap_diagram.sh bastardkb/skeletyl dario
```

### Rationale

1. **Production-ready**: Actively maintained with comprehensive documentation ✅
2. **Excellent output quality**: SVG with proper semantics, convertible to PNG ✅
3. **Custom keycode support**: Configuration-based mapping with Unicode symbols ✅
4. **Meets FR-005 requirements**: Visual diagrams suitable for printing/sharing ✅
5. **Scriptable**: Command-line tool integrates with build automation ✅
6. **Web UI available**: https://caksoylar.github.io/keymap-drawer for testing ✅
7. **Layout-agnostic**: Supports any keyboard layout via configuration ✅
8. **Low maintenance**: External tool, no custom code to maintain ✅

### Alternatives Considered

- **keymapviz**: Rejected due to ASCII-only output (FR-005 requires visual diagrams)
- **Custom Python script**: Rejected due to high development effort (4-8 hours) vs. setup time (1-2 hours)
- **go-qmk-keymap**: Rejected due to alpha status and invasive keymap.c modifications required

---

## Implementation Plan Updates

Based on these decisions, the following Technical Context items are now resolved:

### Architecture Approach ✅ RESOLVED

**Selected**: Hybrid approach (Userspace + Layout Wrapper Macros)

**Implementation details:**
- Create `users/dario/` with shared code (layers.h, dario.h, dario.c, mods.c)
- Define layer content as macros in `layers.h`
- Each keyboard keymap includes shared headers and uses local wrapper macros
- Keyboard-specific files (OLED, RGB, encoders) remain in keyboard keymap directories

**Build compatibility:**
```bash
make boardsource/lulu/rp2040:dario
make lily58/rev1:dario
make bastardkb/skeletyl:dario
```

### Visualization Tools ✅ RESOLVED

**Selected**: keymap-drawer

**Installation steps:**
1. Install keymap-drawer: `python3 -m pip install --user keymap-drawer`
2. Create config file: `~/.config/keymap-drawer/config.yaml`
3. Add custom keycode mappings for U_*, MS_*, RM_* keycodes
4. Create automation script: `scripts/generate_keymap_diagram.sh`
5. Test with Lulu keymap

**Output formats:**
- Primary: SVG (scalable, high quality)
- Secondary: PNG (via cairosvg conversion)
- Suitable for printing and digital sharing (FR-005 ✅)

---

## Decision 3: Per-Layer Extra Keys Strategy (2025-11-09)

### Question

How should wrapper macros handle keyboards with extra keys (like Lulu's 58-key layout) when different layers need different extra key configurations?

**Context**: Most layers will use the core 36-key layout with extras as `KC_NO`, but some layers (like a future gaming layer) may want to populate the number row and outer columns with real keycodes.

### Options Evaluated

#### Option 1: Layer-Specific Wrappers ✅ SELECTED

Define multiple wrapper macros for different use cases:

```c
// Standard wrapper: all extras are KC_NO
#define LAYOUT_split_3x5_3(K00, K01, ...) LAYOUT(XXX, XXX, ..., K00, K01, ...)

// Gaming wrapper: number row + outer columns populated
#define LAYOUT_split_3x5_3_WITH_NUMROW(K00, K01, ...) LAYOUT(KC_1, KC_2, ..., K00, K01, ...)
```

**Usage**:
```c
[NAV]    = LAYOUT_split_3x5_3(LAYER_NAV),           // Standard
[GAMING] = LAYOUT_split_3x5_3_WITH_NUMROW(LAYER_GAMING),  // With extras
```

**Pros**:
- ✅ Self-documenting: wrapper name indicates what extras are active
- ✅ Clean separation: most layers use standard wrapper
- ✅ Easy to add new wrapper types for different extra key patterns
- ✅ Maintains single source of truth for core 36 keys

**Cons**:
- ❌ Need to define multiple wrappers (but only as needed)

#### Option 2: Parameterized Wrapper with Extra Key Arguments

Single wrapper accepting both core keys and explicit extra key parameters.

**Verdict**: ❌ Rejected - Too verbose when using extras (20+ additional parameters), error-prone

#### Option 3: Separate Local Layer Definitions

Keep shared layers pure, define full Lulu-specific layers locally.

**Verdict**: ❌ Rejected - Violates DRY principle, core 36 keys would be duplicated

### Decision: Option 1 (Layer-Specific Wrappers)

**Rationale**:
1. **Scalability**: Start with standard `LAYOUT_split_3x5_3`, add specialized wrappers only when needed
2. **Future gaming layer**: Aligns with deferred feature (spec.md Future Work) - can add `LAYOUT_split_3x5_3_WITH_NUMROW` later
3. **Readability**: `LAYOUT_split_3x5_3_WITH_NUMROW(LAYER_GAMING)` clearly communicates intent
4. **Proven pattern**: Commonly used in QMK community for similar multi-keyboard setups

**Implementation**:
- Phase 5 (tasks.md): Implement standard `LAYOUT_split_3x5_3` wrapper for Lulu and Lily58
- Future work: Add specialized wrappers as needed for layers with extras

**Reference**: See `WRAPPER_MACRO_QUESTION.md` for detailed analysis of all three approaches.

---

## Next Steps

With research complete, proceed to Phase 1 (Design & Contracts):

1. **Generate data-model.md** - Define entities (Shared Base Layout, Keyboard Profile, etc.)
2. **Generate contracts/** - File structure contracts and API surface (if applicable)
3. **Generate quickstart.md** - Developer onboarding guide
4. **Update agent context** - Add technology choices to `.specify/memory/claude.md`

---

## References

### Code Examples Found

- **Existing userspace**: `/Users/dario/git/qmk_firmware/users/daranguiz/`
- **Lulu wrapper macro**: `/Users/dario/git/qmk_firmware/keyboards/boardsource/lulu/keymaps/dario/keymap_config.h:70-82`
- **Lily58 wrapper macro**: `/Users/dario/git/qmk_firmware/keyboards/lily58/keymaps/daranguiz_miryoku/config.h:68-94`
- **Build system logic**: `/Users/dario/git/qmk_firmware/builddefs/build_keyboard.mk:462-478`

### External Resources

- **keymap-drawer**: https://github.com/caksoylar/keymap-drawer
- **keymap-drawer web UI**: https://caksoylar.github.io/keymap-drawer
- **QMK userspace docs**: https://docs.qmk.fm/feature_userspace
- **QMK community layouts**: https://docs.qmk.fm/feature_layouts
