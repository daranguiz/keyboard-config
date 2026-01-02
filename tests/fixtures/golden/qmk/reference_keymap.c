// AUTO-GENERATED - DO NOT EDIT
// Reference keymap for parity testing
// Source: tests/fixtures/configs/reference_keymap.yaml

#include QMK_KEYBOARD_H
#include "dario.h"

// =============================================================================
// SHIFT-MORPH KEY OVERRIDES
// =============================================================================
const key_override_t sm_comm_exlm_override = ko_make_basic(MOD_MASK_SHIFT, KC_COMM, KC_EXLM);
const key_override_t sm_dot_ques_override = ko_make_basic(MOD_MASK_SHIFT, KC_DOT, KC_QUES);
const key_override_t sm_slsh_bsls_override = ko_make_basic(MOD_MASK_SHIFT, KC_SLSH, KC_BSLS);

const key_override_t *key_overrides[] = {
    &sm_comm_exlm_override,
    &sm_dot_ques_override,
    &sm_slsh_bsls_override,
    NULL
};

// =============================================================================
// COMBOS
// =============================================================================
enum combos {
    REF_COMBO_ESC,
    REF_COMBO_CAPS,
    COMBO_LENGTH
};

const uint16_t PROGMEM ref_combo_esc_keys[] = {KC_Q, KC_W, COMBO_END};
const uint16_t PROGMEM ref_combo_caps_keys[] = {LSFT_T(KC_F), LSFT_T(KC_J), COMBO_END};

combo_t key_combos[] = {
    [REF_COMBO_ESC] = COMBO(ref_combo_esc_keys, KC_ESC),
    [REF_COMBO_CAPS] = COMBO(ref_combo_caps_keys, KC_CAPS),
};

// =============================================================================
// KEYMAP LAYERS
// =============================================================================
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    // =========================================================================
    // BASE_REF: Main reference layer with all behavior types
    // =========================================================================
    [BASE_REF] = LAYOUT_split_3x5_3(
        // Row 0: Simple alpha keys
        KC_Q,           KC_W,           KC_E,           KC_R,           KC_T,
        KC_Y,           KC_U,           KC_I,           KC_O,           KC_P,
        // Row 1: Home row mods (left and right)
        LGUI_T(KC_A),   LALT_T(KC_S),   LCTL_T(KC_D),   LSFT_T(KC_F),   KC_G,
        KC_H,           LSFT_T(KC_J),   LCTL_T(KC_K),   LALT_T(KC_L),   LGUI_T(KC_SCLN),
        // Row 2: Simple keys + shift-morph
        KC_Z,           KC_X,           KC_C,           KC_V,           KC_COMM,
        KC_N,           KC_M,           KC_DOT,         KC_SLSH,        KC_MINS,
        // Thumbs: layer-tap, magic, mod-tap
        LT(NAV_REF, KC_BSPC), QK_AREP, LSFT_T(KC_DEL),
        LSFT_T(KC_TAB), LT(NAV_REF, KC_SPC), KC_ENT
    ),

    // =========================================================================
    // NAV_REF: Navigation layer with df:, bt:, arrows
    // =========================================================================
    [NAV_REF] = LAYOUT_split_3x5_3(
        // Row 0: df: at position 0
        DF(BASE_REF),   KC_NO,          KC_NO,          KC_NO,          KC_NO,
        KC_NO,          KC_NO,          KC_UP,          KC_NO,          QK_BOOT,
        // Row 1: Pure modifiers
        KC_LGUI,        KC_LALT,        KC_LCTL,        KC_LSFT,        KC_NO,
        KC_NO,          KC_LEFT,        KC_DOWN,        KC_RGHT,        KC_NO,
        // Row 2: Bluetooth (filtered to KC_NO for QMK)
        KC_NO,          KC_NO,          KC_NO,          KC_NO,          KC_NO,
        KC_NO,          KC_HOME,        KC_PGDN,        KC_PGUP,        KC_END,
        // Thumbs: Transparent
        KC_TRNS,        KC_TRNS,        KC_TRNS,
        KC_TRNS,        KC_TRNS,        KC_TRNS
    ),
};

// =============================================================================
// MAGIC KEY (Alternate Repeat)
// =============================================================================
uint16_t get_alt_repeat_key_keycode_user(uint16_t keycode, uint8_t mods) {
    switch (keycode) {
        case KC_SPC:  return MAGIC_STRING_THE;   // Space -> "THE"
        case KC_COMM: return MAGIC_STRING_BUT;   // Comma -> " BUT"
        case KC_DOT:  return KC_SLSH;            // Period -> /
    }
    return KC_TRNS;  // Default: repeat
}
