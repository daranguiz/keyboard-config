"""
YAML configuration parser for unified keymap system

This module handles parsing of:
- config/keymap.yaml: Layer definitions
- config/boards.yaml: Board inventory
- config/aliases.yaml: Behavior aliases
"""

from pathlib import Path
from typing import Dict, List
import yaml

from data_model import (
    KeyGrid,
    Layer,
    LayerExtension,
    Board,
    BoardInventory,
    KeymapConfiguration,
    BehaviorAlias,
    RowStaggerConfig,
    ValidationError
)


class YAMLConfigParser:
    """Parser for YAML configuration files"""

    @staticmethod
    def parse_keymap(yaml_path: Path) -> KeymapConfiguration:
        """
        Parse config/keymap.yaml

        Returns:
            KeymapConfiguration with all layers loaded
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'layers' not in data:
            raise ValidationError("keymap.yaml must contain 'layers' section")

        layers = {}
        for layer_name, layer_data in data['layers'].items():
            core = None
            full_layout = None

            # Parse core layout (for normal layers)
            if 'core' in layer_data:
                core_data = layer_data['core']

                # Support both old format (list of rows) and new format (dict with left/right/thumbs)
                if isinstance(core_data, list):
                    # Old format: flat list of rows
                    core = KeyGrid(rows=core_data)
                elif isinstance(core_data, dict):
                    # New format: explicit left/right/thumbs sections
                    if 'left' not in core_data or 'right' not in core_data or 'thumbs' not in core_data:
                        raise ValidationError(
                            f"Layer {layer_name}: 'core' dict must have 'left', 'right', and 'thumbs' sections"
                        )

                    # Flatten to rows: left rows + right rows + thumb rows
                    core_rows = (
                        core_data['left'] +      # Left hand rows (3 rows for 3x5)
                        core_data['right'] +     # Right hand rows (3 rows for 3x5)
                        core_data['thumbs']      # Thumb rows (2 rows: left thumbs, right thumbs)
                    )
                    core = KeyGrid(rows=core_rows)
                else:
                    raise ValidationError(f"Layer {layer_name}: 'core' must be a list or dict")

            # Parse full_layout (for special layers like GAME)
            if 'full_layout' in layer_data:
                full_rows = layer_data['full_layout']
                if not isinstance(full_rows, list):
                    raise ValidationError(f"Layer {layer_name}: 'full_layout' must be a list of rows")
                full_layout = KeyGrid(rows=full_rows)

            # Validate that at least one layout type is provided
            if core is None and full_layout is None:
                raise ValidationError(f"Layer {layer_name}: must have either 'core' or 'full_layout'")

            # Parse extensions (optional)
            extensions = {}
            if 'extensions' in layer_data:
                for ext_type, ext_data in layer_data['extensions'].items():
                    extension = LayerExtension(
                        extension_type=ext_type,
                        keys=ext_data
                    )
                    extension.validate()
                    extensions[ext_type] = extension

            # Create layer
            layer = Layer(name=layer_name, core=core, full_layout=full_layout, extensions=extensions)
            layers[layer_name] = layer

        # Validate extension consistency across all layers
        # If any layer defines an extension type, ALL layers must define it
        all_extension_types = set()
        for layer in layers.values():
            all_extension_types.update(layer.extensions.keys())

        if all_extension_types:
            # Check that all layers have all extension types
            for layer_name, layer in layers.items():
                missing_extensions = all_extension_types - set(layer.extensions.keys())
                if missing_extensions:
                    raise ValidationError(
                        f"Layer {layer_name}: missing extension definitions for {missing_extensions}. "
                        f"All layers must define the same extension types. Define them with NONE values if unused."
                    )

        # Get metadata if present
        metadata = data.get('metadata', {})

        config = KeymapConfiguration(layers=layers, metadata=metadata)
        config.validate()

        return config

    @staticmethod
    def parse_boards(yaml_path: Path) -> BoardInventory:
        """
        Parse config/boards.yaml

        Returns:
            BoardInventory with all board configurations
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'boards' not in data:
            raise ValidationError("boards.yaml must contain 'boards' section")

        boards = {}
        for board_id, board_data in data['boards'].items():
            # Required fields
            if 'name' not in board_data:
                raise ValidationError(f"Board {board_id}: 'name' is required")
            if 'firmware' not in board_data:
                raise ValidationError(f"Board {board_id}: 'firmware' is required")

            # Create board
            board = Board(
                id=board_id,
                name=board_data['name'],
                firmware=board_data['firmware'],
                layout_size=board_data.get('layout_size', '3x5_3'),
                extra_layers=board_data.get('extra_layers', []),
                qmk_keyboard=board_data.get('qmk_keyboard'),
                zmk_shield=board_data.get('zmk_shield'),
                zmk_board=board_data.get('zmk_board')
            )

            board.validate()
            boards[board_id] = board

        inventory = BoardInventory(boards=boards)
        inventory.validate()

        return inventory

    @staticmethod
    def parse_aliases(yaml_path: Path) -> Dict[str, BehaviorAlias]:
        """
        Parse config/aliases.yaml

        Returns:
            Dictionary of BehaviorAlias objects indexed by alias name
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'behaviors' not in data:
            raise ValidationError("aliases.yaml must contain 'behaviors' section")

        aliases = {}
        for alias_name, alias_data in data['behaviors'].items():
            # Required fields
            required = ['description', 'qmk_pattern', 'zmk_pattern', 'params']
            for field in required:
                if field not in alias_data:
                    raise ValidationError(
                        f"Alias {alias_name}: '{field}' is required"
                    )

            # Create alias
            alias = BehaviorAlias(
                alias_name=alias_name,
                description=alias_data['description'],
                params=alias_data['params'],
                qmk_pattern=alias_data['qmk_pattern'],
                zmk_pattern=alias_data['zmk_pattern'],
                firmware_support=alias_data.get('firmware_support', ['qmk', 'zmk'])
            )

            aliases[alias_name] = alias

        return aliases

    @staticmethod
    def parse_special_keycodes(yaml_path: Path) -> Dict[str, Dict[str, str]]:
        """
        Parse special keycode mappings from config/aliases.yaml

        Returns:
            Dictionary of keycodes with their QMK and ZMK translations
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or 'keycodes' not in data:
            return {}  # Optional section

        return data['keycodes']

    @staticmethod
    def parse_keycodes(yaml_path: Path) -> Dict[str, Dict[str, str]]:
        """
        Parse comprehensive keycode mappings from config/keycodes.yaml

        The YAML is a flat mapping of key name -> {qmk: "...", zmk: "..."}.
        An empty string for a firmware means "not supported" and will be
        filtered by the translators.
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        if not data or not isinstance(data, dict):
            return {}

        return data

    @staticmethod
    def parse_rowstagger(yaml_path: Path) -> RowStaggerConfig:
        """
        Parse a row-staggered keyboard layout configuration

        Args:
            yaml_path: Path to YAML file (e.g., config/rowstagger/nightlife.yaml)

        Returns:
            RowStaggerConfig with layout definition

        Example YAML structure:
            name: "Nightlife"
            id: "-12407"
            group: "126"
            layout:
              - [f, d, l, g, v, q, r, u, o, ",", "[", "]"]  # Row 1 (12 keys)
              - [s, t, h, c, y, j, n, e, a, i, "'"]         # Row 2 (11 keys)
              - [z, k, m, p, w, x, b, ";", ".", /]          # Row 3 (10 keys)
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required_fields = ['name', 'id', 'group', 'layout']
        for field in required_fields:
            if field not in data:
                raise ValidationError(
                    f"Row-stagger config must contain '{field}' field"
                )

        # Validate layout is a list
        if not isinstance(data['layout'], list):
            raise ValidationError("'layout' must be a list of rows")

        # Create config
        config = RowStaggerConfig(
            name=data['name'],
            id=data['id'],
            group=data['group'],
            layout=data['layout'],
            fingermap=data.get('fingermap')  # Optional field
        )

        # Validate
        config.validate()

        return config
