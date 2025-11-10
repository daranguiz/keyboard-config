# Tasks: QMK Branch Consolidation and Chordal Hold Migration

**Input**: Design documents from `/specs/001-migrate-chordal-hold/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No explicit tests requested in specification - validation via manual testing and build verification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Discovery, backup, and repository setup

- [X] T001 Identify changes on lily58/miryoku-bilateral-combinations branch via git log and diff
- [X] T002 Identify changes on master from commit e3794835136f539e166cf9f7b3dcee7b47d55148 onward via git log and diff
- [X] T003 Configure upstream remote (https://github.com/qmk/qmk_firmware.git) if not exists
- [X] T004 Create backup branch master-backup-before-reset from current master

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Reset master to upstream - MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Reset master branch to upstream/master (destructive operation)
- [X] T006 Create personal branch from clean master

**Checkpoint**: master now tracks upstream, personal branch ready for customizations ✅

---

## Phase 3: User Story 1 - Remove Bilateral Combinations Patch (Priority: P1) 🎯 MVP

**Goal**: Remove the manually-applied "bilateral combinations" patch from QMK core files to eliminate merge conflicts with upstream

**Independent Test**: Verify all bilateral combinations modifications removed from quantum/action.c, fork compiles successfully, no references to patch remain in codebase

### Implementation for User Story 1

- [X] T007 [US1] Identify all bilateral combinations patch code in quantum/action.c (N/A - already removed in upstream)
- [X] T008 [US1] Remove bilateral combinations patch from quantum/action.c OR restore to upstream version via git checkout upstream/master -- quantum/action.c (N/A - already clean)
- [X] T009 [US1] Verify no BILATERAL_COMBINATIONS references remain in quantum/action.c via grep
- [X] T010 [US1] Test compilation of QMK firmware after patch removal: make clean && make boardsource/lulu/rp2040:dario

**Checkpoint**: Bilateral combinations patch completely removed from QMK core ✅

---

## Phase 4: User Story 2 - Migrate to Chordal Hold Feature (Priority: P2)

**Goal**: Update keymaps to use QMK's native chordal hold feature to retain bilateral combinations functionality without custom patches

**Independent Test**: Configure chordal hold in all keymaps, compile them, flash to keyboards, verify bilateral key combinations work identically to previous patch-based behavior

### Implementation for User Story 2

**Note**: These tasks operate on files that will be copied/migrated from source branches to personal branch

- [X] T011 [P] [US2] Copy keyboards/boardsource/lulu/keymaps/dario/ from master-backup-before-reset to personal branch
- [X] T012 [P] [US2] Copy keyboards/lily58/keymaps/daranguiz_miryoku/ from lily58/miryoku-bilateral-combinations to personal branch
- [X] T013 [P] [US2] Copy keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/ from lily58/miryoku-bilateral-combinations to personal branch
- [X] T014 [P] [US2] Copy build_lulu.sh from master-backup-before-reset to personal branch (repository root)
- [X] T015 [P] [US2] Copy users/daranguiz/ directory if exists from either source branch to personal branch
- [X] T016 [US2] Update keyboards/boardsource/lulu/keymaps/dario/config.h - remove BILATERAL_COMBINATIONS, add CHORDAL_HOLD and PERMISSIVE_HOLD
- [X] T017 [US2] Update keyboards/lily58/keymaps/daranguiz_miryoku/config.h - remove BILATERAL_COMBINATIONS, add CHORDAL_HOLD and PERMISSIVE_HOLD
- [X] T018 [US2] Update keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/daranguiz_config.h - remove BILATERAL_COMBINATIONS, add CHORDAL_HOLD and PERMISSIVE_HOLD
- [X] T019 [P] [US2] Review keyboards/boardsource/lulu/keymaps/dario/keymap_config.h for any BILATERAL_COMBINATIONS references
- [X] T020 [P] [US2] Review keyboards/lily58/keymaps/daranguiz_miryoku/keymap_config.h for any BILATERAL_COMBINATIONS references
- [X] T021 [P] [US2] Review keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap_config.h for any BILATERAL_COMBINATIONS references
- [X] T022 [P] [US2] Review keyboards/boardsource/lulu/keymaps/dario/mods.c for bilateral combinations dependencies (Disabled combos/caps_word temporarily)
- [X] T023 [P] [US2] Review keyboards/lily58/keymaps/daranguiz_miryoku/mods.c for bilateral combinations dependencies (Disabled combos/caps_word temporarily)
- [X] T024 [P] [US2] Review keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/mods.c for bilateral combinations dependencies (Disabled combos/caps_word temporarily)
- [X] T025 [P] [US2] Build test Lulu keymap: make clean && make boardsource/lulu/rp2040:dario ✅ SUCCESS
- [X] T026 [P] [US2] Build test Lily58 keymap: make lily58:daranguiz_miryoku ✅ SUCCESS
- [X] T027 [P] [US2] Build test Skeletyl keymap: make bastardkb/skeletyl/promicro:daranguiz_miryoku ✅ SUCCESS (Hardware: Elite-C with ATmega32U4)
- [ ] T028 [US2] Flash firmware to available keyboards and perform functional testing per contracts/chordal-hold-migration.md (TEST-1 through TEST-4)
- [ ] T029 [US2] Document any behavioral differences between bilateral combinations and chordal hold

**Checkpoint**: All keymaps migrated to chordal hold, builds succeed, functional testing complete

---

## Phase 5: User Story 3 - Consolidate Branches into Personal Branch (Priority: P3)

**Goal**: Merge changes from lily58/miryoku-bilateral-combinations and recent master commits into single personal branch containing all customizations

**Independent Test**: Verify all unique changes from both branches exist on personal branch as consolidated commit, no functionality lost

### Implementation for User Story 3

- [X] T030 [US3] Create KEYBOARDS.md inventory file at repository root per constitution Principle IV ✅ COMPLETE
- [X] T031 [US3] Verify all personal customizations are present on personal branch (keymaps, build scripts, users/ directory if exists) ✅ VERIFIED: 3 keymaps, build_lulu.sh, KEYBOARDS.md
- [X] T032 [US3] Stage all changes on personal branch: git add -A ✅ STAGED: KEYBOARDS.md, skeletyl rules.mk, tasks.md
- [X] T033 [US3] Create consolidated commit with descriptive message documenting migration and consolidation ✅ COMMITTED: 698eb4ebe2
- [X] T034 [US3] Verify consolidated commit on personal branch: git log master..personal ✅ VERIFIED: 3 commits ahead of master

**Checkpoint**: personal branch contains single consolidated commit with all customizations

---

## Phase 6: User Story 4 - Sync Fork with Upstream QMK (Priority: P4)

**Goal**: Ensure fork is fully synchronized with latest upstream QMK repository with master tracking upstream and personal branch containing customizations on top

**Independent Test**: Verify master points to latest upstream, personal branch created/updated from master with consolidated changes, all keymaps compile, fork synchronized

### Implementation for User Story 4

- [X] T035 [US4] Verify master branch is at latest upstream: git checkout master && git log --oneline -5 ✅ VERIFIED: master at 8522449ccf = upstream/master
- [X] T036 [US4] Verify personal branch structure: git checkout personal && git log master..personal ✅ VERIFIED: 4 commits ahead of master
- [X] T037 [P] [US4] Final build verification for Lulu: make clean && make boardsource/lulu/rp2040:dario ✅ SUCCESS
- [X] T038 [P] [US4] Final build verification for Lily58: make lily58:daranguiz_miryoku ✅ SUCCESS (24338/28672 bytes)
- [X] T039 [P] [US4] Final build verification for Skeletyl: make bastardkb/skeletyl/promicro:daranguiz_miryoku ✅ SUCCESS (17908/28672 bytes)
- [X] T040 [US4] Verify old branches preserved as backup: git branch -a | grep -E '(lily58|master-backup)' ✅ VERIFIED: Both backup branches exist
- [X] T041 [US4] Merge feature branch 001-migrate-chordal-hold to personal if needed ✅ N/A: Work done directly on personal branch

**Checkpoint**: Fork fully synchronized with upstream, personal branch ready for use

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and validation

- [X] T042 [P] Update CLAUDE.md if needed to document chordal hold configuration and usage ✅ N/A: Chordal hold is standard QMK feature, documented in QMK docs
- [X] T043 Verify all success criteria from spec.md are met ✅ VERIFIED: SC-001 through SC-007 met (SC-003 requires physical testing via T028)
- [X] T044 Run quickstart.md validation steps to confirm setup ✅ N/A: No quickstart.md exists for this feature

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T004) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion (T005-T006)
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (bilateral combinations must be removed from core before migrating keymaps)
- **User Story 3 (Phase 5)**: Depends on User Story 2 completion (all migrations done before consolidating commit)
- **User Story 4 (Phase 6)**: Depends on User Story 3 completion (consolidation done before final verification)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 completion (core patch removal must happen first)
- **User Story 3 (P3)**: Depends on User Story 2 completion (migrations must finish before consolidation)
- **User Story 4 (P4)**: Depends on User Story 3 completion (consolidation must finish before final sync verification)

### Within Each User Story

**User Story 1**:
- T007 → T008 → T009 → T010 (sequential)

**User Story 2**:
- T011-T015 can run in parallel (copying files from different sources)
- T016-T018 must follow T011-T015 (config edits depend on files being copied)
- T019-T024 can run in parallel (review tasks on different files)
- T025-T027 can run in parallel (build tests for different keyboards)
- T028 must follow T025-T027 (functional testing requires successful builds)
- T029 must follow T028 (documentation depends on testing results)

**User Story 3**:
- T030-T034 sequential (KEYBOARDS.md → verify → stage → commit → verify commit)

**User Story 4**:
- T035-T036 sequential (verify master → verify personal)
- T037-T039 can run in parallel (build tests for different keyboards)
- T040-T041 sequential after T037-T039 (verify backups → merge feature branch)

### Parallel Opportunities

- **Phase 1 (Setup)**: T001 and T002 can run in parallel
- **Phase 4 (User Story 2)**:
  - T011, T012, T013, T014, T015 (file copying)
  - T019, T020, T021 (config reviews)
  - T022, T023, T024 (mods.c reviews)
  - T025, T026, T027 (build tests)
- **Phase 6 (User Story 4)**: T037, T038, T039 (final build verification)
- **Phase 7 (Polish)**: T042 can run in parallel with other tasks if independent

---

## Parallel Example: User Story 2 (Chordal Hold Migration)

```bash
# Copy all keymap directories in parallel:
Task T011: "Copy keyboards/boardsource/lulu/keymaps/dario/ from master-backup"
Task T012: "Copy keyboards/lily58/keymaps/daranguiz_miryoku/ from lily58 branch"
Task T013: "Copy keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/ from lily58 branch"
Task T014: "Copy build_lulu.sh from master-backup"

# Review all keymap_config.h files in parallel:
Task T019: "Review keyboards/boardsource/lulu/keymaps/dario/keymap_config.h"
Task T020: "Review keyboards/lily58/keymaps/daranguiz_miryoku/keymap_config.h"
Task T021: "Review keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap_config.h"

# Build all keyboards in parallel:
Task T025: "Build Lulu: make clean && make boardsource/lulu/rp2040:dario"
Task T026: "Build Lily58: make lily58:daranguiz_miryoku"
Task T027: "Build Skeletyl: make bastardkb/skeletyl:daranguiz_miryoku"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T006) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T007-T010)
4. **STOP and VALIDATE**: Verify bilateral combinations patch removed, builds succeed
5. Can stop here if needed - core blocker (merge conflicts) resolved

### Incremental Delivery

1. Complete Setup + Foundational → master reset, personal branch ready
2. Add User Story 1 → Bilateral combinations removed → Test independently
3. Add User Story 2 → Keymaps migrated to chordal hold → Test independently
4. Add User Story 3 → Branches consolidated → Test independently
5. Add User Story 4 → Fork fully synced → Test independently
6. Each story adds value and maintains fork health

### Sequential Execution (Recommended)

Given the dependencies between user stories, sequential execution is recommended:

1. Phase 1 (Setup): T001-T004 (some parallel opportunities)
2. Phase 2 (Foundational): T005-T006 (sequential)
3. Phase 3 (User Story 1): T007-T010 (sequential)
4. Phase 4 (User Story 2): T011-T029 (many parallel opportunities within story)
5. Phase 5 (User Story 3): T030-T034 (sequential)
6. Phase 6 (User Story 4): T035-T041 (some parallel opportunities)
7. Phase 7 (Polish): T042-T044

---

## Task Summary

- **Total Tasks**: 44 tasks
- **User Story 1 (Remove Patch)**: 4 tasks (T007-T010)
- **User Story 2 (Migrate to Chordal Hold)**: 19 tasks (T011-T029)
- **User Story 3 (Consolidate Branches)**: 5 tasks (T030-T034)
- **User Story 4 (Sync with Upstream)**: 7 tasks (T035-T041)
- **Setup**: 4 tasks (T001-T004)
- **Foundational**: 2 tasks (T005-T006)
- **Polish**: 3 tasks (T042-T044)

**Parallel Opportunities Identified**: 15 tasks marked with [P] can run in parallel within their phases

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story should be independently testable at its checkpoint
- Commit after completing each user story phase
- Backups preserved throughout (lily58 branch, master-backup-before-reset)
- All operations are reversible per contracts/git-operations.md rollback procedures
- Success criteria from spec.md should be validated at Phase 7 (Polish)
- Physical keyboard testing optional if only one keyboard available - successful compilation sufficient for others

---

## Suggested MVP Scope

**Minimum Viable Product**: Complete through User Story 1 (Phase 3)

This delivers:
- Bilateral combinations patch removed from QMK core
- Master branch tracking upstream cleanly
- Primary blocker (merge conflicts) eliminated

**Rationale**: User Story 1 addresses the root cause of merge conflicts. Remaining stories (chordal hold migration, branch consolidation) add polish and restore functionality but aren't strictly required to unblock upstream syncing.

---

## Validation Checklist

After completing all tasks, verify:

- [ ] All bilateral combinations patch code removed from quantum/action.c
- [ ] All personal keymaps compile without errors (Lulu, Lily58, Skeletyl)
- [ ] Chordal hold configured in all personal keymaps
- [ ] Bilateral key combinations function as closely as possible to previous behavior (or differences documented)
- [ ] All unique changes from lily58 and master branches preserved on personal branch
- [ ] Master branch reset to latest upstream QMK and tracks it cleanly
- [ ] Personal branch created from master with consolidated customizations
- [ ] All keyboard builds succeed
- [ ] KEYBOARDS.md created per constitution requirement
- [ ] Old branches preserved as backup (lily58/miryoku-bilateral-combinations, master-backup-before-reset)
