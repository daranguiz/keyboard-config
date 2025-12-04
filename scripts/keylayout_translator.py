"""
macOS .keylayout translator for row-staggered keyboards

This module handles translation from unified layout definitions to macOS-specific:
- Virtual key codes (physical key positions)
- Output values (characters)
- Shift layer inference
"""

from typing import List, Dict, Tuple


class KeylayoutTranslator:
    """Translate row-stagger layout to macOS .keylayout format"""

    # macOS virtual key codes (HIToolbox/Events.h)
    # Maps QWERTY key names to their physical key codes
    QWERTY_TO_KEYCODE: Dict[str, int] = {
        # Number row
        '`': 50, '1': 18, '2': 19, '3': 20, '4': 21, '5': 23,
        '6': 22, '7': 26, '8': 28, '9': 25, '0': 29, '-': 27, '=': 24,

        # Top row (QWERTYUIOP)
        'q': 12, 'w': 13, 'e': 14, 'r': 15, 't': 17,
        'y': 16, 'u': 32, 'i': 34, 'o': 31, 'p': 35, '[': 33, ']': 30,

        # Home row (ASDFGHJKL)
        'a': 0, 's': 1, 'd': 2, 'f': 3, 'g': 5,
        'h': 4, 'j': 38, 'k': 40, 'l': 37, ';': 41, "'": 39,

        # Bottom row (ZXCVBNM)
        'z': 6, 'x': 7, 'c': 8, 'v': 9, 'b': 11,
        'n': 45, 'm': 46, ',': 43, '.': 47, '/': 44,

        # Special keys
        '\\': 42,
    }

    # Shift mappings for symbols
    SHIFT_MAP: Dict[str, str] = {
        # Number row
        '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
        '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+',

        # Punctuation
        ',': '<', '.': '>', '/': '?', ';': ':', "'": '"',
        '[': '{', ']': '}', '\\': '|',
    }

    # QWERTY position mapping (for quick lookups)
    # Maps each QWERTY position to its row index and column index
    QWERTY_POSITIONS: List[List[str]] = [
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']'],  # Top row
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'"],        # Home row
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']              # Bottom row
    ]

    def get_keycode_for_position(self, row: int, col: int) -> int:
        """
        Get macOS virtual key code for a QWERTY position

        Args:
            row: Row index (0=top, 1=home, 2=bottom)
            col: Column index (0-based)

        Returns:
            macOS virtual key code
        """
        qwerty_key = self.QWERTY_POSITIONS[row][col]
        return self.QWERTY_TO_KEYCODE[qwerty_key]

    def get_output_for_key(self, key: str, shifted: bool = False) -> str:
        """
        Get XML output value for a key

        Args:
            key: Key character (e.g., 'a', ',', '[')
            shifted: Whether this is for the shift layer

        Returns:
            XML output attribute value (e.g., 'a', 'A', '<', '{')
        """
        if shifted:
            # Letters: uppercase
            if key.isalpha() and len(key) == 1:
                return key.upper()
            # Symbols: lookup in SHIFT_MAP
            elif key in self.SHIFT_MAP:
                return self.SHIFT_MAP[key]
            # Otherwise unchanged
            else:
                return key
        else:
            # Base layer: lowercase/unchanged
            return key

    def infer_shift_layer(self, base_layout: List[List[str]]) -> List[List[str]]:
        """
        Auto-generate shift layer from base layout

        Args:
            base_layout: Base layer (3 rows of keys)

        Returns:
            Shift layer (3 rows of keys) with:
            - Letters: uppercase (f → F, d → D, etc.)
            - Symbols: shifted equivalents (, → <, [ → {, etc.)
        """
        shift_layout = []

        for row in base_layout:
            shift_row = []
            for key in row:
                shifted_key = self.get_output_for_key(key, shifted=True)
                shift_row.append(shifted_key)
            shift_layout.append(shift_row)

        return shift_layout

    def translate_keymapping(
        self,
        layout: List[List[str]]
    ) -> List[Tuple[int, str]]:
        """
        Translate a layout to (keycode, output) pairs

        Args:
            layout: 3 rows of keys mapping to QWERTY positions

        Returns:
            List of (keycode, output) tuples for XML generation
        """
        mappings = []

        for row_idx, row in enumerate(layout):
            for col_idx, key in enumerate(row):
                keycode = self.get_keycode_for_position(row_idx, col_idx)
                output = key
                mappings.append((keycode, output))

        return mappings

    def escape_xml(self, text: str) -> str:
        """
        Escape special characters for XML output attribute

        Args:
            text: Raw character

        Returns:
            XML-escaped character
        """
        # Special XML entities
        if text == '<':
            return '&#x003C;'
        elif text == '>':
            return '&#x003E;'
        elif text == '&':
            return '&#x0026;'
        elif text == '"':
            return '&#x0022;'
        elif text == "'":
            return '&#x0027;'
        else:
            return text
