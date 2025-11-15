"""
Keymap visualization generation using keymap-drawer
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional


class KeymapVisualizer:
    """Generate SVG visualizations of keymaps using keymap-drawer"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.output_dir = repo_root / "docs" / "keymaps"
        self.config_file = repo_root / ".keymap-drawer-config.yaml"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        """Check if keymap-drawer CLI is available"""
        return shutil.which("keymap") is not None and shutil.which("qmk") is not None

    def generate_for_qmk_board(self, board_id: str, qmk_keyboard: str, keymap: str = "dario") -> Optional[Path]:
        """
        Generate SVG visualization for a QMK board using keymap-drawer

        Args:
            board_id: Board identifier (e.g., "skeletyl")
            qmk_keyboard: QMK keyboard path (e.g., "bastardkb/skeletyl/promicro")
            keymap: Keymap name (default: "dario")

        Returns:
            Path to generated SVG file, or None if generation failed
        """
        if not self.is_available():
            return None

        # Output file path
        keyboard_safe = qmk_keyboard.replace("/", "_")
        output_file = self.output_dir / f"{keyboard_safe}_{keymap}.svg"

        try:
            # Convert keymap to JSON
            c2json_cmd = [
                "qmk", "c2json",
                "-kb", qmk_keyboard,
                "-km", keymap,
                "--no-cpp"  # Don't expand macros (avoids userspace include issues)
            ]

            c2json_result = subprocess.run(
                c2json_cmd,
                capture_output=True,
                text=True,
                check=True
            )

            keymap_json = c2json_result.stdout

            # Parse with keymap-drawer
            parse_cmd = ["keymap", "parse", "-q", "-"]
            if self.config_file.exists():
                parse_cmd.insert(1, "-c")
                parse_cmd.insert(2, str(self.config_file))

            # Don't specify layer names - let keymap-drawer auto-detect from the JSON

            parse_result = subprocess.run(
                parse_cmd,
                input=keymap_json,
                capture_output=True,
                text=True,
                check=True
            )

            parsed_keymap = parse_result.stdout

            # Draw SVG
            draw_cmd = ["keymap", "draw", "-"]
            if self.config_file.exists():
                draw_cmd.insert(1, "-c")
                draw_cmd.insert(2, str(self.config_file))

            draw_result = subprocess.run(
                draw_cmd,
                input=parsed_keymap,
                capture_output=True,
                text=True,
                check=True
            )

            # Write SVG file
            output_file.write_text(draw_result.stdout)

            return output_file

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Visualization generation failed: {e}")
            if e.stderr:
                print(f"     {e.stderr}")
            return None
        except Exception as e:
            print(f"  ⚠️  Unexpected error during visualization: {e}")
            return None

    def generate_all(self, boards: dict) -> dict:
        """
        Generate visualizations for all QMK boards

        Args:
            boards: Dictionary of board_id -> Board objects

        Returns:
            Dictionary mapping board_id to generated SVG path (or None if failed)
        """
        if not self.is_available():
            print("  ⚠️  keymap-drawer or qmk CLI not available, skipping visualization")
            return {}

        results = {}

        for board_id, board in boards.items():
            if board.firmware == "qmk":
                svg_path = self.generate_for_qmk_board(
                    board_id,
                    board.qmk_keyboard,
                    "dario"
                )
                results[board_id] = svg_path

        return results
