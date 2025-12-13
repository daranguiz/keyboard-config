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

// ZMK: quick-tap-ms = <200>
// #define QUICK_TAP_TERM 200  // Defaults to TAPPING_TERM if not set

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
// Note: QMK uses single QUICK_TAP_TERM (200ms) for both LT and MT keys

// ZMK: flavor = "balanced"
// Note: Uses PERMISSIVE_HOLD defined above

// ZMK: hold-trigger-key-positions (opposite hand rule)
#define CHORDAL_HOLD

// ZMK: hold-trigger-on-release
// Note: No direct QMK equivalent, approximated by CHORDAL_HOLD + PERMISSIVE_HOLD

// ----------------------------------------------------------------------------
// HOLD-PREFERRED MOD-TAPS (mt:LSFT:TAB and mt:LSFT:DEL)
// ----------------------------------------------------------------------------

// Enable per-key configuration for hold-on-other-key-press
// This allows TAB and DEL mod-taps to use hold-preferred behavior
// (immediately activate hold when another key is pressed)
#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY

// ----------------------------------------------------------------------------
// ADDITIONAL QMK-SPECIFIC SETTINGS (No ZMK equivalent)
// ----------------------------------------------------------------------------

#define BOOTMAGIC_ROW 0
#define BOOTMAGIC_COLUMN 0

#define QMK_KEYS_PER_SCAN 4

// #define NO_ACTION_MACRO  // REMOVED to enable text expansion macros
#define NO_ACTION_FUNCTION

// ----------------------------------------------------------------------------
// COMBOS
// ----------------------------------------------------------------------------

// Standard combo timeout (maps to timeout-ms in ZMK)
#define COMBO_TERM 50

// Make combos position-based by always checking keycodes from layer 0 (BASE_NIGHT)
// This ensures combos trigger at the same physical positions regardless of active layer
// (e.g., dfu_left works on Racket layer even though the keys are different)
#define COMBO_ONLY_FROM_LAYER 0

// Note: QMK does not have built-in require-prior-idle support for combos
// This is a ZMK-only feature (require-prior-idle-ms)
