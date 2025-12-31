#!/usr/bin/env python3
"""
ZMK firmware compilation tests (Tier 2)

Tests actual ZMK firmware compilation via Docker or west.
Requires ZMK firmware repository and Docker OR west toolchain.

Setup:
    export ZMK_REPO=/path/to/zmk
    # Ensure Docker is running OR west toolchain is installed
"""

import pytest
import subprocess
from pathlib import Path
import os


@pytest.mark.tier2
@pytest.mark.zmk
@pytest.mark.requires_docker
class TestZMKCompilationDocker:
    """Test ZMK firmware compilation via Docker"""

    def test_docker_available(self, docker_available):
        """Docker should be available for ZMK builds"""
        assert docker_available, "Docker is required for ZMK builds"

    def test_zmk_repo_exists(self, zmk_firmware_path):
        """ZMK firmware repository should exist"""
        assert zmk_firmware_path.exists(), f"ZMK repo not found at {zmk_firmware_path}"
        assert (zmk_firmware_path / "app").exists(), "ZMK app directory should exist"

    def test_compile_chocofi_docker(self, repo_root, zmk_firmware_path, docker_available):
        """Compile chocofi (ZMK shield) via Docker"""
        if not docker_available:
            pytest.skip("Docker not available")

        # Generate keymaps
        result = subprocess.run(
            ["python3", "scripts/generate.py", "--board", "chocofi"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Generation failed: {result.stderr}"

        # Copy generated keymap to ZMK repo
        # Note: This assumes zmk/keymaps/corne_dario structure
        src_keymap = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"
        assert src_keymap.exists(), "Generated keymap should exist"

        # Build via Docker (using ZMK's build script approach)
        # ZMK build command: west build -d build/left -b nice_nano_v2 -- -DSHIELD=corne_left
        zmk_config_dir = repo_root / "zmk" / "keymaps" / "corne_dario"

        # Build left side
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{zmk_firmware_path}:/workspace/zmk",
                "-v", f"{zmk_config_dir}:/workspace/zmk-config",
                "zmkfirmware/zmk-build-arm:stable",
                "bash", "-c",
                "cd /workspace/zmk/app && "
                "west build -p -d build/left -b nice_nano_v2 -- "
                "-DSHIELD=corne_left -DZMK_CONFIG=/workspace/zmk-config"
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
        )

        if result.returncode != 0:
            print(f"Docker build output:\n{result.stdout}\n{result.stderr}")
            pytest.fail(f"ZMK left side compilation failed: {result.stderr[:500]}")

        assert "Building" in result.stdout or "built" in result.stdout.lower()

        # Check for .uf2 output
        # ZMK outputs to app/build/left/zephyr/zmk.uf2
        uf2_path = zmk_firmware_path / "app" / "build" / "left" / "zephyr" / "zmk.uf2"
        assert uf2_path.exists(), f"Expected .uf2 file at {uf2_path}"

        # Verify file size
        size = uf2_path.stat().st_size
        assert size > 10000, f"UF2 file is suspiciously small ({size} bytes)"
        print(f"✓ Left side compiled: {size} bytes")

    def test_compile_chocofi_both_sides(self, repo_root, zmk_firmware_path, docker_available):
        """Compile both left and right sides of split keyboard"""
        if not docker_available:
            pytest.skip("Docker not available")

        # Generate keymaps
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "chocofi"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        zmk_config_dir = repo_root / "zmk" / "keymaps" / "corne_dario"

        for side in ["left", "right"]:
            print(f"\n=== Building {side} side ===")

            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{zmk_firmware_path}:/workspace/zmk",
                    "-v", f"{zmk_config_dir}:/workspace/zmk-config",
                    "zmkfirmware/zmk-build-arm:stable",
                    "bash", "-c",
                    f"cd /workspace/zmk/app && "
                    f"west build -p -d build/{side} -b nice_nano_v2 -- "
                    f"-DSHIELD=corne_{side} -DZMK_CONFIG=/workspace/zmk-config"
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            assert result.returncode == 0, f"{side} side compilation failed"

            uf2_path = zmk_firmware_path / "app" / "build" / side / "zephyr" / "zmk.uf2"
            assert uf2_path.exists(), f"{side} .uf2 should exist"
            print(f"✓ {side} side compiled successfully")

    def test_compile_all_zmk_boards(self, repo_root, zmk_firmware_path, docker_available, board_inventory):
        """Compile all ZMK boards via Docker"""
        if not docker_available:
            pytest.skip("Docker not available")

        # Generate all keymaps
        subprocess.run(
            ["python3", "scripts/generate.py"],
            cwd=repo_root,
            capture_output=True,
            timeout=120,
        )

        # Get ZMK boards
        zmk_boards = [b for b in board_inventory.boards.values() if b.firmware == "zmk"]
        assert len(zmk_boards) > 0, "Should have at least one ZMK board"

        failed_boards = []

        for board in zmk_boards:
            print(f"\n=== Compiling {board.id} ===")

            # Determine shield and board names
            if board.zmk_shield:
                shield_base = board.zmk_shield
                # For split keyboards, build both sides
                sides = ["left", "right"]
            else:
                # Integrated board (not a shield)
                shield_base = None
                sides = [""]

            for side in sides:
                shield_name = f"{shield_base}_{side}" if shield_base and side else shield_base or ""
                build_dir = f"build/{board.id}_{side}" if side else f"build/{board.id}"

                # Determine keymap directory
                if board.zmk_shield:
                    zmk_config_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_shield}_dario"
                else:
                    zmk_config_dir = repo_root / "zmk" / "keymaps" / f"{board.zmk_board}_dario"

                # Determine board name (nice_nano_v2, etc.)
                zmk_board_name = board.zmk_board if board.zmk_board else "nice_nano_v2"

                # Build command
                shield_arg = f"-DSHIELD={shield_name}" if shield_name else ""

                result = subprocess.run(
                    [
                        "docker", "run", "--rm",
                        "-v", f"{zmk_firmware_path}:/workspace/zmk",
                        "-v", f"{zmk_config_dir}:/workspace/zmk-config",
                        "zmkfirmware/zmk-build-arm:stable",
                        "bash", "-c",
                        f"cd /workspace/zmk/app && "
                        f"west build -p -d {build_dir} -b {zmk_board_name} -- "
                        f"{shield_arg} -DZMK_CONFIG=/workspace/zmk-config"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,
                )

                if result.returncode != 0:
                    failed_boards.append(f"{board.id} {side}: {result.stderr[:200]}")
                else:
                    print(f"✓ {board.id} {side} compiled successfully")

        assert len(failed_boards) == 0, f"Failed to compile boards:\n" + "\n".join(failed_boards)

    def test_zmk_firmware_size_reasonable(self, repo_root, zmk_firmware_path, docker_available):
        """Check ZMK firmware size is reasonable"""
        if not docker_available:
            pytest.skip("Docker not available")

        # Generate and compile chocofi
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "chocofi"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        zmk_config_dir = repo_root / "zmk" / "keymaps" / "corne_dario"

        subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{zmk_firmware_path}:/workspace/zmk",
                "-v", f"{zmk_config_dir}:/workspace/zmk-config",
                "zmkfirmware/zmk-build-arm:stable",
                "bash", "-c",
                "cd /workspace/zmk/app && "
                "west build -p -d build/left -b nice_nano_v2 -- "
                "-DSHIELD=corne_left -DZMK_CONFIG=/workspace/zmk-config"
            ],
            capture_output=True,
            timeout=600,
        )

        uf2_path = zmk_firmware_path / "app" / "build" / "left" / "zephyr" / "zmk.uf2"
        size = uf2_path.stat().st_size

        # ZMK firmware is typically 100-500KB
        assert size < 1_000_000, f"Firmware size {size} bytes is unreasonably large"
        assert size > 10_000, f"Firmware size {size} bytes is unreasonably small"

        print(f"Firmware size: {size} bytes ({size/1024:.1f} KB)")


@pytest.mark.tier2
@pytest.mark.zmk
class TestZMKCompilationWest:
    """Test ZMK compilation using native west toolchain (no Docker)"""

    def test_west_available(self):
        """Check if west toolchain is available"""
        result = subprocess.run(
            ["which", "west"],
            capture_output=True,
        )

        if result.returncode != 0:
            pytest.skip("west toolchain not available (use Docker tests instead)")

    def test_compile_chocofi_west(self, repo_root, zmk_firmware_path):
        """Compile chocofi using native west toolchain"""
        # Check west availability
        result = subprocess.run(["which", "west"], capture_output=True)
        if result.returncode != 0:
            pytest.skip("west not available")

        # Generate keymaps
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "chocofi"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        zmk_config_dir = repo_root / "zmk" / "keymaps" / "corne_dario"

        # Build with west
        result = subprocess.run(
            [
                "west", "build",
                "-p", "-d", "build/left",
                "-b", "nice_nano_v2",
                "--",
                "-DSHIELD=corne_left",
                f"-DZMK_CONFIG={zmk_config_dir}"
            ],
            cwd=zmk_firmware_path / "app",
            capture_output=True,
            text=True,
            timeout=600,
        )

        assert result.returncode == 0, f"West build failed: {result.stderr}"

        uf2_path = zmk_firmware_path / "app" / "build" / "left" / "zephyr" / "zmk.uf2"
        assert uf2_path.exists()


@pytest.mark.tier2
@pytest.mark.zmk
class TestZMKKeyboardSpecifics:
    """Test board-specific ZMK features"""

    def test_chocofi_bindings_structure(self, repo_root):
        """Chocofi keymap should have proper bindings structure"""
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "chocofi"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Check structure
        assert "#include <behaviors.dtsi>" in content
        assert "#include <dt-bindings/zmk/keys.h>" in content
        assert "bindings" in content
        assert "keymap {" in content or "/ {" in content

    def test_zmk_home_row_mods(self, repo_root):
        """ZMK keymap should have home row mod behaviors"""
        subprocess.run(
            ["python3", "scripts/generate.py", "--board", "chocofi"],
            cwd=repo_root,
            capture_output=True,
            timeout=60,
        )

        keymap_file = repo_root / "zmk" / "keymaps" / "corne_dario" / "corne.keymap"

        with open(keymap_file) as f:
            content = f.read()

        # Should have home row mod behaviors
        assert "&hml" in content or "&hmr" in content or "home-row-mod" in content.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tier2"])
