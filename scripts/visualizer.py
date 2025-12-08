"""
Keymap visualization generation using keymap-drawer
"""

import json
import os
import re
import subprocess
import shutil
import tempfile
import yaml
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Iterator
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

    def _get_friendly_key_name(self, key: str) -> str:
        """
        Get friendly display name for a key

        Args:
            key: Key name from keymap.yaml (e.g., "SPC", "R", "ENT")

        Returns:
            Friendly display name (e.g., "Space", "R", "Enter")
        """
        # Check keycodes.yaml for display_glyph or display_name
        if key in self.keycodes:
            kc_data = self.keycodes[key]
            if isinstance(kc_data, dict):
                if "display_glyph" in kc_data:
                    return kc_data["display_glyph"]
                if "display_name" in kc_data:
                    return kc_data["display_name"]

        # Smart defaults for common keys
        if len(key) == 1 and key.isalpha():
            return key.lower()  # Single letters → lowercase

        # Map of special keys to friendly names
        special_keys = {
            "SPC": "Space",
            "ENT": "Enter",
            "BSPC": "Bksp",
            "DEL": "Del",
            "TAB": "Tab",
        }
        return special_keys.get(key, key)

    def _generate_layer_tap_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        Extract all layer-tap and mod-tap keys from keymap.yaml and generate display mappings

        Returns:
            Dictionary mapping QMK codes to {tap, hold} display format
            Example: {"LT(NUM_NIGHT, KC_R)": {"tap": "R", "hold": "NUM"}}
        """
        # Load keymap config
        keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )

        # Load layer_legend_map from .keymap-drawer-config.yaml for layer display names
        with open(self.config_file) as f:
            drawer_config = yaml.safe_load(f)
        layer_legend_map = drawer_config.get('parse_config', {}).get('layer_legend_map', {})

        # Track unique (layer, key) or (mod, key) combinations
        lt_combinations = set()  # For layer-tap keys
        mt_combinations = set()  # For mod-tap keys

        # Scan all layers
        for layer_name, layer in keymap_config.layers.items():
            # Scan core layout
            if layer.core:
                for row in layer.core.rows:
                    for keycode in row:
                        if keycode.startswith("lt:"):
                            parts = keycode.split(":")
                            if len(parts) == 3:
                                lt_combinations.add((parts[1], parts[2]))
                        elif keycode.startswith("mt:"):
                            parts = keycode.split(":")
                            if len(parts) == 3:
                                mt_combinations.add((parts[1], parts[2]))

            # Scan extensions
            if layer.extensions:
                for layout_size, ext in layer.extensions.items():
                    if hasattr(ext, 'keys') and ext.keys:
                        for key_list_name, key_list in ext.keys.items():
                            # key_list might be a single string or a list
                            keys_to_check = key_list if isinstance(key_list, list) else [key_list]
                            for keycode in keys_to_check:
                                if keycode.startswith("lt:"):
                                    parts = keycode.split(":")
                                    if len(parts) == 3:
                                        lt_combinations.add((parts[1], parts[2]))
                                elif keycode.startswith("mt:"):
                                    parts = keycode.split(":")
                                    if len(parts) == 3:
                                        mt_combinations.add((parts[1], parts[2]))

        # Generate mappings
        mappings = {}

        # Layer-tap mappings
        for layer, key in lt_combinations:
            # Lowercase alpha keys in the QMK code to match translation output
            key_display = key.lower() if len(key) == 1 and key.isalpha() else key
            qmk_code = f"LT({layer}, KC_{key_display})"
            tap_display = self._get_friendly_key_name(key)
            # Use layer_legend_map to get friendly layer name, fallback to layer name
            hold_display = layer_legend_map.get(layer, layer)
            mappings[qmk_code] = {"tap": tap_display, "hold": hold_display}

        # Mod-tap mappings
        for mod, key in mt_combinations:
            # Lowercase alpha keys in the QMK code to match translation output
            key_display = key.lower() if len(key) == 1 and key.isalpha() else key
            qmk_code = f"{mod}_T(KC_{key_display})"
            tap_display = self._get_friendly_key_name(key)
            # Get modifier display from keycodes.yaml, fallback to mod name
            hold_display = self._get_friendly_key_name(mod)
            mappings[qmk_code] = {"tap": tap_display, "hold": hold_display}

        return mappings

    def is_available(self) -> bool:
        """Check if keymap-drawer CLI is available"""
        return shutil.which("keymap") is not None

    def _get_base_layer_names(self) -> List[str]:
        """Get all BASE_* layer names from keymap.yaml"""
        keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )
        return [name for name in keymap_config.layers.keys() if name.startswith("BASE_")]

    def _get_layer_tap_positions_for_layer(self, layer_name: str, layout_size: str) -> List[int]:
        """
        Get the actual positions of layer-tap keys for a specific layer

        Args:
            layer_name: Name of the layer
            layout_size: Layout size identifier

        Returns:
            List of key positions that have layer-tap (lt:) keys
        """
        # Load the keymap config
        keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )

        if layer_name not in keymap_config.layers:
            return []

        layer = keymap_config.layers[layer_name]

        # Build the full keycode list for this layer
        keycodes = self._build_superset_layer(layer, layout_size)

        # Reorder to QMK format to match SVG positions
        reordered = self._reorder_keys_for_qmk(keycodes, layout_size)

        # Find positions with lt: prefix
        layer_tap_positions = []
        for i, keycode in enumerate(reordered):
            if keycode.startswith("lt:"):
                layer_tap_positions.append(i)

        return layer_tap_positions

    def _get_hrm_positions_for_layer(self, layer_name: str, layout_size: str) -> List[int]:
        """
        Get the actual positions of home row mod (hrm:) keys for a specific layer

        Args:
            layer_name: Name of the layer
            layout_size: Layout size identifier

        Returns:
            List of key positions that have hrm: keys
        """
        # Load the keymap config
        keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )

        if layer_name not in keymap_config.layers:
            return []

        layer = keymap_config.layers[layer_name]

        # Build the full keycode list for this layer
        keycodes = self._build_superset_layer(layer, layout_size)

        # Reorder to QMK format to match SVG positions
        reordered = self._reorder_keys_for_qmk(keycodes, layout_size)

        # Find positions with hrm: prefix
        hrm_positions = []
        for i, keycode in enumerate(reordered):
            if keycode.startswith("hrm:"):
                hrm_positions.append(i)

        return hrm_positions

    def _get_mod_tap_positions_for_layer(self, layer_name: str, layout_size: str) -> List[int]:
        """
        Get the actual positions of mod-tap (mt:) keys for a specific layer

        Args:
            layer_name: Name of the layer
            layout_size: Layout size identifier

        Returns:
            List of key positions that have mod-tap (mt:) keys
        """
        # Load the keymap config
        keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )

        if layer_name not in keymap_config.layers:
            return []

        layer = keymap_config.layers[layer_name]

        # Build the full keycode list for this layer
        keycodes = self._build_superset_layer(layer, layout_size)

        # Reorder to QMK format to match SVG positions
        reordered = self._reorder_keys_for_qmk(keycodes, layout_size)

        # Find positions with mt: prefix
        mod_tap_positions = []
        for i, keycode in enumerate(reordered):
            if keycode.startswith("mt:"):
                mod_tap_positions.append(i)

        return mod_tap_positions

    def _generate_dynamic_css(self, layout_size: str, base_layers: List[str], layers_in_viz: List = None) -> str:
        """
        Generate dynamic CSS for layer highlighting based on layout and layer names

        Args:
            layout_size: Layout size identifier (e.g., "3x5_3", "3x6_3")
            base_layers: List of BASE_* layer names
            layers_in_viz: Optional list of Layer objects being visualized (for targeted CSS)

        Returns:
            CSS string with dynamic layer highlighting
        """
        css = '''
'''
        # Build CSS selectors dynamically for each BASE layer's actual layer-tap positions
        base_layer_selectors = []
        base_layer_text_selectors = []

        for layer in base_layers:
            # Get the actual layer-tap positions for this specific layer
            layer_tap_positions = self._get_layer_tap_positions_for_layer(layer, layout_size)

            for pos in layer_tap_positions:
                base_layer_selectors.append(f"    .layer-{layer} .keypos-{pos} rect")
                base_layer_text_selectors.append(f"    .layer-{layer} .keypos-{pos} text")

        # Build home row mod selectors dynamically from hrm: and mt: prefixes
        home_row_selectors = []
        for layer in base_layers:
            # Get positions of hrm: (home row mod) keys
            hrm_positions = self._get_hrm_positions_for_layer(layer, layout_size)
            for pos in hrm_positions:
                home_row_selectors.append(f"    .layer-{layer} .keypos-{pos} rect")

            # Also add mod-tap (mt:) positions - they should have same styling as hrm
            mod_tap_positions = self._get_mod_tap_positions_for_layer(layer, layout_size)
            for pos in mod_tap_positions:
                home_row_selectors.append(f"    .layer-{layer} .keypos-{pos} rect")

        # Continue building CSS
        css += '''
    /* Remove underline from layer activator text */
    text.layer-activator {
      text-decoration: none !important;
    }

    /* Remove bold from hold text (layer names on modifier keys) */
    text.hold {
      font-weight: normal !important;
    }

    /* Highlight layer-tap keys with bright green on all BASE layers */
'''
        css += ",\n".join(base_layer_selectors)
        css += ''' {
      fill: #4CAF50 !important;
      stroke: none !important;
      opacity: 1 !important;
    }
'''
        css += ",\n".join(base_layer_text_selectors)
        css += ''' {
      fill: white !important;
    }
'''
        # Add glyph selectors (for SVG icons like backspace, enter, etc.)
        base_layer_glyph_selectors = [s.replace(' text', ' use') for s in base_layer_text_selectors]
        css += ",\n".join(base_layer_glyph_selectors)
        css += ''' {
      fill: white !important;
    }

    /* Highlight home row mods and mod-tap keys with lighter green stroke on all BASE layers */
'''
        css += ",\n".join(home_row_selectors)
        css += ''' {
      stroke: #66BB6A !important;
      stroke-width: 2 !important;
    }

    /* On other layers, highlight the key that keeps you on that layer */
'''

        # For non-BASE layers, find the position of the layer-tap key that activates them
        # Look through the actual layers being visualized to find the correct activator positions
        layer_activator_positions = {}

        if layers_in_viz and base_layers:
            # Use the BASE layer from the visualization set to find activator positions
            # This ensures we get the correct thumb positions for each base layer variant
            for base_layer_name in base_layers:
                # Find the base layer object
                base_layer = next((l for l in layers_in_viz if l.name == base_layer_name), None)
                if not base_layer:
                    continue

                # Get the keycodes for this base layer
                keycodes = self._build_superset_layer(base_layer, layout_size)
                reordered = self._reorder_keys_for_qmk(keycodes, layout_size)

                # Find positions for each layer activator in this base layer
                for i, keycode in enumerate(reordered):
                    if keycode.startswith("lt:"):
                        parts = keycode.split(":")
                        if len(parts) >= 2:
                            layer_name = parts[1]
                            # Map the activator position for this layer
                            # Only set if not already set (first occurrence wins)
                            if layer_name not in layer_activator_positions:
                                layer_activator_positions[layer_name] = i
        elif base_layers:
            # Fallback: Use the first BASE layer to find activator positions
            first_base = base_layers[0]
            keymap_config = YAMLConfigParser.parse_keymap(self.config_dir / "keymap.yaml")
            layer = keymap_config.layers[first_base]
            keycodes = self._build_superset_layer(layer, layout_size)
            reordered = self._reorder_keys_for_qmk(keycodes, layout_size)

            # Find positions for each layer activator
            for i, keycode in enumerate(reordered):
                if keycode.startswith("lt:"):
                    parts = keycode.split(":")
                    if len(parts) >= 2:
                        layer_name = parts[1]
                        layer_activator_positions[layer_name] = i

        # Generate CSS for layer activators
        activator_selectors = []
        activator_text_selectors = []

        for layer_name, pos in layer_activator_positions.items():
            activator_selectors.append(f"    .layer-{layer_name} .keypos-{pos} rect")
            activator_text_selectors.append(f"    .layer-{layer_name} .keypos-{pos} text")

        if activator_selectors:
            css += ",\n".join(activator_selectors)
            css += ''' {
      fill: #FF9800 !important;
      stroke: none !important;
    }
'''
            css += ",\n".join(activator_text_selectors)
            css += ''' {
      fill: white !important;
    }
'''
            # Add glyph selectors for orange activator keys
            activator_glyph_selectors = [s.replace(' text', ' use') for s in activator_text_selectors]
            css += ",\n".join(activator_glyph_selectors)
            css += ''' {
      fill: white !important;
    }
'''

        css += '''

    /* Make sure ghost keys (on other layers) are clearly different */
    .key.ghost rect {
      opacity: 0.3 !important;
    }
'''
        return css

    @contextmanager
    def _get_layout_specific_config(self, layout_size: str, layers_in_viz: List = None) -> Iterator[Path]:
        """
        Create a layout-specific config file with correct key position styling

        Args:
            layout_size: Layout size identifier (e.g., "3x5_3", "3x6_3")
            layers_in_viz: Optional list of Layer objects being visualized (for targeted CSS)

        Returns:
            Path to the layout-specific config file
        """
        # Load base config
        with open(self.config_file) as f:
            config = yaml.safe_load(f)

        # Determine which base layers to use for CSS generation
        if layers_in_viz:
            # Use only the base layers present in this visualization
            base_layers = [layer.name for layer in layers_in_viz if layer.name.startswith("BASE_")]
        else:
            # Fallback: get all BASE layer names dynamically
            base_layers = self._get_base_layer_names()

        # Update ortho_layout for the specific board size
        if layout_size == "3x6_3":
            config['draw_config']['ortho_layout'] = {
                'split': True,
                'rows': 3,
                'columns': 6,
                'thumbs': 3
            }

        # Generate dynamic CSS based on layout size and BASE layers
        config['draw_config']['svg_extra_style'] = self._generate_dynamic_css(layout_size, base_layers, layers_in_viz)

        # Auto-generate layer-tap and mod-tap mappings from keymap.yaml
        auto_generated_mappings = self._generate_layer_tap_mappings()

        # Merge auto-generated mappings into raw_binding_map
        # Keep existing static entries, but replace any LT(...) or *_T(...) entries
        if 'parse_config' not in config:
            config['parse_config'] = {}
        if 'raw_binding_map' not in config['parse_config']:
            config['parse_config']['raw_binding_map'] = {}

        # Remove old layer-tap and mod-tap entries (will be replaced by auto-generated ones)
        raw_binding_map = config['parse_config']['raw_binding_map']
        keys_to_remove = [k for k in raw_binding_map.keys() if k.startswith("LT(") or "_T(KC_" in k]
        for key in keys_to_remove:
            del raw_binding_map[key]

        # Add auto-generated mappings
        raw_binding_map.update(auto_generated_mappings)

        # Write to temp config file in system temp directory
        fd, temp_path = tempfile.mkstemp(
            prefix=f"keymap-drawer-{layout_size}-", suffix=".yaml"
        )
        temp_config = Path(temp_path)
        with os.fdopen(fd, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        try:
            yield temp_config
        finally:
            if temp_config.exists():
                temp_config.unlink()

    def _add_inline_font_size(self, svg_content: str) -> str:
        """
        Add inline font-size attributes to tap text elements for PDF compatibility

        svglib (used for SVG-to-PDF conversion) doesn't fully support CSS class
        selectors like 'text.key.tap', so we add inline font-size attributes.

        Args:
            svg_content: SVG markup string

        Returns:
            Updated SVG markup with inline font-size attributes
        """
        import re

        # Pattern to match text elements with class="key tap" (in either order)
        # We need to handle both 'class="key tap"' and 'class="tap key"'
        pattern = re.compile(
            r'(<text\s+[^>]*class="(?:key tap|tap key)"[^>]*)(>)',
            re.IGNORECASE
        )

        def add_font_size(match: re.Match) -> str:
            opening_tag = match.group(1)
            closing_bracket = match.group(2)

            # Check if style attribute already exists
            if 'style=' in opening_tag:
                # Append to existing style
                opening_tag = opening_tag.replace('style="', 'style="font-size: 20px; ')
                return f'{opening_tag}{closing_bracket}'
            else:
                # Add new style attribute
                # Use style attribute instead of font-size attribute for better svglib support
                return f'{opening_tag} style="font-size: 20px"{closing_bracket}'

        return pattern.sub(add_font_size, svg_content)

    def _format_layer_labels(self, svg_content: str, layout_size: str) -> str:
        """
        Center layer labels between halves and enlarge text

        Args:
            svg_content: Raw SVG markup from keymap-drawer
            layout_size: Layout identifier to determine positioning

        Returns:
            Updated SVG markup with formatted layer labels
        """
        label_layouts = {
            # x coordinates account for the leading translate(30, 0) wrapping each layer group.
            # Values = (canvas_width / 2) - 30 to place text at actual center line.
            "3x6_3": {"x": 420, "y": 133, "font_size": 28},  # width=900
            "3x5_3": {"x": 448, "y": 112, "font_size": 28},  # width=956
        }
        defaults = {"x": 420, "y": 120, "font_size": 26}
        config = label_layouts.get(layout_size, defaults)

        pattern = re.compile(
            r'(?P<indent>\s*)<text x="[^"]+" y="[^"]+" class="label" id="(?P<id>[^"]+)">[^<]*</text>'
        )

        def _replace(match: re.Match) -> str:
            indent = match.group("indent")
            layer_id = match.group("id")
            style = 'style="text-anchor: middle; dominant-baseline: middle;"'
            return (
                f'{indent}<text x="{config["x"]}" y="{config["y"]}" class="label" id="{layer_id}" '
                f'text-anchor="middle" dominant-baseline="middle" font-size="{config["font_size"]}" {style}>{layer_id}</text>'
            )

        return pattern.sub(_replace, svg_content)

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
                # Lowercase single letter keys
                key_display = key.lower() if len(key) == 1 and key.isalpha() else key
                return f"{mod}_T(KC_{key_display})"

        # Handle mod-tap: mt:MOD:KEY -> MOD_T(KC_KEY)
        # Same display as hrm, but different behavior (no chordal hold)
        if keycode.startswith("mt:"):
            parts = keycode.split(":")
            if len(parts) == 3:
                mod, key = parts[1], parts[2]
                # Lowercase single letter keys
                key_display = key.lower() if len(key) == 1 and key.isalpha() else key
                return f"{mod}_T(KC_{key_display})"

        # Handle layer-tap: lt:LAYER:KEY -> LT(LAYER, KC_KEY)
        if keycode.startswith("lt:"):
            parts = keycode.split(":")
            if len(parts) == 3:
                layer, key = parts[1], parts[2]
                # Lowercase single letter keys
                key_display = key.lower() if len(key) == 1 and key.isalpha() else key
                return f"LT({layer}, KC_{key_display})"

        # Handle default layer switch: df:LAYER -> DF(LAYER)
        if keycode.startswith("df:"):
            parts = keycode.split(":")
            if len(parts) == 2:
                layer = parts[1]
                return f"DF({layer})"

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
        # Only lowercase single letter alpha keys
        if len(keycode) == 1 and keycode.isalpha():
            return f"KC_{keycode.lower()}"
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

            # Get layout-specific config (handles ortho_layout and CSS styling)
            with self._get_layout_specific_config(board.layout_size) as layout_config:
                # Parse with keymap-drawer (config must come before subcommand)
                parse_cmd = ["keymap", "-c", str(layout_config), "parse", "-q", str(json_file)]

                parse_result = subprocess.run(
                    parse_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                parsed_keymap = parse_result.stdout

                # Post-process: Rename layers from L0-L7 to friendly names
                # keymap-drawer's layer_names config doesn't actually rename layers in parse output
                layer_names = ["COLEMAK", "GALLIUM", "NIGHT", "NUM", "SYM", "NAV", "MEDIA", "FUN"]
                for i, name in enumerate(layer_names):
                    parsed_keymap = parsed_keymap.replace(f"L{i}:", f"{name}:")

                # Draw SVG (config must come before subcommand)
                draw_cmd = ["keymap", "-c", str(layout_config), "draw", "-"]

                draw_result = subprocess.run(
                    draw_cmd,
                    input=parsed_keymap,
                    capture_output=True,
                    text=True,
                    check=True
                )

                svg_output = self._format_layer_labels(
                    draw_result.stdout, board.layout_size
                )

                # Replace BASE_* layer names with clean names in SVG
                svg_output = svg_output.replace('BASE_COLEMAK', 'COLEMAK')
                svg_output = svg_output.replace('BASE_GALLIUM', 'GALLIUM')
                svg_output = svg_output.replace('BASE_NIGHT', 'NIGHT')
                svg_output = svg_output.replace('BASE_DUSK', 'DUSK')

                # Write SVG file
                svg_file.write_text(svg_output)

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

    def _get_layer_sets_by_base(self) -> Dict[str, List[str]]:
        """Map each base layer to its associated layers"""
        return {
            'BASE_NIGHT': ['BASE_NIGHT', 'SYM_NIGHT', 'NUM_NIGHT',
                          'NAV_NIGHT', 'MEDIA_NIGHT', 'FUN'],
            'BASE_DUSK': ['BASE_DUSK', 'SYM_NIGHT', 'NUM_NIGHT',
                          'NAV_NIGHT', 'MEDIA_NIGHT', 'FUN'],
            'BASE_COLEMAK': ['BASE_COLEMAK', 'SYM', 'NUM', 'NAV', 'MEDIA', 'FUN']
        }

    def generate_superset_visualizations(self, board_inventory) -> None:
        """Generate visualizations grouped by base layer (3x6_3 only)"""
        if not self.is_available():
            print("  ⚠️  keymap-drawer not available, skipping visualization")
            return

        print("📊 Generating keymap visualizations...")

        layer_sets = self._get_layer_sets_by_base()
        layout_size = "3x6_3"

        for base_name, layer_names in layer_sets.items():
            print(f"  📊 Generating visualization for {base_name}")
            self._generate_for_base_layer(base_name, layer_names, layout_size)

        print(f"✅ Generated {len(layer_sets)} base layer visualizations")

    def _generate_for_base_layer(self, base_name: str, layer_names: List[str],
                                  layout_size: str) -> None:
        """Generate complete visualization set for one base layer"""

        # Load and filter layers
        keymap_config = YAMLConfigParser.parse_keymap(self.config_dir / "keymap.yaml")
        layers = [keymap_config.layers[name] for name in layer_names
                  if name in keymap_config.layers]

        if not layers:
            return

        # Remove BASE_ prefix and convert to lowercase for output filename
        # BASE_NIGHT -> night, BASE_NIGHT_V2 -> night_v2, BASE_COLEMAK -> colemak
        output_name = base_name.replace('BASE_', '').lower()

        # Generate full SVG
        self._generate_svg_for_layers(layers, layout_size, output_name=output_name)

        # Generate 2-page print PDF
        self._generate_print_pdf_for_base(base_name, layers, layout_size)

        # Generate single-layer base PDF for large printing
        self._generate_single_layer_pdf(base_name, layers[0], layout_size)

        # Clean up main JSON file
        json_file = self.output_dir / f"{output_name}.json"
        if json_file.exists():
            json_file.unlink()

    def _generate_print_pdf_for_base(self, base_name: str, all_layers: List,
                                     layout_size: str) -> Path:
        """Generate 2-page PDF with same layer order as SVG (3 layers per page)"""

        # Remove BASE_ prefix and convert to lowercase for output filename
        output_name = base_name.replace('BASE_', '').lower()

        # Split layers into two pages, maintaining the same order as the main SVG
        # Page 1: First 3 layers (BASE, SYM, NUM)
        # Page 2: Last 3 layers (NAV, MEDIA, FUN)
        page1_layers = all_layers[:3]
        page2_layers = all_layers[3:]

        # Generate page SVGs for PDF (no white outline on labels)
        # For page 2, we need to pass all_layers for CSS generation context
        # so the orange highlighting knows the thumb key positions from the BASE layer
        svg1 = self._generate_svg_for_layers(
            page1_layers, layout_size, suffix="_print1",
            output_name=output_name, for_display=False
        )
        svg2 = self._generate_svg_for_layers(
            page2_layers, layout_size, suffix="_print2",
            output_name=output_name,
            css_context_layers=all_layers, for_display=False
        )

        # Combine to PDF
        pdf_file = self._combine_svgs_to_pdf(output_name, [svg1, svg2])

        # Clean up intermediate SVGs only if PDF generation succeeded
        if pdf_file:
            svg1.unlink()
            svg2.unlink()

        # Clean up JSON files
        for suffix in ["_print1", "_print2"]:
            json_file = self.output_dir / f"{output_name}{suffix}.json"
            if json_file.exists():
                json_file.unlink()

        return pdf_file

    def _generate_svg_for_layers(self, layers: List, layout_size: str,
                                 suffix: str = "", output_name: str = None,
                                 css_context_layers: List = None, for_display: bool = True) -> Path:
        """
        Generate SVG visualization for specific layers

        Args:
            layers: List of Layer objects from keymap.yaml
            layout_size: Layout size identifier
            suffix: Optional suffix for filename (e.g., "_print1")
            output_name: Optional custom output name (defaults to layout_{layout_size})
            css_context_layers: Full layer list for CSS generation context (defaults to layers)
            for_display: If True, apply SVG styling (white outline). If False, apply PDF styling (no outline).

        Returns:
            Path to generated SVG file
        """
        if output_name is None:
            output_name = f"layout_{layout_size}{suffix}"
        else:
            output_name = f"{output_name}{suffix}"

        # JSON files always go to out/visualizations/
        json_file = self.output_dir / f"{output_name}.json"

        # Final SVGs (without suffix like _print1) go to docs/ for README embedding
        # Intermediate files go to out/visualizations/
        if suffix:
            svg_file = self.output_dir / f"{output_name}.svg"
        else:
            svg_file = self.docs_dir / f"{output_name}.svg"

        try:
            # Determine QMK keyboard metadata for keymap-drawer
            # Use crkbd as the canonical 3x6_3 keyboard for visualization
            if layout_size == "3x6_3":
                keyboard = "crkbd/rev1"
                layout = "LAYOUT_split_3x6_3"
            elif layout_size == "3x5_3":
                keyboard = "bastardkb/skeletyl/promicro"
                layout = "LAYOUT_split_3x5_3"
            else:
                keyboard = "crkbd/rev1"
                layout = "LAYOUT"

            # Convert to QMK JSON format
            layers_json = []
            for layer in layers:
                # Build keycodes from Layer object
                keycodes = self._build_superset_layer(layer, layout_size)
                # Translate keycodes to QMK format for keymap-drawer
                translated = [self._translate_keycode_for_display(kc) for kc in keycodes]
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

            # Get layout-specific config (handles ortho_layout and CSS styling)
            # Pass css_context_layers (for CSS generation) if provided, otherwise use layers
            # This allows page 2 of PDFs to use the BASE layer from all_layers for thumb positions
            context_layers = css_context_layers if css_context_layers is not None else layers
            with self._get_layout_specific_config(layout_size, context_layers) as layout_config:
                # Parse with keymap-drawer (config must come before subcommand)
                parse_cmd = ["keymap", "-c", str(layout_config), "parse", "-q", str(json_file)]

                parse_result = subprocess.run(
                    parse_cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                parsed_keymap = parse_result.stdout

                # Post-process: Rename layers from L0-L5 to friendly names
                layer_names = [layer.name for layer in layers]
                for i, name in enumerate(layer_names):
                    parsed_keymap = parsed_keymap.replace(f"L{i}:", f"{name}:")

                # Draw SVG (config must come before subcommand)
                draw_cmd = ["keymap", "-c", str(layout_config), "draw", "-"]

                draw_result = subprocess.run(
                    draw_cmd,
                    input=parsed_keymap,
                    capture_output=True,
                    text=True,
                    check=True
                )

                svg_output = self._format_layer_labels(
                    draw_result.stdout, layout_size
                )

                # Replace BASE_* layer names with clean names in SVG
                # Order matters: replace longer names first to avoid partial matches
                svg_output = svg_output.replace('BASE_COLEMAK', 'COLEMAK')
                svg_output = svg_output.replace('BASE_GALLIUM', 'GALLIUM')
                svg_output = svg_output.replace('BASE_NIGHT', 'NIGHT')
                svg_output = svg_output.replace('BASE_DUSK', 'DUSK')

                # Replace NIGHT variant layer names with clean names (NUM, SYM, etc.)
                svg_output = svg_output.replace('NUM_NIGHT', 'NUM')
                svg_output = svg_output.replace('SYM_NIGHT', 'SYM')
                svg_output = svg_output.replace('NAV_NIGHT', 'NAV')
                svg_output = svg_output.replace('MEDIA_NIGHT', 'MEDIA')

                # Apply inline styles for better rendering
                # for_display controls white outline: True=white outline (SVG), False=no outline (PDF)
                svg_output = self._add_inline_styles_for_pdf(svg_output, for_pdf=not for_display)

                # Write SVG file
                svg_file.write_text(svg_output)

            print(f"    ✅ {svg_file.name}")
            return svg_file

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Visualization generation failed for {output_name}: {e}")
            if e.stderr:
                print(f"     {e.stderr}")
            return None
        except Exception as e:
            print(f"  ⚠️  Unexpected error during visualization for {output_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _add_inline_styles_for_pdf(self, svg_content: str, for_pdf: bool = True) -> str:
        """
        Add inline style attributes to text elements for PDF rendering

        svglib doesn't support CSS classes well, so we need to add inline styles
        to ensure proper rendering in PDFs.

        Args:
            svg_content: SVG markup string
            for_pdf: If True, omit white stroke on labels (for PDF). If False, include it (for SVG).

        Returns:
            Updated SVG markup with inline styles
        """
        import re

        # Pattern to match text elements with class="key tap" and capture the content
        tap_pattern = re.compile(
            r'(<text\s+[^>]*class="(?:[^"]*\s)?tap(?:\s[^"]*)?"[^>]*)(>)([^<]*)(</text>)',
            re.IGNORECASE
        )

        def add_tap_inline_style(match: re.Match) -> str:
            opening_tag = match.group(1)
            closing_bracket = match.group(2)
            content = match.group(3)
            closing_tag = match.group(4)

            # Determine if this should be bold
            # Bold for: single alphas, single digits, symbols (not multi-char words like "Space", "Undo", F1-F12)

            # Check for HTML entities that represent single characters
            single_char_entities = ['&lt;', '&gt;', '&quot;', '&amp;', '&apos;']

            should_be_bold = (
                (len(content) == 1) or  # Single char (letters, digits, symbols)
                (len(content) == 2 and not content[0].isalpha()) or  # Two-char symbols like !=, &&
                content in single_char_entities  # HTML entities for single chars
            )

            # Exclude function keys (F1-F12) and other multi-char names
            if content.startswith('F') and len(content) > 1 and content[1:].isdigit():
                should_be_bold = False

            if should_be_bold:
                # Bold styling for letters, numbers, symbols (use numeric weight and explicit font for PDF compatibility)
                if 'style=' in opening_tag:
                    opening_tag = opening_tag.replace('style="', 'style="font-size: 28px; font-weight: 700; font-family: Helvetica, Arial, sans-serif; ')
                else:
                    opening_tag = f'{opening_tag} style="font-size: 28px; font-weight: 700; font-family: Helvetica, Arial, sans-serif"'
            else:
                # Regular weight and smaller for named keys (Space, Undo, F1-F12, etc.)
                if 'style=' in opening_tag:
                    opening_tag = opening_tag.replace('style="', 'style="font-size: 20px; font-weight: 400; font-family: Helvetica, Arial, sans-serif; ')
                else:
                    opening_tag = f'{opening_tag} style="font-size: 20px; font-weight: 400; font-family: Helvetica, Arial, sans-serif"'

            return f'{opening_tag}{closing_bracket}{content}{closing_tag}'

        # Pattern to match layer label text elements
        label_pattern = re.compile(
            r'(<text\s+[^>]*class="label"[^>]*)(>)([^<]*)(</text>)',
            re.IGNORECASE
        )

        def add_label_inline_style(match: re.Match) -> str:
            opening_tag = match.group(1)
            closing_bracket = match.group(2)
            content = match.group(3)
            closing_tag = match.group(4)

            # Layer labels should be bold with explicit font
            # For SVG: add white stroke outline for visibility
            # For PDF: no stroke (solid black only)
            new_styles = []
            new_styles.append('font-weight: 700')
            new_styles.append('font-family: Helvetica, Arial, sans-serif')

            if not for_pdf:
                # Only add white outline for SVG display
                new_styles.append('stroke: white')
                new_styles.append('stroke-width: 4')
                new_styles.append('paint-order: stroke')
            else:
                # For PDF, no stroke
                new_styles.append('stroke: none')

            if 'style=' in opening_tag:
                # Extract existing style content
                style_match = re.search(r'style="([^"]*)"', opening_tag)
                if style_match:
                    existing_styles = style_match.group(1)
                    # Prepend new styles to existing
                    combined_styles = '; '.join(new_styles) + '; ' + existing_styles
                    opening_tag = re.sub(r'style="[^"]*"', f'style="{combined_styles}"', opening_tag)
            else:
                # No existing style attribute, add new one
                opening_tag = f'{opening_tag} style="{"; ".join(new_styles)}"'

            return f'{opening_tag}{closing_bracket}{content}{closing_tag}'

        # Apply both transformations
        svg_content = tap_pattern.sub(add_tap_inline_style, svg_content)
        svg_content = label_pattern.sub(add_label_inline_style, svg_content)

        return svg_content

    def _combine_svgs_to_pdf(self, output_name: str, svg_files: List[Path]) -> Optional[Path]:
        """Combine multiple SVGs into single multi-page PDF using cairosvg"""

        pdf_path = self.output_dir / f"{output_name}.pdf"

        try:
            import cairosvg
            from PyPDF2 import PdfMerger
            import tempfile
            import os
            import re

            # Convert each SVG to a separate PDF page
            temp_pdfs = []

            for svg_path in svg_files:
                # Read SVG content (styles already applied with for_display=False)
                svg_content = svg_path.read_text()

                # Create temp PDF for this page
                with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as tmp_pdf:
                    temp_pdf_path = tmp_pdf.name

                # Convert SVG to PDF using cairosvg (handles entities properly!)
                cairosvg.svg2pdf(bytestring=svg_content.encode('utf-8'), write_to=temp_pdf_path)
                temp_pdfs.append(temp_pdf_path)

            # Merge all PDFs into one
            merger = PdfMerger()
            for temp_pdf in temp_pdfs:
                merger.append(temp_pdf)

            merger.write(str(pdf_path))
            merger.close()

            # Clean up temp PDFs
            for temp_pdf in temp_pdfs:
                if os.path.exists(temp_pdf):
                    os.unlink(temp_pdf)

            print(f"    📄 {pdf_path.name}")
            return pdf_path
        except Exception as e:
            print(f"  ⚠️  PDF generation failed (SVG output is still available): {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_rowstagger_pdf(self, svg_path: Path, layout_name: str) -> Optional[Path]:
        """Generate landscape PDF for row-stagger keyboard layout"""
        pdf_path = self.output_dir / f"{layout_name}.pdf"

        try:
            import cairosvg

            # Read SVG content and add inline styles for better PDF rendering
            svg_content = svg_path.read_text()

            # Replace "Base:" with the layout name (capitalized, no colon)
            display_name = layout_name.capitalize()
            svg_content = svg_content.replace('>Base:</text>', f'>{display_name}</text>')
            svg_content = svg_content.replace('id="Base"', f'id="{display_name}"')

            svg_content = self._add_inline_styles_for_pdf(svg_content)

            # Convert SVG to PDF using cairosvg
            cairosvg.svg2pdf(bytestring=svg_content.encode('utf-8'), write_to=str(pdf_path))

            print(f"    📄 {pdf_path.name}")
            return pdf_path
        except Exception as e:
            print(f"  ⚠️  PDF generation failed for {layout_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_single_layer_pdf(self, base_name: str, base_layer, layout_size: str) -> Optional[Path]:
        """Generate single-layer landscape PDF showing only the base layer for large printing"""
        # Remove BASE_ prefix and convert to lowercase for output filename
        output_name = base_name.replace('BASE_', '').lower()
        pdf_path = self.output_dir / f"{output_name}_base.pdf"

        try:
            import cairosvg

            # Generate SVG for just the base layer (for PDF, no white outline)
            svg_file = self._generate_svg_for_layers(
                [base_layer],
                layout_size,
                suffix="_base",
                output_name=output_name,
                for_display=False
            )

            # Read SVG content (styles already applied with for_display=False)
            svg_content = svg_file.read_text()

            # Convert SVG to PDF using cairosvg
            cairosvg.svg2pdf(bytestring=svg_content.encode('utf-8'), write_to=str(pdf_path))

            # Clean up intermediate SVG
            if svg_file.exists():
                svg_file.unlink()

            # Clean up JSON file
            json_file = self.output_dir / f"{output_name}_base.json"
            if json_file.exists():
                json_file.unlink()

            print(f"    📄 {pdf_path.name}")
            return pdf_path
        except Exception as e:
            print(f"  ⚠️  Single-layer PDF generation failed for {output_name}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _old_generate_superset_visualizations(self, board_inventory) -> Dict[str, Optional[Path]]:
        """
        OLD VERSION - Generate one visualization per layout_size using keymap.yaml superset

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

                # Skip FUN layer from visualization
                if layer_name == "FUN":
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

            # Generate standalone primary base layer visualization
            # The first BASE_* layer is considered the primary layout
            base_layers = [name for name in keymap_config.layers.keys() if name.startswith("BASE_")]
            if base_layers:
                primary_base = base_layers[0]
                self._generate_primary_base_layer(
                    layout_size,
                    representative_board,
                    primary_base,
                    keymap_config
                )

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
        import shutil

        # Generate full visualization (goes to docs/)
        svg_file = self._generate_svg_for_layers(layout_size, representative_board, superset_layers, suffix="", is_final=True)

        # Copy final SVG to out/visualizations/ for build artifacts
        if svg_file:
            out_svg = self.output_dir / svg_file.name
            shutil.copy2(svg_file, out_svg)

        # Generate split versions for printing (3 layers each) - temporary, for PDF generation
        print_svgs = []
        if len(superset_layers) > 3:
            first_half = superset_layers[:3]
            second_half = superset_layers[3:]

            # Generate print split SVGs (will be deleted after PDF creation)
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

                # Delete the intermediate print split SVGs and JSONs
                for svg in print_svgs:
                    if svg.exists():
                        svg.unlink()
                # Also delete JSON files
                for suffix in ["", "_print1", "_print2"]:
                    json_file = self.output_dir / f"layout_{layout_size}{suffix}.json"
                    if json_file.exists():
                        json_file.unlink()

        return svg_file

    def _old_combine_svgs_to_pdf(self, layout_size: str, svg_files: List[Path]) -> Optional[Path]:
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

    def _old_generate_svg_for_layers(self, layout_size: str, representative_board, layers: List[Dict], suffix: str = "", is_final: bool = False) -> Optional[Path]:
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

            # Get layout-specific config (handles ortho_layout and CSS styling)
            with self._get_layout_specific_config(layout_size) as layout_config:
                # Parse with keymap-drawer (config must come before subcommand)
                parse_cmd = ["keymap", "-c", str(layout_config), "parse", "-q", str(json_file)]

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

                # Draw SVG (config must come before subcommand)
                draw_cmd = ["keymap", "-c", str(layout_config), "draw", "-"]

                draw_result = subprocess.run(
                    draw_cmd,
                    input=parsed_keymap,
                    capture_output=True,
                    text=True,
                    check=True
                )

                svg_output = self._format_layer_labels(
                    draw_result.stdout, layout_size
                )

                # Replace BASE_* layer names with clean names in SVG
                svg_output = svg_output.replace('BASE_COLEMAK', 'COLEMAK')
                svg_output = svg_output.replace('BASE_GALLIUM', 'GALLIUM')
                svg_output = svg_output.replace('BASE_NIGHT', 'NIGHT')
                svg_output = svg_output.replace('BASE_DUSK', 'DUSK')

                # Write SVG file
                svg_file.write_text(svg_output)

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

    def _old_generate_primary_base_layer(self, layout_size: str, representative_board, primary_base: str, keymap_config) -> Optional[Path]:
        """
        Generate standalone visualization for the primary base layer

        Args:
            layout_size: Layout size identifier
            representative_board: Board object for metadata
            primary_base: Name of the primary base layer (first BASE_* layer)
            keymap_config: Parsed keymap configuration

        Returns:
            Path to generated SVG file, or None if generation failed
        """
        import json
        import subprocess
        import yaml
        import tempfile
        import os
        import re

        try:
            # Get the primary base layer
            layer = keymap_config.layers[primary_base]

            # Build keycodes
            keycodes = self._build_superset_layer(layer, layout_size)

            # Translate for display
            translated = [self._translate_keycode_for_display(kc) for kc in keycodes]

            # Reorder for QMK
            reordered = self._reorder_keys_for_qmk(translated, layout_size)

            # Determine keyboard and layout
            if representative_board.firmware == "qmk":
                keyboard = representative_board.qmk_keyboard
            else:
                if layout_size == "3x6_3":
                    keyboard = "crkbd/rev1"
                elif layout_size == "3x5_3":
                    keyboard = "bastardkb/skeletyl/promicro"
                else:
                    keyboard = representative_board.id

            if layout_size == "3x5_3":
                layout = "LAYOUT_split_3x5_3"
            elif layout_size == "3x6_3":
                layout = "LAYOUT_split_3x6_3"
            else:
                layout = "LAYOUT"

            # Create JSON
            keymap_data = {
                "keyboard": keyboard,
                "keymap": "dario",
                "layout": layout,
                "layers": [reordered]
            }

            # Write JSON
            json_file = self.output_dir / f"primary_{layout_size}.json"
            json_file.write_text(json.dumps(keymap_data, indent=2))

            # Generate CSS with just the primary base layer
            css = self._generate_dynamic_css(layout_size, [primary_base])

            # Load config and add CSS
            with open(self.config_file) as f:
                config = yaml.safe_load(f)

            config['draw_config']['svg_extra_style'] = css

            # Update ortho_layout if needed
            if layout_size == "3x6_3":
                config['draw_config']['ortho_layout'] = {
                    'split': True,
                    'rows': 3,
                    'columns': 6,
                    'thumbs': 3
                }

            # Write temp config
            fd, temp_path = tempfile.mkstemp(prefix=f"keymap-primary-{layout_size}-", suffix=".yaml")
            temp_config = Path(temp_path)
            with os.fdopen(fd, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            # Parse
            parse_cmd = ["keymap", "-c", str(temp_config), "parse", "-q", str(json_file)]
            parse_result = subprocess.run(parse_cmd, capture_output=True, text=True, check=True)

            # Rename layer
            clean_name = primary_base.replace('BASE_', '')
            parsed_keymap = parse_result.stdout.replace("L0:", f"{clean_name}:")

            # Draw
            draw_cmd = ["keymap", "-c", str(temp_config), "draw", "-"]
            draw_result = subprocess.run(draw_cmd, input=parsed_keymap, capture_output=True, text=True, check=True)

            svg_output = draw_result.stdout.replace(primary_base, clean_name)

            # Format layer label
            pattern = re.compile(r'(?P<indent>\s*)<text x="[^"]+" y="[^"]+" class="label" id="(?P<id>[^"]+)">[^<]*</text>')

            # Get correct x position based on layout
            label_x = "448" if layout_size == "3x5_3" else "420"
            label_y = "112" if layout_size == "3x5_3" else "133"

            svg_output = pattern.sub(
                f'\\g<indent><text x="{label_x}" y="{label_y}" class="label" id="\\g<id>" text-anchor="middle" dominant-baseline="middle" font-size="28" style="text-anchor: middle; dominant-baseline: middle;">\\g<id></text>',
                svg_output
            )

            # Write SVG to docs/ for embedding
            svg_file = self.docs_dir / f"primary_{layout_size}.svg"
            svg_file.write_text(svg_output)

            # Also copy to out/visualizations/
            import shutil
            out_svg = self.output_dir / svg_file.name
            shutil.copy2(svg_file, out_svg)

            # Generate landscape PDF for printing
            self._generate_primary_pdf(svg_file, layout_size)

            # Clean up
            temp_config.unlink()
            json_file.unlink()  # Clean up JSON file

            print(f"    📄 {svg_file.name} ({clean_name} only)")
            return svg_file

        except Exception as e:
            print(f"  ⚠️  Failed to generate primary base layer: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_primary_pdf(self, svg_file: Path, layout_size: str):
        """Generate landscape PDF for the primary base layer"""
        try:
            from svglib.svglib import svg2rlg
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.graphics import renderPDF

            pdf_file = self.output_dir / f"primary_{layout_size}_landscape.pdf"

            drawing = svg2rlg(str(svg_file))
            if not drawing:
                return

            page_width, page_height = landscape(letter)
            c = canvas.Canvas(str(pdf_file), pagesize=landscape(letter))

            margin = 36
            available_width = page_width - (2 * margin)
            available_height = page_height - (2 * margin)

            scale_x = available_width / drawing.width
            scale_y = available_height / drawing.height
            scale = min(scale_x, scale_y, 1.5)

            scaled_width = drawing.width * scale
            scaled_height = drawing.height * scale
            x = margin + (available_width - scaled_width) / 2
            y = margin + (available_height - scaled_height) / 2

            drawing.scale(scale, scale)
            renderPDF.draw(drawing, c, x, y)
            c.save()

            print(f"    📄 {pdf_file.name}")
        except Exception as e:
            print(f"  ⚠️  Failed to generate primary PDF: {e}")

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

    def generate_rowstagger_visualizations(self) -> None:
        """Generate visualizations for row-stagger keyboard layouts"""
        from config_parser import YAMLConfigParser
        from keylayout_translator import KeylayoutTranslator

        rowstagger_dir = self.config_dir / "rowstagger"
        if not rowstagger_dir.exists():
            return

        yaml_files = list(rowstagger_dir.glob("*.yaml"))
        if not yaml_files:
            return

        print(f"📊 Generating row-stagger visualizations...")
        translator = KeylayoutTranslator()

        for yaml_file in yaml_files:
            try:
                # Parse config
                config = YAMLConfigParser.parse_rowstagger(yaml_file)
                layout_name = yaml_file.stem

                # Write QMK info.json
                info_json_path = self.output_dir / f"{layout_name}_info.json"
                with open(info_json_path, 'w') as f:
                    json.dump(self._build_qmk_info_json(), f, indent=2)

                # Convert to keymap-drawer YAML format
                keymap_yaml = self._rowstagger_to_keymap_yaml(config, translator, info_json_path)

                # Write YAML to output directory
                yaml_path = self.output_dir / f"{layout_name}_rowstagger.yaml"
                with open(yaml_path, 'w') as f:
                    yaml.dump(keymap_yaml, f, default_flow_style=False, sort_keys=False)

                # Generate SVG using keymap-drawer
                svg_path = self.docs_dir / f"{layout_name}_rowstagger.svg"
                with open(svg_path, 'w') as svg_file:
                    result = subprocess.run(
                        ['keymap', 'draw', str(yaml_path)],
                        stdout=svg_file,
                        stderr=subprocess.PIPE,
                        text=True
                    )

                if result.returncode == 0 and svg_path.exists():
                    print(f"  ✅ {layout_name}_rowstagger.svg")

                    # Generate landscape PDF for printing
                    self._generate_rowstagger_pdf(svg_path, layout_name)

                    # Clean up intermediate files
                    if info_json_path.exists():
                        info_json_path.unlink()
                    if yaml_path.exists():
                        yaml_path.unlink()
                else:
                    print(f"  ⚠️  Failed to generate {layout_name}_rowstagger.svg")
                    if result.stderr:
                        print(f"      {result.stderr.strip()}")

            except Exception as e:
                print(f"  ⚠️  Error generating visualization for {yaml_file.name}: {e}")

    def _rowstagger_to_keymap_yaml(self, config, translator, info_json_path: Path) -> Dict:
        """Convert row-stagger config to keymap-drawer YAML format"""
        # Build CSS for fingermap coloring if provided
        fingermap_css = ""
        if config.fingermap:
            finger_colors = {
                0: "#ff9999",  # L-pinky - pink
                1: "#ffbb88",  # L-ring - orange
                2: "#ffee88",  # L-middle - yellow
                3: "#99dd99",  # L-index - green
                4: "#88ccff",  # R-index - blue
                5: "#bb99ff",  # R-middle - purple
                6: "#ffaa88",  # R-ring - coral
                7: "#ff99cc",  # R-pinky - rose
            }

            # Build CSS that targets keys by their index in the layer
            # Layer structure: 14 (number row) + [Tab + 12 alphas + \] + [Caps + 11 alphas + Enter] + [Shift + 10 alphas + Shift] + 8 (space row)
            # Alpha keys start at index 15 (after number row + Tab)
            css_rules = []

            # Top row alphas (keypos 15-26: b through ])
            for i, finger in enumerate(config.fingermap[0]):
                key_idx = 15 + i
                css_rules.append(f".keypos-{key_idx} rect {{ fill: {finger_colors[finger]} !important; }}")

            # Home row alphas (keypos 29-39: n through /)
            for i, finger in enumerate(config.fingermap[1]):
                key_idx = 29 + i
                css_rules.append(f".keypos-{key_idx} rect {{ fill: {finger_colors[finger]} !important; }}")

            # Bottom row alphas (keypos 42-51: v through ,)
            for i, finger in enumerate(config.fingermap[2]):
                key_idx = 42 + i
                css_rules.append(f".keypos-{key_idx} rect {{ fill: {finger_colors[finger]} !important; }}")

            fingermap_css = "\n".join(css_rules)

        return {
            "layout": {
                "qmk_info_json": str(info_json_path)
            },
            "layers": {
                "Base": self._build_flat_layer(config.layout, config.fingermap)
            },
            "draw_config": {
                "key_h": 60,
                "key_w": 60,
                "key_rx": 6,
                "key_ry": 6,
                "n_columns": 1,
                "separate_combo_diagrams": False,
                "combo_w": 24,
                "combo_h": 22,
                "inner_pad_w": 2,
                "inner_pad_h": 2,
                "line_spacing": 1.2,
                "arc_scale": 1.0,
                "append_colon_to_layer_header": True,
                "small_pad": 2,
                "legend_rel_x": 0,
                "legend_rel_y": 0,
                "glyph_tap_size": 28,
                "glyph_hold_size": 20,
                "glyph_shifted_size": 16,
                "svg_extra_style": f"""
                    /* Grey out number row, modifiers, and spacebar by keypos */
                    .keypos-0 rect, .keypos-1 rect, .keypos-2 rect, .keypos-3 rect,
                    .keypos-4 rect, .keypos-5 rect, .keypos-6 rect, .keypos-7 rect,
                    .keypos-8 rect, .keypos-9 rect, .keypos-10 rect, .keypos-11 rect,
                    .keypos-12 rect, .keypos-13 rect,
                    .keypos-14 rect, .keypos-27 rect, .keypos-28 rect, .keypos-40 rect,
                    .keypos-41 rect, .keypos-52 rect,
                    .keypos-53 rect, .keypos-54 rect, .keypos-55 rect, .keypos-56 rect,
                    .keypos-57 rect, .keypos-58 rect, .keypos-59 rect, .keypos-60 rect
                    {{ fill: #999999 !important; }}
                    /* Increase legend size */
                    .tap {{ font-size: 32px; font-weight: 900; }}
                    /* Fingermap colors (per-key targeting) */
                    {fingermap_css}
                """
            }
        }

    def _build_qmk_info_json(self) -> Dict:
        """Build a QMK info.json structure for 60% ANSI layout"""
        layout = []

        # Row 0: Number row (Esc through Backspace)
        for i in range(13):
            layout.append({"x": i, "y": 0})
        layout.append({"x": 13, "y": 0, "w": 2})  # Backspace

        # Row 1: Tab row (Tab, q-], backslash)
        layout.append({"x": 0, "y": 1, "w": 1.5})  # Tab
        for i in range(12):
            layout.append({"x": 1.5 + i, "y": 1})  # q through ]
        layout.append({"x": 13.5, "y": 1, "w": 1.5})  # Backslash

        # Row 2: Caps row (Caps, a-', Enter)
        layout.append({"x": 0, "y": 2, "w": 1.75})  # Caps
        for i in range(11):
            layout.append({"x": 1.75 + i, "y": 2})  # a through '
        layout.append({"x": 12.75, "y": 2, "w": 2.25})  # Enter

        # Row 3: Shift row (Shift, z-/, Shift)
        layout.append({"x": 0, "y": 3, "w": 2.25})  # Left Shift
        for i in range(10):
            layout.append({"x": 2.25 + i, "y": 3})  # z through /
        layout.append({"x": 12.25, "y": 3, "w": 2.75})  # Right Shift

        # Row 4: Bottom row (Ctrl, Win, Alt, Space, Alt, Win, Menu, Ctrl)
        layout.append({"x": 0, "y": 4, "w": 1.25})  # Ctrl
        layout.append({"x": 1.25, "y": 4, "w": 1.25})  # Win
        layout.append({"x": 2.5, "y": 4, "w": 1.25})  # Alt
        layout.append({"x": 3.75, "y": 4, "w": 6.25})  # Space
        layout.append({"x": 10, "y": 4, "w": 1.25})  # Alt
        layout.append({"x": 11.25, "y": 4, "w": 1.25})  # Win
        layout.append({"x": 12.5, "y": 4, "w": 1.25})  # Menu
        layout.append({"x": 13.75, "y": 4, "w": 1.25})  # Ctrl

        return {
            "layouts": {
                "LAYOUT_60_ansi": {
                    "layout": layout
                }
            }
        }

    def _build_flat_layer(self, layout: List[List[str]], fingermap: Optional[List[List[int]]] = None) -> List:
        """Build a flat list of keys for the layer"""
        # Build a simple list of keys
        # Fingermap styling will be handled by generating CSS that targets specific key indices
        return (
            # Number row (14 keys) - all empty (will be grey)
            [""] * 14 +
            # Top row (1.5u Tab + 12 alphas + 1.5u backslash)
            [""] + layout[0] + [""] +
            # Home row (1.75u Caps + 11 alphas + 2.25u Enter)
            [""] + layout[1] + [""] +
            # Bottom row (2.25u Shift + 10 alphas + 2.75u Shift)
            [""] + layout[2] + [""] +
            # Space row (8 keys) - all empty (will be grey)
            [""] * 8
        )
