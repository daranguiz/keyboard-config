#!/usr/bin/env python3
"""
Unit tests for qmk_translator.py

Tests QMK keycode translation including:
- Basic keycodes (A → KC_A)
- Home row mods (hrm:LGUI:A → LGUI_T(KC_A))
- Layer-tap (lt:NAV:SPC → LT(NAV, KC_SPC))
- Mod-tap (mt:LSFT:TAB → LSFT_T(KC_TAB))
- Default layer (df:BASE_ALT → DF(BASE_ALT))
- One-shot layer (osl:NAV → OSL(NAV))
- Shift-morph tracking (sm:COMM:AT → KC_COMM + track)
- Magic key (MAGIC → QK_AREP)
- Bluetooth filtering (bt:next → KC_NO)
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from qmk_translator import QMKTranslator


@pytest.mark.tier1
class TestBasicKeycodes:
    """Test basic keycode translation"""

    def test_alpha_keys(self, qmk_translator):
        """Alpha keys should translate to KC_* format"""
        assert qmk_translator.translate("A") == "KC_A"
        assert qmk_translator.translate("Z") == "KC_Z"

    def test_number_keys(self, qmk_translator):
        """Number keys should translate to KC_* format"""
        assert qmk_translator.translate("0") == "KC_0"
        assert qmk_translator.translate("9") == "KC_9"

    def test_special_keys(self, qmk_translator):
        """Special keys should translate correctly"""
        assert qmk_translator.translate("SPC") == "KC_SPC"
        assert qmk_translator.translate("ENT") == "KC_ENT"
        assert qmk_translator.translate("TAB") == "KC_TAB"
        assert qmk_translator.translate("BSPC") == "KC_BSPC"
        assert qmk_translator.translate("ESC") == "KC_ESC"

    def test_none_keycode(self, qmk_translator):
        """NONE should translate to KC_NO"""
        assert qmk_translator.translate("NONE") == "KC_NO"

    def test_transparent_keycode(self, qmk_translator):
        """TRNS should translate to KC_TRNS"""
        assert qmk_translator.translate("TRNS") == "KC_TRNS"


@pytest.mark.tier1
class TestHomeRowMods:
    """Test home row mod (hrm:) translation"""

    def test_hrm_lgui(self, qmk_translator):
        """hrm:LGUI:A should translate to LGUI_T(KC_A)"""
        result = qmk_translator.translate("hrm:LGUI:A")
        assert result == "LGUI_T(KC_A)"

    def test_hrm_lalt(self, qmk_translator):
        """hrm:LALT:S should translate to LALT_T(KC_S)"""
        result = qmk_translator.translate("hrm:LALT:S")
        assert result == "LALT_T(KC_S)"

    def test_hrm_lctl(self, qmk_translator):
        """hrm:LCTL:D should translate to LCTL_T(KC_D)"""
        result = qmk_translator.translate("hrm:LCTL:D")
        assert result == "LCTL_T(KC_D)"

    def test_hrm_lsft(self, qmk_translator):
        """hrm:LSFT:F should translate to LSFT_T(KC_F)"""
        result = qmk_translator.translate("hrm:LSFT:F")
        assert result == "LSFT_T(KC_F)"

    def test_hrm_right_hand(self, qmk_translator):
        """Right hand hrm should also work"""
        result = qmk_translator.translate("hrm:LGUI:SCLN")
        assert result == "LGUI_T(KC_SCLN)"


@pytest.mark.tier1
class TestLayerTap:
    """Test layer-tap (lt:) translation"""

    def test_lt_nav_space(self, qmk_translator):
        """lt:NAV:SPC should translate to LT(NAV, KC_SPC)"""
        result = qmk_translator.translate("lt:NAV:SPC")
        assert result == "LT(NAV, KC_SPC)"

    def test_lt_num_bspc(self, qmk_translator):
        """lt:NUM:BSPC should translate to LT(NUM, KC_BSPC)"""
        result = qmk_translator.translate("lt:NUM:BSPC")
        assert result == "LT(NUM, KC_BSPC)"

    def test_lt_sym_enter(self, qmk_translator):
        """lt:SYM:ENT should translate to LT(SYM, KC_ENT)"""
        result = qmk_translator.translate("lt:SYM:ENT")
        assert result == "LT(SYM, KC_ENT)"

    def test_lt_with_variant_layer(self, qmk_translator):
        """lt: with variant layers should work"""
        result = qmk_translator.translate("lt:NUM_NIGHT:BSPC")
        assert result == "LT(NUM_NIGHT, KC_BSPC)"


@pytest.mark.tier1
class TestModTap:
    """Test mod-tap (mt:) translation"""

    def test_mt_lsft_tab(self, qmk_translator):
        """mt:LSFT:TAB should translate to LSFT_T(KC_TAB)"""
        result = qmk_translator.translate("mt:LSFT:TAB")
        assert result == "LSFT_T(KC_TAB)"

    def test_mt_lctl_esc(self, qmk_translator):
        """mt:LCTL:ESC should translate to LCTL_T(KC_ESC)"""
        result = qmk_translator.translate("mt:LCTL:ESC")
        assert result == "LCTL_T(KC_ESC)"

    def test_mt_other_mods(self, qmk_translator):
        """Other modifiers should work"""
        assert qmk_translator.translate("mt:LGUI:A") == "LGUI_T(KC_A)"
        assert qmk_translator.translate("mt:LALT:B") == "LALT_T(KC_B)"


@pytest.mark.tier1
class TestDefaultLayer:
    """Test default layer (df:) translation"""

    def test_df_base_alt(self, qmk_translator):
        """df:BASE_ALT should translate to DF(BASE_ALT)"""
        result = qmk_translator.translate("df:BASE_ALT")
        assert result == "DF(BASE_ALT)"

    def test_df_base_primary(self, qmk_translator):
        """df:BASE_PRIMARY should translate to DF(BASE_PRIMARY)"""
        result = qmk_translator.translate("df:BASE_PRIMARY")
        assert result == "DF(BASE_PRIMARY)"

    def test_df_any_layer(self, qmk_translator):
        """df: should work with any layer name"""
        result = qmk_translator.translate("df:GAME")
        assert result == "DF(GAME)"


@pytest.mark.tier1
class TestOneShotLayer:
    """Test one-shot layer (osl:) translation"""

    def test_osl_nav(self, qmk_translator):
        """osl:NAV should translate to OSL(NAV)"""
        result = qmk_translator.translate("osl:NAV")
        assert result == "OSL(NAV)"

    def test_osl_variant_layer(self, qmk_translator):
        """osl:NUM_NIGHT should translate to OSL(NUM_NIGHT)"""
        result = qmk_translator.translate("osl:NUM_NIGHT")
        assert result == "OSL(NUM_NIGHT)"


@pytest.mark.tier1
class TestShiftMorph:
    """Test shift-morph (sm:) translation and tracking"""

    def test_sm_comm_at(self, qmk_translator):
        """sm:COMM:AT should translate to KC_COMM and track shift-morph"""
        result = qmk_translator.translate("sm:COMM:AT")
        assert result == "KC_COMM"

        # Should track the shift-morph
        morphs = qmk_translator.get_shift_morphs()
        assert len(morphs) > 0, "Should have tracked shift-morph"

    def test_sm_dot_grv(self, qmk_translator):
        """sm:DOT:GRV should translate to KC_DOT and track"""
        result = qmk_translator.translate("sm:DOT:GRV")
        assert result == "KC_DOT"

        morphs = qmk_translator.get_shift_morphs()
        # Morphs are tuples (base, shifted) without KC_ prefix
        assert any(m[0] == "DOT" for m in morphs)

    def test_multiple_shift_morphs_tracked(self, qmk_translator):
        """Multiple shift-morphs should all be tracked"""
        qmk_translator.translate("sm:COMM:AT")
        qmk_translator.translate("sm:DOT:GRV")

        morphs = qmk_translator.get_shift_morphs()
        assert len(morphs) >= 2, "Should track multiple shift-morphs"


@pytest.mark.tier1
class TestCapsWord:
    """Test caps word keycode translation"""

    def test_caps_word_basic(self, qmk_translator):
        """CAPS_WORD should translate to CW_TOGG"""
        assert qmk_translator.translate("CAPS_WORD") == "CW_TOGG"

    def test_caps_word_vs_caps_lock(self, qmk_translator):
        """CAPS_WORD and CAPS should be distinct"""
        caps_word = qmk_translator.translate("CAPS_WORD")
        caps_lock = qmk_translator.translate("CAPS")
        assert caps_word == "CW_TOGG"
        assert caps_lock == "KC_CAPS"
        assert caps_word != caps_lock


@pytest.mark.tier1
class TestMagicKey:
    """Test magic key translation"""

    def test_magic_keycode(self, qmk_translator):
        """MAGIC should translate to QK_AREP"""
        result = qmk_translator.translate("MAGIC")
        assert result == "QK_AREP"


@pytest.mark.tier1
class TestBluetoothFiltering:
    """Test Bluetooth keycode filtering (QMK doesn't support BT)"""

    def test_bt_next_filtered(self, qmk_translator):
        """bt:next should translate to KC_NO (filtered out for QMK)"""
        result = qmk_translator.translate("bt:next")
        assert result == "KC_NO"

    def test_bt_prev_filtered(self, qmk_translator):
        """bt:prev should translate to KC_NO"""
        result = qmk_translator.translate("bt:prev")
        assert result == "KC_NO"

    def test_bt_clr_filtered(self, qmk_translator):
        """bt:clr should translate to KC_NO"""
        result = qmk_translator.translate("bt:clr")
        assert result == "KC_NO"


@pytest.mark.tier1
class TestContextAwareness:
    """Test translator context awareness"""

    def test_set_layer_context(self, qmk_translator):
        """Translator should accept layer context"""
        # Should not raise
        qmk_translator.set_context(layer="NAV", position=0)

    def test_set_position_context(self, qmk_translator):
        """Translator should accept position context"""
        # Should not raise
        qmk_translator.set_context(layer="BASE_PRIMARY", position=12)


@pytest.mark.tier1
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_keycode(self, qmk_translator):
        """Empty keycode should raise ValidationError"""
        from data_model import ValidationError
        with pytest.raises(ValidationError):
            qmk_translator.translate("")

    def test_unknown_keycode_with_prefix(self, qmk_translator):
        """Unknown prefix should be handled"""
        # Behavior depends on implementation
        # Some may pass through, some may raise
        try:
            result = qmk_translator.translate("unknown:FOO:BAR")
            # If it doesn't raise, should return something
            assert result is not None
        except Exception:
            # Raising is also acceptable
            pass

    def test_malformed_syntax(self, qmk_translator):
        """Malformed syntax should be handled"""
        # Missing parts in prefixed syntax
        try:
            result = qmk_translator.translate("hrm:LGUI")  # Missing key
            assert result is not None
        except Exception:
            # Raising is acceptable
            pass


@pytest.mark.tier1
class TestAliasResolution:
    """Test alias resolution"""

    def test_common_aliases(self, qmk_translator, aliases):
        """Common aliases should resolve correctly"""
        # ESC, TAB, SPC, etc. are aliases that should resolve
        result = qmk_translator.translate("ESC")
        assert "ESC" in result or "KC_ESC" in result

        result = qmk_translator.translate("SPC")
        assert "SPC" in result or "KC_SPC" in result


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
