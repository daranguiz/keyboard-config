#pragma once

#include QMK_KEYBOARD_H

// Layer definitions
enum layers {
    BASE,
    NAV,
    MOUSE,
    MEDIA,
    NUM,
    SYM,
    FUN,
    BUTTON
};

// Not available/Not used keycodes
#define U_NA KC_NO  // key present but not available for use
#define U_NU KC_NO  // key available but not used
#define U_NP KC_NO  // key is not present

// Clipboard keycodes (Mac-specific)
#define U_UND LCMD(KC_Z)  // Undo
#define U_RDO SCMD(KC_Z)  // Redo
#define U_CUT LCMD(KC_X)  // Cut
#define U_CPY LCMD(KC_C)  // Copy
#define U_PST LCMD(KC_V)  // Paste

// Mouse key placeholders (mouse keys not used)
#define MS_LEFT KC_NO
#define MS_DOWN KC_NO
#define MS_UP   KC_NO
#define MS_RGHT KC_NO

// Mouse wheel placeholders
#define MS_WHLL KC_NO
#define MS_WHLD KC_NO
#define MS_WHLU KC_NO
#define MS_WHLR KC_NO

// Mouse button placeholders
#define MS_BTN1 KC_NO
#define MS_BTN2 KC_NO
#define MS_BTN3 KC_NO

// RGB aliases (conditional on RGB support)
#if defined(RGBLIGHT_ENABLE) || defined(RGB_MATRIX_ENABLE)
    #define RM_TOGG RGB_TOG
    #define RM_NEXT RGB_MOD
    #define RM_HUEU RGB_HUI
    #define RM_SATU RGB_SAI
    #define RM_VALU RGB_VAI
#else
    #define RM_TOGG KC_NO
    #define RM_NEXT KC_NO
    #define RM_HUEU KC_NO
    #define RM_SATU KC_NO
    #define RM_VALU KC_NO
#endif
