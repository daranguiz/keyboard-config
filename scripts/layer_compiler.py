"""
Layer compiler

Compiles layers by applying extensions and translating keycodes
"""

from typing import List, Union, Dict, Any
from data_model import Layer, Board, CompiledLayer, ValidationError
from qmk_translator import QMKTranslator
from zmk_translator import ZMKTranslator


class LayerCompiler:
    """Compiles layers for specific boards and firmwares"""

    def __init__(self, qmk_translator: QMKTranslator, zmk_translator: ZMKTranslator):
        """
        Initialize compiler with translators

        Args:
            qmk_translator: QMK keycode translator
            zmk_translator: ZMK keycode translator
        """
        self.qmk_translator = qmk_translator
        self.zmk_translator = zmk_translator

    def compile_layer(
        self,
        layer: Layer,
        board: Board,
        firmware: str
    ) -> CompiledLayer:
        """
        Compile a layer for a specific board and firmware

        This applies the following transformations:
        1. Start with either core or full_layout
        2. Resolve position references (L36(n)) if present
        3. Apply extensions/padding based on board requirements
        4. Translate keycodes to firmware-specific syntax
        5. Validate complex keybindings

        Args:
            layer: Layer to compile
            board: Target board
            firmware: Target firmware ("qmk" or "zmk")

        Returns:
            CompiledLayer with translated keycodes

        Raises:
            ValidationError: If compilation fails
        """
        # 1. Get initial keycodes
        if layer.full_layout is not None:
            # Use full_layout directly (for special layers like GAME, or boards with L36 refs)
            keycodes = layer.full_layout.flatten()
            print(f"DEBUG: Layer {layer.name} has full_layout, flattened to {len(keycodes)} keys")
            print(f"DEBUG: First 5 keycodes after flatten: {keycodes[:5]}")

            # 2. Check if this layout contains position references
            has_refs = self._contains_position_references(keycodes)
            print(f"DEBUG: Contains position references? {has_refs}")
            if has_refs:
                # Need core to resolve references
                if layer.core is None:
                    raise ValidationError(
                        f"Layer {layer.name} uses L36 references but has no core defined"
                    )
                # Flatten core and resolve all L36(n) references
                core_flat = self._flatten_core_for_references(layer.core)
                print(f"DEBUG: Core flattened, first 5 items: {core_flat[:5]}")
                keycodes = self._resolve_position_references(keycodes, core_flat)
                print(f"DEBUG: After resolution, first 5 items: {keycodes[:5]}")
                print(f"DEBUG: Keycodes contain dicts? {any(isinstance(kc, dict) for kc in keycodes)}")
        else:
            # Use core layout and pad to board size
            keycodes = layer.core.flatten()
            keycodes = self._pad_layout_for_board(keycodes, board, layer)

        # 3. Select translator based on firmware
        translator = self.qmk_translator if firmware == "qmk" else self.zmk_translator

        # Set current layer for ZMK translator (for layer-aware MAGIC translation)
        if firmware == "zmk" and hasattr(translator, 'current_layer'):
            translator.current_layer = layer.name

        # 4. Validate complex keybindings before translation
        for keycode in keycodes:
            translator.validate_keybinding(keycode, layer.name)

        # 5. Translate keycodes (with position awareness for ZMK)
        translated = []
        for idx, kc in enumerate(keycodes):
            # Set key index for position-aware translation (ZMK hrm -> hml/hmr)
            if hasattr(translator, 'set_key_index'):
                translator.set_key_index(idx)
            translated.append(translator.translate(kc))

        print(f"DEBUG: Compiled layer {layer.name} with {len(translated)} keycodes")

        return CompiledLayer(
            name=layer.name,
            board=board,
            keycodes=translated,
            firmware=firmware
        )

    def get_extension_keys(self, extension) -> List[str]:
        """
        Flatten extension keys to a list

        Args:
            extension: LayerExtension object

        Returns:
            Flattened list of keycodes
        """
        result = []
        # Extensions define keys positionally
        # For 3x6_3: outer_pinky_left (list of 3), outer_pinky_right (list of 3)

        # Process in consistent order
        if 'outer_pinky_left' in extension.keys:
            left_keys = extension.keys['outer_pinky_left']
            if isinstance(left_keys, list):
                result.extend(left_keys)
            else:
                result.append(left_keys)

        if 'outer_pinky_right' in extension.keys:
            right_keys = extension.keys['outer_pinky_right']
            if isinstance(right_keys, list):
                result.extend(right_keys)
            else:
                result.append(right_keys)

        return result

    def _pad_layout_for_board(
        self,
        keycodes: List[str],
        board: Board,
        layer: Layer
    ) -> List[str]:
        """
        Pad the 36-key core layout to match the board's physical size.

        Uses brute-force code generation: expands core layout with KC_NO
        padding or applies optional extensions if defined.

        Args:
            keycodes: Core 36-key layout
            board: Target board
            layer: Current layer

        Returns:
            Padded keycode list matching board's physical size
        """
        layout_size = board.layout_size

        # 36-key boards: no padding needed
        if layout_size == "3x5_3":
            return keycodes

        # 42-key boards (3x6_3): add outer pinky column (3 keys per side)
        # Need to interleave the extension keys into the 3x5 matrix
        elif layout_size == "3x6_3":
            # Get extension keys (6 total: 3 left, 3 right)
            if "3x6_3" in layer.extensions:
                ext = layer.extensions["3x6_3"]
                left_pinky = ext.keys.get("outer_pinky_left", ["NONE"] * 3)
                right_pinky = ext.keys.get("outer_pinky_right", ["NONE"] * 3)
            else:
                left_pinky = ["NONE"] * 3
                right_pinky = ["NONE"] * 3

            # Interleave extension keys into the matrix
            # Core layout: left 3x5 (0-14), right 3x5 (15-29), thumbs 3+3 (30-35)
            # Target layout: left 3x6 (rows with pinky), right 3x6 (rows with pinky), thumbs 3+3
            result = []

            # Left hand: 3 rows of 6 (add pinky column to each row)
            for row in range(3):
                result.append(left_pinky[row])  # Left outer pinky
                result.extend(keycodes[row*5:(row+1)*5])  # Main 5 keys

            # Right hand: 3 rows of 6 (add pinky column to each row)
            for row in range(3):
                result.extend(keycodes[15 + row*5:15 + (row+1)*5])  # Main 5 keys
                result.append(right_pinky[row])  # Right outer pinky

            # Thumbs (unchanged from core)
            result.extend(keycodes[30:36])

            return result
        # 42->58 layout: use 3x6_3 logical layout then map into Lulu/Lily58 matrix
        elif layout_size == "custom_58_from_3x6":
            padded_42 = self._pad_to_3x6(keycodes, layer)
            return self._pad_to_58_keys_from_3x6(padded_42, layer, board)


        # 58-key boards (custom_58): Lulu, Lily58
        # These have: 12 number row + 30 main (3x5x2) + 2 outer pinky + 8 thumbs (4x2)
        # We need to map our 36-key core into this 58-key matrix
        elif layout_size == "custom_58":
            return self._pad_to_58_keys(keycodes, layer, board)

        # Custom layouts (like custom_boaty) should not reach this method
        elif layout_size.startswith("custom_"):
            raise ValidationError(
                f"Board {board.id} has custom layout size {layout_size}. "
                f"Custom layouts must use full_layout with L36(n) references, not core padding. "
                f"Ensure the layer has a full_layout defined in the board-specific keymap file."
            )

        # Unknown layout - just return core
        else:
            return keycodes

    def _pad_to_58_keys(
        self,
        keycodes: List[str],
        layer: Layer,
        board: Board
    ) -> List[str]:
        """
        Pad 36-key core to 58-key layout (Lulu/Lily58).

        Lulu/Lily58 physical layout (from info.json):
        - 6x4 matrix per side = 24 keys per side
        - Left side: rows 0-4, columns 0-5 (matrix positions)
        - Right side: rows 5-9, columns 0-5 (matrix positions)
        - Total: 58 keys

        Row breakdown:
        - Row 0 (number row): 6 keys left + 6 keys right = 12 keys (NONE)
        - Rows 1-3 (main 3x5): 15 keys left + 15 keys right = 30 keys (from core 0-29)
        - Row 4 (thumb row): 5 keys left + 5 keys right = 10 keys
          - Left: outer 2 NONE + inner 3 from core[30:33]
          - Right: inner 3 from core[33:36] + outer 2 NONE

        We also need 6 outer pinky column keys (3 per side) for rows 1-3

        Total mapping:
        - Number row (12): NONE
        - Left pinky col (3): NONE (rows 1-3, col 0)
        - Left main 3x5 (15): from core 0-14
        - Right main 3x5 (15): from core 15-29
        - Right pinky col (3): NONE (rows 1-3, col 5)
        - Left thumb row (5): NONE, NONE, core[30], core[31], core[32]
        - Right thumb row (5): core[33], core[34], core[35], NONE, NONE

        Total: 12 + 3 + 15 + 15 + 3 + 5 + 5 = 58 ✓

        Args:
            keycodes: 36-key core layout
            layer: Current layer
            board: Board configuration

        Returns:
            58-key padded layout
        """
        result = []

        # Row 0: Number row (12 keys) - all NONE
        result.extend(["NONE"] * 6)  # Left number row
        result.extend(["NONE"] * 6)  # Right number row

        # Rows 1-3: Main finger keys with outer pinky columns
        # Our core is organized as: left hand (0-14), right hand (15-29)
        # But we need to interleave pinky columns

        # Split core into left and right hands
        left_core = keycodes[0:15]   # Left 3x5
        right_core = keycodes[15:30]  # Right 3x5

        # Process rows 1-3 (3 rows of 6 keys each per side)
        for row in range(3):
            # Left side: outer pinky (NONE) + main 5 keys
            result.append("NONE")
            result.extend(left_core[row*5:(row+1)*5])

            # Right side: main 5 keys + outer pinky (NONE)
            result.extend(right_core[row*5:(row+1)*5])
            result.append("NONE")

        # Row 4: Thumb row (5 keys per side)
        # Left thumbs: 2 NONE + 3 from core
        result.extend(["NONE"] * 2)
        result.extend(keycodes[30:33])

        # Right thumbs: 3 from core + 2 NONE
        result.extend(keycodes[33:36])
        result.extend(["NONE"] * 2)

        return result

    def _pad_to_3x6(
        self,
        keycodes: List[str],
        layer: Layer
    ) -> List[str]:
        """Helper: convert 36-key core to 42-key 3x6_3 with extensions if present."""
        if "3x6_3" in layer.extensions:
            ext = layer.extensions["3x6_3"]
            left_pinky = ext.keys.get("outer_pinky_left", ["NONE"] * 3)
            right_pinky = ext.keys.get("outer_pinky_right", ["NONE"] * 3)
        else:
            left_pinky = ["NONE"] * 3
            right_pinky = ["NONE"] * 3

        result = []
        for row in range(3):
            result.append(left_pinky[row])
            result.extend(keycodes[row*5:(row+1)*5])
        for row in range(3):
            result.extend(keycodes[15 + row*5:15 + (row+1)*5])
            result.append(right_pinky[row])
        result.extend(keycodes[30:36])
        return result

    def _pad_to_58_keys_from_3x6(
        self,
        keycodes: List[str],
        layer: Layer,
        board: Board
    ) -> List[str]:
        """
        Pad 42-key 3x6_3 layout into the Lulu/Lily58 58-key matrix.

        Mapping:
        - Row 0 (number row): 12 keys -> NONE (no numbers defined)
        - Main rows (rows 1-3): take 42-key 3x6 data (already includes pinkies)
          left 3x6 + right 3x6
        - Row 3 has two center positions (LBRC/RBRC) between halves
        - Thumb row (row 4): 8 keys -> map 6 thumbs, pad outermost with NONE
        """
        left_top = keycodes[0:6]
        left_home = keycodes[6:12]
        left_bottom = keycodes[12:18]
        right_top = keycodes[18:24]
        right_home = keycodes[24:30]
        right_bottom = keycodes[30:36]
        thumbs = keycodes[36:42]

        row0 = ["NONE"] * 12
        row1 = left_top + right_top
        row2 = left_home + right_home
        row3 = left_bottom + ["NONE", "NONE"] + right_bottom
        row4 = ["NONE", thumbs[0], thumbs[1], thumbs[2], thumbs[3], thumbs[4], thumbs[5], "NONE"]

        return row0 + row1 + row2 + row3 + row4

    def _contains_position_references(self, keycodes: List[Union[str, dict]]) -> bool:
        """Check if keycode list contains any L36(n) position references"""
        for kc in keycodes:
            if isinstance(kc, dict) and kc.get("_ref") == "L36":
                return True
        return False

    def _flatten_core_for_references(self, core) -> List[Union[str, Dict[str, Any]]]:
        """
        Flatten 36-key core layout to flat list for position reference resolution.

        Position mapping (0-35) - row-based ordering:
        - 0-9: Top row (L36_0-4 = left top, L36_5-9 = right top)
        - 10-19: Home row (L36_10-14 = left home, L36_15-19 = right home)
        - 20-29: Bottom row (L36_20-24 = left bottom, L36_25-29 = right bottom)
        - 30-32: Left thumbs (3 keys)
        - 33-35: Right thumbs (3 keys)

        Args:
            core: KeyGrid with core layout

        Returns:
            Flattened list of 36 keycodes (strings or behavior dicts like hrm:LGUI:A)
        """
        flat = []

        # Row-based ordering: interleave left and right for each row
        for row in range(3):
            # Left side of this row (5 keys)
            flat.extend(core.rows[row])
            # Right side of this row (5 keys)
            flat.extend(core.rows[3 + row])

        # Thumbs: left then right
        flat.extend(core.rows[6])  # Left thumbs (3 keys)
        flat.extend(core.rows[7])  # Right thumbs (3 keys)

        if len(flat) != 36:
            raise ValidationError(
                f"Core layout must have exactly 36 keys, got {len(flat)}"
            )

        return flat

    def _resolve_position_references(
        self,
        keycodes: List[Union[str, dict]],
        core_flat: List[Union[str, Dict[str, Any]]]
    ) -> List[Union[str, Dict[str, Any]]]:
        """
        Resolve all L36(n) position references to actual keycodes from core.

        Args:
            keycodes: List potentially containing L36 reference dicts
            core_flat: Flattened 36-key core layout (strings or behavior dicts)

        Returns:
            List with all references resolved to actual keycodes (strings or behavior dicts)

        Raises:
            ValidationError: If reference index is out of range
        """
        resolved = []

        for kc in keycodes:
            if isinstance(kc, dict) and kc.get("_ref") == "L36":
                index = kc["index"]
                if index >= len(core_flat):
                    raise ValidationError(
                        f"L36 index {index} out of range (core has {len(core_flat)} keys)"
                    )
                # Resolve reference to actual keycode from core
                resolved.append(core_flat[index])
            else:
                # Regular keycode (string)
                resolved.append(kc)

        return resolved
