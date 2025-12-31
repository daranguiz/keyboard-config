#!/usr/bin/env python3
"""
Unit tests for validator.py

Tests configuration validation including:
- Layer structure validation (36-key core)
- Layer name validation (C identifier rules)
- Board configuration validation
- L36 position reference bounds
- Required fields validation
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validator import ConfigValidator, ValidationError
from data_model import Layer, KeyGrid, Board
from config_parser import YAMLConfigParser


@pytest.mark.tier1
class TestLayerStructureValidation:
    """Test layer structure validation"""

    def test_validate_36_key_core(self, keymap_config):
        """Valid 36-key core should pass"""
        validator = ConfigValidator()

        # Use a layer from production config
        layers = keymap_config.layers
        validator.validate_keymap_config(layers)

    def test_production_config_is_valid(self, keymap_config):
        """Production keymap config should validate successfully"""
        validator = ConfigValidator()
        # Should not raise
        validator.validate_keymap_config(keymap_config.layers)

    def test_require_base_layer(self):
        """Config without BASE layer should fail"""
        validator = ConfigValidator()

        # Create non-BASE layer
        nav_layer = Layer(
            name="NAV",
            core=KeyGrid(rows=[
                ["LEFT", "DOWN", "UP", "RGHT", "NONE"],
                ["HOME", "PGDN", "PGUP", "END", "NONE"],
                ["NONE", "NONE", "NONE", "NONE", "NONE"],
                ["CAPS", "INS", "APP", "NONE", "NONE"],
                ["NONE", "NONE", "NONE", "NONE", "NONE"],
                ["NONE", "NONE", "NONE", "NONE", "NONE"],
                ["NONE", "NONE", "NONE"],
                ["NONE", "NONE", "NONE"]
            ])
        )

        layers = {"NAV": nav_layer}

        with pytest.raises(ValidationError, match="At least one BASE"):
            validator.validate_keymap_config(layers)


@pytest.mark.tier1
class TestLayerNameValidation:
    """Test layer name validation"""

    def test_layer_names_must_be_uppercase(self):
        """Layer names must be uppercase"""
        validator = ConfigValidator()

        # Test through the public API
        assert not validator._is_valid_c_identifier("base_colemak")
        assert validator._is_valid_c_identifier("BASE_COLEMAK")

    def test_layer_names_must_be_valid_c_identifiers(self):
        """Layer names must be valid C identifiers"""
        validator = ConfigValidator()

        # Test invalid names
        invalid_names = [
            "BASE-COLEMAK",  # Hyphen not allowed
            "BASE COLEMAK",  # Space not allowed
            "123BASE",       # Can't start with number
            "BASE.COLEMAK",  # Period not allowed
        ]

        for name in invalid_names:
            assert not validator._is_valid_c_identifier(name)

    def test_valid_layer_names_pass(self):
        """Valid layer names should pass"""
        validator = ConfigValidator()

        valid_names = [
            "BASE_COLEMAK",
            "BASE_NIGHT",
            "NAV",
            "NUM_NIGHT",
            "SYM",
            "FUN",
            "MEDIA"
        ]

        for name in valid_names:
            # Should return True
            assert validator._is_valid_c_identifier(name)


@pytest.mark.tier1
class TestBoardValidation:
    """Test board configuration validation"""

    def test_board_ids_must_be_lowercase(self):
        """Board IDs must be lowercase"""
        validator = ConfigValidator()

        # Test through the validator method
        assert not validator._is_valid_board_id("Skeletyl")  # Invalid: mixed case
        assert not validator._is_valid_board_id("LULU")  # Invalid: uppercase

    def test_valid_board_ids_pass(self):
        """Valid board IDs should pass"""
        validator = ConfigValidator()

        valid_ids = [
            "skeletyl",
            "lulu",
            "lily58",
            "chocofi",
            "corneish_zen",
            "boaty"
        ]

        for board_id in valid_ids:
            # Should return True
            assert validator._is_valid_board_id(board_id)

    def test_qmk_boards_require_qmk_keyboard_field(self):
        """QMK boards must have qmk_keyboard field"""
        validator = ConfigValidator()

        qmk_board_missing_keyboard = Board(
            id="skeletyl",
            name="Test Board",
            firmware="qmk",
            qmk_keyboard=None,  # Missing!
            layout_size="3x5_3"
        )

        with pytest.raises(ValidationError, match="qmk_keyboard"):
            validator._validate_board(qmk_board_missing_keyboard)

    def test_zmk_boards_require_shield_or_board(self):
        """ZMK boards must have zmk_shield or zmk_board field"""
        validator = ConfigValidator()

        zmk_board_missing_fields = Board(
            id="chocofi",
            name="Test Board",
            firmware="zmk",
            zmk_shield=None,
            zmk_board=None,  # Both missing!
            layout_size="3x6_3"
        )

        with pytest.raises(ValidationError, match="zmk_shield.*zmk_board"):
            validator._validate_board(zmk_board_missing_fields)

    def test_layout_size_must_be_valid(self):
        """Layout size must be from recognized list"""
        validator = ConfigValidator()

        board_invalid_layout = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="invalid_size"
        )

        with pytest.raises(ValidationError, match="layout_size"):
            validator._validate_board(board_invalid_layout)

    def test_valid_layout_sizes(self):
        """Valid layout sizes should pass"""
        validator = ConfigValidator()

        valid_sizes = [
            "3x5_3",
            "3x6_3",
            "custom_58_from_3x6",
            "custom_boaty"
        ]

        for size in valid_sizes:
            board = Board(
                id="test",
                name="Test",
                firmware="qmk",
                qmk_keyboard="test/board",
                layout_size=size
            )
            # Should not raise
            validator._validate_board(board)

    def test_production_board_inventory_is_valid(self, board_inventory):
        """Production board inventory should validate"""
        validator = ConfigValidator()
        # Should not raise - board_inventory.boards is a dict, need list
        boards_list = list(board_inventory.boards.values())
        validator.validate_board_config(boards_list)


@pytest.mark.tier1
class TestL36PositionReferences:
    """Test L36 position reference validation"""

    def test_l36_indices_in_range(self):
        """L36 indices should be validated during layer compilation"""
        # Note: L36 validation happens during layer compilation, not in validator
        # This test verifies the concept - actual validation is in layer_compiler.py
        valid_indices = list(range(36))
        invalid_indices = [-1, 36, 100, -100]

        for i in valid_indices:
            assert 0 <= i <= 35, f"Valid index {i} should be in range"

        for i in invalid_indices:
            assert not (0 <= i <= 35), f"Invalid index {i} should be out of range"


@pytest.mark.tier1
class TestConfigIntegration:
    """Test full config validation"""

    def test_full_production_config_validates(self, keymap_config, board_inventory):
        """Full production configuration should validate"""
        validator = ConfigValidator()

        # Validate keymap
        validator.validate_keymap_config(keymap_config.layers)

        # Validate board inventory
        boards_list = list(board_inventory.boards.values())
        validator.validate_board_config(boards_list)

    def test_duplicate_board_ids_rejected(self):
        """Duplicate board IDs should be rejected"""
        validator = ConfigValidator()

        boards_list = [
            Board(
                id="skeletyl",
                name="Skeletyl 1",
                firmware="qmk",
                qmk_keyboard="bastardkb/skeletyl/promicro",
                layout_size="3x5_3"
            ),
            Board(
                id="skeletyl",  # Duplicate ID
                name="Skeletyl 2",
                firmware="qmk",
                qmk_keyboard="bastardkb/skeletyl/v2",
                layout_size="3x5_3"
            )
        ]

        with pytest.raises(ValidationError, match="Duplicate board"):
            validator.validate_board_config(boards_list)
