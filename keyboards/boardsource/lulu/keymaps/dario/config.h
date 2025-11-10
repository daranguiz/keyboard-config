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
#ifdef AUTO_SHIFT_TIMEOUT
#undef AUTO_SHIFT_TIMEOUT
#endif

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

// Bootmagic: Hold the upper-left key at power on to enter bootloader
// This allows entering bootloader without opening the keyboard or pressing BOOTSEL
// Row 0, Column 0 corresponds to the upper-left key on the physical Lulu
#define BOOTMAGIC_ROW 0
#define BOOTMAGIC_COLUMN 0

// Keymap customization
#define MIRYOKU_ALPHAS_COLEMAK
#define MIRYOKU_CLIPBOARD_MAC

#define PERMISSIVE_HOLD_PER_KEY
#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY

// https://thomasbaart.nl/2018/12/01/reducing-firmware-size-in-qmk/
#define NO_ACTION_MACRO
#define NO_ACTION_FUNCTION


