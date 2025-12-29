#include "dario.h"
#include "quantum/repeat_key.h"

// Forward declaration: generated per-keymap for magic text expansions
bool process_magic_record(uint16_t keycode, keyrecord_t *record);
__attribute__((weak)) bool process_magic_record(uint16_t keycode, keyrecord_t *record) { return true; }

// Forward declaration: generated per-keymap for combo macro handling
bool process_combo_macros(uint16_t keycode, keyrecord_t *record);
__attribute__((weak)) bool process_combo_macros(uint16_t keycode, keyrecord_t *record) { return true; }

// Global variable to track current base layer for magic key context
static uint8_t current_base_layer = BASE_PRIMARY;  // Default starting layer

// Getter function for magic key system to query current base layer
uint8_t get_current_base_layer(void) {
    return current_base_layer;
}

// Per-key tapping term configuration
uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        // Home row mods from all BASE layers: use HRM tapping term (280ms)
        // BASE_NIGHT: LGUI/LALT/LCTL/LSFT on N/S/H/T (left), LSFT/LCTL/LALT/LGUI on C/A/E/I (right)
        case LGUI_T(KC_N):
        case LALT_T(KC_S):
        case LCTL_T(KC_H):
        case LSFT_T(KC_T):
        case LSFT_T(KC_C):
        case LCTL_T(KC_A):
        case LALT_T(KC_E):
        case LGUI_T(KC_I):
        // BASE_GALLIUM: LGUI/LALT/LCTL/LSFT on N/R/T/S (left), LSFT/LCTL/LALT/LGUI on H/A/E/I (right)
        case LALT_T(KC_R):
        // case LSFT_T(KC_T):  // Already listed above (BASE_NIGHT)
        // case LSFT_T(KC_C):  // Already listed above (BASE_NIGHT - but GALLIUM uses H here)
        case LSFT_T(KC_H):
        // case LCTL_T(KC_A):  // Already listed above (BASE_NIGHT)
        // case LALT_T(KC_E):  // Already listed above (BASE_NIGHT)
        // case LGUI_T(KC_I):  // Already listed above (BASE_NIGHT)
            return TAPPING_TERM_HRM;

        // Layer-tap keys: use standard tapping term (200ms)
        case LT(NAV, KC_SPC):
        case LT(NUM, KC_BSPC):
        case LT(NUM, QK_AREP):
        case LT(SYM, KC_R):
        case LT(MEDIA, KC_ENT):
            return 200;

        default:
            return TAPPING_TERM;
    }
}

// Per-key hold-on-other-key-press (hold-preferred behavior)
// Enables immediate hold activation for thumb mod-taps
bool get_hold_on_other_key_press(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        // Hold-preferred mod-taps: TAB/BSPC/MAGIC with LSFT
        case LSFT_T(KC_TAB):
        case LSFT_T(KC_BSPC):
        case LSFT_T(QK_AREP):
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
        // Thumbs on BASE_* layers
        case LT(NUM, KC_BSPC):
        case LT(NUM, QK_AREP):
        case LT(SYM, KC_R):
        case LSFT_T(KC_DEL):
        case LSFT_T(KC_BSPC):
        case LSFT_T(QK_AREP):
        case LSFT_T(KC_TAB):
        case LT(NAV, KC_SPC):
        case LT(MEDIA, KC_ENT):
            return true;
    }
    return false;
}

static char handedness_for_keypos(keypos_t key) {
#ifdef SPLIT_KEYBOARD
    // On split boards the row index encodes the hand (left rows first, right rows second).
    return (key.row < (MATRIX_ROWS / 2)) ? 'L' : 'R';
#else
    // For monoblock boards, fall back to a column split.
    return (key.col < (MATRIX_COLS / 2)) ? 'L' : 'R';
#endif
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
    // Track base layer changes for magic key context
    if (record->event.pressed) {
        switch (keycode) {
            case DF(BASE_PRIMARY):
                current_base_layer = BASE_PRIMARY;
                break;
            case DF(BASE_ALT):
                current_base_layer = BASE_ALT;
                break;
            case DF(BASE_ALT2):
                current_base_layer = BASE_ALT2;
                break;
        }
    }

    // Light logging for combo-related keys to see if they arrive together
    if (record->event.pressed) {
        switch (keycode) {
            case KC_B: case KC_Q: case KC_Z:
            case KC_P: case KC_DOT: case KC_QUOT:
            case KC_G: case KC_O: case KC_U:
                uprintf("combo-key %u r%u c%u t%u layer=%u\n",
                        keycode,
                        record->event.key.row,
                        record->event.key.col,
                        record->event.time,
                        get_highest_layer(layer_state));
                break;
        }
    }

    // Delegate magic/alternate repeat handling
    if (!magic_process_record(keycode, record)) {
        return false;
    }

    if (!process_magic_record(keycode, record)) {
        return false;
    }

    // Delegate combo macro handling (generated per-keymap)
    if (!process_combo_macros(keycode, record)) {
        return false;
    }

    return true;
}

// Combo debug logging: prints combo index + press/release to QMK console
void process_combo_event(uint16_t combo_index, bool pressed) {
    uprintf("combo %u %s layer=%u state=%lu\n",
            combo_index,
            pressed ? "down" : "up",
            get_highest_layer(layer_state),
            (unsigned long)layer_state);
}
