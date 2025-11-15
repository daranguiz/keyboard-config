#!/usr/bin/env python3
"""
One-time migration script: users/dario/layers.h → config/keymap.yaml

Parses existing C macro layer definitions and converts them to unified YAML format.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


def parse_layer_macro(macro_text: str) -> List[str]:
    """
    Extract keycodes from #define LAYER_* macro.

    Example input:
        #define LAYER_BASE \
            KC_Q, KC_W, ..., \
            ...

    Returns:
        ['KC_Q', 'KC_W', ...]
    """
    # Remove #define line and layer name
    lines = macro_text.strip().split('\n')

    # Find the line with #define
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('#define'):
            start_idx = i + 1
            break

    # Join all lines after #define, remove backslashes and extra whitespace
    keycode_lines = lines[start_idx:]
    keycodes_str = ' '.join(keycode_lines).replace('\\', '').strip()

    # Split by commas and clean up
    keycodes = [kc.strip() for kc in keycodes_str.split(',') if kc.strip()]

    return keycodes


def translate_to_unified(qmk_keycode: str) -> str:
    """
    Translate QMK C syntax to unified YAML syntax.

    Translations:
    - LGUI_T(KC_A) → hrm:LGUI:A
    - LALT_T(KC_R) → hrm:LALT:R
    - LT(NAV, KC_SPC) → lt:NAV:SPC
    - KC_NO, U_NA, U_NU, U_NP → NONE
    - KC_A → A
    - ALGR_T(KC_DOT) → special case: ALGR_T:DOT
    """
    # Handle mod-tap: LGUI_T(KC_A) -> hrm:LGUI:A
    mod_tap_match = re.match(r'([LR](?:GUI|ALT|CTL|SFT))_T\(KC_(\w+)\)', qmk_keycode)
    if mod_tap_match:
        mod, key = mod_tap_match.groups()
        return f"hrm:{mod}:{key}"

    # Handle ALGR_T specially (AltGr is a modifier tap)
    algr_match = re.match(r'ALGR_T\(KC_(\w+)\)', qmk_keycode)
    if algr_match:
        key = algr_match.group(1)
        return f"ALGR_T:{key}"

    # Handle layer-tap: LT(NAV, KC_SPC) -> lt:NAV:SPC
    layer_tap_match = re.match(r'LT\((\w+),\s*KC_(\w+)\)', qmk_keycode)
    if layer_tap_match:
        layer, key = layer_tap_match.groups()
        return f"lt:{layer}:{key}"

    # Handle special unavailable/unused markers
    if qmk_keycode in ('KC_NO', 'U_NA', 'U_NU', 'U_NP'):
        return 'NONE'

    # Handle standard KC_ keycodes: KC_A -> A
    if qmk_keycode.startswith('KC_'):
        return qmk_keycode[3:]

    # Handle RGB macros (RM_*)
    if qmk_keycode.startswith('RM_'):
        return qmk_keycode  # Keep as-is for now

    # Return as-is if no pattern matches
    return qmk_keycode


def reorder_keycodes_to_split_layout(keycodes: List[str]) -> List[str]:
    """
    Reorder keycodes from interleaved format (10+10+10+6) to split format.

    Input format (from layers.h):
      Row 0: L0 L1 L2 L3 L4 R0 R1 R2 R3 R4  (10 keys)
      Row 1: L5 L6 L7 L8 L9 R5 R6 R7 R8 R9  (10 keys)
      Row 2: L10 L11 L12 L13 L14 R10 R11 R12 R13 R14  (10 keys)
      Row 3: LT0 LT1 LT2 RT0 RT1 RT2  (6 keys)

    Output format (3x5_3 split):
      Row 0: L0 L1 L2 L3 L4        (left hand row 0)
      Row 1: L5 L6 L7 L8 L9        (left hand row 1)
      Row 2: L10 L11 L12 L13 L14   (left hand row 2)
      Row 3: R0 R1 R2 R3 R4        (right hand row 0)
      Row 4: R5 R6 R7 R8 R9        (right hand row 1)
      Row 5: R10 R11 R12 R13 R14   (right hand row 2)
      Row 6: LT0 LT1 LT2           (left thumbs)
      Row 7: RT0 RT1 RT2           (right thumbs)
    """
    if len(keycodes) != 36:
        raise ValueError(f"Expected 36 keycodes, got {len(keycodes)}")

    # Split the interleaved rows
    row0 = keycodes[0:10]   # First 10 keys
    row1 = keycodes[10:20]  # Second 10 keys
    row2 = keycodes[20:30]  # Third 10 keys
    thumbs = keycodes[30:36]  # Last 6 keys

    # Reorder to split layout
    reordered = []

    # Left hand rows (first 5 from each row)
    reordered.extend(row0[0:5])  # L0-L4
    reordered.extend(row1[0:5])  # L5-L9
    reordered.extend(row2[0:5])  # L10-L14

    # Right hand rows (last 5 from each row)
    reordered.extend(row0[5:10])  # R0-R4
    reordered.extend(row1[5:10])  # R5-R9
    reordered.extend(row2[5:10])  # R10-R14

    # Thumbs (first 3 are left, last 3 are right)
    reordered.extend(thumbs[0:3])  # LT0-LT2
    reordered.extend(thumbs[3:6])  # RT0-RT2

    return reordered


def format_as_yaml_layer(layer_name: str, keycodes: List[str], indent: int = 4) -> str:
    """
    Format a list of 36 keycodes as YAML layer definition.

    Layout structure (3x5_3):
    - Rows 0-2: Left hand (3x5)
    - Rows 3-5: Right hand (3x5)
    - Row 6: Left thumbs (3)
    - Row 7: Right thumbs (3)
    """
    if len(keycodes) != 36:
        raise ValueError(f"Expected 36 keycodes for layer {layer_name}, got {len(keycodes)}")

    # Reorder from interleaved to split format
    split_keycodes = reorder_keycodes_to_split_layout(keycodes)

    ind = ' ' * indent
    yaml = f"{ind}{layer_name}:\n"
    yaml += f"{ind}  core:\n"

    # Left hand (rows 0-2: 5 keys each)
    yaml += f"{ind}    # Left hand (3x5)\n"
    for i in range(3):
        row = split_keycodes[i*5:(i+1)*5]
        yaml += f"{ind}    - [{', '.join(f'{k:15}' for k in row)}]\n"

    # Right hand (rows 3-5: 5 keys each)
    yaml += f"{ind}    # Right hand (3x5)\n"
    for i in range(3, 6):
        row = split_keycodes[i*5:(i+1)*5]
        yaml += f"{ind}    - [{', '.join(f'{k:15}' for k in row)}]\n"

    # Thumbs (rows 6-7: 3 keys each)
    yaml += f"{ind}    # Thumbs (3+3)\n"
    left_thumbs = split_keycodes[30:33]
    right_thumbs = split_keycodes[33:36]
    yaml += f"{ind}    - [{', '.join(f'{k:15}' for k in left_thumbs)}]\n"
    yaml += f"{ind}    - [{', '.join(f'{k:15}' for k in right_thumbs)}]\n"

    return yaml


def split_keycodes_respecting_parens(keycodes_str: str) -> List[str]:
    """
    Split comma-separated keycodes while respecting parentheses.

    Example: "KC_A, LT(NAV, KC_SPC), KC_B" -> ["KC_A", "LT(NAV, KC_SPC)", "KC_B"]
    """
    keycodes = []
    current = []
    paren_depth = 0

    for char in keycodes_str:
        if char == '(':
            paren_depth += 1
            current.append(char)
        elif char == ')':
            paren_depth -= 1
            current.append(char)
        elif char == ',' and paren_depth == 0:
            # Top-level comma - this is a separator
            keycode = ''.join(current).strip()
            if keycode:
                keycodes.append(keycode)
            current = []
        else:
            current.append(char)

    # Don't forget the last keycode
    keycode = ''.join(current).strip()
    if keycode:
        keycodes.append(keycode)

    return keycodes


def extract_layers_from_header(header_path: Path) -> Dict[str, List[str]]:
    """
    Parse users/dario/layers.h and extract all layer definitions.

    Returns:
        Dict mapping layer name to list of unified keycodes
    """
    content = header_path.read_text()

    # Find all #define LAYER_* macros
    # Pattern: #define LAYER_NAME followed by continuation lines with backslashes
    # Match until we hit the next #define or #endif
    layer_pattern = r'#define\s+(LAYER_\w+)\s+((?:[^\n]*\\\n)*[^\n]*)'

    layers = {}
    for match in re.finditer(layer_pattern, content, re.MULTILINE):
        layer_macro_name = match.group(1)
        layer_content = match.group(2)

        # Extract layer name (LAYER_BASE -> BASE)
        layer_name = layer_macro_name.replace('LAYER_', '')

        # Parse the macro to get keycodes
        # Remove backslashes and newlines
        keycodes_str = layer_content.replace('\\', '').replace('\n', ' ').strip()

        # Split by commas, but respect parentheses (for LT(), LGUI_T(), etc.)
        qmk_keycodes = split_keycodes_respecting_parens(keycodes_str)

        # Translate to unified syntax
        unified_keycodes = [translate_to_unified(kc) for kc in qmk_keycodes]

        layers[layer_name] = unified_keycodes

    return layers


def generate_keymap_yaml(layers: Dict[str, List[str]]) -> str:
    """
    Generate complete config/keymap.yaml from migrated layers.
    """
    yaml = "# Unified Keymap Configuration\n"
    yaml += "# Auto-generated from users/dario/layers.h\n"
    yaml += "# Generated by scripts/migrate_layers.py\n\n"
    yaml += "layers:\n"

    # Define layer order
    layer_order = ['BASE', 'NAV', 'MEDIA', 'NUM', 'SYM', 'FUN']

    for layer_name in layer_order:
        if layer_name in layers:
            yaml += format_as_yaml_layer(layer_name, layers[layer_name], indent=2)
            yaml += "\n"

    # Add any layers not in the predefined order
    for layer_name in layers:
        if layer_name not in layer_order:
            yaml += format_as_yaml_layer(layer_name, layers[layer_name], indent=2)
            yaml += "\n"

    return yaml


def main():
    """Main migration entry point."""
    repo_root = Path(__file__).parent.parent

    # Input: existing layers.h
    layers_h_path = repo_root / "users" / "dario" / "layers.h"

    # Output: new config/keymap.yaml
    output_path = repo_root / "config" / "keymap.yaml"

    print(f"🔍 Reading layers from: {layers_h_path}")

    if not layers_h_path.exists():
        print(f"❌ Error: {layers_h_path} not found")
        return 1

    # Extract and translate layers
    layers = extract_layers_from_header(layers_h_path)

    print(f"✅ Extracted {len(layers)} layers: {', '.join(layers.keys())}")

    # Generate YAML
    yaml_content = generate_keymap_yaml(layers)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml_content)

    print(f"✅ Generated: {output_path}")
    print("\n📝 Next steps:")
    print("   1. Review config/keymap.yaml for accuracy")
    print("   2. Add extensions for larger boards if needed")
    print("   3. Run scripts/generate.py to test generation")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
