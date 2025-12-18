#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zmk/event_manager.h>
#include <zmk/events/keycode_state_changed.h>
#include <zmk/keys.h>

#include "contextual_hold_tap_internal.h"

LOG_MODULE_DECLARE(dario_contextual_ht);

static struct cht_last_key_info last_key = {
    .keycode = 0,
    .timestamp = 0,
    .valid = false,
};

struct cht_last_key_info cht_get_last_key_info(void) {
    return last_key;
}

void cht_record_last_key(uint32_t keycode, int64_t timestamp) {
    if (timestamp < last_key.timestamp) {
        return;
    }
    last_key.keycode = keycode;
    last_key.timestamp = timestamp;
    last_key.valid = true;
}

static int contextual_hold_tap_listener(const zmk_event_t *eh) {
    const struct zmk_keycode_state_changed *ev = as_zmk_keycode_state_changed(eh);
    if (ev == NULL) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    if (!ev->state) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    if (is_mod(ev->usage_page, ev->keycode)) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    cht_record_last_key(ev->keycode, ev->timestamp);
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(contextual_hold_tap, contextual_hold_tap_listener);
ZMK_SUBSCRIPTION(contextual_hold_tap, zmk_keycode_state_changed);
