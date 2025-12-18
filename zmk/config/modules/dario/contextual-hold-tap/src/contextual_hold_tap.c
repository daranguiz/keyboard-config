#include <zephyr/device.h>
#include <drivers/behavior.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/util.h>
#include <zmk/keys.h>
#include <dt-bindings/zmk/keys.h>
#include <zmk/behavior.h>
#include <zmk/matrix.h>
#include <zmk/endpoints.h>
#include <zmk/event_manager.h>
#include <zmk/events/position_state_changed.h>
#include <zmk/events/keycode_state_changed.h>

#include "contextual_hold_tap_internal.h"

#define DT_DRV_COMPAT dario_behavior_contextual_hold_tap

#if DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT)

#if IS_ENABLED(CONFIG_DARIO_CONTEXTUAL_HT_LOG)
LOG_MODULE_REGISTER(dario_contextual_ht, LOG_LEVEL_DBG);
#else
LOG_MODULE_REGISTER(dario_contextual_ht, CONFIG_ZMK_LOG_LEVEL);
#endif

#if !IS_ENABLED(CONFIG_DARIO_CONTEXTUAL_HT_LOG)
#undef LOG_DBG
#define LOG_DBG(...) (void)0
#endif

#define CHT_MAX_HELD CONFIG_DARIO_CONTEXTUAL_HT_MAX_HELD
#define CHT_MAX_CAPTURED_EVENTS CONFIG_DARIO_CONTEXTUAL_HT_MAX_CAPTURED_EVENTS

// increase if you have keyboard with more keys.
#define CHT_POSITION_NOT_USED 9999

enum flavor { FLAVOR_BALANCED, FLAVOR_TAP_PREFERRED, FLAVOR_HOLD_PREFERRED };

enum status {
    STATUS_UNDECIDED,
    STATUS_TAP,
    STATUS_HOLD_INTERRUPT,
    STATUS_HOLD_TIMER,
};

enum decision_moment {
    HT_KEY_DOWN,
    HT_KEY_UP,
    HT_OTHER_KEY_DOWN,
    HT_OTHER_KEY_UP,
    HT_TIMER_EVENT,
    HT_QUICK_TAP,
};

struct behavior_contextual_hold_tap_config {
    int tapping_term_ms;
    int quick_tap_ms;
    int require_prior_idle_ms;
    enum flavor normal_flavor;
    enum flavor after_flavor;
    bool hold_while_undecided;
    bool hold_while_undecided_linger;
    bool retro_tap;
    bool hold_trigger_on_release;
    const int32_t *hold_trigger_key_positions;
    int32_t hold_trigger_key_positions_len;
    const struct zmk_behavior_binding *tap_bindings;
    uint8_t tap_bindings_len;
    const struct zmk_behavior_binding *hold_bindings;
    uint8_t hold_bindings_len;
    const uint32_t *prior_keycodes;
    uint8_t prior_keycodes_len;
    int prior_timeout_ms;
};

struct behavior_contextual_hold_tap_data {
#if IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
    struct behavior_parameter_metadata_set set;
#endif // IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
};

// this data is specific for each hold-tap
struct active_hold_tap {
    int32_t position;
#if IS_ENABLED(CONFIG_ZMK_SPLIT)
    uint8_t source;
#endif
    int64_t timestamp;
    enum status status;
    enum flavor selected_flavor;
    const struct behavior_contextual_hold_tap_config *config;
    struct k_work_delayable work;
    bool work_is_cancelled;

    // initialized to -1, which is to be interpreted as "no other key has been pressed yet"
    int32_t position_of_first_other_key_pressed;
};

// The undecided hold tap is the hold tap that needs to be decided before
// other keypress events can be released. While the undecided_hold_tap is
// not NULL, most events are captured in captured_events.
// After the hold_tap is decided, it will stay in the active_hold_taps until
// its key-up has been processed and the delayed work is cleaned up.
static struct active_hold_tap *undecided_hold_tap = NULL;
static struct active_hold_tap active_hold_taps[CHT_MAX_HELD] = {};
// We capture most position_state_changed events and some modifiers_state_changed events.

enum captured_event_tag {
    ET_NONE,
    ET_POS_CHANGED,
    ET_CODE_CHANGED,
};

union captured_event_data {
    struct zmk_position_state_changed_event position;
    struct zmk_keycode_state_changed_event keycode;
};

struct captured_event {
    enum captured_event_tag tag;
    union captured_event_data data;
};

static struct captured_event captured_events[CHT_MAX_CAPTURED_EVENTS] = {};

static int release_captured_events(void);

// Keep track of which key was tapped most recently for the standard, if it is a hold-tap
// a position will be given, if not it will just be INT32_MIN
struct last_tapped {
    int32_t position;
    int64_t timestamp;
};

// Set time stamp to large negative number initially for test suites, but not
// int64 min since it will overflow if -1 is added
static struct last_tapped last_tapped = {INT32_MIN, INT32_MIN};

static void store_last_tapped(int64_t timestamp) {
    if (timestamp > last_tapped.timestamp) {
        last_tapped.position = INT32_MIN;
        last_tapped.timestamp = timestamp;
    }
}

static void store_last_hold_tapped(struct active_hold_tap *hold_tap) {
    last_tapped.position = hold_tap->position;
    last_tapped.timestamp = hold_tap->timestamp;
}

static bool is_quick_tap(struct active_hold_tap *hold_tap) {
    if ((last_tapped.timestamp + hold_tap->config->require_prior_idle_ms) > hold_tap->timestamp) {
        return true;
    } else {
        return (last_tapped.position == hold_tap->position) &&
               (last_tapped.timestamp + hold_tap->config->quick_tap_ms) > hold_tap->timestamp;
    }
}

static int capture_event(struct captured_event *data) {
    for (int i = 0; i < CHT_MAX_CAPTURED_EVENTS; i++) {
        if (captured_events[i].tag == ET_NONE) {
            captured_events[i] = *data;
            return 0;
        }
    }
    return -ENOMEM;
}

static bool have_captured_keydown_event(uint32_t position) {
    for (int i = 0; i < CHT_MAX_CAPTURED_EVENTS; i++) {
        struct captured_event *ev = &captured_events[i];
        if (ev->tag == ET_NONE) {
            return false;
        }

        if (ev->tag != ET_POS_CHANGED) {
            continue;
        }

        if (ev->data.position.data.position == position && ev->data.position.data.state) {
            return true;
        }
    }
    return false;
}

static inline const char *flavor_str(enum flavor flavor) {
    switch (flavor) {
    case FLAVOR_BALANCED:
        return "balanced";
    case FLAVOR_TAP_PREFERRED:
        return "tap-preferred";
    case FLAVOR_HOLD_PREFERRED:
        return "hold-preferred";
    default:
        return "UNKNOWN FLAVOR";
    }
}

static inline const char *status_str(enum status status) {
    switch (status) {
    case STATUS_UNDECIDED:
        return "undecided";
    case STATUS_HOLD_TIMER:
        return "hold-timer";
    case STATUS_HOLD_INTERRUPT:
        return "hold-interrupt";
    case STATUS_TAP:
        return "tap";
    default:
        return "UNKNOWN STATUS";
    }
}

static inline const char *decision_moment_str(enum decision_moment decision_moment) {
    switch (decision_moment) {
    case HT_KEY_UP:
        return "key-up";
    case HT_OTHER_KEY_DOWN:
        return "other-key-down";
    case HT_OTHER_KEY_UP:
        return "other-key-up";
    case HT_QUICK_TAP:
        return "quick-tap";
    case HT_TIMER_EVENT:
        return "timer";
    default:
        return "UNKNOWN STATUS";
    }
}

static int invoke_binding_set(const struct zmk_behavior_binding *bindings, uint8_t count,
                              struct zmk_behavior_binding_event *event, bool pressed) {
    for (uint8_t i = 0; i < count; i++) {
        int ret = zmk_behavior_invoke_binding(&bindings[i], *event, pressed);
        if (ret) {
            return ret;
        }
    }
    return 0;
}

static int press_hold_binding(struct active_hold_tap *hold_tap) {
    const struct behavior_contextual_hold_tap_config *cfg = hold_tap->config;
    struct zmk_behavior_binding_event event = {
        .position = hold_tap->position,
        .timestamp = hold_tap->timestamp,
#if IS_ENABLED(CONFIG_ZMK_SPLIT)
        .source = hold_tap->source,
#endif
    };

    return invoke_binding_set(cfg->hold_bindings, cfg->hold_bindings_len, &event, true);
}

static int press_tap_binding(struct active_hold_tap *hold_tap) {
    const struct behavior_contextual_hold_tap_config *cfg = hold_tap->config;
    struct zmk_behavior_binding_event event = {
        .position = hold_tap->position,
        .timestamp = hold_tap->timestamp,
#if IS_ENABLED(CONFIG_ZMK_SPLIT)
        .source = hold_tap->source,
#endif
    };

    store_last_hold_tapped(hold_tap);
    return invoke_binding_set(cfg->tap_bindings, cfg->tap_bindings_len, &event, true);
}

static int release_hold_binding(struct active_hold_tap *hold_tap) {
    const struct behavior_contextual_hold_tap_config *cfg = hold_tap->config;
    struct zmk_behavior_binding_event event = {
        .position = hold_tap->position,
        .timestamp = hold_tap->timestamp,
#if IS_ENABLED(CONFIG_ZMK_SPLIT)
        .source = hold_tap->source,
#endif
    };

    return invoke_binding_set(cfg->hold_bindings, cfg->hold_bindings_len, &event, false);
}

static int release_tap_binding(struct active_hold_tap *hold_tap) {
    const struct behavior_contextual_hold_tap_config *cfg = hold_tap->config;
    struct zmk_behavior_binding_event event = {
        .position = hold_tap->position,
        .timestamp = hold_tap->timestamp,
#if IS_ENABLED(CONFIG_ZMK_SPLIT)
        .source = hold_tap->source,
#endif
    };

    return invoke_binding_set(cfg->tap_bindings, cfg->tap_bindings_len, &event, false);
}

static int press_binding(struct active_hold_tap *hold_tap) {
    if (hold_tap->config->retro_tap && hold_tap->status == STATUS_HOLD_TIMER) {
        return 0;
    }

    if (hold_tap->status == STATUS_HOLD_TIMER || hold_tap->status == STATUS_HOLD_INTERRUPT) {
        if (hold_tap->config->hold_while_undecided) {
            // the hold is already active, so we don't need to press it again
            return 0;
        } else {
            return press_hold_binding(hold_tap);
        }
    } else {
        if (hold_tap->config->hold_while_undecided &&
            !hold_tap->config->hold_while_undecided_linger) {
            // time to release the hold before pressing the tap
            release_hold_binding(hold_tap);
        }
        return press_tap_binding(hold_tap);
    }
}

static int release_binding(struct active_hold_tap *hold_tap) {
    if (hold_tap->config->retro_tap && hold_tap->status == STATUS_HOLD_TIMER) {
        return 0;
    }

    if (hold_tap->status == STATUS_HOLD_TIMER || hold_tap->status == STATUS_HOLD_INTERRUPT) {
        return release_hold_binding(hold_tap);
    } else {
        return release_tap_binding(hold_tap);
    }
}

static bool is_first_other_key_pressed_trigger_key(struct active_hold_tap *hold_tap) {
    for (int i = 0; i < hold_tap->config->hold_trigger_key_positions_len; i++) {
        if (hold_tap->config->hold_trigger_key_positions[i] ==
            hold_tap->position_of_first_other_key_pressed) {
            return true;
        }
    }
    return false;
}

// Force a tap decision if the positional conditions for a hold decision are not met.
static void decide_positional_hold(struct active_hold_tap *hold_tap) {
    // Only force a tap decision if the positional hold/tap feature is enabled.
    if (!(hold_tap->config->hold_trigger_key_positions_len > 0)) {
        return;
    }

    // Only force a tap decision if another key was pressed after
    // the hold/tap key.
    if (hold_tap->position_of_first_other_key_pressed == -1) {
        return;
    }

    // Only force a tap decision if the first other key to be pressed
    // (after the hold/tap key) is not one of the trigger keys.
    if (is_first_other_key_pressed_trigger_key(hold_tap)) {
        return;
    }

    // Since the positional key conditions have failed, force a TAP decision.
    hold_tap->status = STATUS_TAP;
}

static void decide_hold_tap(struct active_hold_tap *hold_tap,
                            enum decision_moment decision_moment) {
    if (hold_tap->status != STATUS_UNDECIDED) {
        return;
    }

    if (hold_tap != undecided_hold_tap) {
        LOG_DBG("ERROR found undecided hold tap that is not the active hold tap");
        return;
    }

    if (hold_tap->config->hold_while_undecided && decision_moment == HT_KEY_DOWN) {
        LOG_DBG("%d hold behavior pressed while undecided", hold_tap->position);
        press_hold_binding(hold_tap);
        return;
    }

    switch (hold_tap->selected_flavor) {
    case FLAVOR_HOLD_PREFERRED:
        switch (decision_moment) {
        case HT_KEY_UP:
            hold_tap->status = STATUS_TAP;
            break;
        case HT_OTHER_KEY_DOWN:
            hold_tap->status = STATUS_HOLD_INTERRUPT;
            break;
        case HT_TIMER_EVENT:
            hold_tap->status = STATUS_HOLD_TIMER;
            break;
        case HT_QUICK_TAP:
            hold_tap->status = STATUS_TAP;
            break;
        default:
            break;
        }
        break;
    case FLAVOR_BALANCED:
        switch (decision_moment) {
        case HT_KEY_UP:
            hold_tap->status = STATUS_TAP;
            break;
        case HT_OTHER_KEY_UP:
            hold_tap->status = STATUS_HOLD_INTERRUPT;
            break;
        case HT_TIMER_EVENT:
            hold_tap->status = STATUS_HOLD_TIMER;
            break;
        case HT_QUICK_TAP:
            hold_tap->status = STATUS_TAP;
            break;
        default:
            break;
        }
        break;
    case FLAVOR_TAP_PREFERRED:
        switch (decision_moment) {
        case HT_KEY_UP:
            hold_tap->status = STATUS_TAP;
            break;
        case HT_TIMER_EVENT:
            hold_tap->status = STATUS_HOLD_TIMER;
            break;
        case HT_QUICK_TAP:
            hold_tap->status = STATUS_TAP;
            break;
        default:
            break;
        }
        break;
    }

    if (hold_tap->status == STATUS_UNDECIDED) {
        return;
    }

    decide_positional_hold(hold_tap);

    LOG_DBG("%d decided %s (%s decision moment %s)", hold_tap->position,
            status_str(hold_tap->status), flavor_str(hold_tap->selected_flavor),
            decision_moment_str(decision_moment));
    undecided_hold_tap = NULL;
    press_binding(hold_tap);
    release_captured_events();
}

static void decide_retro_tap(struct active_hold_tap *hold_tap) {
    if (!hold_tap->config->retro_tap) {
        return;
    }
    if (hold_tap->status == STATUS_HOLD_TIMER) {
        release_binding(hold_tap);
        LOG_DBG("%d retro tap", hold_tap->position);
        hold_tap->status = STATUS_TAP;
        press_binding(hold_tap);
        return;
    }
}

static void update_hold_status_for_retro_tap(uint32_t ignore_position) {
    for (int i = 0; i < CHT_MAX_HELD; i++) {
        struct active_hold_tap *hold_tap = &active_hold_taps[i];
        if (hold_tap->position == ignore_position ||
            hold_tap->position == CHT_POSITION_NOT_USED || hold_tap->config->retro_tap == false) {
            continue;
        }
        if (hold_tap->status == STATUS_HOLD_TIMER) {
            LOG_DBG("Update hold tap %d status to hold-interrupt", hold_tap->position);
            hold_tap->status = STATUS_HOLD_INTERRUPT;
            press_binding(hold_tap);
        }
    }
}

static struct active_hold_tap *find_hold_tap(uint32_t position) {
    for (int i = 0; i < CHT_MAX_HELD; i++) {
        if (active_hold_taps[i].position == position) {
            return &active_hold_taps[i];
        }
    }
    return NULL;
}

static struct active_hold_tap *store_hold_tap(struct zmk_behavior_binding_event *event,
                                              const struct behavior_contextual_hold_tap_config *config) {
    for (int i = 0; i < CHT_MAX_HELD; i++) {
        if (active_hold_taps[i].position != CHT_POSITION_NOT_USED) {
            continue;
        }
        active_hold_taps[i].position = event->position;
#if IS_ENABLED(CONFIG_ZMK_SPLIT)
        active_hold_taps[i].source = event->source;
#endif
        active_hold_taps[i].status = STATUS_UNDECIDED;
        active_hold_taps[i].config = config;
        active_hold_taps[i].timestamp = event->timestamp;
        active_hold_taps[i].position_of_first_other_key_pressed = -1;
        active_hold_taps[i].selected_flavor = config->normal_flavor;
        return &active_hold_taps[i];
    }
    return NULL;
}

static void clear_hold_tap(struct active_hold_tap *hold_tap) {
    hold_tap->position = CHT_POSITION_NOT_USED;
    hold_tap->status = STATUS_UNDECIDED;
    hold_tap->work_is_cancelled = false;
    hold_tap->selected_flavor = FLAVOR_BALANCED;
}

static enum flavor select_flavor(const struct behavior_contextual_hold_tap_config *cfg,
                                 int64_t now) {
    if (cfg->prior_keycodes_len == 0) {
        return cfg->normal_flavor;
    }

    struct cht_last_key_info last = cht_get_last_key_info();
    if (!last.valid) {
        return cfg->normal_flavor;
    }

    if (now - last.timestamp > cfg->prior_timeout_ms) {
        return cfg->normal_flavor;
    }

    for (uint8_t i = 0; i < cfg->prior_keycodes_len; i++) {
        if (cfg->prior_keycodes[i] == last.keycode) {
            return cfg->after_flavor;
        }
    }

    return cfg->normal_flavor;
}

static int release_captured_events(void) {
    if (undecided_hold_tap != NULL) {
        return 0;
    }

    for (int i = 0; i < CHT_MAX_CAPTURED_EVENTS; i++) {
        struct captured_event *captured_event = &captured_events[i];
        enum captured_event_tag tag = captured_event->tag;

        if (tag == ET_NONE) {
            return 0;
        }

        captured_events[i].tag = ET_NONE;
        if (undecided_hold_tap != NULL) {
            k_msleep(10);
        }

        switch (tag) {
        case ET_CODE_CHANGED:
            LOG_DBG("Releasing mods changed event 0x%02X %s",
                    captured_event->data.keycode.data.keycode,
                    (captured_event->data.keycode.data.state ? "pressed" : "released"));
            ZMK_EVENT_RAISE_AT(captured_event->data.keycode, contextual_hold_tap);
            break;
        case ET_POS_CHANGED:
            LOG_DBG("Releasing key position event for position %d %s",
                    captured_event->data.position.data.position,
                    (captured_event->data.position.data.state ? "pressed" : "released"));
            ZMK_EVENT_RAISE_AT(captured_event->data.position, contextual_hold_tap);
            break;
        default:
            LOG_ERR("Unhandled captured event type");
            break;
        }
    }
    return 0;
}

static int on_hold_tap_binding_pressed(struct zmk_behavior_binding *binding,
                                       struct zmk_behavior_binding_event event) {
    const struct device *dev = zmk_behavior_get_binding(binding->behavior_dev);
    const struct behavior_contextual_hold_tap_config *cfg = dev->config;

    if (undecided_hold_tap != NULL) {
        LOG_DBG("ERROR another hold-tap behavior is undecided.");
        return ZMK_BEHAVIOR_OPAQUE;
    }

    struct active_hold_tap *hold_tap = store_hold_tap(&event, cfg);

    if (hold_tap == NULL) {
        LOG_ERR("unable to store hold-tap info, did you press more than %d hold-taps?",
                CHT_MAX_HELD);
        return ZMK_BEHAVIOR_OPAQUE;
    }

    hold_tap->selected_flavor = select_flavor(cfg, event.timestamp);
    if (IS_ENABLED(CONFIG_DARIO_CONTEXTUAL_HT_LOG)) {
        struct cht_last_key_info last = cht_get_last_key_info();
        int64_t age = last.valid ? (event.timestamp - last.timestamp) : -1;
        LOG_DBG("%d new undecided hold_tap flavor=%s (last key 0x%X age=%lldms)", event.position,
                flavor_str(hold_tap->selected_flavor), last.valid ? last.keycode : 0,
                age);
    }

    undecided_hold_tap = hold_tap;

    if (is_quick_tap(hold_tap)) {
        decide_hold_tap(hold_tap, HT_QUICK_TAP);
    }

    decide_hold_tap(hold_tap, HT_KEY_DOWN);

    int32_t tapping_term_ms_left = (hold_tap->timestamp + cfg->tapping_term_ms) - k_uptime_get();
    if (tapping_term_ms_left < 0) {
        tapping_term_ms_left = 0;
    }
    k_work_schedule(&hold_tap->work, K_MSEC(tapping_term_ms_left));

    return ZMK_BEHAVIOR_OPAQUE;
}

static int on_hold_tap_binding_released(struct zmk_behavior_binding *binding,
                                        struct zmk_behavior_binding_event event) {
    struct active_hold_tap *hold_tap = find_hold_tap(event.position);
    if (hold_tap == NULL) {
        LOG_ERR("ACTIVE_HOLD_TAP_CLEANED_UP_TOO_EARLY");
        return ZMK_BEHAVIOR_OPAQUE;
    }

    int work_cancel_result = k_work_cancel_delayable(&hold_tap->work);
    if (event.timestamp > (hold_tap->timestamp + hold_tap->config->tapping_term_ms)) {
        decide_hold_tap(hold_tap, HT_TIMER_EVENT);
    }

    decide_hold_tap(hold_tap, HT_KEY_UP);
    decide_retro_tap(hold_tap);
    release_binding(hold_tap);

    if (hold_tap->config->hold_while_undecided && hold_tap->config->hold_while_undecided_linger) {
        release_hold_binding(hold_tap);
    }

    if (work_cancel_result == -EINPROGRESS) {
        LOG_DBG("%d hold-tap timer work in event queue", event.position);
        hold_tap->work_is_cancelled = true;
    } else {
        LOG_DBG("%d cleaning up hold-tap", event.position);
        clear_hold_tap(hold_tap);
    }

    return ZMK_BEHAVIOR_OPAQUE;
}

static int position_state_changed_listener(const zmk_event_t *eh) {
    struct zmk_position_state_changed *ev = as_zmk_position_state_changed(eh);

    update_hold_status_for_retro_tap(ev->position);

    if (undecided_hold_tap == NULL) {
        LOG_DBG("%d bubble (no undecided hold_tap active)", ev->position);
        return ZMK_EV_EVENT_BUBBLE;
    }

    if ((undecided_hold_tap->config->hold_trigger_on_release !=
         ev->state) && (undecided_hold_tap->position_of_first_other_key_pressed == -1)) {
        undecided_hold_tap->position_of_first_other_key_pressed = ev->position;
    }

    if (undecided_hold_tap->position == ev->position) {
        if (ev->state) { // keydown
            LOG_ERR("hold-tap listener should be called before most other listeners!");
            return ZMK_EV_EVENT_BUBBLE;
        } else { // keyup
            LOG_DBG("%d bubble undecided hold-tap keyrelease event", undecided_hold_tap->position);
            return ZMK_EV_EVENT_BUBBLE;
        }
    }

    if (ev->timestamp >
        (undecided_hold_tap->timestamp + undecided_hold_tap->config->tapping_term_ms)) {
        decide_hold_tap(undecided_hold_tap, HT_TIMER_EVENT);
    }

    if (undecided_hold_tap == NULL) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    if (!ev->state && !have_captured_keydown_event(ev->position)) {
        LOG_DBG("%d bubbling %d %s event", undecided_hold_tap->position, ev->position,
                ev->state ? "down" : "up");
        return ZMK_EV_EVENT_BUBBLE;
    }

    LOG_DBG("%d capturing %d %s event", undecided_hold_tap->position, ev->position,
            ev->state ? "down" : "up");
    struct captured_event capture = {
        .tag = ET_POS_CHANGED,
        .data = {.position = copy_raised_zmk_position_state_changed(ev)},
    };
    capture_event(&capture);
    decide_hold_tap(undecided_hold_tap, ev->state ? HT_OTHER_KEY_DOWN : HT_OTHER_KEY_UP);
    return ZMK_EV_EVENT_CAPTURED;
}

static int keycode_state_changed_listener(const zmk_event_t *eh) {
    struct zmk_keycode_state_changed *ev = as_zmk_keycode_state_changed(eh);

    if (ev->state && !is_mod(ev->usage_page, ev->keycode)) {
        store_last_tapped(ev->timestamp);
    }

    if (undecided_hold_tap == NULL) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    if (!is_mod(ev->usage_page, ev->keycode)) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    if (undecided_hold_tap->config->hold_while_undecided &&
        undecided_hold_tap->status == STATUS_UNDECIDED) {
        return ZMK_EV_EVENT_BUBBLE;
    }

    LOG_DBG("%d capturing 0x%02X %s event", undecided_hold_tap->position, ev->keycode,
            ev->state ? "down" : "up");
    struct captured_event capture = {
        .tag = ET_CODE_CHANGED, .data = {.keycode = copy_raised_zmk_keycode_state_changed(ev)}};
    capture_event(&capture);
    return ZMK_EV_EVENT_CAPTURED;
}

int behavior_contextual_hold_tap_listener(const zmk_event_t *eh) {
    if (as_zmk_position_state_changed(eh) != NULL) {
        return position_state_changed_listener(eh);
    } else if (as_zmk_keycode_state_changed(eh) != NULL) {
        return keycode_state_changed_listener(eh);
    }
    return ZMK_EV_EVENT_BUBBLE;
}

ZMK_LISTENER(behavior_contextual_hold_tap, behavior_contextual_hold_tap_listener);
ZMK_SUBSCRIPTION(behavior_contextual_hold_tap, zmk_position_state_changed);
ZMK_SUBSCRIPTION(behavior_contextual_hold_tap, zmk_keycode_state_changed);

void behavior_contextual_hold_tap_timer_work_handler(struct k_work *item) {
    struct k_work_delayable *d_work = k_work_delayable_from_work(item);
    struct active_hold_tap *hold_tap = CONTAINER_OF(d_work, struct active_hold_tap, work);

    if (hold_tap->work_is_cancelled) {
        clear_hold_tap(hold_tap);
    } else {
        decide_hold_tap(hold_tap, HT_TIMER_EVENT);
    }
}

static int behavior_contextual_hold_tap_init(const struct device *dev) {
    static bool init_first_run = true;

    if (init_first_run) {
        for (int i = 0; i < CHT_MAX_HELD; i++) {
            k_work_init_delayable(&active_hold_taps[i].work,
                                  behavior_contextual_hold_tap_timer_work_handler);
            active_hold_taps[i].position = CHT_POSITION_NOT_USED;
        }
    }
    init_first_run = false;
    return 0;
}

static const struct behavior_driver_api behavior_contextual_hold_tap_driver_api = {
    .binding_pressed = on_hold_tap_binding_pressed,
    .binding_released = on_hold_tap_binding_released,
#if IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
    .get_parameter_metadata = zmk_behavior_get_empty_param_metadata,
#endif // IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
};

#define TAP_BINDING_ENTRY(idx, node)                                                                \
    {                                                                                              \
        .behavior_dev = DEVICE_DT_NAME(DT_INST_PHANDLE_BY_IDX(node, tap_bindings, idx)),           \
        .param1 = COND_CODE_0(DT_INST_PHA_HAS_CELL_AT_IDX(node, tap_bindings, idx, param1), (0),   \
                              (DT_INST_PHA_BY_IDX(node, tap_bindings, idx, param1))),             \
        .param2 = COND_CODE_0(DT_INST_PHA_HAS_CELL_AT_IDX(node, tap_bindings, idx, param2), (0),   \
                              (DT_INST_PHA_BY_IDX(node, tap_bindings, idx, param2))),             \
    }

#define HOLD_BINDING_ENTRY(idx, node)                                                               \
    {                                                                                              \
        .behavior_dev = DEVICE_DT_NAME(DT_INST_PHANDLE_BY_IDX(node, hold_bindings, idx)),          \
        .param1 = COND_CODE_0(DT_INST_PHA_HAS_CELL_AT_IDX(node, hold_bindings, idx, param1), (0),  \
                              (DT_INST_PHA_BY_IDX(node, hold_bindings, idx, param1))),            \
        .param2 = COND_CODE_0(DT_INST_PHA_HAS_CELL_AT_IDX(node, hold_bindings, idx, param2), (0),  \
                              (DT_INST_PHA_BY_IDX(node, hold_bindings, idx, param2))),            \
    }

#define KP_INST(n)                                                                                 \
    static const struct zmk_behavior_binding contextual_hold_tap_config_##n##_tap[] = {            \
        LISTIFY(DT_INST_PROP_LEN(n, tap_bindings), TAP_BINDING_ENTRY, (, ), n)};                    \
    static const struct zmk_behavior_binding contextual_hold_tap_config_##n##_hold[] = {           \
        LISTIFY(DT_INST_PROP_LEN(n, hold_bindings), HOLD_BINDING_ENTRY, (, ), n)};                  \
    static const uint32_t contextual_hold_tap_prior_keycodes_##n[] = DT_INST_PROP(n, prior_keycodes); \
    static const int32_t contextual_hold_tap_trigger_positions_##n[] =                              \
        DT_INST_PROP(n, hold_trigger_key_positions);                                                \
    static const struct behavior_contextual_hold_tap_config behavior_contextual_hold_tap_config_##n = { \
        .tapping_term_ms = DT_INST_PROP(n, tapping_term_ms),                                       \
        .quick_tap_ms = DT_INST_PROP(n, quick_tap_ms),                                             \
        .require_prior_idle_ms = DT_INST_PROP(n, require_prior_idle_ms),                           \
        .normal_flavor = DT_ENUM_IDX(DT_DRV_INST(n), normal_flavor),                               \
        .after_flavor = DT_ENUM_IDX(DT_DRV_INST(n), after_flavor),                                 \
        .hold_while_undecided = DT_INST_PROP(n, hold_while_undecided),                             \
        .hold_while_undecided_linger = DT_INST_PROP(n, hold_while_undecided_linger),               \
        .retro_tap = DT_INST_PROP(n, retro_tap),                                                   \
        .hold_trigger_on_release = DT_INST_PROP(n, hold_trigger_on_release),                       \
        .hold_trigger_key_positions = contextual_hold_tap_trigger_positions_##n,                   \
        .hold_trigger_key_positions_len = DT_INST_PROP_LEN(n, hold_trigger_key_positions),         \
        .tap_bindings = contextual_hold_tap_config_##n##_tap,                                      \
        .tap_bindings_len = DT_INST_PROP_LEN(n, tap_bindings),                                     \
        .hold_bindings = contextual_hold_tap_config_##n##_hold,                                    \
        .hold_bindings_len = DT_INST_PROP_LEN(n, hold_bindings),                                   \
        .prior_keycodes = contextual_hold_tap_prior_keycodes_##n,                                  \
        .prior_keycodes_len = DT_INST_PROP_LEN(n, prior_keycodes),                                 \
        .prior_timeout_ms = DT_INST_PROP(n, prior_timeout_ms),                                     \
    };                                                                                             \
    static struct behavior_contextual_hold_tap_data behavior_contextual_hold_tap_data_##n = {};    \
    BEHAVIOR_DT_INST_DEFINE(n, behavior_contextual_hold_tap_init, NULL,                            \
                            &behavior_contextual_hold_tap_data_##n,                                \
                            &behavior_contextual_hold_tap_config_##n, POST_KERNEL,                 \
                            CONFIG_KERNEL_INIT_PRIORITY_DEFAULT,                                   \
                            &behavior_contextual_hold_tap_driver_api);

DT_INST_FOREACH_STATUS_OKAY(KP_INST)

#endif /* DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT) */
