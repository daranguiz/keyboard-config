#include "dario.h"
#include "quantum/repeat_key.h"
#include "print.h"
#include "action_layer.h"
#include "quantum/quantum_keycodes.h"

// Forward declaration generated in keymap.c (magic macros/text expansions)
extern bool process_magic_record(uint16_t keycode, keyrecord_t *record);

#define MAGIC_LOG(...) uprintf(__VA_ARGS__)

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
        return QK_LAYER_TAP_GET_TAP_KEYCODE(keycode);
    }
    return keycode;
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

    // Alternate repeat key: emit mapped text or keycode based on last key
    if (record->event.pressed && tap == QK_AREP) {
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
