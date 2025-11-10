# Context Restoration Handoff Document
**Feature**: 001-migrate-chordal-hold
**Date**: 2025-11-07
**Last Update**: Post-context-reset

## Quick Status Summary

**Current Branch**: `personal` (synced with origin/personal)
**Last Commit**: `d3d472fe77 WIP: Migrate to chordal hold and consolidate branches`
**Build Status**:
- ✅ Lulu (boardsource/lulu/rp2040:dario): **Compiles successfully**
- ⏳ Lily58 (lily58:daranguiz_miryoku): **Needs keycode updates** (same pattern as Lulu)
- ⏳ Skeletyl (bastardkb/skeletyl:daranguiz_miryoku): **Needs keycode updates** (same pattern as Lulu)

**Next Task**: Update deprecated keycodes in Lily58 and Skeletyl keymaps (T026-T027)

---

## Repository State

### Branch Structure
```
master (reset to upstream/master)
  ├─ QMK 0.30.6 (latest upstream)
  └─ Tracks: upstream/master

personal (1 commit ahead of master)
  ├─ Base: master (QMK 0.30.6)
  ├─ Commit: d3d472fe77 (WIP migration)
  └─ Contains: All 3 keymaps + chordal hold config

master-backup-before-reset
  └─ Preserves: Old master state before reset

lily58/miryoku-bilateral-combinations
  └─ Preserves: Old lily58 branch state

001-migrate-chordal-hold (current feature branch)
  └─ Contains: All spec files and this handoff doc
```

### Git Remotes
```
origin: <your fork>
upstream: https://github.com/qmk/qmk_firmware.git
```

---

## What Has Been Completed

### ✅ Phase 1-3: Foundation & Patch Removal (T001-T010)
- Identified changes on both source branches
- Configured upstream remote
- Created backup branches
- Reset master to upstream/master (QMK 0.30.6)
- Created personal branch
- Verified bilateral combinations patch already removed (upstream clean)

### ✅ Phase 4 (Partial): Chordal Hold Migration (T011-T025)
**Files Copied to personal branch**:
- `keyboards/boardsource/lulu/keymaps/dario/` (from master-backup)
- `keyboards/lily58/keymaps/daranguiz_miryoku/` (from lily58 branch)
- `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/` (from lily58 branch)
- `build_lulu.sh` (from master-backup)
- `users/daranguiz/` (from master-backup)

**Config Files Updated** (all 3 keymaps):
- Removed: `#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM`
- Removed: `#define IGNORE_MOD_TAP_INTERRUPT` (deprecated in 0.30.x)
- Added:
  ```c
  // Chordal hold: opposite hands rule for tap-hold keys
  // Settles tap-hold as tap when same-hand key is pressed
  #define CHORDAL_HOLD
  #define PERMISSIVE_HOLD  // Required for chordal hold to function

  // IGNORE_MOD_TAP_INTERRUPT removed - now default behavior in QMK 0.30.x
  ```

**Combos/Caps Word Temporarily Disabled** (all 3 keymaps):
- Set `COMBO_ENABLE = no` in rules.mk (marked with TODO)
- Commented out `caps_word.c` in rules.mk (marked with TODO)
- Commented out combo/caps_word code in mods.c (marked with TODO)
- **Reason**: QMK 0.30.x has combo introspection build errors
- **User's Intent**: Clean removal, no workarounds; re-enable later

**Deprecated Keycodes Fixed** (Lulu only):
- Updated `keyboards/boardsource/lulu/keymaps/dario/keymap.c`
- See "Keycode Mapping Reference" section below for exact changes
- **Result**: ✅ Lulu builds successfully!

---

## What Needs To Be Done Next

### 🎯 Immediate Priority: T026-T027 (Keycode Updates)

**Files needing updates**:
1. `keyboards/lily58/keymaps/daranguiz_miryoku/keymap.c`
2. `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap.c`

**Apply same keycode changes as Lulu** (see mapping reference below).

**Build commands to verify**:
```bash
# Lily58
make clean && make lily58:daranguiz_miryoku

# Skeletyl
make clean && make bastardkb/skeletyl:daranguiz_miryoku
```

**Expected result**: Both should compile successfully like Lulu.

---

## Keycode Mapping Reference

These are the QMK 0.30.x keycode changes that were applied to Lulu and need to be applied to Lily58 and Skeletyl:

### Mouse Movement
```c
KC_MS_L  → MS_LEFT
KC_MS_D  → MS_DOWN
KC_MS_U  → MS_UP
KC_MS_R  → MS_RGHT
```

### Mouse Wheel
```c
KC_WH_L  → MS_WHLL
KC_WH_D  → MS_WHLD
KC_WH_U  → MS_WHLU
KC_WH_R  → MS_WHLR
```

### Mouse Buttons
```c
KC_BTN1  → MS_BTN1
KC_BTN2  → MS_BTN2
KC_BTN3  → MS_BTN3
KC_BTN4  → MS_BTN4
KC_BTN5  → MS_BTN5
```

### RGB Controls
```c
RGB_TOG  → RM_TOGG
RGB_MOD  → RM_NEXT
RGB_HUI  → RM_HUEU
RGB_SAI  → RM_SATU
RGB_VAI  → RM_VALU
RGB_HUD  → RM_HUED
RGB_SAD  → RM_SATD
RGB_VAD  → RM_VALD
```

### Other Keys
```c
KC_SLCK  → KC_SCRL  (scroll lock)
RESET    → QK_BOOT  (reset to bootloader)
KC_LCTRL → KC_LCTL  (left control)
KC_RCTRL → KC_RCTL  (right control)
```

### Pattern for Finding Deprecated Keycodes

Look for these in MOUSE, MEDIA, FUN, and BUTTON layers in keymap.c:
- Any `KC_MS_*` or `KC_WH_*` or `KC_BTN*` → Replace with `MS_*`
- Any `RGB_*` → Replace with `RM_*` equivalent
- Any `RESET` → Replace with `QK_BOOT`
- Any `KC_SLCK` → Replace with `KC_SCRL`

---

## Layer Structure Reference

All three keymaps follow the Miryoku layout pattern with these layers:

```c
enum layers { BASE, EXTRA, TAP, BUTTON, NAV, MOUSE, MEDIA, NUM, SYM, FUN };
```

**Layers most likely to have deprecated keycodes**:
- **MOUSE**: Contains mouse movement, wheel, and button keycodes
- **MEDIA**: Contains RGB controls and media keys
- **FUN**: Contains function keys and system keys (RESET/KC_SLCK)
- **BUTTON**: Contains mouse button keycodes

---

## Build Commands Quick Reference

### Clean Build (Recommended)
```bash
make clean
make boardsource/lulu/rp2040:dario   # ✅ Works
make lily58:daranguiz_miryoku         # ⏳ Needs keycode updates
make bastardkb/skeletyl:daranguiz_miryoku  # ⏳ Needs keycode updates
```

### Using build_lulu.sh
```bash
./build_lulu.sh
```

### Build All Three (After T026-T027 Complete)
```bash
make clean
make boardsource/lulu/rp2040:dario && \
  make lily58:daranguiz_miryoku && \
  make bastardkb/skeletyl:daranguiz_miryoku
```

---

## File Locations Reference

### Config Files (All Updated)
- [keyboards/boardsource/lulu/keymaps/dario/config.h](keyboards/boardsource/lulu/keymaps/dario/config.h)
- [keyboards/lily58/keymaps/daranguiz_miryoku/config.h](keyboards/lily58/keymaps/daranguiz_miryoku/config.h)
- [keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/daranguiz_config.h](keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/daranguiz_config.h)

### Keymap Files (Lulu Done, Others Pending)
- [keyboards/boardsource/lulu/keymaps/dario/keymap.c](keyboards/boardsource/lulu/keymaps/dario/keymap.c) ✅
- [keyboards/lily58/keymaps/daranguiz_miryoku/keymap.c](keyboards/lily58/keymaps/daranguiz_miryoku/keymap.c) ⏳
- [keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap.c](keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap.c) ⏳

### Rules Files (All Updated - Combos Disabled)
- [keyboards/boardsource/lulu/keymaps/dario/rules.mk](keyboards/boardsource/lulu/keymaps/dario/rules.mk)
- [keyboards/lily58/keymaps/daranguiz_miryoku/rules.mk](keyboards/lily58/keymaps/daranguiz_miryoku/rules.mk)
- [keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/rules.mk](keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/rules.mk)

### Mods Files (All Updated - Combos/Caps Word Commented Out)
- [keyboards/boardsource/lulu/keymaps/dario/mods.c](keyboards/boardsource/lulu/keymaps/dario/mods.c)
- [keyboards/lily58/keymaps/daranguiz_miryoku/mods.c](keyboards/lily58/keymaps/daranguiz_miryoku/mods.c)
- [keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/mods.c](keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/mods.c)

---

## Remaining Tasks (After T026-T027)

### Phase 4 Completion (User Story 2)
- [X] T025: Build test Lulu ✅
- [ ] **T026: Build test Lily58** ⬅ **YOU ARE HERE**
- [ ] **T027: Build test Skeletyl** ⬅ **YOU ARE HERE**
- [ ] T028: Flash and functionally test keyboards
- [ ] T029: Document behavioral differences

### Phase 5 (User Story 3 - Consolidation)
- [ ] T030: Create KEYBOARDS.md inventory
- [ ] T031: Verify all customizations present
- [ ] T032: Stage changes
- [ ] T033: Create consolidated commit
- [ ] T034: Verify commit

### Phase 6 (User Story 4 - Final Sync)
- [ ] T035-T041: Final verification and sync

### Phase 7 (Polish)
- [ ] T042-T044: Documentation updates and validation

**See [tasks.md](tasks.md) for full task list.**

---

## Known Issues and TODOs

### Issue 1: Combos Disabled (All Keymaps)
**Status**: Temporarily disabled with TODO comments
**Reason**: QMK 0.30.x has combo introspection build errors
**User Intent**: Clean removal, no workarounds; re-enable later
**TODO**: After migration complete, investigate QMK 0.30.x combo support and re-enable

**Files affected**:
- All rules.mk: `COMBO_ENABLE = no  # TODO: Re-enable after fixing introspection errors`
- All mods.c: Combo code commented out with TODO comments

### Issue 2: Caps Word Disabled (All Keymaps)
**Status**: Temporarily disabled with TODO comments
**Reason**: Depends on combo feature (see Issue 1)
**TODO**: Re-enable after combos are working

**Files affected**:
- All rules.mk: `# SRC += ./features/caps_word.c  # TODO: Re-enable after build is working`
- All mods.c: `caps_word` code commented out with TODO comments

### Issue 3: Deprecated Keycodes (Lily58 & Skeletyl)
**Status**: ⏳ In progress (T026-T027)
**Solution**: Apply same keycode updates as Lulu (see mapping reference above)

---

## Testing Strategy (After Builds Succeed)

### Minimal Testing (If Only One Keyboard Available)
1. Build all three keymaps successfully (sufficient for lily58/skeletyl if you don't have them)
2. Flash firmware to Lulu (or whichever keyboard you have)
3. Test chordal hold behavior:
   - **Opposite hands**: Hold mod-tap on left hand, press key on right → Should apply modifier
   - **Same hand roll**: Quickly press mod-tap + same-hand key → Should tap both keys (no modifier)

### Full Testing (If All Keyboards Available)
1. Flash to all keyboards
2. Test chordal hold on each
3. Document any behavioral differences compared to bilateral combinations

**See [quickstart.md:329-351](quickstart.md) Phase 4.3 for detailed test cases.**

---

## Important Context from User

### User's Explicit Preferences
1. **No Hacks**: When combo build failed, user said: "let's just remove caps word for now. I don't want to introduce hacks at this stage."
2. **Clean Removal**: User wants clean disabling with TODO comments, not workarounds
3. **Git History**: User cares about clean git history and wanted changes committed before continuing

### User's Git Workflow
- User prefers clean, atomic commits
- User explicitly asked for tasks.md to be kept up to date
- User explicitly requested this handoff document for context restoration

---

## Quick Recovery Commands

### Check Current State
```bash
git status
git branch -a
git log master..personal --oneline
```

### View Last Commit
```bash
git show d3d472fe77
```

### Rebuild Everything
```bash
make clean
make boardsource/lulu/rp2040:dario
```

### Verify Chordal Hold Config
```bash
grep -r "CHORDAL_HOLD" keyboards/boardsource/lulu/keymaps/dario/
grep -r "CHORDAL_HOLD" keyboards/lily58/keymaps/daranguiz_miryoku/
grep -r "CHORDAL_HOLD" keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/
```

### Check for Remaining Bilateral References
```bash
grep -r "BILATERAL_COMBINATIONS" keyboards/
```

---

## Documentation Links

- [Feature Spec](spec.md) - Full specification
- [Implementation Plan](plan.md) - Detailed implementation strategy
- [Tasks](tasks.md) - All tasks with completion status
- [Research Notes](research.md) - QMK chordal hold research
- [Quickstart Guide](quickstart.md) - Step-by-step walkthrough
- [Data Model](data-model.md) - Git data structures
- [Git Operations Contract](contracts/git-operations.md) - Git safety protocols
- [Chordal Hold Migration Contract](contracts/chordal-hold-migration.md) - Migration requirements

**QMK Official Docs**: https://docs.qmk.fm/tap_hold#chordal-hold

---

## Workflow to Resume Implementation

1. **Read this document** ✅ (You're doing it!)
2. **Check current branch**: `git status` (should be on `personal`)
3. **Read lily58 keymap**: Review `keyboards/lily58/keymaps/daranguiz_miryoku/keymap.c`
4. **Apply keycode updates**: Use mapping reference above
5. **Build test**: `make clean && make lily58:daranguiz_miryoku`
6. **Repeat for skeletyl**: Same process
7. **Update tasks.md**: Mark T026 and T027 as complete
8. **Commit changes**: `git add -A && git commit -m "Update deprecated keycodes for lily58 and skeletyl"`
9. **Move to next phase**: Continue with T028 (functional testing) or T030 (KEYBOARDS.md creation)

---

## Final Notes

**Last Known Good State**: Lulu keymap builds successfully and is ready for testing.

**Immediate Goal**: Get lily58 and skeletyl keymaps building by applying the same keycode updates that fixed Lulu.

**Long-term Goal**: Complete all 44 tasks, create consolidated commit, sync with upstream, and have a working QMK fork with chordal hold instead of bilateral combinations patch.

**User's Ultimate Objective** (from spec):
> "I want to end up with a fork of QMK that is fully up to date with upstream, without the bilateral combinations patch, using native chordal hold instead, with master tracking upstream and personal branch containing all my customizations."

**Current Progress**: ~57% complete (25/44 tasks done)

---

**Document created**: 2025-11-07
**Last commit**: d3d472fe77
**Branch**: personal
**Next tasks**: T026-T027 (keycode updates for lily58/skeletyl)
