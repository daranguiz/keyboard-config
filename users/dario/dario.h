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

// Mouse movement aliases
#define MS_LEFT KC_MS_LEFT
#define MS_DOWN KC_MS_DOWN
#define MS_UP   KC_MS_UP
#define MS_RGHT KC_MS_RIGHT

// Mouse wheel aliases
#define MS_WHLL KC_MS_WH_LEFT
#define MS_WHLD KC_MS_WH_DOWN
#define MS_WHLU KC_MS_WH_UP
#define MS_WHLR KC_MS_WH_RIGHT

// Mouse button aliases
#define MS_BTN1 KC_MS_BTN1
#define MS_BTN2 KC_MS_BTN2
#define MS_BTN3 KC_MS_BTN3

// RGB aliases
#define RM_TOGG RGB_TOG
#define RM_NEXT RGB_MOD
#define RM_HUEU RGB_HUI
#define RM_SATU RGB_SAI
#define RM_VALU RGB_VAI
