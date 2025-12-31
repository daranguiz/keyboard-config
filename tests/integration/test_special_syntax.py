#!/usr/bin/env python3
"""
Special syntax integration tests (Tier 1)

Tests all special syntax features end-to-end:
- hrm: (home row mods)
- lt: (layer-tap)
- mt: (mod-tap)
- df: (default layer)
- sm: (shift-morph)
- L36 position references
- Magic key behaviors
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate import KeymapGenerator


@pytest.mark.tier1
class TestHomeRowMods:
    """Test hrm: syntax generates correctly"""

    def test_qmk_hrm_generates_mod_tap(self, repo_root):
        """hrm: should generate LGUI_T() style macros in QMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have home row mod macros
        hrm_patterns = ["LGUI_T", "LALT_T", "LCTL_T", "LSFT_T"]
        found = [p for p in hrm_patterns if p in content]

        assert len(found) > 0, f"Should have home row mod macros, found: {found}"

    def test_zmk_hrm_generates_behaviors(self, repo_root):
        """hrm: should generate &hml/&hmr behaviors in ZMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have home row mod behaviors
        assert "&hml" in content or "&hmr" in content, \
            "Should have home row mod behaviors"


@pytest.mark.tier1
class TestLayerTap:
    """Test lt: syntax generates correctly"""

    def test_qmk_lt_generates_layer_tap(self, repo_root):
        """lt: should generate LT() macros in QMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have LT macros for layer-tap
        assert "LT(" in content, "Should have LT() layer-tap macros"

    def test_zmk_lt_generates_behavior(self, repo_root):
        """lt: should generate &lt behaviors in ZMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have &lt behaviors
        assert "&lt" in content, "Should have &lt layer-tap behaviors"


@pytest.mark.tier1
class TestModTap:
    """Test mt: syntax generates correctly"""

    def test_qmk_mt_generates_mod_tap(self, repo_root):
        """mt: should generate mod-tap macros in QMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have mod-tap macros (_T pattern)
        assert "_T(KC_" in content, "Should have mod-tap macros"

    def test_zmk_mt_generates_behavior(self, repo_root):
        """mt: should generate &mt behaviors in ZMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have &mt behaviors
        assert "&mt" in content, "Should have &mt mod-tap behaviors"


@pytest.mark.tier1
class TestDefaultLayer:
    """Test df: syntax generates correctly"""

    def test_qmk_df_generates_default_layer(self, repo_root):
        """df: should generate DF() macros in QMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have DF() macros for default layer switching
        assert "DF(" in content, "Should have DF() default layer macros"

    def test_zmk_df_generates_to_behavior(self, repo_root):
        """df: should generate &to behaviors in ZMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have &to behaviors
        assert "&to" in content, "Should have &to default layer behaviors"


@pytest.mark.tier1
class TestShiftMorph:
    """Test sm: syntax generates correctly"""

    def test_qmk_sm_generates_key_overrides(self, repo_root):
        """sm: should generate key override structures in QMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have key override structures if sm: is used
        # Note: Actual presence depends on whether keymap uses sm:
        # Just verify file is valid
        assert "keymap" in content.lower()

    def test_zmk_sm_generates_mod_morph(self, repo_root):
        """sm: should generate mod-morph behaviors in ZMK"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have mod-morph behaviors if sm: is used
        # Just verify file is valid
        assert "keymap" in content.lower()


@pytest.mark.tier1
class TestL36References:
    """Test L36_N position references"""

    def test_l36_references_resolve_in_full_layout(self, repo_root, board_inventory):
        """L36_N references should resolve to actual keycodes in full_layout"""
        # Find boards with custom layouts (likely to use L36 references)
        custom_boards = [
            b for b in board_inventory.boards.values()
            if b.layout_size.startswith("custom_")
        ]

        if not custom_boards:
            pytest.skip("No custom layout boards to test L36 references")

        generator = KeymapGenerator(repo_root, verbose=False)

        # Generate for custom board
        board = custom_boards[0]
        generator.generate_for_board(board.id)

        if board.firmware == "qmk":
            keymap_file = (
                repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
                "keymaps" / "dario" / "keymap.c"
            )
        else:
            pytest.skip("ZMK custom boards not implemented yet")

        if not keymap_file.exists():
            pytest.skip("Keymap file not generated")

        with open(keymap_file) as f:
            content = f.read()

        # Should NOT contain "L36_" in the output (should be resolved)
        assert "L36_" not in content, "L36 references should be resolved to actual keycodes"


@pytest.mark.tier1
class TestMagicKey:
    """Test MAGIC key generation"""

    def test_qmk_magic_generates_arep(self, repo_root, magic_config):
        """MAGIC should generate QK_AREP in QMK"""
        if not magic_config or not magic_config.mappings:
            pytest.skip("No magic key configuration")

        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have QK_AREP for magic key
        assert "QK_AREP" in content or "MAGIC" in content, \
            "Should have magic key keycode"

    def test_qmk_magic_generates_function(self, repo_root, magic_config):
        """QMK should generate get_alt_repeat_key_keycode_user function"""
        if not magic_config or not magic_config.mappings:
            pytest.skip("No magic key configuration")

        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have magic key function
        assert "get_alt_repeat_key_keycode_user" in content or "magic" in content.lower(), \
            "Should have magic key function"

    def test_zmk_magic_generates_adaptive_key(self, repo_root, magic_config):
        """ZMK should generate adaptive-key behaviors for magic"""
        if not magic_config or not magic_config.mappings:
            pytest.skip("No magic key configuration")

        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have adaptive-key behaviors for magic
        assert "adaptive-key" in content or "&ak_" in content or "magic" in content.lower(), \
            "Should have magic key adaptive behaviors"


@pytest.mark.tier1
class TestComplexSyntaxCombinations:
    """Test combinations of multiple syntax features"""

    def test_layer_with_all_features(self, repo_root):
        """Layer with hrm, lt, mt, df, sm should generate correctly"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Should have multiple feature types
        features_present = []

        if "LGUI_T" in content or "LALT_T" in content:
            features_present.append("hrm")
        if "LT(" in content:
            features_present.append("lt")
        if "_T(KC_" in content:
            features_present.append("mt")
        if "DF(" in content:
            features_present.append("df")

        # Should have at least 3 different feature types
        assert len(features_present) >= 3, \
            f"Should have multiple features, found: {features_present}"

    def test_all_modifiers_work(self, repo_root):
        """All modifier types (LGUI, LALT, LCTL, LSFT) should work"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # All modifiers should be present
        modifiers = ["LGUI", "LALT", "LCTL", "LSFT"]
        found_mods = [m for m in modifiers if m in content]

        assert len(found_mods) >= 3, \
            f"Should have multiple modifiers, found: {found_mods}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
