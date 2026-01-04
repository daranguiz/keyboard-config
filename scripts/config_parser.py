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


def _safe_loader_without_bools():
    """
    Return a SafeLoader that does not implicitly convert bare words like
    ON/OFF/YES/NO/TRUE/FALSE into booleans. This keeps multi-letter magic
    mappings (e.g., ON/ION) as plain strings.
    """
    class NoBoolSafeLoader(yaml.SafeLoader):
        pass

    # Strip bool resolvers
    for ch, resolvers in list(NoBoolSafeLoader.yaml_implicit_resolvers.items()):
        filtered = [r for r in resolvers if r[0] != 'tag:yaml.org,2002:bool']
        if filtered:
            NoBoolSafeLoader.yaml_implicit_resolvers[ch] = filtered
        else:
            NoBoolSafeLoader.yaml_implicit_resolvers.pop(ch, None)

    return NoBoolSafeLoader

from data_model import (
    KeyGrid,
    Layer,
    LayerExtension,
    Board,
    BoardInventory,
    KeymapConfiguration,
    BehaviorAlias,
    RowStaggerConfig,
    Combo,
    ComboConfiguration,
    ValidationError
)


class YAMLConfigParser:
    """Parser for YAML configuration files"""

    @staticmethod
    def parse_keymap(yaml_path: Path, overlay_path: Path = None) -> KeymapConfiguration:
        """
        Parse config/keymap.yaml with optional board-specific overlay

        Args:
            yaml_path: Path to main keymap.yaml (with core definitions)
            overlay_path: Optional path to board-specific keymap file (with full_layout definitions)

        Returns:
            KeymapConfiguration with all layers loaded (merged if overlay provided)
        """
        loader = _safe_loader_without_bools()
        with open(yaml_path, 'r') as f:
            data = yaml.load(f, Loader=loader)

        if not data or 'layers' not in data:
            raise ValidationError("keymap.yaml must contain 'layers' section")

        layers_data = data['layers']

        # If overlay provided, merge full_layout definitions
        if overlay_path and overlay_path.exists():
            with open(overlay_path, 'r') as f:
                overlay_data = yaml.safe_load(f)

            if overlay_data and 'layers' in overlay_data:
                overlay_layers = overlay_data['layers']

                # Merge: overlay full_layout takes precedence, but preserve core from main
                for layer_name, overlay_layer in overlay_layers.items():
                    if layer_name in layers_data:
                        # Add/override full_layout to existing layer
                        if 'full_layout' in overlay_layer:
                            layers_data[layer_name]['full_layout'] = overlay_layer['full_layout']
                    else:
                        # New layer only in overlay
                        layers_data[layer_name] = overlay_layer

        layers = {}
        for layer_name, layer_data in layers_data.items():
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

            # Parse full_layout (for special layers like GAME, or boards with position references)
            if 'full_layout' in layer_data:
                full_rows = layer_data['full_layout']
                if not isinstance(full_rows, list):
                    raise ValidationError(f"Layer {layer_name}: 'full_layout' must be a list")
                # full_layout is a flat list of keycodes, but KeyGrid expects rows (list of lists)
                # Wrap it in a single row
                full_layout = KeyGrid(rows=[full_rows])

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
                keymap_file=board_data.get('keymap_file'),  # Board-specific keymap file
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

    @staticmethod
    def parse_combos(yaml_path: Path) -> ComboConfiguration:
        """
        Parse combo definitions from config/keymap.yaml

        Args:
            yaml_path: Path to keymap.yaml

        Returns:
            ComboConfiguration with all combo definitions

        The combos section is optional. If not present, returns empty ComboConfiguration.
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Combos section is optional
        if not data or 'combos' not in data:
            return ComboConfiguration(combos=[])

        combos_data = data['combos']
        if not isinstance(combos_data, list):
            raise ValidationError("'combos' must be a list")

        combos = []
        for combo_data in combos_data:
            # Validate required fields
            required_fields = ['name', 'description', 'key_positions', 'action']
            for field in required_fields:
                if field not in combo_data:
                    raise ValidationError(
                        f"Combo definition missing required field: '{field}'"
                    )

            # Create combo
            combo = Combo(
                name=combo_data['name'],
                description=combo_data['description'],
                key_positions=combo_data['key_positions'],
                action=combo_data['action'],
                macro_text=combo_data.get('macro_text'),
                timeout_ms=combo_data.get('timeout_ms', 50),
                require_prior_idle_ms=combo_data.get('require_prior_idle_ms'),
                layers=combo_data.get('layers'),
                slow_release=combo_data.get('slow_release', False),
                hold_ms=combo_data.get('hold_ms'),  # DEPRECATED but kept for backwards compatibility
                training=combo_data.get('training', False)  # Default: training disabled
            )

            combo.validate()
            combos.append(combo)

        # Create configuration
        config = ComboConfiguration(combos=combos)
        config.validate()

        return config

    @staticmethod
    def parse_magic_keys(yaml_path: Path) -> 'MagicKeyConfiguration':
        """
        Parse magic key definitions from config/keymap.yaml

        Args:
            yaml_path: Path to keymap.yaml

        Returns:
            MagicKeyConfiguration with base-layer-specific magic key mappings

        The magic_keys section is optional. If not present, returns empty MagicKeyConfiguration.
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Magic keys section is optional
        if not data or 'magic_keys' not in data:
            from data_model import MagicKeyConfiguration
            return MagicKeyConfiguration(mappings={})

        magic_keys_data = data['magic_keys']
        if not isinstance(magic_keys_data, dict):
            raise ValidationError("'magic_keys' must be a dictionary mapping base layers to configurations")

        from data_model import MagicKeyMapping, MagicKeyConfiguration

        mappings = {}
        for base_layer, config in magic_keys_data.items():
            # Validate required fields
            if 'mappings' not in config:
                raise ValidationError(
                    f"Magic key configuration for {base_layer} missing required field: 'mappings'"
                )

            # Support new boolean default flag
            default_value = config.get('default')
            if default_value is None and 'default_repeat' in config:
                default_value = 'REPEAT' if config.get('default_repeat') else 'NONE'
            if default_value is None:
                default_value = 'REPEAT'

            # Create magic key mapping
            mapping = MagicKeyMapping(
                base_layer=base_layer,
                timeout_ms=config.get('timeout_ms', 150),
                mappings=config.get('mappings', {}),
                default=default_value
            )

            mapping.validate()
            mappings[base_layer] = mapping

        # Create configuration
        magic_config = MagicKeyConfiguration(mappings=mappings)
        magic_config.validate()

        return magic_config
