# Research: Unified QMK/ZMK Keymap Code Generation

**Feature**: 003-unified-keymap-codegen
**Date**: 2025-11-14
**Status**: Complete

This document consolidates research findings for implementing a Python-based code generator that produces QMK and ZMK keymaps from unified YAML configuration.

---

## 1. Language & Tooling Decision

### Decision: Python 3.11+

**Rationale**:
- **YAML Parsing**: PyYAML 6.0.3 is already installed and provides robust native Python data structure handling
- **String Templating**: Python's f-strings, `.format()`, and native multi-line strings are sufficient for C and devicetree generation
- **Testing**: stdlib unittest is available immediately; pytest can be added later for advanced features
- **Validation**: Python's structured error handling is superior for FR-014 (clear error reporting) and FR-007 (complex keybinding validation)
- **Maintainability**: Classes, modules, and type hints provide better structure than Bash for this complexity level
- **User Direction**: User explicitly requested Python over Bash

**Primary Dependencies**:
- **Python 3.11.10** (already installed via pyenv)
- **PyYAML 6.0.3** (already installed)
- **pytest** (recommended addition for testing): `pip install pytest`

**Alternatives Considered**:
- **Bash + yq**: Rejected - requires installing yq, complex string manipulation, difficult validation logic
- **Jinja2 templates**: Deferred - native Python formatting sufficient initially; can add later if needed
- **Node.js**: Rejected - adds new runtime, no compelling advantage

---

## 2. QMK Code Generation Patterns

### Existing QMK Architecture Analysis

From examining `users/dario/layers.h` and `keyboards/boardsource/lulu/keymaps/dario/`:

**Current Pattern**:
```c
// users/dario/layers.h - Single source of truth (manual C macros)
#define LAYER_BASE \
    KC_Q,              KC_W,              KC_F,              ..., \
    LGUI_T(KC_A),      LALT_T(KC_R),      LCTL_T(KC_S),      ..., \
    ...

// keyboards/.../keymap.c - Uses wrapper macro
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE]   = LAYOUT_wrapper(LAYER_BASE),
    [NUM]    = LAYOUT_wrapper(LAYER_NUM),
    ...
};

// keyboards/.../keymap_config.h - Maps 36-key to board-specific layout
#define LAYOUT_wrapper(...) LAYOUT_split_3x5_3(__VA_ARGS__)
#define LAYOUT_split_3x5_3(K00, K01, ...) \
    LAYOUT(\
        XXX, XXX, ...,  /* number row not used */ \
        XXX, K00, K01, K02, K03, K04, ...\
    )
```

**Key Insights**:
1. Layer definitions use C macros with comma-separated keycodes
2. Mod-tap keys use `LGUI_T(KC_A)`, `LALT_T(KC_R)`, `LSFT_T(KC_T)` syntax
3. Layer-tap keys use `LT(LAYER, KC_KEY)` syntax
4. Wrapper macros map 36-key layout to board-specific LAYOUT macros
5. `U_NA`, `U_NU`, `U_NP` constants indicate unavailable/unused/non-present keys
6. RGB aliases (`RM_TOGG`, `RM_NEXT`) handle conditional feature support

### QMK Code Generation Approach

**Recommended Strategy**: Hybrid template + programmatic generation

**Structure**:
```python
# scripts/qmk_generator.py
class QMKGenerator:
    def __init__(self, config, board):
        self.config = config  # Parsed YAML
        self.board = board    # Board definition from boards.yaml

    def generate_keymap_c(self) -> str:
        """Generate keymap.c file"""
        layers = self._generate_layers()
        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml

#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {{
{layers}
}};
"""

    def _generate_layers(self) -> str:
        """Generate all layer definitions"""
        layer_defs = []
        for layer_name in self.config['layers']:
            keycodes = self._compile_layer(layer_name)
            formatted = self._format_layout_macro(keycodes)
            layer_defs.append(f"    [{layer_name}] = {formatted},")
        return "\n".join(layer_defs)

    def _compile_layer(self, layer_name: str) -> list:
        """Compile layer with extensions applied"""
        core = self.config['layers'][layer_name]['core']
        extensions = self._get_extensions_for_board(layer_name)
        return core + extensions  # Simplified - actual logic more complex

    def _format_layout_macro(self, keycodes: list) -> str:
        """Format keycodes into LAYOUT_* macro call"""
        # Group keycodes into rows for readability
        rows = self._group_into_rows(keycodes)
        formatted_rows = [", ".join(row) for row in rows]
        return f"LAYOUT_split_3x5_3(\n        " + ",\n        ".join(formatted_rows) + "\n    )"
```

**Keycode Translation**:
```python
class KeycodeTranslator:
    """Translate unified YAML syntax to QMK C syntax"""

    def translate(self, unified_key: str) -> str:
        """
        Unified format examples:
        - "KC_A" -> "KC_A"
        - "hrm:LGUI:A" -> "LGUI_T(KC_A)"
        - "lt:NAV:SPC" -> "LT(NAV, KC_SPC)"
        - "NONE" -> "KC_NO"
        - "bt:next" -> "KC_NO" (Bluetooth filtered for QMK)
        """
        if unified_key == "NONE":
            return "KC_NO"

        # Homerow mod: hrm:LGUI:A -> LGUI_T(KC_A)
        if unified_key.startswith("hrm:"):
            _, mod, key = unified_key.split(":")
            return f"{mod}_T(KC_{key})"

        # Layer-tap: lt:NAV:SPC -> LT(NAV, KC_SPC)
        if unified_key.startswith("lt:"):
            _, layer, key = unified_key.split(":")
            return f"LT({layer}, KC_{key})"

        # Firmware-specific filtering
        if unified_key.startswith("bt:"):  # Bluetooth (ZMK-only)
            return "KC_NO"  # Filter for QMK

        # Standard keycode: A -> KC_A
        if not unified_key.startswith("KC_"):
            return f"KC_{unified_key}"

        return unified_key
```

**File Structure**:
- `qmk/keymaps/<board>_dario/keymap.c` - Generated layer definitions
- `qmk/keymaps/<board>_dario/config.h` - Generated includes and layer enums
- `qmk/keymaps/<board>_dario/rules.mk` - Generated build rules
- `qmk/keymaps/<board>_dario/README.md` - Generated with ASCII art

**Formatting Considerations**:
- Use 4-space indentation for C code
- Align keycodes in columns for readability (optional enhancement)
- Multi-line arrays with proper line breaks
- Include file header comments indicating auto-generation

**Validation Strategy**:
- Parse generated C to ensure syntactic validity (simple regex checks)
- Integration test: Run `qmk compile -kb <board> -km dario` to verify compilation
- Unit test keycode translation functions independently

---

## 3. ZMK Code Generation Patterns

### ZMK Keymap Structure

**ZMK Devicetree Syntax** (.keymap files):
```dts
// ZMK uses devicetree overlay syntax
#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>

/ {
    keymap {
        compatible = "zmk,keymap";

        base_layer {
            bindings = <
                &kp Q       &kp W       &kp F       &kp P       &kp G
                &hrm LGUI A &hrm LALT R &hrm LCTL S &hrm LSFT T &kp D
                &kp Z       &kp X       &kp C       &kp V       &kp B
                            &kp RET     &lt NAV SPC &lt MEDIA TAB
            >;
        };

        nav_layer {
            bindings = <
                &none   &none   &none   &none   &none
                &kp LGUI &kp LALT &kp LCTL &kp LSFT &none
                &trans  &trans  &trans  &trans  &trans
                        &trans  &trans  &trans
            >;
        };
    };
};
```

**Key Patterns**:
- Behaviors use `&` prefix: `&kp`, `&hrm`, `&lt`, `&mo`, `&bt`
- Custom behaviors defined in ZMK config (e.g., `&hrm` for homerow mods)
- `&none` = no key action (equivalent to QMK's `KC_NO`)
- `&trans` = transparent (pass through to lower layer)
- Layer names use `_layer` suffix convention
- Bindings use angle brackets `< >` with space-separated entries

### ZMK Code Generation Approach

**Recommended Strategy**: Template-based with behavior translation

**Structure**:
```python
# scripts/zmk_generator.py
class ZMKGenerator:
    def __init__(self, config, board):
        self.config = config
        self.board = board

    def generate_keymap(self) -> str:
        """Generate .keymap devicetree file"""
        layers = self._generate_layers()
        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
#include <dt-bindings/zmk/bt.h>

/ {{
    keymap {{
        compatible = "zmk,keymap";

{layers}
    }};
}};
"""

    def _generate_layers(self) -> str:
        layer_defs = []
        for layer_name in self.config['layers']:
            keycodes = self._compile_layer(layer_name)
            formatted = self._format_bindings(keycodes)
            layer_defs.append(f"""        {layer_name.lower()}_layer {{
            bindings = <
{formatted}
            >;
        }};""")
        return "\n\n".join(layer_defs)

    def _format_bindings(self, keycodes: list) -> str:
        """Format keycodes as ZMK bindings with proper indentation"""
        # Group into rows for visual layout
        rows = self._group_into_rows(keycodes)
        formatted_rows = []
        for row in rows:
            formatted_rows.append("                " + " ".join(row))
        return "\n".join(formatted_rows)
```

**Keycode Translation for ZMK**:
```python
class ZMKKeycodeTranslator:
    """Translate unified YAML syntax to ZMK devicetree syntax"""

    def translate(self, unified_key: str) -> str:
        """
        Unified format -> ZMK format:
        - "KC_A" -> "&kp A"
        - "hrm:LGUI:A" -> "&hrm LGUI A"
        - "lt:NAV:SPC" -> "&lt NAV SPC"
        - "NONE" -> "&none"
        - "bt:next" -> "&bt BT_NXT"
        - "QK_BOOT" -> "&bootloader"
        """
        if unified_key == "NONE":
            return "&none"

        # Homerow mod: hrm:LGUI:A -> &hrm LGUI A
        if unified_key.startswith("hrm:"):
            _, mod, key = unified_key.split(":")
            return f"&hrm {mod} {key}"

        # Layer-tap: lt:NAV:SPC -> &lt NAV SPC
        if unified_key.startswith("lt:"):
            _, layer, key = unified_key.split(":")
            layer_num = self._get_layer_index(layer)
            return f"&lt {layer_num} {key}"

        # Bluetooth: bt:next -> &bt BT_NXT
        if unified_key.startswith("bt:"):
            action = unified_key.split(":")[1]
            bt_map = {
                "next": "BT_NXT",
                "prev": "BT_PRV",
                "clear": "BT_CLR",
            }
            return f"&bt {bt_map.get(action, 'BT_NXT')}"

        # Bootloader
        if unified_key == "QK_BOOT":
            return "&bootloader"

        # Standard keycode: KC_A -> &kp A
        if unified_key.startswith("KC_"):
            key = unified_key[3:]  # Remove KC_ prefix
            return f"&kp {key}"

        # Bare keycode: A -> &kp A
        return f"&kp {unified_key}"
```

**Behavior Translation**:
The unified YAML uses firmware-agnostic aliases that get translated:
- `hrm:` → QMK: `LGUI_T()`, ZMK: `&hrm` (custom behavior)
- `lt:` → QMK: `LT()`, ZMK: `&lt`
- `bt:` → QMK: `KC_NO` (filtered), ZMK: `&bt BT_*`

**Validation Strategy**:
- Parse generated devicetree for syntax errors
- Integration test: Attempt ZMK build (if ZMK toolchain available)
- Verify custom behaviors referenced in bindings exist in `zmk/config/global/behaviors.dtsi`

---

## 4. YAML Schema Design

### config/keymap.yaml Structure

```yaml
# Core keymap configuration
layers:
  BASE:
    core:  # 36-key base layout
      # Left hand (3x5)
      - [Q,              W,              F,              P,              G]
      - [hrm:LGUI:A,     hrm:LALT:R,     hrm:LCTL:S,     hrm:LSFT:T,     D]
      - [Z,              lt:FUN:X,       C,              V,              B]
      # Right hand (3x5)
      - [J,              L,              U,              Y,              QUOT]
      - [H,              hrm:RSFT:N,     hrm:RCTL:E,     hrm:RALT:I,     hrm:RGUI:O]
      - [K,              M,              COMM,           ALGR_T:DOT,     SLSH]
      # Thumbs (3+3)
      - [ENT,            lt:NAV:SPC,     lt:MEDIA:TAB]
      - [lt:SYM:DEL,     LSFT,           lt:NUM:BSPC]

    extensions:
      3x5_3_pinky:  # 38-key: +1 outer pinky key per side
        outer_pinky_left: TAB
        outer_pinky_right: QUOT

      3x6_3:  # 42-key: +3-key pinky column per side
        outer_pinky_left: [TAB, GRV, CAPS]
        outer_pinky_right: [QUOT, BSLS, ENT]

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

    extensions:
      3x5_3_pinky:
        outer_pinky_left: NONE
        outer_pinky_right: HOME

# ... other layers (MEDIA, NUM, SYM, FUN, etc.)
```

### config/boards.yaml Structure

```yaml
# Board inventory and configuration
# NOTE: Features (OLED, RGB, etc.) are configured in firmware-specific files:
#   - QMK: qmk/config/boards/<board_id>.mk
#   - ZMK: zmk/config/boards/<board_id>.conf
boards:
  skeletyl:
    name: "Bastard Keyboards Skeletyl"
    firmware: qmk
    qmk_keyboard: "bastardkb/skeletyl/promicro"
    layout_size: "3x5_3"  # 36-key base (no extensions applied)

  lulu:
    name: "Boardsource Lulu (RP2040)"
    firmware: qmk
    qmk_keyboard: "boardsource/lulu/rp2040"
    layout_size: "custom_58"  # 58-key custom (uses board-specific wrapper)
    extra_layers:  # Board-specific layers
      - GAME

  lily58:
    name: "Lily58 Rev1"
    firmware: qmk
    qmk_keyboard: "lily58/rev1"
    layout_size: "custom_58"  # 58-key custom (uses board-specific wrapper)
    extra_layers:  # Board-specific layers
      - GAME

  corne:
    name: "Corne (CRKBD)"
    firmware: zmk
    zmk_shield: "corne"
    layout_size: "3x6_3"  # 42-key (automatically applies extensions["3x6_3"])
```

**Example firmware-specific feature configuration:**

```make
# qmk/config/boards/lulu.mk
BOOTMAGIC_ENABLE = yes
MOUSEKEY_ENABLE = yes
OLED_ENABLE = yes
RGB_MATRIX_ENABLE = yes
```

```conf
# zmk/config/boards/corne.conf
CONFIG_ZMK_MOUSE=y
CONFIG_BT_CTLR_TX_PWR_PLUS_8=y
```

### config/aliases.yaml Structure

```yaml
# Firmware-agnostic behavior aliases
behaviors:
  hrm:
    description: "Homerow mod (hold for modifier, tap for key)"
    qmk_pattern: "{mod}_T(KC_{key})"
    zmk_pattern: "&hrm {mod} {key}"
    params: [mod, key]

  lt:
    description: "Layer-tap (hold for layer, tap for key)"
    qmk_pattern: "LT({layer}, KC_{key})"
    zmk_pattern: "&lt {layer} {key}"
    params: [layer, key]

  bt:
    description: "Bluetooth control (ZMK-only)"
    qmk_pattern: "KC_NO"  # Filtered
    zmk_pattern: "&bt BT_{action}"
    params: [action]
    firmware_support: [zmk]

# Keycode mappings
keycodes:
  NONE:
    qmk: "KC_NO"
    zmk: "&none"

  QK_BOOT:
    qmk: "QK_BOOT"
    zmk: "&bootloader"
```

---

## 5. Testing Strategy

### Unit Testing Structure

```python
# tests/test_keycode_translator.py
import unittest
from scripts.keycode_translator import QMKTranslator, ZMKTranslator

class TestQMKTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = QMKTranslator()

    def test_simple_keycode(self):
        self.assertEqual(self.translator.translate("A"), "KC_A")

    def test_homerow_mod(self):
        self.assertEqual(
            self.translator.translate("hrm:LGUI:A"),
            "LGUI_T(KC_A)"
        )

    def test_layer_tap(self):
        self.assertEqual(
            self.translator.translate("lt:NAV:SPC"),
            "LT(NAV, KC_SPC)"
        )

    def test_bluetooth_filtered(self):
        """Bluetooth keys should be filtered to KC_NO in QMK"""
        self.assertEqual(self.translator.translate("bt:next"), "KC_NO")

class TestZMKTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = ZMKTranslator()

    def test_simple_keycode(self):
        self.assertEqual(self.translator.translate("A"), "&kp A")

    def test_homerow_mod(self):
        self.assertEqual(
            self.translator.translate("hrm:LGUI:A"),
            "&hrm LGUI A"
        )

    def test_bluetooth_support(self):
        """Bluetooth keys should work in ZMK"""
        self.assertEqual(self.translator.translate("bt:next"), "&bt BT_NXT")
```

### Integration Testing

```python
# tests/test_integration.py
import subprocess
import tempfile
import shutil

class TestQMKGeneration(unittest.TestCase):
    def test_generated_keymap_compiles(self):
        """Verify generated QMK keymap compiles successfully"""
        # Generate keymap
        from scripts.generate_qmk import generate_for_board
        generate_for_board("skeletyl")

        # Attempt compilation
        result = subprocess.run(
            ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0, f"Compilation failed: {result.stderr}")
```

---

## 6. Migration Strategy

### Existing Code to YAML Conversion

**Challenge**: Convert existing `users/dario/layers.h` to `config/keymap.yaml`

**Approach**:
1. Write a one-time migration script `scripts/migrate_layers.py`
2. Parse existing C macros using regex to extract keycodes
3. Translate QMK-specific syntax to unified format:
   - `LGUI_T(KC_A)` → `hrm:LGUI:A`
   - `LT(NAV, KC_SPC)` → `lt:NAV:SPC`
   - `KC_NO` → `NONE`
4. Generate initial `config/keymap.yaml` with core layouts
5. Manually add extensions for larger boards (38-key, 42-key)

**Migration Script Pseudocode**:
```python
def migrate_layer_from_c_macro(macro_text: str) -> dict:
    """
    Parse: #define LAYER_BASE \
           KC_Q, KC_W, ...

    Return: {
        'core': [[Q, W, F, ...], [A, R, S, ...], ...]
    }
    """
    keycodes = extract_keycodes(macro_text)
    unified_keycodes = [translate_to_unified(kc) for kc in keycodes]
    return group_into_layout(unified_keycodes, rows=4, cols=9)
```

---

## 7. Integration with Build Pipeline

### Modified build_all.sh

```bash
#!/bin/bash
# Generate keymaps before building

echo "Generating keymaps from unified config..."
python3 scripts/generate.py

if [ $? -ne 0 ]; then
    echo "❌ Keymap generation failed"
    exit 1
fi

echo "✅ Keymaps generated successfully"
echo ""
echo "Building QMK firmwares..."
qmk userspace-compile

echo ""
echo "Generating keymap visualizations..."
bash scripts/generate_keymap_diagram.sh
```

### GitHub Actions Workflow

```yaml
# .github/workflows/build-all.yml
name: Build All Firmwares

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: pip install pyyaml pytest

      - name: Run generator tests
        run: pytest tests/

      - name: Generate keymaps
        run: python3 scripts/generate.py

      - name: Build QMK firmwares
        uses: qmk/qmk_build@main
        with:
          keyboards: |
            bastardkb/skeletyl/promicro:dario
            boardsource/lulu/rp2040:dario
            lily58/rev1:dario

      # TODO: Add ZMK build steps when ZMK boards are configured
```

---

## 8. Open Questions Resolved

### Q: Python vs Bash for generator?
**A**: Python 3.11+ (user confirmed)

### Q: YAML parsing library?
**A**: PyYAML 6.0.3 (already installed)

### Q: Testing framework?
**A**: Start with stdlib unittest, add pytest as optional dependency

### Q: Template engine needed?
**A**: No - native Python string formatting (f-strings, multi-line strings) is sufficient

### Q: How to handle firmware-incompatible features?
**A**:
- Simple keycodes (e.g., Bluetooth): Silent filtering during translation
- Complex keybindings: Strict validation, fail generation with clear error

### Q: Auto-generate KEYBOARDS.md from boards.yaml?
**A**: YES - implement as part of generator (Principle IV compliance)

### Q: Visualization integration?
**A**:
- Generate ASCII art in keymap file comments
- Call existing `generate_keymap_diagram.sh` after keymap generation
- Integrate into main `generate.sh` pipeline

---

## 9. Implementation Phases

### Phase 1: Core Generator (Minimal Viable Product)
- Parse `config/keymap.yaml` (core layouts only, no extensions)
- Parse `config/boards.yaml` (basic board definitions)
- Generate QMK keymap.c for 36-key boards (Skeletyl)
- Keycode translation: simple keycodes + hrm + lt
- Basic validation (schema check)

### Phase 2: Extension Support
- Implement per-layer extensions (3x5_3_pinky, 3x6_3)
- Generate for larger boards (Lulu, Lily58)
- Board-specific layer overrides (GAME layer)

### Phase 3: ZMK Generation
- ZMK devicetree generator
- ZMK keycode translation
- Bluetooth keycode support

### Phase 4: Validation & Testing
- Comprehensive unit tests
- Integration tests (compilation verification)
- Error reporting improvements

### Phase 5: Tooling & DX
- Migration script (`migrate_layers.py`)
- Add board script (`add_board.sh`)
- Visualization integration
- Auto-generate KEYBOARDS.md

---

## Summary

**Technical Decisions Made**:
1. ✅ **Language**: Python 3.11+
2. ✅ **YAML Parsing**: PyYAML 6.0.3
3. ✅ **Testing**: unittest (stdlib) + pytest (optional)
4. ✅ **Templating**: Native Python (no Jinja2 initially)
5. ✅ **Code Generation**: Hybrid template + programmatic approach
6. ✅ **Keycode Translation**: Pattern-based with firmware filtering

**Research Complete**: All "NEEDS CLARIFICATION" items from Technical Context resolved.

**Next Steps**: Proceed to Phase 1 (Data Model & Contracts)
