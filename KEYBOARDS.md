# Keyboard Inventory

**Auto-generated from `config/boards.yaml`** - Do not edit manually

Last updated: 2025-11-15 15:14:56

This document lists all keyboards configured in this repository with their firmware types and build configurations.

## Summary

- **Total keyboards**: 5
- **QMK firmwares**: 4
- **ZMK firmwares**: 1

---

## QMK Keyboards (4)

### Bastard Keyboards Skeletyl

**Board ID**: `skeletyl`  
**Firmware**: QMK  
**Keyboard**: `bastardkb/skeletyl/promicro`  
**Layout**: 3x5_3  

**Build command**:
```bash
qmk compile -kb bastardkb/skeletyl/promicro -km dario
```

**Configuration**: `qmk/config/boards/skeletyl.mk`

---

### Boardsource Lulu (RP2040)

**Board ID**: `lulu`  
**Firmware**: QMK  
**Keyboard**: `boardsource/lulu/rp2040`  
**Layout**: custom_58  
**Extra Layers**: GAME  

**Build command**:
```bash
qmk compile -kb boardsource/lulu/rp2040 -km dario
```

**Configuration**: `qmk/config/boards/lulu.mk`

---

### Corne (CRKBD) - QMK

**Board ID**: `corne_qmk`  
**Firmware**: QMK  
**Keyboard**: `crkbd/rev1`  
**Layout**: 3x6_3  

**Build command**:
```bash
qmk compile -kb crkbd/rev1 -km dario
```

**Configuration**: `qmk/config/boards/corne_qmk.mk`

---

### Lily58 Rev1

**Board ID**: `lily58`  
**Firmware**: QMK  
**Keyboard**: `lily58/rev1`  
**Layout**: custom_58  
**Extra Layers**: GAME  

**Build command**:
```bash
qmk compile -kb lily58/rev1 -km dario
```

**Configuration**: `qmk/config/boards/lily58.mk`

---

## ZMK Keyboards (1)

### Corne (CRKBD) - ZMK

**Board ID**: `corne_zmk`  
**Firmware**: ZMK  
**Shield**: `corne`  
**Layout**: 3x6_3  

**Configuration**: `zmk/config/boards/{board_id}.conf`

---


## Adding a New Keyboard

To add a new keyboard to this inventory:

### Option 1: Manual Configuration

1. Add an entry to `config/boards.yaml`:
   ```yaml
   <board_id>:
     name: "Board Name"
     firmware: qmk  # or zmk
     qmk_keyboard: "manufacturer/board/variant"  # for QMK
     # OR
     zmk_shield: "shield_name"  # for ZMK
     layout_size: "3x5_3"  # or 3x6_3, custom_*, etc.
     extra_layers: []  # optional board-specific layers
   ```

2. Create board-specific config:
   - **QMK**: `qmk/config/boards/<board_id>.mk` (feature flags)
   - **ZMK**: `zmk/config/boards/<board_id>.conf` (ZMK settings)

3. If the board has extensions, add them to layers in `config/keymap.yaml`:
   ```yaml
   layers:
     BASE:
       extensions:
         3x6_3:  # for 42-key boards
           outer_pinky_left: [TAB, GRV, CAPS]
           outer_pinky_right: [QUOT, BSLS, ENT]
   ```

4. Generate keymaps:
   ```bash
   python3 scripts/generate.py
   ```

5. Add to build targets:
   ```bash
   qmk userspace-add -kb <keyboard> -km dario
   ```

6. Update this file:
   ```bash
   python3 scripts/generate_keyboards_md.py
   ```

### Option 2: Helper Script

```bash
bash scripts/add_board.sh <board_id> <firmware> <keyboard_path> <layout_size>
```

Example:
```bash
bash scripts/add_board.sh corne zmk corne 3x6_3
```

This will automatically:
- Add entry to `config/boards.yaml`
- Create config template
- Regenerate this file

---

## Layout Sizes

- **3x5_3**: 36-key (3x5 fingers + 3 thumbs per hand) - Base layout
- **3x6_3**: 42-key (3x6 fingers + 3 thumbs per hand) - Corne, etc.
- **custom_***: Custom layouts with board-specific wrappers (Lulu, Lily58)

---

## Configuration Files

### Per-Board Configuration (Firmware-Specific Features)

**QMK**: `qmk/config/boards/<board_id>.mk`
- Feature flags (OLED, RGB Matrix, etc.)
- Build-time settings
- Board-specific QMK options

**ZMK**: `zmk/config/boards/<board_id>.conf`
- ZMK settings (Bluetooth, display, etc.)
- Shield-specific configuration

### Unified Keymap Configuration

**All keyboards share the same keymap** defined in `config/keymap.yaml`.

The 36-key core layout is identical across all keyboards. Larger boards automatically receive extensions based on their `layout_size`.

---

## Build All Keyboards

```bash
# Generate keymaps for all boards
python3 scripts/generate.py

# Build all QMK keyboards
qmk userspace-compile

# Or use the combined script
./build_all.sh
```

---

## Further Reading

- **Main documentation**: `CLAUDE.md` (repository root)
- **Keymap configuration guide**: `config/README.md`
- **Project constitution**: `.specify/memory/constitution.md`
- **Implementation plan**: `specs/003-unified-keymap-codegen/plan.md`
