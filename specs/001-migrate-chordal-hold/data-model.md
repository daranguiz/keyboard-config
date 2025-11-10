# Data Model: QMK Branch Consolidation and Chordal Hold Migration

**Date**: 2025-11-07
**Feature**: 001-migrate-chordal-hold

## Overview

This is a repository refactoring task, not a traditional application with data models. The "entities" are git branches, source files, and configuration settings.

## Git Repository Structure

### Branches

| Branch | Purpose | Status | Actions |
|--------|---------|--------|---------|
| `lily58/miryoku-bilateral-combinations` | Historical branch with bilateral combinations work | SOURCE | Extract unique changes, preserve as backup |
| `master` (current) | Current working branch, includes commits from e3794835136f539e166cf9f7b3dcee7b47d55148 onward | SOURCE | Extract changes from e3794835136f539e166cf9f7b3dcee7b47d55148+, will be reset |
| `master` (after reset) | Clean tracking of upstream QMK | TARGET | Reset to upstream/master |
| `personal` | New branch for all personal customizations | TARGET | Create from reset master, apply consolidated changes |
| `001-migrate-chordal-hold` | Feature branch for this work | WORKING | Current branch, merge to personal when complete |

### Branch Relationships

```
upstream/master (QMK official)
    ↓
master (reset to upstream)
    ↓
personal (consolidated customizations)
    ↑
001-migrate-chordal-hold (this work)

# Archived for backup:
lily58/miryoku-bilateral-combinations
master (old, before reset)
```

## File Entities

### 1. Bilateral Combinations Patch Files

**Entity**: Patched QMK core file

**Location**: `quantum/action.c`

**State**: TO BE REVERTED

**Properties**:
- Lines to remove: 88 net additions (lines 58-60, 300-360, 415-420, 535-538, 545-548, 562-565, 744-747)
- Guard macro: `#ifdef BILATERAL_COMBINATIONS`
- Integration points: 5 action processing paths

**Validation**:
- After removal, quantum/action.c should match upstream version (for bilateral combinations code)
- Build should still succeed without BILATERAL_COMBINATIONS defined

### 2. Personal Keymap Files

**Entity**: Dario keymap for Lulu keyboard

**Location**: `keyboards/boardsource/lulu/keymaps/dario/`

**State**: TO BE MIGRATED

**Files**:
- `config.h` - Configuration (needs chordal hold migration)
- `keymap.c` - Keymap definition (may need chordal_hold_layout)
- `rules.mk` - Build rules (no changes expected)
- `keymap_config.h` - Additional config (review for bilateral combinations references)
- `mods.c` - Custom mods (review for bilateral combinations dependencies)
- `features/caps_word.{c,h}` - Caps word feature (no changes expected)

**Properties to Change**:

In `config.h`:
- REMOVE: `#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM`
- REMOVE: `// Note, only available with the manna_harbour patch`
- ADD: `#define CHORDAL_HOLD`
- ADD: `#define PERMISSIVE_HOLD` (or `HOLD_ON_OTHER_KEY_PRESS`)

Optionally in `keymap.c`:
- ADD: `const char chordal_hold_layout[] PROGMEM = "..."` if handedness needs explicit definition

**Validation**:
- Keymap compiles successfully: `make boardsource/lulu/rp2040:dario`
- Flash to hardware and test bilateral mod combinations (both shifts, etc.)
- Document any behavioral differences

### 3. Build Scripts

**Entity**: Keyboard build script

**Location**: `build_lulu.sh` (repository root)

**State**: NO CHANGE NEEDED

**Content**:
```bash
#!/bin/sh
make boardsource/lulu/rp2040:dario
```

**Validation**: Build script continues to work after migration

### 4. Inventory Documentation

**Entity**: Keyboard inventory file (NEW)

**Location**: `KEYBOARDS.md` (repository root)

**State**: TO BE CREATED

**Required Fields** (per constitution Principle IV):
- Keyboard name
- Path to keymap
- Hardware variant
- Key count
- Status (active/deprecated/etc.)

**Content**:
```markdown
# Personal Keyboards Inventory

## Active Keyboards

### Boardsource Lulu (RP2040)
- **Path**: keyboards/boardsource/lulu/keymaps/dario/
- **Hardware**: RP2040 variant
- **Keys**: 58 keys (split 3x6+4 layout)
- **Build**: `make boardsource/lulu/rp2040:dario` or `./build_lulu.sh`
- **Status**: Active
- **Features**: OLED, split keyboard, NKRO, combos, chordal hold
- **Last Updated**: 2025-11-07
```

**Validation**: File exists and contains accurate information

## Configuration State Transitions

### Bilateral Combinations → Chordal Hold Migration

**Current State (Bilateral Combinations)**:
```c
// In config.h:
#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM  // 300ms timeout
// Note, only available with the manna_harbour patch
```

**Target State (Chordal Hold)**:
```c
// In config.h:
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to work
```

**Optional Enhancement**:
```c
// In keymap.c (if explicit handedness needed):
const char chordal_hold_layout[] PROGMEM =
    "LLLLLLL RRRRRRR\n"  // Top row (58-key Lulu)
    "LLLLLLL RRRRRRR\n"  // Home row
    "LLLLLLL RRRRRRR\n"  // Bottom row
    " LLLL   RRRR  ";    // Thumb clusters
```

## Relationships and Dependencies

### File Dependencies

```
quantum/action.c (PATCHED)
    ← used by QMK build system
    ← referenced by keyboards/.../dario/config.h (via BILATERAL_COMBINATIONS)

keyboards/boardsource/lulu/keymaps/dario/config.h
    → defines BILATERAL_COMBINATIONS (TO BE REMOVED)
    → will define CHORDAL_HOLD (TO BE ADDED)

build_lulu.sh
    → invokes make boardsource/lulu/rp2040:dario
    → depends on keymap files being valid
```

### Migration Dependencies

**Sequential Order**:
1. First: Consolidate branches (preserve all changes)
2. Then: Remove bilateral combinations patch from quantum/action.c
3. Then: Migrate keymap configuration to chordal hold
4. Then: Test compilation and functionality
5. Finally: Create KEYBOARDS.md documentation

**Rationale**: Must preserve work before removing patch; must remove patch before testing new configuration.

## Validation Rules

### Build Validation

**Rule**: All keymaps must compile successfully after changes

**Test Command**: `make boardsource/lulu/rp2040:dario`

**Success Criteria**:
- Build completes without errors
- Firmware file generated (.uf2 for RP2040)

### Functional Validation

**Rule**: Bilateral modifier combinations must work as expected (or differences documented)

**Test Cases**:
1. Press both shift keys (home row mods) simultaneously → should trigger bilateral combination behavior
2. Press shift + opposite-hand letter key → should apply shift modifier normally
3. Press shift + same-hand letter key → should tap the underlying key per chordal hold rule

**Success Criteria**:
- Core functionality preserved
- Any behavioral differences documented in implementation notes

### Documentation Validation

**Rule**: KEYBOARDS.md must exist and be accurate (constitution Principle IV)

**Test**: File exists at `/Users/dario/git/qmk_firmware/KEYBOARDS.md`

**Success Criteria**:
- Contains all keyboards with dario keymaps
- Includes required fields per constitution

## Summary

This data model defines the git branch structure, file entities, configuration state transitions, and validation rules for the QMK branch consolidation and chordal hold migration. The primary entities are git branches (source and target), the bilateral combinations patch in quantum/action.c (to be removed), and the personal keymap configuration (to be migrated to chordal hold).
