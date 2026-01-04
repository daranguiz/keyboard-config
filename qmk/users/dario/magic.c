#include "dario.h"
#include "quantum/repeat_key.h"
#include "print.h"
#include "action_layer.h"
#include "quantum/quantum_keycodes.h"

// Forward declaration generated in keymap.c (magic macros/text expansions)
extern bool process_magic_record(uint16_t keycode, keyrecord_t *record);

// Training helper generated in keymap.c (maps magic macro to its first key)
__attribute__((weak)) uint16_t magic_training_first_keycode(uint16_t keycode) { return keycode; }

// Combo training helper generated in keymap.c (checks if prev+curr matches combo output bigram)
__attribute__((weak)) bool combo_training_check(uint16_t prev_kc, uint16_t curr_kc) { return false; }

#define MAGIC_LOG(...) uprintf(__VA_ARGS__)

// Track previous tapped key for training (independent of QK_REP tracking)
static uint16_t training_prev_key = KC_NO;
static uint8_t training_prev_mods = 0;

static void magic_debug_banner(void) {
    static bool shown = false;
    if (!shown) {
        MAGIC_LOG("MAGIC_DEBUG ON\n");
        shown = true;
    }
}

static uint16_t unwrap_tap_keycode(uint16_t keycode) {
    if (IS_QK_MOD_TAP(keycode)) {
        uint16_t tap = QK_MOD_TAP_GET_TAP_KEYCODE(keycode);
        // QK_AREP doesn't fit in the mod-tap tap field; it truncates to 0x7A.
        if (tap == 0x7A) {
            return QK_AREP;
        }
        return tap;
    }
    if (IS_QK_LAYER_TAP(keycode)) {
        uint16_t tap = QK_LAYER_TAP_GET_TAP_KEYCODE(keycode);
        // QK_AREP (0x7C05) doesn't fit in layer-tap's 8-bit tap field; it truncates.
        // Check for the truncated value (QK_AREP & 0xFF).
        // NOTE: This may incorrectly match LT(x, KC_B) if the truncated value
        // collides with KC_B. Verify keymap doesn't have LT with that base key.
        if (tap == (QK_AREP & 0xFF)) {
            return QK_AREP;
        }
        return tap;
    }
    return keycode;
}

static bool is_magic_tap_action(uint16_t keycode, keyrecord_t *record) {
    if (IS_QK_MOD_TAP(keycode) || IS_QK_LAYER_TAP(keycode)) {
        return record->tap.count > 0 && !record->tap.interrupted;
    }
    return true;
}

// Core handler for alternate repeat tap (magic) key
static bool handle_magic_tap(uint16_t keycode, keyrecord_t *record) {
    MAGIC_LOG("AREP trigger raw=%u tap=%u layer=%u\n",
              keycode,
              unwrap_tap_keycode(keycode),
              get_highest_layer(layer_state));

    uint16_t last_key = unwrap_tap_keycode(get_last_keycode());
    const uint8_t last_mods = get_last_mods();
    const uint16_t alt = get_alt_repeat_key_keycode_user(last_key, last_mods);

    MAGIC_LOG("AREP key=%u layer=%u last=%u mods=%u alt=%u\n",
              keycode,
              get_highest_layer(layer_state),
              last_key,
              last_mods,
              alt);

    // If the alternate is one of our magic macros/text-expansions, let keymap.c handle it
    keyrecord_t fake = *record;
    fake.event.pressed = true;
    if (!process_magic_record(alt, &fake)) {
        MAGIC_LOG("AREP alt macro consumed\n");
        return false;
    }

    // Default repeat fallback: if no mapping, repeat the last key
    if (alt == QK_REP) {
        MAGIC_LOG("AREP default repeat key=%u mods=%u\n", last_key, last_mods);
        tap_code16(last_key);
        return false;
    }

    // Otherwise send the alternate keycode directly; rely on current mods already active
    MAGIC_LOG("AREP tapping alt=%u\n", alt);
    tap_code16(alt);
    return false;
}

// Prevent repeat keys from overwriting the remembered "last key"
bool get_repeat_key_eligible_user(uint16_t keycode, keyrecord_t *record, uint8_t *remembered_mods) {
    magic_debug_banner();
    uint16_t tap = unwrap_tap_keycode(keycode);
    switch (keycode) {
        case QK_REP:
        case QK_AREP:
            return false;
        default:
            if (tap == QK_AREP) {
                return false;
            }
            return true;
    }
}

// Log the last key remembered by repeat key (when MAGIC_DEBUG is enabled)
bool remember_last_key_user(uint16_t keycode, keyrecord_t *record, uint8_t *remembered_mods) {
    magic_debug_banner();
    uint16_t tap = unwrap_tap_keycode(keycode);
    if (tap == QK_AREP) {
        MAGIC_LOG("REMEMBER skip magic key=%u raw=%u layer=%u\n",
                  tap,
                  keycode,
                  get_highest_layer(layer_state));
        return false;
    }
    MAGIC_LOG("REMEMBER key=%u mods=%u layer=%u\n",
              tap,
              *remembered_mods,
              get_highest_layer(layer_state));
    return true;  // keep default remember logic
}

bool magic_process_record(uint16_t keycode, keyrecord_t *record) {
    magic_debug_banner();

    uint16_t tap = unwrap_tap_keycode(keycode);
    const bool is_magic_mod_tap = IS_QK_MOD_TAP(keycode) && tap == QK_AREP;
    const bool is_magic_layer_tap = IS_QK_LAYER_TAP(keycode) && tap == QK_AREP;

    // Training mode: if the previous key would trigger a magic alternate that
    // matches this key, emit '#' instead to encourage using MAGIC.
    // Note: get_alt_repeat_key_keycode_user uses base layer tracking internally
    if (record->event.pressed && tap != QK_AREP && tap != QK_REP && is_magic_tap_action(keycode, record)) {
        uint16_t last_key = unwrap_tap_keycode(training_prev_key);
        uint16_t alt = get_alt_repeat_key_keycode_user(last_key, training_prev_mods);
        uint16_t expected = magic_training_first_keycode(alt);
        MAGIC_LOG("TRAIN check last=%u alt=%u expected=%u key=%u layer=%u\n",
                  last_key,
                  alt,
                  expected,
                  tap,
                  get_highest_layer(layer_state));
        if (expected == tap && expected != QK_REP && expected != KC_NO) {
            MAGIC_LOG("TRAIN block last=%u alt=%u key=%u layer=%u\n",
                      last_key,
                      alt,
                      expected,
                      get_highest_layer(layer_state));
            tap_code16(KC_HASH);
            return false;
        }

        // Combo training: check if previous+current key matches a combo output bigram
        if (combo_training_check(last_key, tap)) {
            MAGIC_LOG("COMBO_TRAIN block prev=%u curr=%u layer=%u\n",
                      last_key,
                      tap,
                      get_highest_layer(layer_state));
            tap_code16(KC_HASH);
            return false;
        }

        // Update training tracker after evaluating
        training_prev_key = tap;
        training_prev_mods = get_mods();
    }

    // For mod-tap magic key: only treat as tap on release when it was a real tap.
    if (is_magic_mod_tap) {
        if (record->event.pressed) {
            MAGIC_LOG("AREP modtap press raw=%u tapcnt=%u interrupted=%u layer=%u\n",
                      keycode,
                      record->tap.count,
                      record->tap.interrupted,
                      get_highest_layer(layer_state));
            return true;  // allow normal mod-tap processing (hold = shift)
        }

        // Release: tap.count==0 means it was a hold (shift). Non-zero == tap.
        if (record->tap.count == 0 || record->tap.interrupted) {
            MAGIC_LOG("AREP modtap hold skip raw=%u tapcnt=%u interrupted=%u layer=%u\n",
                      keycode,
                      record->tap.count,
                      record->tap.interrupted,
                      get_highest_layer(layer_state));
            return true;
        }

        MAGIC_LOG("AREP modtap tap raw=%u tapcnt=%u interrupted=%u layer=%u\n",
                  keycode,
                  record->tap.count,
                  record->tap.interrupted,
                  get_highest_layer(layer_state));
        return handle_magic_tap(keycode, record);
    }

    // For layer-tap magic key: only treat as tap on release when it was a real tap.
    if (is_magic_layer_tap) {
        if (record->event.pressed) {
            MAGIC_LOG("AREP layertap press raw=%u tapcnt=%u interrupted=%u layer=%u\n",
                      keycode,
                      record->tap.count,
                      record->tap.interrupted,
                      get_highest_layer(layer_state));
            return true;  // allow normal layer-tap processing (hold = layer)
        }

        // Release: tap.count==0 means it was a hold (layer). Non-zero == tap.
        if (record->tap.count == 0 || record->tap.interrupted) {
            MAGIC_LOG("AREP layertap hold skip raw=%u tapcnt=%u interrupted=%u layer=%u\n",
                      keycode,
                      record->tap.count,
                      record->tap.interrupted,
                      get_highest_layer(layer_state));
            return true;
        }

        MAGIC_LOG("AREP layertap tap raw=%u tapcnt=%u interrupted=%u layer=%u\n",
                  keycode,
                  record->tap.count,
                  record->tap.interrupted,
                  get_highest_layer(layer_state));
        return handle_magic_tap(keycode, record);
    }

    // Alternate repeat key (plain, not wrapped): emit mapped text or keycode based on last key
    if (record->event.pressed && tap == QK_AREP && !IS_QK_MOD_TAP(keycode) && !IS_QK_LAYER_TAP(keycode)) {
        return handle_magic_tap(keycode, record);
    }

    if (tap == QK_REP) {
        MAGIC_LOG("REP trigger raw=%u tap=%u layer=%u last=%u mods=%u\n",
                  keycode,
                  tap,
                  get_highest_layer(layer_state),
                  unwrap_tap_keycode(get_last_keycode()),
                  get_last_mods());
    }

    return true;
}
