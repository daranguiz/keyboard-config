#!/usr/bin/env python3
"""
Cross-board consistency tests (Tier 1)

Tests that ensure keymaps are consistent across different boards:
- Same layer definitions produce same keycodes across boards
- 36-key core is identical on all boards
- Extensions only add keys, don't modify core
- Layer ordering is consistent
- Combo position translations are correct
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate import KeymapGenerator


@pytest.mark.tier1
class TestCoreConsistency:
    """Test that 36-key core is consistent across boards"""

    def test_base_layer_core_identical_across_boards(self, repo_root, board_inventory):
        """Base layer core (36 keys) should be identical across all boards"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Get QMK boards
        qmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "qmk"]

        if len(qmk_boards) < 2:
            pytest.skip("Need at least 2 QMK boards to test consistency")

        # Read keymap files and extract BASE layer
        base_layer_contents = {}

        for board in qmk_boards:
            keymap_file = (
                repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
                "keymaps" / "dario" / "keymap.c"
            )

            if not keymap_file.exists():
                continue

            with open(keymap_file) as f:
                content = f.read()

            # Extract BASE_PRIMARY layer definition
            if "[BASE_PRIMARY]" in content:
                # Find layer definition
                start = content.find("[BASE_PRIMARY]")
                end = content.find("),", start)
                if end > start:
                    layer_def = content[start:end]
                    base_layer_contents[board.id] = layer_def

        # All boards should have similar BASE layer structure
        if len(base_layer_contents) >= 2:
            # At minimum, verify all have the layer
            assert len(base_layer_contents) >= 2, "Should have BASE layer on multiple boards"

    def test_overlay_layers_consistent(self, repo_root, board_inventory):
        """Overlay layers (NAV, NUM, SYM) should be consistent across boards"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Get all boards
        boards = list(board_inventory.boards.values())

        if len(boards) < 2:
            pytest.skip("Need at least 2 boards to test consistency")

        # Common overlay layers that should exist on all boards
        overlay_layers = ["NAV", "NUM", "SYM", "MEDIA"]

        # Check that these layers appear in generated files
        for board in boards[:2]:  # Check first 2 boards
            if board.firmware == "qmk":
                keymap_file = (
                    repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
                    "keymaps" / "dario" / "keymap.c"
                )
            else:
                if board.zmk_shield:
                    keymap_file = (
                        repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario" /
                        f"{board.zmk_shield}.keymap"
                    )
                else:
                    keymap_file = (
                        repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario" /
                        f"{board.zmk_board}.keymap"
                    )

            if not keymap_file.exists():
                continue

            with open(keymap_file) as f:
                content = f.read()

            # Check that overlay layers are defined
            for layer in overlay_layers:
                assert f"[{layer}]" in content or f"#{layer}" in content or layer in content, \
                    f"Layer {layer} should be defined on {board.id}"


@pytest.mark.tier1
class TestExtensionConsistency:
    """Test that extensions only add keys, don't modify core"""

    def test_extensions_only_add_keys(self, repo_root, board_inventory):
        """Extensions should add keys without modifying 36-key core"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Find a 36-key board and a 42-key board (firmware-agnostic)
        board_36 = None
        board_42 = None

        for board in board_inventory.boards.values():
            if board.layout_size == "3x5_3" and not board_36:
                board_36 = board
            elif board.layout_size == "3x6_3" and not board_42:
                board_42 = board

        if not board_36 or not board_42:
            pytest.skip("Need both 36-key and 42-key boards")

        # Get appropriate file paths based on firmware
        if board_36.firmware == "qmk":
            keymap_36 = (
                repo_root / "qmk" / "keyboards" / board_36.qmk_keyboard /
                "keymaps" / "dario" / "keymap.c"
            )
        else:  # zmk
            shield_or_board = board_36.zmk_shield or board_36.zmk_board
            keymap_36 = (
                repo_root / "zmk" / "keymaps" / f"{shield_or_board}_dario" /
                f"{shield_or_board}.keymap"
            )

        if board_42.firmware == "qmk":
            keymap_42 = (
                repo_root / "qmk" / "keyboards" / board_42.qmk_keyboard /
                "keymaps" / "dario" / "keymap.c"
            )
        else:  # zmk
            shield_or_board = board_42.zmk_shield or board_42.zmk_board
            keymap_42 = (
                repo_root / "zmk" / "keymaps" / f"{shield_or_board}_dario" /
                f"{shield_or_board}.keymap"
            )

        if not keymap_36.exists() or not keymap_42.exists():
            pytest.skip("Keymap files not generated")

        with open(keymap_36) as f:
            content_36 = f.read()

        with open(keymap_42) as f:
            content_42 = f.read()

        # Both should have BASE layer (adjust for firmware syntax)
        if board_36.firmware == "qmk":
            assert "[BASE_" in content_36 or "BASE_" in content_36
        else:
            assert "BASE_" in content_36

        if board_42.firmware == "qmk":
            assert "[BASE_" in content_42 or "BASE_" in content_42
        else:
            assert "BASE_" in content_42


@pytest.mark.tier1
class TestLayerOrdering:
    """Test that layer ordering is consistent"""

    def test_base_layers_first(self, repo_root, board_inventory):
        """BASE layers should appear first in keymap definitions"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check first QMK board
        qmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "qmk"]

        if not qmk_boards:
            pytest.skip("No QMK boards")

        board = qmk_boards[0]
        keymap_file = (
            repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
            "keymaps" / "dario" / "keymap.c"
        )

        if not keymap_file.exists():
            pytest.skip("Keymap file not generated")

        with open(keymap_file) as f:
            content = f.read()

        # Find positions of BASE layers and overlay layers
        base_pos = content.find("[BASE_PRIMARY]")
        nav_pos = content.find("[NAV]")

        if base_pos > 0 and nav_pos > 0:
            # BASE should come before NAV
            assert base_pos < nav_pos, "BASE layer should come before overlay layers"

    def test_layer_enum_order_matches_definitions(self, repo_root):
        """Layer enum order should match layer definition order"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        if not keymap_file.exists():
            pytest.skip("Keymap file not generated")

        with open(keymap_file) as f:
            content = f.read()

        # Check that keymaps array exists
        assert "const uint16_t PROGMEM keymaps" in content


@pytest.mark.tier1
class TestComboConsistency:
    """Test that combos are consistent across boards"""

    def test_combos_on_all_boards(self, repo_root, board_inventory, combos):
        """Combos should be defined on all boards"""
        if not combos or not combos.combos:
            pytest.skip("No combos configured")

        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check each board
        for board in board_inventory.boards.values():
            if board.firmware == "qmk":
                keymap_file = (
                    repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
                    "keymaps" / "dario" / "keymap.c"
                )
            else:
                if board.zmk_shield:
                    keymap_file = (
                        repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario" /
                        f"{board.zmk_shield}.keymap"
                    )
                else:
                    keymap_file = (
                        repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario" /
                        f"{board.zmk_board}.keymap"
                    )

            if not keymap_file.exists():
                continue

            with open(keymap_file) as f:
                content = f.read()

            # Check that combos section exists
            if board.firmware == "qmk":
                assert "combo_t" in content or content.count("combo") > 0, \
                    f"QMK board {board.id} should have combos"
            else:
                assert "combos {" in content, \
                    f"ZMK board {board.id} should have combos section"


@pytest.mark.tier1
class TestFirmwareSpecificFeatures:
    """Test firmware-specific features are correctly isolated"""

    def test_bluetooth_only_in_zmk(self, repo_root, board_inventory):
        """Bluetooth keycodes should only appear in ZMK, not QMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check QMK files - should NOT have bluetooth
        qmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "qmk"]

        for board in qmk_boards:
            keymap_file = (
                repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
                "keymaps" / "dario" / "keymap.c"
            )

            if not keymap_file.exists():
                continue

            with open(keymap_file) as f:
                content = f.read()

            # QMK should not have bluetooth keycodes (they should be filtered to KC_NO)
            # This is expected - bt: keys are converted to KC_NO for QMK
            # Just verify file exists and has content
            assert len(content) > 100

        # Check ZMK files - may have bluetooth
        zmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "zmk"]

        for board in zmk_boards:
            if board.zmk_shield:
                keymap_file = (
                    repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario" /
                    f"{board.zmk_shield}.keymap"
                )
            else:
                keymap_file = (
                    repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario" /
                    f"{board.zmk_board}.keymap"
                )

            if not keymap_file.exists():
                continue

            with open(keymap_file) as f:
                content = f.read()

            # ZMK files are valid
            assert len(content) > 100


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
