#include "dario.h"

// Per-key tapping term configuration
uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        // Home row mods from all BASE layers: use HRM tapping term (280ms)
        // BASE_COLEMAK: LGUI/LALT/LCTL/LSFT on A/R/S/T (left), LSFT/LCTL/LALT/LGUI on N/E/I/O (right)
        case LGUI_T(KC_A):
        case LALT_T(KC_R):
        case LCTL_T(KC_S):
        case LSFT_T(KC_T):
        case LSFT_T(KC_N):
        case LCTL_T(KC_E):
        case LALT_T(KC_I):
        case LGUI_T(KC_O):
        // BASE_NIGHT: LGUI/LALT/LCTL/LSFT on N/S/H/T (left), LSFT/LCTL/LALT/LGUI on C/A/E/I (right)
        case LGUI_T(KC_N):
        case LALT_T(KC_S):
        case LCTL_T(KC_H):
        // case LSFT_T(KC_T):  // Already listed above (BASE_COLEMAK)
        case LSFT_T(KC_C):
        case LCTL_T(KC_A):
        case LALT_T(KC_E):
        case LGUI_T(KC_I):
        // BASE_DUSK: LGUI/LALT/LCTL/LSFT on N/S/T/C (left), LSFT/LCTL/LALT/LGUI on H/A/E/I (right)
        // Most keys already covered above, no additional unique combinations needed
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

// Per-key hold-on-other-key-press (hold-preferred behavior)
// Enables immediate hold activation for TAB and DEL mod-taps
bool get_hold_on_other_key_press(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        // Hold-preferred mod-taps: TAB and DEL with LSFT
        case LSFT_T(KC_TAB):
        case LSFT_T(KC_DEL):
            return true;  // Immediately select hold action when another key is pressed
        default:
            return false;  // Use default behavior for all other keys
    }
}

// Thumb-aware chordal hold: ignore thumbs so Flow Tap can resolve rolls
// while still using opposite-hand protection for main alphas.
#ifdef CHORDAL_HOLD
static bool is_thumb_keycode(uint16_t keycode) {
    switch (keycode) {
        // Thumbs on BASE_COLEMAK
        case KC_ENT:
        case LT(NAV, KC_SPC):
        case LT(MEDIA, KC_TAB):
        case LT(SYM, KC_DEL):
        case KC_LSFT:
        case LT(NUM, KC_BSPC):
        // Thumbs on BASE_NIGHT
        case LT(NUM_NIGHT, KC_BSPC):
        case LT(SYM_NIGHT, KC_R):
        case LSFT_T(KC_DEL):
        case LSFT_T(KC_TAB):
        case LT(NAV_NIGHT, KC_SPC):
        case LT(MEDIA_NIGHT, KC_ENT):
            return true;
    }
    return false;
}

static char handedness_for_keypos(keypos_t key) {
    // Simple column-based split: lower columns are left, upper are right.
    // Works across all current boards; thumbs are filtered separately above.
    return (key.col < (MATRIX_COLS / 2)) ? 'L' : 'R';
}

bool get_chordal_hold(uint16_t tap_hold_keycode, keyrecord_t *tap_hold_record, uint16_t other_keycode, keyrecord_t *other_record) {
    if (is_thumb_keycode(tap_hold_keycode) || is_thumb_keycode(other_keycode)) {
        return true;  // Never penalize holds when a thumb key is involved
    }

    const char tap_hand   = handedness_for_keypos(tap_hold_record->event.key);
    const char other_hand = handedness_for_keypos(other_record->event.key);
    return tap_hand != other_hand;
}
#endif  // CHORDAL_HOLD

// Custom keycode handler
// Clipboard keys are handled by macros in dario.h
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case MACRO_GITHUB_URL:
            if (record->event.pressed) {
                SEND_STRING("https://github.com/daranguiz/keyboard-config?tab=readme-ov-file#readme");
            }
            return false;
    }
    return true;
}
