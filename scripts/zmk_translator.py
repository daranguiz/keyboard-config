"""
ZMK keycode translator

Translates unified keymap syntax to ZMK devicetree syntax
"""

import re
from typing import Dict, Optional
from data_model import BehaviorAlias, ValidationError


class ZMKTranslator:
    """Translate unified syntax to ZMK devicetree syntax"""

    def __init__(
        self,
        aliases: Optional[Dict[str, BehaviorAlias]] = None,
        special_keycodes: Optional[Dict[str, Dict[str, str]]] = None,
        layer_indices: Optional[Dict[str, int]] = None,
        layout_size: Optional[str] = None,
        magic_config: Optional['MagicKeyConfiguration'] = None
    ):
        """
        Initialize translator with behavior aliases and special keycodes

        Args:
            aliases: Dictionary of BehaviorAlias objects
            special_keycodes: Dictionary of special keycode mappings
            layer_indices: Dictionary mapping layer names to indices (for &lt)
            layout_size: Board layout size (e.g., "3x5_3", "3x6_3") for position-aware translation
            magic_config: Optional MagicKeyConfiguration for layer-aware MAGIC translation
        """
        self.aliases = aliases or {}
        self.special_keycodes = special_keycodes or {}
        self.layer_indices = layer_indices or {}
        self.layout_size = layout_size
        self.magic_config = magic_config
        self.current_key_index = 0  # Track current key position for context-aware translation
        self.current_layer = None  # Track current layer for layer-aware translation
        # Track shift-morph definitions for behavior generation
        # Format: {(base_key, shifted_key): True}
        self.shift_morphs: Dict[tuple, bool] = {}

    def get_shift_morphs(self) -> list:
        """
        Get list of shift-morph definitions for behavior generation

        Returns:
            List of (base_key, shifted_key) tuples
        """
        return list(self.shift_morphs.keys())

    def clear_shift_morphs(self):
        """Clear tracked shift-morphs (call before processing a new keymap)"""
        self.shift_morphs = {}

    def translate(self, unified) -> str:
        """
        Translate unified keycode to ZMK devicetree syntax

        Examples:
        - "A" -> "&kp A"
        - "hrm:LGUI:A" -> "&hrm LGUI A"
        - "lt:NAV:SPC" -> "&lt NAV SPC"
        - "osl:NAV" -> "&sl NAV"
        - "NONE" -> "&none"
        - "bt:next" -> "&bt BT_NXT"

        Args:
            unified: Unified keycode (string or int)

        Returns:
            ZMK devicetree string

        Raises:
            ValidationError: If keycode is invalid or unsupported
        """
        # Convert to string if needed
        unified = str(unified)

        # Special handling for MAGIC key (layer-aware)
        if unified == "MAGIC":
            if not self.magic_config:
                return "&none"  # No magic config, return none

            # Determine base layer from current layer name
            base_layer = self._get_base_layer_for_layer(self.current_layer)
            # Fallback to first configured base layer if current layer can't be mapped
            if not base_layer and self.magic_config.mappings:
                base_layer = next(iter(self.magic_config.mappings.keys()))

            if base_layer and base_layer in self.magic_config.mappings:
                # Return base-layer-specific adaptive key behavior
                return f"&ak_{base_layer.lower().replace('base_', '')}"
            else:
                # No mapping for this base layer
                return "&none"

        # Handle special keycodes
        if unified in self.special_keycodes:
            value = self.special_keycodes[unified].get('zmk', '&none')
            return value if value else "&none"  # Treat empty string as unsupported

        # Handle aliased behaviors (e.g., hrm:LGUI:A, lt:NAV:SPC)
        if ':' in unified:
            return self._translate_alias(unified)

        # Look up common name in keycodes.yaml and return ZMK value
        # keycodes.yaml uses common names (e.g., "A", "SLSH", "LGUI", "QK_BOOT", "BT_SEL_0")
        if unified in self.special_keycodes:
            value = self.special_keycodes[unified].get('zmk', '&none')
            return value if value else "&none"

        # Unknown keycode - raise error instead of silent fallback
        raise ValidationError(
            f"Unknown keycode '{unified}' not found in keycodes.yaml. "
            f"All keycodes must be defined in config/keycodes.yaml"
        )

    def _translate_key_for_zmk(self, key: str) -> str:
        """
        Translate a key token to ZMK format, extracting just the key part
        (no &kp prefix, used for parameters in behaviors like &hrm or &lt)

        Args:
            key: Key token in common name format (e.g., "A", "SPC", "SLSH")

        Returns:
            ZMK key name (e.g., "A", "SPACE", "FSLH")
        """
        # Special handling for MAGIC key - use layer-aware translation
        if key == "MAGIC":
            full_translation = self.translate(key)
            # Return full behavior reference (including &) since lt/mt need it
            # e.g., "&ak_gallium" stays as "&ak_gallium"
            return full_translation

        # keycodes.yaml uses common names (e.g., "SLSH", not "KC_SLSH")
        if key in self.special_keycodes:
            zmk_value = self.special_keycodes[key].get('zmk', '')
            if zmk_value:
                # Extract key from "&kp KEY" format
                if zmk_value.startswith('&kp '):
                    return zmk_value[4:]  # Remove "&kp " prefix
                # For special cases like "&none", return as-is
                return zmk_value

        # If not found, return key as-is (will become &kp <key>)
        return key

    def _translate_alias(self, unified: str) -> str:
        """
        Translate aliased behavior to ZMK syntax

        Args:
            unified: Aliased keycode (e.g., "hrm:LGUI:A")

        Returns:
            ZMK devicetree string

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
            # Track this shift-morph for behavior generation
            self.shift_morphs[(base_key, shifted_key)] = True
            # Return reference to the mod-morph behavior that will be generated
            return f"&sm_{base_key.lower()}_{shifted_key.lower()}"

        # Check if alias exists
        if alias_name not in self.aliases:
            # Unknown alias - return &none (will be filtered)
            # Note: All known aliases should be defined in aliases.yaml
            return "&none"

        alias = self.aliases[alias_name]

        # Check if alias is supported in ZMK
        if 'zmk' not in alias.firmware_support:
            return "&none"  # Filter unsupported

        # Validate parameter count
        if len(parts) - 1 != len(alias.params):
            raise ValidationError(
                f"Alias {alias_name} expects {len(alias.params)} parameters, "
                f"got {len(parts) - 1}"
            )

        # Special handling for MAGIC inside layer-tap:
        # Using &lt with MAGIC would pass the adaptive-key phandle to &kp, which
        # results in an invalid keycode (observed as a stray "6" on hardware).
        # Route MAGIC through a layer-tap wrapper that taps the adaptive key
        # directly instead of wrapping it in &kp.
        if alias_name == 'lt' and len(parts) == 3 and parts[2] == 'MAGIC':
            base_layer = self._get_base_layer_for_layer(self.current_layer)
            if self.magic_config and base_layer and base_layer in self.magic_config.mappings:
                suffix = base_layer.lower().replace("base_", "")
                # Pass layer plus dummy 0 to satisfy hold-tap's two binding cells
                return f"&lt_ak_{suffix} {parts[1]} 0"
            # If no magic config is available, drop the binding rather than emit
            # an invalid keycode.
            return "&none"

        # Special handling for MAGIC inside mod-tap:
        # Use a mod-tap helper that taps the adaptive key directly.
        if alias_name == 'mt' and len(parts) == 3 and parts[2] == 'MAGIC':
            base_layer = self._get_base_layer_for_layer(self.current_layer)
            if self.magic_config and base_layer and base_layer in self.magic_config.mappings:
                suffix = base_layer.lower().replace("base_", "")
                # Supply a dummy second cell (0) to satisfy hold-tap's two binding cells
                return f"&mt_ak_{suffix} {parts[1]} 0"
            return "&none"

        # Build parameter dict
        params = {}
        for i, param_name in enumerate(alias.params):
            param_value = parts[i + 1]
            # ZMK uses layer name #defines (e.g., &lt FUN X), not numeric indices
            # The #defines are generated in the keymap file header
            if param_name == 'key':
                # Translate key using keycodes.yaml if available
                params[param_name] = self._translate_key_for_zmk(param_value)
            else:
                params[param_name] = param_value

        # Special handling for hrm: use position-aware behavior (hml vs hmr)
        if alias_name == 'hrm':
            is_left_hand = self._is_left_hand_key(self.current_key_index)
            behavior = 'hml' if is_left_hand else 'hmr'
            # Return position-specific behavior instead of generic hrm
            return f"&{behavior} {params['mod']} {params['key']}"

        # Translate using alias pattern
        return alias.translate_zmk(**params)

    def validate_keybinding(self, unified, layer_name: str) -> None:
        """
        Validate complex keybinding for ZMK compatibility (FR-007)

        This performs strict validation to ensure complex keybindings
        (homerow mods, layer-taps, etc.) are compatible with ZMK.

        Args:
            unified: Unified keycode (string or int)
            layer_name: Layer name (for error context)

        Raises:
            ValidationError: If keybinding is incompatible with ZMK
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
        if 'zmk' not in alias.firmware_support:
            # This is a QMK-only feature - OK, will be filtered
            return

        # Validate parameter count
        if len(parts) - 1 != len(alias.params):
            raise ValidationError(
                f"Layer {layer_name}: Alias '{alias_name}' expects "
                f"{len(alias.params)} parameters, got {len(parts) - 1} "
                f"in keycode '{unified}'"
            )

        # Additional ZMK-specific validation
        # For example, validate modifier names for homerow mods
        if alias_name == 'hrm':
            mod = parts[1]
            # Accept both QMK and ZMK modifier names
            valid_mods = ['LGUI', 'RGUI', 'LALT', 'RALT', 'LCTRL', 'RCTRL', 'LSHFT', 'RSHFT',
                         'LCTL', 'RCTL', 'LSFT', 'RSFT']  # Also accept QMK shorthand
            if mod not in valid_mods:
                raise ValidationError(
                    f"Layer {layer_name}: Invalid modifier '{mod}' in '{unified}'. "
                    f"Valid modifiers: {', '.join(valid_mods)}"
                )

    def set_layer_indices(self, layer_names: list):
        """
        Set layer name to index mapping for &lt translation

        Args:
            layer_names: Ordered list of layer names
        """
        self.layer_indices = {name: idx for idx, name in enumerate(layer_names)}

    def set_key_index(self, index: int):
        """
        Set current key index for position-aware translation

        Args:
            index: Current key position in the layout (0-based)
        """
        self.current_key_index = index

    def set_context(self, layer: str = None, position: int = None) -> None:
        """Set layer and position context for translation.

        Args:
            layer: Layer name (for magic key awareness)
            position: Key position index (for left/right hand detection in hrm)

        Note:
            This is a convenience method that combines layer and position setting.
            It internally calls set_key_index() for position awareness.
        """
        if layer is not None:
            self.current_layer = layer
        if position is not None:
            self.set_key_index(position)

    @property
    def layer_map(self) -> dict:
        """Get layer name to index mapping.

        Returns:
            Dictionary mapping layer names to indices

        Note:
            This property exposes the layer_indices dictionary that is set via
            set_layer_indices(). Returns empty dict if not initialized.
        """
        return self.layer_indices if hasattr(self, 'layer_indices') else {}

    def get_mod_morphs(self) -> list:
        """Alias for get_shift_morphs() for API compatibility.

        In ZMK terminology, shift-morphs are implemented as mod-morphs.

        Returns:
            List of (base_key, shifted_key) tuples

        Note:
            This is an alias for get_shift_morphs() to maintain compatibility
            with ZMK terminology where shift-morphs are called mod-morphs.
        """
        return self.get_shift_morphs()

    def _is_left_hand_key(self, key_index: int) -> bool:
        """
        Determine if a key position is on the left hand (row-wise numbering)

        Args:
            key_index: Key position (0-based, row-wise)

        Returns:
            True if key is on left hand, False if on right hand
        """
        if self.layout_size == "3x5_3":
            # 36 keys row-wise: 0-9 top, 10-19 home, 20-29 bottom, 30-35 thumbs
            # Left: cols 0-4 on each row, right: cols 5-9
            if key_index >= 30:
                return key_index < 33  # 30-32 left thumbs, 33-35 right thumbs
            col = key_index % 10
            return col < 5
        elif self.layout_size == "3x6_3":
            # 42 keys row-wise: 0-11 top, 12-23 home, 24-35 bottom, 36-41 thumbs
            # Left: cols 0-5 on each row, right: cols 6-11
            if key_index >= 36:
                return key_index < 39  # 36-38 left thumbs, 39-41 right thumbs
            col = key_index % 12
            return col < 6
        elif self.layout_size == "totem_38":
            # 38 keys: top/home rows have 10 keys, bottom row has 12 (pinky), thumbs have 6
            # Top row (0-9): 5 left (0-4), 5 right (5-9)
            # Home row (10-19): 5 left (10-14), 5 right (15-19)
            # Bottom row (20-31): 6 left (20-25), 6 right (26-31)
            # Thumbs (32-37): 3 left (32-34), 3 right (35-37)
            if key_index >= 32:
                return key_index < 35  # 32-34 left thumbs, 35-37 right thumbs
            elif key_index >= 20:
                # Bottom row with pinky: 12 keys, 6 per side
                col = (key_index - 20) % 12
                return col < 6
            else:
                # Top and home rows: 10 keys each, 5 per side
                col = key_index % 10
                return col < 5
        else:
            # Default: assume row-wise 42-key layout
            if key_index >= 36:
                return key_index < 39
            col = key_index % 12
            return col < 6

    def _get_base_layer_for_layer(self, layer_name: str) -> Optional[str]:
        """
        Determine which base layer a given layer belongs to.

        Examples:
        - BASE_NIGHT → BASE_NIGHT
        - NUM_NIGHT → BASE_NIGHT
        - BASE_GALLIUM → BASE_GALLIUM
        - NAV_NIGHT → BASE_NIGHT

        Args:
            layer_name: Name of the layer to check

        Returns:
            Base layer name (e.g., "BASE_NIGHT") or None if not found
        """
        if not layer_name:
            return None

        # Direct base layer
        if layer_name.startswith("BASE_"):
            return layer_name

        # Derived layer - extract suffix and find matching base
        if "_" in layer_name:
            suffix = layer_name.split("_", 1)[1]  # NUM_NIGHT → NIGHT
            base_candidate = f"BASE_{suffix}"

            # Check if this base layer exists in magic config
            if self.magic_config and base_candidate in self.magic_config.mappings:
                return base_candidate

        return None
