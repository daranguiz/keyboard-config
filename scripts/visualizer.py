"""
Keymap visualization generation using keymap-drawer
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from config_parser import YAMLConfigParser
from qmk_translator import QMKTranslator
from svglib.svglib import svg2rlg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics import renderPDF


class KeymapVisualizer:
    """Generate SVG visualizations of keymaps using keymap-drawer"""

    def __init__(self, repo_root: Path, qmk_translator: Optional[QMKTranslator] = None):
        self.repo_root = repo_root
        # Final SVGs go to docs/ root (for README embedding)
        self.docs_dir = repo_root / "docs"
        # Intermediate files (JSON, print splits, PDFs) go to out/visualizations/
        self.output_dir = repo_root / "out" / "visualizations"
        self.config_file = repo_root / ".keymap-drawer-config.yaml"
        self.config_dir = repo_root / "config"
        self.qmk_translator = qmk_translator

        # Load keycode display mappings
        self.keycodes = self._load_keycodes()

        # Ensure output directories exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_keycodes(self) -> Dict:
        """Load keycodes.yaml for display name/glyph lookups"""
        from config_parser import YAMLConfigParser
        keycodes_path = self.config_dir / "keycodes.yaml"
        if keycodes_path.exists():
            return YAMLConfigParser.parse_keycodes(keycodes_path)
        return {}

    def is_available(self) -> bool:
        """Check if keymap-drawer CLI is available"""
        return shutil.which("keymap") is not None

    def _translate_keycode_for_display(self, keycode: str) -> str:
        """
        Translate keymap.yaml format directly to keymap-drawer display format

        This bypasses firmware-specific translation to show the superset view,
        including ZMK-only keys like BT_SEL_0 that don't exist in QMK.

        Checks keycodes.yaml for display_glyph or display_name overrides.

        Args:
            keycode: Raw keycode from keymap.yaml (e.g., "hrm:LGUI:A", "lt:NAV:SPC")

        Returns:
            Keycode string for keymap-drawer display
        """
        # Handle special "no key" values
        if keycode in ["NONE", "U_NA", "U_NU", "U_NP"]:
            return "KC_NO"

        # Handle home row mods: hrm:MOD:KEY -> MOD_T(KC_KEY)
        if keycode.startswith("hrm:"):
            parts = keycode.split(":")
            if len(parts) == 3:
                mod, key = parts[1], parts[2]
                return f"{mod}_T(KC_{key})"

        # Handle layer-tap: lt:LAYER:KEY -> LT(LAYER, KC_KEY)
        if keycode.startswith("lt:"):
            parts = keycode.split(":")
            if len(parts) == 3:
                layer, key = parts[1], parts[2]
                return f"LT({layer}, KC_{key})"

        # Check for custom display glyph/name in keycodes.yaml
        if keycode in self.keycodes:
            kc_data = self.keycodes[keycode]
            # Glyph takes precedence over name
            if isinstance(kc_data, dict) and "display_glyph" in kc_data:
                return kc_data["display_glyph"]
            if isinstance(kc_data, dict) and "display_name" in kc_data:
                return kc_data["display_name"]

        # QMK boot/reset
        if keycode == "QK_BOOT":
            return "QK_BOOT"

        # Regular keycodes - prefix with KC_ for keymap-drawer
        return f"KC_{keycode}"

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

            # Post-process: Rename layers from L0-L5 to friendly names
            # keymap-drawer's layer_names config doesn't actually rename layers in parse output
            layer_names = ["BASE", "NUM", "SYM", "NAV", "MEDIA", "FUN"]
            for i, name in enumerate(layer_names):
                parsed_keymap = parsed_keymap.replace(f"L{i}:", f"{name}:")

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

    def _build_superset_layer(self, layer, layout_size: str) -> List[str]:
        """
        Build a superset layer with all keycodes from keymap.yaml (no filtering)

        Args:
            layer: Layer object from keymap.yaml
            layout_size: Layout size identifier (e.g., "3x5_3", "3x6_3")

        Returns:
            List of keycodes in our internal format (ready for QMK reordering)
        """
        keycodes = []

        # Core layout is stored as KeyGrid with rows field
        # Format: [L1, L2, L3, R1, R2, R3, LT, RT]
        # where L1-L3 are left hand rows, R1-R3 are right hand rows, LT/RT are thumb rows
        core_rows = layer.core.rows

        # Flatten the core layout
        # Left hand (rows 0-2)
        for row in core_rows[0:3]:
            keycodes.extend(row)

        # Right hand (rows 3-5)
        for row in core_rows[3:6]:
            keycodes.extend(row)

        # Thumbs (rows 6-7)
        keycodes.extend(core_rows[6])  # Left thumbs
        keycodes.extend(core_rows[7])  # Right thumbs

        # Add extensions if present for this layout size
        if layer.extensions and layout_size in layer.extensions:
            ext = layer.extensions[layout_size]

            if layout_size == "3x6_3":
                # For 3x6_3, we need to insert outer pinky columns
                # Original: [L1-L5, L6-L10, L11-L15, R1-R5, R6-R10, R11-R15, LT1-LT3, RT1-RT3]
                # Need to insert outer columns to make it proper 3x6_3
                left_outer = ext.keys.get('outer_pinky_left', ['NONE', 'NONE', 'NONE'])
                right_outer = ext.keys.get('outer_pinky_right', ['NONE', 'NONE', 'NONE'])

                # Rebuild with outer columns
                # Split back into rows
                left_rows = [keycodes[0:5], keycodes[5:10], keycodes[10:15]]
                right_rows = [keycodes[15:20], keycodes[20:25], keycodes[25:30]]
                thumbs_left = keycodes[30:33]
                thumbs_right = keycodes[33:36]

                # Add outer columns
                keycodes = []
                for i, row in enumerate(left_rows):
                    keycodes.extend([left_outer[i]] + row)
                for i, row in enumerate(right_rows):
                    keycodes.extend(row + [right_outer[i]])
                keycodes.extend(thumbs_left)
                keycodes.extend(thumbs_right)

        return keycodes

    def generate_superset_visualizations(self, board_inventory) -> Dict[str, Optional[Path]]:
        """
        Generate one visualization per layout_size using keymap.yaml superset

        Args:
            board_inventory: BoardInventory object

        Returns:
            Dictionary mapping layout_size to generated SVG path (or None if failed)
        """
        if not self.is_available():
            print("  ⚠️  keymap-drawer not available, skipping visualization")
            return {}

        # Load keymap config from YAML
        keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )

        # Group boards by layout_size
        layout_groups = {}
        for board_id, board in board_inventory.boards.items():
            size = board.layout_size
            if size not in layout_groups:
                layout_groups[size] = []
            layout_groups[size].append(board)

        results = {}

        # Generate one visualization per layout size
        for layout_size, boards in layout_groups.items():
            # Skip custom layouts for now (they need special handling)
            if layout_size.startswith("custom_"):
                print(f"  ⏭️  Skipping {layout_size} layout (custom layouts not yet supported)")
                continue

            # Use the first board as a representative for QMK keyboard metadata
            representative_board = boards[0]

            print(f"  📊 Generating visualization for {layout_size} layout ({len(boards)} boards)")

            # Build superset layers from keymap.yaml
            superset_layers = []
            for layer_name, layer in keymap_config.layers.items():
                # Skip board-specific layers (those with full_layout)
                # Only include universal layers or layers for this layout_size
                if layer.full_layout is not None:
                    # This is a custom layer (like GAME) - skip for now
                    # TODO: Handle custom layers if needed
                    continue

                keycodes = self._build_superset_layer(layer, layout_size)
                superset_layers.append({
                    'name': layer_name,
                    'keycodes': keycodes
                })

            # Generate visualization
            svg_path = self._generate_for_layout_size(
                layout_size,
                representative_board,
                superset_layers
            )
            results[layout_size] = svg_path

        return results

    def _generate_for_layout_size(self, layout_size: str, representative_board, superset_layers: List[Dict]) -> Optional[Path]:
        """
        Generate SVG visualization for a layout size

        Args:
            layout_size: Layout size identifier
            representative_board: A board object to use for QMK metadata
            superset_layers: List of dicts with 'name' and 'keycodes'

        Returns:
            Path to generated SVG file, or None if generation failed
        """
        # Generate full visualization (goes to docs/)
        svg_file = self._generate_svg_for_layers(layout_size, representative_board, superset_layers, suffix="", is_final=True)

        # Generate split versions for printing (3 layers each) - goes to out/visualizations/
        print_svgs = []
        if len(superset_layers) > 3:
            first_half = superset_layers[:3]
            second_half = superset_layers[3:]

            svg1 = self._generate_svg_for_layers(layout_size, representative_board, first_half, suffix="_print1", is_final=False)
            svg2 = self._generate_svg_for_layers(layout_size, representative_board, second_half, suffix="_print2", is_final=False)

            if svg1:
                print_svgs.append(svg1)
            if svg2:
                print_svgs.append(svg2)

            # Combine into PDF (goes to out/visualizations/)
            if print_svgs:
                pdf_file = self._combine_svgs_to_pdf(layout_size, print_svgs)
                if pdf_file:
                    print(f"    📄 {pdf_file.name}")

        return svg_file

    def _combine_svgs_to_pdf(self, layout_size: str, svg_files: List[Path]) -> Optional[Path]:
        """
        Combine multiple SVG files into a single PDF for printing

        Args:
            layout_size: Layout size identifier
            svg_files: List of SVG file paths to combine

        Returns:
            Path to generated PDF file, or None if generation failed
        """
        pdf_file = self.output_dir / f"layout_{layout_size}_print.pdf"

        # Create PDF canvas
        c = canvas.Canvas(str(pdf_file), pagesize=letter)
        page_width, page_height = letter

        for svg_path in svg_files:
            # Render SVG to ReportLab drawing
            drawing = svg2rlg(str(svg_path))

            if drawing is None:
                print(f"  ⚠️  Failed to load SVG: {svg_path}")
                continue

            # Scale to fit page (with margins)
            margin = 36  # 0.5 inch margins
            available_width = page_width - (2 * margin)
            available_height = page_height - (2 * margin)

            # Calculate scaling factor to fit page
            scale_x = available_width / drawing.width
            scale_y = available_height / drawing.height
            scale = min(scale_x, scale_y, 1.0)  # Don't scale up, only down

            # Center the drawing
            scaled_width = drawing.width * scale
            scaled_height = drawing.height * scale
            x = margin + (available_width - scaled_width) / 2
            y = margin + (available_height - scaled_height) / 2

            # Draw on canvas
            drawing.scale(scale, scale)
            renderPDF.draw(drawing, c, x, y)
            c.showPage()

        c.save()
        return pdf_file

    def _generate_svg_for_layers(self, layout_size: str, representative_board, layers: List[Dict], suffix: str = "", is_final: bool = False) -> Optional[Path]:
        """
        Generate SVG visualization for specific layers

        Args:
            layout_size: Layout size identifier
            representative_board: A board object to use for QMK metadata
            layers: List of dicts with 'name' and 'keycodes'
            suffix: Optional suffix for filename (e.g., "_print1")
            is_final: If True, outputs final SVG to docs/; otherwise to out/visualizations/

        Returns:
            Path to generated SVG file, or None if generation failed
        """
        # Choose output directory based on whether this is a final or intermediate file
        if is_final:
            # Final SVGs (no suffix) go to docs/ for README embedding
            svg_output_dir = self.docs_dir
        else:
            # Intermediate files (print splits, etc.) go to out/visualizations/
            svg_output_dir = self.output_dir

        # JSON files always go to out/visualizations/
        json_file = self.output_dir / f"layout_{layout_size}{suffix}.json"
        svg_file = svg_output_dir / f"layout_{layout_size}{suffix}.svg"

        try:
            # Determine QMK keyboard metadata
            if representative_board.firmware == "qmk":
                keyboard = representative_board.qmk_keyboard
            else:
                # For ZMK boards, use QMK equivalent
                if layout_size == "3x6_3":
                    keyboard = "crkbd/rev1"
                elif layout_size == "3x5_3":
                    keyboard = "bastardkb/skeletyl/promicro"
                else:
                    keyboard = representative_board.id

            # Determine layout macro
            if layout_size == "3x5_3":
                layout = "LAYOUT_split_3x5_3"
            elif layout_size == "3x6_3":
                layout = "LAYOUT_split_3x6_3"
            else:
                layout = "LAYOUT"

            # Convert to QMK JSON format
            layers_json = []
            for layer in layers:
                # Translate keycodes to QMK format for keymap-drawer
                translated = [self._translate_keycode_for_display(kc) for kc in layer['keycodes']]
                # Reorder keys for QMK layout
                reordered = self._reorder_keys_for_qmk(translated, layout_size)
                layers_json.append(reordered)

            keymap_data = {
                "keyboard": keyboard,
                "keymap": "dario",
                "layout": layout,
                "layers": layers_json
            }

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

            # Post-process: Rename layers from L0-L5 to friendly names
            layer_names = [layer['name'] for layer in layers]
            for i, name in enumerate(layer_names):
                parsed_keymap = parsed_keymap.replace(f"L{i}:", f"{name}:")

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

            if suffix:
                print(f"    ✅ {svg_file.name}")
            else:
                print(f"    ✅ {svg_file.name}")
            return svg_file

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Visualization generation failed for {layout_size}{suffix}: {e}")
            if e.stderr:
                print(f"     {e.stderr}")
            return None
        except Exception as e:
            print(f"  ⚠️  Unexpected error during visualization for {layout_size}{suffix}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_all(self, board_inventory, compiled_layers_by_board: Dict) -> dict:
        """
        Generate visualizations for all boards (DEPRECATED - now generates per layout_size)

        Args:
            board_inventory: BoardInventory object
            compiled_layers_by_board: Dictionary mapping board_id -> list of CompiledLayer objects

        Returns:
            Dictionary mapping layout_size to generated SVG path (or None if failed)
        """
        # Call new superset visualization method
        return self.generate_superset_visualizations(board_inventory)
