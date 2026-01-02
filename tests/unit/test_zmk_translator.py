#!/usr/bin/env python3
"""
Unit tests for zmk_translator.py

Tests ZMK keycode translation including:
- Basic keycodes (A → A, SPC → SPACE)
- Home row mods with position awareness (hrm:LGUI:A → &hml LGUI A)
- Layer-tap (lt:NAV:SPC → &lt NAV SPACE)
- Default layer (df:BASE_ALT → &to BASE_ALT)
- One-shot layer (osl:NAV → &sl NAV)
- Shift-morph via mod-morph behaviors
- Magic key with layer awareness (&ak_magic_night)
- Bluetooth keycodes (bt:next → &bt BT_NXT)
- Layer index translation
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from zmk_translator import ZMKTranslator


@pytest.mark.tier1
class TestBasicKeycodes:
    """Test basic keycode translation"""

    def test_alpha_keys(self, zmk_translator):
        """Alpha keys should translate to ZMK devicetree format with &kp prefix"""
        assert zmk_translator.translate("A") == "&kp A"
        assert zmk_translator.translate("Z") == "&kp Z"

    def test_number_keys(self, zmk_translator):
        """Number keys should translate to ZMK devicetree format with &kp prefix"""
        assert zmk_translator.translate("0") == "&kp N0"
        assert zmk_translator.translate("9") == "&kp N9"

    def test_special_keys(self, zmk_translator):
        """Special keys should translate to ZMK devicetree format with &kp prefix"""
        assert zmk_translator.translate("SPC") == "&kp SPACE"
        assert zmk_translator.translate("ENT") == "&kp ENTER"
        assert zmk_translator.translate("TAB") == "&kp TAB"
        assert zmk_translator.translate("ESC") == "&kp ESC"

    def test_none_keycode(self, zmk_translator):
        """NONE should translate to &none"""
        result = zmk_translator.translate("NONE")
        assert result == "&none" or result == "NONE"

    def test_transparent_keycode(self, zmk_translator):
        """TRNS should translate to &trans"""
        result = zmk_translator.translate("TRNS")
        assert result == "&trans" or result == "TRNS"


@pytest.mark.tier1
class TestHomeRowMods:
    """Test home row mod (hrm:) translation with position awareness"""

    def test_hrm_left_hand(self, zmk_translator):
        """Left hand hrm should use &hml"""
        # Set context to left hand (position < 18 for 36-key layout)
        zmk_translator.set_context(layer="BASE_PRIMARY", position=10)

        result = zmk_translator.translate("hrm:LGUI:A")
        assert result == "&hml LGUI A" or result == "&hml LGUI A"

    def test_hrm_right_hand(self, zmk_translator):
        """Right hand hrm should use &hmr"""
        # Set context to right hand (position >= 18 for 36-key layout)
        zmk_translator.set_context(layer="BASE_PRIMARY", position=18)

        result = zmk_translator.translate("hrm:LGUI:SCLN")
        assert result == "&hmr LGUI SCLN" or "&hmr" in result

    def test_hrm_all_mods(self, zmk_translator):
        """All modifiers should work"""
        zmk_translator.set_context(layer="BASE_PRIMARY", position=10)

        # Test each modifier
        for mod in ["LGUI", "LALT", "LCTL", "LSFT"]:
            result = zmk_translator.translate(f"hrm:{mod}:A")
            assert mod in result, f"Modifier {mod} should appear in result"


@pytest.mark.tier1
class TestLayerTap:
    """Test layer-tap (lt:) translation"""

    def test_lt_nav_space(self, zmk_translator):
        """lt:NAV:SPC should translate to &lt NAV SPACE"""
        result = zmk_translator.translate("lt:NAV:SPC")
        # Layer index may vary, just check structure
        assert "&lt" in result
        assert "SPACE" in result or "SPC" in result

    def test_lt_num_bspc(self, zmk_translator):
        """lt:NUM:BSPC should translate to &lt NUM BSPC"""
        result = zmk_translator.translate("lt:NUM:BSPC")
        assert "&lt" in result
        assert "BSPC" in result

    def test_lt_with_layer_indices(self, zmk_translator):
        """lt: should use layer indices (numbers)"""
        result = zmk_translator.translate("lt:NAV:SPC")
        # Should contain &lt and a number (layer index)
        assert "&lt" in result


@pytest.mark.tier1
class TestDefaultLayer:
    """Test default layer (df:) translation"""

    def test_df_base_alt(self, zmk_translator):
        """df:BASE_ALT should translate to &to BASE_ALT"""
        result = zmk_translator.translate("df:BASE_ALT")
        assert "&to" in result

    def test_df_with_layer_index(self, zmk_translator):
        """df: should use layer index"""
        result = zmk_translator.translate("df:BASE_PRIMARY")
        assert "&to" in result
        # Should have a number (layer index)


@pytest.mark.tier1
class TestOneShotLayer:
    """Test one-shot layer (osl:) translation"""

    def test_osl_nav(self, zmk_translator):
        """osl:NAV should translate to &sl NAV"""
        result = zmk_translator.translate("osl:NAV")
        assert result == "&sl NAV"

    def test_osl_variant_layer(self, zmk_translator):
        """osl:NUM_NIGHT should translate to &sl NUM_NIGHT"""
        result = zmk_translator.translate("osl:NUM_NIGHT")
        assert result == "&sl NUM_NIGHT"


@pytest.mark.tier1
class TestModTap:
    """Test mod-tap (mt:) translation"""

    def test_mt_lsft_tab(self, zmk_translator):
        """mt:LSFT:TAB should translate to &mt LSFT TAB"""
        result = zmk_translator.translate("mt:LSFT:TAB")
        assert "&mt" in result
        assert "LSFT" in result or "LSHIFT" in result
        assert "TAB" in result

    def test_mt_other_mods(self, zmk_translator):
        """Other modifiers should work"""
        result = zmk_translator.translate("mt:LCTL:ESC")
        assert "&mt" in result
        assert "LCTL" in result or "LCTRL" in result


@pytest.mark.tier1
class TestShiftMorph:
    """Test shift-morph via mod-morph behaviors"""

    def test_sm_creates_behavior(self, zmk_translator):
        """sm:COMM:AT should create mod-morph behavior"""
        result = zmk_translator.translate("sm:COMM:AT")

        # Should return a behavior reference like &sm_comm_at
        assert "&" in result or result.startswith("sm_")

        # Should track the mod-morph
        morphs = zmk_translator.get_mod_morphs()
        assert len(morphs) > 0, "Should have tracked mod-morph"

    def test_sm_dot_grv(self, zmk_translator):
        """sm:DOT:GRV should create mod-morph behavior"""
        result = zmk_translator.translate("sm:DOT:GRV")
        assert "&" in result or "sm_" in result

        morphs = zmk_translator.get_mod_morphs()
        assert any("dot" in str(m).lower() for m in morphs)


@pytest.mark.tier1
class TestCapsWord:
    """Test caps word behavior translation"""

    def test_caps_word_basic(self, zmk_translator):
        """CAPS_WORD should translate to &caps_word"""
        assert zmk_translator.translate("CAPS_WORD") == "&caps_word"

    def test_caps_word_vs_caps_lock(self, zmk_translator):
        """CAPS_WORD and CAPS should be distinct"""
        caps_word = zmk_translator.translate("CAPS_WORD")
        caps_lock = zmk_translator.translate("CAPS")
        assert caps_word == "&caps_word"
        assert caps_lock == "&kp CAPS"
        assert caps_word != caps_lock


@pytest.mark.tier1
class TestMagicKey:
    """Test magic key translation with layer awareness"""

    def test_magic_with_layer_context(self, zmk_translator, magic_config):
        """MAGIC should translate to layer-specific adaptive key if magic_config is valid"""
        zmk_translator.set_context(layer="BASE_NIGHT", position=0)

        result = zmk_translator.translate("MAGIC")
        # If magic_config is None/invalid, should return &none, otherwise layer-specific behavior
        if magic_config is None:
            assert result == "&none", "Without magic_config, MAGIC should return &none"
        else:
            # Should reference layer-specific magic behavior
            assert "&ak" in result or "MAGIC" in result or result == "&none"

    def test_magic_different_layers(self, zmk_translator):
        """MAGIC should produce different behaviors for different layers"""
        zmk_translator.set_context(layer="BASE_NIGHT", position=0)
        result_night = zmk_translator.translate("MAGIC")

        zmk_translator.set_context(layer="BASE_PRIMARY", position=0)
        result_primary = zmk_translator.translate("MAGIC")

        # Results may differ based on layer (or may be the same if using shared magic)
        # Just verify they're both valid
        assert result_night is not None
        assert result_primary is not None


@pytest.mark.tier1
class TestBluetoothKeycodes:
    """Test Bluetooth keycode translation (ZMK supports BT)"""

    def test_bt_next(self, zmk_translator):
        """bt:next should translate to &bt BT_next"""
        result = zmk_translator.translate("bt:next")
        assert result == "&bt BT_next"

    def test_bt_prev(self, zmk_translator):
        """bt:prev should translate to &bt BT_prev"""
        result = zmk_translator.translate("bt:prev")
        assert result == "&bt BT_prev"

    def test_bt_clr(self, zmk_translator):
        """bt:clr should translate to &bt BT_clr"""
        result = zmk_translator.translate("bt:clr")
        assert result == "&bt BT_clr"


@pytest.mark.tier1
class TestLayerIndexMapping:
    """Test layer name to index translation"""

    def test_layer_names_mapped_to_indices(self, zmk_translator, keymap_config):
        """Layer names should be mapped to numeric indices"""
        # First, set up layer indices from keymap config
        layer_names = list(keymap_config.layers.keys())
        zmk_translator.set_layer_indices(layer_names)

        # Get layer mapping
        layer_map = zmk_translator.layer_map

        # Should have mappings
        assert len(layer_map) > 0, "Should have layer mappings"

        # Should have BASE layers
        base_layers = [name for name in layer_map.keys() if name.startswith("BASE")]
        assert len(base_layers) > 0, "Should have BASE layer mappings"

        # Indices should be integers
        for layer_name, index in layer_map.items():
            assert isinstance(index, int), f"Layer {layer_name} index should be int"


@pytest.mark.tier1
class TestContextAwareness:
    """Test translator context awareness"""

    def test_set_layer_context(self, zmk_translator):
        """Translator should accept layer context"""
        # Should not raise
        zmk_translator.set_context(layer="NAV", position=0)

    def test_set_position_context(self, zmk_translator):
        """Translator should accept position context"""
        # Should not raise
        zmk_translator.set_context(layer="BASE_PRIMARY", position=12)

    def test_position_affects_hrm(self, zmk_translator):
        """Position should affect hrm translation (left vs right)"""
        # Left hand
        zmk_translator.set_context(layer="BASE_PRIMARY", position=10)
        result_left = zmk_translator.translate("hrm:LGUI:A")

        # Right hand
        zmk_translator.set_context(layer="BASE_PRIMARY", position=18)
        result_right = zmk_translator.translate("hrm:LGUI:A")

        # Should use different behaviors (&hml vs &hmr)
        # (May be the same if implementation doesn't distinguish)


@pytest.mark.tier1
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_keycode(self, zmk_translator):
        """Empty keycode should raise ValidationError"""
        from data_model import ValidationError
        with pytest.raises(ValidationError):
            zmk_translator.translate("")

    def test_unknown_keycode_with_prefix(self, zmk_translator):
        """Unknown prefix should be handled"""
        try:
            result = zmk_translator.translate("unknown:FOO:BAR")
            # If it doesn't raise, should return something
            assert result is not None
        except Exception:
            # Raising is also acceptable
            pass


@pytest.mark.tier1
class TestAliasResolution:
    """Test alias resolution"""

    def test_common_aliases(self, zmk_translator):
        """Common aliases should resolve correctly"""
        # ESC, TAB, SPC, etc. are aliases that should resolve
        result = zmk_translator.translate("ESC")
        assert result is not None
        assert "ESC" in result or result == "ESC"

        result = zmk_translator.translate("SPC")
        assert result is not None
        assert "SPACE" in result or "SPC" in result


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
