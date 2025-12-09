"""
ZMK keymap generator

Generates ZMK devicetree (.keymap) files from compiled layers
"""

from typing import List, Dict
from pathlib import Path
from data_model import CompiledLayer, Board, ComboConfiguration, Combo


class ZMKGenerator:
    """Generate ZMK devicetree keymap files"""

    def __init__(self):
        pass

    def generate_keymap(
        self,
        board: Board,
        compiled_layers: List[CompiledLayer],
        combos: ComboConfiguration = None,
        magic_config: 'MagicKeyConfiguration' = None
    ) -> str:
        """
        Generate .keymap devicetree file for ZMK

        Args:
            board: Board configuration
            compiled_layers: List of compiled layers (already translated to ZMK syntax)
            combos: Optional combo configuration
            magic_config: Optional magic key configuration

        Returns:
            Complete .keymap file content as string
        """
        # Generate layer index #defines
        layer_defines = ""
        for idx, layer in enumerate(compiled_layers):
            layer_defines += f"#define {layer.name} {idx}\n"

        # Generate layer definitions
        layer_defs = []
        for layer in compiled_layers:
            layer_def = self._format_layer_definition(layer, board)
            layer_defs.append(layer_def)

        layers_code = "\n\n".join(layer_defs)

        # Generate combo and macro sections
        layer_names = [layer.name for layer in compiled_layers]
        combos_section = ""
        macros_section = ""

        if combos and combos.combos:
            combos_section = "\n" + self.generate_combos_section(combos, layer_names, board)
            macros_section = "\n" + self.generate_macros_section(combos)

        # Generate magic key behaviors section
        behaviors_section = ""
        if magic_config and magic_config.mappings:
            behaviors_section = "\n" + self.generate_magic_keys_section(magic_config, compiled_layers)

        # Generate complete keymap file
        shield_or_board = board.zmk_shield if board.zmk_shield else board.zmk_board
        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml
// Board: {board.name}
// Shield/Board: {shield_or_board}

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
#include <dt-bindings/zmk/bt.h>
#include "dario_behaviors.dtsi"

{layer_defines}
/ {{
{combos_section}
{macros_section}{behaviors_section}
    keymap {{
        compatible = "zmk,keymap";

{layers_code}
    }};
}};
"""

    def _format_layer_definition(self, layer: CompiledLayer, board: Board) -> str:
        """
        Format a single layer as ZMK devicetree node

        Args:
            layer: Compiled layer with ZMK keycodes
            board: Board configuration (for layout size)

        Returns:
            Layer definition as string
        """
        layer_name = layer.name.lower()
        bindings = self._format_bindings(layer.keycodes, board.layout_size)

        return f"""        {layer_name}_layer {{
            bindings = <
{bindings}
            >;
        }};"""

    def _format_bindings(self, keycodes: List[str], layout_size: str = "3x5_3") -> str:
        """
        Format keycodes as ZMK bindings with proper indentation

        Args:
            keycodes: List of ZMK keycodes (e.g., "&kp A", "&hml LGUI A")
            layout_size: Board layout size (e.g., "3x5_3", "3x6_3")

        Returns:
            Formatted bindings string
        """
        # Format for Corne's physical layout (6 columns per row, 3 rows + 3 thumb keys)
        if layout_size == "3x6_3" and len(keycodes) == 42:
            # 3x6_3 layout: 6 columns, 3 rows per hand + 3 thumbs per hand
            # Format as: left6 right6 | left6 right6 | left6 right6 | left3 right3
            rows = [
                keycodes[0:6] + keycodes[18:24],    # Row 1: left 6 + right 6
                keycodes[6:12] + keycodes[24:30],   # Row 2: left 6 + right 6
                keycodes[12:18] + keycodes[30:36],  # Row 3: left 6 + right 6
                keycodes[36:39] + keycodes[39:42],  # Thumbs: left 3 + right 3
            ]
        elif layout_size == "3x5_3" and len(keycodes) == 36:
            # 3x5_3 layout: 5 columns, 3 rows per hand + 3 thumbs per hand
            rows = [
                keycodes[0:5] + keycodes[15:20],    # Row 1: left 5 + right 5
                keycodes[5:10] + keycodes[20:25],   # Row 2: left 5 + right 5
                keycodes[10:15] + keycodes[25:30],  # Row 3: left 5 + right 5
                keycodes[30:33] + keycodes[33:36],  # Thumbs: left 3 + right 3
            ]
        else:
            # Generic fallback: chunk into rows of 12 (or 10 for 3x5_3)
            chunk_size = 12 if layout_size == "3x6_3" else 10
            rows = []
            for i in range(0, len(keycodes), chunk_size):
                rows.append(keycodes[i:i+chunk_size])

        # Format with proper indentation (simple space separation)
        formatted_rows = []
        for row in rows:
            formatted_row = " " * 16 + " ".join(row)
            formatted_rows.append(formatted_row)

        return "\n".join(formatted_rows)

    def generate_visualization(self, board: Board, compiled_layers: List[CompiledLayer]) -> str:
        """
        Generate ASCII art visualization of keymap

        Args:
            board: Board configuration
            compiled_layers: List of compiled layers

        Returns:
            ASCII art as string (for README or comments)
        """
        lines = []
        lines.append(f"# Keymap Visualization: {board.name}")
        lines.append("")

        for layer in compiled_layers:
            lines.append(f"## {layer.name} Layer")
            lines.append("")

            # For 36-key layout
            if len(layer.keycodes) == 36:
                lines.append("```")
                lines.append("Left Hand              Right Hand")
                lines.append("╭─────────────────╮    ╭─────────────────╮")

                # Row 1
                left_r1 = layer.keycodes[0:5]
                right_r1 = layer.keycodes[15:20]
                lines.append(f"│ {' '.join(f'{self._simplify_keycode(k):4}' for k in left_r1)} │    │ {' '.join(f'{self._simplify_keycode(k):4}' for k in right_r1)} │")

                # Row 2
                left_r2 = layer.keycodes[5:10]
                right_r2 = layer.keycodes[20:25]
                lines.append(f"│ {' '.join(f'{self._simplify_keycode(k):4}' for k in left_r2)} │    │ {' '.join(f'{self._simplify_keycode(k):4}' for k in right_r2)} │")

                # Row 3
                left_r3 = layer.keycodes[10:15]
                right_r3 = layer.keycodes[25:30]
                lines.append(f"│ {' '.join(f'{self._simplify_keycode(k):4}' for k in left_r3)} │    │ {' '.join(f'{self._simplify_keycode(k):4}' for k in right_r3)} │")

                lines.append("╰─────────────────╯    ╰─────────────────╯")

                # Thumbs
                left_thumbs = layer.keycodes[30:33]
                right_thumbs = layer.keycodes[33:36]
                lines.append(f"      {' '.join(f'{self._simplify_keycode(k):4}' for k in left_thumbs)}              {' '.join(f'{self._simplify_keycode(k):4}' for k in right_thumbs)}")
                lines.append("```")
            else:
                # Generic layout
                lines.append("```")
                for i, kc in enumerate(layer.keycodes):
                    if i % 6 == 0 and i > 0:
                        lines.append("")
                    lines.append(f"{i:2d}: {kc}")
                lines.append("```")

            lines.append("")

        return "\n".join(lines)

    def _simplify_keycode(self, zmk_keycode: str) -> str:
        """
        Simplify ZMK keycode for visualization

        Args:
            zmk_keycode: Full ZMK keycode (e.g., "&kp A", "&hrm LGUI A")

        Returns:
            Simplified string for display
        """
        # Remove & prefix
        kc = zmk_keycode.lstrip('&')

        # Handle simple keycodes
        if kc.startswith('kp '):
            return kc[3:]  # Remove "kp "

        # Handle behaviors - just show behavior name
        if ' ' in kc:
            behavior, *params = kc.split()
            if behavior == 'hrm':
                # hrm LGUI A -> A/GUI
                return f"{params[1]}/{params[0][1:]}"  # A/GUI
            elif behavior == 'lt':
                # lt NAV SPC -> SPC/NAV
                return f"{params[1]}/{params[0]}"
            elif behavior == 'bt':
                # bt BT_NXT -> BT→
                action_map = {
                    'BT_NXT': 'BT→',
                    'BT_PRV': 'BT←',
                    'BT_CLR': 'BT×'
                }
                return action_map.get(params[0], 'BT')
            else:
                return behavior.upper()

        # None/transparent
        if kc == 'none':
            return '___'
        if kc == 'trans':
            return '▽▽▽'

        return kc.upper()[:4]

    def translate_combo_positions(self, canonical_positions: List[int], board: Board) -> List[int]:
        """
        Translate combo positions from canonical 36-key layout to board's physical layout

        Args:
            canonical_positions: Positions in canonical 3x5_3 (36-key) layout
            board: Board configuration with layout_size

        Returns:
            Translated positions for the board's physical layout
        """
        # For 3x5_3 boards, no translation needed
        if board.layout_size == "3x5_3":
            return canonical_positions

        # For 3x6_3 boards with outer columns, add offset for each row
        # Canonical 3x5_3: rows of 10 keys (0-9, 10-19, 20-29) + 6 thumbs (30-35)
        # Physical 3x6_3: rows of 12 keys (0-11, 12-23, 24-35) + 6 thumbs (36-41)
        if board.layout_size == "3x6_3":
            translated = []
            for pos in canonical_positions:
                if pos < 30:  # Alpha keys (rows 0-2)
                    row = pos // 10
                    col = pos % 10
                    # Add 1 for outer column, plus row offset
                    new_pos = row * 12 + col + 1
                else:  # Thumb keys (row 3)
                    # Thumbs start at position 36 on 3x6_3
                    new_pos = pos - 30 + 36
                translated.append(new_pos)
            return translated

        # For other layouts, return as-is (TODO: add support for more layouts)
        return canonical_positions

    def generate_combos_section(self, combos: ComboConfiguration, layer_names: List[str], board: Board) -> str:
        """
        Generate ZMK combos devicetree section

        Args:
            combos: ComboConfiguration with all combos
            layer_names: List of layer names for layer index lookup
            board: Board configuration for position translation

        Returns:
            Combos section as devicetree code (empty string if no combos)
        """
        if not combos.combos:
            return ""

        # Generate combo definitions
        combo_defs = []
        for combo in combos.combos:
            # Translate positions from canonical 36-key layout to board layout
            translated_positions = self.translate_combo_positions(combo.key_positions, board)

            # Convert positions to ZMK format (space-separated integers in angle brackets)
            positions_str = " ".join(str(pos) for pos in translated_positions)

            # Convert layer names to indices
            layer_indices = []
            if combo.layers:
                for layer_name in combo.layers:
                    if layer_name in layer_names:
                        idx = layer_names.index(layer_name)
                        layer_indices.append(str(idx))

            layers_str = " ".join(layer_indices) if layer_indices else ""

            # Generate binding - always use direct binding (no hold-tap)
            if combo.macro_text is not None:
                # This is a text expansion macro
                binding = f"&{combo.name.lower()}"
            elif combo.action == "DFU":
                binding = "&bootloader"
            else:
                binding = f"&kp {combo.action}"

            # Build combo definition
            combo_def = f"""        combo_{combo.name} {{
            timeout-ms = <{combo.timeout_ms}>;
            key-positions = <{positions_str}>;
            bindings = <{binding}>;"""

            # Add layers if specified
            if layers_str:
                combo_def += f"\n            layers = <{layers_str}>;"

            # Add require-prior-idle-ms if specified
            if combo.require_prior_idle_ms:
                combo_def += f"\n            require-prior-idle-ms = <{combo.require_prior_idle_ms}>;"

            # Add slow_release if specified
            if combo.slow_release:
                combo_def += f"\n            slow-release;"

            combo_def += "\n        };"

            combo_defs.append(combo_def)

        combos_code = "\n\n".join(combo_defs)

        return f"""    combos {{
        compatible = "zmk,combos";

{combos_code}
    }};"""

    def generate_macros_section(self, combos: ComboConfiguration) -> str:
        """
        Generate ZMK behaviors section for hold combos

        Args:
            combos: ComboConfiguration with all combos

        Returns:
            Behaviors section as devicetree code (empty string - deprecated)

        NOTE: This method is deprecated. Hold combos are no longer supported.
        Use standard instant combos with require-prior-idle-ms instead.
        """
        # No longer generating hold-tap behaviors for combos
        # Combos now use direct bindings (instant trigger)
        return ""

    def generate_macro_behaviors(self, combos: ComboConfiguration) -> str:
        """
        Generate ZMK macro behaviors for text expansion

        Returns:
            Devicetree macros section
        """
        if not combos or not combos.combos:
            return ""

        macro_combos = [c for c in combos.combos if c.macro_text is not None]
        if not macro_combos:
            return ""

        macro_defs = []
        for combo in macro_combos:
            macro_name = combo.name.lower()

            # Convert text to sequence of &kp keypresses
            key_sequence = []
            for char in combo.macro_text:
                zmk_key = self.char_to_zmk_keycode(char)
                key_sequence.append(f"&kp {zmk_key}")

            # Group into lines for readability (10 keys per line)
            lines = []
            for i in range(0, len(key_sequence), 10):
                chunk = key_sequence[i:i+10]
                lines.append("                , <&macro_tap " + " ".join(chunk) + ">")

            bindings_code = "\n".join(lines)

            macro_def = f"""        {macro_name}: {macro_name}_macro {{
            compatible = "zmk,behavior-macro";
            label = "{macro_name.upper()}";
            #binding-cells = <0>;
            bindings
{bindings_code}
                ;
        }};"""

            macro_defs.append(macro_def)

        return f"""
/ {{
    macros {{
{chr(10).join(macro_defs)}
    }};
}};
"""

    def generate_magic_keys_section(
        self,
        magic_config: 'MagicKeyConfiguration',
        compiled_layers: List[CompiledLayer]
    ) -> str:
        """
        Generate ZMK adaptive key behaviors for magic keys

        Uses zmk-adaptive-key module (urob/zmk-adaptive-key).
        Generates separate adaptive key behaviors for each base layer:
        - ak_night (for BASE_NIGHT family)
        - ak_gallium (for BASE_GALLIUM family)

        Args:
            magic_config: MagicKeyConfiguration with base-layer mappings
            compiled_layers: List of CompiledLayer for validation

        Returns:
            ZMK devicetree behaviors section
        """
        if not magic_config or not magic_config.mappings:
            return ""

        code_lines = [
            "    // Magic key behaviors (adaptive key)",
            "    // Each base layer has its own adaptive key with layer-specific mappings",
            "    behaviors {",
        ]

        # Generate adaptive key behavior for each base layer
        for base_layer, mapping in magic_config.mappings.items():
            # Behavior name: BASE_NIGHT → ak_night, BASE_GALLIUM → ak_gallium
            behavior_suffix = base_layer.lower().replace("base_", "")
            behavior_name = f"ak_{behavior_suffix}"

            code_lines.append(f"        // Adaptive key for {base_layer} family")
            code_lines.append(f"        {behavior_name}: {behavior_name} {{")
            code_lines.append(f"            compatible = \"zmk,behavior-adaptive-key\";")
            code_lines.append(f"            #binding-cells = <0>;")

            # Default behavior
            if mapping.default == "REPEAT":
                code_lines.append(f"            bindings = <&key_repeat>;")
            elif mapping.default == "NONE":
                code_lines.append(f"            bindings = <&none>;")
            else:
                default_zmk = self._translate_simple_keycode(mapping.default)
                code_lines.append(f"            bindings = <{default_zmk}>;")

            code_lines.append("")

            # Generate trigger for each mapping
            for prev_key, alt_key in mapping.mappings.items():
                prev_zmk_raw = self._translate_simple_keycode(prev_key)
                alt_zmk = self._translate_simple_keycode(alt_key)

                # Extract keycode from &kp syntax for trigger-keys
                # "&kp U" → "U", "&kp DOT" → "DOT"
                prev_keycode = prev_zmk_raw.replace("&kp ", "")

                # Generate safe trigger name
                trigger_name = prev_key.replace('.', 'dot').replace('/', 'slash').replace("'", 'quot').lower() + "_trigger"

                code_lines.append(f"            {trigger_name} {{")
                code_lines.append(f"                trigger-keys = <{prev_keycode}>;")
                code_lines.append(f"                bindings = <{alt_zmk}>;")
                # If timeout_ms is 0, omit the property to allow unlimited timing
                if mapping.timeout_ms > 0:
                    code_lines.append(f"                max-prior-idle-ms = <{mapping.timeout_ms}>;")
                code_lines.append(f"            }};")

            code_lines.append(f"        }};")
            code_lines.append("")

            # Layer-tap helper so MAGIC can be used as the tap side of a layer-tap
            code_lines.append(f"        lt_ak_{behavior_suffix}: lt_ak_{behavior_suffix} {{")
            code_lines.append(f"            compatible = \"zmk,behavior-hold-tap\";")
            code_lines.append(f"            label = \"LT_AK_{behavior_suffix.upper()}\";")
            code_lines.append(f"            #binding-cells = <2>;")
            code_lines.append(f"            flavor = \"balanced\";")
            code_lines.append(f"            tapping-term-ms = <200>;")
            code_lines.append(f"            quick-tap-ms = <200>;")
            code_lines.append(f"            bindings = <&mo>, <&ak_{behavior_suffix}>;")
            code_lines.append(f"        }};")
            code_lines.append("")

        code_lines.append("    };")
        code_lines.append("")

        return "\n".join(code_lines)

    def _translate_simple_keycode(self, keycode: str) -> str:
        """
        Translate simple keycode to ZMK format (for magic key mappings)

        Args:
            keycode: Simple keycode (e.g., "A", ".", "/")

        Returns:
            ZMK keycode (e.g., "&kp A", "&kp DOT", "&kp SLASH")
        """
        # Strip QMK-style KC_ prefix if present for compatibility with magic defaults
        if keycode.startswith("KC_"):
            keycode = keycode[3:]

        # Handle special characters
        special_chars = {
            ".": "DOT",
            ",": "COMMA",
            "/": "SLASH",
            "'": "SQT",
            "-": "MINUS",
            ";": "SEMI",
            "[": "LBKT",
            "]": "RBKT",
        }

        if keycode in special_chars:
            return f"&kp {special_chars[keycode]}"

        # Single letter
        if len(keycode) == 1 and keycode.isalpha():
            return f"&kp {keycode.upper()}"

        # Already prefixed
        if keycode.startswith("&kp "):
            return keycode

        # Default: add &kp prefix
        return f"&kp {keycode}"

    def char_to_zmk_keycode(self, char: str) -> str:
        """Convert character to ZMK keycode"""
        # Mapping of characters to ZMK keycodes
        char_map = {
            'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E',
            'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J',
            'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O',
            'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T',
            'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z',
            '0': 'N0', '1': 'N1', '2': 'N2', '3': 'N3', '4': 'N4',
            '5': 'N5', '6': 'N6', '7': 'N7', '8': 'N8', '9': 'N9',
            '/': 'FSLH', '-': 'MINUS', '.': 'DOT', ':': 'COLON',
            '?': 'QMARK', '=': 'EQUAL', '#': 'HASH', '_': 'UNDER',
            ' ': 'SPACE'
        }

        return char_map.get(char, char.upper())
