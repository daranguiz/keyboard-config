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

        # Handle special keycodes
        if unified in self.special_keycodes:
            return self.special_keycodes[unified].get('qmk', 'KC_NO')

        # Handle aliased behaviors (e.g., hrm:LGUI:A, lt:NAV:SPC)
        if ':' in unified:
            return self._translate_alias(unified)

        # Handle already-prefixed keycodes (e.g., KC_A, QK_BOOT)
        if unified.startswith('KC_') or unified.startswith('QK_'):
            return unified

        # Handle special QMK keycodes that don't use KC_ prefix
        # RGB controls, RGB Matrix controls (these are actual keycodes without KC_ prefix)
        special_prefixes = ['RGB_', 'RM_']

        # Check if it's a function-like macro (contains parentheses)
        if '(' in unified:
            return unified

        # Check if it starts with any special prefix
        for prefix in special_prefixes:
            if unified.startswith(prefix):
                return unified

        # Simple keycode: A -> KC_A
        return f"KC_{unified}"

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

        # Check if alias exists
        if alias_name not in self.aliases:
            # Unknown alias - might be a firmware-specific feature
            # Check if it's a ZMK-only feature (starts with known ZMK prefixes)
            if alias_name in ['bt', 'out', 'ext_power']:
                return "KC_NO"  # Filter ZMK-specific
            raise ValidationError(f"Unknown behavior alias: {alias_name}")

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
            # Check for known ZMK-only features
            if alias_name in ['bt', 'out', 'ext_power', 'rgb_ug', 'bl']:
                # This is OK - will be filtered silently
                return
            raise ValidationError(
                f"Layer {layer_name}: Unknown behavior alias '{alias_name}' "
                f"in keycode '{unified}'"
            )

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
            valid_mods = ['LGUI', 'RGUI', 'LALT', 'RALT', 'LCTL', 'RCTL', 'LSFT', 'RSFT']
            if mod not in valid_mods:
                raise ValidationError(
                    f"Layer {layer_name}: Invalid modifier '{mod}' in '{unified}'. "
                    f"Valid modifiers: {', '.join(valid_mods)}"
                )
