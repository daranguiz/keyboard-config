#!/usr/bin/env python3
"""
QMK firmware compilation tests (Tier 2)

Tests actual QMK firmware compilation for all boards.
Requires QMK firmware repository and toolchains.

Setup:
    export QMK_FIRMWARE_PATH=/path/to/qmk_firmware
    # Ensure QMK toolchains are installed (avr-gcc, arm-none-eabi-gcc)
"""

import pytest
import subprocess
from pathlib import Path
import os
import re


@pytest.mark.tier2
@pytest.mark.qmk
class TestQMKCompilation:
    """Test actual QMK firmware compilation"""

    def test_qmk_setup_exists(self, qmk_firmware_path, qmk_build_env):
        """QMK firmware and build environment should be available"""
        assert qmk_firmware_path.exists(), f"QMK firmware not found at {qmk_firmware_path}"
        assert "QMK_USERSPACE" in qmk_build_env
        assert "QMK_HOME" in qmk_build_env

    def test_compile_skeletyl(self, repo_root, qmk_firmware_path, qmk_build_env):
        """Compile skeletyl firmware (36-key board)"""
        # Generate keymaps first
        result = subprocess.run(
            ["python3", "scripts/generate.py", "--board", "skeletyl"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Generation failed: {result.stderr}"

        # Compile firmware
        result = subprocess.run(
            ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
        )

        assert result.returncode == 0, f"QMK compilation failed:\n{result.stderr}"
        assert "Linking:" in result.stdout or ".hex" in result.stdout.lower()

    def test_compile_lulu(self, repo_root, qmk_firmware_path, qmk_build_env, board_inventory):
        """Compile lulu firmware (58-key board with extensions)"""
        # Check if lulu is in inventory
        if "lulu" not in board_inventory.boards:
            pytest.skip("Lulu not in board inventory")

        board = board_inventory.boards["lulu"]
        assert board.firmware == "qmk"

        # Generate keymaps
        result = subprocess.run(
            ["python3", "scripts/generate.py", "--board", "lulu"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0

        # Compile
        result = subprocess.run(
            ["qmk", "compile", "-kb", board.qmk_keyboard, "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            text=True,
            timeout=300,
        )

        assert result.returncode == 0, f"Lulu compilation failed:\n{result.stderr}"

    def test_compile_all_qmk_boards(self, repo_root, qmk_firmware_path, qmk_build_env, board_inventory):
        """Compile all QMK boards in inventory"""
        # Generate all keymaps
        result = subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Generation failed: {result.stderr}"

        # Get QMK boards
        qmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "qmk"]
        assert len(qmk_boards) > 0, "Should have at least one QMK board"

        failed_boards = []

        for board in qmk_boards:
            print(f"\n=== Compiling {board.id} ({board.qmk_keyboard}) ===")

            result = subprocess.run(
                ["qmk", "compile", "-kb", board.qmk_keyboard, "-km", "dario"],
                cwd=qmk_firmware_path,
                env=qmk_build_env,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                failed_boards.append(f"{board.id}: {result.stderr[:200]}")
            else:
                print(f"✓ {board.id} compiled successfully")

        assert len(failed_boards) == 0, f"Failed to compile boards:\n" + "\n".join(failed_boards)

    def test_qmk_firmware_size_regression(self, repo_root, qmk_firmware_path, qmk_build_env):
        """Check firmware size doesn't exceed reasonable limits"""
        # Generate keymaps
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "skeletyl"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        # Compile
        result = subprocess.run(
            ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            text=True,
            timeout=300,
        )

        assert result.returncode == 0

        # Parse size from output
        # QMK outputs: "   text    data     bss     dec     hex filename"
        size_match = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", result.stdout)
        if size_match:
            text_size = int(size_match.group(1))
            data_size = int(size_match.group(2))
            total_size = text_size + data_size

            # Pro Micro has 28672 bytes flash (ATmega32U4)
            # Warn if > 90% usage
            assert total_size < 25000, f"Firmware size {total_size} bytes exceeds safe limit"

            print(f"Firmware size: {total_size} bytes ({total_size/28672*100:.1f}% of flash)")

    def test_qmk_clean_build(self, qmk_firmware_path, qmk_build_env):
        """Test clean build (no cached objects)"""
        # Clean first
        result = subprocess.run(
            ["qmk", "clean"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            timeout=30,
        )

        # Compile from clean state
        result = subprocess.run(
            ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            text=True,
            timeout=300,
        )

        assert result.returncode == 0, "Clean build should succeed"

    def test_generated_hex_file_exists(self, qmk_firmware_path, qmk_build_env):
        """Verify .hex file is created after build"""
        # Build
        subprocess.run(
            ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            timeout=300,
        )

        # Check for .hex file in QMK build directory
        # QMK typically outputs to .build/
        build_dir = qmk_firmware_path / ".build"
        hex_files = list(build_dir.glob("*.hex"))

        assert len(hex_files) > 0, "Should generate at least one .hex file"

        # Check file size
        for hex_file in hex_files:
            size = hex_file.stat().st_size
            assert size > 1000, f"{hex_file.name} is suspiciously small ({size} bytes)"


@pytest.mark.tier2
@pytest.mark.qmk
class TestQMKKeyboardSpecifics:
    """Test board-specific QMK features"""

    def test_skeletyl_3x5_3_layout(self, repo_root, qmk_firmware_path, qmk_build_env):
        """Skeletyl should use LAYOUT_split_3x5_3"""
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "skeletyl"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        keymap_file = (
            repo_root / "qmk" / "keyboards" / "bastardkb" / "skeletyl" /
            "promicro" / "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        assert "LAYOUT_split_3x5_3" in content

        # Compile to verify layout compatibility
        result = subprocess.run(
            ["qmk", "compile", "-kb", "bastardkb/skeletyl/promicro", "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            text=True,
            timeout=300,
        )

        assert result.returncode == 0

    def test_lulu_custom_layout(self, repo_root, qmk_firmware_path, qmk_build_env, board_inventory):
        """Lulu should use custom layout with extensions"""
        if "lulu" not in board_inventory.boards:
            pytest.skip("Lulu not in inventory")

        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "lulu"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        board = board_inventory.boards["lulu"]
        keymap_file = (
            repo_root / "qmk" / "keyboards" / board.qmk_keyboard /
            "keymaps" / "dario" / "keymap.c"
        )

        with open(keymap_file) as f:
            content = f.read()

        # Lulu has custom layout size
        assert "LAYOUT" in content

        # Compile to verify
        result = subprocess.run(
            ["qmk", "compile", "-kb", board.qmk_keyboard, "-km", "dario"],
            cwd=qmk_firmware_path,
            env=qmk_build_env,
            capture_output=True,
            text=True,
            timeout=300,
        )

        assert result.returncode == 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tier2"])
