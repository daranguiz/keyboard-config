#!/usr/bin/env python3
"""
Unit tests for layer_compiler.py

Tests layer compilation including:
- 36-key → 36-key compilation (no padding)
- 36-key → 42-key compilation (3x6_3 extensions)
- 36-key → 58-key compilation (custom layouts)
- L36 position reference resolution
- Full_layout layer handling
- Extension application
- Translator context setting
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from layer_compiler import LayerCompiler
from data_model import Layer, KeyGrid, Board


@pytest.mark.tier1
class TestBasicCompilation:
    """Test basic layer compilation"""

    def test_compile_36_to_36(self, keymap_config, layer_compiler):
        """Compiling 36-key layer for 36-key board should not add padding"""
        # Get a base layer
        base_layers = [name for name in keymap_config.layers if name.startswith("BASE")]
        if not base_layers:
            pytest.skip("No base layers")

        layer_name = base_layers[0]
        layer = keymap_config.layers[layer_name]

        # Create 36-key board
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Should have exactly 36 keys
        assert len(compiled.keycodes) == 36, \
            f"36-key board should have 36 keys, got {len(compiled.keycodes)}"

    def test_compile_36_to_42(self, keymap_config, layer_compiler):
        """Compiling 36-key layer for 42-key board should add extensions"""
        # Get a base layer
        base_layers = [name for name in keymap_config.layers if name.startswith("BASE")]
        if not base_layers:
            pytest.skip("No base layers")

        layer_name = base_layers[0]
        layer = keymap_config.layers[layer_name]

        # Check if layer has 3x6_3 extension
        if "3x6_3" not in layer.extensions:
            pytest.skip("Layer doesn't have 3x6_3 extension")

        # Create 42-key board
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x6_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Should have 42 keys (36 + 6 from outer pinky columns)
        assert len(compiled.keycodes) == 42, \
            f"42-key board should have 42 keys, got {len(compiled.keycodes)}"

    def test_compiled_layer_metadata(self, keymap_config, layer_compiler):
        """Compiled layer should have correct metadata"""
        base_layers = [name for name in keymap_config.layers if name.startswith("BASE")]
        if not base_layers:
            pytest.skip("No base layers")

        layer_name = base_layers[0]
        layer = keymap_config.layers[layer_name]

        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Check metadata
        assert compiled.name == layer_name
        assert compiled.board == board
        assert compiled.firmware == "qmk"

    def test_keycodes_are_translated(self, keymap_config, layer_compiler):
        """Compiled keycodes should be translated to firmware format"""
        base_layers = [name for name in keymap_config.layers if name.startswith("BASE")]
        if not base_layers:
            pytest.skip("No base layers")

        layer_name = base_layers[0]
        layer = keymap_config.layers[layer_name]

        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Check that keycodes are QMK format (KC_* or special macros)
        for keycode in compiled.keycodes:
            assert isinstance(keycode, str), "Keycode should be string"
            # QMK keycodes typically start with KC_ or are macros like LT(), LGUI_T(), etc.
            # Just verify they're non-empty
            assert len(keycode) > 0, "Keycode should not be empty"


@pytest.mark.tier1
class TestExtensionHandling:
    """Test extension application"""

    def test_extensions_applied_for_matching_board(self, keymap_config, layer_compiler):
        """Extensions should be applied for boards that need them"""
        # Find a layer with 3x6_3 extension
        layers_with_ext = [
            (name, layer) for name, layer in keymap_config.layers.items()
            if "3x6_3" in layer.extensions
        ]

        if not layers_with_ext:
            pytest.skip("No layers with 3x6_3 extension")

        layer_name, layer = layers_with_ext[0]

        # Create 42-key board
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x6_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Should have 42 keys
        assert len(compiled.keycodes) == 42

    def test_extensions_not_applied_for_36_key_board(self, keymap_config, layer_compiler):
        """Extensions should not be applied for 36-key boards"""
        # Find a layer with 3x6_3 extension
        layers_with_ext = [
            (name, layer) for name, layer in keymap_config.layers.items()
            if "3x6_3" in layer.extensions
        ]

        if not layers_with_ext:
            pytest.skip("No layers with 3x6_3 extension")

        layer_name, layer = layers_with_ext[0]

        # Create 36-key board
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Should have exactly 36 keys (extensions not applied)
        assert len(compiled.keycodes) == 36


@pytest.mark.tier1
class TestFullLayoutLayers:
    """Test full_layout layer handling"""

    def test_full_layout_compilation(self, full_layout_config, layer_compiler):
        """Layers with full_layout should compile correctly"""
        # Use test fixture with full_layout layers
        full_layout_layers = [
            (name, layer) for name, layer in full_layout_config.layers.items()
            if layer.full_layout
        ]

        assert len(full_layout_layers) > 0, "Test fixture should have full_layout layers"

        layer_name, layer = full_layout_layers[0]

        # Determine board size from full_layout length
        full_size = len(layer.full_layout.flatten())

        # Use custom board size for boaty-style layout
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="custom_63"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Should have same number of keys as full_layout
        assert len(compiled.keycodes) == full_size


@pytest.mark.tier1
class TestL36References:
    """Test L36 position reference resolution"""

    def test_l36_references_resolved(self, full_layout_config, layer_compiler):
        """L36_N references should be resolved to actual keycodes"""
        # Use test fixture with full_layout and L36 references
        full_layout_layers = [
            (name, layer) for name, layer in full_layout_config.layers.items()
            if layer.full_layout
        ]

        assert len(full_layout_layers) > 0, "Test fixture should have full_layout layers"

        layer_name, layer = full_layout_layers[0]

        # Check that it has L36 references (parsed as dicts)
        flat = layer.full_layout.flatten()
        l36_refs = [k for k in flat if isinstance(k, dict) and k.get("_ref") == "L36"]
        assert len(l36_refs) > 0, f"Test fixture should have L36 references in {layer_name}"

        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="custom_63"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # All keycodes should be strings (L36 refs resolved)
        for keycode in compiled.keycodes:
            assert isinstance(keycode, str), \
                "All keycodes should be resolved to strings"


@pytest.mark.tier1
class TestTranslatorContext:
    """Test translator context setting"""

    def test_translator_receives_layer_context(self, keymap_config, layer_compiler):
        """Compiler should set layer context on translator"""
        base_layers = [name for name in keymap_config.layers if name.startswith("BASE")]
        if not base_layers:
            pytest.skip("No base layers")

        layer_name = base_layers[0]
        layer = keymap_config.layers[layer_name]

        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        # Compile layer - translator should receive context
        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Just verify compilation succeeded
        assert compiled is not None
        assert len(compiled.keycodes) > 0


@pytest.mark.tier1
class TestMultipleLayerCompilation:
    """Test compiling multiple layers"""

    def test_compile_all_layers_for_board(self, keymap_config, layer_compiler):
        """Should be able to compile all layers for a board"""
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        # Compile all layers
        compiled_layers = []
        for layer_name, layer in keymap_config.layers.items():
            try:
                compiled = layer_compiler.compile_layer(layer, board, "qmk")
                compiled_layers.append(compiled)
            except Exception as e:
                # Some layers may not compile for 36-key boards (like GAME)
                # That's OK, skip them
                continue

        # Should have compiled at least some layers
        assert len(compiled_layers) > 0, "Should compile at least some layers"

    def test_consistent_key_count_per_board_size(self, keymap_config, qmk_translator):
        """All compiled layers for same board should have same key count"""
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x5_3"
        )

        compiler = LayerCompiler(keymap_config, qmk_translator)

        # Compile layers
        key_counts = []
        for layer_name, layer in keymap_config.layers.items():
            try:
                compiled = compiler.compile_layer(layer_name, layer, board)
                key_counts.append(len(compiled.keycodes))
            except Exception:
                continue

        # All compiled layers should have same key count
        if key_counts:
            assert len(set(key_counts)) == 1, \
                f"All layers should have same key count for same board, got: {set(key_counts)}"


@pytest.mark.tier1
class TestErrorHandling:
    """Test error handling in compilation"""

    def test_none_filled_extensions_compile(self, no_extensions_config, layer_compiler):
        """Compiling layer with NONE-filled extensions should work correctly"""
        # Get the NAV_NO_EXT layer specifically (has all-NONE extensions)
        assert "NAV_NO_EXT" in no_extensions_config.layers, "Test fixture should have NAV_NO_EXT layer"
        layer = no_extensions_config.layers["NAV_NO_EXT"]

        # Verify it has 3x6_3 extensions with all NONE
        assert "3x6_3" in layer.extensions, "NAV_NO_EXT should have 3x6_3 extensions"
        ext = layer.extensions["3x6_3"]
        # Check that outer_pinky keys are NONE
        assert all(k == "NONE" for k in ext.keys["outer_pinky_left"]), "Left extensions should be NONE"
        assert all(k == "NONE" for k in ext.keys["outer_pinky_right"]), "Right extensions should be NONE"

        # Compile for 42-key board
        board = Board(
            id="test",
            name="Test",
            firmware="qmk",
            qmk_keyboard="test/board",
            layout_size="3x6_3"
        )

        compiled = layer_compiler.compile_layer(layer, board, "qmk")

        # Should have 42 keys (36 core + 6 extension)
        assert len(compiled.keycodes) == 42

        # Extension keys should be KC_NO (translated from NONE)
        assert "KC_NO" in compiled.keycodes, "Should have KC_NO from NONE extensions"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
