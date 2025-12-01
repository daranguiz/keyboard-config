// AUTO-GENERATED - DO NOT EDIT
// Generated from config/keymap.yaml by scripts/generate.py
// Board: Lily58 Rev1
// Firmware: QMK

#include "dario.h"

// Board-specific layers (extend standard enum from dario.h)
enum {
    GAME = FUN + 1  // Continue from last standard layer
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE_NIGHT] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_B                , KC_F                , KC_L                , KC_K                , KC_Q                , KC_P                , KC_G                , KC_O                , KC_U                , KC_DOT              , KC_NO               ,
        KC_NO               , LGUI_T(KC_N)        , LALT_T(KC_S)        , LCTL_T(KC_H)        , LSFT_T(KC_T)        , KC_M                , KC_Y                , RSFT_T(KC_C)        , RCTL_T(KC_A)        , RALT_T(KC_E)        , RGUI_T(KC_I)        , KC_ENT              ,
        KC_NO               , KC_X                , KC_V                , KC_J                , KC_D                , KC_Z                , KC_NO               , KC_NO               , KC_QUOT             , KC_W                , KC_SLSH             , KC_SCLN             , KC_COMM             , KC_NO               ,
        KC_NO               , LT(MEDIA, KC_ENT)   , LT(NAV, KC_R)       , LSFT_T(KC_TAB)      , LT(SYM, KC_DEL)     , RSFT_T(KC_SPC)      , LT(NUM, KC_BSPC)    , KC_NO               
    ),
    [BASE_NIGHT_V2] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_B                , KC_F                , KC_L                , KC_K                , KC_Q                , KC_P                , KC_G                , KC_O                , KC_U                , KC_DOT              , KC_NO               ,
        KC_NO               , LGUI_T(KC_N)        , LALT_T(KC_S)        , LCTL_T(KC_H)        , LSFT_T(KC_T)        , KC_M                , KC_Y                , RSFT_T(KC_C)        , RCTL_T(KC_A)        , RALT_T(KC_E)        , RGUI_T(KC_I)        , KC_ENT              ,
        KC_NO               , KC_X                , KC_V                , KC_J                , KC_D                , KC_Z                , KC_NO               , KC_NO               , KC_QUOT             , KC_W                , KC_SLSH             , KC_MINS             , KC_COMM             , KC_NO               ,
        KC_NO               , LT(NUM_NIGHT_V2, KC_BSPC), LT(SYM_NIGHT_V2, KC_R), LSFT_T(KC_DEL)      , LSFT_T(KC_TAB)      , LT(NAV_NIGHT_V2, KC_SPC), LT(MEDIA_NIGHT_V2, KC_ENT), KC_NO               
    ),
    [BASE_COLEMAK] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_Q                , KC_W                , KC_F                , KC_P                , KC_G                , KC_J                , KC_L                , KC_U                , KC_Y                , KC_QUOT             , KC_NO               ,
        KC_NO               , LGUI_T(KC_A)        , LALT_T(KC_R)        , LCTL_T(KC_S)        , LSFT_T(KC_T)        , KC_D                , KC_H                , RSFT_T(KC_N)        , RCTL_T(KC_E)        , RALT_T(KC_I)        , RGUI_T(KC_O)        , KC_ENT              ,
        KC_NO               , KC_Z                , KC_X                , KC_C                , KC_V                , KC_B                , KC_NO               , KC_NO               , KC_K                , KC_M                , KC_COMM             , KC_DOT              , KC_SLSH             , KC_NO               ,
        KC_NO               , KC_ENT              , LT(NAV, KC_SPC)     , LT(MEDIA, KC_TAB)   , LT(SYM, KC_DEL)     , KC_LSFT             , LT(NUM, KC_BSPC)    , KC_NO               
    ),
    [NUM] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LBRC             , KC_4                , KC_5                , KC_6                , KC_RBRC             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_LCBR             , KC_SLSH             , KC_1                , KC_2                , KC_3                , KC_EQL              , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_RCBR             ,
        KC_NO               , KC_GRV              , KC_7                , KC_8                , KC_9                , KC_BSLS             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_COLN             , KC_0                , KC_MINS             , KC_NO               , KC_NO               , KC_NO               , KC_NO               
    ),
    [SYM] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LCBR             , KC_DLR              , KC_PERC             , KC_CIRC             , KC_RCBR             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_QUES             , KC_EXLM             , KC_AT               , KC_HASH             , KC_PLUS             , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_NO               ,
        KC_NO               , KC_TILD             , KC_AMPR             , KC_ASTR             , KC_COLN             , KC_PIPE             , KC_NO               , KC_NO               , QK_BOOT             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LPRN             , KC_RPRN             , KC_UNDS             , KC_NO               , KC_NO               , KC_NO               , KC_NO               
    ),
    [NAV] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_ESC              , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LGUI             , KC_LALT             , KC_LCTL             , KC_LSFT             , KC_NO               , KC_CAPS             , KC_LEFT             , KC_DOWN             , KC_UP               , KC_RGHT             , KC_NO               ,
        KC_NO               , LGUI(KC_Z)          , LGUI(KC_X)          , LGUI(KC_C)          , LGUI(KC_V)          , SGUI(KC_Z)          , KC_NO               , KC_NO               , KC_INS              , KC_HOME             , KC_PGDN             , KC_PGUP             , KC_END              , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_DEL              , KC_ENT              , KC_BSPC             , KC_NO               
    ),
    [MEDIA] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , DF(BASE_NIGHT)      , DF(BASE_NIGHT_V2)   , DF(BASE_COLEMAK)    , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LGUI             , KC_LALT             , KC_LCTL             , KC_LSFT             , KC_NO               , KC_NO               , KC_MPRV             , KC_VOLD             , KC_VOLU             , KC_MNXT             , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , QK_BOOT             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_MSTP             , KC_MPLY             , KC_MUTE             , KC_NO               
    ),
    [FUN] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_F12              , KC_F7               , KC_F8               , KC_F9               , KC_PSCR             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_F11              , KC_F4               , KC_F5               , KC_F6               , KC_SCRL             , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_NO               ,
        KC_NO               , KC_F10              , KC_F1               , KC_F2               , KC_F3               , KC_PAUS             , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_APP              , KC_SPC              , KC_TAB              , KC_NO               , KC_NO               , KC_NO               , KC_NO               
    ),
    [NUM_NIGHT_V2] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_NO               , KC_LBRC             , KC_RBRC             , KC_NO               , KC_NO               , KC_CIRC             , KC_7                , KC_8                , KC_9                , KC_PERC             , KC_NO               ,
        KC_NO               , KC_LGUI             , KC_LALT             , KC_LCTL             , KC_LSFT             , KC_PIPE             , KC_HASH             , KC_4                , KC_5                , KC_6                , KC_GRV              , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_DLR              , KC_1                , KC_2                , KC_3                , KC_TILD             , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_COLN             , KC_0                , KC_AT               , KC_NO               
    ),
    [SYM_NIGHT_V2] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_ASTR             , KC_PERC             , KC_DLR              , KC_DQUO             , KC_NO               , KC_PLUS             , KC_LT               , KC_LCBR             , KC_RCBR             , KC_GT               , KC_NO               ,
        KC_NO               , KC_LGUI             , KC_LALT             , KC_LCTL             , KC_LSFT             , KC_BSLS             , KC_EXLM             , KC_EQL              , KC_LPRN             , KC_RPRN             , KC_SCLN             , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_AMPR             , KC_NO               , KC_NO               , KC_NO               , KC_UNDS             , KC_MINS             , KC_LBRC             , KC_RBRC             , KC_COLN             , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_QUES             , KC_SPC              , KC_SLSH             , KC_NO               
    ),
    [NAV_NIGHT_V2] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_ESC              , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_LEFT             , KC_DOWN             , KC_UP               , KC_RGHT             , KC_CAPS             , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_NO               ,
        KC_NO               , KC_END              , KC_PGDN             , KC_PGUP             , KC_HOME             , KC_INS              , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_BSPC             , KC_ENT              , KC_DEL              , KC_NO               , KC_NO               , KC_NO               , KC_NO               
    ),
    [MEDIA_NIGHT_V2] = LAYOUT(
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , DF(BASE_NIGHT)      , DF(BASE_NIGHT_V2)   , DF(BASE_COLEMAK)    , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               ,
        KC_NO               , KC_MNXT             , KC_VOLU             , KC_VOLD             , KC_MPRV             , KC_NO               , KC_NO               , KC_LSFT             , KC_LCTL             , KC_LALT             , KC_LGUI             , KC_NO               ,
        KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , KC_NO               , QK_BOOT             , KC_NO               ,
        KC_NO               , KC_MUTE             , KC_MPLY             , KC_MSTP             , KC_NO               , KC_NO               , KC_NO               , KC_NO               
    ),
};
