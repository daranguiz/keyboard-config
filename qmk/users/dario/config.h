#pragma once

// ============================================================================
// QMK Configuration for Timeless Home Row Mods
// Maps to ZMK configuration in zmk/config/dario_behaviors.dtsi
// ============================================================================

// ----------------------------------------------------------------------------
// LAYER-TAP KEYS (LT) - Maps to ZMK &lt behavior
// ----------------------------------------------------------------------------

// ZMK: tapping-term-ms = <200>
#define TAPPING_TERM 200
#define TAPPING_TERM_PER_KEY

// ZMK: quick-tap-ms = <150>
#define QUICK_TAP_TERM 150

// ZMK: flavor = "balanced"
#define PERMISSIVE_HOLD

// ----------------------------------------------------------------------------
// HOME ROW MODS (MT) - Maps to ZMK hml/hmr behaviors
// ----------------------------------------------------------------------------

// ZMK: tapping-term-ms = <280>
#define TAPPING_TERM_HRM 280

// ZMK: require-prior-idle-ms = <150>
#define FLOW_TAP_TERM 150

// ZMK: quick-tap-ms = <175>
// Note: QMK uses single QUICK_TAP_TERM (150ms) for both LT and MT keys

// ZMK: flavor = "balanced"
// Note: Uses PERMISSIVE_HOLD defined above

// ZMK: hold-trigger-key-positions (opposite hand rule)
#define CHORDAL_HOLD
#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY

// ZMK: hold-trigger-on-release
// Note: No direct QMK equivalent, approximated by CHORDAL_HOLD + PERMISSIVE_HOLD

// ----------------------------------------------------------------------------
// ADDITIONAL QMK-SPECIFIC SETTINGS (No ZMK equivalent)
// ----------------------------------------------------------------------------

#define BOOTMAGIC_ROW 0
#define BOOTMAGIC_COLUMN 0

#define QMK_KEYS_PER_SCAN 4

#define NO_ACTION_MACRO
#define NO_ACTION_FUNCTION
