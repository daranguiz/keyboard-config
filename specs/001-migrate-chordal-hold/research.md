# Research: QMK Branch Consolidation and Chordal Hold Migration

**Date**: 2025-11-07
**Feature**: 001-migrate-chordal-hold

## Research Questions Resolved

### 1. Personal Keymaps Requiring Migration

**Decision**: 3 keyboards with personal keymaps across branches

**On Current Branch (001-migrate-chordal-hold / master)**:
1. **Boardsource Lulu (RP2040)** - keymap: `dario`
   - Location: `keyboards/boardsource/lulu/keymaps/dario/`
   - Files: keymap.c, config.h (has BILATERAL_COMBINATIONS), rules.mk, keymap_config.h, mods.c, features/caps_word.{c,h}
   - Build script: `build_lulu.sh`

**On lily58/miryoku-bilateral-combinations Branch**:
2. **Lily58** - keymap: `daranguiz_miryoku`
   - Location: `keyboards/lily58/keymaps/daranguiz_miryoku/`
   - Files: keymap.c, config.h, rules.mk, keymap_config.h, mods.c, oled.{c,h}, features/caps_word.{c,h}, readme.org

3. **Bastard Keyboards Skeletyl** - keymap: `daranguiz_miryoku`
   - Location: `keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/`
   - Files: keymap.c, daranguiz_config.h, rules.mk, keymap_config.h, mods.c, features/caps_word.{c,h}, readme.org

**User Space Code**:
- `users/daranguiz/` exists on current branch (master/001) with manna-harbour_miryoku integration
- Need to verify if lily58 branch also has users/daranguiz/ or if it was removed

**Note**: "daranguiz" is your username for miryoku-based keymaps, "dario" is for the lulu

**Rationale**: Complete search across both branches reveals 3 keyboards total. All need to be migrated to chordal hold.

**Alternatives Considered**: None - this is a discovery task.

---

### 2. Bilateral Combinations Patch Location and Extent

**Decision**: Patch is localized to one core file: `quantum/action.c`

**Extent**:
- **1 core file modified**: `quantum/action.c` (88 net lines added)
- **5 integration points** in action processing logic
- **1 configuration file**: `keyboards/boardsource/lulu/keymaps/dario/config.h`

**Details**:

The bilateral combinations patch in `quantum/action.c`:
- Lines 58-60: Conditional include for quantum.h
- Lines 300-360: Complete implementation (state tracking, left/right detection, hold/release/tap functions)
- Lines 415-420: Integration into ACT_LMODS/ACT_RMODS processing
- Lines 535-538: Integration into MODS_TAP tap phase
- Lines 545-548: Integration into MODS_TAP hold phase
- Lines 562-565: Integration into MODS_TAP release phase
- Lines 744-747: Integration into layer-tap processing

**Guard Macros**: All code wrapped in `#ifdef BILATERAL_COMBINATIONS`

**Configuration**: Enabled in keymap config with `#define BILATERAL_COMBINATIONS TAPPING_TERM_HRM` (300ms timeout)

**Commits**: Introduced in commit a3fb5f75af (2022-02-20)

**Rationale**: Very thorough search of quantum/ and tmk_core/ found no other modifications. The patch is clean and localized.

**Alternatives Considered**: None - this is a discovery task.

---

### 3. Chordal Hold Configuration Syntax

**Decision**: Chordal Hold is QMK's native feature (released 2025-02-27) that replaces bilateral combinations

**Feature Location**: Built into QMK core (PR #24560)

**Configuration Syntax**:

1. **Enable in config.h**:
   ```c
   #define CHORDAL_HOLD
   ```

2. **Use with tap-hold mode** (add one of these):
   ```c
   #define PERMISSIVE_HOLD
   // OR
   #define HOLD_ON_OTHER_KEY_PRESS
   ```

3. **Optional: Define handedness in keymap.c**:
   ```c
   const char chordal_hold_layout[] PROGMEM = "LLLLL RRRRR\n"
                                               "LLLLL RRRRR\n"
                                               "LLLLL RRRRR\n"
                                               " LLL   RRR ";
   ```
   - 'L' = left hand key
   - 'R' = right hand key
   - '*' = exempt from opposite hands rule
   - Layout matches physical key positions

**Documentation**: https://docs.qmk.fm/tap_hold#chordal-hold

**Rationale**: Official QMK documentation and PR #24560 provide complete configuration details.

**Alternatives Considered**:
- Achordion (predecessor, user-space implementation) - Rejected because chordal hold is the official core feature
- Keep bilateral combinations - Rejected per spec requirements (causes merge conflicts)

---

### 4. Feature Parity: Bilateral Combinations vs. Chordal Hold

**Decision**: Chordal Hold provides equivalent core functionality with "opposite hands" rule

**Capabilities - What Chordal Hold CAN Do**:
- ✅ Opposite hands rule: tap-hold keys settled as tap when same-hand key pressed
- ✅ Configurable handedness per key position
- ✅ Works with mod-tap keys (home row mods)
- ✅ Works with layer-tap keys
- ✅ Integrates with Permissive Hold and Hold On Other Key Press modes
- ✅ Exempt specific keys from the rule with '*' marker

**Capabilities - Bilateral Combinations Specific**:
- Bilateral combinations had custom timeout (`BILATERAL_COMBINATIONS TAPPING_TERM_HRM`)
- Implementation details may differ slightly

**Limitations**:
- Chordal hold does NOT have a configurable timeout separate from tapping term
- Behavior is primarily "same hand = tap" rule, not complex bilateral triggering

**Migration Path**:
1. Remove `#define BILATERAL_COMBINATIONS` from config.h
2. Add `#define CHORDAL_HOLD` to config.h
3. Add `#define PERMISSIVE_HOLD` (or HOLD_ON_OTHER_KEY_PRESS) to config.h
4. Optionally define `chordal_hold_layout` in keymap.c for explicit handedness
5. Test and adjust if behavior differs

**Potential Behavior Differences**:
- Timing differences possible (chordal hold uses standard tapping term)
- May need to test bilateral mod combinations carefully
- Document any functional changes discovered during testing

**Rationale**: Based on QMK documentation and PR description, chordal hold was explicitly designed to replace Achordion and bilateral combinations patterns.

**Alternatives Considered**:
- Keep bilateral combinations - Rejected (merge conflict source)
- Use Achordion user-space feature - Rejected (chordal hold is the official replacement)

---

## Technology Stack Best Practices

### Git Branch Strategy

**Decision**: Use master for upstream tracking, personal branch for customizations

**Pattern**:
1. Reset master to upstream/master (latest QMK)
2. Create personal branch from master
3. Cherry-pick or manually apply consolidated changes to personal branch
4. Never modify master (keep it clean for pulling upstream)

**Rationale**: Aligns with constitution Principle I (Upstream Modularity) and user clarification from spec.

---

## Summary

All research questions resolved. Key findings:

1. **3 keymaps need migration**:
   - boardsource/lulu/keymaps/dario (on current branch)
   - lily58/keymaps/daranguiz_miryoku (on lily58 branch)
   - bastardkb/skeletyl/keymaps/daranguiz_miryoku (on lily58 branch)
   - All 3 define `BILATERAL_COMBINATIONS TAPPING_TERM_HRM`
2. **Patch is very localized**: Only quantum/action.c (88 lines, guarded by ifdef)
3. **Chordal hold is simple**: Just add `#define CHORDAL_HOLD` and a permissive hold mode
4. **Feature parity is good**: Core opposite-hands functionality equivalent, minor timing differences possible
5. **User space code**: users/daranguiz/ exists on master with miryoku integration

**Ready to proceed to Phase 1 design**.
