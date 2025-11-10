#include QMK_KEYBOARD_H
#include "keymap_config.h"

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE]   = LAYOUT_wrapper(LAYER_BASE),
    [NAV]    = LAYOUT_wrapper(LAYER_NAV),
    [MOUSE]  = LAYOUT_wrapper(LAYER_MOUSE),
    [MEDIA]  = LAYOUT_wrapper(LAYER_MEDIA),
    [NUM]    = LAYOUT_wrapper(LAYER_NUM),
    [SYM]    = LAYOUT_wrapper(LAYER_SYM),
    [FUN]    = LAYOUT_wrapper(LAYER_FUN),
    [BUTTON] = LAYOUT_wrapper(LAYER_BUTTON)
};
