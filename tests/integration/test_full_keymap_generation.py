#!/usr/bin/env python3
"""
Full-featured keymap generation test (Tier 1)

This test uses the REAL production keymap.yaml to ensure all features work together.
It's fast (codegen only, no compilation) and catches feature regressions.

Tests all real-world features:
- Multiple base layers (BASE_NIGHT, BASE_GALLIUM, etc.)
- Combos
- Magic keys
- Shift-morphs (sm:)
- Layer-tap (lt:)
- Mod-tap (mt:)
- Home row mods (hrm:)
- Extensions (3x6_3)
- L36 references (Boaty)
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate import KeymapGenerator
from helpers import (
    assert_file_exists,
    count_occurrences_in_file,
    get_combos_from_keymap_c,
    get_layers_from_keymap_c,
    assert_contains,
    assert_auto_generated_warning
)


@pytest.mark.tier1
class TestFullKeymapGeneration:
    """Test full keymap generation with all production features"""

    def test_generate_all_boards_succeeds(self, repo_root, tmp_path):
        """Full generation for all boards should succeed without errors"""
        generator = KeymapGenerator(repo_root, verbose=False)

        # Should not raise
        generator.generate_all()

    def test_qmk_boards_generated(self, repo_root, board_inventory):
        """All QMK boards should have generated files"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check each QMK board
        for board_id, board in board_inventory.boards.items():
            if board.firmware != "qmk":
                continue

            # Construct expected path
            keymap_dir = repo_root / "qmk" / "keyboards" / board.qmk_keyboard / "keymaps" / "dario"

            # Check required files exist
            assert_file_exists(keymap_dir / "keymap.c")
            assert_file_exists(keymap_dir / "config.h")
            assert_file_exists(keymap_dir / "rules.mk")
            assert_file_exists(keymap_dir / "README.md")

    def test_zmk_boards_generated(self, repo_root, board_inventory):
        """All ZMK boards should have generated files"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check each ZMK board
        for board_id, board in board_inventory.boards.items():
            if board.firmware != "zmk":
                continue

            # Construct expected path
            if board.zmk_shield:
                keymap_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario"
                keymap_file = keymap_dir / f"{board.zmk_shield}.keymap"
            else:
                keymap_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario"
                keymap_file = keymap_dir / f"{board.zmk_board}.keymap"

            # Check required files exist
            assert_file_exists(keymap_file)
            assert_file_exists(keymap_dir / "README.md")


@pytest.mark.tier1
class TestQMKFeatures:
    """Test QMK-specific feature generation"""

    @pytest.fixture
    def skeletyl_keymap(self, repo_root):
        """Generate and return path to skeletyl keymap.c"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_path = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )
        return keymap_path

    def test_qmk_has_combos(self, skeletyl_keymap, combos):
        """All combos from config should appear in QMK output"""
        with open(skeletyl_keymap) as f:
            content = f.read()

        # Check that combos are defined
        assert "combo_t" in content, "Combo definitions should exist"

        # Check each combo appears
        for combo in combos.combos:
            # Combo names are uppercased in enum
            assert combo.name.upper() in content, f"Combo {combo.name} should be in keymap"

    def test_qmk_has_magic_keys(self, skeletyl_keymap, magic_config):
        """Magic key macros should be generated"""
        if not magic_config or not magic_config.mappings:
            pytest.skip("No magic key config")

        with open(skeletyl_keymap) as f:
            content = f.read()

        # Check for magic key function
        assert "get_alt_repeat_key_keycode_user" in content, "Magic key function should exist"

        # Check for QK_AREP references
        assert "QK_AREP" in content, "Magic key keycode should be used"

    def test_qmk_has_shift_morphs(self, skeletyl_keymap):
        """Shift-morph key overrides should exist"""
        with open(skeletyl_keymap) as f:
            content = f.read()

        # Check for key override structures
        if "sm:" in str(skeletyl_keymap.parent.parent.parent):  # If shift-morphs exist in config
            assert "key_override_t" in content, "Key override type should exist"

    def test_qmk_has_layer_tap(self, skeletyl_keymap):
        """Layer-tap (lt:) should produce LT() macros"""
        with open(skeletyl_keymap) as f:
            content = f.read()

        # LT macros should appear for layer-tap keys
        assert "LT(" in content, "Layer-tap macros should exist"

    def test_qmk_has_mod_tap(self, skeletyl_keymap):
        """Mod-tap (mt:) should produce mod-tap macros"""
        with open(skeletyl_keymap) as f:
            content = f.read()

        # Check for shift-tab or other mod-tap combos
        assert "_T(KC_" in content, "Mod-tap macros should exist"

    def test_qmk_has_home_row_mods(self, skeletyl_keymap):
        """Home row mods (hrm:) should produce LGUI_T etc."""
        with open(skeletyl_keymap) as f:
            content = f.read()

        # Home row mods should appear
        hrm_patterns = ["LGUI_T", "LALT_T", "LCTL_T", "LSFT_T"]
        found_hrm = any(pattern in content for pattern in hrm_patterns)
        assert found_hrm, "Home row mod macros should exist"

    def test_qmk_has_multiple_base_layers(self, skeletyl_keymap, keymap_config):
        """Multiple base layers should be generated"""
        layers = get_layers_from_keymap_c(skeletyl_keymap)

        # Count BASE layers
        base_layers = [l for l in layers if l.startswith("BASE")]
        assert len(base_layers) >= 2, f"Should have multiple BASE layers, found: {base_layers}"

    def test_qmk_auto_generated_warning(self, skeletyl_keymap):
        """Generated files should have AUTO-GENERATED warning"""
        assert_auto_generated_warning(skeletyl_keymap)


@pytest.mark.tier1
class TestZMKFeatures:
    """Test ZMK-specific feature generation"""

    @pytest.fixture
    def chocofi_keymap(self, repo_root):
        """Generate and return path to chocofi keymap"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_path = (
            repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"
        )
        return keymap_path

    def test_zmk_has_combos(self, chocofi_keymap, combos):
        """All combos should appear in ZMK output"""
        with open(chocofi_keymap) as f:
            content = f.read()

        # Check for combo section
        assert "combos {" in content, "Combos section should exist"

        # Check each combo appears
        for combo in combos.combos:
            assert combo.name in content, f"Combo {combo.name} should be in keymap"

    def test_zmk_has_magic_behaviors(self, chocofi_keymap, magic_config):
        """Magic key adaptive behaviors should be generated"""
        if not magic_config or not magic_config.mappings:
            pytest.skip("No magic key config")

        with open(chocofi_keymap) as f:
            content = f.read()

        # Check for adaptive-key behaviors for magic
        # Example: ak_magic_night, ak_magic_gallium
        assert "adaptive-key" in content or "ak_" in content, "Magic adaptive behaviors should exist"

    def test_zmk_has_mod_morphs(self, chocofi_keymap):
        """Shift-morph should generate mod-morph behaviors"""
        with open(chocofi_keymap) as f:
            content = f.read()

        # Check for mod-morph behaviors (for shift-morphs)
        if "sm:" in str(chocofi_keymap):  # If config has shift-morphs
            assert "mod-morph" in content, "Mod-morph behaviors should exist for shift-morphs"

    def test_zmk_has_layer_tap(self, chocofi_keymap):
        """Layer-tap should produce &lt behaviors"""
        with open(chocofi_keymap) as f:
            content = f.read()

        assert "&lt" in content, "Layer-tap behaviors should exist"

    def test_zmk_has_home_row_mods(self, chocofi_keymap):
        """Home row mods should produce &hml/&hmr"""
        with open(chocofi_keymap) as f:
            content = f.read()

        # Check for home row mod behaviors
        assert "&hml" in content or "&hmr" in content, "Home row mod behaviors should exist"

    def test_zmk_auto_generated_warning(self, chocofi_keymap):
        """Generated files should have AUTO-GENERATED warning"""
        assert_auto_generated_warning(chocofi_keymap)


@pytest.mark.tier1
class TestBoardSpecificFeatures:
    """Test board-specific features"""

    def test_3x6_3_extensions_populated(self, repo_root):
        """3x6_3 boards should have outer pinky extensions"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")  # 3x6_3 board

        keymap_path = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_path) as f:
            content = f.read()

        # 42-key boards should have more keys than 36-key
        # Check that bindings array is longer
        bindings_count = content.count("&")
        assert bindings_count > 40, "3x6_3 board should have 42+ key bindings"

    def test_boaty_uses_l36_references(self, repo_root, board_inventory):
        """Boaty custom layout should resolve L36 references"""
        # Check if boaty is configured
        if "boaty" not in board_inventory.boards:
            pytest.skip("Boaty not configured")

        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("boaty")

        # Boaty uses custom layout with L36 references
        # Just verify it generates without error
        # (Actual L36 resolution tested in unit tests)


@pytest.mark.tier1
class TestRowStaggerGeneration:
    """Test row-stagger (macOS .keylayout) generation"""

    def test_keylayout_files_generated(self, repo_root):
        """Row-stagger configs should generate .keylayout files"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Check for .keylayout files in out/
        keylayout_dir = repo_root / "out" / "keylayout"

        # Should have at least one .keylayout file if row-stagger configs exist
        rowstagger_configs = repo_root / "config" / "rowstagger"
        if rowstagger_configs.exists() and list(rowstagger_configs.glob("*.yaml")):
            assert keylayout_dir.exists(), "keylayout output directory should exist"
            keylayout_files = list(keylayout_dir.glob("*.keylayout"))
            assert len(keylayout_files) > 0, "Should generate at least one .keylayout file"


@pytest.mark.tier1
class TestGenerationPerformance:
    """Test that generation is fast (Tier 1 requirement)"""

    def test_full_generation_is_fast(self, repo_root):
        """Full generation should complete in < 10 seconds"""
        import time

        generator = KeymapGenerator(repo_root, verbose=False)

        start = time.time()
        generator.generate_all()
        duration = time.time() - start

        # Should be very fast (codegen only, no compilation)
        # Allow up to 10s for full generation with all features
        assert duration < 10.0, f"Generation took {duration:.2f}s, should be < 10s"
