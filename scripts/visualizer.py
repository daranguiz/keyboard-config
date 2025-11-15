"""
Keymap visualization generation using keymap-drawer
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict


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
        return shutil.which("keymap") is not None

    def _reorder_keys_for_qmk(self, keycodes: List[str], layout_size: str) -> List[str]:
        """
        Reorder keys from our internal format to QMK's expected format

        Our format: [L1, L2, L3, R1, R2, R3, LT, RT] (grouped by hand)
        QMK format: [L1, R1, L2, R2, L3, R3, LT, RT] (interleaved by row)

        Args:
            keycodes: List of keycodes in our internal format
            layout_size: Layout size identifier

        Returns:
            Reordered list in QMK format
        """
        if layout_size == "3x5_3":
            # 36-key layout: 3 rows × 5 cols per hand + 3 thumbs per hand
            left_top = keycodes[0:5]      # L row 1
            left_home = keycodes[5:10]    # L row 2
            left_bottom = keycodes[10:15] # L row 3
            right_top = keycodes[15:20]   # R row 1
            right_home = keycodes[20:25]  # R row 2
            right_bottom = keycodes[25:30] # R row 3
            left_thumbs = keycodes[30:33]  # L thumbs
            right_thumbs = keycodes[33:36] # R thumbs

            # Interleave: L1, R1, L2, R2, L3, R3, LT, RT
            return (left_top + right_top +
                    left_home + right_home +
                    left_bottom + right_bottom +
                    left_thumbs + right_thumbs)

        elif layout_size == "3x6_3":
            # 42-key layout: 3 rows × 6 cols per hand + 3 thumbs per hand
            left_top = keycodes[0:6]
            left_home = keycodes[6:12]
            left_bottom = keycodes[12:18]
            right_top = keycodes[18:24]
            right_home = keycodes[24:30]
            right_bottom = keycodes[30:36]
            left_thumbs = keycodes[36:39]
            right_thumbs = keycodes[39:42]

            return (left_top + right_top +
                    left_home + right_home +
                    left_bottom + right_bottom +
                    left_thumbs + right_thumbs)
        else:
            # For other layouts, assume they're already in the correct order
            return keycodes

    def generate_keymap_json(self, board, compiled_layers: List) -> Dict:
        """
        Generate QMK-style keymap JSON from compiled layers

        Args:
            board: Board object
            compiled_layers: List of CompiledLayer objects

        Returns:
            Dictionary in QMK keymap.json format
        """
        # Determine layout macro name
        if board.firmware == "qmk":
            if board.layout_size == "3x5_3":
                layout = "LAYOUT_split_3x5_3"
            elif board.layout_size == "3x6_3":
                layout = "LAYOUT_split_3x6_3"
            else:
                layout = "LAYOUT"
            keyboard = board.qmk_keyboard
        else:
            # For ZMK boards, use the QMK equivalent keyboard name for keymap-drawer
            # (keymap-drawer expects a QMK keyboard name)
            if board.layout_size == "3x6_3":
                keyboard = "crkbd/rev1"  # Corne is the QMK equivalent
                layout = "LAYOUT_split_3x6_3"
            else:
                keyboard = board.id
                layout = "LAYOUT"

        # Convert layers to QMK JSON format
        # Keys need to be reordered: our format is [L1, L2, L3, R1, R2, R3, LT, RT]
        # but QMK wants [L1, R1, L2, R2, L3, R3, LT, RT] (interleaved by row)
        layers_json = []
        for layer in compiled_layers:
            reordered = self._reorder_keys_for_qmk(layer.keycodes, board.layout_size)
            layers_json.append(reordered)

        return {
            "keyboard": keyboard,
            "keymap": "dario",
            "layout": layout,
            "layers": layers_json
        }

    def generate_for_board(self, board, compiled_layers: List) -> Optional[Path]:
        """
        Generate SVG visualization for a board using keymap-drawer

        Args:
            board: Board object with configuration
            compiled_layers: List of CompiledLayer objects with translated keycodes

        Returns:
            Path to generated SVG file, or None if generation failed
        """
        if not self.is_available():
            return None

        # Output file paths
        board_safe = board.id.replace("/", "_")
        json_file = self.output_dir / f"{board_safe}_dario.json"
        svg_file = self.output_dir / f"{board_safe}_dario.svg"

        try:
            # Generate QMK-style JSON from our compiled layers
            keymap_data = self.generate_keymap_json(board, compiled_layers)

            # Write JSON file
            json_file.write_text(json.dumps(keymap_data, indent=2))

            # Parse with keymap-drawer
            parse_cmd = ["keymap", "parse", "-q", str(json_file)]
            if self.config_file.exists():
                parse_cmd.insert(1, "-c")
                parse_cmd.insert(2, str(self.config_file))

            parse_result = subprocess.run(
                parse_cmd,
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
            svg_file.write_text(draw_result.stdout)

            return svg_file

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Visualization generation failed: {e}")
            if e.stderr:
                print(f"     {e.stderr}")
            return None
        except Exception as e:
            print(f"  ⚠️  Unexpected error during visualization: {e}")
            return None

    def generate_all(self, board_inventory, compiled_layers_by_board: Dict) -> dict:
        """
        Generate visualizations for all boards

        Args:
            board_inventory: BoardInventory object
            compiled_layers_by_board: Dictionary mapping board_id -> list of CompiledLayer objects

        Returns:
            Dictionary mapping board_id to generated SVG path (or None if failed)
        """
        if not self.is_available():
            print("  ⚠️  keymap-drawer not available, skipping visualization")
            return {}

        results = {}

        for board_id, board in board_inventory.boards.items():
            if board_id in compiled_layers_by_board:
                svg_path = self.generate_for_board(
                    board,
                    compiled_layers_by_board[board_id]
                )
                results[board_id] = svg_path

        return results
