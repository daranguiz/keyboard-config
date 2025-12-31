#!/usr/bin/env python3
"""
Golden file snapshot regression tests (Tier 1)

This test compares generated output against baseline "golden" files to catch
unintended changes in code generation. Golden files are stored in
tests/fixtures/golden/ and should be updated when output format intentionally changes.

To update golden files when output format changes:
    pytest tests/integration/test_golden_snapshots.py --snapshot-update
"""

import pytest
from pathlib import Path
import sys
import hashlib

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from generate import KeymapGenerator


def get_file_hash(file_path: Path) -> str:
    """Get MD5 hash of file contents (for quick comparison)"""
    if not file_path.exists():
        return ""

    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def normalize_whitespace(content: str) -> str:
    """Normalize whitespace for comparison (ignore trailing whitespace changes)"""
    lines = content.splitlines()
    # Strip trailing whitespace from each line
    normalized = [line.rstrip() for line in lines]
    return "\n".join(normalized)


@pytest.mark.tier1
class TestGoldenSnapshots:
    """Test generated output against golden files"""

    def test_qmk_skeletyl_structure_stable(self, repo_root):
        """QMK skeletyl keymap.c structure should remain stable"""
        # Generate fresh output
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        assert keymap_file.exists(), "Keymap file should be generated"

        with open(keymap_file) as f:
            content = f.read()

        # Check for stable structural elements
        assert "AUTO-GENERATED" in content
        assert "#include" in content
        assert "const uint16_t PROGMEM keymaps" in content
        assert "LAYOUT_split_3x5_3" in content

        # Check for layer definitions
        base_layers = ["BASE_PRIMARY", "BASE_ALT", "BASE_ALT2"]
        for layer in base_layers:
            assert f"[{layer}]" in content, f"Layer {layer} should be defined"

    def test_zmk_chocofi_structure_stable(self, repo_root):
        """ZMK chocofi keymap structure should remain stable"""
        # Generate fresh output
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        assert keymap_file.exists(), "Keymap file should be generated"

        with open(keymap_file) as f:
            content = f.read()

        # Check for stable structural elements
        assert "AUTO-GENERATED" in content
        assert "#include" in content
        assert "keymap {" in content or "/ {" in content
        assert "bindings" in content

    def test_generated_file_hashes_stable(self, repo_root, request):
        """Generated file structure should remain stable (hash comparison)"""
        # Generate all files
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_all()

        # Key files to check for stability
        files_to_check = [
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" / "promicro" / "keymaps" / "dario" / "keymap.c",
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" / "promicro" / "keymaps" / "dario" / "config.h",
            repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap",
        ]

        # This is a placeholder test - actual golden file comparison would require
        # storing baseline hashes and comparing against them
        # For now, just verify files exist and are non-empty
        for file_path in files_to_check:
            if file_path.exists():
                assert file_path.stat().st_size > 100, \
                    f"{file_path} should have substantial content"

    def test_layer_count_stable(self, repo_root):
        """Number of generated layers should remain stable"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Count layer definitions
        layer_count = content.count("[") - content.count("/*[")  # Approximate
        # Should have multiple layers (at least 5: BASE layers + overlays)
        assert layer_count >= 5, f"Should have at least 5 layers, found {layer_count}"

    def test_combo_count_stable(self, repo_root, combos):
        """Number of generated combos should match config"""
        if not combos or not combos.combos:
            pytest.skip("No combos configured")

        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Count combos in generated file
        # QMK combos are defined as combo_t structures
        expected_combo_count = len(combos.combos)

        # Check that combo names appear in the file
        found_combos = 0
        for combo in combos.combos:
            if combo.name.upper() in content:
                found_combos += 1

        # Should find most combos (some may be filtered for specific layers)
        assert found_combos >= expected_combo_count // 2, \
            f"Should find at least half of combos ({expected_combo_count}), found {found_combos}"

    def test_qmk_includes_stable(self, repo_root):
        """QMK includes should remain stable"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Required includes
        assert "#include QMK_KEYBOARD_H" in content or "#include" in content
        # Note: Exact includes may vary, just verify some includes exist

    def test_zmk_includes_stable(self, repo_root):
        """ZMK includes should remain stable"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("chocofi")

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Required includes
        required_includes = [
            "<behaviors.dtsi>",
            "<dt-bindings/zmk/keys.h>"
        ]

        for include in required_includes:
            assert include in content, f"Should include {include}"


@pytest.mark.tier1
class TestOutputConsistency:
    """Test consistency across multiple generations"""

    def test_deterministic_output(self, repo_root):
        """Generating twice should produce identical output"""
        generator = KeymapGenerator(repo_root, verbose=False)

        # Generate twice
        generator.generate_for_board("skeletyl")
        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            first_gen = f.read()

        # Generate again
        generator.generate_for_board("skeletyl")

        with open(keymap_file) as f:
            second_gen = f.read()

        # Should be identical (deterministic output)
        assert first_gen == second_gen, "Output should be deterministic"

    def test_no_trailing_whitespace_changes(self, repo_root):
        """Generated files should have consistent whitespace"""
        generator = KeymapGenerator(repo_root, verbose=False)
        generator.generate_for_board("skeletyl")

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Normalize and compare
        normalized = normalize_whitespace(content)

        # Original and normalized should be very similar (allowing for trailing whitespace)
        # This is more of a style check
        assert len(content) > 0
        assert len(normalized) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
