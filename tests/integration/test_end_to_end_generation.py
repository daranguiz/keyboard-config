#!/usr/bin/env python3
"""
End-to-end keymap generation test (Tier 1)

This test validates the full generation pipeline without compiling firmware.
It's fast (< 30s) and ensures all boards generate valid output files.
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate import KeymapGenerator
from helpers import (
    assert_file_exists,
    assert_auto_generated_warning
)


@pytest.mark.tier1
class TestEndToEndGeneration:
    """Test complete generation pipeline"""

    def test_generate_all_succeeds(self, repo_root):
        """Full generation should complete without errors"""
        generator = KeymapGenerator(repo_root, verbose=False)
        # Should not raise
        generator.generate_all()

    def test_qmk_keymap_files_generated(self, repo_root, board_inventory):
        """QMK boards should have all required files"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        qmk_boards = [
            board for board in board_inventory.boards.values()
            if board.firmware == "qmk"
        ]

        for board in qmk_boards:
            keymap_dir = repo_root / "qmk" / "keyboards" / board.qmk_keyboard / "keymaps" / "dario"

            # Required files
            assert_file_exists(keymap_dir / "keymap.c")
            assert_file_exists(keymap_dir / "config.h")
            assert_file_exists(keymap_dir / "rules.mk")
            assert_file_exists(keymap_dir / "README.md")

            # Check AUTO-GENERATED warning
            assert_auto_generated_warning(keymap_dir / "keymap.c")
            assert_auto_generated_warning(keymap_dir / "config.h")

    def test_zmk_keymap_files_generated(self, repo_root, board_inventory):
        """ZMK boards should have all required files"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        zmk_boards = [
            board for board in board_inventory.boards.values()
            if board.firmware == "zmk"
        ]

        for board in zmk_boards:
            if board.zmk_shield:
                keymap_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario"
                keymap_file = keymap_dir / f"{board.zmk_shield}.keymap"
            else:
                keymap_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario"
                keymap_file = keymap_dir / f"{board.zmk_board}.keymap"

            # Required files
            assert_file_exists(keymap_file)
            assert_file_exists(keymap_dir / "README.md")

            # Check AUTO-GENERATED warning
            assert_auto_generated_warning(keymap_file)

    def test_single_board_generation(self, repo_root):
        """Generating a single board should work"""
        generator = KeymapGenerator(repo_root, verbose=False)

        # Generate just one board
        generator.generate_for_board("skeletyl")

        # Check it was generated
        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )
        assert_file_exists(keymap_file)

    def test_qmk_keymap_c_structure(self, repo_root):
        """QMK keymap.c should have expected structure"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have required elements
        assert "#include" in content, "Should have includes"
        assert "const uint16_t PROGMEM keymaps" in content, "Should have keymaps array"
        assert "LAYOUT_split_3x5_3" in content, "Should use LAYOUT macro"

    def test_zmk_keymap_structure(self, repo_root):
        """ZMK .keymap should have expected devicetree structure"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have devicetree structure
        assert "keymap {" in content or "/ {" in content, "Should have keymap section"
        assert "bindings" in content, "Should have bindings"
        assert "#include" in content, "Should have includes"

    def test_generated_files_not_empty(self, repo_root, board_inventory):
        """All generated files should have content"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check QMK files
        qmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "qmk"]
        for board in qmk_boards:
            keymap_file = (
                repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
                "keymaps" / "dario" / "keymap.c"
            )
            if keymap_file.exists():
                size = keymap_file.stat().st_size
                assert size > 1000, f"{keymap_file} should have substantial content (> 1KB)"

        # Check ZMK files
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

            if keymap_file.exists():
                size = keymap_file.stat().st_size
                assert size > 1000, f"{keymap_file} should have substantial content (> 1KB)"

    def test_readme_generation(self, repo_root):
        """README files should be generated"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        readme = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "README.md"
        )

        assert_file_exists(readme)

        with open(readme) as f:
            content = f.read()

        # Should have content (README files can be quite long with ASCII art)
        assert len(content) > 100, "README should have content"
        # Check for either AUTO-GENERATED or Generated (both are valid)
        assert ("AUTO-GENERATED" in content or "Generated" in content), \
            "Should have generation notice"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
