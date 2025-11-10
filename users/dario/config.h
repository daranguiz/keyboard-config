#pragma once

// Bootmagic: Hold upper-left key at power on to enter bootloader
// Row 0, Column 0 is typically the upper-left key on most keyboards
#define BOOTMAGIC_ROW 0
#define BOOTMAGIC_COLUMN 0

// Mod-tap and home row mods configuration
#define TAPPING_TERM 200
#define TAPPING_TERM_PER_KEY

// Custom macro for home row mod tapping term (TAPPING_TERM + 100)
#define TAPPING_TERM_HRM 300

// Chordal hold: opposite hands rule for tap-hold keys
// Settles tap-hold as tap when same-hand key is pressed
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to function
#define PERMISSIVE_HOLD_PER_KEY
#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY

// Enable rapid switch from tap to hold
#define TAPPING_FORCE_HOLD

// Recommended for heavy chording
#define QMK_KEYS_PER_SCAN 4

// Mouse key speed and acceleration
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

// Firmware size optimization
#define NO_ACTION_MACRO
#define NO_ACTION_FUNCTION
