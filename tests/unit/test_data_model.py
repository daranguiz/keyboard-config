#!/usr/bin/env python3
"""
Unit tests for data_model.py

Tests data model structures including:
- KeyGrid creation and flattening
- L36 position reference parsing and validation
- Layer construction
- Board metadata structure
- Combo and magic key data structures
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from data_model import (
    KeyGrid, Layer, LayerExtension, Board, Combo, ComboConfiguration,
    MagicKeyConfiguration, ValidationError
)


@pytest.mark.tier1
class TestKeyGrid:
    """Test KeyGrid data structure"""

    def test_keygrid_creation(self):
        """KeyGrid should be created from nested lists"""
        rows = [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "J"],
            ["K", "L", "M", "N", "O"],
            ["P", "Q", "R", "S", "T"],
            ["U", "V", "W", "X", "Y"],
            ["Z", "1", "2", "3", "4"],
            ["5", "6", "7"],
            ["8", "9", "0"]
        ]

        grid = KeyGrid(rows=rows)
        assert grid is not None

    def test_keygrid_flatten(self):
        """KeyGrid should flatten to single list"""
        rows = [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "J"],
            ["K", "L", "M", "N", "O"],
            ["P", "Q", "R", "S", "T"],
            ["U", "V", "W", "X", "Y"],
            ["Z", "1", "2", "3", "4"],
            ["5", "6", "7"],
            ["8", "9", "0"]
        ]

        grid = KeyGrid(rows=rows)
        flat = grid.flatten()

        # Should have 36 keys (5+5+5+5+5+5+3+3)
        assert len(flat) == 36

        # Should contain all keys
        for key in ["A", "B", "C", "F", "G", "5", "8", "9", "0"]:
            assert key in flat, f"Key {key} should be in flattened grid"

    def test_keygrid_integer_conversion(self):
        """KeyGrid should convert integers to strings"""
        rows = [
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8, 9],
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8, 9],
            [0, 1, 2, 3, 4],
            [5, 6, 7, 8, 9],
            [0, 1, 2],
            [3, 4, 5]
        ]

        grid = KeyGrid(rows=rows)
        flat = grid.flatten()

        # All should be strings
        for key in flat:
            assert isinstance(key, str), f"Expected string, got {type(key)}"

    def test_l36_reference_parsing(self):
        """KeyGrid should parse L36_N references"""
        rows = [
            ["L36_0", "L36_1", "L36_2", "L36_3", "L36_4"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C"],
            ["D", "E", "F"]
        ]

        grid = KeyGrid(rows=rows)
        flat = grid.flatten()

        # First 5 should be L36 references (dicts)
        for i in range(5):
            assert isinstance(flat[i], dict), f"Position {i} should be L36 reference dict"
            assert flat[i]["_ref"] == "L36"
            assert flat[i]["index"] == i

        # Rest should be strings
        for i in range(5, len(flat)):
            assert isinstance(flat[i], str), f"Position {i} should be string"

    def test_l36_index_validation(self):
        """L36 indices should be validated"""
        # Valid index (0-35)
        rows = [
            ["L36_0"],
            [], [], [], [], [],
            [], []
        ]
        grid = KeyGrid(rows=rows)  # Should not raise

        # Invalid index (out of range)
        with pytest.raises(ValidationError, match="out of range"):
            rows_invalid = [
                ["L36_36"],  # Out of range
                [], [], [], [], [],
                [], []
            ]
            KeyGrid(rows=rows_invalid)

    def test_keygrid_properties(self):
        """KeyGrid should have left_hand, right_hand, thumbs properties"""
        rows = [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "J"],
            ["K", "L", "M", "N", "O"],
            ["P", "Q", "R", "S", "T"],
            ["U", "V", "W", "X", "Y"],
            ["Z", "1", "2", "3", "4"],
            ["5", "6", "7"],
            ["8", "9", "0"]
        ]

        grid = KeyGrid(rows=rows)

        # Left hand should be first 3 rows
        assert len(grid.left_hand) == 3
        assert grid.left_hand[0] == ["A", "B", "C", "D", "E"]

        # Right hand should be next 3 rows
        assert len(grid.right_hand) == 3
        assert grid.right_hand[0] == ["P", "Q", "R", "S", "T"]

        # Thumbs
        assert grid.thumbs_left == ["5", "6", "7"]
        assert grid.thumbs_right == ["8", "9", "0"]


@pytest.mark.tier1
class TestLayer:
    """Test Layer data structure"""

    def test_layer_with_core(self):
        """Layer should be created with core"""
        core = KeyGrid(rows=[
            ["A"] * 5, ["B"] * 5, ["C"] * 5,
            ["D"] * 5, ["E"] * 5, ["F"] * 5,
            ["G"] * 3, ["H"] * 3
        ])

        layer = Layer(name="TEST", core=core)
        assert layer.name == "TEST"
        assert layer.core is not None

    def test_layer_with_full_layout(self):
        """Layer should be created with full_layout"""
        full_layout = KeyGrid(rows=[
            ["A"] * 58  # 58-key layout
        ])

        layer = Layer(name="TEST", full_layout=full_layout)
        assert layer.name == "TEST"
        assert layer.full_layout is not None

    def test_layer_with_extensions(self):
        """Layer should support extensions"""
        core = KeyGrid(rows=[
            ["A"] * 5, ["B"] * 5, ["C"] * 5,
            ["D"] * 5, ["E"] * 5, ["F"] * 5,
            ["G"] * 3, ["H"] * 3
        ])

        ext = LayerExtension(
            extension_type="3x6_3",
            keys={
                "outer_pinky_left": ["X", "Y", "Z"],
                "outer_pinky_right": ["P", "Q", "R"]
            }
        )

        layer = Layer(name="TEST", core=core, extensions={"3x6_3": ext})
        assert "3x6_3" in layer.extensions


@pytest.mark.tier1
class TestBoard:
    """Test Board data structure"""

    def test_qmk_board_creation(self):
        """QMK board should be created with required fields"""
        board = Board(
            id="skeletyl",
            name="Skeletyl",
            firmware="qmk",
            qmk_keyboard="bastardkb/skeletyl/promicro",
            layout_size="3x5_3"
        )

        assert board.id == "skeletyl"
        assert board.firmware == "qmk"
        assert board.qmk_keyboard == "bastardkb/skeletyl/promicro"

    def test_zmk_board_creation(self):
        """ZMK board should be created with shield or board field"""
        board = Board(
            id="chocofi",
            name="Chocofi",
            firmware="zmk",
            zmk_shield="corne",
            layout_size="3x6_3"
        )

        assert board.id == "chocofi"
        assert board.firmware == "zmk"
        assert board.zmk_shield == "corne"

    def test_board_get_extensions(self):
        """Board should infer extensions from layout_size"""
        board_36 = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )
        assert board_36.get_extensions() == []

        board_42 = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x6_3"
        )
        assert board_42.get_extensions() == ["3x6_3"]

    def test_board_validation(self):
        """Board should validate firmware-specific fields"""
        # QMK board without qmk_keyboard
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            layout_size="3x5_3"
        )

        with pytest.raises(ValidationError, match="qmk_keyboard"):
            board.validate()

        # ZMK board without zmk_shield or zmk_board
        board_zmk = Board(
            id="test",
            name="Test",
            firmware="zmk",
            layout_size="3x5_3"
        )

        with pytest.raises(ValidationError, match="zmk_shield.*zmk_board"):
            board_zmk.validate()


@pytest.mark.tier1
class TestCombo:
    """Test Combo data structure"""

    def test_combo_creation(self):
        """Combo should be created with required fields"""
        combo = Combo(
            name="test_combo",
            description="Test combo",
            key_positions=[10, 11],
            action="ESC",
            layers=["BASE"]
        )

        assert combo.name == "test_combo"
        assert combo.key_positions == [10, 11]
        assert combo.action == "ESC"
        assert combo.layers == ["BASE"]

    def test_combo_with_macro_text(self):
        """Combo should support macro_text"""
        combo = Combo(
            name="github_url",
            description="GitHub URL",
            key_positions=[7, 8, 9, 10],
            action="MACRO",
            macro_text="https://github.com",
            layers=["BASE"]
        )

        assert combo.macro_text == "https://github.com"

    def test_combo_validation_positions(self):
        """Combo should validate key_positions"""
        # Valid positions
        combo = Combo(
            name="test",
            description="Test",
            key_positions=[0, 35],  # Min and max valid
            action="ESC",
            layers=["BASE"]
        )
        combo.validate()  # Should not raise

        # Invalid position (out of range)
        combo_invalid = Combo(
            name="test",
            description="Test",
            key_positions=[0, 36],  # 36 is out of range
            action="ESC",
            layers=["BASE"]
        )

        with pytest.raises(ValidationError, match="out of range"):
            combo_invalid.validate()


@pytest.mark.tier1
class TestComboConfiguration:
    """Test ComboConfiguration"""

    def test_combo_configuration_creation(self):
        """ComboConfiguration should hold list of combos"""
        combo1 = Combo(
            name="combo1",
            description="Combo 1",
            key_positions=[10, 11],
            action="ESC",
            layers=["BASE"]
        )

        combo2 = Combo(
            name="combo2",
            description="Combo 2",
            key_positions=[20, 21],
            action="TAB",
            layers=["BASE"]
        )

        config = ComboConfiguration(combos=[combo1, combo2])
        assert len(config.combos) == 2


@pytest.mark.tier1
class TestMagicKeyConfiguration:
    """Test MagicKeyConfiguration"""

    def test_magic_key_configuration(self):
        """MagicKeyConfiguration should hold mappings"""
        from data_model import MagicKeyMapping

        mapping = MagicKeyMapping(
            base_layer="BASE",
            mappings={
                " ": "THE",
                ",": " BUT"
            },
            timeout_ms=0,
            default="REPEAT"
        )

        config = MagicKeyConfiguration(
            mappings={"BASE": mapping}
        )

        assert "BASE" in config.mappings
        assert config.mappings["BASE"].base_layer == "BASE"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
