#include "dario.h"

// Per-key tapping term configuration
uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        // Home row mods from all BASE layers: use HRM tapping term (280ms)
        // BASE_COLEMAK: LGUI/LALT/LCTL/LSFT on A/R/S/T (left), RSFT/RCTL/RALT/RGUI on N/E/I/O (right)
        case LGUI_T(KC_A):
        case LALT_T(KC_R):
        case LCTL_T(KC_S):
        case LSFT_T(KC_T):
        case RSFT_T(KC_N):
        case RCTL_T(KC_E):
        case RALT_T(KC_I):
        case RGUI_T(KC_O):
        // BASE_NIGHT: LGUI/LALT/LCTL/LSFT on N/S/H/T (left), RSFT/RCTL/RALT/RGUI on C/A/E/I (right)
        case LGUI_T(KC_N):
        case LALT_T(KC_S):
        case LCTL_T(KC_H):
        // case LSFT_T(KC_T):  // Already listed above (BASE_COLEMAK)
        case RSFT_T(KC_C):
        case RCTL_T(KC_A):
        case RALT_T(KC_E): 
        case RGUI_T(KC_I):  
            return TAPPING_TERM_HRM;

        // Layer-tap keys: use standard tapping term (200ms)
        case LT(NAV, KC_SPC):
        case LT(NUM, KC_BSPC):
        case LT(SYM, KC_DEL):
        case LT(MEDIA, KC_ENT):
        case LT(NAV_NIGHT, KC_SPC):
        case LT(NUM_NIGHT, KC_BSPC):
        case LT(SYM_NIGHT, KC_DEL):
        case LT(MEDIA_NIGHT, KC_ENT):
            return 200;

        default:
            return TAPPING_TERM;
    }
}

// Chordal hold (hold on other key press) configuration
// Enable for home row mods (hrm:), disable for thumb shift mod-taps (mt:LSFT)
bool get_hold_on_other_key_press(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        // Home row mods from all BASE layers: enable chordal hold (opposite hand rule)
        // BASE_COLEMAK: LGUI/LALT/LCTL/LSFT on A/R/S/T (left), RSFT/RCTL/RALT/RGUI on N/E/I/O (right)
        case LGUI_T(KC_A):
        case LALT_T(KC_R):
        case LCTL_T(KC_S):
        case LSFT_T(KC_T):
        case RSFT_T(KC_N):
        case RCTL_T(KC_E):
        case RALT_T(KC_I):
        case RGUI_T(KC_O):
        // BASE_NIGHT: LGUI/LALT/LCTL/LSFT on N/S/H/T (left), RSFT/RCTL/RALT/RGUI on C/A/E/I (right)
        case LGUI_T(KC_N):
        case LALT_T(KC_S):
        case LCTL_T(KC_H):
        // case LSFT_T(KC_T):  // Already listed above (BASE_COLEMAK)
        case RSFT_T(KC_C):
        case RCTL_T(KC_A):
        case RALT_T(KC_E):  
        case RGUI_T(KC_I):  
            return true;  // Enable chordal hold for home row mods

        // Thumb shift mod-taps: disable chordal hold (use standard behavior)
        case LSFT_T(KC_TAB):
        case LSFT_T(KC_DEL):
            return false;  // Disable chordal hold for thumb shift keys

        default:
            return false;  // Disable for everything else
    }
}

// Custom keycode handler
// Clipboard keys are handled by macros in dario.h
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    // Add custom keycode handling here as needed
    return true;
}
