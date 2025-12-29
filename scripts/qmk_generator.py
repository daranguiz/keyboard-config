"""
QMK keymap generator

Generates QMK C code files from compiled layers
"""

from pathlib import Path
from typing import List, Dict, Tuple
import re
from data_model import Board, CompiledLayer, ComboConfiguration, Combo


class QMKGenerator:
    """Generate QMK C keymap files"""

    def __init__(self):
        # Track magic macro strings for QMK (text expansions)
        self.magic_macros: Dict[str, str] = {}

    def generate_keymap(
        self,
        board: Board,
        compiled_layers: List[CompiledLayer],
        output_dir: Path,
        combos: ComboConfiguration = None,
        magic_config: 'MagicKeyConfiguration' = None,
        raw_layers: Dict[str, 'Layer'] = None
    ) -> Dict[str, str]:
        """
        Generate all QMK files for a board

        Args:
            board: Target board
            compiled_layers: List of compiled layers
            output_dir: Output directory path
            combos: Optional combo configuration
            magic_config: Optional magic key configuration
            raw_layers: Raw layer definitions (for combo keycode lookup)

        Returns:
            Dictionary of {filename: content} for all generated files
        """
        files = {}

        # Generate keymap.c
        files['keymap.c'] = self.generate_keymap_c(board, compiled_layers, combos, magic_config, raw_layers)

        # Generate config.h
        files['config.h'] = self.generate_config_h(board, compiled_layers)

        # Generate rules.mk
        files['rules.mk'] = self.generate_rules_mk(board)

        # Generate README.md with ASCII art visualization
        files['README.md'] = self.generate_visualization(board, compiled_layers)

        return files

    def generate_keymap_c(
        self,
        board: Board,
        compiled_layers: List[CompiledLayer],
        combos: ComboConfiguration = None,
        magic_config: 'MagicKeyConfiguration' = None,
        raw_layers: Dict[str, 'Layer'] = None
    ) -> str:
        """
        Generate keymap.c file

        Args:
            board: Target board
            compiled_layers: List of compiled layers
            combos: Optional combo configuration
            magic_config: Optional magic key configuration
            raw_layers: Raw layer definitions (for combo keycode lookup)

        Returns:
            Complete keymap.c file content
        """
        # Generate layer definitions
        layer_defs = []
        layer_names = [layer.name for layer in compiled_layers]

        for layer in compiled_layers:
            formatted = self.format_layer_definition(board, layer)
            layer_defs.append(f"    [{layer.name}] = {formatted},")

        layers_code = "\n".join(layer_defs)

        # Check if we need additional layer definitions (for board-specific layers like GAME)
        has_extra_layers = len(board.extra_layers) > 0
        extra_layers_code = ""
        if has_extra_layers:
            # Define extra layer enum values after the standard layers
            extra_layers_list = ", ".join(board.extra_layers)
            extra_layers_code = f"""
// Board-specific layers (extend standard enum from dario.h)
enum {{
    {extra_layers_list} = MEDIA + 1  // Continue from last standard layer
}};
"""

        # Collect combo macros first (for text expansion combos)
        combo_macros = []
        if combos and combos.combos:
            for combo in combos.combos:
                if combo.macro_text is not None:
                    macro_name = f"MACRO_{combo.name.upper()}"
                    combo_macros.append((macro_name, combo.macro_text))

        # Generate magic key code if magic_config is provided
        magic_code = ""
        magic_handlers = ""
        self.magic_macros = {}
        if magic_config and magic_config.mappings:
            magic_code, self.magic_macros = self.generate_magic_keys_inline(magic_config, compiled_layers)

        # Generate unified custom keycode enum (combo macros first, then magic macros)
        custom_enum = self.generate_custom_keycode_enum(combo_macros, self.magic_macros)

        # Generate magic handlers if we have magic macros
        if self.magic_macros:
            magic_handlers = "\n" + self.generate_magic_macro_handlers(self.magic_macros)

        # Generate combo code if combos are provided (without the macro enum - that's in custom_enum)
        combo_code = ""
        if combos and combos.combos:
            combo_code = "\n" + self.generate_combos_inline(combos, layer_names, compiled_layers, board, raw_layers, skip_macro_enum=True)

        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml by scripts/generate.py
// Board: {board.name}
// Firmware: QMK

#include "dario.h"
{custom_enum}
{extra_layers_code}
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {{
{layers_code}
}};
{combo_code}{magic_code}{magic_handlers}"""

    def format_layer_definition(
        self,
        board: Board,
        layer: CompiledLayer
    ) -> str:
        """
        Format a layer definition using the appropriate LAYOUT macro

        Args:
            board: Target board
            layer: Compiled layer

        Returns:
            Formatted LAYOUT_* macro call
        """
        keycodes = layer.keycodes
        num_keys = len(keycodes)

        # Determine which LAYOUT macro to use
        if board.layout_size == "3x5_3":
            # 36-key split 3x5_3
            return self._format_split_3x5_3(keycodes)
        elif board.layout_size == "3x6_3":
            # 42-key split 3x6_3
            return self._format_split_3x6_3(keycodes)
        elif board.layout_size in ["custom_58", "custom_58_from_3x6"] or board.layout_size.startswith("custom_"):
            # Custom layout - use board-specific wrapper
            return self._format_custom_layout(board, keycodes)
        else:
            # Default: split 3x5_3
            return self._format_split_3x5_3(keycodes)

    def _format_split_3x5_3(self, keycodes: List[str]) -> str:
        """Format 36-key split 3x5_3 layout

        Input (row-wise): 0-4 top-left, 5-9 top-right, 10-14 home-left, 15-19 home-right,
                          20-24 bottom-left, 25-29 bottom-right, 30-32 thumbs-left, 33-35 thumbs-right

        Output (LAYOUT_split_3x5_3): Interleaved rows, no reversal needed.
        The LAYOUT macro handles physical-to-logical mapping internally.
        """
        if len(keycodes) != 36:
            raise ValueError(f"Expected 36 keys for 3x5_3 layout, got {len(keycodes)}")

        # Build interleaved rows (left + right per row)
        rows = [
            keycodes[0:5] + keycodes[5:10],      # Top row (left + right)
            keycodes[10:15] + keycodes[15:20],   # Home row (left + right)
            keycodes[20:25] + keycodes[25:30],   # Bottom row (left + right)
            keycodes[30:33] + keycodes[33:36],   # Thumbs (left + right)
        ]

        formatted_rows = []
        for i, row in enumerate(rows):
            if i < 3:  # Finger rows (10 keys each)
                formatted_rows.append("        " + ", ".join(f"{k:20}" for k in row) + ",")
            else:  # Thumb row (6 keys, no trailing comma)
                formatted_rows.append("                              " + ", ".join(f"{k:20}" for k in row))

        return f"LAYOUT_split_3x5_3(\n" + "\n".join(formatted_rows) + "\n    )"

    def _format_split_3x6_3(self, keycodes: List[str]) -> str:
        """Format 42-key split 3x6_3 layout

        Input (row-wise from _pad_to_3x6): 0-11 top (6 left + 6 right), 12-23 home, 24-35 bottom, 36-41 thumbs

        Output (LAYOUT_split_3x6_3): Interleaved rows, no reversal needed.
        The LAYOUT macro handles physical-to-logical mapping internally.
        """
        if len(keycodes) != 42:
            raise ValueError(f"Expected 42 keys for 3x6_3 layout, got {len(keycodes)}")

        # Build interleaved rows (left + right per row)
        rows = [
            keycodes[0:6] + keycodes[6:12],      # Top row (left + right)
            keycodes[12:18] + keycodes[18:24],   # Home row (left + right)
            keycodes[24:30] + keycodes[30:36],   # Bottom row (left + right)
            keycodes[36:39] + keycodes[39:42],   # Thumbs (left + right)
        ]

        formatted_rows = []
        for i, row in enumerate(rows):
            if i < 3:  # Finger rows (12 keys each)
                formatted_rows.append("        " + ", ".join(f"{k:20}" for k in row) + ",")
            else:  # Thumb row (6 keys, no trailing comma)
                formatted_rows.append("                                    " + ", ".join(f"{k:20}" for k in row))

        return f"LAYOUT_split_3x6_3(\n" + "\n".join(formatted_rows) + "\n    )"

    def _format_custom_layout(self, board: Board, keycodes: List[str]) -> str:
        """
        Format custom layout (e.g., Lulu, Lily58, Boaty)

        For custom_58_from_3x6 layouts (Lulu, Lily58), we expect 58 keys.
        Input is logical row order: left6 + right6 per row.
        Output must reverse right-side columns for the LAYOUT macro.

        For custom_boaty layouts, we expect 63 keys total.
        """
        num_keys = len(keycodes)

        if board.layout_size == "custom_boaty":
            # Boaty: 63 keys - different structure, handle separately
            row_breaks = [12, 12, 12, 14, 13]
            rows = []
            idx = 0
            for width in row_breaks:
                row = keycodes[idx:idx+width]
                rows.append("        " + ", ".join(f"{k:20}" for k in row) + ",")
                idx += width
            if rows:
                rows[-1] = rows[-1].rstrip(",")
            return f"LAYOUT(\n" + "\n".join(rows) + "\n    )"

        # Lulu/Lily58: 58 keys - no reversal needed
        # The LAYOUT macro handles physical-to-logical mapping internally
        # Input from _pad_to_58_keys_from_3x6:
        #   0-11:  row0 (number row)
        #   12-23: row1 (top alpha)
        #   24-35: row2 (home)
        #   36-49: row3 (bottom + 2 inner keys) = 14 keys
        #   50-57: row4 (thumbs) = 8 keys

        row_breaks = [12, 12, 12, 14, 8]
        rows = []
        idx = 0
        for width in row_breaks:
            row = keycodes[idx:idx+width]
            rows.append("        " + ", ".join(f"{k:20}" for k in row) + ",")
            idx += width
        if rows:
            rows[-1] = rows[-1].rstrip(",")

        return f"LAYOUT(\n" + "\n".join(rows) + "\n    )"


    def generate_config_h(
        self,
        board: Board,
        compiled_layers: List[CompiledLayer]
    ) -> str:
        """Generate config.h file"""
        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml by scripts/generate.py
// Board: {board.name}

#pragma once
"""

    def generate_rules_mk(self, board: Board) -> str:
        """Generate rules.mk file"""
        return f"""# AUTO-GENERATED - DO NOT EDIT
# Generated from config/boards.yaml by scripts/generate.py
# Board: {board.name}

# User name for userspace integration
USER_NAME := dario

# Include board-specific features if they exist
-include $(USER_PATH)/../../config/boards/{board.id}.mk

# Include global QMK rules if they exist
-include $(USER_PATH)/../../config/global/rules.mk
"""

    def generate_visualization(
        self,
        board: Board,
        compiled_layers: List[CompiledLayer]
    ) -> str:
        """
        Generate README.md with ASCII art visualization

        Args:
            board: Target board
            compiled_layers: List of compiled layers

        Returns:
            README.md content with ASCII art layer diagrams
        """
        # Generate basic ASCII art for each layer
        visualizations = []

        for layer in compiled_layers:
            viz = self._generate_layer_ascii(layer, board)
            visualizations.append(f"## {layer.name} Layer\n\n```\n{viz}\n```\n")

        viz_content = "\n".join(visualizations)

        return f"""# Keymap for {board.name}

**Auto-generated from config/keymap.yaml**

Do not edit this file directly. Edit config/keymap.yaml instead and regenerate.

## Build

```bash
qmk compile -kb {board.qmk_keyboard} -km dario
```

## Layers

{viz_content}

---

*Generated by scripts/generate.py*
"""

    def _generate_layer_ascii(self, layer: CompiledLayer, board: Board) -> str:
        """
        Generate ASCII art for a single layer

        This is a simple visualization. For production, consider integrating
        with keymap-drawer or a similar tool.
        """
        keycodes = layer.keycodes

        if board.layout_size == "3x5_3" and len(keycodes) == 36:
            # 36-key layout
            return f"""
╭─────────┬─────────┬─────────┬─────────┬─────────╮   ╭─────────┬─────────┬─────────┬─────────┬─────────╮
│ {keycodes[0]:7} │ {keycodes[1]:7} │ {keycodes[2]:7} │ {keycodes[3]:7} │ {keycodes[4]:7} │   │ {keycodes[15]:7} │ {keycodes[16]:7} │ {keycodes[17]:7} │ {keycodes[18]:7} │ {keycodes[19]:7} │
├─────────┼─────────┼─────────┼─────────┼─────────┤   ├─────────┼─────────┼─────────┼─────────┼─────────┤
│ {keycodes[5]:7} │ {keycodes[6]:7} │ {keycodes[7]:7} │ {keycodes[8]:7} │ {keycodes[9]:7} │   │ {keycodes[20]:7} │ {keycodes[21]:7} │ {keycodes[22]:7} │ {keycodes[23]:7} │ {keycodes[24]:7} │
├─────────┼─────────┼─────────┼─────────┼─────────┤   ├─────────┼─────────┼─────────┼─────────┼─────────┤
│ {keycodes[10]:7} │ {keycodes[11]:7} │ {keycodes[12]:7} │ {keycodes[13]:7} │ {keycodes[14]:7} │   │ {keycodes[25]:7} │ {keycodes[26]:7} │ {keycodes[27]:7} │ {keycodes[28]:7} │ {keycodes[29]:7} │
╰─────────┴─────────┴─────────┼─────────┼─────────┤   ├─────────┼─────────┼─────────┴─────────┴─────────╯
                              │ {keycodes[30]:7} │ {keycodes[31]:7} │   │ {keycodes[34]:7} │ {keycodes[35]:7} │
                              │ {keycodes[32]:7} │         │   │         │         │
                              ╰─────────┴─────────╯   ╰─────────┴─────────╯
"""
        else:
            # Fallback: just list the keycodes
            return "\n".join([f"{i:2d}: {kc}" for i, kc in enumerate(keycodes)])

    def generate_combos_h(self, combos: ComboConfiguration, layer_names: List[str]) -> str:
        """
        Generate combos.h file with combo enum and declarations

        Args:
            combos: ComboConfiguration with all combos
            layer_names: List of layer names for layer index lookup

        Returns:
            Complete combos.h file content
        """
        if not combos.combos:
            # No combos defined
            return ""

        # Generate enum values for each combo
        combo_enum_names = []
        for combo in combos.combos:
            enum_name = f"COMBO_{combo.name.upper()}"
            combo_enum_names.append(enum_name)

        combo_enums = ",\n    ".join(combo_enum_names)

        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated combo definitions from config/keymap.yaml

#pragma once

#ifdef COMBO_ENABLE

#include "quantum.h"

// Combo indices
enum combo_events {{
    {combo_enums},
    COMBO_LENGTH
}};

// Combo configuration
#define COMBO_LEN COMBO_LENGTH

// External combo array declaration
extern combo_t key_combos[];

#endif  // COMBO_ENABLE
"""

    def generate_combos_c(
        self,
        combos: ComboConfiguration,
        layer_names: List[str],
        compiled_layers: List[CompiledLayer],
        board: Board
    ) -> str:
        """
        Generate combos.c file with combo definitions and processing logic

        Args:
            combos: ComboConfiguration with all combos
            layer_names: List of layer names for layer index lookup
            compiled_layers: List of compiled layers (to translate action keycodes)

        Returns:
            Complete combos.c file content
        """
        if not combos.combos:
            # No combos defined
            return ""

        # Generate combo key sequences
        combo_sequences = []
        for combo in combos.combos:
            enum_name = f"COMBO_{combo.name.upper()}"
            # Convert positions to match the board's LAYOUT_* ordering
            translated_positions = self.translate_combo_positions(combo.key_positions, board)
            positions_str = ", ".join(str(pos) for pos in translated_positions)
            combo_sequences.append(
                f"const uint16_t PROGMEM {combo.name}_combo[] = {{{positions_str}, COMBO_END}};"
            )

        sequences_code = "\n".join(combo_sequences)

        # Generate combo_t array with simple instant combos
        combo_defs = []
        for combo in combos.combos:
            enum_name = f"COMBO_{combo.name.upper()}"

            # Translate action to QMK keycode
            if combo.macro_text is not None:
                # This is a text expansion macro
                qmk_keycode = f"MACRO_{combo.name.upper()}"
            elif combo.action == "DFU":
                qmk_keycode = "QK_BOOT"  # Modern QMK bootloader keycode
            else:
                # Use the keycode translator for other actions
                qmk_keycode = f"KC_{combo.action}"  # TODO: use proper translator

            # Use simple COMBO() macro for instant trigger
            combo_defs.append(f"    [{enum_name}] = COMBO({combo.name}_combo, {qmk_keycode})")

        combos_array = ",\n".join(combo_defs)

        # No hold logic needed for instant combos
        process_combo_code = ""

        # Generate layer filtering
        layer_filter_code = ""
        filtered_combos = [c for c in combos.combos if c.layers is not None]

        if filtered_combos:
            filter_cases = []
            for combo in filtered_combos:
                enum_name = f"COMBO_{combo.name.upper()}"

                # Generate layer checks
                layer_checks = []
                for layer_name in combo.layers:
                    if layer_name in layer_names:
                        layer_checks.append(f"layer == {layer_name}")

                if layer_checks:
                    layer_condition = " || ".join(layer_checks)
                    filter_cases.append(f"""        case {enum_name}:
            // Only active on {', '.join(combo.layers)}
            return ({layer_condition});""")

            filter_switch_code = "\n".join(filter_cases)

            layer_filter_code = f"""
// Layer filtering
bool combo_should_trigger(uint16_t combo_index, combo_t *combo, uint16_t keycode, keyrecord_t *record) {{
    uint8_t layer = get_current_base_layer();

    switch (combo_index) {{
{filter_switch_code}
        default:
            return true;  // Other combos active on all layers
    }}
}}
"""

        return f"""// AUTO-GENERATED - DO NOT EDIT
// Generated combo processing logic from config/keymap.yaml

#include "dario.h"
#include "combos.h"

#ifdef COMBO_ENABLE

// Combo key sequences
{sequences_code}

// Combo definitions
combo_t key_combos[] = {{
{combos_array}
}};
{process_combo_code}
{layer_filter_code}
#endif  // COMBO_ENABLE
"""

    def _extract_base_keycode(self, qmk_keycode: str) -> str:
        """
        Extract the base keycode from a QMK keycode, stripping mod-tap wrappers.

        Examples:
            "LGUI_T(KC_N)" -> "KC_N"
            "LALT_T(KC_S)" -> "KC_S"
            "LT(NUM, KC_MAGIC)" -> "KC_MAGIC"
            "KC_B" -> "KC_B"
            "XXXXXXX" -> None (transparent/none keys)
        """
        import re

        # Skip transparent/none keys
        if qmk_keycode in ("XXXXXXX", "_______", "KC_NO", "KC_TRNS"):
            return None

        # Match mod-tap patterns like LGUI_T(KC_X), LALT_T(KC_X), etc.
        mod_tap_match = re.match(r'[A-Z]+_T\((.+)\)', qmk_keycode)
        if mod_tap_match:
            return mod_tap_match.group(1)

        # Match layer-tap patterns like LT(LAYER, KC_X)
        layer_tap_match = re.match(r'LT\([^,]+,\s*(.+)\)', qmk_keycode)
        if layer_tap_match:
            return layer_tap_match.group(1)

        # Already a plain keycode
        return qmk_keycode

    def _get_combo_keycodes(
        self,
        combo: 'Combo',
        raw_layers: Dict[str, 'Layer']
    ) -> List[str]:
        """
        Look up keycodes for combo positions from the raw layer definitions.

        Uses the first layer in combo.layers (or first base layer if not specified)
        to determine what keys are at each position in the 36-key core layout.
        """
        if not raw_layers:
            raise ValueError(f"Combo '{combo.name}' requires raw_layers for keycode lookup")

        # Find the layer to use for keycode lookup
        target_layer_name = None
        if combo.layers:
            target_layer_name = combo.layers[0]
        else:
            # Use first base layer
            for layer_name in raw_layers.keys():
                if layer_name.startswith("BASE_"):
                    target_layer_name = layer_name
                    break

        if not target_layer_name:
            raise ValueError(f"Combo '{combo.name}' has no valid layer for keycode lookup")

        target_layer = raw_layers.get(target_layer_name)
        if not target_layer:
            raise ValueError(f"Combo '{combo.name}' references layer '{target_layer_name}' which doesn't exist")

        if not target_layer.core:
            raise ValueError(f"Combo '{combo.name}' references layer '{target_layer_name}' which has no core layout")

        # Flatten the core layout to 36 keys in row-wise order
        # KeyGrid.rows structure after parsing:
        #   rows[0:3] = left hand rows (3 rows × 5 cols)
        #   rows[3:6] = right hand rows (3 rows × 5 cols)
        #   rows[6] = left thumb keys (3 keys)
        #   rows[7] = right thumb keys (3 keys)
        core = target_layer.core
        flat_keys = []

        # Top row: left[0] + right[0] (positions 0-9)
        flat_keys.extend(core.rows[0])  # Left top row
        flat_keys.extend(core.rows[3])  # Right top row

        # Home row: left[1] + right[1] (positions 10-19)
        flat_keys.extend(core.rows[1])  # Left home row
        flat_keys.extend(core.rows[4])  # Right home row

        # Bottom row: left[2] + right[2] (positions 20-29)
        flat_keys.extend(core.rows[2])  # Left bottom row
        flat_keys.extend(core.rows[5])  # Right bottom row

        # Thumbs: thumbs[0] + thumbs[1] (positions 30-35)
        flat_keys.extend(core.rows[6])  # Left thumbs
        flat_keys.extend(core.rows[7])  # Right thumbs

        # Look up keycodes at each combo position
        keycodes = []
        for pos in combo.key_positions:
            if pos >= len(flat_keys):
                raise ValueError(
                    f"Combo '{combo.name}' references position {pos} but layer '{target_layer_name}' "
                    f"only has {len(flat_keys)} core keys"
                )

            raw_key = flat_keys[pos]

            # Extract base key from HRM/LT wrappers (e.g., "hrm:LGUI:N" -> "N")
            if raw_key.startswith("hrm:") or raw_key.startswith("mt:"):
                # Format: hrm:MOD:KEY or mt:MOD:KEY
                parts = raw_key.split(":")
                raw_key = parts[-1] if len(parts) >= 3 else raw_key
            elif raw_key.startswith("lt:"):
                # Format: lt:LAYER:KEY
                parts = raw_key.split(":")
                raw_key = parts[-1] if len(parts) >= 3 else raw_key

            # Skip transparent/none keys
            if raw_key in ("NONE", "TRANS", "XXX", "_______"):
                raise ValueError(
                    f"Combo '{combo.name}' references position {pos} which has a "
                    f"transparent/none key in layer '{target_layer_name}'"
                )

            # Convert to QMK keycode
            qmk_keycode = f"KC_{raw_key}"

            keycodes.append(qmk_keycode)

        return keycodes

    def generate_combos_inline(
        self,
        combos: ComboConfiguration,
        layer_names: List[str],
        compiled_layers: List[CompiledLayer],
        board: Board,
        raw_layers: Dict[str, 'Layer'] = None,
        skip_macro_enum: bool = False
    ) -> str:
        """
        Generate combo code inline for keymap.c (not separate files)

        This is identical to generate_combos_c but without file headers
        and the #include directives since it's embedded in keymap.c

        Args:
            skip_macro_enum: If True, don't generate the macro enum (it's in generate_custom_keycode_enum)
        """
        if not combos.combos:
            return ""

        # Generate combo sequences by looking up keycodes from raw layer definitions
        sequences = []
        for combo in combos.combos:
            keys = self._get_combo_keycodes(combo, raw_layers)
            positions_str = ", ".join(keys)
            sequences.append(f"const uint16_t PROGMEM {combo.name}_combo[] = {{{positions_str}, COMBO_END}};")
        sequences_code = "\n".join(sequences)

        # Generate combo array entries with simple instant combos
        combos_array_entries = []
        for combo in combos.combos:
            enum_name = f"COMBO_{combo.name.upper()}"

            # Translate action to QMK keycode
            if combo.macro_text is not None:
                # This is a text expansion macro
                qmk_keycode = f"MACRO_{combo.name.upper()}"
            elif combo.action == "DFU":
                qmk_keycode = "QK_BOOT"
            else:
                qmk_keycode = f"KC_{combo.action}"

            # Use simple COMBO() macro for instant trigger
            combos_array_entries.append(f"    [{enum_name}] = COMBO({combo.name}_combo, {qmk_keycode})")
        combos_array = ",\n".join(combos_array_entries)

        # Generate enum
        combo_enum_names = [f"COMBO_{c.name.upper()}" for c in combos.combos]
        combo_enums = ",\n    ".join(combo_enum_names)

        # No hold logic needed for instant combos
        process_combo_code = ""

        # Generate layer filtering
        has_layer_filtering = any(c.layers for c in combos.combos)
        layer_filter_code = ""
        if has_layer_filtering:
            filter_cases = []
            for combo in combos.combos:
                if combo.layers:
                    enum_name = f"COMBO_{combo.name.upper()}"
                    layer_checks = " || ".join(f"layer == {ln}" for ln in combo.layers)
                    filter_cases.append(f"""        case {enum_name}:
            // Only active on {", ".join(combo.layers)}
            return ({layer_checks});""")

            filter_cases_str = "\n".join(filter_cases)
            layer_filter_code = f"""

// Layer filtering
bool combo_should_trigger(uint16_t combo_index, combo_t *combo, uint16_t keycode, keyrecord_t *record) {{
    uint8_t layer = get_current_base_layer();

    switch (combo_index) {{
{filter_cases_str}
        default:
            return true;  // Other combos active on all layers
    }}
}}
"""

        # Generate macro definitions for combos with macro_text
        combo_macros = []
        combo_macro_handlers = []
        for combo in combos.combos:
            if combo.macro_text is not None:
                macro_name = f"MACRO_{combo.name.upper()}"
                combo_macros.append(macro_name)
                # Generate handler case
                combo_macro_handlers.append(f"""        case {macro_name}:
            if (record->event.pressed) {{
                SEND_STRING("{combo.macro_text}");
            }}
            return false;""")

        # Generate macro enum if there are any combo macros (unless skip_macro_enum is True)
        macro_enum_code = ""
        if combo_macros and not skip_macro_enum:
            # First macro uses SAFE_RANGE, rest increment from there
            enum_entries = [f"    {combo_macros[0]} = SAFE_RANGE"]
            for macro_name in combo_macros[1:]:
                enum_entries.append(f"    {macro_name}")
            enum_entries_str = ",\n".join(enum_entries)
            macro_enum_code = f"""
// Combo macro keycodes
enum combo_macros {{
{enum_entries_str}
}};
"""

        # Generate process_combo_macros handler for combo macros
        macro_handler_code = ""
        if combo_macro_handlers:
            handlers = "\n".join(combo_macro_handlers)
            macro_handler_code = f"""

// Combo macro handlers
bool process_combo_macros(uint16_t keycode, keyrecord_t *record) {{
    switch (keycode) {{
{handlers}
        default:
            return true;
    }}
}}
"""

        return f"""
#ifdef COMBO_ENABLE
{macro_enum_code}
// Combo indices
enum combo_events {{
    {combo_enums},
    COMBO_LENGTH
}};

#define COMBO_COUNT COMBO_LENGTH

// Combo key sequences
{sequences_code}

// Combo definitions
combo_t key_combos[] = {{
{combos_array}
}};
{process_combo_code}
{layer_filter_code}{macro_handler_code}
#endif  // COMBO_ENABLE
"""

    def translate_combo_positions(self, canonical_positions: List[int], board: Board) -> List[int]:
        """
        Translate combo positions from canonical row-wise 36-key ordering to the board's
        LAYOUT_* ordering used in QMK keymaps.

        Canonical row-wise positions (36-key):
          0-9:   top row (0-4 left, 5-9 right)
          10-19: home row (10-14 left, 15-19 right)
          20-29: bottom row (20-24 left, 25-29 right)
          30-35: thumbs (30-32 left, 33-35 right)

        Since LayerCompiler now outputs row-wise, the physical LAYOUT positions
        match the row-wise scheme for each board size.
        """
        layout = board.layout_size

        # 36-key split (3x5_3): direct 1:1 mapping (row-wise in = row-wise out)
        if layout == "3x5_3":
            return canonical_positions

        # 42-key split (3x6_3): map 36-key row-wise → 42-key row-wise
        # Output layout: 0-11 top, 12-23 home, 24-35 bottom, 36-41 thumbs
        # Each row has: pinky + 5 left + 5 right + pinky
        if layout == "3x6_3":
            translated = []
            for pos in canonical_positions:
                if pos >= 30:  # Thumbs (30-35 → 36-41)
                    translated.append(pos + 6)
                else:  # Alpha keys
                    row = pos // 10      # Which row (0, 1, 2)
                    col = pos % 10       # Which column in that row (0-9)
                    # Output row has 12 keys: [pinky, left0-4, right0-4, pinky]
                    # Left cols 0-4 → output cols 1-5
                    # Right cols 5-9 → output cols 6-10
                    if col < 5:
                        new_col = col + 1  # Left hand (skip pinky)
                    else:
                        new_col = col + 1  # Right hand (col 5→6, 6→7, etc.)
                    translated.append(row * 12 + new_col)
            return translated

        # 58-key (custom_58_from_3x6): map 36-key row-wise → 58-key layout
        # Output: 12 number row + 36 main (3 rows of pinky+5+5+pinky) + 10 thumb row
        if layout == "custom_58_from_3x6":
            translated = []
            for pos in canonical_positions:
                if pos >= 30:  # Thumbs
                    # Thumb row is at positions 48-57
                    # Left thumbs (30-32) → positions 49, 50, 51
                    # Right thumbs (33-35) → positions 52, 53, 54
                    thumb_idx = pos - 30
                    if thumb_idx < 3:
                        translated.append(49 + thumb_idx)  # Left thumbs
                    else:
                        translated.append(49 + thumb_idx)  # Right thumbs (52, 53, 54)
                else:  # Alpha keys
                    row = pos // 10
                    col = pos % 10
                    # Skip number row (12 keys), then each row has 12 keys
                    # Row offset: 12 + row * 12
                    # Left cols 0-4 → output cols 1-5
                    # Right cols 5-9 → output cols 6-10
                    if col < 5:
                        new_col = col + 1
                    else:
                        new_col = col + 1
                    translated.append(12 + row * 12 + new_col)
            return translated

        # Fallback (custom layouts): return canonical
        return canonical_positions

    def generate_magic_keys_inline(
        self,
        magic_config: 'MagicKeyConfiguration',
        compiled_layers: List[CompiledLayer]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Generate QMK alternate repeat key configuration inline in keymap.c

        Uses get_alt_repeat_key_keycode_user() callback to provide
        base-layer-specific alternate key mappings.

        Args:
            magic_config: MagicKeyConfiguration with base-layer mappings
            compiled_layers: List of CompiledLayer for layer name lookups

        Returns:
            (C code string, macro_map) where macro_map is {macro_name: text}
        """
        if not magic_config or not magic_config.mappings:
            return "", {}

        # Build layer name set for validation
        layer_map = {layer.name: layer.name for layer in compiled_layers}
        macro_map: Dict[str, str] = {}

        code_lines = [
            "",
            "// Magic key configuration (alternate repeat key)",
            "uint16_t get_alt_repeat_key_keycode_user(uint16_t keycode, uint8_t mods) {",
            "    // Get current base layer (not active overlay)",
            "    uint8_t base_layer = get_current_base_layer();",
            "    ",
        ]

        # Generate switch statement for each base layer
        for base_layer, mapping in magic_config.mappings.items():
            if base_layer not in layer_map:
                continue  # Skip if layer not compiled for this board

            # Only check the base layer itself, not derived layers
            # (base layer tracking handles this now)
            code_lines.append(f"    // {base_layer} family")
            code_lines.append(f"    if (base_layer == {base_layer}) {{")
            code_lines.append("        switch (keycode) {")

            # Generate mappings
            for prev_key, alt_key in mapping.mappings.items():
                prev_qmk = self._translate_simple_keycode(prev_key)
                macro_name = None

                sequence = self._extract_magic_macro_sequence(alt_key)
                if sequence:
                    macro_name = self._build_magic_macro_name(base_layer, prev_key)
                    macro_map[macro_name] = "".join(sequence)

                if macro_name:
                    alt_qmk = macro_name
                else:
                    alt_qmk = self._translate_simple_keycode(alt_key)
                code_lines.append(f"            case {prev_qmk}: return {alt_qmk};")

            code_lines.append("        }")
            code_lines.append("    }")
            code_lines.append("")

        # Handle default behavior
        default_behavior = list(magic_config.mappings.values())[0].default
        if default_behavior == "REPEAT":
            code_lines.append("    // Default: repeat previous key")
            code_lines.append("    return QK_REP;")
        elif default_behavior == "NONE":
            code_lines.append("    // Default: do nothing")
            code_lines.append("    return KC_NO;")
        else:
            code_lines.append(f"    // Default: {default_behavior}")
            code_lines.append(f"    return {self._translate_simple_keycode(default_behavior)};")

        code_lines.append("}")
        code_lines.append("")

        return "\n".join(code_lines), macro_map

    def _translate_simple_keycode(self, keycode) -> str:
        """
        Translate simple keycode to QMK format (for magic key mappings)

        Args:
            keycode: Simple keycode (e.g., "A", ".", "/")

        Returns:
            QMK keycode (e.g., "KC_A", "KC_DOT", "KC_SLSH")
        """
        if isinstance(keycode, list):
            keycode = "".join(str(k) for k in keycode)

        if not isinstance(keycode, str):
            keycode = str(keycode)

        # Handle special characters
        special_chars = {
            ".": "KC_DOT",
            ",": "KC_COMM",
            "/": "KC_SLSH",
            "'": "KC_QUOT",
            "-": "KC_MINS",
            ";": "KC_SCLN",
            "[": "KC_LBRC",
            "]": "KC_RBRC",
            " ": "KC_SPC",
            ">": "KC_GT",
            "<": "KC_LT",
            ":": "KC_COLN",
            "?": "KC_QUES",
            "=": "KC_EQL",
            "#": "KC_HASH",
            "_": "KC_UNDS",
        }

        if keycode in special_chars:
            return special_chars[keycode]

        # Single letter: KC_X
        if len(keycode) == 1 and keycode.isalpha():
            return f"KC_{keycode.upper()}"

        # Already prefixed
        if keycode.startswith("KC_"):
            return keycode

        # Default: add KC_ prefix
        return f"KC_{keycode}"

    def _extract_magic_macro_sequence(self, alt_key) -> List[str]:
        """
        Return list of characters if alt_key represents a text expansion.
        """
        if isinstance(alt_key, dict) and 'text' in alt_key and isinstance(alt_key['text'], str):
            return list(alt_key['text'])
        if isinstance(alt_key, list):
            return [str(k) for k in alt_key]
        if isinstance(alt_key, str) and len(alt_key) > 1:
            return list(alt_key)
        return []

    def _build_magic_macro_name(self, base_layer: str, prev_key) -> str:
        """
        Construct a stable macro name for a magic text expansion.
        """
        behavior_suffix = base_layer.lower().replace("base_", "")
        safe_prev = self._sanitize_token(prev_key) or "key"
        safe_prev = safe_prev.replace(" ", "_")

        if safe_prev == "key":
            # Disambiguate punctuation/non-alnum keys by ASCII code
            chars = str(prev_key)
            if len(chars) == 1:
                safe_prev = f"CHR_{ord(chars)}"
        return f"MAGIC_{behavior_suffix}_{safe_prev}".upper()

    def generate_custom_keycode_enum(
        self,
        combo_macros: List[Tuple[str, str]],
        magic_macros: Dict[str, str]
    ) -> str:
        """
        Generate a unified enum for all custom keycodes (combo macros + magic macros).

        Combo macros come first, then magic macros continue from there.
        This ensures no keycode value conflicts.

        Args:
            combo_macros: List of (macro_name, macro_text) tuples for combo macros
            magic_macros: Dict of {macro_name: text} for magic macros

        Returns:
            C enum definition string
        """
        if not combo_macros and not magic_macros:
            return ""

        lines = []
        enum_entries = []

        # Combo macros come first
        if combo_macros:
            # First combo macro starts at SAFE_RANGE
            enum_entries.append(f"    {combo_macros[0][0]} = SAFE_RANGE")
            for macro_name, _ in combo_macros[1:]:
                enum_entries.append(f"    {macro_name}")

        # Magic macros follow combo macros
        if magic_macros:
            magic_names = sorted(magic_macros.keys())
            for name in magic_names:
                enum_entries.append(f"    {name}")

        if enum_entries:
            lines.append("")
            lines.append("enum magic_macros {")
            lines.append(",\n".join(enum_entries) + ",")
            lines.append("};")
            lines.append("")

        return "\n".join(lines)

    def generate_magic_macro_enum(self, macro_map: Dict[str, str]) -> str:
        """
        Emit enum definitions for magic text expansion keycodes.
        DEPRECATED: Use generate_custom_keycode_enum instead for unified enum.
        """
        if not macro_map:
            return ""

        names = sorted(macro_map.keys())
        lines = [
            "#ifndef MACRO_GITHUB_URL",
            "#define MACRO_GITHUB_URL SAFE_RANGE",
            "#endif",
            "",
            "enum magic_macros {",
        ]

        lines.append(f"    {names[0]} = MACRO_GITHUB_URL + 1,")
        for name in names[1:]:
            lines.append(f"    {name},")
        lines.append("};")
        lines.append("")
        return "\n".join(lines)

    def _char_to_qmk_keycode(self, ch: str) -> str:
        """Translate a single character to a QMK keycode string."""
        if len(ch) != 1:
            raise ValueError(f"Expected single character, got '{ch}'")
        if ch.isalpha():
            return f"KC_{ch.upper()}"
        mapping = {
            " ": "KC_SPC",
            ",": "KC_COMM",
            ".": "KC_DOT",
            "-": "KC_MINS",
            "'": "KC_QUOT",
            "/": "KC_SLSH",
        }
        if ch in mapping:
            return mapping[ch]
        # Fallback: use the character itself; likely to be caught by compiler if invalid
        return f"KC_{ch.upper()}"

    def generate_magic_macro_handlers(self, macro_map: Dict[str, str]) -> str:
        """
        Emit process_magic_record() helper that SEND_STRINGs magic expansions.
        """
        if not macro_map:
            return ""

        lines = [
            "",
            "bool process_magic_record(uint16_t keycode, keyrecord_t *record) {",
            "    if (!record->event.pressed) {",
            "        return true;",
            "    }",
            "    switch (keycode) {",
        ]

        for name in sorted(macro_map.keys()):
            text = macro_map[name]
            # Default to lowercase output for magic text expansions
            text = text.lower()
            escaped = text.replace("\\", "\\\\").replace("\"", "\\\"")
            lines.append(f"        case {name}:")
            lines.append(f"            SEND_STRING(\"{escaped}\");")
            lines.append(f"            return false;")

        lines.append("    }")
        lines.append("    return true;")
        lines.append("}")
        lines.append("")

        # Helper used by magic.c training: map magic macro keycodes to the first
        # key they would emit, so we can detect direct bigrams and punish with '#'.
        lines.append("uint16_t magic_training_first_keycode(uint16_t keycode) {")
        lines.append("    switch (keycode) {")
        for name in sorted(macro_map.keys()):
            text = macro_map[name]
            text = text.lower()
            first = text[0] if text else ""
            # Only train on bigrams (single-char alternates). Skip multi-char macros.
            keycode_str = self._char_to_qmk_keycode(first) if first and len(text) == 1 else "KC_NO"
            lines.append(f"        case {name}: return {keycode_str};")
        lines.append("    }")
        lines.append("    return keycode;")
        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def _sanitize_token(self, token: str) -> str:
        """
        Sanitize token into an identifier-friendly fragment.
        """
        token = str(token)
        token = token.replace("&kp ", "")
        token = token.replace("&", "")
        token = token.replace("KC_", "")
        token = token.replace(" ", "_")
        token = re.sub(r'[^A-Za-z0-9_]+', "_", token)
        token = token.strip("_")
        return token or "key"
