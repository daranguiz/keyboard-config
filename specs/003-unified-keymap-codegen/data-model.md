# Data Model: Unified Keymap Code Generation

**Feature**: 003-unified-keymap-codegen
**Date**: 2025-11-14
**Status**: Complete

This document defines the data entities, their relationships, and validation rules for the unified keymap configuration system.

---

## Entity Relationship Diagram

```
┌─────────────────────────┐
│   KeymapConfiguration   │
│                         │
│ - layers: Layer[]       │
│ - metadata: dict        │
└───────────┬─────────────┘
            │
            │ contains
            ▼
    ┌───────────────┐
    │     Layer     │
    │               │
    │ - name: str   │
    │ - core: Grid  │
    │ - extensions  │
    └───────┬───────┘
            │
            │ has
            ▼
    ┌─────────────────────┐
    │    LayerExtension   │
    │                     │
    │ - name: str         │
    │ - keys: KeyDef[]    │
    └─────────────────────┘

┌─────────────────────────┐
│    BoardInventory       │
│                         │
│ - boards: Board[]       │
└───────────┬─────────────┘
            │
            │ contains
            ▼
    ┌──────────────────────┐
    │       Board          │
    │                      │
    │ - id: str            │
    │ - firmware: Firmware │
    │ - layout_size: str   │
    │ - extensions: str[]  │
    │ - features: str[]    │
    │ - extra_layers: str[]│
    └──────────┬───────────┘
               │
               │ generates
               ▼
    ┌───────────────────────┐
    │   GeneratedKeymap     │
    │                       │
    │ - board: Board        │
    │ - layers: CompiledLayer[]│
    │ - format: QMK | ZMK   │
    └───────────────────────┘

┌─────────────────────────┐
│   BehaviorAliases       │
│                         │
│ - behaviors: Behavior[] │
│ - keycodes: Keycode[]   │
└─────────────────────────┘
```

---

## Core Entities

### 1. KeymapConfiguration

Represents the unified keymap definition from `config/keymap.yaml`.

**Fields**:
- `layers`: `Dict[str, Layer]` - All layer definitions indexed by layer name
- `metadata`: `Dict[str, Any]` - Optional metadata (author, version, description)

**Validation Rules**:
- At least one layer must be defined
- All layer names must be valid C identifiers (uppercase alphanumeric + underscore)
- Required layers: `BASE` (others are optional)
- Layer names must be unique

**Python Representation**:
```python
@dataclass
class KeymapConfiguration:
    layers: Dict[str, Layer]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self):
        if not self.layers:
            raise ValidationError("At least one layer must be defined")
        if "BASE" not in self.layers:
            raise ValidationError("BASE layer is required")
        for name in self.layers:
            if not name.isupper() or not name.replace("_", "").isalnum():
                raise ValidationError(f"Invalid layer name: {name}")
```

---

### 2. Layer

Represents a single keyboard layer (e.g., BASE, NAV, NUM).

**Fields**:
- `name`: `str` - Layer identifier (e.g., "BASE", "NAV")
- `core`: `KeyGrid` - The 36-key core layout (required)
- `extensions`: `Dict[str, LayerExtension]` - Optional extensions for larger boards

**Structure**:
```python
@dataclass
class Layer:
    name: str
    core: KeyGrid  # 36 keys in 4 rows (3x5 left, 3x5 right, 3+3 thumbs)
    extensions: Dict[str, LayerExtension] = field(default_factory=dict)

    def validate(self):
        if len(self.core.flatten()) != 36:
            raise ValidationError(f"Layer {self.name} core must have exactly 36 keys")
```

**Core Layout Structure** (KeyGrid):
```python
@dataclass
class KeyGrid:
    """
    Represents a grid of keys as nested lists
    For 3x5_3 layout:
      - rows[0:3]: left hand columns (3 rows × 5 cols)
      - rows[3:6]: right hand columns (3 rows × 5 cols)
      - rows[6]: left thumb keys (3 keys)
      - rows[7]: right thumb keys (3 keys)
    """
    rows: List[List[str]]  # Nested list of keycode strings

    def flatten(self) -> List[str]:
        """Flatten to single list of 36 keycodes"""
        return [key for row in self.rows for key in row]

    @property
    def left_hand(self) -> List[List[str]]:
        """First 3 rows (3x5)"""
        return self.rows[0:3]

    @property
    def right_hand(self) -> List[List[str]]:
        """Next 3 rows (3x5)"""
        return self.rows[3:6]

    @property
    def thumbs_left(self) -> List[str]:
        """Row 6 (3 keys)"""
        return self.rows[6]

    @property
    def thumbs_right(self) -> List[str]:
        """Row 7 (3 keys)"""
        return self.rows[7]
```

---

### 3. LayerExtension

Represents additional keys for boards larger than 36-key.

**Fields**:
- `extension_type`: `str` - Extension identifier (e.g., "3x5_3_pinky", "3x6_3")
- `keys`: `Dict[str, Union[str, List[str]]]` - Position-based key definitions

**Extension Types**:
- `3x5_3_pinky`: 38-key layout (36-key + 1 outer pinky key per side)
  - Positions: `outer_pinky_left`, `outer_pinky_right`
- `3x6_3`: 42-key layout (36-key + 3-key outer pinky column per side)
  - Positions: `outer_pinky_left` (list of 3), `outer_pinky_right` (list of 3)
- Custom board-specific: Any other layout variations

**Python Representation**:
```python
@dataclass
class LayerExtension:
    extension_type: str  # "3x5_3_pinky", "3x6_3", etc.
    keys: Dict[str, Union[str, List[str]]]

    def validate(self):
        if self.extension_type == "3x5_3_pinky":
            required = {"outer_pinky_left", "outer_pinky_right"}
            if not required.issubset(self.keys.keys()):
                raise ValidationError(f"3x5_3_pinky requires: {required}")
            for pos in required:
                if isinstance(self.keys[pos], list):
                    raise ValidationError(f"{pos} must be a single key, not a list")

        elif self.extension_type == "3x6_3":
            required = {"outer_pinky_left", "outer_pinky_right"}
            if not required.issubset(self.keys.keys()):
                raise ValidationError(f"3x6_3 requires: {required}")
            for pos in required:
                if not isinstance(self.keys[pos], list) or len(self.keys[pos]) != 3:
                    raise ValidationError(f"{pos} must be a list of exactly 3 keys")
```

**YAML Example**:
```yaml
extensions:
  3x5_3_pinky:
    outer_pinky_left: TAB
    outer_pinky_right: QUOT

  3x6_3:
    outer_pinky_left: [TAB, GRV, CAPS]
    outer_pinky_right: [QUOT, BSLS, ENT]
```

---

### 4. Board

Represents a physical keyboard configuration from `config/boards.yaml`.

**Fields**:
- `id`: `str` - Unique board identifier (e.g., "skeletyl", "lulu")
- `name`: `str` - Human-readable name
- `firmware`: `Literal["qmk", "zmk"]` - Target firmware
- `qmk_keyboard`: `Optional[str]` - QMK keyboard path (e.g., "bastardkb/skeletyl/promicro")
- `zmk_shield`: `Optional[str]` - ZMK shield name (e.g., "corne")
- `layout_size`: `str` - Physical layout size (e.g., "3x5_3", "3x6_3", "custom_58")
- `extra_layers`: `List[str]` - Board-specific additional layers (e.g., ["GAME"])

**Note**:
- Firmware-specific settings (feature flags like OLED, RGB, mousekey, etc.) are NOT stored in boards.yaml. They remain in firmware-specific config files: `qmk/config/boards/<board>.mk` and `zmk/config/boards/<board>.conf`.
- Extensions are **automatically inferred** from `layout_size`: If layout_size is "3x6_3", the system automatically applies `extensions["3x6_3"]` from layer definitions.

**Validation Rules**:
- `id` must be unique across all boards
- If `firmware == "qmk"`, `qmk_keyboard` is required
- If `firmware == "zmk"`, `zmk_shield` is required
- `layout_size` must match one of: "3x5_3" (36-key base), "3x5_3_pinky" (38-key), "3x6_3" (42-key), or "custom_*" for special layouts

**Python Representation**:
```python
@dataclass
class Board:
    id: str
    name: str
    firmware: Literal["qmk", "zmk"]
    layout_size: str = "3x5_3"  # Default to 36-key
    extra_layers: List[str] = field(default_factory=list)

    # Firmware-specific fields
    qmk_keyboard: Optional[str] = None
    zmk_shield: Optional[str] = None

    def get_extensions(self) -> List[str]:
        """Infer which extensions to apply based on layout_size"""
        if self.layout_size == "3x5_3":
            return []  # Base 36-key, no extensions
        elif self.layout_size == "3x5_3_pinky":
            return ["3x5_3_pinky"]  # 38-key
        elif self.layout_size == "3x6_3":
            return ["3x6_3"]  # 42-key
        elif self.layout_size.startswith("custom_"):
            return []  # Custom layouts use board-specific wrappers
        else:
            return []  # Unknown - assume base layout

    def validate(self):
        if self.firmware == "qmk" and not self.qmk_keyboard:
            raise ValidationError(f"Board {self.id}: qmk_keyboard required for QMK firmware")
        if self.firmware == "zmk" and not self.zmk_shield:
            raise ValidationError(f"Board {self.id}: zmk_shield required for ZMK firmware")

    def get_output_directory(self) -> str:
        """Get the output directory for generated keymaps"""
        if self.firmware == "qmk":
            # Replace slashes with underscores for directory name
            safe_name = self.qmk_keyboard.replace("/", "_")
            return f"qmk/keymaps/{safe_name}_dario"
        else:  # zmk
            return f"zmk/keymaps/{self.zmk_shield}_dario"
```

**YAML Example**:
```yaml
boards:
  skeletyl:
    name: "Bastard Keyboards Skeletyl"
    firmware: qmk
    qmk_keyboard: "bastardkb/skeletyl/promicro"
    layout_size: "3x5_3"  # 36-key base (no extensions applied)

  corne:
    name: "Corne (CRKBD)"
    firmware: zmk
    zmk_shield: "corne"
    layout_size: "3x6_3"  # 42-key (automatically applies extensions["3x6_3"])

  lulu:
    name: "Boardsource Lulu (RP2040)"
    firmware: qmk
    qmk_keyboard: "boardsource/lulu/rp2040"
    layout_size: "custom_58"  # 58-key custom (uses board-specific wrapper)
    extra_layers: ["GAME"]
```

**Firmware-specific features are configured separately**:
```make
# qmk/config/boards/skeletyl.mk
BOOTMAGIC_ENABLE = yes
MOUSEKEY_ENABLE = yes

# qmk/config/boards/lulu.mk
OLED_ENABLE = yes
RGB_MATRIX_ENABLE = yes
```

---

### 5. BehaviorAlias

Defines firmware-agnostic keycode aliases that translate to firmware-specific syntax.

**Fields**:
- `alias_name`: `str` - The alias prefix (e.g., "hrm", "lt", "bt")
- `description`: `str` - Human-readable description
- `params`: `List[str]` - Parameter names (e.g., ["mod", "key"])
- `qmk_pattern`: `str` - QMK C code pattern (e.g., "{mod}_T(KC_{key})")
- `zmk_pattern`: `str` - ZMK devicetree pattern (e.g., "&hrm {mod} {key}")
- `firmware_support`: `List[str]` - Supported firmwares (default: ["qmk", "zmk"])

**Python Representation**:
```python
@dataclass
class BehaviorAlias:
    alias_name: str
    description: str
    params: List[str]
    qmk_pattern: str
    zmk_pattern: str
    firmware_support: List[str] = field(default_factory=lambda: ["qmk", "zmk"])

    def translate_qmk(self, **kwargs) -> str:
        """
        Translate to QMK syntax
        Example: translate_qmk(mod="LGUI", key="A") -> "LGUI_T(KC_A)"
        """
        if "qmk" not in self.firmware_support:
            return "KC_NO"  # Filter unsupported
        return self.qmk_pattern.format(**kwargs)

    def translate_zmk(self, **kwargs) -> str:
        """
        Translate to ZMK syntax
        Example: translate_zmk(mod="LGUI", key="A") -> "&hrm LGUI A"
        """
        if "zmk" not in self.firmware_support:
            return "&none"  # Filter unsupported
        return self.zmk_pattern.format(**kwargs)
```

**Example Aliases**:
```python
HOMEROW_MOD = BehaviorAlias(
    alias_name="hrm",
    description="Homerow mod (hold for modifier, tap for key)",
    params=["mod", "key"],
    qmk_pattern="{mod}_T(KC_{key})",
    zmk_pattern="&hrm {mod} {key}"
)

LAYER_TAP = BehaviorAlias(
    alias_name="lt",
    description="Layer-tap (hold for layer, tap for key)",
    params=["layer", "key"],
    qmk_pattern="LT({layer}, KC_{key})",
    zmk_pattern="&lt {layer} {key}"
)

BLUETOOTH = BehaviorAlias(
    alias_name="bt",
    description="Bluetooth control (ZMK-only)",
    params=["action"],
    qmk_pattern="KC_NO",  # Always filtered
    zmk_pattern="&bt BT_{action}",
    firmware_support=["zmk"]  # ZMK-only
)
```

---

### 6. CompiledLayer

Represents a layer after extensions have been applied and keycodes compiled for a specific board.

**Fields**:
- `name`: `str` - Layer name
- `board`: `Board` - Target board
- `keycodes`: `List[str]` - Flattened list of keycodes (already translated to firmware syntax)
- `firmware`: `Literal["qmk", "zmk"]` - Target firmware

**Python Representation**:
```python
@dataclass
class CompiledLayer:
    name: str
    board: Board
    keycodes: List[str]  # Already translated (e.g., "LGUI_T(KC_A)" for QMK)
    firmware: Literal["qmk", "zmk"]

    def __len__(self) -> int:
        return len(self.keycodes)

    def format_for_qmk(self) -> str:
        """Format as QMK LAYOUT_* macro call"""
        # Implementation in generator
        pass

    def format_for_zmk(self) -> str:
        """Format as ZMK devicetree bindings"""
        # Implementation in generator
        pass
```

---

## Data Transformations

### Layer Compilation Pipeline

```
KeymapConfiguration (YAML)
    │
    ├─> Layer.core (36 keys)
    │       │
    │       └─> Apply board.extensions
    │               │
    │               └─> CompiledLayer (36+ keys)
    │                       │
    │                       └─> Translate keycodes (unified → firmware)
    │                               │
    │                               ├─> QMK: LGUI_T(KC_A), LT(NAV, KC_SPC)
    │                               └─> ZMK: &hrm LGUI A, &lt NAV SPC
    │
    └─> GeneratedKeymap (QMK/ZMK files)
```

**Pseudocode**:
```python
def compile_layer(layer: Layer, board: Board, firmware: str) -> CompiledLayer:
    """Compile a layer for a specific board and firmware"""

    # 1. Start with core layout (36 keys)
    keycodes = layer.core.flatten()

    # 2. Apply extensions if board requires them
    for ext_name in board.extensions:
        if ext_name in layer.extensions:
            extension = layer.extensions[ext_name]
            keycodes.extend(extension.get_keys_for_board(board))

    # 3. Translate to firmware-specific syntax
    translator = get_translator(firmware)
    translated = [translator.translate(kc) for kc in keycodes]

    # 4. Validate complex keybindings (FR-007)
    validate_complex_keybindings(translated, firmware)

    return CompiledLayer(
        name=layer.name,
        board=board,
        keycodes=translated,
        firmware=firmware
    )
```

---

## Validation Rules Summary

### KeymapConfiguration Validation
- ✅ At least one layer defined
- ✅ `BASE` layer is required
- ✅ Layer names are valid C identifiers
- ✅ No duplicate layer names

### Layer Validation
- ✅ Core layout has exactly 36 keys
- ✅ All keycodes are valid (either simple or aliased)
- ✅ Extension types match board requirements

### Board Validation
- ✅ Unique board IDs
- ✅ Firmware-specific fields present (qmk_keyboard or zmk_shield)
- ✅ Referenced extensions exist in layer definitions
- ✅ Features are valid for the firmware type

### Keycode Validation
- ✅ Simple keycodes: Match pattern `[A-Z0-9_]+` or `KC_[A-Z0-9_]+`
- ✅ Aliased keycodes: Match pattern `alias:param1:param2:...`
- ✅ Complex keybindings (hrm, lt): Validate firmware compatibility
- ✅ Firmware-specific keycodes: Validate support

**Validation Error Examples**:
```python
# Invalid layer name
ValidationError("Invalid layer name: base")  # Must be uppercase

# Missing required layer
ValidationError("BASE layer is required")

# Wrong core size
ValidationError("Layer NAV core must have exactly 36 keys, found 35")

# Invalid board config
ValidationError("Board lulu: qmk_keyboard required for QMK firmware")

# Firmware incompatibility (FR-007)
ValidationError("Layer NAV: hrm:LGUI:A uses ZMK-only behavior &hrm not supported in QMK")
```

---

## State Transitions

### Configuration Lifecycle

```
1. [YAML Files]
     ↓ parse
2. [In-Memory Data Model]
     ↓ validate
3. [Validated Configuration]
     ↓ compile (per board)
4. [CompiledLayers]
     ↓ generate
5. [Generated Files] (keymap.c, .keymap)
     ↓ build (QMK/ZMK toolchain)
6. [Firmware Binaries] (.hex, .uf2)
```

---

## Summary

**Core Entities**:
1. `KeymapConfiguration` - Unified keymap definition
2. `Layer` - Individual keyboard layer with core + extensions
3. `LayerExtension` - Additional keys for larger boards
4. `Board` - Physical keyboard configuration
5. `BehaviorAlias` - Firmware-agnostic keycode translation
6. `CompiledLayer` - Firmware-ready layer output

**Key Relationships**:
- Configuration **contains** Layers
- Layers **have** Extensions
- Boards **reference** Extensions
- Compilation **transforms** Layers → CompiledLayers using Aliases

**Validation Strategy**:
- Schema validation (structure, required fields)
- Business logic validation (36-key requirement, extension compatibility)
- Firmware compatibility validation (FR-007)
- Build verification (integration testing)

**Next Steps**: Define API contracts (generator interfaces)
