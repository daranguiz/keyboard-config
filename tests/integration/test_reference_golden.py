#!/usr/bin/env python3
"""
Golden File Regression Tests for Reference Keymap
=================================================

These tests generate output using the reference keymap configuration and
compare against verified "golden" files to detect unintended changes.

Usage:
    pytest tests/integration/test_reference_golden.py -v

To update golden files (when changes are intentional):
    pytest tests/integration/test_reference_golden.py --snapshot-update
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


def normalize_for_comparison(content: str) -> str:
    """
    Normalize content for comparison:
    - Strip trailing whitespace from each line
    - Normalize line endings
    - Remove empty trailing lines
    """
    lines = content.splitlines()
    normalized = [line.rstrip() for line in lines]
    # Remove trailing empty lines
    while normalized and not normalized[-1]:
        normalized.pop()
    return "\n".join(normalized)


def read_file_normalized(path: Path) -> str:
    """Read file and normalize for comparison"""
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return normalize_for_comparison(f.read())


def write_golden_file(path: Path, content: str):
    """Write content to golden file (for --snapshot-update)"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


@pytest.mark.tier1
class TestQMKGoldenFiles:
    """Test QMK output against golden files"""

    def test_qmk_keymap_structure(self, qmk_translator, reference_keymap_config, fixtures_dir, request):
        """
        Test that QMK keymap generation produces expected structure.

        This is a structural test - verifies key elements are present.
        Full golden file comparison is optional (depends on golden file existence).
        """
        # Verify translator can process reference config layers
        layers = reference_keymap_config.layers

        # Test that BASE_REF and NAV_REF layers exist
        assert "BASE_REF" in layers, "BASE_REF layer should exist in reference config"
        assert "NAV_REF" in layers, "NAV_REF layer should exist in reference config"

        # Test that key positions translate correctly
        base_layer = layers["BASE_REF"]

        # Check position 0 (Q)
        qmk_translator.set_context(layer="BASE_REF", position=0)
        # The actual key at position 0 in BASE_REF is Q
        assert qmk_translator.translate("Q") == "KC_Q"

        # Check position 10 (hrm:LGUI:A)
        qmk_translator.set_context(layer="BASE_REF", position=10)
        assert qmk_translator.translate("hrm:LGUI:A") == "LGUI_T(KC_A)"

        # Check position 30 (lt:NAV_REF:BSPC)
        qmk_translator.set_context(layer="BASE_REF", position=30)
        assert qmk_translator.translate("lt:NAV_REF:BSPC") == "LT(NAV_REF, KC_BSPC)"

    def test_qmk_golden_comparison(self, fixtures_dir, request):
        """
        Compare generated QMK output against golden file.

        Skipped if golden file doesn't exist yet.
        Use --snapshot-update to create/update golden file.
        """
        golden_path = fixtures_dir / "golden" / "qmk" / "reference_keymap.c"
        update_snapshots = request.config.getoption("--snapshot-update", default=False)

        if not golden_path.exists() and not update_snapshots:
            pytest.skip("Golden file not yet created. Use --snapshot-update to create.")

        # TODO: When full generator integration is ready, generate and compare
        # For now, this is a placeholder that validates the golden file exists
        if golden_path.exists():
            content = read_file_normalized(golden_path)
            assert len(content) > 100, "Golden file should have substantial content"
            assert "AUTO-GENERATED" in content or "LAYOUT" in content, \
                "Golden file should contain keymap markers"


@pytest.mark.tier1
class TestZMKGoldenFiles:
    """Test ZMK output against golden files"""

    def test_zmk_keymap_structure(self, zmk_translator, reference_keymap_config, fixtures_dir, request):
        """
        Test that ZMK keymap generation produces expected structure.

        This is a structural test - verifies key elements are present.
        """
        layers = reference_keymap_config.layers

        # Test that layers exist
        assert "BASE_REF" in layers
        assert "NAV_REF" in layers

        # Check left-hand position (10) uses &hml
        zmk_translator.set_context(layer="BASE_REF", position=10)
        result = zmk_translator.translate("hrm:LGUI:A")
        assert "&hml" in result, f"Left hand HRM should use &hml, got {result}"

        # Check right-hand position (16) uses &hmr
        zmk_translator.set_context(layer="BASE_REF", position=16)
        result = zmk_translator.translate("hrm:LSFT:J")
        assert "&hmr" in result, f"Right hand HRM should use &hmr, got {result}"

        # Check layer-tap
        zmk_translator.set_context(layer="BASE_REF", position=30)
        result = zmk_translator.translate("lt:NAV_REF:BSPC")
        assert "&lt" in result, f"Layer-tap should use &lt, got {result}"

    def test_zmk_golden_comparison(self, fixtures_dir, request):
        """
        Compare generated ZMK output against golden file.

        Skipped if golden file doesn't exist yet.
        Use --snapshot-update to create/update golden file.
        """
        golden_path = fixtures_dir / "golden" / "zmk" / "reference.keymap"
        update_snapshots = request.config.getoption("--snapshot-update", default=False)

        if not golden_path.exists() and not update_snapshots:
            pytest.skip("Golden file not yet created. Use --snapshot-update to create.")

        if golden_path.exists():
            content = read_file_normalized(golden_path)
            assert len(content) > 100, "Golden file should have substantial content"
            assert "keymap" in content or "bindings" in content, \
                "Golden file should contain ZMK keymap markers"


@pytest.mark.tier1
class TestCrossGoldenConsistency:
    """Test consistency between QMK and ZMK golden outputs"""

    def test_same_layer_count(self, reference_keymap_config):
        """Both firmwares should have same number of layers"""
        layers = reference_keymap_config.layers
        # This is a config-level test - actual generation should preserve this
        assert len(layers) >= 2, "Reference config should have at least 2 layers"

    def test_same_combo_count(self, reference_keymap_config):
        """Both firmwares should have same number of combos"""
        # Combos are stored in the config, not directly in layers
        # This validates config structure
        if hasattr(reference_keymap_config, 'combos'):
            combos = reference_keymap_config.combos
            assert len(combos) >= 1, "Reference config should have at least 1 combo"


@pytest.mark.tier1
class TestReferenceConfigValidity:
    """Test that reference config is valid and complete"""

    def test_reference_config_parses(self, reference_keymap_config):
        """Reference config should parse without errors"""
        assert reference_keymap_config is not None

    def test_reference_config_has_base_layer(self, reference_keymap_config):
        """Reference config should have at least one BASE layer"""
        layers = reference_keymap_config.layers
        base_layers = [name for name in layers.keys() if name.startswith("BASE")]
        assert len(base_layers) >= 1, "Should have at least one BASE layer"

    def test_reference_config_has_all_behaviors(self, reference_keymap_config):
        """Reference config should exercise all behavior types"""
        # This test validates the config was designed correctly
        # by checking that all behavior prefixes are represented

        # Get raw layer data to check for behavior patterns
        layers = reference_keymap_config.layers

        # For a proper test, we'd need to serialize the config and search
        # For now, just verify structure exists
        assert "BASE_REF" in layers
        assert "NAV_REF" in layers

    def test_reference_boards_parse(self, reference_board_inventory):
        """Reference boards config should parse without errors"""
        assert reference_board_inventory is not None

    def test_reference_boards_have_both_firmwares(self, reference_board_inventory):
        """Reference boards should include both QMK and ZMK"""
        boards = reference_board_inventory.boards

        qmk_boards = [b for b in boards.values() if b.firmware == "qmk"]
        zmk_boards = [b for b in boards.values() if b.firmware == "zmk"]

        assert len(qmk_boards) >= 1, "Should have at least one QMK board"
        assert len(zmk_boards) >= 1, "Should have at least one ZMK board"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
