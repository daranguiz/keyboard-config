// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml by scripts/generate.py
// Board: Bastard Keyboards Skeletyl
// Firmware: QMK

#include "dario.h"

#ifndef MACRO_GITHUB_URL
#define MACRO_GITHUB_URL SAFE_RANGE
#endif

enum magic_macros {
    MAGIC_DUSK_CHR_32 = MACRO_GITHUB_URL + 1,
    MAGIC_DUSK_CHR_44,
    MAGIC_NIGHT_B,
    MAGIC_NIGHT_CHR_32,
    MAGIC_NIGHT_CHR_44,
    MAGIC_NIGHT_I,
    MAGIC_NIGHT_J,
    MAGIC_NIGHT_M,
    MAGIC_NIGHT_N,
    MAGIC_NIGHT_Q,
    MAGIC_NIGHT_T,
    MAGIC_NIGHT_W,
    MAGIC_RACKET_CHR_32,
    MAGIC_RACKET_CHR_44,
};


const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE_NIGHT] = LAYOUT_split_3x5_3(
        KC_B                , KC_F                , KC_L                , KC_K                , KC_Q                ,
        KC_P                , KC_G                , KC_O                , KC_U                , KC_DOT              ,
        LGUI_T(KC_N)        , LALT_T(KC_S)        , LCTL_T(KC_H)        , LSFT_T(KC_T)        , KC_M                ,
        KC_Y                , LSFT_T(KC_C)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        ,
        KC_X                , KC_V                , KC_J                , KC_D                , KC_Z                ,
        KC_QUOT             , KC_W                , KC_MINS             , KC_SCLN             , KC_COMM             ,
                              LT(NUM_NIGHT, KC_BSPC), LT(SYM_NIGHT, KC_R) , LSFT_T(QK_AREP)     ,
                              LSFT_T(KC_TAB)      , LT(NAV_NIGHT, KC_SPC), LT(MEDIA_NIGHT, KC_ENT)
    ),
    [BASE_GALLIUM] = LAYOUT_split_3x5_3(
        KC_B                , KC_L                , KC_D                , KC_C                , KC_V                ,
        KC_J                , KC_Y                , KC_O                , KC_U                , KC_DOT              ,
        LGUI_T(KC_N)        , LALT_T(KC_R)        , LCTL_T(KC_T)        , LSFT_T(KC_S)        , KC_G                ,
        KC_P                , LSFT_T(KC_H)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        ,
        KC_X                , KC_Q                , KC_M                , KC_W                , KC_Z                ,
        KC_K                , KC_F                , KC_QUOT             , KC_MINS             , KC_COMM             ,
                              LT(NUM_NIGHT, KC_BSPC), LT(SYM_NIGHT, QK_AREP), LSFT_T(KC_DEL)      ,
                              LSFT_T(KC_TAB)      , LT(NAV_NIGHT, KC_SPC), LT(MEDIA_NIGHT, KC_ENT)
    ),
    [BASE_DUSK] = LAYOUT_split_3x5_3(
        KC_B                , KC_F                , KC_D                , KC_W                , KC_P                ,
        KC_J                , KC_QUOT             , KC_O                , KC_U                , KC_COMM             ,
        LGUI_T(KC_N)        , LALT_T(KC_S)        , LCTL_T(KC_T)        , LSFT_T(KC_C)        , KC_Y                ,
        KC_M                , LSFT_T(KC_H)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        ,
        KC_X                , KC_V                , KC_K                , KC_G                , KC_Q                ,
        KC_Z                , KC_L                , KC_MINS             , KC_SLSH             , KC_DOT              ,
                              LT(NUM_NIGHT, KC_BSPC), LT(SYM_NIGHT, KC_R) , LSFT_T(QK_AREP)     ,
                              LSFT_T(KC_TAB)      , LT(NAV_NIGHT, KC_SPC), LT(MEDIA_NIGHT, KC_ENT)
    ),
    [BASE_RACKET] = LAYOUT_split_3x5_3(
        KC_F                , KC_D                , KC_L                , KC_W                , KC_J                ,
        KC_MINS             , KC_B                , KC_O                , KC_U                , KC_COMM             ,
        LGUI_T(KC_S)        , LALT_T(KC_T)        , LCTL_T(KC_H)        , LSFT_T(KC_C)        , KC_Y                ,
        KC_Q                , LSFT_T(KC_N)        , LCTL_T(KC_A)        , LALT_T(KC_E)        , LGUI_T(KC_I)        ,
        KC_X                , KC_K                , KC_M                , KC_G                , KC_V                ,
        KC_Z                , KC_P                , KC_QUOT             , KC_SLSH             , KC_DOT              ,
                              LT(NUM_NIGHT, KC_BSPC), LT(SYM_NIGHT, KC_R) , LSFT_T(QK_AREP)     ,
                              LSFT_T(KC_TAB)      , LT(NAV_NIGHT, KC_SPC), LT(MEDIA_NIGHT, KC_ENT)
    ),
    [NUM_NIGHT] = LAYOUT_split_3x5_3(
        KC_NO               , KC_TILD             , KC_PERC             , KC_COLN             , KC_NO               ,
        KC_CIRC             , KC_7                , KC_8                , KC_9                , KC_COMM             ,
        KC_LGUI             , KC_LALT             , KC_LCTL             , KC_LSFT             , KC_PIPE             ,
        KC_HASH             , KC_1                , KC_2                , KC_3                , KC_GRV              ,
        LGUI(KC_Z)          , LGUI(KC_X)          , LGUI(KC_C)          , LGUI(KC_V)          , SGUI(KC_Z)          ,
        KC_DLR              , KC_4                , KC_5                , KC_6                , KC_DOT              ,
                              KC_NO               , KC_NO               , KC_NO               ,
                              KC_SLSH             , KC_0                , KC_AT               
    ),
    [SYM_NIGHT] = LAYOUT_split_3x5_3(
        KC_DLR              , KC_ASTR             , KC_PERC             , KC_COLN             , KC_NO               ,
        KC_PLUS             , KC_MINS             , KC_LCBR             , KC_RCBR             , KC_COMM             ,
        KC_LGUI             , KC_LALT             , KC_LCTL             , KC_LSFT             , KC_EQL              ,
        KC_EXLM             , KC_QUES             , KC_LPRN             , KC_RPRN             , KC_SCLN             ,
        KC_NO               , KC_NO               , KC_NO               , KC_AMPR             , KC_NO               ,
        KC_BSLS             , KC_LT               , KC_LBRC             , KC_RBRC             , KC_GT               ,
                              KC_NO               , KC_NO               , KC_NO               ,
                              KC_SLSH             , KC_SPC              , KC_ENT              
    ),
    [NAV_NIGHT] = LAYOUT_split_3x5_3(
        KC_NO               , KC_PGUP             , KC_NO               , KC_NO               , KC_ESC              ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LEFT             , KC_UP               , KC_RGHT             , KC_CAPS             ,
        KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             ,
        KC_END              , KC_PGDN             , KC_DOWN             , KC_HOME             , KC_INS              ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
                              KC_BSPC             , KC_ENT              , KC_DEL              ,
                              KC_NO               , KC_NO               , KC_NO               
    ),
    [MEDIA_NIGHT] = LAYOUT_split_3x5_3(
        DF(BASE_NIGHT)      , DF(BASE_GALLIUM)    , DF(BASE_DUSK)       , DF(BASE_RACKET)     , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_MNXT             , KC_VOLU             , KC_VOLD             , KC_MPRV             , KC_NO               ,
        KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             ,
        LGUI(KC_Z)          , LGUI(KC_X)          , LGUI(KC_C)          , LGUI(KC_V)          , SGUI(KC_Z)          ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , QK_BOOT             ,
                              KC_MUTE             , KC_MPLY             , KC_MSTP             ,
                              KC_NO               , KC_NO               , KC_NO               
    ),
};


#ifdef COMBO_ENABLE

// Combo indices
enum combo_events {
    COMBO_DFU_LEFT,
    COMBO_DFU_RIGHT,
    COMBO_GITHUB_URL,
    COMBO_LENGTH
};

#define COMBO_COUNT COMBO_LENGTH

// Combo key sequences
const uint16_t PROGMEM dfu_left_combo[] = {KC_B, KC_Q, KC_Z, COMBO_END};
const uint16_t PROGMEM dfu_right_combo[] = {KC_P, KC_DOT, KC_QUOT, COMBO_END};
const uint16_t PROGMEM github_url_combo[] = {KC_G, KC_O, KC_U, KC_DOT, COMBO_END};

// Combo definitions
combo_t key_combos[] = {
    [COMBO_DFU_LEFT] = COMBO(dfu_left_combo, QK_BOOT),
    [COMBO_DFU_RIGHT] = COMBO(dfu_right_combo, QK_BOOT),
    [COMBO_GITHUB_URL] = COMBO(github_url_combo, MACRO_GITHUB_URL)
};



// Layer filtering
bool combo_should_trigger(uint16_t combo_index, combo_t *combo, uint16_t keycode, keyrecord_t *record) {
    uint8_t layer = get_current_base_layer();

    switch (combo_index) {
        case COMBO_DFU_LEFT:
            // Only active on BASE_NIGHT, BASE_GALLIUM, BASE_DUSK, BASE_RACKET
            return (layer == BASE_NIGHT || layer == BASE_GALLIUM || layer == BASE_DUSK || layer == BASE_RACKET);
        case COMBO_DFU_RIGHT:
            // Only active on BASE_NIGHT, BASE_GALLIUM, BASE_DUSK, BASE_RACKET
            return (layer == BASE_NIGHT || layer == BASE_GALLIUM || layer == BASE_DUSK || layer == BASE_RACKET);
        case COMBO_GITHUB_URL:
            // Only active on BASE_NIGHT, BASE_GALLIUM, BASE_DUSK, BASE_RACKET
            return (layer == BASE_NIGHT || layer == BASE_GALLIUM || layer == BASE_DUSK || layer == BASE_RACKET);
        default:
            return true;  // Other combos active on all layers
    }
}

#endif  // COMBO_ENABLE

// Magic key configuration (alternate repeat key)
uint16_t get_alt_repeat_key_keycode_user(uint16_t keycode, uint8_t mods) {
    // Get current base layer (not active overlay)
    uint8_t base_layer = get_current_base_layer();
    
    // BASE_GALLIUM family
    if (base_layer == BASE_GALLIUM) {
        switch (keycode) {
            case KC_DOT: return KC_SLSH;
            case KC_A: return KC_Y;
            case KC_B: return KC_R;
            case KC_C: return KC_S;
            case KC_E: return KC_Y;
            case KC_G: return KC_S;
            case KC_M: return KC_B;
            case KC_O: return KC_K;
            case KC_P: return KC_H;
            case KC_R: return KC_L;
            case KC_S: return KC_C;
            case KC_U: return KC_E;
            case KC_Y: return KC_E;
        }
    }

    // BASE_NIGHT family
    if (base_layer == BASE_NIGHT) {
        switch (keycode) {
            case KC_SPC: return MAGIC_NIGHT_CHR_32;
            case KC_COMM: return MAGIC_NIGHT_CHR_44;
            case KC_MINS: return KC_GT;
            case KC_DOT: return KC_SLSH;
            case KC_A: return KC_O;
            case KC_B: return MAGIC_NIGHT_B;
            case KC_C: return KC_Y;
            case KC_G: return KC_Y;
            case KC_H: return KC_L;
            case KC_I: return MAGIC_NIGHT_I;
            case KC_J: return MAGIC_NIGHT_J;
            case KC_M: return MAGIC_NIGHT_M;
            case KC_N: return MAGIC_NIGHT_N;
            case KC_P: return KC_Y;
            case KC_Q: return MAGIC_NIGHT_Q;
            case KC_T: return MAGIC_NIGHT_T;
            case KC_U: return KC_E;
            case KC_V: return KC_S;
            case KC_W: return MAGIC_NIGHT_W;
            case KC_Y: return KC_QUOT;
        }
    }

    // BASE_DUSK family
    if (base_layer == BASE_DUSK) {
        switch (keycode) {
            case KC_SPC: return MAGIC_DUSK_CHR_32;
            case KC_COMM: return MAGIC_DUSK_CHR_44;
            case KC_DOT: return KC_SLSH;
        }
    }

    // BASE_RACKET family
    if (base_layer == BASE_RACKET) {
        switch (keycode) {
            case KC_DOT: return KC_SLSH;
            case KC_SPC: return MAGIC_RACKET_CHR_32;
            case KC_COMM: return MAGIC_RACKET_CHR_44;
            case KC_MINS: return KC_GT;
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
        case MAGIC_DUSK_CHR_32:
            SEND_STRING("the");
            return false;
        case MAGIC_DUSK_CHR_44:
            SEND_STRING(" but");
            return false;
        case MAGIC_NIGHT_B:
            SEND_STRING("efore");
            return false;
        case MAGIC_NIGHT_CHR_32:
            SEND_STRING("the");
            return false;
        case MAGIC_NIGHT_CHR_44:
            SEND_STRING(" but");
            return false;
        case MAGIC_NIGHT_I:
            SEND_STRING("on");
            return false;
        case MAGIC_NIGHT_J:
            SEND_STRING("ust");
            return false;
        case MAGIC_NIGHT_M:
            SEND_STRING("ent");
            return false;
        case MAGIC_NIGHT_N:
            SEND_STRING("ion");
            return false;
        case MAGIC_NIGHT_Q:
            SEND_STRING("ue");
            return false;
        case MAGIC_NIGHT_T:
            SEND_STRING("ion");
            return false;
        case MAGIC_NIGHT_W:
            SEND_STRING("hich");
            return false;
        case MAGIC_RACKET_CHR_32:
            SEND_STRING("the");
            return false;
        case MAGIC_RACKET_CHR_44:
            SEND_STRING(" but");
            return false;
    }
    return true;
}

uint16_t magic_training_first_keycode(uint16_t keycode) {
    switch (keycode) {
        case MAGIC_DUSK_CHR_32: return KC_NO;
        case MAGIC_DUSK_CHR_44: return KC_NO;
        case MAGIC_NIGHT_B: return KC_NO;
        case MAGIC_NIGHT_CHR_32: return KC_NO;
        case MAGIC_NIGHT_CHR_44: return KC_NO;
        case MAGIC_NIGHT_I: return KC_NO;
        case MAGIC_NIGHT_J: return KC_NO;
        case MAGIC_NIGHT_M: return KC_NO;
        case MAGIC_NIGHT_N: return KC_NO;
        case MAGIC_NIGHT_Q: return KC_NO;
        case MAGIC_NIGHT_T: return KC_NO;
        case MAGIC_NIGHT_W: return KC_NO;
        case MAGIC_RACKET_CHR_32: return KC_NO;
        case MAGIC_RACKET_CHR_44: return KC_NO;
    }
    return keycode;
}
