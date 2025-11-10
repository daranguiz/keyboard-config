#include "keymap_config.h"
#include "config.h"
#include <stdio.h>

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
  [BASE] = LAYOUT_split_3x5_3(
    KC_Q,              KC_W,              KC_F,              KC_P,              KC_G,              KC_J,              KC_L,              KC_U,              KC_Y,              KC_QUOT,
    LGUI_T(KC_A),      LALT_T(KC_R),      LCTL_T(KC_S),      LSFT_T(KC_T),      KC_D,              KC_H,              LSFT_T(KC_N),      LCTL_T(KC_E),      LALT_T(KC_I),      LGUI_T(KC_O),
    LT(BUTTON, KC_Z),  LT(FUN, KC_X),     KC_C,              KC_V,              KC_B,              KC_K,              KC_M,              KC_COMM,           ALGR_T(KC_DOT),    LT(BUTTON, KC_SLSH),
    KC_ENT, LT(NAV, KC_SPC),  LT(MEDIA, KC_TAB),             LT(SYM, KC_DEL), KC_LSFT,    LT(NUM, KC_BSPC)
  ),
  [NAV] = LAYOUT_split_3x5_3(
    U_NA,   U_NA,    U_NA,    U_NA,    U_NA,    U_RDO,   U_PST,   U_CPY,   U_CUT,   U_UND,
    KC_LGUI, KC_LALT, KC_LCTL, KC_LSFT, U_NA,    KC_CAPS, KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT,
    U_UND,   U_CUT,   U_CPY,   U_PST,   U_NA,    KC_INS,  KC_HOME, KC_PGDN, KC_PGUP, KC_END,
    U_NA,    U_NA,    U_NA,    KC_DEL,  KC_ENT,  KC_BSPC
  ),
  [MOUSE] = LAYOUT_split_3x5_3(
    U_NA,   U_NA,    U_NA,    U_NA,    U_NA,    U_RDO,   U_PST,   U_CPY,   U_CUT,   U_UND,
    KC_LGUI, KC_LALT, KC_LCTL, KC_LSFT, U_NA,    U_NU,    MS_LEFT, MS_DOWN, MS_UP,   MS_RGHT,
    U_NA,    KC_ALGR, U_NA,    U_NA,    U_NA,    U_NU,    MS_WHLL, MS_WHLD, MS_WHLU, MS_WHLR,
    U_NA,    U_NA,    U_NA,    MS_BTN1, MS_BTN3, MS_BTN2
  ),
  [MEDIA] = LAYOUT_split_3x5_3(
    U_NA,   U_NA,    U_NA,    U_NA,    U_NA,    RM_TOGG, RM_NEXT, RM_HUEU, RM_SATU, RM_VALU,
    KC_LGUI, KC_LALT, KC_LCTL, KC_LSFT, U_NA,    U_NU,    KC_MPRV, KC_VOLD, KC_VOLU, KC_MNXT,
    U_NA,    KC_ALGR, U_NA,    U_NA,    U_NA,    U_NU,    U_NU,    U_NU,    U_NU,    U_NU,
    U_NA,    U_NA,    U_NA,    KC_MSTP, KC_MPLY, KC_MUTE
  ),
  [NUM] = LAYOUT_split_3x5_3(
    KC_LBRC, KC_4,    KC_5,    KC_6,    KC_RBRC, U_NA,    U_NA,    U_NA,    U_NA,    U_NA,
    KC_SCLN, KC_1,    KC_2,    KC_3,    KC_EQL,  U_NA,    KC_LSFT, KC_LCTL, KC_LALT, KC_LGUI,
    KC_GRV,  KC_7,    KC_8,    KC_9,    KC_BSLS, U_NA,    U_NA,    U_NA,    KC_ALGR, U_NA,
    KC_DOT,  KC_0,    KC_MINS, U_NA,    U_NA,    U_NA
  ),
  [SYM] = LAYOUT_split_3x5_3(
    KC_LCBR, KC_DLR,  KC_PERC, KC_CIRC, KC_RCBR, U_NA,    U_NA,    U_NA,    U_NA,    U_NA,
    KC_COLN, KC_EXLM, KC_AT,   KC_HASH, KC_PLUS, U_NA,    KC_LSFT, KC_LCTL, KC_LALT, KC_LGUI,
    KC_TILD, KC_AMPR, KC_ASTR, KC_LPRN, KC_PIPE, U_NA,    U_NA,    U_NA,    KC_ALGR, U_NA,
    KC_LPRN, KC_RPRN, KC_UNDS, U_NA,    U_NA,    U_NA
  ),
  [FUN] = LAYOUT_split_3x5_3(
    KC_F12,  KC_F7,   KC_F8,   KC_F9,   KC_PSCR, U_NA,    U_NA,    U_NA,    U_NA,    U_NA,
    KC_F11,  KC_F4,   KC_F5,   KC_F6,   KC_SCRL, U_NA,    KC_LSFT, KC_LCTL, KC_LALT, KC_LGUI,
    KC_F10,  KC_F1,   KC_F2,   KC_F3,   KC_PAUS, U_NA,    U_NA,    U_NA,    KC_ALGR, U_NA,
    KC_APP,  KC_SPC,  KC_TAB,  U_NA,    U_NA,    U_NA
  ),
  [BUTTON] = LAYOUT_split_3x5_3(
    U_UND,   U_CUT,   U_CPY,   U_PST,   U_RDO,   U_RDO,   U_PST,   U_CPY,   U_CUT,   U_UND,
    KC_LGUI, KC_LALT, KC_LCTL, KC_LSFT, KC_TRNS, KC_TRNS, KC_LSFT, KC_LCTL, KC_LALT, KC_LGUI,
    U_UND,   U_CUT,   U_CPY,   U_PST,   U_RDO,   U_RDO,   U_PST,   U_CPY,   U_CUT,   U_UND,
    MS_BTN2, MS_BTN3, MS_BTN1, MS_BTN1, MS_BTN3, MS_BTN2
  )
};
