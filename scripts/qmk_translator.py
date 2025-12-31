"""
QMK keycode translator

Translates unified keymap syntax to QMK C code syntax
"""

import re
from typing import Dict, Optional
from data_model import BehaviorAlias, ValidationError


class QMKTranslator:
    """Translate unified syntax to QMK C syntax"""

    def __init__(
        self,
        aliases: Optional[Dict[str, BehaviorAlias]] = None,
        special_keycodes: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize translator with behavior aliases and special keycodes

        Args:
            aliases: Dictionary of BehaviorAlias objects
            special_keycodes: Dictionary of special keycode mappings
        """
        self.aliases = aliases or {}
        self.special_keycodes = special_keycodes or {}
        # Track shift-morph definitions for code generation
        # Format: {(base_key, shifted_key): True}
        self.shift_morphs: Dict[tuple, bool] = {}

    def get_shift_morphs(self) -> list:
        """
        Get list of shift-morph definitions for code generation

        Returns:
            List of (base_key, shifted_key) tuples
        """
        return list(self.shift_morphs.keys())

    def clear_shift_morphs(self):
        """Clear tracked shift-morphs (call before processing a new keymap)"""
        self.shift_morphs = {}

    def translate(self, unified) -> str:
        """
        Translate unified keycode to QMK C syntax

        Examples:
        - "A" -> "KC_A"
        - "hrm:LGUI:A" -> "LGUI_T(KC_A)"
        - "lt:NAV:SPC" -> "LT(NAV, KC_SPC)"
        - "NONE" -> "KC_NO"
        - "bt:next" -> "KC_NO" (Bluetooth filtered for QMK)

        Args:
            unified: Unified keycode (string or int)

        Returns:
            QMK C code string

        Raises:
            ValidationError: If keycode is invalid or unsupported
        """
        # Convert to string if needed (for numeric keys from YAML)
        unified = str(unified)

        # Special handling for MAGIC key (QMK alternate repeat key)
        if unified == "MAGIC":
            return "QK_AREP"

        # Handle special keycodes
        if unified in self.special_keycodes:
            value = self.special_keycodes[unified].get('qmk', 'KC_NO')
            return value if value else "KC_NO"  # Treat empty string as unsupported

        # Handle aliased behaviors (e.g., hrm:LGUI:A, lt:NAV:SPC)
        if ':' in unified:
            return self._translate_alias(unified)

        # Look up common name in keycodes.yaml and return QMK value
        # keycodes.yaml uses common names (e.g., "A", "SLSH", "LGUI", "QK_BOOT", "RM_TOGG")
        if unified in self.special_keycodes:
            value = self.special_keycodes[unified].get('qmk', 'KC_NO')
            return value if value else "KC_NO"

        # Unknown keycode - raise error instead of silent fallback
        raise ValidationError(
            f"Unknown keycode '{unified}' not found in keycodes.yaml. "
            f"All keycodes must be defined in config/keycodes.yaml"
        )

    def _get_valid_modifiers(self) -> list:
        """
        Get list of valid modifier keycodes from keycodes.yaml

        Returns:
            List of valid modifier names (e.g., ['LGUI', 'RGUI', 'LALT', ...])
        """
        # Derive modifiers from keycodes.yaml
        # keycodes.yaml uses common names (LGUI, not KC_LGUI)
        modifiers = []
        for keycode in self.special_keycodes.keys():
            # Look for Lxxx and Rxxx modifiers
            if keycode.startswith('L') or keycode.startswith('R'):
                # Check if it ends with GUI, ALT, CTL/CTRL, SFT/SHFT
                if any(keycode.endswith(mod) for mod in ['GUI', 'ALT', 'CTL', 'CTRL', 'SFT', 'SHFT']):
                    modifiers.append(keycode)
        return modifiers

    def _translate_alias(self, unified: str) -> str:
        """
        Translate aliased behavior to QMK syntax

        Args:
            unified: Aliased keycode (e.g., "hrm:LGUI:A")

        Returns:
            QMK C code string

        Raises:
            ValidationError: If alias is unknown or firmware incompatible
        """
        parts = unified.split(':')
        alias_name = parts[0]

        # Special handling for shift-morph (sm:BASE:SHIFTED)
        if alias_name == 'sm':
            if len(parts) != 3:
                raise ValidationError(
                    f"Shift-morph 'sm' expects 2 parameters (base_key, shifted_key), "
                    f"got {len(parts) - 1}"
                )
            base_key = parts[1]
            shifted_key = parts[2]
            # Track this shift-morph for code generation
            self.shift_morphs[(base_key, shifted_key)] = True
            # Return the base keycode - the key override will handle the shift behavior
            if base_key in self.special_keycodes:
                return self.special_keycodes[base_key].get('qmk', f'KC_{base_key}')
            return f'KC_{base_key}'

        # Check if alias exists
        if alias_name not in self.aliases:
            # Unknown alias - return KC_NO (will be filtered)
            # Note: All known aliases should be defined in aliases.yaml
            return "KC_NO"

        alias = self.aliases[alias_name]

        # Check if alias is supported in QMK
        if 'qmk' not in alias.firmware_support:
            return "KC_NO"  # Filter unsupported

        # Validate parameter count
        if len(parts) - 1 != len(alias.params):
            raise ValidationError(
                f"Alias {alias_name} expects {len(alias.params)} parameters, "
                f"got {len(parts) - 1}"
            )

        # Build parameter dict
        params = {}
        for i, param_name in enumerate(alias.params):
            params[param_name] = parts[i + 1]

        # Translate using alias pattern
        return alias.translate_qmk(**params)

    def validate_keybinding(self, unified, layer_name: str) -> None:
        """
        Validate complex keybinding for QMK compatibility (FR-007)

        This performs strict validation to ensure complex keybindings
        (homerow mods, layer-taps, etc.) are compatible with QMK.

        Args:
            unified: Unified keycode (string or int)
            layer_name: Layer name (for error context)

        Raises:
            ValidationError: If keybinding is incompatible with QMK
        """
        # Convert to string if needed
        unified = str(unified)

        # If it's a simple keycode, no validation needed
        if ':' not in unified:
            return

        # Parse alias
        parts = unified.split(':')
        alias_name = parts[0]

        # Check if alias exists
        if alias_name not in self.aliases:
            # Unknown alias - silently accept (will be filtered during translation)
            # Note: All known aliases should be defined in aliases.yaml
            return

        alias = self.aliases[alias_name]

        # Check firmware support
        if 'qmk' not in alias.firmware_support:
            # This is a ZMK-only feature - OK, will be filtered
            return

        # Validate parameter count
        if len(parts) - 1 != len(alias.params):
            raise ValidationError(
                f"Layer {layer_name}: Alias '{alias_name}' expects "
                f"{len(alias.params)} parameters, got {len(parts) - 1} "
                f"in keycode '{unified}'"
            )

        # Additional QMK-specific validation
        # For example, validate modifier names for homerow mods
        if alias_name == 'hrm':
            mod = parts[1]
            valid_mods = self._get_valid_modifiers()
            if mod not in valid_mods:
                raise ValidationError(
                    f"Layer {layer_name}: Invalid modifier '{mod}' in '{unified}'. "
                    f"Valid modifiers: {', '.join(valid_mods)}"
                )
