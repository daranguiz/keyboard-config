"""
ZMK keymap generator

Generates ZMK devicetree (.keymap) files from compiled layers
"""

from typing import List, Dict, Tuple
import re
from pathlib import Path
from data_model import CompiledLayer, Board, ComboConfiguration, Combo, ValidationError


class ZMKGenerator:
    """Generate ZMK devicetree keymap files"""

    def __init__(self, magic_training: bool = False, special_keycodes: Dict[str, Dict[str, str]] = None,
                 behaviors_dtsi_path: str = None):
        self.magic_training = magic_training
        self.special_keycodes = special_keycodes or {}
        self.char_token_map = self._build_char_token_map()
        # Track macro behaviors generated for magic/combos so bindings can reference them
        self.generated_macros: Dict[str, str] = {}
        # Parse behavior timings from dario_behaviors.dtsi
        self.behavior_timings = self._parse_behaviors_dtsi(behaviors_dtsi_path) if behaviors_dtsi_path else {}

    def _parse_behaviors_dtsi(self, dtsi_path: str) -> Dict[str, Dict[str, any]]:
        """
        Parse dario_behaviors.dtsi to extract timing values for hold-tap behaviors.

        Returns dict like:
        {
            'lt': {'tapping_term_ms': 200, 'quick_tap_ms': 200, 'flavor': 'balanced'},
            'mt': {'tapping_term_ms': 200, 'quick_tap_ms': 200, 'flavor': 'hold-preferred'},
            'hml': {'require_prior_idle_ms': 150, 'tapping_term_ms': 280, 'quick_tap_ms': 200, 'flavor': 'balanced',
                    'hold_trigger_key_positions': '6 7 8 9 10 11 18 19 20 21 22 23 30 31 32 33 34 35 39 40 41'},
            'hmr': {...}
        }
        """
        try:
            with open(dtsi_path, 'r') as f:
                content = f.read()
        except (FileNotFoundError, IOError) as e:
            print(f"Warning: Could not read behaviors dtsi file {dtsi_path}: {e}")
            return {}

        timings = {}

        # Parse &lt and &mt overrides (global behavior overrides)
        for behavior in ['lt', 'mt']:
            pattern = rf'&{behavior}\s*\{{\s*([^}}]+)\}}'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                timings[behavior] = self._parse_behavior_block(match.group(1))

        # Parse named behaviors (hml, hmr, etc.)
        # Pattern: name: label { ... }
        named_pattern = r'(\w+):\s*\w+\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        for match in re.finditer(named_pattern, content, re.DOTALL):
            name = match.group(1)
            if name in ['hml', 'hmr']:
                timings[name] = self._parse_behavior_block(match.group(2))

        return timings

    def _parse_behavior_block(self, block: str) -> Dict[str, any]:
        """
        Parse a behavior block to dynamically extract all properties.

        Returns dict with original dtsi property names as keys, preserving
        the exact format needed for output (numeric in angle brackets,
        strings in quotes, booleans as standalone semicolons).
        """
        props = {}

        # Match numeric properties: property-name = <value>;
        for match in re.finditer(r'([\w-]+)\s*=\s*<([^>]+)>', block):
            prop_name = match.group(1)
            value = match.group(2).strip()
            # Try to parse as int, otherwise keep as string (for space-separated lists)
            try:
                props[prop_name] = ('numeric', int(value))
            except ValueError:
                props[prop_name] = ('numeric_list', value)

        # Match string properties: property-name = "value";
        for match in re.finditer(r'([\w-]+)\s*=\s*"([^"]+)"', block):
            prop_name = match.group(1)
            value = match.group(2)
            props[prop_name] = ('string', value)

        # Match boolean properties (standalone): property-name;
        # Must be careful to not match properties with values
        for match in re.finditer(r'\b([\w-]+)\s*;', block):
            prop_name = match.group(1)
            # Only add if not already captured as a property with value
            if prop_name not in props:
                # Skip common non-property tokens
                if prop_name not in ['compatible', 'label', 'bindings']:
                    props[prop_name] = ('boolean', True)

        return props

    def _emit_behavior_properties(self, behavior: str, indent: str = "            ",
                                   exclude: List[str] = None) -> List[str]:
        """
        Emit all properties for a behavior as dtsi code lines.

        Args:
            behavior: The behavior name (e.g., 'lt', 'mt', 'hml')
            indent: Indentation string for each line
            exclude: List of property names to skip (e.g., 'bindings' which is set separately)

        Returns:
            List of dtsi code lines with properties
        """
        exclude = exclude or []
        lines = []

        if behavior not in self.behavior_timings:
            return lines

        for prop_name, (prop_type, value) in self.behavior_timings[behavior].items():
            if prop_name in exclude:
                continue

            if prop_type == 'numeric':
                lines.append(f"{indent}{prop_name} = <{value}>;")
            elif prop_type == 'numeric_list':
                lines.append(f"{indent}{prop_name} = <{value}>;")
            elif prop_type == 'string':
                lines.append(f"{indent}{prop_name} = \"{value}\";")
            elif prop_type == 'boolean':
                lines.append(f"{indent}{prop_name};")

        return lines

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

        # Generate combo and macro sections
        layer_names = [layer.name for layer in compiled_layers]
        combos_section = ""
        macros_section = ""
        macro_refs: Dict[Tuple[str, str], str] = {}

        # Collect macros for combos and magic expansions (text outputs)
        macro_defs: List[str] = []
        if combos and combos.combos:
            combos_section = "\n" + self.generate_combos_section(combos, layer_names, board)

        if magic_config and magic_config.mappings:
            magic_macro_defs, macro_refs = self._collect_magic_macros(magic_config)
            macro_defs.extend(magic_macro_defs)

        if macro_defs:
            macros_section = "\n" + self._wrap_macros_section(macro_defs)

        # Generate magic key behaviors section
        behaviors_section = ""
        training_replacements: Dict[str, Dict[str, str]] = {}
        if magic_config and magic_config.mappings:
            behaviors_section = "\n" + self.generate_magic_keys_section(magic_config, compiled_layers, macro_refs)
            if self.magic_training:
                training_behaviors, training_replacements = self.generate_magic_training_section(
                    magic_config, compiled_layers, macro_refs
                )
                if training_behaviors:
                    behaviors_section += "\n" + training_behaviors

        # Generate layer definitions (with optional training replacements)
        layer_defs = []
        for layer in compiled_layers:
            layer_def = self._format_layer_definition(layer, board, training_replacements, magic_config)
            layer_defs.append(layer_def)

        layers_code = "\n\n".join(layer_defs)

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

    def _format_layer_definition(
        self,
        layer: CompiledLayer,
        board: Board,
        training_replacements: Dict[str, Dict[str, str]],
        magic_config: 'MagicKeyConfiguration'
    ) -> str:
        """
        Format a single layer as ZMK devicetree node

        Args:
            layer: Compiled layer with ZMK keycodes
            board: Board configuration (for layout size)

        Returns:
            Layer definition as string
        """
        layer_name = layer.name.lower()

        # Apply training replacements if applicable to this layer's base family
        keycodes = layer.keycodes
        if training_replacements and magic_config:
            # Determine base mapping for this layer
            mapping = magic_config.get_mapping_for_layer(layer.name) if hasattr(magic_config, "get_mapping_for_layer") else None
            if mapping:
                base_layer = mapping.base_layer
                if base_layer in training_replacements:
                    replacement_map = training_replacements[base_layer]
                    keycodes = [replacement_map.get(kc, kc) for kc in keycodes]

        bindings = self._format_bindings(keycodes, board.layout_size)

        return f"""        {layer_name}_layer {{
            bindings = <
{bindings}
            >;
        }};"""

    def _format_bindings(self, keycodes: List[str], layout_size: str = "3x5_3") -> str:
        """
        Format keycodes as ZMK bindings with proper indentation

        Args:
            keycodes: List of ZMK keycodes in row-wise order:
                      - 3x5_3: [0-9]=row1, [10-19]=row2, [20-29]=row3, [30-35]=thumbs
                      - 3x6_3: [0-11]=row1, [12-23]=row2, [24-35]=row3, [36-41]=thumbs
            layout_size: Board layout size (e.g., "3x5_3", "3x6_3")

        Returns:
            Formatted bindings string
        """
        # Input is row-wise from layer compiler:
        # 3x5_3: [left5 right5] per row, then [left3 right3] thumbs
        # 3x6_3: [pinky left5 right5 pinky] per row, then [left3 right3] thumbs
        if layout_size == "3x6_3" and len(keycodes) == 42:
            # 3x6_3 layout: 12 keys per row (pinky + 5 left + 5 right + pinky)
            # Input is already row-wise: [0-11]=row1, [12-23]=row2, [24-35]=row3, [36-41]=thumbs
            rows = [
                keycodes[0:12],     # Row 1: all 12 keys
                keycodes[12:24],    # Row 2: all 12 keys
                keycodes[24:36],    # Row 3: all 12 keys
                keycodes[36:42],    # Thumbs: all 6 keys
            ]
        elif layout_size == "3x5_3" and len(keycodes) == 36:
            # 3x5_3 layout: 10 keys per row (5 left + 5 right)
            # Input is row-wise: [0-9]=row1, [10-19]=row2, [20-29]=row3, [30-35]=thumbs
            rows = [
                keycodes[0:10],     # Row 1: left 5 + right 5
                keycodes[10:20],    # Row 2: left 5 + right 5
                keycodes[20:30],    # Row 3: left 5 + right 5
                keycodes[30:36],    # Thumbs: left 3 + right 3
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

            # For 36-key layout (row-wise ordering)
            # [0-9]=row1, [10-19]=row2, [20-29]=row3, [30-35]=thumbs
            if len(layer.keycodes) == 36:
                lines.append("```")
                lines.append("Left Hand              Right Hand")
                lines.append("╭─────────────────╮    ╭─────────────────╮")

                # Row 1: positions 0-4 (left) and 5-9 (right)
                left_r1 = layer.keycodes[0:5]
                right_r1 = layer.keycodes[5:10]
                lines.append(f"│ {' '.join(f'{self._simplify_keycode(k):4}' for k in left_r1)} │    │ {' '.join(f'{self._simplify_keycode(k):4}' for k in right_r1)} │")

                # Row 2: positions 10-14 (left) and 15-19 (right)
                left_r2 = layer.keycodes[10:15]
                right_r2 = layer.keycodes[15:20]
                lines.append(f"│ {' '.join(f'{self._simplify_keycode(k):4}' for k in left_r2)} │    │ {' '.join(f'{self._simplify_keycode(k):4}' for k in right_r2)} │")

                # Row 3: positions 20-24 (left) and 25-29 (right)
                left_r3 = layer.keycodes[20:25]
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
        Translate combo positions from canonical row-wise 36-key layout to board's physical layout.

        Canonical row-wise positions (36-key):
          0-9:   top row (0-4 left, 5-9 right)
          10-19: home row (10-14 left, 15-19 right)
          20-29: bottom row (20-24 left, 25-29 right)
          30-35: thumbs (30-32 left, 33-35 right)

        Args:
            canonical_positions: Positions in canonical row-wise 36-key layout
            board: Board configuration with layout_size

        Returns:
            Translated positions for the board's physical ZMK layout
        """
        # For 3x5_3 boards, direct 1:1 mapping (row-wise in = row-wise out)
        if board.layout_size == "3x5_3":
            return canonical_positions

        # For 3x6_3 boards: map row-wise 36-key → row-wise 42-key with pinky columns
        # Output: rows of 12 keys (0-11, 12-23, 24-35) + 6 thumbs (36-41)
        # Each row: [pinky, left0-4, right0-4, pinky]
        if board.layout_size == "3x6_3":
            translated = []
            for pos in canonical_positions:
                if pos < 30:  # Alpha keys (rows 0-2)
                    row = pos // 10
                    col = pos % 10
                    # Add 1 for left pinky column offset
                    new_pos = row * 12 + col + 1
                else:  # Thumb keys (30-35 → 36-41)
                    new_pos = pos - 30 + 36
                translated.append(new_pos)
            return translated

        # For other layouts, return as-is
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

    def _wrap_macros_section(self, macro_defs: List[str]) -> str:
        """
        Wrap a list of macro behavior definitions in a macros node.
        """
        return f"""    macros {{
{chr(10).join(macro_defs)}
    }};
"""

    def _build_macro_definition(self, name: str, sequence: List[str]) -> str:
        """
        Build a single macro behavior definition using a safe tap timing so longer
        text expansions don't drop characters.
        """
        # Convert sequence of characters into &kp keypresses
        key_sequence = []
        for ch in sequence:
            zmk_key = self.char_to_zmk_keycode(ch)
            key_sequence.append(f"&kp {zmk_key}")

        # Group into lines for readability (10 keys per line)
        lines = [
            f"        {name}: {name}_macro {{",
            f"            compatible = \"zmk,behavior-macro\";",
            f"            label = \"{name.upper()}\";",
            f"            #binding-cells = <0>;",
            f"            bindings",
            f"                = <&macro_wait_time 10>",
            f"                , <&macro_tap_time 10>",
        ]

        for i in range(0, len(key_sequence), 10):
            chunk = key_sequence[i:i+10]
            lines.append("                , <&macro_tap " + " ".join(chunk) + ">")

        lines.append("                ;")
        lines.append("        };")

        return "\n".join(lines)

    def _collect_combo_macros(self, combos: ComboConfiguration) -> List[str]:
        """
        Collect macro definitions for combo text expansions.
        """
        macro_defs: List[str] = []
        if not combos or not combos.combos:
            return macro_defs

        for combo in combos.combos:
            if combo.macro_text is None:
                continue
            macro_name = combo.name.lower()
            if macro_name in self.generated_macros:
                continue
            macro_def = self._build_macro_definition(macro_name, list(combo.macro_text))
            self.generated_macros[macro_name] = macro_def
            macro_defs.append(macro_def)

        return macro_defs

    def _extract_macro_sequence(self, keycode) -> List[str]:
        """
        Determine if a keycode represents a text sequence; return list of chars if so.
        """
        if isinstance(keycode, dict) and 'text' in keycode and isinstance(keycode['text'], str):
            return list(keycode['text'])
        if isinstance(keycode, list):
            return [str(ch) for ch in keycode]
        if isinstance(keycode, str) and len(keycode) > 1:
            return list(keycode)
        return []

    def _collect_magic_macros(self, magic_config: 'MagicKeyConfiguration') -> Tuple[List[str], Dict[Tuple[str, str], str]]:
        """
        Collect macro definitions for magic key text expansions and return macro references.
        """
        macro_defs: List[str] = []
        macro_refs: Dict[Tuple[str, str], str] = {}

        if not magic_config or not magic_config.mappings:
            return macro_defs, macro_refs

        for base_layer, mapping in magic_config.mappings.items():
            behavior_suffix = base_layer.lower().replace("base_", "")
            for prev_key, alt_key in mapping.mappings.items():
                sequence = self._extract_macro_sequence(alt_key)
                if not sequence:
                    continue

                safe_prev = self._sanitize_token(prev_key)
                if safe_prev == "key":
                    safe_prev = "chr_" + "_".join(str(ord(c)) for c in str(prev_key))
                macro_name = f"magic_{behavior_suffix}_{safe_prev}"
                macro_refs[(base_layer, str(prev_key))] = macro_name

                if macro_name in self.generated_macros:
                    continue

                macro_def = self._build_macro_definition(macro_name, sequence)
                self.generated_macros[macro_name] = macro_def
                macro_defs.append(macro_def)

        return macro_defs, macro_refs

    def generate_magic_keys_section(
        self,
        magic_config: 'MagicKeyConfiguration',
        compiled_layers: List[CompiledLayer],
        macro_refs: Dict[Tuple[str, str], str] = None
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

        macro_refs = macro_refs or {}

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

                macro_name = macro_refs.get((base_layer, str(prev_key)))
                if macro_name:
                    alt_zmk = f"&{macro_name}"
                else:
                    alt_zmk = self._translate_simple_keycode(alt_key)

                # Extract keycode from &kp syntax for trigger-keys
                # "&kp U" → "U", "&kp DOT" → "DOT", "&macro_tap &kp E &kp N" → "E"
                prev_keycode = prev_zmk_raw.replace("&kp ", "").split()[0]

                # Generate safe trigger name
                trigger_name = f"{self._sanitize_token(prev_zmk_raw)}_trigger"

                code_lines.append(f"            {trigger_name} {{")
                code_lines.append(f"                trigger-keys = <{prev_keycode}>;")
                code_lines.append(f"                bindings = <{alt_zmk}>;")
                # If timeout_ms is 0, omit the property to allow unlimited timing
                if mapping.timeout_ms > 0:
                    code_lines.append(f"                max-prior-idle-ms = <{mapping.timeout_ms}>;")
                code_lines.append(f"            }};")

            code_lines.append(f"        }};")
            code_lines.append("")

            # Properties to exclude (set explicitly in generated code)
            exclude_props = ['compatible', 'label', 'binding-cells', 'bindings']

            # Layer-tap helper so MAGIC can be used as the tap side of a layer-tap
            # All properties dynamically sourced from &lt in dario_behaviors.dtsi
            code_lines.append(f"        lt_ak_{behavior_suffix}: lt_ak_{behavior_suffix} {{")
            code_lines.append(f"            compatible = \"zmk,behavior-hold-tap\";")
            code_lines.append(f"            label = \"LT_AK_{behavior_suffix.upper()}\";")
            code_lines.append(f"            #binding-cells = <2>;")
            code_lines.extend(self._emit_behavior_properties('lt', exclude=exclude_props))
            code_lines.append(f"            bindings = <&mo>, <&ak_{behavior_suffix}>;")
            code_lines.append(f"        }};")
            code_lines.append("")

            # Mod-tap helper so MAGIC can be used as the tap side of a mod-tap
            # All properties dynamically sourced from &mt in dario_behaviors.dtsi
            code_lines.append(f"        mt_ak_{behavior_suffix}: mt_ak_{behavior_suffix} {{")
            code_lines.append(f"            compatible = \"zmk,behavior-hold-tap\";")
            code_lines.append(f"            label = \"MT_AK_{behavior_suffix.upper()}\";")
            code_lines.append(f"            #binding-cells = <2>;")
            code_lines.extend(self._emit_behavior_properties('mt', exclude=exclude_props))
            code_lines.append(f"            bindings = <&kp>, <&ak_{behavior_suffix}>;")
            code_lines.append(f"        }};")
            code_lines.append("")

        code_lines.append("    };")
        code_lines.append("")

        return "\n".join(code_lines)

    def generate_magic_training_section(
        self,
        magic_config: 'MagicKeyConfiguration',
        compiled_layers: List[CompiledLayer],
        macro_refs: Dict[Tuple[str, str], str] = None
    ) -> Tuple[str, Dict[str, Dict[str, str]]]:
        """
        Generate training adaptive-key behaviors that emit '#' when a magic
        bigram is typed directly (without using MAGIC). For each base layer,
        creates one adaptive key per alternate output that falls back to the
        normal key but maps any magic-triggering predecessor to '#'.

        Returns:
            (behaviors_code, replacement_map) where replacement_map maps
            base_layer -> {alt_keycode: training_behavior_ref}
        """
        code_lines = [
            "    // Magic training behaviors: punish direct bigrams with '#'",
            "    behaviors {",
        ]

        macro_refs = macro_refs or {}
        replacement_map: Dict[str, Dict[str, str]] = {}

        # Track adaptive training behaviors per base layer so HRMs can reference them
        training_meta: Dict[str, Dict[str, Dict[str, str]]] = {}

        for base_layer, mapping in magic_config.mappings.items():
            # Group prev keys by alt output
            grouped: Dict[str, List[str]] = {}
            alt_lookup: Dict[str, object] = {}
            for prev_key, alt_key in mapping.mappings.items():
                macro_name = macro_refs.get((base_layer, str(prev_key)))
                if macro_name:
                    alt_zmk = f"&{macro_name}"
                else:
                    alt_zmk = self._translate_simple_keycode(alt_key)
                alt_lookup[alt_zmk] = alt_key
                grouped.setdefault(alt_zmk, []).append(prev_key)

            if not grouped:
                continue

            behavior_suffix = base_layer.lower().replace("base_", "")
            replacement_map[base_layer] = {}
            training_meta[base_layer] = {}

            for alt_zmk, prev_list in grouped.items():
                alt_key_value = alt_lookup[alt_zmk]
                macro_name = None
                if isinstance(prev_list, list) and prev_list:
                    macro_name = macro_refs.get((base_layer, str(prev_list[0])))
                if macro_name:
                    alt_zmk = f"&{macro_name}"
                else:
                    alt_zmk = self._translate_simple_keycode(alt_key_value)
                alt_keycode = alt_zmk.replace("&kp ", "")

                # Safe behavior name derived from translated ZMK keycode
                alt_safe = self._sanitize_token(alt_zmk)
                behavior_name = f"ak_train_{behavior_suffix}_{alt_safe}"

                # Build trigger key list
                trigger_keys = []
                for prev_key in prev_list:
                    prev_zmk_raw = self._translate_simple_keycode(prev_key)
                    trigger_keys.append(prev_zmk_raw.replace("&kp ", ""))

                code_lines.append(f"        {behavior_name}: {behavior_name} {{")
                code_lines.append(f"            compatible = \"zmk,behavior-adaptive-key\";")
                code_lines.append(f"            #binding-cells = <0>;")
                code_lines.append(f"            bindings = <{alt_zmk}>;")

                code_lines.append(f"            guard_trigger {{")
                code_lines.append(f"                trigger-keys = <{' '.join(trigger_keys)}>;")
                code_lines.append(f"                bindings = <&kp HASH>;")
                if mapping.timeout_ms > 0:
                    code_lines.append(f"                max-prior-idle-ms = <{mapping.timeout_ms}>;")
                code_lines.append(f"            }};")

                code_lines.append(f"        }};")
                code_lines.append("")

                replacement_map[base_layer][alt_zmk] = f"&{behavior_name}"
                training_meta[base_layer][alt_zmk] = {
                    "behavior_name": behavior_name,
                    "alt_safe": alt_safe,
                    "behavior_suffix": behavior_suffix,
                }

        # Generate HRM training wrappers: swap tap side of home-row mods to the
        # adaptive training behavior when the tap key is a magic alternate.
        hrm_behavior_names: set = set()
        for layer in compiled_layers:
            # Map this layer to its base magic family (if any)
            layer_mapping = magic_config.get_mapping_for_layer(layer.name) if hasattr(magic_config, "get_mapping_for_layer") else None
            if not layer_mapping:
                continue
            base_layer = layer_mapping.base_layer
            if base_layer not in training_meta:
                continue

            for kc in layer.keycodes:
                if not (kc.startswith("&hml") or kc.startswith("&hmr")):
                    continue
                parts = kc.split()
                if len(parts) < 3:
                    continue
                mod = parts[1]
                tap_key = parts[2]
                alt_zmk = self._translate_simple_keycode(tap_key)
                if alt_zmk not in training_meta[base_layer]:
                    continue

                meta = training_meta[base_layer][alt_zmk]
                behavior_suffix = meta["behavior_suffix"]
                alt_safe = meta["alt_safe"]
                ak_train_ref = f"&{meta['behavior_name']}"

                if kc.startswith("&hml"):
                    hrm_name = f"hml_train_{behavior_suffix}_{alt_safe}"
                    # Left-hand hold-tap wrapper using the training adaptive key as tap
                    # Uses timing from hml in dario_behaviors.dtsi
                    if hrm_name not in hrm_behavior_names:
                        # Properties to exclude (set explicitly in generated code)
                        exclude_props = ['compatible', 'label', 'binding-cells', 'bindings']
                        code_lines.append(f"        {hrm_name}: {hrm_name} {{")
                        code_lines.append(f"            compatible = \"zmk,behavior-hold-tap\";")
                        code_lines.append(f"            label = \"HML_TRAIN_{behavior_suffix.upper()}_{alt_safe.upper()}\";")
                        code_lines.append(f"            #binding-cells = <2>;")
                        # All properties dynamically sourced from hml in dario_behaviors.dtsi
                        code_lines.extend(self._emit_behavior_properties('hml', exclude=exclude_props))
                        code_lines.append(f"            bindings = <&kp>, <{ak_train_ref}>;")
                        code_lines.append(f"        }};")
                        code_lines.append("")
                        hrm_behavior_names.add(hrm_name)

                    # Replace this specific HRM keycode in the layer
                    replacement_map.setdefault(base_layer, {})[kc] = f"&{hrm_name} {mod} 0"

                elif kc.startswith("&hmr"):
                    hrm_name = f"hmr_train_{behavior_suffix}_{alt_safe}"
                    # Right-hand hold-tap wrapper using the training adaptive key as tap
                    # All properties dynamically sourced from hmr in dario_behaviors.dtsi
                    if hrm_name not in hrm_behavior_names:
                        # Properties to exclude (set explicitly in generated code)
                        exclude_props = ['compatible', 'label', 'binding-cells', 'bindings']
                        code_lines.append(f"        {hrm_name}: {hrm_name} {{")
                        code_lines.append(f"            compatible = \"zmk,behavior-hold-tap\";")
                        code_lines.append(f"            label = \"HMR_TRAIN_{behavior_suffix.upper()}_{alt_safe.upper()}\";")
                        code_lines.append(f"            #binding-cells = <2>;")
                        code_lines.extend(self._emit_behavior_properties('hmr', exclude=exclude_props))
                        code_lines.append(f"            bindings = <&kp>, <{ak_train_ref}>;")
                        code_lines.append(f"        }};")
                        code_lines.append("")
                        hrm_behavior_names.add(hrm_name)

                    replacement_map.setdefault(base_layer, {})[kc] = f"&{hrm_name} {mod} 0"

        code_lines.append("    };")
        code_lines.append("")

        # If no behaviors generated, return empty
        behaviors_code = "\n".join(code_lines) if len(code_lines) > 2 else ""
        return behaviors_code, replacement_map

    def _translate_simple_keycode(self, keycode) -> str:
        """
        Translate simple keycode to ZMK format (for magic key mappings)

        Args:
            keycode: Simple keycode (e.g., "A", ".", "/") or disambiguated dict

        Returns:
            ZMK keycode (e.g., "&kp A", "&kp DOT", "&kp SLASH")
        """
        # Disambiguated mapping forms: {'text': 'ent'} or {'kc': 'ENTER'}
        if isinstance(keycode, dict):
            if 'text' in keycode and isinstance(keycode['text'], str):
                macro_keys = " ".join(
                    [f"&kp {self.char_to_zmk_keycode(ch)}" for ch in keycode['text']]
                )
                return f"&macro_tap {macro_keys}"
            if 'kc' in keycode and isinstance(keycode['kc'], str):
                return self._translate_simple_keycode(keycode['kc'])

        # Array of chars/keys → macro tap sequence
        if isinstance(keycode, list):
            macro_keys = " ".join(
                [f"&kp {self.char_to_zmk_keycode(str(ch))}" for ch in keycode]
            )
            return f"&macro_tap {macro_keys}"

        if not isinstance(keycode, str):
            keycode = str(keycode)

        # Strip QMK-style KC_ prefix if present for compatibility with magic defaults
        if keycode.startswith("KC_"):
            keycode = keycode[3:]

        # Multi-letter string → emit a macro_tap sequence of characters (avoids interpreting as keycode like ENT)
        if isinstance(keycode, str) and len(keycode) > 1:
            macro_keys = " ".join(
                [f"&kp {self.char_to_zmk_keycode(ch)}" for ch in keycode]
            )
            return f"&macro_tap {macro_keys}"

        # Prefer keycodes.yaml lookup when available (single-token names)
        if isinstance(keycode, str) and keycode in self.special_keycodes:
            zmk_val = self.special_keycodes[keycode].get("zmk")
            if zmk_val:
                return zmk_val

        # Canonicalize single-character punctuation/digits to tokens based on keycodes.yaml
        if isinstance(keycode, str) and len(keycode) == 1:
            token = self.char_token_map.get(keycode)
            if token and token in self.special_keycodes:
                zmk_val = self.special_keycodes[token].get("zmk")
                if zmk_val:
                    return zmk_val
            raise ValidationError(f"Unknown magic key '{keycode}' not found in keycodes.yaml")

        # Single letter
        if isinstance(keycode, str) and len(keycode) == 1 and keycode.isalpha():
            return f"&kp {keycode.upper()}"

        # Already prefixed
        if keycode.startswith("&kp "):
            return keycode

        # Default: add &kp prefix
        return f"&kp {keycode}"

    def _sanitize_token(self, token: str) -> str:
        """
        Sanitize a ZMK expression or key token into a devicetree-safe identifier fragment.
        """
        token = str(token)
        token = token.replace("&macro_tap ", "mt_")
        token = token.replace("&kp ", "")
        token = token.replace("&", "")
        token = token.replace(" ", "_")
        token = re.sub(r'[^A-Za-z0-9_]+', "_", token)
        token = token.strip("_")
        return token.lower() or "key"

    def char_to_zmk_keycode(self, char: str) -> str:
        """Convert character to ZMK keycode, using keycodes.yaml tokens."""
        char = str(char)
        if len(char) != 1:
            raise ValidationError(f"Expected a single character for macro output, got '{char}'")

        # Letters and digits map directly
        if char.isalpha():
            token = char.upper()
        elif char.isdigit():
            token = f"N{char}"
        else:
            token = self.char_token_map.get(char)

        if not token or token not in self.special_keycodes:
            raise ValidationError(f"Unknown character '{char}' for magic macro; add it to keycodes.yaml")

        zmk_val = self.special_keycodes[token].get("zmk")
        if not zmk_val:
            raise ValidationError(f"Missing ZMK value for token '{token}' in keycodes.yaml")

        # Remove leading '&kp ' to keep compatibility with earlier consumers
        return zmk_val.replace("&kp ", "") if isinstance(zmk_val, str) and zmk_val.startswith("&kp ") else zmk_val

    def _build_char_token_map(self) -> Dict[str, str]:
        """
        Build a mapping from single characters to keycodes.yaml tokens, derived from known token names.
        """
        char_map: Dict[str, str] = {}
        for token, meta in self.special_keycodes.items():
            if not isinstance(meta, dict):
                continue

            # Prefer explicit "char" field in keycodes.yaml
            ch = meta.get("char")

            # Fall back to a single-character display_name if present
            if not ch:
                display_name = meta.get("display_name")
                if isinstance(display_name, str) and len(display_name) == 1:
                    ch = display_name

            if isinstance(ch, str) and len(ch) == 1:
                char_map[ch] = token
        return char_map
