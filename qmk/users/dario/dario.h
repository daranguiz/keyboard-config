#pragma once

#include QMK_KEYBOARD_H

// Layer definitions
// NOTE: Order must match config/keymap.yaml layer order
enum layers {
    BASE_NIGHT,
    BASE_NIGHT_V2,
    BASE_COLEMAK,
    NUM,
    SYM,
    NAV,
    MEDIA,
    FUN,
    NUM_NIGHT_V2,
    SYM_NIGHT_V2,
    NAV_NIGHT_V2,
    MEDIA_NIGHT_V2
};

// Not available/Not used keycodes
#define U_NA KC_NO  // key present but not available for use
#define U_NU KC_NO  // key available but not used
#define U_NP KC_NO  // key is not present

// RGB aliases (conditional on RGB support)
// Note: RGB_MATRIX already defines RM_* keycodes, so we only need to handle RGBLIGHT and disabled cases
#if defined(RGBLIGHT_ENABLE)
    #define RM_TOGG RGB_TOG
    #define RM_NEXT RGB_MOD
    #define RM_HUEU RGB_HUI
    #define RM_SATU RGB_SAI
    #define RM_VALU RGB_VAI
#elif !defined(RGB_MATRIX_ENABLE)
    // Only define fallbacks if RGB_MATRIX is not enabled (it defines its own RM_* codes)
    #define RM_TOGG KC_NO
    #define RM_NEXT KC_NO
    #define RM_HUEU KC_NO
    #define RM_SATU KC_NO
    #define RM_VALU KC_NO
#endif
