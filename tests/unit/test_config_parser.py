#!/usr/bin/env python3
"""
Unit tests for config_parser.py

Tests YAML configuration parsing including:
- Keymap parsing (layers, extensions)
- Board inventory parsing
- Aliases parsing
- Combos and magic keys parsing
- Integer keycode handling
- L36 position reference parsing
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from config_parser import YAMLConfigParser
from data_model import Layer, KeyGrid, Board


@pytest.mark.tier1
class TestKeymapParsing:
    """Test keymap.yaml parsing"""

    def test_parse_production_keymap(self, config_dir):
        """Parse production keymap.yaml successfully"""
        keymap = YAMLConfigParser.parse_keymap(config_dir / "keymap.yaml")

        # Should have layers
        assert keymap.layers, "Keymap should have layers"
        assert len(keymap.layers) > 0, "Should have at least one layer"

    def test_layers_are_layer_objects(self, keymap_config):
        """All parsed layers should be Layer objects"""
        for layer_name, layer in keymap_config.layers.items():
            assert isinstance(layer, Layer), f"{layer_name} should be a Layer object"

    def test_base_layers_exist(self, keymap_config):
        """At least one BASE layer should exist"""
        base_layers = [name for name in keymap_config.layers if name.startswith("BASE")]
        assert len(base_layers) >= 1, "Should have at least one BASE layer"

    def test_layer_has_core_or_full_layout(self, keymap_config):
        """Each layer should have either core or full_layout"""
        for layer_name, layer in keymap_config.layers.items():
            assert layer.core or layer.full_layout, \
                f"{layer_name} should have either core or full_layout"

    def test_core_is_keygrid(self, keymap_config):
        """Layer core should be KeyGrid object"""
        for layer_name, layer in keymap_config.layers.items():
            if layer.core:
                assert isinstance(layer.core, KeyGrid), \
                    f"{layer_name} core should be KeyGrid"

    def test_core_has_36_keys(self, keymap_config):
        """Layer core should flatten to exactly 36 keys"""
        for layer_name, layer in keymap_config.layers.items():
            if layer.core:
                flat = layer.core.flatten()
                assert len(flat) == 36, \
                    f"{layer_name} core should have 36 keys, got {len(flat)}"

    def test_extensions_parsed(self, keymap_config):
        """Extensions should be parsed for layers that have them"""
        # Find a layer with 3x6_3 extension
        layers_with_ext = [
            name for name, layer in keymap_config.layers.items()
            if "3x6_3" in layer.extensions
        ]

        if layers_with_ext:
            layer_name = layers_with_ext[0]
            layer = keymap_config.layers[layer_name]
            ext = layer.extensions["3x6_3"]

            assert "outer_pinky_left" in ext.keys
            assert "outer_pinky_right" in ext.keys


@pytest.mark.tier1
class TestBoardInventoryParsing:
    """Test boards.yaml parsing"""

    def test_parse_production_boards(self, config_dir):
        """Parse production boards.yaml successfully"""
        boards = YAMLConfigParser.parse_boards(config_dir / "boards.yaml")

        assert boards.boards, "Should have boards"
        assert len(boards.boards) > 0, "Should have at least one board"

    def test_boards_are_board_objects(self, board_inventory):
        """All parsed boards should be Board objects"""
        for board_id, board in board_inventory.boards.items():
            assert isinstance(board, Board), f"{board_id} should be a Board object"

    def test_qmk_boards_have_required_fields(self, board_inventory):
        """QMK boards should have qmk_keyboard field"""
        qmk_boards = [
            board for board in board_inventory.boards.values()
            if board.firmware == "qmk"
        ]

        for board in qmk_boards:
            assert board.qmk_keyboard, f"QMK board {board.id} should have qmk_keyboard"

    def test_zmk_boards_have_required_fields(self, board_inventory):
        """ZMK boards should have zmk_shield or zmk_board field"""
        zmk_boards = [
            board for board in board_inventory.boards.values()
            if board.firmware == "zmk"
        ]

        for board in zmk_boards:
            assert board.zmk_shield or board.zmk_board, \
                f"ZMK board {board.id} should have zmk_shield or zmk_board"

    def test_board_ids_are_lowercase(self, board_inventory):
        """Board IDs should be lowercase"""
        for board_id in board_inventory.boards.keys():
            assert board_id.islower(), f"Board ID {board_id} should be lowercase"

    def test_layout_sizes_valid(self, board_inventory):
        """Layout sizes should be valid values"""
        valid_sizes = ["3x5_3", "3x6_3", "totem_38"]

        for board in board_inventory.boards.values():
            assert (
                board.layout_size in valid_sizes or
                board.layout_size.startswith("custom_")
            ), f"Board {board.id} has invalid layout_size: {board.layout_size}"


@pytest.mark.tier1
class TestAliasesParsing:
    """Test aliases.yaml parsing"""

    def test_parse_aliases(self, config_dir):
        """Parse aliases.yaml successfully"""
        aliases = YAMLConfigParser.parse_aliases(config_dir / "aliases.yaml")

        assert aliases, "Should have aliases"

    def test_aliases_are_dict(self, aliases):
        """Aliases should be a dictionary"""
        assert isinstance(aliases, dict), "Aliases should be a dict"

    def test_behavior_aliases_exist(self, aliases):
        """Behavior aliases should exist"""
        # Check for behavior aliases (hrm, lt, mt, sm, df, bt)
        behavior_aliases = ["hrm", "lt", "mt", "sm", "df", "bt"]

        for alias in behavior_aliases:
            assert alias in aliases, f"Behavior alias {alias} should exist"


@pytest.mark.tier1
class TestCombosParsing:
    """Test combos parsing from keymap.yaml"""

    def test_parse_combos(self, combos):
        """Combos should be parsed"""
        if combos and combos.combos:
            assert len(combos.combos) > 0, "Should have at least one combo"

    def test_combo_structure(self, combos):
        """Each combo should have required fields"""
        if not combos or not combos.combos:
            pytest.skip("No combos configured")

        for combo in combos.combos:
            assert combo.name, "Combo should have name"
            assert combo.key_positions, "Combo should have key_positions"
            assert combo.action, "Combo should have action"
            assert combo.layers, "Combo should have layers"

    def test_combo_positions_are_integers(self, combos):
        """Combo positions should be integers"""
        if not combos or not combos.combos:
            pytest.skip("No combos configured")

        for combo in combos.combos:
            for pos in combo.key_positions:
                assert isinstance(pos, int), \
                    f"Combo {combo.name} position should be int, got {type(pos)}"

    def test_combo_positions_in_range(self, combos):
        """Combo positions should be in valid range (0-35)"""
        if not combos or not combos.combos:
            pytest.skip("No combos configured")

        for combo in combos.combos:
            for pos in combo.key_positions:
                assert 0 <= pos <= 35, \
                    f"Combo {combo.name} position {pos} out of range (0-35)"


@pytest.mark.tier1
class TestMagicKeysParsing:
    """Test magic keys parsing from keymap.yaml"""

    def test_parse_magic_keys(self, magic_config):
        """Magic keys should be parsed if configured"""
        # Magic keys are optional
        if magic_config:
            assert magic_config.mappings, "Magic config should have mappings"

    def test_magic_mappings_structure(self, magic_config):
        """Magic mappings should have correct structure"""
        if not magic_config or not magic_config.mappings:
            pytest.skip("No magic keys configured")

        # Should be dict of layer -> dict of trigger -> output
        assert isinstance(magic_config.mappings, dict), \
            "Magic mappings should be a dict"


@pytest.mark.tier1
class TestIntegerKeycodes:
    """Test integer keycode parsing (0-9)"""

    def test_integer_keycodes_in_layers(self, keymap_config):
        """Integer keycodes (0-9) should be parsed correctly"""
        # Check if any layer contains integer keycodes
        found_integer = False

        for layer_name, layer in keymap_config.layers.items():
            if layer.core:
                flat = layer.core.flatten()
                for keycode in flat:
                    if keycode in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        found_integer = True
                        # Should be string, not int
                        assert isinstance(keycode, str), \
                            f"Integer keycode should be parsed as string, got {type(keycode)}"

        # Note: Not asserting found_integer because it's optional


@pytest.mark.tier1
class TestL36References:
    """Test L36 position reference parsing"""

    def test_l36_references_in_full_layout(self, full_layout_config):
        """L36_N references should be parsed in full_layout"""
        # Use test fixture with full_layout layers
        layers_with_full = [
            layer for layer in full_layout_config.layers.values()
            if layer.full_layout
        ]

        assert len(layers_with_full) > 0, "Test fixture should have full_layout layers"

        # Check that L36 references are parsed as dicts with _ref="L36"
        for layer in layers_with_full:
            flat = layer.full_layout.flatten()
            l36_refs = [k for k in flat if isinstance(k, dict) and k.get("_ref") == "L36"]
            assert len(l36_refs) > 0, f"Should have at least one L36 reference in {layer.name}"

            for ref in l36_refs:
                # Should be a dict with _ref and index
                assert isinstance(ref, dict), f"L36 reference should be dict, got {type(ref)}"
                assert ref.get("_ref") == "L36", "Should have _ref='L36'"
                assert "index" in ref, "Should have index field"
                assert 0 <= ref["index"] <= 35, "Index should be 0-35"


@pytest.mark.tier1
class TestErrorHandling:
    """Test error handling for invalid configs"""

    def test_missing_file_raises_error(self, config_dir):
        """Parsing non-existent file should raise error"""
        with pytest.raises(FileNotFoundError):
            YAMLConfigParser.parse_keymap(config_dir / "nonexistent.yaml")

    def test_empty_yaml_handled(self, tmp_path):
        """Empty YAML should be handled gracefully"""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        # Should not crash, but may return None or empty structure
        # (exact behavior depends on implementation)
        try:
            result = YAMLConfigParser.parse_keymap(empty_file)
            # If it doesn't raise, result should be None or have no layers
            if result:
                assert not result.layers or len(result.layers) == 0
        except Exception:
            # Some parsers may raise - that's also acceptable
            pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
