"""
Configuration validator

Validates keymap and board configuration for correctness
"""

from typing import Dict, List, Optional
from data_model import KeyGrid, Layer, LayerExtension, Board


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class ConfigValidator:
    """Validate configuration files"""

    def validate_keymap_config(self, layers: Dict[str, Layer]) -> None:
        """
        Validate keymap configuration

        Args:
            layers: Dictionary of layer name to Layer object

        Raises:
            ValidationError: If validation fails
        """
        # Schema validation
        if not layers:
            raise ValidationError("At least one layer must be defined")

        # At least one BASE layer is required (BASE, BASE_COLEMAK, BASE_GALLIUM, etc.)
        base_layers = [name for name in layers if name.startswith("BASE")]
        if not base_layers:
            raise ValidationError("At least one BASE layer is required (e.g., BASE, BASE_COLEMAK, BASE_GALLIUM)")

        # Validate layer names are valid C identifiers
        for layer_name in layers:
            if not self._is_valid_c_identifier(layer_name):
                raise ValidationError(
                    f"Invalid layer name: '{layer_name}'. "
                    f"Layer names must be uppercase alphanumeric with underscores"
                )

        # Validate each layer
        for layer_name, layer in layers.items():
            self._validate_layer(layer_name, layer)

    def validate_board_config(self, boards: List[Board]) -> None:
        """
        Validate board configuration

        Args:
            boards: List of Board objects

        Raises:
            ValidationError: If validation fails
        """
        if not boards:
            raise ValidationError("At least one board must be defined")

        # Check for duplicate board IDs
        board_ids = [board.id for board in boards]
        duplicates = set([bid for bid in board_ids if board_ids.count(bid) > 1])
        if duplicates:
            raise ValidationError(f"Duplicate board IDs found: {duplicates}")

        # Validate each board
        for board in boards:
            self._validate_board(board)

    def _validate_layer(self, layer_name: str, layer: Layer) -> None:
        """
        Validate a single layer

        Args:
            layer_name: Name of the layer
            layer: Layer object

        Raises:
            ValidationError: If validation fails
        """
        # Validate layer has either core or full_layout
        if not layer.core and not layer.full_layout:
            raise ValidationError(f"Layer {layer_name}: must have either 'core' or 'full_layout'")

        # Validate core has exactly 36 keys (if provided)
        if layer.core:
            flat_core = layer.core.flatten()
            if len(flat_core) != 36:
                raise ValidationError(
                    f"Layer {layer_name}: core must have exactly 36 keys, found {len(flat_core)}"
                )

            # Validate all keycodes are strings
            for i, keycode in enumerate(flat_core):
                if not isinstance(keycode, str):
                    raise ValidationError(
                        f"Layer {layer_name}: keycode at position {i} must be a string, "
                        f"got {type(keycode).__name__}"
                    )

        # Validate full_layout if provided
        if layer.full_layout:
            flat_full = layer.full_layout.flatten()
            # Validate all keycodes in full_layout are strings
            for i, keycode in enumerate(flat_full):
                if not isinstance(keycode, str):
                    raise ValidationError(
                        f"Layer {layer_name}: full_layout keycode at position {i} must be a string, "
                        f"got {type(keycode).__name__}"
                    )

        # Validate extensions
        for ext_name, extension in layer.extensions.items():
            self._validate_extension(layer_name, ext_name, extension)

    def _validate_extension(
        self,
        layer_name: str,
        ext_name: str,
        extension: LayerExtension
    ) -> None:
        """
        Validate a layer extension

        Args:
            layer_name: Name of the layer
            ext_name: Name of the extension
            extension: LayerExtension object

        Raises:
            ValidationError: If validation fails
        """
        if ext_name == "3x6_3":
            # 42-key: 3-key outer pinky column per side
            required = {"outer_pinky_left", "outer_pinky_right"}
            if not required.issubset(extension.keys.keys()):
                raise ValidationError(
                    f"Layer {layer_name}: extension 3x6_3 requires: {required}"
                )
            for pos in required:
                if not isinstance(extension.keys[pos], list) or len(extension.keys[pos]) != 3:
                    raise ValidationError(
                        f"Layer {layer_name}: extension 3x6_3 "
                        f"{pos} must be a list of exactly 3 keys"
                    )

    def _validate_board(self, board: Board) -> None:
        """
        Validate a single board

        Args:
            board: Board object

        Raises:
            ValidationError: If validation fails
        """
        # Validate board ID
        if not board.id:
            raise ValidationError("Board ID is required")

        if not self._is_valid_board_id(board.id):
            raise ValidationError(
                f"Invalid board ID: '{board.id}'. "
                f"Board IDs must be lowercase alphanumeric with underscores"
            )

        # Validate firmware-specific fields
        if board.firmware == "qmk":
            if not board.qmk_keyboard:
                raise ValidationError(
                    f"Board {board.id}: qmk_keyboard is required for QMK firmware"
                )
        elif board.firmware == "zmk":
            if not board.zmk_shield and not board.zmk_board:
                raise ValidationError(
                    f"Board {board.id}: either zmk_shield or zmk_board is required for ZMK firmware"
                )
        else:
            raise ValidationError(
                f"Board {board.id}: invalid firmware type '{board.firmware}'. "
                f"Must be 'qmk' or 'zmk'"
            )

        # Validate layout_size
        valid_sizes = ["3x5_3", "3x6_3", "totem_38"]
        if not (board.layout_size in valid_sizes or board.layout_size.startswith("custom_")):
            raise ValidationError(
                f"Board {board.id}: invalid layout_size '{board.layout_size}'. "
                f"Must be one of {valid_sizes} or start with 'custom_'"
            )

    def _is_valid_c_identifier(self, name: str) -> bool:
        """
        Check if name is a valid C identifier

        Args:
            name: Name to check

        Returns:
            True if valid C identifier
        """
        if not name:
            return False

        # Must be uppercase for layer names
        if not name.isupper():
            return False

        # Must start with letter or underscore
        if not (name[0].isalpha() or name[0] == '_'):
            return False

        # Can only contain alphanumeric and underscore
        return all(c.isalnum() or c == '_' for c in name)

    def _is_valid_board_id(self, board_id: str) -> bool:
        """
        Check if board_id is valid

        Args:
            board_id: Board ID to check

        Returns:
            True if valid board ID
        """
        if not board_id:
            return False

        # Must be lowercase
        if not board_id.islower():
            return False

        # Can only contain lowercase alphanumeric and underscore
        return all(c.isalnum() or c == '_' for c in board_id)
