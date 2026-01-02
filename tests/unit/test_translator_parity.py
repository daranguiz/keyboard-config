#!/usr/bin/env python3
"""
Translator Parity Tests
=======================

Exhaustive tests verifying QMK and ZMK translators produce semantically
equivalent output from the same unified input.

Test Philosophy:
- Simple structure: each test is just `assert actual == expected`
- Comprehensive coverage: 50+ hardcoded test cases
- Deterministic: uses fixed positions and layer names

Coverage:
- Basic keycodes (alpha, numbers, special keys)
- Home row mods with position awareness (left/right)
- Layer-tap, mod-tap, default layer, one-shot layer
- Shift-morph (base key for QMK, behavior ref for ZMK)
- Bluetooth filtering (QMK filters to KC_NO)
- Magic key
- Transparent and none keys
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


# =============================================================================
# TEST CASE DEFINITIONS
# =============================================================================
# Format: (unified_input, position, layer, qmk_expected, zmk_expected, description)
#
# Position reference (36-key layout):
# Left hand:  0-4 (top), 10-14 (home), 20-24 (bottom), 30-32 (thumbs)
# Right hand: 5-9 (top), 15-19 (home), 25-29 (bottom), 33-35 (thumbs)
# =============================================================================

# -----------------------------------------------------------------------------
# BASIC ALPHA KEYS (positions don't affect output)
# -----------------------------------------------------------------------------
ALPHA_CASES = [
    ("A", 10, "BASE_REF", "KC_A", "&kp A", "Alpha A"),
    ("B", 24, "BASE_REF", "KC_B", "&kp B", "Alpha B"),
    ("C", 22, "BASE_REF", "KC_C", "&kp C", "Alpha C"),
    ("D", 12, "BASE_REF", "KC_D", "&kp D", "Alpha D"),
    ("E", 2, "BASE_REF", "KC_E", "&kp E", "Alpha E"),
    ("F", 13, "BASE_REF", "KC_F", "&kp F", "Alpha F"),
    ("G", 14, "BASE_REF", "KC_G", "&kp G", "Alpha G"),
    ("H", 15, "BASE_REF", "KC_H", "&kp H", "Alpha H"),
    ("I", 7, "BASE_REF", "KC_I", "&kp I", "Alpha I"),
    ("J", 16, "BASE_REF", "KC_J", "&kp J", "Alpha J"),
    ("K", 17, "BASE_REF", "KC_K", "&kp K", "Alpha K"),
    ("L", 18, "BASE_REF", "KC_L", "&kp L", "Alpha L"),
    ("M", 26, "BASE_REF", "KC_M", "&kp M", "Alpha M"),
    ("N", 25, "BASE_REF", "KC_N", "&kp N", "Alpha N"),
    ("O", 8, "BASE_REF", "KC_O", "&kp O", "Alpha O"),
    ("P", 9, "BASE_REF", "KC_P", "&kp P", "Alpha P"),
    ("Q", 0, "BASE_REF", "KC_Q", "&kp Q", "Alpha Q"),
    ("R", 3, "BASE_REF", "KC_R", "&kp R", "Alpha R"),
    ("S", 11, "BASE_REF", "KC_S", "&kp S", "Alpha S"),
    ("T", 4, "BASE_REF", "KC_T", "&kp T", "Alpha T"),
    ("U", 6, "BASE_REF", "KC_U", "&kp U", "Alpha U"),
    ("V", 23, "BASE_REF", "KC_V", "&kp V", "Alpha V"),
    ("W", 1, "BASE_REF", "KC_W", "&kp W", "Alpha W"),
    ("X", 21, "BASE_REF", "KC_X", "&kp X", "Alpha X"),
    ("Y", 5, "BASE_REF", "KC_Y", "&kp Y", "Alpha Y"),
    ("Z", 20, "BASE_REF", "KC_Z", "&kp Z", "Alpha Z"),
]

# -----------------------------------------------------------------------------
# NUMBER KEYS (note: ZMK uses N prefix for numbers)
# -----------------------------------------------------------------------------
NUMBER_CASES = [
    ("0", 0, "NAV_REF", "KC_0", "&kp N0", "Number 0"),
    ("1", 1, "NAV_REF", "KC_1", "&kp N1", "Number 1"),
    ("2", 2, "NAV_REF", "KC_2", "&kp N2", "Number 2"),
    ("3", 3, "NAV_REF", "KC_3", "&kp N3", "Number 3"),
    ("4", 4, "NAV_REF", "KC_4", "&kp N4", "Number 4"),
    ("5", 5, "NAV_REF", "KC_5", "&kp N5", "Number 5"),
    ("6", 6, "NAV_REF", "KC_6", "&kp N6", "Number 6"),
    ("7", 7, "NAV_REF", "KC_7", "&kp N7", "Number 7"),
    ("8", 8, "NAV_REF", "KC_8", "&kp N8", "Number 8"),
    ("9", 9, "NAV_REF", "KC_9", "&kp N9", "Number 9"),
]

# -----------------------------------------------------------------------------
# SPECIAL KEYS (space, enter, etc.)
# -----------------------------------------------------------------------------
SPECIAL_KEY_CASES = [
    ("SPC", 34, "BASE_REF", "KC_SPC", "&kp SPACE", "Space"),
    ("ENT", 35, "BASE_REF", "KC_ENT", "&kp ENTER", "Enter"),
    ("TAB", 33, "BASE_REF", "KC_TAB", "&kp TAB", "Tab"),
    ("BSPC", 30, "BASE_REF", "KC_BSPC", "&kp BSPC", "Backspace"),
    ("DEL", 32, "BASE_REF", "KC_DEL", "&kp DEL", "Delete"),
    ("ESC", 0, "BASE_REF", "KC_ESC", "&kp ESC", "Escape"),
    ("CAPS", 0, "NAV_REF", "KC_CAPS", "&kp CAPS", "Caps Lock"),
    ("GRV", 0, "BASE_REF", "KC_GRV", "&kp GRAVE", "Grave/Backtick"),
    ("MINS", 29, "BASE_REF", "KC_MINS", "&kp MINUS", "Minus"),
    ("EQL", 0, "BASE_REF", "KC_EQL", "&kp EQUAL", "Equal"),
    ("LBRC", 0, "BASE_REF", "KC_LBRC", "&kp LBKT", "Left Bracket"),
    ("RBRC", 0, "BASE_REF", "KC_RBRC", "&kp RBKT", "Right Bracket"),
    ("BSLS", 0, "BASE_REF", "KC_BSLS", "&kp BSLH", "Backslash"),
    ("SCLN", 19, "BASE_REF", "KC_SCLN", "&kp SEMI", "Semicolon"),
    ("QUOT", 0, "BASE_REF", "KC_QUOT", "&kp SQT", "Quote"),
    ("COMM", 24, "BASE_REF", "KC_COMM", "&kp COMMA", "Comma"),
    ("DOT", 27, "BASE_REF", "KC_DOT", "&kp DOT", "Period"),
    ("SLSH", 28, "BASE_REF", "KC_SLSH", "&kp FSLH", "Forward Slash"),
]

# -----------------------------------------------------------------------------
# NAVIGATION KEYS
# -----------------------------------------------------------------------------
NAVIGATION_CASES = [
    ("LEFT", 16, "NAV_REF", "KC_LEFT", "&kp LEFT", "Arrow Left"),
    ("DOWN", 17, "NAV_REF", "KC_DOWN", "&kp DOWN", "Arrow Down"),
    ("UP", 7, "NAV_REF", "KC_UP", "&kp UP", "Arrow Up"),
    ("RGHT", 18, "NAV_REF", "KC_RGHT", "&kp RIGHT", "Arrow Right"),
    ("HOME", 26, "NAV_REF", "KC_HOME", "&kp HOME", "Home"),
    ("END", 29, "NAV_REF", "KC_END", "&kp END", "End"),
    ("PGUP", 28, "NAV_REF", "KC_PGUP", "&kp PG_UP", "Page Up"),
    ("PGDN", 27, "NAV_REF", "KC_PGDN", "&kp PG_DN", "Page Down"),
    ("INS", 0, "NAV_REF", "KC_INS", "&kp INS", "Insert"),
]

# -----------------------------------------------------------------------------
# MODIFIER KEYS (pure modifiers, not mod-tap)
# -----------------------------------------------------------------------------
MODIFIER_CASES = [
    ("LGUI", 10, "NAV_REF", "KC_LGUI", "&kp LGUI", "Left GUI"),
    ("LALT", 11, "NAV_REF", "KC_LALT", "&kp LALT", "Left Alt"),
    ("LCTL", 12, "NAV_REF", "KC_LCTL", "&kp LCTRL", "Left Control"),
    ("LSFT", 13, "NAV_REF", "KC_LSFT", "&kp LSHFT", "Left Shift"),
    ("RGUI", 19, "NAV_REF", "KC_RGUI", "&kp RGUI", "Right GUI"),
    ("RALT", 18, "NAV_REF", "KC_RALT", "&kp RALT", "Right Alt"),
    ("RCTL", 17, "NAV_REF", "KC_RCTL", "&kp RCTRL", "Right Control"),
    ("RSFT", 16, "NAV_REF", "KC_RSFT", "&kp RSHFT", "Right Shift"),
]

# -----------------------------------------------------------------------------
# SPECIAL CONTROL KEYS
# -----------------------------------------------------------------------------
CONTROL_CASES = [
    ("NONE", 0, "NAV_REF", "KC_NO", "&none", "No key (NONE)"),
    ("TRNS", 30, "NAV_REF", "KC_TRNS", "&trans", "Transparent"),
    # Note: DFU/bootloader tested separately as it may have different names
]

# -----------------------------------------------------------------------------
# HOME ROW MODS - Position-aware (ZMK uses &hml for left, &hmr for right)
# -----------------------------------------------------------------------------
HOME_ROW_MOD_LEFT_CASES = [
    # Left hand positions (0-14, 20-24, 30-32) use &hml in ZMK
    # Note: ZMK uses LCTL (not LCTRL), LSFT (not LSHFT)
    ("hrm:LGUI:A", 10, "BASE_REF", "LGUI_T(KC_A)", "&hml LGUI A", "HRM GUI:A left pos 10"),
    ("hrm:LALT:S", 11, "BASE_REF", "LALT_T(KC_S)", "&hml LALT S", "HRM ALT:S left pos 11"),
    ("hrm:LCTL:D", 12, "BASE_REF", "LCTL_T(KC_D)", "&hml LCTL D", "HRM CTL:D left pos 12"),
    ("hrm:LSFT:F", 13, "BASE_REF", "LSFT_T(KC_F)", "&hml LSFT F", "HRM SFT:F left pos 13"),
    # Additional left-hand positions
    ("hrm:LGUI:Q", 0, "BASE_REF", "LGUI_T(KC_Q)", "&hml LGUI Q", "HRM GUI:Q left pos 0"),
    ("hrm:LALT:Z", 20, "BASE_REF", "LALT_T(KC_Z)", "&hml LALT Z", "HRM ALT:Z left pos 20"),
    ("hrm:LCTL:ESC", 30, "BASE_REF", "LCTL_T(KC_ESC)", "&hml LCTL ESC", "HRM CTL:ESC thumb pos 30"),
]

HOME_ROW_MOD_RIGHT_CASES = [
    # Right hand positions (5-9, 15-19, 25-29, 33-35) use &hmr in ZMK
    # Note: ZMK uses LCTL (not LCTRL), LSFT (not LSHFT)
    ("hrm:LSFT:J", 16, "BASE_REF", "LSFT_T(KC_J)", "&hmr LSFT J", "HRM SFT:J right pos 16"),
    ("hrm:LCTL:K", 17, "BASE_REF", "LCTL_T(KC_K)", "&hmr LCTL K", "HRM CTL:K right pos 17"),
    ("hrm:LALT:L", 18, "BASE_REF", "LALT_T(KC_L)", "&hmr LALT L", "HRM ALT:L right pos 18"),
    ("hrm:LGUI:SCLN", 19, "BASE_REF", "LGUI_T(KC_SCLN)", "&hmr LGUI SEMI", "HRM GUI:; right pos 19"),
    # Additional right-hand positions
    ("hrm:LGUI:P", 9, "BASE_REF", "LGUI_T(KC_P)", "&hmr LGUI P", "HRM GUI:P right pos 9"),
    ("hrm:LALT:N", 25, "BASE_REF", "LALT_T(KC_N)", "&hmr LALT N", "HRM ALT:N right pos 25"),
    ("hrm:LCTL:ENT", 35, "BASE_REF", "LCTL_T(KC_ENT)", "&hmr LCTL ENTER", "HRM CTL:ENT thumb pos 35"),
]

# -----------------------------------------------------------------------------
# LAYER-TAP
# -----------------------------------------------------------------------------
LAYER_TAP_CASES = [
    ("lt:NAV_REF:BSPC", 30, "BASE_REF", "LT(NAV_REF, KC_BSPC)", "&lt NAV_REF BSPC", "LT NAV:BSPC"),
    ("lt:NAV_REF:SPC", 34, "BASE_REF", "LT(NAV_REF, KC_SPC)", "&lt NAV_REF SPACE", "LT NAV:SPC"),
    ("lt:NAV_REF:ENT", 35, "BASE_REF", "LT(NAV_REF, KC_ENT)", "&lt NAV_REF ENTER", "LT NAV:ENT"),
    ("lt:NAV_REF:TAB", 33, "BASE_REF", "LT(NAV_REF, KC_TAB)", "&lt NAV_REF TAB", "LT NAV:TAB"),
]

# -----------------------------------------------------------------------------
# MOD-TAP (simpler than hrm, no chordal hold)
# Note: ZMK uses LSFT (not LSHFT), LCTL (not LCTRL)
# -----------------------------------------------------------------------------
MOD_TAP_CASES = [
    ("mt:LSFT:DEL", 32, "BASE_REF", "LSFT_T(KC_DEL)", "&mt LSFT DEL", "MT SFT:DEL"),
    ("mt:LSFT:TAB", 33, "BASE_REF", "LSFT_T(KC_TAB)", "&mt LSFT TAB", "MT SFT:TAB"),
    ("mt:LCTL:ESC", 30, "BASE_REF", "LCTL_T(KC_ESC)", "&mt LCTL ESC", "MT CTL:ESC"),
    ("mt:LGUI:SPC", 34, "BASE_REF", "LGUI_T(KC_SPC)", "&mt LGUI SPACE", "MT GUI:SPC"),
    ("mt:LALT:BSPC", 31, "BASE_REF", "LALT_T(KC_BSPC)", "&mt LALT BSPC", "MT ALT:BSPC"),
]

# -----------------------------------------------------------------------------
# DEFAULT LAYER (df:)
# -----------------------------------------------------------------------------
DEFAULT_LAYER_CASES = [
    ("df:BASE_REF", 0, "NAV_REF", "DF(BASE_REF)", "&to BASE_REF", "DF BASE_REF"),
    ("df:NAV_REF", 0, "BASE_REF", "DF(NAV_REF)", "&to NAV_REF", "DF NAV_REF"),
]

# -----------------------------------------------------------------------------
# ONE-SHOT LAYER (osl:)
# -----------------------------------------------------------------------------
ONE_SHOT_LAYER_CASES = [
    ("osl:NAV_REF", 0, "BASE_REF", "OSL(NAV_REF)", "&sl NAV_REF", "OSL NAV_REF"),
    ("osl:NUM_REF", 0, "BASE_REF", "OSL(NUM_REF)", "&sl NUM_REF", "OSL NUM_REF"),
]

# -----------------------------------------------------------------------------
# SHIFT-MORPH (sm:) - QMK returns base key, ZMK returns mod-morph behavior
# -----------------------------------------------------------------------------
SHIFT_MORPH_CASES = [
    ("sm:COMM:EXLM", 24, "BASE_REF", "KC_COMM", "&sm_comm_exlm", "SM COMM->EXLM"),
    ("sm:DOT:QUES", 27, "BASE_REF", "KC_DOT", "&sm_dot_ques", "SM DOT->QUES"),
    ("sm:SLSH:BSLS", 28, "BASE_REF", "KC_SLSH", "&sm_slsh_bsls", "SM SLSH->BSLS"),
    ("sm:SCLN:COLN", 19, "BASE_REF", "KC_SCLN", "&sm_scln_coln", "SM SCLN->COLN"),
    ("sm:QUOT:DQUO", 0, "BASE_REF", "KC_QUOT", "&sm_quot_dquo", "SM QUOT->DQUO"),
]

# -----------------------------------------------------------------------------
# BLUETOOTH (bt:) - QMK filters to KC_NO, ZMK produces &bt behavior
# Note: Actual ZMK output uses lowercase (BT_clr, BT_next, BT_prev)
# -----------------------------------------------------------------------------
BLUETOOTH_CASES = [
    ("bt:clr", 20, "NAV_REF", "KC_NO", "&bt BT_clr", "BT clear"),
    ("bt:prev", 21, "NAV_REF", "KC_NO", "&bt BT_prev", "BT previous"),
    ("bt:next", 22, "NAV_REF", "KC_NO", "&bt BT_next", "BT next"),
    # Note: bt:sel:N syntax not supported - use BT_SEL_0 etc. directly
]

# -----------------------------------------------------------------------------
# MAGIC KEY
# Note: ZMK magic key is layer-aware. When no magic config is present,
# it returns &none. The actual behavior name depends on the base layer.
# -----------------------------------------------------------------------------
MAGIC_CASES = [
    # MAGIC tested separately due to layer-awareness complexity
]

# -----------------------------------------------------------------------------
# REPEAT KEY
# -----------------------------------------------------------------------------
REPEAT_CASES = [
    ("REPEAT", 0, "BASE_REF", "QK_REP", "&key_repeat", "Repeat key"),
]


# =============================================================================
# TEST CLASSES
# =============================================================================

@pytest.mark.tier1
class TestAlphaKeyParity:
    """Test alpha key translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        ALPHA_CASES,
        ids=[c[5] for c in ALPHA_CASES]
    )
    def test_alpha_keys(self, qmk_translator, zmk_translator,
                        unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestNumberKeyParity:
    """Test number key translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        NUMBER_CASES,
        ids=[c[5] for c in NUMBER_CASES]
    )
    def test_number_keys(self, qmk_translator, zmk_translator,
                         unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestSpecialKeyParity:
    """Test special key translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        SPECIAL_KEY_CASES,
        ids=[c[5] for c in SPECIAL_KEY_CASES]
    )
    def test_special_keys(self, qmk_translator, zmk_translator,
                          unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestNavigationKeyParity:
    """Test navigation key translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        NAVIGATION_CASES,
        ids=[c[5] for c in NAVIGATION_CASES]
    )
    def test_navigation_keys(self, qmk_translator, zmk_translator,
                             unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestModifierKeyParity:
    """Test modifier key translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        MODIFIER_CASES,
        ids=[c[5] for c in MODIFIER_CASES]
    )
    def test_modifier_keys(self, qmk_translator, zmk_translator,
                           unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestControlKeyParity:
    """Test control key (NONE, TRNS, DFU) translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        CONTROL_CASES,
        ids=[c[5] for c in CONTROL_CASES]
    )
    def test_control_keys(self, qmk_translator, zmk_translator,
                          unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestHomeRowModLeftParity:
    """Test home row mod translation for LEFT hand positions"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        HOME_ROW_MOD_LEFT_CASES,
        ids=[c[5] for c in HOME_ROW_MOD_LEFT_CASES]
    )
    def test_hrm_left(self, qmk_translator, zmk_translator,
                      unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestHomeRowModRightParity:
    """Test home row mod translation for RIGHT hand positions"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        HOME_ROW_MOD_RIGHT_CASES,
        ids=[c[5] for c in HOME_ROW_MOD_RIGHT_CASES]
    )
    def test_hrm_right(self, qmk_translator, zmk_translator,
                       unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestLayerTapParity:
    """Test layer-tap translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        LAYER_TAP_CASES,
        ids=[c[5] for c in LAYER_TAP_CASES]
    )
    def test_layer_tap(self, qmk_translator, zmk_translator,
                       unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestModTapParity:
    """Test mod-tap translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        MOD_TAP_CASES,
        ids=[c[5] for c in MOD_TAP_CASES]
    )
    def test_mod_tap(self, qmk_translator, zmk_translator,
                     unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestDefaultLayerParity:
    """Test default layer (df:) translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        DEFAULT_LAYER_CASES,
        ids=[c[5] for c in DEFAULT_LAYER_CASES]
    )
    def test_default_layer(self, qmk_translator, zmk_translator,
                           unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestOneShotLayerParity:
    """Test one-shot layer (osl:) translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        ONE_SHOT_LAYER_CASES,
        ids=[c[5] for c in ONE_SHOT_LAYER_CASES]
    )
    def test_one_shot_layer(self, qmk_translator, zmk_translator,
                            unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestShiftMorphParity:
    """Test shift-morph (sm:) translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        SHIFT_MORPH_CASES,
        ids=[c[5] for c in SHIFT_MORPH_CASES]
    )
    def test_shift_morph(self, qmk_translator, zmk_translator,
                         unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestBluetoothParity:
    """Test Bluetooth (bt:) translation - QMK filters to KC_NO"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        BLUETOOTH_CASES,
        ids=[c[5] for c in BLUETOOTH_CASES]
    )
    def test_bluetooth(self, qmk_translator, zmk_translator,
                       unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


@pytest.mark.tier1
class TestMagicKeyParity:
    """Test magic key translation parity"""

    def test_qmk_magic_key(self, qmk_translator):
        """MAGIC should translate to QK_AREP in QMK"""
        qmk_translator.set_context(layer="BASE_REF", position=31)
        result = qmk_translator.translate("MAGIC")
        assert result == "QK_AREP", f"QMK MAGIC: expected QK_AREP, got {result}"

    def test_zmk_magic_key(self, zmk_translator):
        """MAGIC in ZMK returns layer-aware behavior or &none if no config"""
        zmk_translator.set_context(layer="BASE_REF", position=31)
        result = zmk_translator.translate("MAGIC")
        # Without magic config, returns &none; with config, returns &ak_<layer>
        assert result == "&none" or result.startswith("&ak_"), \
            f"ZMK MAGIC: expected &none or &ak_*, got {result}"


@pytest.mark.tier1
class TestRepeatKeyParity:
    """Test repeat key translation parity"""

    @pytest.mark.parametrize(
        "unified,pos,layer,qmk_exp,zmk_exp,desc",
        REPEAT_CASES,
        ids=[c[5] for c in REPEAT_CASES]
    )
    def test_repeat_key(self, qmk_translator, zmk_translator,
                        unified, pos, layer, qmk_exp, zmk_exp, desc):
        qmk_translator.set_context(layer=layer, position=pos)
        zmk_translator.set_context(layer=layer, position=pos)

        assert qmk_translator.translate(unified) == qmk_exp, f"QMK {desc}"
        assert zmk_translator.translate(unified) == zmk_exp, f"ZMK {desc}"


# =============================================================================
# SHIFT-MORPH TRACKING TESTS
# =============================================================================

@pytest.mark.tier1
class TestShiftMorphTracking:
    """Test that shift-morphs are tracked correctly for code generation"""

    def test_qmk_tracks_shift_morphs(self, qmk_translator):
        """QMK translator should track shift-morphs for key override generation"""
        # Clear any existing state
        if hasattr(qmk_translator, 'clear_shift_morphs'):
            qmk_translator.clear_shift_morphs()

        # Translate shift-morphs
        qmk_translator.translate("sm:COMM:EXLM")
        qmk_translator.translate("sm:DOT:QUES")
        qmk_translator.translate("sm:SLSH:BSLS")

        morphs = qmk_translator.get_shift_morphs()
        assert len(morphs) >= 3, f"Should track 3 shift-morphs, got {len(morphs)}"

    def test_zmk_tracks_shift_morphs(self, zmk_translator):
        """ZMK translator should track shift-morphs for mod-morph generation"""
        # Clear any existing state
        if hasattr(zmk_translator, 'clear_shift_morphs'):
            zmk_translator.clear_shift_morphs()

        # Translate shift-morphs
        zmk_translator.translate("sm:COMM:EXLM")
        zmk_translator.translate("sm:DOT:QUES")
        zmk_translator.translate("sm:SLSH:BSLS")

        morphs = zmk_translator.get_mod_morphs()
        assert len(morphs) >= 3, f"Should track 3 mod-morphs, got {len(morphs)}"


# =============================================================================
# SUMMARY STATS
# =============================================================================

def _count_test_cases():
    """Count total test cases for documentation"""
    total = (
        len(ALPHA_CASES) +
        len(NUMBER_CASES) +
        len(SPECIAL_KEY_CASES) +
        len(NAVIGATION_CASES) +
        len(MODIFIER_CASES) +
        len(CONTROL_CASES) +
        len(HOME_ROW_MOD_LEFT_CASES) +
        len(HOME_ROW_MOD_RIGHT_CASES) +
        len(LAYER_TAP_CASES) +
        len(MOD_TAP_CASES) +
        len(DEFAULT_LAYER_CASES) +
        len(ONE_SHOT_LAYER_CASES) +
        len(SHIFT_MORPH_CASES) +
        len(BLUETOOTH_CASES) +
        len(MAGIC_CASES) +
        len(REPEAT_CASES)
    )
    return total


# When running directly, show stats
if __name__ == "__main__":
    print(f"Total parity test cases: {_count_test_cases()}")
    pytest.main([__file__, "-v"])
