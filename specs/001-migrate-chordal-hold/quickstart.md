# Quickstart: QMK Branch Consolidation and Chordal Hold Migration

**Feature**: 001-migrate-chordal-hold
**Branch**: 001-migrate-chordal-hold
**Date**: 2025-11-07

## Overview

This guide provides step-by-step instructions to consolidate QMK fork branches and migrate from the bilateral combinations patch to QMK's native chordal hold feature.

## Prerequisites

- [x] Git repository with lily58/miryoku-bilateral-combinations and master branches
- [x] QMK build environment configured
- [x] Physical Lulu keyboard for testing (optional but recommended)

## Quick Reference

**Total Time Estimate**: 2-3 hours (including testing)

**Phases**:
1. Discovery & Backup (15 min)
2. Branch Consolidation (30 min)
3. Chordal Hold Migration (45 min)
4. Testing & Validation (60 min)

---

## Phase 1: Discovery & Backup

### Step 1.1: Review Changes on lily58 Branch

```bash
git checkout lily58/miryoku-bilateral-combinations
git log --oneline --decorate
git diff master...lily58/miryoku-bilateral-combinations > /tmp/lily58-changes.diff
```

**Action**: Review /tmp/lily58-changes.diff to understand what's unique on this branch.

---

### Step 1.2: Review Changes on master from e379483513+

```bash
git checkout master
git log --oneline e3794835136f539e166cf9f7b3dcee7b47d55148..HEAD
git diff e3794835136f539e166cf9f7b3dcee7b47d55148..HEAD > /tmp/master-recent-changes.diff
```

**Action**: Review /tmp/master-recent-changes.diff to understand recent master changes.

---

### Step 1.3: Configure Upstream Remote

```bash
git remote -v
# If upstream not present:
git remote add upstream https://github.com/qmk/qmk_firmware.git
git fetch upstream
```

**Verify**: `git remote -v` shows upstream → qmk/qmk_firmware

---

### Step 1.4: Create Backup Branches

```bash
git checkout master
git branch master-backup-before-reset

git checkout lily58/miryoku-bilateral-combinations
# This branch already exists, no backup needed (we're keeping it per spec)
```

**Verify**: `git branch` shows master-backup-before-reset

---

## Phase 2: Branch Consolidation

### Step 2.1: Reset master to Upstream

⚠️ **WARNING**: This is destructive. Ensure backups exist (Step 1.4).

```bash
git checkout master
git fetch upstream
git reset --hard upstream/master
```

**Verify**: `git log master..upstream/master` shows no output (branches synced)

---

### Step 2.2: Create personal Branch

```bash
git checkout master
git checkout -b personal
```

**Verify**: `git branch --show-current` outputs "personal"

---

### Step 2.3: Apply Consolidated Changes

**Option A: Manual file copying** (recommended for first iteration):

```bash
# Still on personal branch

# Copy personal keymap from old master
git checkout master-backup-before-reset -- keyboards/boardsource/lulu/keymaps/dario/

# Copy any other personal files identified in discovery (build scripts, etc.)
git checkout master-backup-before-reset -- build_lulu.sh

# Stage changes
git add keyboards/boardsource/lulu/keymaps/dario/
git add build_lulu.sh
```

**Option B: Cherry-pick specific commits** (if changes were clean commits):

```bash
# Cherry-pick commits from master-backup or lily58 branch
git cherry-pick <commit-hash>
```

**Don't commit yet** - we'll do chordal hold migration first, then commit everything together.

---

## Phase 3: Chordal Hold Migration

### Step 3.1: Remove Bilateral Combinations Patch from quantum/action.c

**Current Location**: Working on personal branch

```bash
# Open quantum/action.c in editor
# Remove all bilateral combinations code (see contracts/chordal-hold-migration.md MOD-1)
```

**Lines to remove**:
- Lines 58-60: `#if (BILATERAL_COMBINATIONS + 0) ... #endif`
- Lines 300-360: Entire bilateral combinations implementation
- Lines 415-420, 535-538, 545-548, 562-565, 744-747: Integration points

**Quick method**: Revert quantum/action.c to upstream version:
```bash
git checkout upstream/master -- quantum/action.c
```

**Verify**: `grep -i bilateral quantum/action.c` returns no results

---

### Step 3.2: Update Keymap config.h

**File**: `keyboards/boardsource/lulu/keymaps/dario/config.h`

**Remove** (around line 19-20):
```c
// Note, only available with the manna_harbour patch
#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM
```

**Add**:
```c
// Chordal hold: opposite hands rule for tap-hold keys
// Settles tap-hold as tap when same-hand key is pressed
#define CHORDAL_HOLD
#define PERMISSIVE_HOLD  // Required for chordal hold to function
```

**Verify**: `grep -i bilateral keyboards/boardsource/lulu/keymaps/dario/config.h` returns no results

---

### Step 3.3: (Optional) Add Handedness Layout

**File**: `keyboards/boardsource/lulu/keymaps/dario/keymap.c`

**Add** (after includes, before keymap definition - ONLY if auto-detection doesn't work):
```c
// Chordal hold handedness layout for Lulu 58-key split keyboard
const char chordal_hold_layout[] PROGMEM =
    "LLLLLLL RRRRRRR\n"  // Top row
    "LLLLLLL RRRRRRR\n"  // Home row
    "LLLLLLL RRRRRRR\n"  // Bottom row
    " LLLL   RRRR  ";    // Thumb clusters
```

**Note**: Try without this first. QMK may auto-detect handedness for split keyboards.

---

### Step 3.4: Create KEYBOARDS.md

**File**: `KEYBOARDS.md` (repository root)

```bash
cat > KEYBOARDS.md << 'EOF'
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

### Lily58
- **Path**: keyboards/lily58/keymaps/daranguiz_miryoku/
- **Hardware**: Standard lily58
- **Keys**: 58 keys (split 3x6+4 layout)
- **Build**: `make lily58:daranguiz_miryoku`
- **Status**: Active (migrated from lily58 branch)
- **Features**: OLED, split keyboard, miryoku layout, chordal hold
- **Last Updated**: 2025-11-07

### Bastard Keyboards Skeletyl
- **Path**: keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/
- **Hardware**: Skeletyl (36-key)
- **Keys**: 36 keys (split 3x5+3 layout)
- **Build**: `make bastardkb/skeletyl:daranguiz_miryoku`
- **Status**: Active (migrated from lily58 branch)
- **Features**: Split keyboard, miryoku layout, chordal hold
- **Last Updated**: 2025-11-07

---

**Last Inventory Update**: 2025-11-07
EOF
```

**Verify**: `cat KEYBOARDS.md` shows the content

---

### Step 3.5: Commit Consolidated Changes

```bash
git add -A
git status  # Review what's staged

git commit -m "Consolidated personal changes: chordal hold migration

- Migrated 3 keymaps to chordal hold:
  * boardsource/lulu/keymaps/dario
  * lily58/keymaps/daranguiz_miryoku
  * bastardkb/skeletyl/keymaps/daranguiz_miryoku
- Removed bilateral combinations patch from quantum/action.c
- Added CHORDAL_HOLD and PERMISSIVE_HOLD to all keymap configs
- Created KEYBOARDS.md inventory (constitution requirement)
- Preserved users/daranguiz/ user space code

This consolidates changes from lily58/miryoku-bilateral-combinations
and master (from e3794835136f539e166cf9f7b3dcee7b47d55148 onward).

Replaces bilateral combinations patch with QMK native chordal hold.
Eliminates merge conflicts with upstream QMK.
"
```

**Verify**: `git log -1` shows the commit

---

## Phase 4: Testing & Validation

### Step 4.1: Build Test

**Build all 3 keyboards**:

```bash
make clean

# Build Lulu
make boardsource/lulu/rp2040:dario

# Build Lily58
make lily58:daranguiz_miryoku

# Build Skeletyl
make bastardkb/skeletyl:daranguiz_miryoku
```

**Expected Output** (for each keyboard):
```
Compiling: keyboards/.../keymap.c                      [OK]
Compiling: keyboards/.../mods.c                        [OK]
...
Linking: .build/..._....elf                            [OK]
Creating binary load file for flashing: .build/...     [OK]
```

**If any build fails**: See Troubleshooting section below.

---

### Step 4.2: Flash to Keyboards (Optional)

**Flash whichever keyboards you have physical access to**:

```bash
# Lulu (RP2040 - put in bootloader mode first)
make boardsource/lulu/rp2040:dario:flash
# Or copy: cp .build/boardsource_lulu_rp2040_dario.uf2 /Volumes/RPI-RP2/

# Lily58 (put in bootloader mode first)
make lily58:daranguiz_miryoku:flash

# Skeletyl (put in bootloader mode first)
make bastardkb/skeletyl:daranguiz_miryoku:flash
```

---

### Step 4.3: Functional Testing

**Perform on each keyboard you have access to** (Lulu, Lily58, Skeletyl):

**Test Case 1: Opposite Hand Mod-Tap** (should trigger hold)
1. Hold left shift mod-tap (e.g., T key)
2. Press right-hand key (e.g., N key)
3. **Expected**: Uppercase N (shift modifier applied)

**Test Case 2: Same Hand Roll** (should trigger tap per chordal hold)
1. Press left shift mod-tap (e.g., T key)
2. Quickly press same-hand key (e.g., F key)
3. **Expected**: "tf" (tap behavior, no shift)

**Test Case 3: Bilateral Mods** (document any behavior change)
1. Hold both shift mod-taps simultaneously
2. **Expected**: [Test and document actual behavior]
3. **Compare**: Note any difference from bilateral combinations

**Note**: If you only have access to one keyboard, successful compilation of the others is sufficient validation.

**Document Results**: Add findings to migration notes if behavior differs on any keyboard.

---

### Step 4.4: Verify Branch Structure

```bash
# master should track upstream
git checkout master
git log --oneline -5

# personal should have consolidated changes
git checkout personal
git log --oneline -5
git log master..personal  # Should show consolidated commit

# Old branches still exist as backup
git branch -a | grep -E '(lily58|master-backup)'
```

**Expected**:
- master tracks upstream QMK
- personal has 1 consolidated commit on top of master
- Old branches preserved

---

## Phase 5: Complete Feature Work

### Step 5.1: Merge Feature Branch to personal

```bash
git checkout personal
git merge 001-migrate-chordal-hold --no-ff -m "Merge branch consolidation and chordal hold migration

Completes feature 001: QMK branch consolidation and chordal hold migration
"
```

**Note**: This may create a merge commit if there are differences, or it may fast-forward if 001 branch is ahead of personal.

---

### Step 5.2: Final Validation

```bash
# Build from personal branch
git checkout personal
make clean
make boardsource/lulu/rp2040:dario
```

**Success Criteria**:
- Build succeeds
- Firmware file created
- All tests passed in Phase 4.3

---

## Success Checklist

- [ ] Old branches backed up (lily58, master-backup-before-reset)
- [ ] master reset to upstream/master
- [ ] personal branch created from master
- [ ] Bilateral combinations patch removed from quantum/action.c
- [ ] Keymap migrated to chordal hold (CHORDAL_HOLD defined)
- [ ] KEYBOARDS.md created
- [ ] Build succeeds: `make boardsource/lulu/rp2040:dario`
- [ ] Consolidated commit on personal branch
- [ ] Functional testing completed
- [ ] Any behavior changes documented

---

## Troubleshooting

### Build Error: "BILATERAL_COMBINATIONS undeclared"

**Cause**: References to BILATERAL_COMBINATIONS still exist in code

**Fix**:
```bash
# Find remaining references
grep -r "BILATERAL_COMBINATIONS" keyboards/boardsource/lulu/keymaps/dario/

# Remove or comment out those references
```

---

### Build Error: "chordal_hold_layout has incorrect size"

**Cause**: Handedness layout string doesn't match keyboard matrix size

**Fix**: Remove `chordal_hold_layout` from keymap.c - let QMK auto-detect for split keyboards

---

### Behavior Difference: Same-hand rolls don't trigger tap

**Cause**: Chordal hold may not be working, or configuration is incorrect

**Fix**:
1. Verify `#define CHORDAL_HOLD` exists in config.h
2. Verify `#define PERMISSIVE_HOLD` exists in config.h
3. Check that handedness is correctly detected (for split keyboards)
4. Try adding explicit `chordal_hold_layout` if auto-detection fails

---

### Git Error: "Cannot reset, uncommitted changes"

**Cause**: Working directory has uncommitted changes before reset

**Fix**:
```bash
git status
git stash  # Save changes temporarily
git reset --hard upstream/master  # Proceed with reset
git stash pop  # Restore changes if needed (may conflict)
```

---

## Rollback Procedures

### Rollback: Restore Old master

```bash
git checkout master
git reset --hard master-backup-before-reset
```

### Rollback: Delete personal Branch and Start Over

```bash
git branch -D personal
git checkout master
# Start over from Phase 2
```

### Rollback: Restore Bilateral Combinations

```bash
git checkout personal
git checkout master-backup-before-reset -- quantum/action.c
git checkout master-backup-before-reset -- keyboards/boardsource/lulu/keymaps/dario/config.h
make clean
make boardsource/lulu/rp2040:dario
```

---

## Next Steps

After successful completion:

1. **Update CLAUDE.md** if needed (document chordal hold usage)
2. **Test extensively** on physical keyboard over several days
3. **Consider syncing master** with latest upstream periodically
4. **Future work**: Address Principles II/III (keymap consistency across keyboards)
5. **Future work**: Add visual keymap documentation (Principle V)

---

## Reference Documentation

- [QMK Chordal Hold Docs](https://docs.qmk.fm/tap_hold#chordal-hold)
- [Feature Spec](spec.md)
- [Implementation Plan](plan.md)
- [Research Notes](research.md)
- [Data Model](data-model.md)
- [Git Operations Contract](contracts/git-operations.md)
- [Chordal Hold Migration Contract](contracts/chordal-hold-migration.md)
