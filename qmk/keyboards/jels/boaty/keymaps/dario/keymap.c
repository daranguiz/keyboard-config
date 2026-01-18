// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml by scripts/generate.py
// Board: Jels Boaty
// Firmware: QMK

#include "dario.h"

enum magic_macros {
    MACRO_GITHUB_URL = SAFE_RANGE,
    MACRO_HT_TO_LM,
    MACRO_STH_TO_LLM,
    MACRO_CAE_TO_CYC,
    MAGIC_ALT2_CHR_32,
    MAGIC_ALT2_CHR_44,
    MAGIC_ALT_CHR_32,
    MAGIC_ALT_CHR_44,
    MAGIC_PRIMARY_CHR_32,
    MAGIC_PRIMARY_CHR_44,
};


const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE_PRIMARY] = LAYOUT(
        KC_PMNS             , KC_PSLS             , KC_PAST             , KC_P7               , KC_P8               , KC_P9               , KC_P4               , KC_P5               , KC_P6               , KC_PPLS             , KC_P1               , KC_P2               ,
        KC_P3               , KC_PENT             , KC_NUM_LOCK         , KC_P0               , KC_P0               , KC_PDOT             , KC_PENT             , KC_PEQL             , KC_BSPC             , KC_ESC              , KC_TAB              , KC_B                ,
        KC_F                , KC_L                , KC_K                , KC_Q                , KC_P                , KC_G                , KC_O                , KC_U                , KC_DOT              , KC_BSPC             , KC_DEL              , KC_CAPS             ,
        LGUI_T(KC_N)        , LALT_T(KC_S)        , LCTL_T(KC_H)        , LSFT_T(KC_T)        , KC_M                , KC_Y                , LSFT_T(KC_C)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        , KC_ENT              , KC_X                , KC_V                , KC_J                ,
        KC_D                , KC_Z                , KC_QUOT             , KC_W                , KC_MINS             , KC_SLSH             , KC_COMM             , LT(NUM, QK_AREP)    , LT(SYM, KC_R)       , LSFT_T(KC_BSPC)     , LSFT_T(KC_TAB)      , LT(NAV, KC_SPC)     , LT(MEDIA, KC_ENT)   
    ),
    [BASE_ALT] = LAYOUT(
        KC_PMNS             , KC_PSLS             , KC_PAST             , KC_P7               , KC_P8               , KC_P9               , KC_P4               , KC_P5               , KC_P6               , KC_PPLS             , KC_P1               , KC_P2               ,
        KC_P3               , KC_PENT             , KC_NUM_LOCK         , KC_P0               , KC_P0               , KC_PDOT             , KC_PENT             , KC_PEQL             , KC_BSPC             , KC_ESC              , KC_TAB              , KC_F                ,
        KC_D                , KC_L                , KC_W                , KC_J                , KC_MINS             , KC_B                , KC_O                , KC_U                , KC_DOT              , KC_BSPC             , KC_DEL              , KC_CAPS             ,
        LGUI_T(KC_S)        , LALT_T(KC_T)        , LCTL_T(KC_H)        , LSFT_T(KC_C)        , KC_Y                , KC_Q                , LSFT_T(KC_N)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        , KC_ENT              , KC_X                , KC_K                , KC_M                ,
        KC_G                , KC_V                , KC_Z                , KC_P                , KC_QUOT             , KC_SLSH             , KC_COMM             , LT(NUM, QK_AREP)    , LT(SYM, KC_R)       , LSFT_T(KC_BSPC)     , LSFT_T(KC_TAB)      , LT(NAV, KC_SPC)     , LT(MEDIA, KC_ENT)   
    ),
    [BASE_ALT2] = LAYOUT(
        KC_PMNS             , KC_PSLS             , KC_PAST             , KC_P7               , KC_P8               , KC_P9               , KC_P4               , KC_P5               , KC_P6               , KC_PPLS             , KC_P1               , KC_P2               ,
        KC_P3               , KC_PENT             , KC_NUM_LOCK         , KC_P0               , KC_P0               , KC_PDOT             , KC_PENT             , KC_PEQL             , KC_BSPC             , KC_ESC              , KC_TAB              , KC_B                ,
        KC_L                , KC_M                , KC_C                , KC_Z                , KC_J                , KC_F                , KC_O                , KC_U                , KC_DOT              , KC_BSPC             , KC_DEL              , KC_CAPS             ,
        LGUI_T(KC_N)        , LALT_T(KC_R)        , LCTL_T(KC_T)        , LSFT_T(KC_D)        , KC_P                , KC_Y                , LSFT_T(KC_H)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        , KC_ENT              , KC_X                , KC_Q                , KC_V                ,
        KC_G                , KC_W                , KC_QUOT             , KC_K                , KC_MINS             , KC_SLSH             , KC_COMM             , LT(NUM, QK_AREP)    , LT(SYM, KC_S)       , LSFT_T(KC_BSPC)     , LSFT_T(KC_TAB)      , LT(NAV, KC_SPC)     , LT(MEDIA, KC_ENT)   
    ),
    [SYM] = LAYOUT(
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_AMPR             ,
        KC_PERC             , KC_DLR              , OSL(NUM)            , KC_NO               , KC_HASH             , KC_PLUS             , KC_LCBR             , KC_RCBR             , KC_EQL              , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        LGUI_T(KC_LABK)     , LALT_T(KC_RABK)     , LCTL_T(KC_LBRC)     , LSFT_T(KC_RBRC)     , KC_NO               , KC_SCLN             , KC_EXLM             , KC_LPRN             , KC_RPRN             , KC_COLN             , KC_TRNS             , KC_CIRC             , KC_PIPE             , KC_TILD             ,
        KC_BSLS             , KC_NO               , KC_DQUO             , KC_ASTR             , KC_UNDS             , KC_QUES             , KC_COMM             , KC_NO               , KC_NO               , KC_NO               , QK_AREP             , KC_SPC              , KC_ENT              
    ),
    [NUM] = LAYOUT(
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_AMPR             ,
        KC_PERC             , KC_DLR              , OSL(SYM_SHADOW)     , KC_NO               , KC_HASH             , KC_7                , KC_8                , KC_9                , KC_DOT              , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        LGUI_T(KC_LABK)     , LALT_T(KC_RABK)     , LCTL_T(KC_LBRC)     , LSFT_T(KC_RBRC)     , KC_NO               , KC_SCLN             , KC_1                , KC_2                , KC_3                , KC_0                , KC_TRNS             , LGUI(KC_Z)          , LGUI(KC_X)          , LGUI(KC_C)          ,
        LGUI(KC_V)          , SGUI(KC_Z)          , KC_DQUO             , KC_4                , KC_5                , KC_6                , KC_COMM             , KC_NO               , KC_NO               , KC_NO               , QK_AREP             , KC_SPC              , KC_ENT              
    ),
    [NAV] = LAYOUT(
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_NO               ,
        KC_PGUP             , KC_NO               , CW_TOGG             , KC_ESC              , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_NO               , KC_LEFT             , KC_UP               , KC_RGHT             , KC_CAPS             , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_TRNS             , KC_END              , KC_PGDN             , KC_DOWN             ,
        KC_HOME             , KC_INS              , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_DEL              , KC_ENT              , KC_BSPC             , KC_NO               , KC_NO               , KC_NO               
    ),
    [MEDIA] = LAYOUT(
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , DF(BASE_PRIMARY)    ,
        DF(BASE_ALT)        , DF(BASE_ALT2)       , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_MNXT             , KC_VOLU             , KC_VOLD             , KC_MPRV             , KC_NO               , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_TRNS             , LGUI(KC_Z)          , LGUI(KC_X)          , LGUI(KC_C)          ,
        LGUI(KC_V)          , SGUI(KC_Z)          , KC_NO               , KC_NO               , KC_NO               , KC_NO               , QK_BOOT             , KC_MUTE             , KC_MPLY             , KC_MSTP             , KC_NO               , KC_NO               , KC_NO               
    ),
    [SYM_SHADOW] = LAYOUT(
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_TRNS             , KC_AMPR             ,
        KC_PERC             , KC_DLR              , OSL(NUM)            , KC_NO               , KC_HASH             , KC_PLUS             , KC_LCBR             , KC_RCBR             , KC_EQL              , KC_TRNS             , KC_TRNS             , KC_TRNS             ,
        LGUI_T(KC_LABK)     , LALT_T(KC_RABK)     , LCTL_T(KC_LBRC)     , LSFT_T(KC_RBRC)     , KC_NO               , KC_SCLN             , KC_EXLM             , KC_LPRN             , KC_RPRN             , KC_COLN             , KC_TRNS             , KC_CIRC             , KC_PIPE             , KC_TILD             ,
        KC_BSLS             , KC_NO               , KC_DQUO             , KC_ASTR             , KC_UNDS             , KC_QUES             , KC_COMM             , KC_NO               , KC_NO               , KC_NO               , QK_AREP             , KC_SPC              , KC_ENT              
    ),
};


#ifdef COMBO_ENABLE

// Combo indices
enum combo_events {
    COMBO_DFU_LEFT,
    COMBO_DFU_RIGHT,
    COMBO_GITHUB_URL,
    COMBO_HT_TO_LM,
    COMBO_STH_TO_LLM,
    COMBO_CAE_TO_CYC,
    COMBO_LENGTH
};

#define COMBO_COUNT COMBO_LENGTH

// Combo key sequences
const uint16_t PROGMEM dfu_left_combo[] = {KC_B, KC_Q, KC_Z, COMBO_END};
const uint16_t PROGMEM dfu_right_combo[] = {KC_P, KC_DOT, KC_QUOT, COMBO_END};
const uint16_t PROGMEM github_url_combo[] = {KC_G, KC_O, KC_U, KC_DOT, COMBO_END};
const uint16_t PROGMEM ht_to_lm_combo[] = {LCTL_T(KC_H), LSFT_T(KC_T), COMBO_END};
const uint16_t PROGMEM sth_to_llm_combo[] = {LALT_T(KC_S), LCTL_T(KC_H), LSFT_T(KC_T), COMBO_END};
const uint16_t PROGMEM cae_to_cyc_combo[] = {LSFT_T(KC_C), LCTL_T(KC_A), LALT_T(KC_E), COMBO_END};

// Combo definitions
combo_t key_combos[] = {
    [COMBO_DFU_LEFT] = COMBO(dfu_left_combo, QK_BOOT),
    [COMBO_DFU_RIGHT] = COMBO(dfu_right_combo, QK_BOOT),
    [COMBO_GITHUB_URL] = COMBO(github_url_combo, MACRO_GITHUB_URL),
    [COMBO_HT_TO_LM] = COMBO(ht_to_lm_combo, MACRO_HT_TO_LM),
    [COMBO_STH_TO_LLM] = COMBO(sth_to_llm_combo, MACRO_STH_TO_LLM),
    [COMBO_CAE_TO_CYC] = COMBO(cae_to_cyc_combo, MACRO_CAE_TO_CYC)
};



// Layer filtering
bool combo_should_trigger(uint16_t combo_index, combo_t *combo, uint16_t keycode, keyrecord_t *record) {
    uint8_t layer = get_current_base_layer();

    switch (combo_index) {
        case COMBO_DFU_LEFT:
            // Only active on BASE_PRIMARY, BASE_ALT, BASE_ALT2
            return (layer == BASE_PRIMARY || layer == BASE_ALT || layer == BASE_ALT2);
        case COMBO_DFU_RIGHT:
            // Only active on BASE_PRIMARY, BASE_ALT, BASE_ALT2
            return (layer == BASE_PRIMARY || layer == BASE_ALT || layer == BASE_ALT2);
        case COMBO_GITHUB_URL:
            // Only active on BASE_PRIMARY, BASE_ALT, BASE_ALT2
            return (layer == BASE_PRIMARY || layer == BASE_ALT || layer == BASE_ALT2);
        case COMBO_HT_TO_LM:
            // Only active on BASE_PRIMARY
            return (layer == BASE_PRIMARY);
        case COMBO_STH_TO_LLM:
            // Only active on BASE_PRIMARY
            return (layer == BASE_PRIMARY);
        case COMBO_CAE_TO_CYC:
            // Only active on BASE_PRIMARY
            return (layer == BASE_PRIMARY);
        default:
            return true;  // Other combos active on all layers
    }
}


// Combo macro handlers
bool process_combo_macros(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case MACRO_GITHUB_URL:
            if (record->event.pressed) {
                SEND_STRING("https://github.com/daranguiz/keyboard-config?tab=readme-ov-file#readme");
            }
            return false;
        case MACRO_HT_TO_LM:
            if (record->event.pressed) {
                SEND_STRING("lm");
            }
            return false;
        case MACRO_STH_TO_LLM:
            if (record->event.pressed) {
                SEND_STRING("llm");
            }
            return false;
        case MACRO_CAE_TO_CYC:
            if (record->event.pressed) {
                SEND_STRING("cyc");
            }
            return false;
        default:
            return true;
    }
}

#endif  // COMBO_ENABLE

// Magic key configuration (alternate repeat key)
uint16_t get_alt_repeat_key_keycode_user(uint16_t keycode, uint8_t mods) {
    // Get current base layer (not active overlay)
    uint8_t base_layer = get_current_base_layer();
    
    // BASE_PRIMARY family
    if (base_layer == BASE_PRIMARY) {
        switch (keycode) {
            case KC_SPC: return MAGIC_PRIMARY_CHR_32;
            case KC_COMM: return MAGIC_PRIMARY_CHR_44;
            case KC_MINS: return KC_GT;
            case KC_DOT: return KC_SLSH;
            case KC_C: return KC_Y;
            case KC_G: return KC_Y;
            case KC_P: return KC_Y;
            case KC_SLSH: return KC_ASTR;
            case KC_ASTR: return KC_SLSH;
        }
    }

    // BASE_ALT family
    if (base_layer == BASE_ALT) {
        switch (keycode) {
            case KC_SPC: return MAGIC_ALT_CHR_32;
            case KC_COMM: return MAGIC_ALT_CHR_44;
            case KC_MINS: return KC_GT;
            case KC_DOT: return KC_SLSH;
            case KC_SLSH: return KC_ASTR;
            case KC_ASTR: return KC_SLSH;
        }
    }

    // BASE_ALT2 family
    if (base_layer == BASE_ALT2) {
        switch (keycode) {
            case KC_SPC: return MAGIC_ALT2_CHR_32;
            case KC_COMM: return MAGIC_ALT2_CHR_44;
            case KC_MINS: return KC_GT;
            case KC_DOT: return KC_SLSH;
            case KC_SLSH: return KC_ASTR;
            case KC_ASTR: return KC_SLSH;
        }
    }

    // Default: repeat previous key
    return QK_REP;
}


bool process_magic_record(uint16_t keycode, keyrecord_t *record) {
    if (!record->event.pressed) {
        return true;
    }
    switch (keycode) {
        case MAGIC_ALT2_CHR_32:
            SEND_STRING("the");
            return false;
        case MAGIC_ALT2_CHR_44:
            SEND_STRING(" but");
            return false;
        case MAGIC_ALT_CHR_32:
            SEND_STRING("the");
            return false;
        case MAGIC_ALT_CHR_44:
            SEND_STRING(" but");
            return false;
        case MAGIC_PRIMARY_CHR_32:
            SEND_STRING("the");
            return false;
        case MAGIC_PRIMARY_CHR_44:
            SEND_STRING(" but");
            return false;
    }
    return true;
}

uint16_t magic_training_first_keycode(uint16_t keycode) {
    switch (keycode) {
        case MAGIC_ALT2_CHR_32: return KC_NO;
        case MAGIC_ALT2_CHR_44: return KC_NO;
        case MAGIC_ALT_CHR_32: return KC_NO;
        case MAGIC_ALT_CHR_44: return KC_NO;
        case MAGIC_PRIMARY_CHR_32: return KC_NO;
        case MAGIC_PRIMARY_CHR_44: return KC_NO;
    }
    return keycode;
}

// Combo training check (no trainable combos)
bool combo_training_check(uint16_t prev_kc, uint16_t curr_kc) {
    return false;
}


#ifdef KEY_OVERRIDE_ENABLE
// Shift-morph key overrides (sm: syntax)
// These override the default shifted behavior of keys
const key_override_t sm_dot_grv = ko_make_basic(MOD_MASK_SHIFT, KC_DOT, KC_GRV);
const key_override_t sm_comm_at = ko_make_basic(MOD_MASK_SHIFT, KC_COMM, KC_AT);

const key_override_t *key_overrides[] = {
    &sm_dot_grv,
    &sm_comm_at,
    NULL
};
#endif  // KEY_OVERRIDE_ENABLE
