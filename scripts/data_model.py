"""
Data model for unified keymap configuration system

This module defines the core data structures used throughout the generator.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal, Union
import re


class ValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


@dataclass
class KeyGrid:
    """
    Represents a grid of keys as nested lists
    For 3x5_3 layout (36-key):
      - rows[0:3]: left hand columns (3 rows × 5 cols)
      - rows[3:6]: right hand columns (3 rows × 5 cols)
      - rows[6]: left thumb keys (3 keys)
      - rows[7]: right thumb keys (3 keys)

    Supports position references like L36_0 which are preserved as dicts.
    """
    rows: List[List[Union[str, Dict[str, Any]]]]  # Nested list of keycodes or position references

    # Pattern for position references (e.g., L36_5)
    POSITION_REF_PATTERN = re.compile(r'^L36_(\d+)$')

    def __post_init__(self):
        """
        Normalize all values to strings or position reference dicts
        Handles YAML integers like 0-9 and parses L36_N syntax
        """
        self.rows = [[self._parse_keycode(key) for key in row] for row in self.rows]

    def _parse_keycode(self, value: Any) -> Union[str, Dict[str, Any]]:
        """Parse a keycode, handling position references like L36_N"""
        if isinstance(value, str):
            # Check for position reference pattern
            match = self.POSITION_REF_PATTERN.match(value)
            if match:
                index = int(match.group(1))
                if index < 0 or index > 35:
                    raise ValidationError(f"L36 index out of range: {index} (must be 0-35)")
                return {"_ref": "L36", "index": index}
            # Regular keycode string
            return value
        else:
            # Convert non-strings (like integers) to strings
            return str(value)

    def flatten(self) -> List[Union[str, Dict[str, Any]]]:
        """Flatten to single list of keycodes (may include position references)"""
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


@dataclass
class LayerExtension:
    """
    Represents additional keys for boards larger than 36-key

    Extension types:
    - 3x6_3: 42-key (36 + 3-key outer pinky column per side)
    """
    extension_type: str  # "3x6_3", etc.
    keys: Dict[str, Union[str, List[str]]]

    def validate(self):
        """Validate extension structure"""
        if self.extension_type == "3x6_3":
            required = {"outer_pinky_left", "outer_pinky_right"}
            if not required.issubset(self.keys.keys()):
                raise ValidationError(f"3x6_3 requires: {required}")
            for pos in required:
                if not isinstance(self.keys[pos], list) or len(self.keys[pos]) != 3:
                    raise ValidationError(f"{pos} must be a list of exactly 3 keys")

    def get_keys_for_board(self) -> List[str]:
        """Flatten extension keys to a list"""
        result = []
        for position, keys in self.keys.items():
            if isinstance(keys, list):
                result.extend(keys)
            else:
                result.append(keys)
        return result


@dataclass
class Layer:
    """
    Represents a single keyboard layer (e.g., BASE, NAV, NUM)

    Fields:
    - name: Layer identifier (e.g., "BASE", "NAV")
    - core: The 36-key core layout (optional if full_layout is provided)
    - full_layout: Complete keyboard layout (for special layers like GAME)
    - extensions: Optional extensions for larger boards
    """
    name: str
    core: Optional[KeyGrid] = None  # 36 keys in 4 rows (3x5 left, 3x5 right, 3+3 thumbs)
    full_layout: Optional[KeyGrid] = None  # Full layout for special layers (e.g., 58 keys)
    extensions: Dict[str, LayerExtension] = field(default_factory=dict)

    def validate(self):
        """Validate layer structure"""
        # Either core or full_layout must be provided (but not both)
        if self.core is None and self.full_layout is None:
            raise ValidationError(
                f"Layer {self.name} must have either 'core' or 'full_layout' defined"
            )

        # Note: Layers CAN have both core and full_layout when using L36() position references
        # The core provides the reference data, and full_layout uses it via L36(n) syntax
        # Old validation prevented this, but we now allow it for custom boards with position references

        # Note: When using L36() position references, layers can have both full_layout and extensions
        # The extensions are for other boards (like 3x6_3), while full_layout is for custom boards
        # We allow this combination to support the unified keymap system
        # Old validation: "full_layout cannot have extensions" - now relaxed for flexibility

        # If core is provided, validate it's 36 keys
        if self.core is not None and len(self.core.flatten()) != 36:
            raise ValidationError(
                f"Layer {self.name} core must have exactly 36 keys, found {len(self.core.flatten())}"
            )

        # Validate layer name (must be valid C identifier)
        if not self.name.isupper() or not self.name.replace("_", "").isalnum():
            raise ValidationError(f"Invalid layer name: {self.name}")


@dataclass
class Board:
    """
    Represents a physical keyboard configuration

    Fields:
    - id: Unique board identifier (e.g., "skeletyl", "lulu")
    - name: Human-readable name
    - firmware: Target firmware ("qmk" or "zmk")
    - layout_size: Physical layout size (e.g., "3x5_3", "3x6_3", "custom_58")
    - extra_layers: Board-specific additional layers (e.g., ["GAME"])
    - keymap_file: Optional board-specific keymap file (e.g., "boaty.yaml")
    - qmk_keyboard: QMK keyboard path (required for QMK boards)
    - zmk_shield: ZMK shield name (required for ZMK boards)
    """
    id: str
    name: str
    firmware: Literal["qmk", "zmk"]
    layout_size: str = "3x5_3"  # Default to 36-key
    extra_layers: List[str] = field(default_factory=list)
    keymap_file: Optional[str] = None  # Board-specific keymap file (e.g., "boaty.yaml")

    # Firmware-specific fields
    qmk_keyboard: Optional[str] = None
    zmk_shield: Optional[str] = None
    zmk_board: Optional[str] = None  # For integrated ZMK boards (e.g., Corneish Zen)

    def get_extensions(self) -> List[str]:
        """Infer which extensions to apply based on layout_size"""
        if self.layout_size == "3x5_3":
            return []  # Base 36-key, no extensions
        elif self.layout_size == "3x6_3":
            return ["3x6_3"]  # 42-key
        elif self.layout_size.startswith("custom_"):
            return []  # Custom layouts use board-specific wrappers
        else:
            return []  # Unknown - assume base layout

    def validate(self):
        """Validate board configuration"""
        if self.firmware == "qmk" and not self.qmk_keyboard:
            raise ValidationError(f"Board {self.id}: qmk_keyboard required for QMK firmware")
        if self.firmware == "zmk" and not self.zmk_shield and not self.zmk_board:
            raise ValidationError(f"Board {self.id}: either zmk_shield or zmk_board required for ZMK firmware")

    def get_output_directory(self) -> str:
        """Get the output directory for generated keymaps"""
        if self.firmware == "qmk":
            # QMK userspace root is qmk/ (set via QMK_USERSPACE environment variable)
            # Within that, QMK requires: keyboards/<keyboard>/keymaps/<keymap_name>
            return f"qmk/keyboards/{self.qmk_keyboard}/keymaps/dario"
        else:  # zmk
            # ZMK keymaps go in zmk/keymaps/
            return f"zmk/keymaps/{self.zmk_shield}_dario"


@dataclass
class CompiledLayer:
    """
    Represents a layer after extensions have been applied and keycodes compiled

    Fields:
    - name: Layer name
    - board: Target board
    - keycodes: Flattened list of keycodes (already translated to firmware syntax)
    - firmware: Target firmware
    """
    name: str
    board: Board
    keycodes: List[str]  # Already translated (e.g., "LGUI_T(KC_A)" for QMK)
    firmware: Literal["qmk", "zmk"]

    def __len__(self) -> int:
        return len(self.keycodes)


@dataclass
class KeymapConfiguration:
    """
    Represents the unified keymap definition from config/keymap.yaml

    Fields:
    - layers: All layer definitions indexed by layer name
    - metadata: Optional metadata (author, version, description)
    """
    layers: Dict[str, Layer]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self):
        """Validate keymap configuration"""
        if not self.layers:
            raise ValidationError("At least one layer must be defined")

        # At least one BASE layer is required (BASE, BASE_COLEMAK, BASE_GALLIUM, etc.)
        base_layers = [name for name in self.layers if name.startswith("BASE")]
        if not base_layers:
            raise ValidationError("At least one BASE layer is required (e.g., BASE, BASE_COLEMAK, BASE_GALLIUM)")

        # Validate all layers
        for layer in self.layers.values():
            layer.validate()


@dataclass
class BoardInventory:
    """
    Represents the board inventory from config/boards.yaml

    Fields:
    - boards: Dictionary of board configurations indexed by board ID
    """
    boards: Dict[str, Board]

    def validate(self):
        """Validate board inventory"""
        if not self.boards:
            raise ValidationError("At least one board must be defined")

        # Validate all boards
        for board in self.boards.values():
            board.validate()

    def get_by_id(self, board_id: str) -> Optional[Board]:
        """Get board by ID"""
        return self.boards.get(board_id)

    def get_by_firmware(self, firmware: Literal["qmk", "zmk"]) -> List[Board]:
        """Get all boards for a specific firmware"""
        return [b for b in self.boards.values() if b.firmware == firmware]


@dataclass
class BehaviorAlias:
    """
    Defines firmware-agnostic keycode aliases

    Fields:
    - alias_name: The alias prefix (e.g., "hrm", "lt", "bt")
    - description: Human-readable description
    - params: Parameter names (e.g., ["mod", "key"])
    - qmk_pattern: QMK C code pattern (e.g., "{mod}_T(KC_{key})")
    - zmk_pattern: ZMK devicetree pattern (e.g., "&hrm {mod} {key}")
    - firmware_support: Supported firmwares (default: ["qmk", "zmk"])
    """
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

        Special handling for MAGIC key: KC_MAGIC → QK_AREP
        """
        if "qmk" not in self.firmware_support:
            return "KC_NO"  # Filter unsupported
        result = self.qmk_pattern.format(**kwargs)
        # Special case: replace KC_MAGIC with QK_AREP for alternate repeat key
        result = result.replace("KC_MAGIC", "QK_AREP")
        return result

    def translate_zmk(self, **kwargs) -> str:
        """
        Translate to ZMK syntax
        Example: translate_zmk(mod="LGUI", key="A") -> "&hrm LGUI A"
        """
        if "zmk" not in self.firmware_support:
            return "&none"  # Filter unsupported
        return self.zmk_pattern.format(**kwargs)


@dataclass
class RowStaggerConfig:
    """
    Represents a row-staggered keyboard layout configuration for macOS .keylayout generation

    Fields:
    - name: Layout name (e.g., "Nightlife", "Colemak")
    - id: macOS keyboard ID (e.g., "-12407")
    - group: macOS keyboard group (e.g., "126")
    - layout: Base layer layout - 3 rows mapping to QWERTY positions
      Row 1: q w e r t y u i o p [ ] (12 keys)
      Row 2: a s d f g h j k l ; ' (11 keys)
      Row 3: z x c v b n m , . / (10 keys)
    - fingermap: Optional finger assignment for each key (0-7)
      0=L-pinky, 1=L-ring, 2=L-middle, 3=L-index
      4=R-index, 5=R-middle, 6=R-ring, 7=R-pinky

    Shift layer is auto-inferred from base layer:
    - Letters: uppercase
    - Symbols: standard shift mappings (, → <, [ → {, etc.)

    Number row stays as standard QWERTY (1234567890-=)
    All other keys (modifiers, space, enter, etc.) stay standard ANSI
    """
    name: str
    id: str
    group: str
    layout: List[List[str]]  # 3 rows of keys
    fingermap: Optional[List[List[int]]] = None  # 3 rows of finger assignments (0-7)

    def __post_init__(self):
        """Normalize all values to strings (handles YAML integers)"""
        self.layout = [[str(key) for key in row] for row in self.layout]
        if self.fingermap is not None:
            self.fingermap = [[int(f) for f in row] for row in self.fingermap]

    def validate(self):
        """Validate row-stagger configuration"""
        if len(self.layout) != 3:
            raise ValidationError(
                f"Row-stagger layout must have exactly 3 rows, found {len(self.layout)}"
            )

        # Validate row lengths
        expected_lengths = [12, 11, 10]  # q-], a-', z-/
        for i, (row, expected) in enumerate(zip(self.layout, expected_lengths)):
            if len(row) != expected:
                raise ValidationError(
                    f"Row {i+1} must have {expected} keys, found {len(row)}"
                )


@dataclass
class Combo:
    """
    Represents a key combination that triggers an action

    Fields:
    - name: Combo identifier (e.g., "dfu_left")
    - description: Human-readable description
    - key_positions: List of key positions using canonical 36-key numbering (0-35)
                     Row-wise: [0-9] = row 0, [10-19] = row 1, [20-29] = row 2, [30-35] = thumbs
    - action: Action keycode or behavior (e.g., "DFU", "ESC", "MACRO_NAME")
    - macro_text: Optional text to expand (enables text expansion macro)
    - timeout_ms: Time window to press all keys simultaneously (default: 50ms)
    - require_prior_idle_ms: ZMK-only: prevent combo if keys pressed within this window (e.g., 150ms)
    - layers: List of layer names where combo is active (None = all layers)
    - slow_release: ZMK-specific: require all keys released simultaneously (default: False)
    - hold_ms: DEPRECATED - use standard instant combos instead
    """
    name: str
    description: str
    key_positions: List[int]  # Canonical 36-key positions (0-35)
    action: str  # Keycode or behavior name
    macro_text: Optional[str] = None  # Text to expand for macros
    timeout_ms: int = 50  # Standard combo timeout
    require_prior_idle_ms: Optional[int] = None  # ZMK: prevent combo during fast typing
    layers: Optional[List[str]] = None  # None = active on all layers
    slow_release: bool = False  # ZMK: require simultaneous release
    hold_ms: Optional[int] = None  # DEPRECATED: For backwards compatibility

    def validate(self):
        """Validate combo configuration"""
        # Validate positions are in range 0-35
        for pos in self.key_positions:
            if pos < 0 or pos > 35:
                raise ValidationError(
                    f"Combo {self.name}: position {pos} out of range (must be 0-35)"
                )

        # Validate at least 2 keys
        if len(self.key_positions) < 2:
            raise ValidationError(
                f"Combo {self.name}: must have at least 2 keys"
            )

        # Validate timeout
        if self.timeout_ms < 1:
            raise ValidationError(
                f"Combo {self.name}: timeout_ms must be positive"
            )

        # Validate macro_text if specified
        if self.macro_text is not None and len(self.macro_text) == 0:
            raise ValidationError(
                f"Combo {self.name}: macro_text cannot be empty"
            )

        # Validate hold_ms if specified
        if self.hold_ms is not None and self.hold_ms < 1:
            raise ValidationError(
                f"Combo {self.name}: hold_ms must be positive"
            )


@dataclass
class ComboConfiguration:
    """
    Collection of all combo definitions from config/keymap.yaml

    Fields:
    - combos: List of Combo objects
    """
    combos: List[Combo] = field(default_factory=list)

    def validate(self):
        """Validate combo configuration"""
        # Validate all combos
        for combo in self.combos:
            combo.validate()

        # Check for duplicate combo names
        names = [c.name for c in self.combos]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            raise ValidationError(
                f"Duplicate combo names found: {set(duplicates)}"
            )

    def get_by_name(self, name: str) -> Optional[Combo]:
        """Get combo by name"""
        for combo in self.combos:
            if combo.name == name:
                return combo
        return None


@dataclass
class MagicKeyMapping:
    """
    Magic key configuration for a specific base layer

    Fields:
    - base_layer: Base layer name (e.g., "BASE_NIGHT", "BASE_GALLIUM")
    - timeout_ms: Maximum time between previous key and magic key press
    - mappings: Dict mapping previous key → alternate key
    - default: Default behavior (REPEAT, NONE, or specific keycode)
    """
    base_layer: str
    timeout_ms: int
    mappings: Dict[str, str]  # previous_key → alternate_key
    default: str = "REPEAT"  # Default action

    def validate(self):
        """Validate magic key mapping"""
        # Validate timeout
        if self.timeout_ms < 1:
            raise ValidationError(
                f"Magic key {self.base_layer}: timeout_ms must be positive"
            )

        # Validate mappings is non-empty
        if not self.mappings:
            raise ValidationError(
                f"Magic key {self.base_layer}: mappings cannot be empty"
            )

        # Validate default action
        valid_defaults = ["REPEAT", "NONE"]
        if self.default not in valid_defaults and not self.default.startswith("KC_"):
            raise ValidationError(
                f"Magic key {self.base_layer}: invalid default '{self.default}'"
            )


@dataclass
class MagicKeyConfiguration:
    """
    Collection of all magic key mappings from config/keymap.yaml

    Fields:
    - mappings: Dict of base_layer → MagicKeyMapping
    """
    mappings: Dict[str, MagicKeyMapping] = field(default_factory=dict)

    def validate(self):
        """Validate all magic key mappings"""
        for base_layer, mapping in self.mappings.items():
            mapping.validate()

    def get_mapping_for_layer(self, layer_name: str) -> Optional[MagicKeyMapping]:
        """
        Get magic key mapping for a given layer name.
        Supports derived layers (e.g., NUM_NIGHT uses BASE_NIGHT mapping)
        """
        # Direct match
        if layer_name in self.mappings:
            return self.mappings[layer_name]

        # Check for base layer prefix (NUM_NIGHT → BASE_NIGHT)
        for base_layer in self.mappings:
            if layer_name.endswith(base_layer.replace("BASE_", "")):
                return self.mappings[base_layer]

        return None
