#include QMK_KEYBOARD_H
#include "keymap_config.h"

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE]   = LAYOUT_wrapper(LAYER_BASE),
    [NUM]    = LAYOUT_wrapper(LAYER_NUM),
    [SYM]    = LAYOUT_wrapper(LAYER_SYM),
    [NAV]    = LAYOUT_wrapper(LAYER_NAV),
    [MEDIA]  = LAYOUT_wrapper(LAYER_MEDIA),
    [FUN]    = LAYOUT_wrapper(LAYER_FUN),
};
