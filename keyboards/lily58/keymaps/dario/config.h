// Copyright 2019 Manna Harbour
// https://github.com/manna-harbour/miryoku
// generated -*- buffer-read-only: t -*-

// This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

#pragma once

//////////////////////// - Mod config etc

// default but used in macros
#undef TAPPING_TERM
#define TAPPING_TERM 200
#define TAPPING_TERM_PER_KEY

// Dario macro, not a QMK thing
#define TAPPING_TERM_HRM (TAPPING_TERM + 100)

// Chordal hold: opposite hands rule for tap-hold keys
// Settles tap-hold as tap when same-hand key is pressed
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to function

// IGNORE_MOD_TAP_INTERRUPT removed - now default behavior in QMK 0.30.x

// Enable rapid switch from tap to hold, disables double tap hold auto-repeat.
#define TAPPING_FORCE_HOLD

// Auto Shift
#define NO_AUTO_SHIFT_ALPHA
#define AUTO_SHIFT_TIMEOUT TAPPING_TERM
#define AUTO_SHIFT_NO_SETUP

// Recommended for heavy chording.
#define QMK_KEYS_PER_SCAN 4

// Mouse key speed and acceleration.
#undef MOUSEKEY_DELAY
#define MOUSEKEY_DELAY          0
#undef MOUSEKEY_INTERVAL
#define MOUSEKEY_INTERVAL       16
#undef MOUSEKEY_WHEEL_DELAY
#define MOUSEKEY_WHEEL_DELAY    0
#undef MOUSEKEY_MAX_SPEED
#define MOUSEKEY_MAX_SPEED      6
#undef MOUSEKEY_TIME_TO_MAX
#define MOUSEKEY_TIME_TO_MAX    64

// Keymap customization
#define MIRYOKU_ALPHAS_COLEMAK
#define MIRYOKU_CLIPBOARD_MAC

#define PERMISSIVE_HOLD_PER_KEY
#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY

// https://thomasbaart.nl/2018/12/01/reducing-firmware-size-in-qmk/
#define NO_ACTION_MACRO
#define NO_ACTION_FUNCTION

#define SPLIT_OLED_ENABLE

//////////////////////// - Keyboard layout



#define XXX KC_NO

#define LAYOUT_miryoku_with_grv(\
     K00, K01, K02, K03, K04,                K05, K06, K07, K08, K09, KGRV,\
     K10, K11, K12, K13, K14,                K15, K16, K17, K18, K19,\
     K20, K21, K22, K23, K24,                K25, K26, K27, K28, K29,\
     N30, N31, K32, K33, K34,                K35, K36, K37, N38, N39\
)\
LAYOUT(\
XXX, XXX, XXX, XXX, XXX, XXX,                XXX, XXX, XXX, XXX, XXX, KGRV,\
XXX, K00, K01, K02, K03, K04,                K05, K06, K07, K08, K09, XXX,\
K00, K10, K11, K12, K13, K14,                K15, K16, K17, K18, K19, K09,\
XXX, K20, K21, K22, K23, K24, XXX,      XXX, K25, K26, K27, K28, K29, XXX,\
               XXX, K32, K33, K34,      K35, K36, K37, XXX\
)

#define LAYOUT_miryoku(\
     K00, K01, K02, K03, K04,                K05, K06, K07, K08, K09,\
     K10, K11, K12, K13, K14,                K15, K16, K17, K18, K19,\
     K20, K21, K22, K23, K24,                K25, K26, K27, K28, K29,\
     N30, N31, K32, K33, K34,                K35, K36, K37, N38, N39\
)\
LAYOUT(\
XXX, XXX, XXX, XXX, XXX, XXX,                XXX, XXX, XXX, XXX, XXX, XXX,\
XXX, K00, K01, K02, K03, K04,                K05, K06, K07, K08, K09, XXX,\
K00, K10, K11, K12, K13, K14,                K15, K16, K17, K18, K19, K09,\
XXX, K20, K21, K22, K23, K24, XXX,      XXX, K25, K26, K27, K28, K29, XXX,\
               XXX, K32, K33, K34,      K35, K36, K37, XXX\
)
