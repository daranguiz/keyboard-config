#include "keymap_config.h"
#include "oled.h"

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

layer_state_t layer_state_set_user(layer_state_t state) {
    enum layers cur_layer = get_highest_layer(state);

    switch (cur_layer) {
        case GAME:
            autoshift_disable();
            break;
        default:
            autoshift_enable();
            break;
    }

    return state;
}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    process_record_user_oled(keycode, record);
    return true;
}
