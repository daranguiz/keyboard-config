# Contract: Chordal Hold Migration

**Feature**: 001-migrate-chordal-hold
**Type**: Code migration contract
**Date**: 2025-11-07

## Overview

This contract defines the specific code changes required to migrate from bilateral combinations patch to QMK's native chordal hold feature.

**Scope**:
- 1 QMK core file: quantum/action.c
- 3 personal keymaps: lulu/dario, lily58/daranguiz_miryoku, skeletyl/daranguiz_miryoku

## File Modifications

### MOD-1: Remove Bilateral Combinations from quantum/action.c

**File**: `quantum/action.c`

**Operation**: REMOVE all bilateral combinations patch code

**Changes**:

1. **Lines 58-60**: Remove conditional quantum.h include
   ```c
   // REMOVE:
   #if (BILATERAL_COMBINATIONS + 0)
   #    include "quantum.h"
   #endif
   ```

2. **Lines 300-360**: Remove bilateral combinations implementation
   ```c
   // REMOVE entire section:
   #ifdef BILATERAL_COMBINATIONS
   static struct {
       bool     active;
       uint16_t code;
       uint16_t tap;
       uint8_t  mods;
       bool     left;
       // ... rest of implementation
   } bilateral_combinations;

   // Remove all functions:
   // - bilateral_combinations_left()
   // - bilateral_combinations_hold()
   // - bilateral_combinations_release()
   // - bilateral_combinations_tap()
   #endif
   ```

3. **Lines 415-420**: Remove ACT_LMODS/ACT_RMODS integration
   ```c
   // REMOVE:
   #if defined(BILATERAL_COMBINATIONS)
                   bilateral_combinations_tap(action, record);
   #endif
   ```

4. **Lines 535-538**: Remove MODS_TAP tap phase integration
   ```c
   // REMOVE:
   #if defined(BILATERAL_COMBINATIONS)
                   bilateral_combinations_tap(action, record);
   #endif
   ```

5. **Lines 545-548**: Remove MODS_TAP hold phase integration
   ```c
   // REMOVE:
   #if defined(BILATERAL_COMBINATIONS)
                   bilateral_combinations_hold(action, record);
   #endif
   ```

6. **Lines 562-565**: Remove MODS_TAP release phase integration
   ```c
   // REMOVE:
   #if defined(BILATERAL_COMBINATIONS)
                   bilateral_combinations_release(action, record);
   #endif
   ```

7. **Lines 744-747**: Remove layer-tap integration
   ```c
   // REMOVE:
   #if defined(BILATERAL_COMBINATIONS)
                   bilateral_combinations_tap(action, record);
   #endif
   ```

**Validation**:
- File should match upstream version for bilateral combinations sections
- Build system should still compile (bilateral combinations was ifdef-guarded)
- No references to BILATERAL_COMBINATIONS remain in the file

---

### MOD-2: Update keyboards/boardsource/lulu/keymaps/dario/config.h

**File**: `keyboards/boardsource/lulu/keymaps/dario/config.h`

**Operation**: REPLACE bilateral combinations config with chordal hold

**Changes**:

**Remove (around line 19-20)**:
```c
// Note, only available with the manna_harbour patch
#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM
```

**Add (in same location)**:
```c
// Chordal hold: opposite hands rule for tap-hold keys
// Settles tap-hold as tap when same-hand key is pressed
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to function
```

**Validation**:
- No BILATERAL_COMBINATIONS references remain
- CHORDAL_HOLD and PERMISSIVE_HOLD are defined
- File still has valid C preprocessor syntax

---

### MOD-3: Update keyboards/lily58/keymaps/daranguiz_miryoku/config.h

**File**: `keyboards/lily58/keymaps/daranguiz_miryoku/config.h`

**Operation**: REPLACE bilateral combinations config with chordal hold

**Source**: This file exists on lily58/miryoku-bilateral-combinations branch

**Changes**:

**Remove**:
```c
#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM
```

**Add**:
```c
// Chordal hold: opposite hands rule for tap-hold keys
// Settles tap-hold as tap when same-hand key is pressed
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to function
```

**Validation**:
- No BILATERAL_COMBINATIONS references remain
- CHORDAL_HOLD and PERMISSIVE_HOLD are defined
- File still has valid C preprocessor syntax

---

### MOD-4: Update keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/daranguiz_config.h

**File**: `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/daranguiz_config.h`

**Operation**: REPLACE bilateral combinations config with chordal hold

**Source**: This file exists on lily58/miryoku-bilateral-combinations branch

**Changes**:

**Remove**:
```c
#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM
```

**Add**:
```c
// Chordal hold: opposite hands rule for tap-hold keys
// Settles tap-hold as tap when same-hand key is pressed
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to function
```

**Validation**:
- No BILATERAL_COMBINATIONS references remain
- CHORDAL_HOLD and PERMISSIVE_HOLD are defined
- File still has valid C preprocessor syntax

---

### MOD-5: (Optional) Add Handedness Layout to Keymaps

**Files**:
- `keyboards/boardsource/lulu/keymaps/dario/keymap.c` (58 keys)
- `keyboards/lily58/keymaps/daranguiz_miryoku/keymap.c` (58 keys)
- `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap.c` (36 keys)

**Operation**: OPTIONALLY add explicit handedness definition

**Note**: Try without this first. QMK should auto-detect handedness for split keyboards. Only add if testing shows incorrect behavior.

**Changes if needed**:

**For Lulu and Lily58 (58 keys, 3x6+4 layout)**:
```c
// Chordal hold handedness layout for 58-key split keyboard
const char chordal_hold_layout[] PROGMEM =
    "LLLLLLL RRRRRRR\n"  // Top row (7 keys per side)
    "LLLLLLL RRRRRRR\n"  // Home row (7 keys per side)
    "LLLLLLL RRRRRRR\n"  // Bottom row (7 keys per side)
    " LLLL   RRRR  ";    // Thumb clusters (4 keys per side)
```

**For Skeletyl (36 keys, 3x5+3 layout)**:
```c
// Chordal hold handedness layout for 36-key split keyboard
const char chordal_hold_layout[] PROGMEM =
    "LLLLL RRRRR\n"  // Top row (5 keys per side)
    "LLLLL RRRRR\n"  // Home row (5 keys per side)
    "LLLLL RRRRR\n"  // Bottom row (5 keys per side)
    " LLL   RRR ";   // Thumb clusters (3 keys per side)
```

**Validation**:
- Layout string matches physical keyboard layout
- Each character maps to a key position
- Left/right split is correctly represented

---

### MOD-6: Review Other Config Files for Dependencies

**Files to review** (all 3 keymaps):
- `keyboards/boardsource/lulu/keymaps/dario/keymap_config.h`
- `keyboards/lily58/keymaps/daranguiz_miryoku/keymap_config.h`
- `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap_config.h`

**Operation**: REVIEW for any bilateral combinations references

**Action**:
- Search each file for "BILATERAL" or "bilateral"
- If found, remove or update references
- If not found, no changes needed

**Validation**:
- No references to BILATERAL_COMBINATIONS remain in any config file

---

### MOD-7: Review mods.c for Dependencies

**Files to review** (all 3 keymaps):
- `keyboards/boardsource/lulu/keymaps/dario/mods.c`
- `keyboards/lily58/keymaps/daranguiz_miryoku/mods.c`
- `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/mods.c`

**Operation**: REVIEW for any bilateral combinations dependencies

**Action**:
- Check if mods.c implementation depends on bilateral combinations behavior
- Test that custom mod logic still works with chordal hold
- Update if necessary

**Validation**:
- All mods.c files compile without errors
- Custom mod behavior functions correctly with chordal hold

---

## Build Validation Contract

### BUILD-1: Compile All Keymaps

**Commands**:
```bash
# Lulu (on personal branch after consolidation)
make boardsource/lulu/rp2040:dario

# Lily58 (on personal branch after consolidation)
make lily58:daranguiz_miryoku

# Skeletyl (on personal branch after consolidation)
make bastardkb/skeletyl:daranguiz_miryoku
```

**Success Criteria** (for each keyboard):
- Build completes without errors
- No warnings about undefined BILATERAL_COMBINATIONS
- Output firmware file generated

**Expected Output** (example for lulu):
```
Compiling: keyboards/boardsource/lulu/keymaps/dario/keymap.c                     [OK]
Compiling: keyboards/boardsource/lulu/keymaps/dario/mods.c                       [OK]
Compiling: keyboards/boardsource/lulu/keymaps/dario/features/caps_word.c         [OK]
...
Linking: .build/boardsource_lulu_rp2040_dario.elf                                [OK]
Creating binary load file for flashing: .build/boardsource_lulu_rp2040_dario.uf2 [OK]
```

---

### BUILD-2: Clean Build Test

**Commands**:
```bash
make clean
make boardsource/lulu/rp2040:dario
make lily58:daranguiz_miryoku
make bastardkb/skeletyl:daranguiz_miryoku
```

**Purpose**: Verify all builds work from clean state

**Success Criteria**:
- Clean succeeds
- All 3 keyboards build from scratch successfully
- No cached object files affect builds

---

## Functional Testing Contract

**Note**: These tests should be performed on each keyboard after flashing (Lulu, Lily58, Skeletyl). Only keyboards you have physical access to need functional testing; others can rely on successful compilation.

### TEST-1: Home Row Mods Basic Function

**Test Case**: Single mod-tap key held + opposite hand key

**Steps**:
1. Hold left home row mod (e.g., LSFT_T on T key)
2. Press opposite hand key (e.g., N key on right)
3. Release both keys

**Expected Behavior**:
- Shift modifier applied to N key
- Uppercase N appears
- No tap behavior triggered

**Chordal Hold Relevance**: Opposite hands, should allow hold behavior

**Test on**: All available keyboards (Lulu, Lily58, Skeletyl)

---

### TEST-2: Same-Hand Key Sequence (Chordal Hold Rule)

**Test Case**: Mod-tap key + same-hand key (fast roll)

**Steps**:
1. Press left home row mod (e.g., LSFT_T on T key)
2. Quickly press same-hand key (e.g., F key on left)
3. Release both keys

**Expected Behavior** (with chordal hold):
- Tap behavior triggered for T key (outputs 't')
- F key outputs normally ('f')
- Result: "tf" (no shift applied)

**Chordal Hold Relevance**: Same hand, triggers tap behavior per opposite hands rule

---

### TEST-3: Bilateral Mod Combination (Both Shifts)

**Test Case**: Both home row shift keys simultaneously

**Steps**:
1. Hold left shift mod-tap key
2. Hold right shift mod-tap key
3. Press another key

**Expected Behavior**:
- **Previous (bilateral combinations)**: Special bilateral combination triggered
- **New (chordal hold)**: May behave differently - document actual behavior

**Action**: Test and document any behavior change vs. bilateral combinations

---

### TEST-4: Permissive Hold Interaction

**Test Case**: Verify permissive hold works with chordal hold

**Steps**:
1. Press mod-tap key
2. Press and release another key before tapping term
3. Release mod-tap key

**Expected Behavior**:
- Mod-tap settles as hold (modifier applied to second key)
- This is permissive hold behavior

**Validation**: Permissive hold and chordal hold work together correctly

---

## Documentation Contract

### DOC-1: Document Behavior Changes

**Requirement**: Create migration notes documenting any functional differences

**Content**:
- List any bilateral combination behaviors that changed
- Document workarounds if needed
- Note any features no longer available

**Location**: Add section to quickstart.md or README in keymap directory

**Template**:
```markdown
## Migration from Bilateral Combinations to Chordal Hold

### Behavior Changes
- [Document what changed]

### Equivalents
- [What works the same]

### Known Limitations
- [What no longer works]
```

---

## Rollback Contract

If migration fails or behavior is unacceptable:

**ROLLBACK-1: Restore Bilateral Combinations**

```bash
# Restore quantum/action.c from before patch removal
git checkout HEAD~1 -- quantum/action.c

# Restore keymap config.h
git checkout HEAD~1 -- keyboards/boardsource/lulu/keymaps/dario/config.h

# Rebuild
make clean
make boardsource/lulu/rp2040:dario
```

**Success Criteria**:
- Bilateral combinations patch restored
- Keymap builds and functions as before migration
- Can defer migration to future work

---

## Summary

This contract defines:
1. **7 file modification operations** (MOD-1 through MOD-7):
   - MOD-1: Remove bilateral combinations from quantum/action.c
   - MOD-2: Migrate lulu/dario config
   - MOD-3: Migrate lily58/daranguiz_miryoku config
   - MOD-4: Migrate skeletyl/daranguiz_miryoku config
   - MOD-5: (Optional) Add handedness layouts
   - MOD-6: Review other config files
   - MOD-7: Review mods.c files
2. **2 build validation steps** (BUILD-1, BUILD-2) covering all 3 keyboards
3. **4 functional test cases** (TEST-1 through TEST-4) to be performed on available keyboards
4. **1 documentation requirement** (DOC-1)
5. **1 rollback procedure** (ROLLBACK-1)

**Scope**: 1 core file + 3 personal keymaps (Lulu, Lily58, Skeletyl)

All modifications are reversible. Testing validates behavioral equivalence to bilateral combinations (or documents differences).
