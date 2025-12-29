#pragma once

#include QMK_KEYBOARD_H

// Layer definitions
// NOTE: Order must match config/keymap.yaml layer order
enum layers {
    BASE_PRIMARY,
    BASE_ALT,
    BASE_ALT2,
    NUM,
    SYM,
    NAV,
    MEDIA
};

// Not available/Not used keycodes
#define U_NA KC_NO  // key present but not available for use
#define U_NU KC_NO  // key available but not used
#define U_NP KC_NO  // key is not present

// Note: Custom keycodes (combo macros, magic macros) are defined per-keymap
// in the generated keymap.c file, starting from SAFE_RANGE

// Base layer tracking for magic key context
uint8_t get_current_base_layer(void);

bool magic_process_record(uint16_t keycode, keyrecord_t *record);

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
