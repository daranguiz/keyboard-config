"""
Data model for unified keymap configuration system

This module defines the core data structures used throughout the generator.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal, Union


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
    """
    rows: List[List[str]]  # Nested list of keycode strings

    def __post_init__(self):
        """Normalize all values to strings (handles YAML integers like 0-9)"""
        self.rows = [[str(key) for key in row] for row in self.rows]

    def flatten(self) -> List[str]:
        """Flatten to single list of keycodes"""
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
    - 3x5_3_pinky: 38-key (36 + 1 outer pinky key per side)
    - 3x6_3: 42-key (36 + 3-key outer pinky column per side)
    """
    extension_type: str  # "3x5_3_pinky", "3x6_3", etc.
    keys: Dict[str, Union[str, List[str]]]

    def validate(self):
        """Validate extension structure"""
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

        # Cannot have both core and full_layout
        if self.core is not None and self.full_layout is not None:
            raise ValidationError(
                f"Layer {self.name} cannot have both 'core' and 'full_layout' - choose one"
            )

        # If using full_layout, extensions are not allowed
        if self.full_layout is not None and len(self.extensions) > 0:
            raise ValidationError(
                f"Layer {self.name} uses 'full_layout' - extensions are not allowed. "
                f"Full layouts must specify all keys directly."
            )

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
    - qmk_keyboard: QMK keyboard path (required for QMK boards)
    - zmk_shield: ZMK shield name (required for ZMK boards)
    """
    id: str
    name: str
    firmware: Literal["qmk", "zmk"]
    layout_size: str = "3x5_3"  # Default to 36-key
    extra_layers: List[str] = field(default_factory=list)

    # Firmware-specific fields
    qmk_keyboard: Optional[str] = None
    zmk_shield: Optional[str] = None
    zmk_board: Optional[str] = None  # For integrated ZMK boards (e.g., Corneish Zen)

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
