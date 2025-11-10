# Tasks: QMK Keymap Refactoring & Modularization

**Input**: Design documents from `/specs/002-keymap-refactor/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/file-structure.md

**Tests**: Tests are NOT included per feature specification. Manual compilation and firmware flashing tests only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Reference Implementation**: Lulu (`keyboards/boardsource/lulu/keymaps/dario/keymap.c`) and Skeletyl (`keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap.c`) have been confirmed to use **identical 3x5+3 layouts** across all 8 layers (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON). This confirmed keymap will be extracted as the shared base layout in `users/dario/layers.h`.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and userspace structure creation

**Note**: This phase creates the foundational userspace directory that will hold all shared keymap code.

- [X] T001 Create userspace directory structure at users/dario/
- [X] T002 Create placeholder users/dario/dario.h with layer enums (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON)
- [X] T003 [P] Create placeholder users/dario/dario.c with empty process_record_user function
- [X] T004 [P] Create users/dario/rules.mk with shared feature flags (MOUSEKEY_ENABLE, EXTRAKEY_ENABLE)
- [X] T005 [P] Create scripts/generate_keymap_diagram.sh for visualization automation
- [X] T006 [P] Create docs/keymaps/ directory for generated visualizations
- [X] T007 Install keymap-drawer tool: python3 -m pip install --user keymap-drawer

**Checkpoint**: Userspace structure ready for shared code implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared keymap infrastructure that ALL keyboards will depend on

**⚠️ CRITICAL**: No keyboard migration can begin until this phase is complete

**Reference Source**: Extract layer definitions from `keyboards/boardsource/lulu/keymaps/dario/keymap.c` lines 6-54 (confirmed identical to Skeletyl)

- [X] T008 Define all custom keycodes in users/dario/dario.h (U_NA, U_NU, U_UND, U_CUT, U_CPY, U_PST, U_RDO, MS_*, RM_*)
- [X] T009 Implement custom keycode handlers in users/dario/dario.c (process_record_user with switch cases for U_UND, U_CUT, U_CPY, U_PST, U_RDO if needed)
- [X] T010 Update users/dario/rules.mk to add dario.c to SRC
- [X] T011 Extract LAYER_BASE from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 7-10) into users/dario/layers.h as LAYER_BASE macro with 36 keycodes
- [X] T012 Extract LAYER_NAV from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 13-16) into users/dario/layers.h
- [X] T013 [P] Extract LAYER_MOUSE from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 19-22) into users/dario/layers.h
- [X] T014 [P] Extract LAYER_MEDIA from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 25-28) into users/dario/layers.h
- [X] T015 [P] Extract LAYER_NUM from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 31-34) into users/dario/layers.h
- [X] T016 [P] Extract LAYER_SYM from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 37-40) into users/dario/layers.h
- [X] T017 [P] Extract LAYER_FUN from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 43-46) into users/dario/layers.h
- [X] T018 [P] Extract LAYER_BUTTON from keyboards/boardsource/lulu/keymaps/dario/keymap.c (lines 49-52) into users/dario/layers.h
- [X] T019 Add header guards and includes to users/dario/layers.h (#ifndef USERSPACE_LAYERS_H, #include "dario.h")
- [X] T020 Compile test build with any existing keyboard to verify userspace compiles successfully

**Checkpoint**: Foundation ready - all 8 layers extracted from confirmed identical keymap - keyboard migration can now begin

---

## Phase 3: User Story 5 - Consistent Naming Convention (Priority: P1)

**Goal**: Standardize all custom keymap directories to use exactly "dario" as the keymap name

**Independent Test**: Search codebase for keymap directories, verify all use "dario", confirm build commands work with :dario

**Why US5 First**: This cleanup must happen before US1 and US4 to ensure we're working with consistently named directories. US5 has no dependencies on the modular system.

### Lily58 Naming Migration

- [X] T021 [US5] Rename keyboards/lily58/keymaps/daranguiz_miryoku/ to keyboards/lily58/keymaps/dario/
- [X] T022 [US5] Update USER_NAME in keyboards/lily58/keymaps/dario/rules.mk to "dario" if not already set
- [X] T023 [US5] Verify build command works: make lily58/rev1:dario

### Skeletyl Naming Migration

- [X] T024 [US5] Rename keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/ to keyboards/bastardkb/skeletyl/keymaps/dario/
- [X] T025 [US5] Update USER_NAME in keyboards/bastardkb/skeletyl/keymaps/dario/rules.mk to "dario" if not already set
- [X] T026 [US5] Verify build command works: make bastardkb/skeletyl/promicro:dario

### Lulu Already Correct

- [X] T027 [US5] Verify keyboards/boardsource/lulu/keymaps/dario/ already uses correct naming
- [X] T028 [US5] Verify build command works: make boardsource/lulu/rp2040:dario

### Build Script Updates

- [X] T029 [P] [US5] Create build_lily58.sh in repository root with correct keyboard path
- [X] T030 [P] [US5] Create build_skeletyl.sh in repository root with correct keyboard path
- [X] T031 [P] [US5] Verify build_lulu.sh exists and uses correct path

### Documentation Updates

- [X] T032 [US5] Update KEYBOARDS.md to reflect all keymaps using "dario" naming
- [X] T033 [US5] Update LULU_FLASHING_GUIDE.md if it references keymap names
- [X] T034 [US5] Search for any other documentation files referencing old keymap names and update

**Checkpoint**: All keymaps consistently named "dario", all build commands use :dario

---

## Phase 4: User Story 4 - Code Cleanup (Priority: P1)

**Goal**: Remove all legacy experimental code, dead code, and redundant configurations

**Independent Test**: Review codebase for commented-out code, unused flags, old experiment references - verify none exist

**Why US4 Before US1**: Clean code is essential before implementing the modular system to avoid bugs from dead code and to have clear starting point.

### Lulu Cleanup

- [ ] T035 [US4] Review keyboards/boardsource/lulu/keymaps/dario/keymap.c and remove all commented-out experimental code
- [ ] T036 [US4] Review keyboards/boardsource/lulu/keymaps/dario/config.h and remove unused configuration flags
- [ ] T037 [US4] Review keyboards/boardsource/lulu/keymaps/dario/rules.mk and remove unused feature flags
- [ ] T038 [US4] Remove any references to bilateral combinations patch in Lulu keymap

### Lily58 Cleanup

- [ ] T039 [US4] Review keyboards/lily58/keymaps/dario/keymap.c and remove all commented-out experimental code
- [ ] T040 [US4] Review keyboards/lily58/keymaps/dario/config.h and remove unused configuration flags
- [ ] T041 [US4] Review keyboards/lily58/keymaps/dario/rules.mk and remove unused feature flags
- [ ] T042 [US4] Remove any references to bilateral combinations patch in Lily58 keymap

### Skeletyl Cleanup

- [ ] T043 [US4] Review keyboards/bastardkb/skeletyl/keymaps/dario/keymap.c and remove all commented-out experimental code
- [ ] T044 [US4] Review keyboards/bastardkb/skeletyl/keymaps/dario/config.h and remove unused configuration flags
- [ ] T045 [US4] Review keyboards/bastardkb/skeletyl/keymaps/dario/rules.mk and remove unused feature flags
- [ ] T046 [US4] Remove any references to bilateral combinations patch in Skeletyl keymap

### Userspace Cleanup (if exists)

- [ ] T047 [US4] Review users/daranguiz/ directory if it exists and identify code to migrate or remove
- [ ] T048 [US4] Remove any legacy userspace directories that won't be used

### Verification

- [ ] T049 [US4] Compile all three keyboards to verify they still build after cleanup
- [ ] T050 [US4] Document all currently-used features in a checklist for reference

**Checkpoint**: Clean codebase with no dead code, only actively used configuration

---

## Phase 4.5: External Userspace Migration (Blocking Prerequisite)

**Goal**: Migrate existing keymaps and userspace to QMK External Userspace to enable proper userspace functionality

**Why This Phase**: QMK 0.30.6 has deprecated in-tree userspace (users/ directory). The build system generates absolute paths (/users/dario) instead of relative paths (users/dario), breaking userspace includes. External Userspace is the official supported solution.

**Prerequisites**: User must fork https://github.com/qmk/qmk_userspace and clone it locally before starting this phase.

**Reference**: https://docs.qmk.fm/newbs_external_userspace

**Scope**: This phase ONLY migrates existing code as-is. Refactoring (layer macros, wrappers) happens in Phase 5.

### External Userspace Setup (User Manual Steps)

- [X] T051A [Phase4.5] User: Fork https://github.com/qmk/qmk_userspace to personal GitHub account
- [X] T051B [Phase4.5] User: Clone forked qmk_userspace repository to $HOME/qmk_userspace
- [X] T051C [Phase4.5] User: Run `qmk config user.overlay_dir="$(realpath ~/qmk_userspace)"` to configure QMK CLI
- [X] T051D [Phase4.5] User: Verify configuration with `qmk config user.overlay_dir`

### Migration: Copy Userspace AS-IS

- [X] T052 [Phase4.5] Copy entire users/dario/ directory to ~/qmk_userspace/users/dario/ (all files unchanged)
- [X] T053 [Phase4.5] Verify ~/qmk_userspace/users/dario/dario.h exists
- [X] T054 [Phase4.5] Verify ~/qmk_userspace/users/dario/dario.c exists
- [X] T055 [Phase4.5] Verify ~/qmk_userspace/users/dario/config.h exists
- [X] T056 [Phase4.5] Verify ~/qmk_userspace/users/dario/rules.mk exists

### Migration: Copy Keymaps AS-IS

- [X] T057 [P] [Phase4.5] Copy entire keyboards/bastardkb/skeletyl/keymaps/dario/ to ~/qmk_userspace/keyboards/bastardkb/skeletyl/keymaps/dario/ (unchanged)
- [X] T058 [P] [Phase4.5] Copy entire keyboards/boardsource/lulu/keymaps/dario/ to ~/qmk_userspace/keyboards/boardsource/lulu/keymaps/dario/ (unchanged)
- [X] T059 [P] [Phase4.5] Copy entire keyboards/lily58/keymaps/dario/ to ~/qmk_userspace/keyboards/lily58/keymaps/dario/ (unchanged)

### Register Build Targets in qmk.json

- [X] T060 [Phase4.5] Run `qmk userspace-add -kb bastardkb/skeletyl/promicro -km dario` to register Skeletyl
- [X] T061 [Phase4.5] Run `qmk userspace-add -kb boardsource/lulu/rp2040 -km dario` to register Lulu
- [X] T062 [Phase4.5] Run `qmk userspace-add -kb lily58/rev1 -km dario` to register Lily58
- [X] T063 [Phase4.5] Verify ~/qmk_userspace/qmk.json contains all three keyboard/keymap entries

### Test Builds from External Userspace

- [X] T064 [Phase4.5] Test build Skeletyl: `qmk compile -kb bastardkb/skeletyl/promicro -km dario`
- [X] T065 [Phase4.5] Test build Lulu: `qmk compile -kb boardsource/lulu/rp2040 -km dario`
- [X] T066 [Phase4.5] Test build Lily58: `qmk compile -kb lily58/rev1 -km dario`
- [X] T067 [Phase4.5] Verify all three builds succeed with existing keymap code

### Test Batch Compilation

- [X] T068 [Phase4.5] Run `qmk userspace-compile` to build all registered keyboards at once
- [X] T069 [Phase4.5] Verify firmware files created in ~/qmk_userspace/ root directory for all three keyboards

### Commit External Userspace

- [X] T070 [Phase4.5] Commit all changes to ~/qmk_userspace/ repository
- [X] T071 [Phase4.5] Push to personal qmk_userspace fork on GitHub

**Checkpoint**: External Userspace working - all three keyboards build successfully from external userspace with existing keymaps

**Next Phase**: Phase 5 will implement the modular layer system (LAYER_* macros, wrappers) on top of this working external userspace.

---

## Phase 5: User Story 1 - Modular Base Layout Management (Priority: P1) 🎯 MVP

**Goal**: Establish single source of truth for core 3x5+3 layout shared across all keyboards

**Independent Test**: Modify LAYER_BASE in users/dario/layers.h once, compile all keyboards, verify identical base layer behavior

**Why US1 After US4/US5**: This is the foundational modular system that requires clean, consistently-named keymaps.

**Reference**: All 8 layers already extracted in Phase 2 from confirmed identical Lulu/Skeletyl keymaps

### Skeletyl Migration (36-key native)

- [ ] T051 [US1] Create keyboards/bastardkb/skeletyl/keymaps/dario/keymap_config.h with includes only (no wrapper needed - native 36-key)
- [ ] T052 [US1] Rewrite keyboards/bastardkb/skeletyl/keymaps/dario/keymap.c to include dario.h and layers.h from userspace
- [ ] T053 [US1] Update keyboards/bastardkb/skeletyl/keymaps/dario/keymap.c keymaps array to use LAYOUT_split_3x5_3(LAYER_BASE), etc. for all 8 layers
- [ ] T054 [US1] Verify keyboards/bastardkb/skeletyl/keymaps/dario/rules.mk has USER_NAME := dario
- [ ] T055 [US1] Test build: make bastardkb/skeletyl/promicro:dario and verify successful compilation
- [ ] T056 [US1] Flash Skeletyl and verify base layer functionality matches original

### Lulu Migration (58-key with wrapper)

- [ ] T057 [US1] Create keyboards/boardsource/lulu/keymaps/dario/keymap_config.h with LAYOUT_split_3x5_3 wrapper macro mapping 36 keys to Lulu's 58-key layout
- [ ] T058 [US1] Define XXX (KC_NO) for unused positions in keyboards/boardsource/lulu/keymaps/dario/keymap_config.h
- [ ] T059 [US1] Rewrite keyboards/boardsource/lulu/keymaps/dario/keymap.c to include keymap_config.h, dario.h, and layers.h
- [ ] T060 [US1] Update keyboards/boardsource/lulu/keymaps/dario/keymap.c keymaps array to use LAYOUT_split_3x5_3(LAYER_BASE), etc. for all 8 layers
- [ ] T061 [US1] Verify keyboards/boardsource/lulu/keymaps/dario/rules.mk has USER_NAME := dario
- [ ] T062 [US1] Test build: make boardsource/lulu/rp2040:dario and verify successful compilation
- [ ] T063 [US1] Flash Lulu and verify base layer functionality matches original

### Lily58 Migration (58-key with wrapper)

- [ ] T064 [US1] Create keyboards/lily58/keymaps/dario/keymap_config.h with LAYOUT_split_3x5_3 wrapper macro mapping 36 keys to Lily58's 58-key layout
- [ ] T065 [US1] Define XXX (KC_NO) for unused positions in keyboards/lily58/keymaps/dario/keymap_config.h
- [ ] T066 [US1] Rewrite keyboards/lily58/keymaps/dario/keymap.c to include keymap_config.h, dario.h, and layers.h
- [ ] T067 [US1] Update keyboards/lily58/keymaps/dario/keymap.c keymaps array to use LAYOUT_split_3x5_3(LAYER_BASE), etc. for all 8 layers
- [ ] T068 [US1] Verify keyboards/lily58/keymaps/dario/rules.mk has USER_NAME := dario
- [ ] T069 [US1] Test build: make lily58/rev1:dario and verify successful compilation
- [ ] T070 [US1] Flash Lily58 and verify base layer functionality matches original

### Verification of Single Source of Truth

- [ ] T071 [US1] Make a test change to LAYER_BASE in users/dario/layers.h (e.g., swap two keys)
- [ ] T072 [US1] Rebuild all three keyboards and verify the change appears in all builds
- [ ] T073 [US1] Revert the test change in users/dario/layers.h

**Checkpoint**: Single source of truth established - modifying users/dario/layers.h affects all keyboards

---

## Phase 6: User Story 2 - Keyboard-Specific Customization (Priority: P2)

**Goal**: Enable hardware-specific features (OLED, extra keys, encoders) per keyboard while keeping base layout shared

**Independent Test**: Configure OLED for Lulu without affecting other keyboards, verify base layer remains identical while OLED functions correctly

**Why US2 After US1**: This builds on the modular base by adding hardware differentiation.

### Lulu OLED Implementation

- [ ] T074 [P] [US2] Review existing OLED code in keyboards/boardsource/lulu/keymaps/dario/ if present
- [ ] T075 [P] [US2] Create or update keyboards/boardsource/lulu/keymaps/dario/oled.c with oled_init_user and oled_task_user functions
- [ ] T076 [US2] Add OLED_ENABLE = yes to keyboards/boardsource/lulu/keymaps/dario/rules.mk
- [ ] T077 [US2] Add SRC += oled.c to keyboards/boardsource/lulu/keymaps/dario/rules.mk
- [ ] T078 [US2] Update OLED display to show current layer name using get_highest_layer(layer_state)
- [ ] T079 [US2] Test build and flash: make boardsource/lulu/rp2040:dario:flash
- [ ] T080 [US2] Verify OLED displays correctly on Lulu

### Lily58 OLED Implementation

- [ ] T081 [P] [US2] Review existing OLED code in keyboards/lily58/keymaps/dario/ if present
- [ ] T082 [P] [US2] Create or update keyboards/lily58/keymaps/dario/oled.c with oled_init_user and oled_task_user functions
- [ ] T083 [US2] Add OLED_ENABLE = yes to keyboards/lily58/keymaps/dario/rules.mk
- [ ] T084 [US2] Add SRC += oled.c to keyboards/lily58/keymaps/dario/rules.mk
- [ ] T085 [US2] Update OLED display to show current layer name using get_highest_layer(layer_state)
- [ ] T086 [US2] Test build and flash: make lily58/rev1:dario:flash
- [ ] T087 [US2] Verify OLED displays correctly on Lily58

### Extra Keys Configuration (Lulu and Lily58)

- [ ] T088 [US2] Document which physical keys on Lulu are extra (beyond 36-key core) in keyboards/boardsource/lulu/keymaps/dario/README.md
- [ ] T089 [US2] Document which physical keys on Lily58 are extra (beyond 36-key core) in keyboards/lily58/keymaps/dario/README.md
- [ ] T090 [US2] Verify extra keys in wrapper macros are mapped to XXX (KC_NO) or have intentional assignments

### Verification

- [ ] T091 [US2] Verify Skeletyl build still succeeds and has no OLED code: make bastardkb/skeletyl:dario
- [ ] T092 [US2] Test that modifying users/dario/layers.h still affects all three keyboards equally
- [ ] T093 [US2] Verify OLED features are keyboard-specific and don't leak to other boards

**Checkpoint**: Keyboard-specific features working, base layout still shared

---

## Phase 7: User Story 3 - Keymap Visualization (Priority: P3)

**Goal**: Generate visual diagrams of keymap for printing or sharing

**Independent Test**: Run visualization generation command, verify output image accurately represents keymap with proper layer labels and key symbols

**Why US3 After US1/US2**: Visualization is quality-of-life feature that's valuable after core refactoring is complete.

### Visualization Configuration

- [ ] T094 [P] [US3] Create ~/.config/keymap-drawer/config.yaml if not exists
- [ ] T095 [P] [US3] Add parse_config section to config.yaml with qmk_remove_keycode_prefix for "KC_"
- [ ] T096 [US3] Add raw_binding_map to config.yaml with custom keycode mappings (U_NA, U_UND, U_RDO, U_CUT, U_CPY, U_PST)
- [ ] T097 [US3] Add raw_binding_map entries for mouse keycodes (MS_LEFT, MS_DOWN, MS_UP, MS_RGHT, MS_BTN1, MS_BTN2, MS_BTN3)
- [ ] T098 [US3] Add draw_config section to config.yaml with ortho_layout settings (split: true, rows: 3, columns: 5, thumbs: 3)

### Visualization Script

- [ ] T099 [US3] Update scripts/generate_keymap_diagram.sh to accept keyboard and keymap arguments
- [ ] T100 [US3] Add qmk c2json command to scripts/generate_keymap_diagram.sh with --no-cpp flag
- [ ] T101 [US3] Add keymap parse command to scripts/generate_keymap_diagram.sh with config file reference
- [ ] T102 [US3] Add keymap draw command to scripts/generate_keymap_diagram.sh with SVG output to docs/keymaps/
- [ ] T103 [US3] Make scripts/generate_keymap_diagram.sh executable: chmod +x scripts/generate_keymap_diagram.sh

### Diagram Generation

- [ ] T104 [P] [US3] Generate Lulu diagram: bash scripts/generate_keymap_diagram.sh boardsource/lulu/rp2040 dario
- [ ] T105 [P] [US3] Generate Lily58 diagram: bash scripts/generate_keymap_diagram.sh lily58/rev1 dario
- [ ] T106 [P] [US3] Generate Skeletyl diagram: bash scripts/generate_keymap_diagram.sh bastardkb/skeletyl dario
- [ ] T107 [US3] Verify all SVG files are created in docs/keymaps/ with correct naming (underscore-separated keyboard paths)
- [ ] T108 [US3] Open and visually inspect all three SVG diagrams to verify accuracy

### ASCII Art Documentation

- [ ] T109 [P] [US3] Add ASCII art for all 8 layers to keyboards/boardsource/lulu/keymaps/dario/README.md following Constitution Principle V format
- [ ] T110 [P] [US3] Add ASCII art for all 8 layers to keyboards/lily58/keymaps/dario/README.md following Constitution Principle V format
- [ ] T111 [P] [US3] Add ASCII art for all 8 layers to keyboards/bastardkb/skeletyl/keymaps/dario/README.md following Constitution Principle V format

### Verification

- [ ] T112 [US3] Test regeneration after making a keymap change to verify automation works
- [ ] T113 [US3] Verify custom keycodes display with correct symbols or names in visualizations
- [ ] T114 [US3] Verify SVG files are suitable for printing (zoom and check clarity)

**Checkpoint**: Visual documentation complete and regenerable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories

- [ ] T115 [P] Update KEYBOARDS.md with complete inventory including build commands, flash commands, and feature lists
- [ ] T116 [P] Update CLAUDE.md to document the new modular keymap architecture for future agent sessions
- [ ] T117 [P] Create or update keyboards/boardsource/lulu/keymaps/dario/README.md with features, build commands, and layer descriptions
- [ ] T118 [P] Create or update keyboards/lily58/keymaps/dario/README.md with features, build commands, and layer descriptions
- [ ] T119 [P] Create or update keyboards/bastardkb/skeletyl/keymaps/dario/README.md with features, build commands, and layer descriptions
- [ ] T120 [P] Add comments to users/dario/layers.h explaining the layout philosophy and home row mods pattern
- [ ] T121 Verify all build scripts work correctly (./build_lulu.sh, ./build_lily58.sh, ./build_skeletyl.sh)
- [ ] T122 Create a master build script that builds all three keyboards in sequence
- [ ] T123 Test compilation time and verify it's within 10% of baseline (per performance goal)
- [ ] T124 Calculate codebase size reduction and verify ≥40% reduction achieved (per success criteria)
- [ ] T125 Run through quickstart.md validation steps to ensure developer onboarding works
- [ ] T126 Verify all tasks from file-structure.md validation checklist are satisfied
- [ ] T127 Create git commit with all changes and descriptive commit message

**Checkpoint**: Feature complete, documented, and validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Story 5 (Phase 3)**: Depends on Setup (Phase 1) - Naming cleanup before modular migration
- **User Story 4 (Phase 4)**: Depends on User Story 5 (Phase 3) - Clean consistently-named keymaps
- **User Story 1 (Phase 5)**: Depends on Foundational (Phase 2) + User Story 4 (Phase 4) - Core modular system
- **User Story 2 (Phase 6)**: Depends on User Story 1 (Phase 5) - Hardware customization on top of modular base
- **User Story 3 (Phase 7)**: Depends on User Story 1 (Phase 5) - Visualization after keymap is modular
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 5 (P1)**: Naming convention - independent, can start after Setup
- **User Story 4 (P1)**: Code cleanup - depends on US5 (clean the correctly-named directories)
- **User Story 1 (P1)**: Modular base layout - depends on Foundational Phase + US4 (need clean code and shared infrastructure)
- **User Story 2 (P2)**: Keyboard-specific customization - depends on US1 (extends the modular system)
- **User Story 3 (P3)**: Visualization - depends on US1 (visualize the modular keymap)

### Within Each User Story

**User Story 5 (Naming)**:
- Lily58 rename, Skeletyl rename, Lulu verification can run in parallel
- Build script updates can run in parallel after renames
- Documentation updates after renames complete

**User Story 4 (Cleanup)**:
- Lulu, Lily58, Skeletyl cleanup can run in parallel
- Verification after all cleanup complete

**User Story 1 (Modular Base)**:
- Skeletyl, Lulu, Lily58 migrations can run sequentially or in parallel
- Each keyboard: wrapper macro → keymap.c rewrite → rules.mk → build test → flash test (sequential)
- Final verification after all keyboards migrated

**User Story 2 (Hardware Features)**:
- Lulu OLED and Lily58 OLED implementations can run in parallel
- Extra keys documentation can run in parallel
- Verification after implementations complete

**User Story 3 (Visualization)**:
- Config setup tasks can run in parallel with script updates
- Diagram generation for three keyboards can run in parallel
- ASCII art for three README files can run in parallel

### Parallel Opportunities

- **Phase 1**: T003, T004, T005, T006 can run in parallel
- **Phase 2**: T013-T018 (all layer definitions except BASE and NAV) can run in parallel after T011-T012
- **Phase 3 (US5)**: T021-T023 (Lily58), T024-T026 (Skeletyl), T027-T028 (Lulu) can run in parallel; T029-T031 (build scripts) can run in parallel
- **Phase 4 (US4)**: T035-T038 (Lulu), T039-T042 (Lily58), T043-T046 (Skeletyl), T047-T048 (userspace) can run in parallel
- **Phase 5 (US1)**: Skeletyl migration (T051-T056), Lulu migration (T057-T063), Lily58 migration (T064-T070) can run in parallel AFTER each completes wrapper macro step
- **Phase 6 (US2)**: T074-T080 (Lulu OLED), T081-T087 (Lily58 OLED), T088-T090 (extra keys docs) can run in parallel
- **Phase 7 (US3)**: T094-T098 (config), T104-T106 (diagram generation), T109-T111 (ASCII art) can run in parallel within their groups
- **Phase 8**: T115-T120 (documentation tasks) can run in parallel

---

## Parallel Example: User Story 1 (Modular Base Layout)

```bash
# After Foundational Phase 2 completes, launch all three keyboard migrations in parallel:

# Terminal 1: Skeletyl migration
Task: "Create keyboards/bastardkb/skeletyl/keymaps/dario/keymap_config.h"
Task: "Rewrite keyboards/bastardkb/skeletyl/keymaps/dario/keymap.c to include dario.h and layers.h"
Task: "Test build: make bastardkb/skeletyl:dario"

# Terminal 2: Lulu migration
Task: "Create keyboards/boardsource/lulu/keymaps/dario/keymap_config.h with wrapper macro"
Task: "Rewrite keyboards/boardsource/lulu/keymaps/dario/keymap.c to include keymap_config.h, dario.h, and layers.h"
Task: "Test build: make boardsource/lulu/rp2040:dario"

# Terminal 3: Lily58 migration
Task: "Create keyboards/lily58/keymaps/dario/keymap_config.h with wrapper macro"
Task: "Rewrite keyboards/lily58/keymaps/dario/keymap.c to include keymap_config.h, dario.h, and layers.h"
Task: "Test build: make lily58/rev1:dario"
```

---

## Implementation Strategy

### MVP First (User Stories 5 + 4 + 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories, extracts confirmed identical layers)
3. Complete Phase 3: User Story 5 (Naming)
4. Complete Phase 4: User Story 4 (Cleanup)
5. Complete Phase 5: User Story 1 (Modular Base Layout)
6. **STOP and VALIDATE**: Test that modifying users/dario/layers.h updates all keyboards
7. Deploy/use firmware if ready

This gives you the core value: single source of truth for layout across all keyboards.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (8 layers extracted from confirmed identical keymaps)
2. Add User Story 5 → Naming consistent
3. Add User Story 4 → Code clean
4. Add User Story 1 → Modular system working (MVP!)
5. Add User Story 2 → Hardware features customizable
6. Add User Story 3 → Visual documentation available
7. Polish → Production ready

Each story adds value without breaking previous stories.

### Sequential Implementation Strategy (Recommended)

Given this is a solo project with embedded firmware (less parallelizable than web services):

1. **Phase 1-2**: Setup and Foundational (required, extracts 8 layers)
2. **Phase 3**: US5 Naming (all keyboards sequentially)
3. **Phase 4**: US4 Cleanup (all keyboards sequentially)
4. **Phase 5**: US1 Modular Base (Skeletyl → Lulu → Lily58 sequentially, test each)
5. **Phase 6**: US2 Hardware Features (Lulu OLED → Lily58 OLED)
6. **Phase 7**: US3 Visualization (config → scripts → generation → ASCII art)
7. **Phase 8**: Polish and validation

---

## Notes

- **Reference keymap**: keyboards/boardsource/lulu/keymaps/dario/keymap.c and keyboards/bastardkb/skeletyl/keymaps/daranguiz_miryoku/keymap.c confirmed identical across all 8 layers
- All 8 layers extracted in Phase 2: BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Build and flash firmware after each keyboard migration to catch issues early
- Commit after each keyboard is fully migrated and tested
- Stop at any checkpoint to validate story independently
- Constitution Principle V requires ASCII art in README.md files
- Constitution Principle I ensures all changes stay in keyboards/*/keymaps/dario/ or users/dario/
- Performance goal: compilation time within 10% of baseline
- Success criteria: 40% code reduction through deduplication

---

## Summary

**Total Tasks**: 127 tasks across 8 phases

**Task Count by User Story**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 13 tasks (extracts all 8 confirmed identical layers)
- Phase 3 (US5 - Naming): 14 tasks
- Phase 4 (US4 - Cleanup): 16 tasks
- Phase 5 (US1 - Modular Base): 23 tasks
- Phase 6 (US2 - Hardware Customization): 20 tasks
- Phase 7 (US3 - Visualization): 21 tasks
- Phase 8 (Polish): 13 tasks

**Parallel Opportunities Identified**:
- 34 tasks marked [P] can run in parallel with others in their phase
- 3 keyboards can be migrated in parallel (if multiple developers)
- Layer definitions (Phase 2) can be parallelized (6 of 8 layers)

**Independent Test Criteria**:
- US5: Search for "dario" keymap directories, verify build commands work
- US4: Search for commented code, verify none exists
- US1: Modify users/dario/layers.h once, verify all keyboards affected
- US2: Configure OLED on one keyboard, verify others unaffected
- US3: Generate SVG, verify accuracy and printability

**Suggested MVP Scope**:
- Phase 1: Setup (7 tasks)
- Phase 2: Foundational (13 tasks) - **Extracts confirmed identical layers**
- Phase 3: US5 Naming (14 tasks)
- Phase 4: US4 Cleanup (16 tasks)
- Phase 5: US1 Modular Base (23 tasks)
- **Total MVP**: 73 tasks

After MVP, you have a working modular keymap system with single source of truth based on the confirmed identical Lulu/Skeletyl layouts. US2 (hardware features) and US3 (visualization) are valuable but not critical for core functionality.

**Format Validation**: ✅ All 127 tasks follow strict checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T127 sequential
- [P] marker: 34 tasks marked as parallelizable
- [Story] label: 94 tasks have user story labels (US1, US2, US3, US4, US5)
- Description: All include clear actions with file paths

**Key Update**: Phase 2 (Foundational) now explicitly references extracting layers from the confirmed identical Lulu/Skeletyl keymaps as validated by the user.
