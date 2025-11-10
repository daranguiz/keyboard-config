# Quickstart Guide: Refactored QMK Keymap System

**Feature**: 002-keymap-refactor
**Date**: 2025-11-09
**Audience**: Developer working with refactored keymap structure

## Overview

This guide provides a quick introduction to working with the refactored QMK keymap system. After the refactor, all keymaps share a common 3x5_3 base layout while supporting keyboard-specific customizations.

**Time to complete**: 15 minutes

---

## Prerequisites

- QMK development environment set up
- Basic understanding of QMK keymaps and layers
- Git access to qmk_firmware repository

---

## Quickstart

### 1. Understanding the Architecture (2 minutes)

The refactored system uses a **hybrid approach**:

- **Shared code** in `users/dario/` (layer definitions, custom keycodes, shared functions)
- **Keyboard-specific** keymaps in `keyboards/<kbd>/keymaps/dario/` (wrapper macros, hardware features)

**Key insight**: You modify layer content in ONE place (`users/dario/layers.h`), and all keyboards get the update.

---

### 2. Modifying the Core Layout (5 minutes)

**Goal**: Change a key in the base layer across ALL keyboards.

#### Step 1: Edit the shared layer definition

```bash
# Open the shared layer file
$EDITOR users/dario/layers.h
```

#### Step 2: Find the layer you want to modify

```c
#define LAYER_BASE \
    KC_Q,    KC_W,    KC_F,    KC_P,    KC_G,    \
    KC_J,    KC_L,    KC_U,    KC_Y,    KC_QUOT, \
    HOME_A,  HOME_R,  HOME_S,  HOME_T,  KC_D,    \
    KC_H,    HOME_N,  HOME_E,  HOME_I,  HOME_O,  \
    // ... rest of layer
```

#### Step 3: Make your change

For example, swap W and F:

```c
#define LAYER_BASE \
    KC_Q,    KC_F,    KC_W,    KC_P,    KC_G,    \  /* Changed: F and W swapped */
    KC_J,    KC_L,    KC_U,    KC_Y,    KC_QUOT, \
    // ... rest unchanged
```

#### Step 4: Rebuild all keyboards

```bash
# Build for all keyboards to verify
make boardsource/lulu/rp2040:dario
make lily58/rev1:dario
make bastardkb/skeletyl:dario
```

**Result**: All three keyboards now have W and F swapped!

---

### 3. Adding a Keyboard-Specific Feature (5 minutes)

**Goal**: Add OLED functionality to Lulu without affecting other keyboards.

#### Step 1: Enable OLED in keyboard's rules.mk

```bash
$EDITOR keyboards/boardsource/lulu/keymaps/dario/rules.mk
```

Add:
```makefile
OLED_ENABLE = yes
SRC += oled.c
```

#### Step 2: Create OLED implementation

```bash
$EDITOR keyboards/boardsource/lulu/keymaps/dario/oled.c
```

```c
#include QMK_KEYBOARD_H

#ifdef OLED_ENABLE
oled_rotation_t oled_init_user(oled_rotation_t rotation) {
    return OLED_ROTATION_270;
}

bool oled_task_user(void) {
    oled_write_P(PSTR("Layer: "), false);
    switch (get_highest_layer(layer_state)) {
        case BASE:
            oled_write_P(PSTR("Base\n"), false);
            break;
        // ... other layers
    }
    return false;
}
#endif
```

#### Step 3: Build and test

```bash
make boardsource/lulu/rp2040:dario:flash
```

**Result**: Lulu now has OLED support. Lily58 and Skeletyl are unchanged.

---

### 4. Visualizing Your Keymap (3 minutes)

**Goal**: Generate a visual diagram of your keymap.

#### Step 1: Install keymap-drawer (one-time setup)

```bash
python3 -m pip install --user keymap-drawer
```

#### Step 2: Run visualization script

```bash
bash scripts/generate_keymap_diagram.sh boardsource/lulu/rp2040 dario
```

#### Step 3: View the output

```bash
open docs/keymaps/boardsource_lulu_rp2040_dario.svg
# Or: firefox docs/keymaps/boardsource_lulu_rp2040_dario.svg
```

**Result**: SVG diagram showing all layers with key labels!

---

## Common Tasks

### Adding a New Keyboard

**Time**: ~15 minutes

1. **Create keymap directory**:
   ```bash
   mkdir -p keyboards/<manufacturer>/<model>/keymaps/dario
   ```

2. **Create `keymap.c`**:
   ```c
   #include "keymap_config.h"  // If wrapper needed
   #include "dario.h"
   #include "layers.h"

   const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
     [BASE]   = LAYOUT_split_3x5_3(LAYER_BASE),
     [NAV]    = LAYOUT_split_3x5_3(LAYER_NAV),
     // ... all 8 layers
   };
   ```

3. **Create wrapper macro** (if keyboard has >36 keys):
   ```bash
   $EDITOR keyboards/<manufacturer>/<model>/keymaps/dario/keymap_config.h
   ```
   See [File Structure Contract](contracts/file-structure.md) for template.

4. **Create `rules.mk`**:
   ```makefile
   USER_NAME := dario
   # Enable keyboard-specific features
   ```

5. **Test**:
   ```bash
   make <manufacturer>/<model>:dario
   ```

6. **Update KEYBOARDS.md**:
   Add entry for new keyboard.

---

### Adding a New Layer

**Time**: ~10 minutes

1. **Add layer enum** in `users/dario/dario.h`:
   ```c
   enum layers {
       BASE,
       NAV,
       // ...
       NEWLAYER  // Add here
   };
   ```

2. **Define layer content** in `users/dario/layers.h`:
   ```c
   #define LAYER_NEWLAYER \
       KC_1,    KC_2,    KC_3,    /* ... 36 keys total */
   ```

3. **Add to keymaps** in all keyboards:
   ```c
   // keyboards/*/keymaps/dario/keymap.c
   const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
       // ...
       [NEWLAYER] = LAYOUT_split_3x5_3(LAYER_NEWLAYER)
   };
   ```

4. **Rebuild all keyboards**:
   ```bash
   make boardsource/lulu/rp2040:dario
   # ... etc
   ```

---

### Adding a Custom Keycode

**Time**: ~5 minutes

1. **Define keycode** in `users/dario/dario.h`:
   ```c
   enum custom_keycodes {
       // ...
       MY_MACRO = SAFE_RANGE + 10
   };
   ```

2. **Implement handler** in `users/dario/dario.c`:
   ```c
   bool process_record_user(uint16_t keycode, keyrecord_t *record) {
       switch (keycode) {
           case MY_MACRO:
               if (record->event.pressed) {
                   SEND_STRING("Hello, World!");
               }
               return false;
           // ...
       }
       return true;
   }
   ```

3. **Use in layer** in `users/dario/layers.h`:
   ```c
   #define LAYER_NEWLAYER \
       MY_MACRO, KC_2, KC_3, /* ... */
   ```

4. **Rebuild**:
   ```bash
   make boardsource/lulu/rp2040:dario
   ```

---

## Directory Reference

Quick navigation to key files:

| What | Where |
|------|-------|
| **Shared layer content** | `users/dario/layers.h` |
| **Layer enums** | `users/dario/dario.h` |
| **Custom keycode handlers** | `users/dario/dario.c` |
| **Lulu keymap** | `keyboards/boardsource/lulu/keymaps/dario/` |
| **Lily58 keymap** | `keyboards/lily58/keymaps/dario/` |
| **Skeletyl keymap** | `keyboards/bastardkb/skeletyl/keymaps/dario/` |
| **Build scripts** | `build_lulu.sh`, `build_lily58.sh`, etc. |
| **Visualization output** | `docs/keymaps/*.svg` |
| **Keyboard inventory** | `KEYBOARDS.md` |

---

## Build Commands Cheat Sheet

```bash
# Build specific keyboard
make boardsource/lulu/rp2040:dario
make lily58/rev1:dario
make bastardkb/skeletyl:dario

# Flash firmware
make boardsource/lulu/rp2040:dario:flash

# Clean build artifacts
make clean

# Build all keyboards in one command
make boardsource/lulu/rp2040:dario lily58/rev1:dario bastardkb/skeletyl:dario

# Generate visualization
bash scripts/generate_keymap_diagram.sh <keyboard> dario

# Using build scripts
./build_lulu.sh
./build_lily58.sh
./build_skeletyl.sh
```

---

## Troubleshooting

### Build fails with "USER_NAME not found"

**Solution**: Add `USER_NAME := dario` to keymap's `rules.mk`

---

### Build fails with "LAYOUT_split_3x5_3 not defined"

**Problem**: Keyboard with >36 keys needs wrapper macro.

**Solution**: Create `keymap_config.h` with wrapper macro (see File Structure Contract).

---

### Changes to layers.h not reflected in compiled firmware

**Problem**: Makefile caching.

**Solution**:
```bash
make clean
make <keyboard>:dario
```

---

### Custom keycode displays wrong in visualization

**Problem**: keymap-drawer config missing mapping.

**Solution**: Edit `~/.config/keymap-drawer/config.yaml`:
```yaml
raw_binding_map:
  "MY_MACRO": "Custom Label"
```

---

## Learning Path

**New to this refactored system?** Follow this path:

1. ✅ **Read this Quickstart** (you are here!)
2. 📖 **Read [File Structure Contract](contracts/file-structure.md)** - Understand mandatory file structure
3. 📖 **Read [Data Model](data-model.md)** - Understand entity relationships
4. 📖 **Read [Research Findings](research.md)** - Understand architectural decisions
5. 🛠️ **Make a small change** - Modify a key in LAYER_BASE
6. 🛠️ **Add keyboard-specific feature** - Enable OLED on one keyboard
7. 📊 **Generate visualization** - Create SVG diagram of your keymap

**Advanced topics:**
- Modifying home row mods pattern
- Adding keyboard-specific extra layers (e.g., gaming layer)
- Customizing OLED display behavior
- Creating combos (when combo support is re-enabled)

---

## Next Steps

After completing this quickstart:

1. **Review your current keymaps**: Identify differences between keyboards that should be unified
2. **Plan migration**: Use the File Structure Contract to plan changes
3. **Implement incrementally**: Start with one keyboard, verify, then migrate others
4. **Update documentation**: Ensure KEYBOARDS.md and README.md files are current

---

## Getting Help

- **File Structure Questions**: See [contracts/file-structure.md](contracts/file-structure.md)
- **Data Model Questions**: See [data-model.md](data-model.md)
- **Architecture Questions**: See [research.md](research.md)
- **QMK Questions**: https://docs.qmk.fm
- **keymap-drawer Questions**: https://github.com/caksoylar/keymap-drawer

---

## Summary

You now know how to:

- ✅ Modify shared layer content (affects all keyboards)
- ✅ Add keyboard-specific features (affects one keyboard)
- ✅ Generate visual keymap diagrams
- ✅ Add new keyboards to the system
- ✅ Navigate the refactored file structure

**Key principle**: One source of truth for the 36-key core layout, with flexibility for keyboard-specific extensions.

Happy keymap hacking! ⌨️
