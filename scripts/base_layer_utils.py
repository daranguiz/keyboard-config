#!/usr/bin/env python3
"""
Base Layer Management Utilities

Provides centralized management of base layer metadata and automatic derivation
of layer families from keymap configuration.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml

from config_parser import YAMLConfigParser
from data_model import KeymapConfiguration, Layer


class BaseLayerManager:
    """Manages base layer metadata and family derivation"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.keymap_config = YAMLConfigParser.parse_keymap(config_dir / "keymap.yaml")
        self.base_metadata = self._load_base_metadata()
        self.layer_families = self._build_layer_families()

    def _load_base_metadata(self) -> Dict[str, Dict]:
        """
        Load base_layers section from keymap.yaml

        Returns:
            Dictionary mapping base layer names to their metadata
            Empty dict if base_layers section doesn't exist (backward compatible)
        """
        with open(self.config_dir / "keymap.yaml") as f:
            config = yaml.safe_load(f)

        # Return empty dict if section doesn't exist (backward compatible)
        return config.get("base_layers", {})

    def get_display_name(self, layer_name: str) -> str:
        """
        Get display-friendly name for any layer

        Examples:
            BASE_COLEMAK -> COLEMAK
            BASE_NIGHT -> NIGHT
            NUM_NIGHT -> NUM
            NAV -> NAV

        Args:
            layer_name: Full layer name (e.g., BASE_COLEMAK, NUM_NIGHT)

        Returns:
            Display name (e.g., COLEMAK, NUM)
        """
        # Check base layer metadata first
        if layer_name in self.base_metadata:
            return self.base_metadata[layer_name].get("display_name", layer_name)

        # Strip BASE_ prefix
        if layer_name.startswith("BASE_"):
            return layer_name.replace("BASE_", "")

        # Strip variant suffixes from utility layers
        for suffix in ["_NIGHT", "_V2", "_DUSK"]:
            if layer_name.endswith(suffix):
                return layer_name.replace(suffix, "")

        return layer_name

    def _derive_layer_family(self, base_layer: Layer) -> str:
        """
        Determine which layer family a base layer belongs to by analyzing
        its layer-tap references.

        Args:
            base_layer: The BASE layer to analyze

        Returns:
            Variant suffix (e.g., "", "_NIGHT", "_V2") or "" for standard family
        """
        # Extract all lt: references from the base layer
        lt_refs = []

        # Check all rows for layer-tap references (thumbs are rows 6 and 7)
        if base_layer.core and base_layer.core.rows:
            for row in base_layer.core.rows:
                for key in row:
                    if isinstance(key, str) and key.startswith("lt:"):
                        parts = key.split(":")
                        if len(parts) >= 2:
                            lt_refs.append(parts[1])

        # Detect variant suffix pattern
        # Look for common suffixes in referenced layers
        suffixes: Set[str] = set()
        for ref in lt_refs:
            # Check for _NIGHT, _V2, etc.
            if "_NIGHT" in ref:
                suffixes.add("_NIGHT")
            elif "_V2" in ref:
                suffixes.add("_V2")
            # Add more patterns as needed

        # Should have consistent suffix or none
        if len(suffixes) == 0:
            return ""  # Standard family
        elif len(suffixes) == 1:
            return suffixes.pop()
        else:
            # Inconsistent - emit warning
            print(
                f"⚠️  Warning: {base_layer.name} references inconsistent layer variants: {suffixes}"
            )
            return ""

    def _build_layer_families(self) -> Dict[str, List[str]]:
        """
        Build mapping of base layer -> [layers in its family]

        Returns:
            Dictionary like:
            {
                'BASE_COLEMAK': ['BASE_COLEMAK', 'NUM', 'SYM', 'NAV', 'MEDIA', 'FUN'],
                'BASE_NIGHT': ['BASE_NIGHT', 'NUM_NIGHT', 'SYM_NIGHT', 'NAV_NIGHT', 'MEDIA_NIGHT', 'FUN'],
                ...
            }
        """
        layer_families = {}

        base_layers = [
            name
            for name in self.keymap_config.layers.keys()
            if name.startswith("BASE_")
        ]

        for base_name in base_layers:
            base_layer = self.keymap_config.layers[base_name]
            variant_suffix = self._derive_layer_family(base_layer)

            # Build the family list
            family = [base_name]

            # Standard utility layers (always present in some form)
            utility_base_names = ["NUM", "SYM", "NAV", "MEDIA", "FUN"]

            for util_name in utility_base_names:
                # FUN layer is always shared (no variant)
                if util_name == "FUN":
                    if "FUN" in self.keymap_config.layers:
                        family.append("FUN")
                else:
                    # Apply variant suffix to other layers
                    layer_name = f"{util_name}{variant_suffix}"

                    # Only add if it exists in keymap
                    if layer_name in self.keymap_config.layers:
                        family.append(layer_name)

            layer_families[base_name] = family

        return layer_families

    def get_layer_family(self, base_name: str) -> List[str]:
        """
        Get all layers in a base layer's family

        Args:
            base_name: Base layer name (e.g., BASE_COLEMAK)

        Returns:
            List of layer names in the family
        """
        return self.layer_families.get(base_name, [])

    def get_all_base_layers(self) -> List[str]:
        """
        Get list of all base layer names

        Returns:
            List of BASE_* layer names
        """
        return [
            name
            for name in self.keymap_config.layers.keys()
            if name.startswith("BASE_")
        ]

    def apply_display_names_to_svg(self, svg_content: str) -> str:
        """
        Apply display name replacements to SVG content

        Replaces all layer references with their display names.
        This eliminates the need for hardcoded replacement lists.

        Args:
            svg_content: SVG content as string

        Returns:
            SVG content with display names applied
        """
        # Sort layer names by length (longest first) to avoid substring collision issues
        # e.g., if we replace BASE_ALT before BASE_ALT2, we get NIGHT2 instead of RACKET
        layer_names = sorted(self.keymap_config.layers.keys(), key=len, reverse=True)

        for layer_name in layer_names:
            display_name = self.get_display_name(layer_name)
            if display_name != layer_name:
                svg_content = svg_content.replace(layer_name, display_name)

        return svg_content

    def generate_keymap_drawer_config(self) -> Dict:
        """
        Generate the dynamic sections of .keymap-drawer-config.yaml

        Returns:
            Dictionary with:
                - layer_names: Ordered list for QMK enum
                - layer_legend_map: Display name mappings
                - df_keycodes: Default layer switch keycodes
        """
        # Build layer_names list (order matters for QMK enum!)
        layer_names = []

        # Add all base layers first (in order they appear in keymap.yaml)
        base_layers = self.get_all_base_layers()
        layer_names.extend(base_layers)

        # Add all utility layers (standard then variants)
        utility_names = ["NUM", "SYM", "NAV", "MEDIA", "FUN"]

        # Add standard versions first
        for util in utility_names:
            if util in self.keymap_config.layers:
                layer_names.append(util)

        # Add variant versions
        for util in utility_names:
            for suffix in ["_NIGHT", "_V2"]:
                variant = f"{util}{suffix}"
                if (
                    variant in self.keymap_config.layers
                    and variant not in layer_names
                ):
                    layer_names.append(variant)

        # Build layer_legend_map
        layer_legend_map = {}
        for layer_name in layer_names:
            display_name = self.get_display_name(layer_name)
            if display_name != layer_name:
                layer_legend_map[layer_name] = display_name

        # Build DF() keycode mappings
        df_keycodes = {}
        for base_name in base_layers:
            display_name = self.get_display_name(base_name)
            # Generate short code (COLEMAK -> CLMK, GALLIUM -> GLIUM, NIGHT -> NHT)
            if len(display_name) <= 4:
                short_code = display_name
            else:
                # Take first 2 and last 2 chars
                short_code = display_name[:2] + display_name[-2:]

            df_keycodes[f"DF({base_name})"] = short_code.upper()

        return {
            "layer_names": layer_names,
            "layer_legend_map": layer_legend_map,
            "df_keycodes": df_keycodes,
        }
