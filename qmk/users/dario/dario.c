#include "dario.h"

// Permissive hold for layer-tap keys
bool get_permissive_hold(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case LT(NAV, KC_SPC):
        case LT(NUM, KC_BSPC):
        case LT(SYM, KC_DEL):
            return true;
        default:
            return false;
    }
}

// Custom keycode handler
// Clipboard keys are handled by macros in dario.h
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    // Add custom keycode handling here as needed
    return true;
}
