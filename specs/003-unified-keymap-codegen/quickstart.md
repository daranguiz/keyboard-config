# Quickstart: Unified Keymap Code Generation

**Feature**: 003-unified-keymap-codegen
**Audience**: Developer implementing this feature
**Date**: 2025-11-14

This guide provides a quick path to implementing and using the unified keymap code generation system.

---

## Prerequisites

- Python 3.11+ installed
- PyYAML 6.0.3 (already installed)
- Existing QMK userspace repository
- (Optional) ZMK repository for migration

---

## Implementation Roadmap

### Phase 1: Core Generator (Week 1-2)

**Goal**: Generate QMK keymaps for 36-key boards from YAML config

#### Step 1.1: Set up project structure

```bash
cd /Users/dario/git/qmk_userspace

# Create directories
mkdir -p config scripts tests/fixtures

# Install testing dependencies
pip install pytest
```

#### Step 1.2: Create minimal YAML configuration

**File**: `config/keymap.yaml`
```yaml
layers:
  BASE:
    core:
      # Left hand (3x5)
      - [Q,            W,              F,              P,              G]
      - [hrm:LGUI:A,   hrm:LALT:R,     hrm:LCTL:S,     hrm:LSFT:T,     D]
      - [Z,            lt:FUN:X,       C,              V,              B]
      # Right hand (3x5)
      - [J,            L,              U,              Y,              QUOT]
      - [H,            hrm:RSFT:N,     hrm:RCTL:E,     hrm:RALT:I,     hrm:RGUI:O]
      - [K,            M,              COMM,           DOT,            SLSH]
      # Thumbs (3+3)
      - [ENT,          lt:NAV:SPC,     lt:MEDIA:TAB]
      - [lt:SYM:DEL,   LSFT,           lt:NUM:BSPC]

  NAV:
    core:
      - [NONE,    NONE,     NONE,     NONE,     NONE]
      - [LGUI,    LALT,     LCTL,     LSFT,     NONE]
      - [NONE,    NONE,     NONE,     NONE,     NONE]
      - [ESC,     NONE,     NONE,     NONE,     NONE]
      - [CAPS,    LEFT,     DOWN,     UP,       RGHT]
      - [INS,     HOME,     PGDN,     PGUP,     END]
      - [NONE,    NONE,     NONE]
      - [DEL,     ENT,      BSPC]

  # Add other layers: NUM, SYM, MEDIA, FUN
```

**File**: `config/boards.yaml`
```yaml
boards:
  skeletyl:
    name: "Bastard Keyboards Skeletyl"
    firmware: qmk
    qmk_keyboard: "bastardkb/skeletyl/promicro"
    layout_size: "3x5_3"  # 36-key base
```

**File**: `qmk/config/boards/skeletyl.mk` (firmware-specific features)
```make
# QMK feature flags for Skeletyl
BOOTMAGIC_ENABLE = yes
MOUSEKEY_ENABLE = yes
NKRO_ENABLE = yes
```

**Note**: Feature flags (BOOTMAGIC_ENABLE, MOUSEKEY_ENABLE, etc.) are NOT in boards.yaml because they're firmware-specific and non-portable. They remain in qmk/config/ and zmk/config/ directories where you edit them directly.

#### Step 1.3: Implement YAML parser

**File**: `scripts/config_parser.py`
```python
from pathlib import Path
from typing import Dict, List
import yaml
from dataclasses import dataclass


@dataclass
class Layer:
    name: str
    core: list  # Simplified for phase 1


def parse_keymap(yaml_path: Path) -> Dict[str, Layer]:
    """Parse config/keymap.yaml"""
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    layers = {}
    for layer_name, layer_data in data['layers'].items():
        layers[layer_name] = Layer(
            name=layer_name,
            core=layer_data['core']
        )

    return layers


def parse_boards(yaml_path: Path) -> List[dict]:
    """Parse config/boards.yaml"""
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return [board for board_id, board in data['boards'].items()]
```

#### Step 1.4: Implement QMK keycode translator

**File**: `scripts/qmk_translator.py`
```python
import re


class QMKTranslator:
    """Translate unified syntax to QMK C syntax"""

    def translate(self, unified: str) -> str:
        """
        Examples:
        - "A" -> "KC_A"
        - "hrm:LGUI:A" -> "LGUI_T(KC_A)"
        - "lt:NAV:SPC" -> "LT(NAV, KC_SPC)"
        - "NONE" -> "KC_NO"
        """
        if unified == "NONE":
            return "KC_NO"

        # Homerow mod
        if unified.startswith("hrm:"):
            parts = unified.split(":")
            mod, key = parts[1], parts[2]
            return f"{mod}_T(KC_{key})"

        # Layer-tap
        if unified.startswith("lt:"):
            parts = unified.split(":")
            layer, key = parts[1], parts[2]
            return f"LT({layer}, KC_{key})"

        # Bluetooth (filter for QMK)
        if unified.startswith("bt:"):
            return "KC_NO"

        # Standard keycode
        if unified.startswith("KC_"):
            return unified

        return f"KC_{unified}"
```

#### Step 1.5: Implement QMK code generator

**File**: `scripts/qmk_generator.py`
```python
from pathlib import Path
from typing import List


class QMKGenerator:
    """Generate QMK C keymap files"""

    def __init__(self, translator):
        self.translator = translator

    def generate_keymap_c(self, board: dict, layers: dict) -> str:
        """Generate keymap.c file"""
        layer_defs = []

        for layer_name, layer in layers.items():
            keycodes = self._flatten_and_translate(layer.core)
            formatted = self._format_layout(keycodes)
            layer_defs.append(f"    [{layer_name}] = LAYOUT_split_3x5_3(\n{formatted}\n    ),")

        layers_code = "\n".join(layer_defs)

        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml

#include QMK_KEYBOARD_H

enum layers {{
    {", ".join(layers.keys())}
}};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {{
{layers_code}
}};
"""

    def _flatten_and_translate(self, core: list) -> List[str]:
        """Flatten nested list and translate keycodes"""
        flat = [key for row in core for key in row]
        return [self.translator.translate(k) for k in flat]

    def _format_layout(self, keycodes: List[str]) -> str:
        """Format keycodes with proper indentation"""
        # Group into rows for readability
        rows = [
            keycodes[0:5],   # Left hand row 1
            keycodes[5:10],  # Left hand row 2
            keycodes[10:15], # Left hand row 3
            keycodes[15:20], # Right hand row 1
            keycodes[20:25], # Right hand row 2
            keycodes[25:30], # Right hand row 3
            keycodes[30:33], # Left thumbs
            keycodes[33:36], # Right thumbs
        ]

        formatted_rows = []
        for i, row in enumerate(rows):
            if i < 6:  # Finger rows
                formatted_rows.append("        " + ", ".join(f"{k:20}" for k in row) + ",")
            else:  # Thumb rows
                formatted_rows.append("                              " + ", ".join(f"{k:20}" for k in row))

        return "\n".join(formatted_rows)
```

#### Step 1.6: Create main entry point

**File**: `scripts/generate.py`
```python
#!/usr/bin/env python3
"""
Main entry point for unified keymap code generation
"""

from pathlib import Path
import sys

from config_parser import parse_keymap, parse_boards
from qmk_translator import QMKTranslator
from qmk_generator import QMKGenerator


def main():
    # Paths
    repo_root = Path(__file__).parent.parent
    config_dir = repo_root / "config"
    qmk_output_dir = repo_root / "qmk/keymaps"

    # Parse configuration
    print("📖 Parsing configuration...")
    layers = parse_keymap(config_dir / "keymap.yaml")
    boards = parse_boards(config_dir / "boards.yaml")

    print(f"✅ Loaded {len(layers)} layers, {len(boards)} boards")

    # Generate for each board
    for board in boards:
        if board['firmware'] != 'qmk':
            continue  # Phase 1: QMK only

        print(f"\n🔨 Generating keymap for {board['name']}...")

        # Generate
        translator = QMKTranslator()
        generator = QMKGenerator(translator)
        keymap_c = generator.generate_keymap_c(board, layers)

        # Write output
        board_dir = qmk_output_dir / f"{board['qmk_keyboard'].replace('/', '_')}_dario"
        board_dir.mkdir(parents=True, exist_ok=True)

        (board_dir / "keymap.c").write_text(keymap_c)

        print(f"✅ Generated {board_dir}/keymap.c")

    print("\n🎉 Keymap generation complete!")


if __name__ == "__main__":
    sys.exit(main())
```

#### Step 1.7: Test the generator

```bash
# Make script executable
chmod +x scripts/generate.py

# Run generator
python3 scripts/generate.py

# Verify output
cat qmk/keymaps/bastardkb_skeletyl_promicro_dario/keymap.c

# Try to compile (integration test)
qmk compile -kb bastardkb/skeletyl/promicro -km dario
```

---

### Phase 2: Extension Support (Week 3)

**Goal**: Support larger boards (38-key, 42-key) with extensions

#### Step 2.1: Add extensions to keymap.yaml

```yaml
layers:
  BASE:
    core:
      # ... 36-key layout ...

    extensions:
      3x6_3:  # Corne (42-key: 3x6 + 3 thumbs)
        outer_pinky_left: [TAB, GRV, CAPS]
        outer_pinky_right: [QUOT, BSLS, ENT]
```

#### Step 2.2: Add larger boards to boards.yaml

**Example: Corne (42-key board with 3x6 matrix)**
```yaml
boards:
  corne:
    name: "Corne (CRKBD)"
    firmware: zmk
    zmk_shield: "corne"
    layout_size: "3x6_3"  # 42-key (generator automatically applies extensions["3x6_3"])
```

**Example: Lulu (58-key board - different approach)**
```yaml
boards:
  lulu:
    name: "Boardsource Lulu"
    firmware: qmk
    qmk_keyboard: "boardsource/lulu/rp2040"
    layout_size: "custom_58"  # Custom layout (uses board-specific wrapper)
    extra_layers: ["GAME"]
```

**Note**:
- **layout_size** is the source of truth - the generator automatically infers which extensions to apply
- For standard sizes like "3x6_3", extensions are automatically applied
- For custom layouts like "custom_58" (Lulu/Lily58), board-specific LAYOUT wrappers are used instead of extensions

```make
# qmk/config/boards/lulu.mk
OLED_ENABLE = yes
RGB_MATRIX_ENABLE = yes
```

#### Step 2.3: Implement layer compiler

**File**: `scripts/layer_compiler.py`
```python
class LayerCompiler:
    def compile_layer(self, layer, board, translator):
        """Apply extensions and translate keycodes"""
        # Start with core (36 keys)
        keycodes = self._flatten(layer.core)

        # Infer which extensions to apply based on layout_size
        extensions_to_apply = board.get_extensions()  # Infers from layout_size

        # Apply extensions
        for ext_name in extensions_to_apply:
            if ext_name in layer.extensions:
                ext_keys = layer.extensions[ext_name]['keys']
                keycodes.extend(self._flatten_extension(ext_keys))

        # Translate
        return [translator.translate(k) for k in keycodes]

    def _flatten_extension(self, ext_keys):
        """Flatten extension keys"""
        result = []
        for position, keys in ext_keys.items():
            if isinstance(keys, list):
                result.extend(keys)
            else:
                result.append(keys)
        return result
```

#### Step 2.4: Update generator to use compiler

Modify `qmk_generator.py` to use `LayerCompiler` for extension support.

---

### Phase 3: ZMK Support (Week 4)

**Goal**: Generate ZMK devicetree keymaps

#### Step 3.1: Implement ZMK translator

**File**: `scripts/zmk_translator.py`
```python
class ZMKTranslator:
    def translate(self, unified: str) -> str:
        """Translate to ZMK devicetree syntax"""
        if unified == "NONE":
            return "&none"

        if unified.startswith("hrm:"):
            parts = unified.split(":")
            mod, key = parts[1], parts[2]
            return f"&hrm {mod} {key}"

        if unified.startswith("lt:"):
            parts = unified.split(":")
            layer, key = parts[1], parts[2]
            # Note: ZMK uses layer numbers, need layer index lookup
            return f"&lt {layer} {key}"

        if unified.startswith("bt:"):
            action = unified.split(":")[1]
            actions = {"next": "BT_NXT", "prev": "BT_PRV"}
            return f"&bt {actions.get(action, 'BT_NXT')}"

        if unified.startswith("KC_"):
            return f"&kp {unified[3:]}"

        return f"&kp {unified}"
```

#### Step 3.2: Implement ZMK generator

**File**: `scripts/zmk_generator.py`
```python
class ZMKGenerator:
    def generate_keymap(self, board: dict, layers: dict) -> str:
        """Generate .keymap devicetree file"""
        layer_defs = []

        for layer_name, layer in layers.items():
            keycodes = self._flatten_and_translate(layer.core)
            bindings = self._format_bindings(keycodes)
            layer_defs.append(f"""        {layer_name.lower()}_layer {{
            bindings = <
{bindings}
            >;
        }};""")

        layers_code = "\n\n".join(layer_defs)

        return f"""// AUTO-GENERATED - DO NOT EDIT
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {{
    keymap {{
        compatible = "zmk,keymap";

{layers_code}
    }};
}};
"""
```

---

## Migration from Existing Keymaps

### Step 1: Create migration script

**File**: `scripts/migrate_layers.py`
```python
"""One-time migration from users/dario/layers.h to config/keymap.yaml"""

import re


def parse_layer_macro(macro_text: str) -> list:
    """Extract keycodes from #define LAYER_* macro"""
    # Remove #define line
    lines = macro_text.strip().split("\n")[1:]
    # Join and split by commas
    keycodes_str = " ".join(lines).replace("\\", "")
    keycodes = [kc.strip() for kc in keycodes_str.split(",")]
    return keycodes


def translate_to_unified(qmk_keycode: str) -> str:
    """Translate QMK syntax to unified syntax"""
    # LGUI_T(KC_A) -> hrm:LGUI:A
    if match := re.match(r'(\w+)_T\(KC_(\w+)\)', qmk_keycode):
        mod, key = match.groups()
        return f"hrm:{mod}:{key}"

    # LT(NAV, KC_SPC) -> lt:NAV:SPC
    if match := re.match(r'LT\((\w+), KC_(\w+)\)', qmk_keycode):
        layer, key = match.groups()
        return f"lt:{layer}:{key}"

    # KC_NO -> NONE
    if qmk_keycode == "KC_NO":
        return "NONE"

    # KC_A -> A
    if qmk_keycode.startswith("KC_"):
        return qmk_keycode[3:]

    return qmk_keycode


# Run migration
with open("users/dario/layers.h", "r") as f:
    content = f.read()

# Parse each layer
# ... implementation ...

# Write to config/keymap.yaml
# ... implementation ...
```

### Step 2: Run migration

```bash
python3 scripts/migrate_layers.py
# Review config/keymap.yaml
# Test generation and compilation
```

---

## Testing

### Unit Tests

**File**: `tests/test_qmk_translator.py`
```python
import pytest
from scripts.qmk_translator import QMKTranslator


def test_simple_keycode():
    t = QMKTranslator()
    assert t.translate("A") == "KC_A"


def test_homerow_mod():
    t = QMKTranslator()
    assert t.translate("hrm:LGUI:A") == "LGUI_T(KC_A)"


def test_layer_tap():
    t = QMKTranslator()
    assert t.translate("lt:NAV:SPC") == "LT(NAV, KC_SPC)"


def test_bluetooth_filtered():
    t = QMKTranslator()
    assert t.translate("bt:next") == "KC_NO"
```

### Integration Tests

```python
def test_full_generation_compiles():
    """Ensure generated keymap compiles"""
    import subprocess

    # Generate
    subprocess.run(["python3", "scripts/generate.py"], check=True)

    # Compile
    result = subprocess.run(
        ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
        capture_output=True
    )

    assert result.returncode == 0
```

---

## Daily Development Workflow

Once implemented, daily usage is simple:

```bash
# 1. Edit unified keymap
vim config/keymap.yaml

# 2. Generate all keymaps
python3 scripts/generate.py

# 3. Build firmware
./build_all.sh

# 4. Flash to keyboard
qmk flash -kb bastardkb/skeletyl/promicro -km dario
```

---

## Troubleshooting

### Generated keymap doesn't compile

1. Check `qmk/keymaps/<board>_dario/keymap.c` for syntax errors
2. Verify layer names are valid C identifiers
3. Check for typos in keycode translation

### Extensions not applied

1. Verify board references correct extension in `boards.yaml`
2. Check that extension exists in layer definition
3. Ensure extension keys are formatted correctly (single key vs list)

### Bluetooth keys not working in ZMK

1. Verify ZMK-specific keycodes use `bt:` prefix
2. Check that ZMK translator is handling `bt:` properly
3. Ensure ZMK config has Bluetooth enabled

---

## Next Steps After Implementation

1. **Add visualization**: Integrate `generate_keymap_diagram.sh` into pipeline
2. **Add boards.yaml auto-generation**: Generate `KEYBOARDS.md` from boards inventory
3. **Improve error messages**: Add line numbers, context for validation errors
4. **Add board command**: Implement `add_board.sh` helper script
5. **CI/CD integration**: Update GitHub Actions to use generator

---

## Success Criteria

✅ Phase 1 Complete when:
- QMK keymaps generated from YAML for 36-key board
- Generated keymap compiles without errors
- Can change key in YAML and see it reflected after regeneration

✅ Phase 2 Complete when:
- Larger boards (Lulu, Lily58) support extensions
- Core 36-key layout identical across all boards
- Extensions only add keys without modifying core

✅ Phase 3 Complete when:
- ZMK keymaps generated from same unified YAML
- Bluetooth keycodes work in ZMK, filtered in QMK
- One config file generates both firmwares successfully

---

## Summary

**Minimum Viable Product** (Phase 1):
- Parse YAML config
- Translate keycodes (simple + hrm + lt)
- Generate QMK keymap.c for 36-key boards
- ~500 lines of Python code

**Full Feature** (Phase 3):
- Extension support for larger boards
- ZMK generation
- Full validation and error handling
- Visualization integration
- ~1500 lines of Python code + tests

**Time Estimate**: 3-4 weeks for complete implementation
