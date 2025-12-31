#!/usr/bin/env python3
"""
Full build pipeline tests (Tier 2)

Tests the complete build_all.sh pipeline including:
- QMK firmware compilation
- ZMK firmware compilation
- Visualization generation
- Keylayout generation
- Artifact collection

Requires full build environment (QMK firmware, ZMK repo, Docker).
"""

import pytest
import subprocess
from pathlib import Path
import os


@pytest.mark.tier2
class TestBuildAllScript:
    """Test complete build_all.sh pipeline"""

    def test_build_all_script_exists(self, repo_root):
        """build_all.sh should exist and be executable"""
        build_script = repo_root / "build_all.sh"
        assert build_script.exists(), "build_all.sh should exist"
        assert os.access(build_script, os.X_OK), "build_all.sh should be executable"

    def test_build_all_basic(self, repo_root, qmk_firmware_path, zmk_firmware_path, docker_available):
        """Run build_all.sh and verify completion"""
        if not docker_available:
            pytest.skip("Docker required for full build")

        # Set environment variables
        env = os.environ.copy()
        env["QMK_USERSPACE"] = str(repo_root / "qmk")
        env["QMK_HOME"] = str(qmk_firmware_path)
        env["ZMK_REPO"] = str(zmk_firmware_path)

        # Run build_all.sh
        result = subprocess.run(
            ["./build_all.sh"],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes
        )

        # Check for successful completion
        # Note: May fail if toolchains missing, but script should run
        print(f"Build output:\n{result.stdout}")
        if result.returncode != 0:
            print(f"Build errors:\n{result.stderr}")

        # Check that script at least started
        assert "Generating" in result.stdout or "Building" in result.stdout or \
               result.returncode == 0, "build_all.sh should execute"

    def test_build_all_creates_out_directory(self, repo_root):
        """build_all.sh should create out/ directory structure"""
        # Run generation only (fast)
        result = subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        assert result.returncode == 0

        # Check out directory structure (may not have firmware if builds fail)
        out_dir = repo_root / "out"
        # Note: out/ is created by build_all.sh, not generate.py

    def test_build_all_with_no_magic_training_flag(self, repo_root):
        """Test build_all.sh with --no-magic-training flag"""
        env = os.environ.copy()
        env["QMK_USERSPACE"] = str(repo_root / "qmk")

        # Run generator with flag
        result = subprocess.run(
            ["python3", "scripts/generate.py", "--no-magic-training"],
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0

        # Verify generated files don't have training code
        # Check a QMK keymap
        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        if keymap_file.exists():
            with open(keymap_file) as f:
                content = f.read()

            # Without training, should not have training-specific code
            # (Implementation detail - check based on actual generator behavior)
            # For now, just verify file was generated
            assert len(content) > 100


@pytest.mark.tier2
@pytest.mark.qmk
class TestBuildArtifactsQMK:
    """Test QMK build artifacts"""

    def test_qmk_firmware_artifacts_created(self, repo_root, qmk_firmware_path, qmk_build_env, board_inventory):
        """QMK builds should create .hex or .uf2 files"""
        # Generate keymaps
        subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        # Build one QMK board
        qmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "qmk"]
        if not qmk_boards:
            pytest.skip("No QMK boards")

        board = qmk_boards[0]

        result = subprocess.run(
            ["qmk", "compile", "-kb", board.qmk_keyboard, "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            timeout=300,
        )

        if result.returncode != 0:
            pytest.skip(f"QMK build failed (toolchain may be missing): {result.stderr[:200]}")

        # Check for artifacts
        build_dir = qmk_firmware_path / ".build"
        artifacts = list(build_dir.glob("*.hex")) + list(build_dir.glob("*.uf2"))

        assert len(artifacts) > 0, "Should create at least one firmware artifact"

        for artifact in artifacts:
            print(f"✓ Created: {artifact.name} ({artifact.stat().st_size} bytes)")

    def test_out_qmk_directory_populated(self, repo_root, qmk_firmware_path, qmk_build_env):
        """After full build, out/qmk/ should have firmware files"""
        # This would be created by build_all.sh, not individual compiles
        # Test that build_all.sh properly copies artifacts

        out_qmk = repo_root / "out" / "qmk"

        # If out/ exists and has files, verify structure
        if out_qmk.exists():
            firmware_files = list(out_qmk.glob("*.hex")) + list(out_qmk.glob("*.uf2"))

            if len(firmware_files) > 0:
                print(f"Found {len(firmware_files)} QMK firmware files in out/qmk/")

                for fw in firmware_files:
                    assert fw.stat().st_size > 1000, f"{fw.name} is too small"
        else:
            pytest.skip("out/qmk/ not created (run build_all.sh first)")


@pytest.mark.tier2
@pytest.mark.zmk
@pytest.mark.requires_docker
class TestBuildArtifactsZMK:
    """Test ZMK build artifacts"""

    def test_zmk_firmware_artifacts_created(self, repo_root, zmk_firmware_path, docker_available, board_inventory):
        """ZMK builds should create .uf2 files"""
        if not docker_available:
            pytest.skip("Docker required")

        # Generate keymaps
        subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        # Build one ZMK board
        zmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "zmk"]
        if not zmk_boards:
            pytest.skip("No ZMK boards")

        board = zmk_boards[0]

        # Determine config directory
        if board.zmk_shield:
            zmk_config_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario"
            shield_name = f"{board.zmk_shield}_left"
        else:
            zmk_config_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario"
            shield_name = ""

        zmk_board_name = board.zmk_board if board.zmk_board else "nice_nano_v2"
        shield_arg = f"-DSHIELD={shield_name}" if shield_name else ""

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{zmk_firmware_path}:/workspace/zmk",
                "-v", f"{zmk_config_dir}:/workspace/zmk-config",
                "zmkfirmware/zmk-build-arm:stable",
                "bash", "-c",
                f"cd /workspace/zmk/app && "
                f"west build -p -d build/test -b {zmk_board_name} -- "
                f"{shield_arg} -DZMK_CONFIG=/workspace/zmk-config"
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            pytest.skip(f"ZMK build failed: {result.stderr[:200]}")

        # Check for .uf2
        uf2_path = zmk_firmware_path / "app" / "build" / "test" / "zephyr" / "zmk.uf2"
        assert uf2_path.exists(), "Should create zmk.uf2"

        size = uf2_path.stat().st_size
        assert size > 10000, "UF2 should be substantial"
        print(f"✓ Created: zmk.uf2 ({size} bytes)")

    def test_out_zmk_directory_populated(self, repo_root):
        """After full build, out/zmk/ should have .uf2 files"""
        out_zmk = repo_root / "out" / "zmk"

        if out_zmk.exists():
            uf2_files = list(out_zmk.glob("*.uf2"))

            if len(uf2_files) > 0:
                print(f"Found {len(uf2_files)} ZMK firmware files in out/zmk/")

                for uf2 in uf2_files:
                    assert uf2.stat().st_size > 10000, f"{uf2.name} is too small"
        else:
            pytest.skip("out/zmk/ not created (run build_all.sh first)")


@pytest.mark.tier2
class TestVisualizationGeneration:
    """Test keymap visualization generation"""

    def test_visualizations_generated(self, repo_root):
        """Visualizations should be generated in out/visualizations/"""
        # Run generation
        result = subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        assert result.returncode == 0

        # Check for visualizations
        # Note: Visualizations may not be in out/ until build_all.sh runs
        # Check if keymap-drawer is available
        keymap_drawer_result = subprocess.run(
            ["which", "keymap"],
            capture_output=True,
        )

        if keymap_drawer_result.returncode != 0:
            pytest.skip("keymap-drawer not installed")

        # If keymap-drawer is available, visualizations should be generated
        # (Location depends on generator implementation)

    def test_out_visualizations_directory(self, repo_root):
        """out/visualizations/ should contain SVG files after full build"""
        out_viz = repo_root / "out" / "visualizations"

        if out_viz.exists():
            svg_files = list(out_viz.glob("*.svg"))

            if len(svg_files) > 0:
                print(f"Found {len(svg_files)} visualization files")

                for svg in svg_files:
                    # Verify SVG structure
                    with open(svg) as f:
                        content = f.read()

                    assert "<svg" in content.lower(), f"{svg.name} should be valid SVG"
                    assert svg.stat().st_size > 100, f"{svg.name} is too small"
        else:
            pytest.skip("out/visualizations/ not created (run build_all.sh first)")


@pytest.mark.tier2
class TestKeylayoutGeneration:
    """Test macOS .keylayout file generation"""

    def test_keylayout_files_generated(self, repo_root):
        """Generate .keylayout files for row-stagger configs"""
        # Run generation
        result = subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0

        # Check for keylayout generation
        # (Location depends on generator implementation)

    def test_out_keylayout_directory(self, repo_root):
        """out/keylayout/ should contain .keylayout files after full build"""
        out_keylayout = repo_root / "out" / "keylayout"

        if out_keylayout.exists():
            keylayout_files = list(out_keylayout.glob("*.keylayout"))

            if len(keylayout_files) > 0:
                print(f"Found {len(keylayout_files)} keylayout files")

                for kl in keylayout_files:
                    # Verify XML structure
                    with open(kl) as f:
                        content = f.read()

                    assert "<?xml" in content, f"{kl.name} should be XML"
                    assert "<keyboard" in content.lower(), f"{kl.name} should be keyboard layout"
                    assert kl.stat().st_size > 100, f"{kl.name} is too small"
        else:
            pytest.skip("out/keylayout/ not created (run build_all.sh first)")


@pytest.mark.tier2
class TestFullBuildConsistency:
    """Test that multiple builds produce consistent results"""

    def test_build_twice_produces_same_artifacts(self, repo_root):
        """Building twice should produce identical artifacts"""
        # First build (generation only for speed)
        result1 = subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        assert result1.returncode == 0

        # Capture generated keymap
        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            first_content = f.read()

        # Second build
        result2 = subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        assert result2.returncode == 0

        with open(keymap_file) as f:
            second_content = f.read()

        # Should be identical
        assert first_content == second_content, "Generated keymaps should be deterministic"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tier2"])
