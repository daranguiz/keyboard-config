# Tasks: Unified QMK/ZMK Keymap Configuration with Code Generation

**Input**: Design documents from `/specs/003-unified-keymap-codegen/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested in spec - tasks focus on implementation and integration testing (compilation verification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- Repository root: `/Users/dario/git/qmk_userspace/`
- Unified config: `config/`
- QMK output: `qmk/keymaps/`, QMK config: `qmk/config/`
- ZMK output: `zmk/keymaps/`, ZMK config: `zmk/config/`
- Scripts: `scripts/`
- Tests: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (config/, scripts/, tests/, tests/fixtures/)
- [X] T002 [P] Install Python testing dependencies (pytest) via pip
- [X] T003 [P] Create config/aliases.yaml with firmware-agnostic behavior aliases (hrm, lt, bt)
- [X] T004 [P] Create .gitignore entries for generated files (qmk/keymaps/, zmk/keymaps/, __pycache__)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data model, parsers, and translators that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement KeyGrid dataclass in scripts/data_model.py with flatten() and property methods
- [X] T006 [P] Implement LayerExtension dataclass in scripts/data_model.py with validation
- [X] T007 [P] Implement Layer dataclass in scripts/data_model.py with core and extensions
- [X] T008 [P] Implement Board dataclass in scripts/data_model.py with get_extensions() and validate()
- [X] T009 [P] Implement CompiledLayer dataclass in scripts/data_model.py
- [X] T010 Implement YAMLConfigParser.parse_keymap() in scripts/config_parser.py (parse config/keymap.yaml)
- [X] T011 [P] Implement YAMLConfigParser.parse_boards() in scripts/config_parser.py (parse config/boards.yaml)
- [X] T012 [P] Implement YAMLConfigParser.parse_aliases() in scripts/config_parser.py (parse config/aliases.yaml)
- [X] T013 Implement QMKTranslator.translate() in scripts/qmk_translator.py (unified → QMK C syntax)
- [X] T014 [P] Implement QMKTranslator.validate_keybinding() in scripts/qmk_translator.py (FR-007 strict validation)
- [X] T015 Implement LayerCompiler.compile_layer() in scripts/layer_compiler.py (apply extensions + translate)
- [X] T016 [P] Implement LayerCompiler.get_extension_keys() in scripts/layer_compiler.py
- [X] T017 Implement ConfigValidator.validate_keymap_config() in scripts/validator.py (schema + business logic)
- [X] T018 [P] Implement ConfigValidator.validate_board_config() in scripts/validator.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Single-Source Keymap Updates (Priority: P1) 🎯 MVP

**Goal**: Update keymap in one place (config/keymap.yaml) and generate both QMK and ZMK keymaps automatically

**Independent Test**: Modify a key binding in config/keymap.yaml, run generation, verify both QMK and ZMK keymaps reflect the change and compile successfully

### Implementation for User Story 1

- [X] T019 [P] [US1] Create initial config/keymap.yaml with BASE and NAV layers (36-key core only, no extensions)
- [X] T020 [P] [US1] Create initial config/boards.yaml with skeletyl board (36-key QMK board)
- [X] T021 [US1] Implement QMKGenerator.generate_keymap() in scripts/qmk_generator.py (generate keymap.c, config.h, rules.mk)
- [X] T022 [US1] Implement QMKGenerator.format_layer_definition() in scripts/qmk_generator.py (format LAYOUT_split_3x5_3 macro)
- [X] T023 [US1] Implement QMKGenerator.generate_visualization() in scripts/qmk_generator.py (ASCII art for README.md)
- [X] T024 [US1] Implement FileSystemWriter.write_file() in scripts/file_writer.py
- [X] T025 [P] [US1] Implement FileSystemWriter.ensure_directory() in scripts/file_writer.py
- [X] T026 [P] [US1] Implement FileSystemWriter.write_all() in scripts/file_writer.py
- [X] T027 [US1] Implement KeymapGenerator.generate_for_board() in scripts/generate.py (orchestrate: parse → validate → compile → generate → write)
- [X] T028 [US1] Implement KeymapGenerator.generate_all() in scripts/generate.py (loop over all boards)
- [X] T029 [US1] Create main CLI entrypoint scripts/generate.py with argument parsing and error handling
- [X] T030 [US1] Add execution permission to scripts/generate.py (chmod +x)
- [X] T031 [US1] Test generation: run scripts/generate.py and verify qmk/keymaps/bastardkb_skeletyl_promicro_dario/keymap.c is created
- [X] T032 [US1] Integration test: compile generated QMK keymap with qmk compile -kb bastardkb/skeletyl/promicro -km dario
- [X] T032a [US1] Update users/dario/dario.h to export layer enums for generated keymaps
- [X] T032b [US1] Update QMKGenerator to include "dario.h" and use shared layer enums instead of generating inline
- [X] T032c [US1] Update QMKGenerator config.h to include users/dario/config.h
- [X] T032d [US1] Update QMKGenerator rules.mk to set USER_NAME := dario
- [X] T032e [US1] Verify users/dario/dario.c custom keycode processing still works
- [X] T032f [US1] Regenerate and recompile to verify userspace integration works

**Checkpoint**: At this point, User Story 1 should be fully functional - single YAML config generates working QMK keymap for 36-key board with proper userspace integration

---

## Phase 4: User Story 2 - Firmware-Specific Feature Handling (Priority: P2)

**Goal**: Define superset keymap with both QMK-specific and ZMK-specific keybindings, automatically filtered during generation

**Independent Test**: Add firmware-specific keybindings (ZMK Bluetooth, QMK-specific features) to config/keymap.yaml, generate both firmwares, verify each output only includes supported features

### Implementation for User Story 2

- [X] T033 [P] [US2] Extend config/aliases.yaml with ZMK-specific aliases (bt:next, bt:prev, bt:clear)
- [X] T034 [P] [US2] Add MEDIA layer to config/keymap.yaml with ZMK Bluetooth controls (bt:next, bt:prev)
- [X] T035 [US2] Implement ZMKTranslator.translate() in scripts/zmk_translator.py (unified → ZMK devicetree syntax)
- [X] T036 [P] [US2] Implement ZMKTranslator.validate_keybinding() in scripts/zmk_translator.py (FR-007 strict validation)
- [X] T037 [US2] Implement ZMKGenerator.generate_keymap() in scripts/zmk_generator.py (generate .keymap devicetree file)
- [X] T038 [P] [US2] Implement ZMKGenerator.format_layer_definition() in scripts/zmk_generator.py (format bindings with &kp, &hrm, &lt)
- [X] T039 [P] [US2] Implement ZMKGenerator.generate_visualization() in scripts/zmk_generator.py (ASCII art)
- [X] T040 [US2] Update KeymapGenerator.generate_for_board() to select translator based on board.firmware (QMK vs ZMK)
- [X] T041 [US2] Add corne ZMK board to config/boards.yaml (36-key ZMK board for testing)
- [X] T042 [US2] Test generation: verify Bluetooth keys appear in ZMK output (zmk/keymaps/corne_dario/corne.keymap) as &bt BT_NXT
- [X] T043 [US2] Test filtering: verify Bluetooth keys are replaced with KC_NO in QMK output (qmk/keymaps/bastardkb_skeletyl_promicro_dario/keymap.c)
- [X] T044 [US2] Test bootloader key consistency: verify QK_BOOT in QMK and &bootloader in ZMK

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - superset keymap generates firmware-specific outputs with proper filtering

---

## Phase 5: User Story 3 - Board-Specific Layout Extensions (Priority: P2)

**Goal**: Define board-specific extensions in unified config, generate keymaps with extra keys for larger boards while maintaining core consistency

**Independent Test**: Define 3x6_3 extension in config/keymap.yaml, verify only boards with layout_size "3x6_3" include extra keys, core 36-key layout remains identical

### Implementation for User Story 3

- [X] T045 [P] [US3] Add extensions section to all layers in config/keymap.yaml (3x5_3_pinky, 3x6_3 extensions)
- [X] T046 [P] [US3] Add lulu board to config/boards.yaml with layout_size "custom_58" and extra_layers ["GAME"]
- [X] T047 [P] [US3] Add lily58 board to config/boards.yaml with layout_size "custom_58" and extra_layers ["GAME"]
- [X] T048 [US3] Update LayerCompiler to pad 36-key core to match board physical size (brute-force codegen: 36→58 with KC_NO padding)
- [X] T049 [US3] Implement LayerExtension.validate() in scripts/data_model.py (check 3x5_3_pinky has single keys, 3x6_3 has 3-key lists)
- [X] T050 [US3] Update QMKGenerator to format complete layouts (36/42/58 keys - no wrapper macros, direct LAYOUT() output)
- [X] T051 [P] [US3] Create qmk/config/boards/lulu.mk with firmware-specific features (OLED_ENABLE, RGB_MATRIX_ENABLE)
- [X] T052 [P] [US3] Create qmk/config/boards/lily58.mk with firmware-specific features (OLED_ENABLE, WPM_ENABLE)
- [X] T053 [US3] Add GAME layer definition to config/keymap.yaml with custom 58-key layout for Lulu/Lily58
- [X] T054 [US3] Implement board-specific layer handling in LayerCompiler (check board.extra_layers, skip layers not in list)
- [X] T055 [US3] Test extension application: verify 3x6_3 boards have 42 keys, 3x5_3 boards have 36 keys
- [X] T056 [US3] Test core consistency: verify first 36 keys are identical across all boards for BASE layer
- [X] T057 [US3] Integration test: compile Lulu keymap with qmk compile -kb boardsource/lulu/rp2040 -km dario
- [X] T058 [US3] Integration test: compile Lily58 keymap with qmk compile -kb lily58/rev1 -km dario

**Checkpoint**: All board sizes (36-key, 42-key, 58-key) generate correctly with consistent core layouts and board-specific extensions

---

## Phase 6: User Story 4 - Repository Migration (Priority: P1)

**Goal**: Migrate current QMK userspace repo to unified monorepo structure with config/, qmk/, zmk/, and unified CI/CD

**Independent Test**: Run migration, verify repo has config/, qmk/, zmk/, scripts/ directories, keymap generation works, GitHub Actions builds all firmwares

### Implementation for User Story 4

- [X] T059 [P] [US4] Create migration script scripts/migrate_layers.py with parse_layer_macro() function
- [X] T060 [P] [US4] Implement translate_to_unified() in scripts/migrate_layers.py (LGUI_T(KC_A) → hrm:LGUI:A, LT(NAV, SPC) → lt:NAV:SPC)
- [X] T061 [US4] Parse existing users/dario/layers.h and convert to config/keymap.yaml (migrate all 8 layers)
- [X] T062 [US4] Backup existing keyboards/ directory to keyboards.backup/
- [X] T063 [P] [US4] Create qmk/config/global/config.h with shared QMK settings (chordal hold, tapping terms)
- [X] T064 [P] [US4] Create qmk/config/global/rules.mk with shared QMK features (BOOTMAGIC_ENABLE, MOUSEKEY_ENABLE, LTO_ENABLE)
- [X] T065 [P] [US4] Migrate keyboards/bastardkb/skeletyl/keymaps/dario/rules.mk → qmk/config/boards/skeletyl.mk
- [X] T066 [P] [US4] Migrate keyboards/boardsource/lulu/keymaps/dario/ OLED/RGB settings → qmk/config/boards/lulu.mk
- [X] T067 [P] [US4] Migrate keyboards/lily58/keymaps/dario/ OLED/WPM settings → qmk/config/boards/lily58.mk
- [X] T068 [US4] Update build_all.sh to run scripts/generate.py before qmk userspace-compile
- [X] T069 [US4] Create .github/workflows/build-all.yml with unified QMK + ZMK build (Python setup, generate, compile, upload artifacts)
- [X] T070 [US4] Update CLAUDE.md with new architecture (config/, qmk/, zmk/, scripts/ structure, generator workflow)
- [X] T071 [US4] Test migration: run scripts/generate.py and verify all QMK boards compile successfully
- [X] T072 [US4] Test CI/CD: push to branch and verify GitHub Actions builds all firmware binaries

**Checkpoint**: Repository is fully migrated to monorepo structure, all builds work locally and in CI/CD

---

## Phase 7: User Story 5 - Easy Board Addition (Priority: P3)

**Goal**: Add new keyboards quickly with minimal configuration via helper script

**Independent Test**: Run add_board.sh with board details, verify boards.yaml is updated and keymap generation works

### Implementation for User Story 5

- [X] T073 [P] [US5] Create scripts/add_board.sh with argument parsing (board_id, firmware, keyboard, layout_size)
- [X] T074 [US5] Implement add_board.sh YAML append logic (add new board entry to config/boards.yaml)
- [X] T075 [P] [US5] Create template for qmk/config/boards/<board>.mk in scripts/templates/qmk_board.mk.template
- [X] T076 [P] [US5] Create template for zmk/config/boards/<board>.conf in scripts/templates/zmk_board.conf.template
- [X] T077 [US5] Implement scripts/add_board.sh template instantiation (create board-specific config files from templates)
- [X] T078 [US5] Add execution permission to scripts/add_board.sh (chmod +x)
- [X] T079 [US5] Test add_board.sh: add a new 36-key QMK board and verify config/boards.yaml is updated
- [X] T080 [US5] Test generation for new board: run scripts/generate.py and verify new board keymap is created

**Checkpoint**: New boards can be added with a single command, keymap generation works immediately

---

## Phase 8: Visual Keymap Documentation (Cross-Cutting)

**Purpose**: Integrate visual keymap generation into pipeline (FR-023, FR-024, FR-025, FR-026)

- [ ] T081 [P] Research keymap visualization options (keymap-drawer integration vs custom Python generator)
- [ ] T082 Implement visualization generation in scripts/visualizer.py (SVG or PNG output)
- [ ] T083 [P] Integrate visualizer into KeymapGenerator.generate_all() (call after keymap generation)
- [ ] T084 [P] Ensure visualizations are placed in docs/keymaps/ directory (FR-025)
- [ ] T085 Update build_all.sh to include visualization generation step
- [ ] T086 Test visualization: run scripts/generate.py and verify docs/keymaps/ contains SVG/PNG diagrams for all boards

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T087 [P] Add unit tests for QMKTranslator in tests/test_qmk_translator.py (test_simple_keycode, test_homerow_mod, test_layer_tap, test_bluetooth_filtered)
- [ ] T088 [P] Add unit tests for ZMKTranslator in tests/test_zmk_translator.py (test_simple_keycode, test_homerow_mod, test_bluetooth_support)
- [ ] T089 [P] Add unit tests for LayerCompiler in tests/test_layer_compiler.py (test_compile_layer_with_extensions, test_extension_filtering)
- [ ] T090 [P] Add integration test in tests/test_integration.py (test_full_generation_compiles for all boards)
- [ ] T091 Add comprehensive error messages to ConfigValidator (include line numbers, context, suggestions)
- [ ] T092 [P] Add README.md to config/ directory explaining YAML schema and usage
- [ ] T093 [P] Create example fixtures in tests/fixtures/ (minimal_keymap.yaml, full_keymap.yaml, boards.yaml)
- [ ] T094 Add --validate flag to scripts/generate.py CLI (validate config without generating)
- [ ] T095 [P] Add --verbose flag to scripts/generate.py CLI (detailed logging)
- [ ] T096 Update quickstart.md with actual implementation paths and examples
- [ ] T097 [P] Auto-generate KEYBOARDS.md from config/boards.yaml (Principle IV compliance)
- [ ] T098 Code cleanup: add type hints to all Python functions
- [ ] T099 [P] Code cleanup: add docstrings to all Python classes and functions
- [ ] T100 Run full validation workflow from quickstart.md (test all generation scenarios)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - **US1 (Phase 3)**: Can start after Phase 2 ✅ MVP - highest priority
  - **US4 (Phase 6)**: Can start after Phase 2 (migration) - P1 priority, recommended to do early
  - **US2 (Phase 4)**: Can start after Phase 2 and US1 completion (builds on QMK generator)
  - **US3 (Phase 5)**: Can start after Phase 2 and US1 completion (extends generator)
  - **US5 (Phase 7)**: Can start after Phase 2 and US1 completion (add board tooling)
- **Visual Documentation (Phase 8)**: Can start after US1 completion
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Phase 3)**: Core generator - NO dependencies on other user stories
- **User Story 4 (P1 - Phase 6)**: Repository migration - NO dependencies on other user stories (can run in parallel with US1)
- **User Story 2 (P2 - Phase 4)**: Firmware filtering - Depends on US1 (extends QMK generator with ZMK)
- **User Story 3 (P2 - Phase 5)**: Extensions - Depends on US1 (extends compiler with extension logic)
- **User Story 5 (P3 - Phase 7)**: Add board tooling - Depends on US1 (requires working generator)

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Data models before parsers
- Parsers before compilers
- Compilers before generators
- Generators before orchestrator
- Core implementation before integration tests
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 - Setup**: All tasks (T001-T004) can run in parallel

**Phase 2 - Foundational**:
- T006, T007, T008, T009 can run in parallel (dataclasses, no cross-dependencies)
- T011, T012 can run in parallel (different parsers)
- T014 can run in parallel with T013 (same class, different methods)
- T016 can run in parallel with T015 (same class, different methods)
- T018 can run in parallel with T017 (same class, different methods)

**Phase 3 - User Story 1**:
- T019, T020 can run in parallel (different config files)
- T024, T025, T026 can run in parallel (FileSystemWriter methods)

**Phase 4 - User Story 2**:
- T033, T034 can run in parallel (different files)
- T036 can run in parallel with T035 (same class, different methods)
- T038, T039 can run in parallel with T037 (same class, different methods)

**Phase 5 - User Story 3**:
- T045, T046, T047 can run in parallel (different config sections)
- T051, T052 can run in parallel (different board config files)

**Phase 6 - User Story 4**:
- T059, T060 can run in parallel (different migration functions)
- T063, T064, T065, T066, T067 can run in parallel (different config files)

**Phase 7 - User Story 5**:
- T075, T076 can run in parallel (different template files)

**Phase 8 - Visual Documentation**:
- T083, T084 can run in parallel (different integration points)

**Phase 9 - Polish**:
- T087, T088, T089, T090, T091, T092, T093, T094, T095, T096, T097, T098, T099 can all run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch config files together:
Task: T019 [P] [US1] "Create initial config/keymap.yaml"
Task: T020 [P] [US1] "Create initial config/boards.yaml"

# Launch FileSystemWriter methods together:
Task: T024 [US1] "Implement FileSystemWriter.write_file()"
Task: T025 [P] [US1] "Implement FileSystemWriter.ensure_directory()"
Task: T026 [P] [US1] "Implement FileSystemWriter.write_all()"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 4)

**Recommended Approach**: US1 first (prove generator works), then US4 (migrate repo structure)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T018) - CRITICAL
3. Complete Phase 3: User Story 1 (T019-T032) - Core generator for 36-key QMK boards
4. **STOP and VALIDATE**: Test US1 independently (modify YAML, generate, compile)
5. Complete Phase 6: User Story 4 (T059-T072) - Migrate to monorepo structure
6. **STOP and VALIDATE**: Test migration (verify all builds work, CI/CD passes)
7. Deploy/demo if ready

**MVP Deliverable**: Single YAML config generates working QMK keymaps, repository migrated to unified structure

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → QMK generation works ✅
3. Add User Story 4 → Test independently → Monorepo migration complete ✅
4. Add User Story 2 → Test independently → Firmware filtering works (ZMK + Bluetooth)
5. Add User Story 3 → Test independently → Extensions work (42-key, 58-key boards)
6. Add User Story 5 → Test independently → Add board tooling works
7. Add Visual Documentation (Phase 8) → SVG/PNG diagrams generated
8. Polish (Phase 9) → Tests, docs, validation, cleanup
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: User Story 1 (T019-T032) - Core generator
   - Developer B: User Story 4 (T059-T072) - Migration (can start in parallel!)
3. After US1 completes:
   - Developer A: User Story 2 (T033-T044) - ZMK support
   - Developer B: User Story 3 (T045-T058) - Extensions
   - Developer C: User Story 5 (T073-T080) - Add board tooling
4. Stories complete and integrate independently

---

## Success Criteria

### Phase 3 (User Story 1) Complete When:
- ✅ QMK keymaps generated from YAML for 36-key board (Skeletyl)
- ✅ Generated keymap compiles without errors
- ✅ Can change key in YAML and see it reflected after regeneration
- ✅ Generated files have clear "auto-generated" warnings

### Phase 4 (User Story 2) Complete When:
- ✅ ZMK keymaps generated from same unified YAML
- ✅ Bluetooth keycodes work in ZMK, filtered to KC_NO in QMK
- ✅ Both firmwares generate successfully from superset config
- ✅ Bootloader keys work correctly in both firmwares

### Phase 5 (User Story 3) Complete When:
- ✅ Larger boards (Lulu, Lily58) support extensions
- ✅ Core 36-key layout identical across all boards
- ✅ Extensions only add keys without modifying core
- ✅ Board-specific layers (GAME) work correctly
- ✅ All boards compile successfully

### Phase 6 (User Story 4) Complete When:
- ✅ Repository restructured to monorepo (config/, qmk/, zmk/, scripts/)
- ✅ All existing keymaps migrated to YAML format
- ✅ Firmware-specific settings moved to qmk/config/, zmk/config/
- ✅ GitHub Actions builds all firmwares successfully
- ✅ Local build_all.sh works with new structure

### Phase 7 (User Story 5) Complete When:
- ✅ add_board.sh script works correctly
- ✅ New boards can be added in <5 minutes
- ✅ Template files generate correct firmware-specific configs
- ✅ Keymap generation works immediately for new boards

### Phase 8 (Visual Documentation) Complete When:
- ✅ Visual diagrams (SVG/PNG) generated automatically
- ✅ Diagrams placed in docs/keymaps/ directory
- ✅ Visualization integrated into main pipeline (not manual)
- ✅ All boards have up-to-date visual documentation

### Phase 9 (Polish) Complete When:
- ✅ Unit tests pass for all translators and compilers
- ✅ Integration tests verify all boards compile
- ✅ Error messages are clear and actionable
- ✅ Documentation is complete and accurate
- ✅ Code follows Python best practices (type hints, docstrings)
- ✅ KEYBOARDS.md auto-generated from boards.yaml

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Integration tests (compilation verification) ensure generated keymaps are valid
- No explicit unit tests requested in spec - focus on integration testing
- Visual documentation (Phase 8) is MANDATORY per FR-023, FR-024, FR-025, FR-026
- Firmware-specific settings (OLED, RGB, etc.) stay in qmk/config/ and zmk/config/ per FR-027, FR-028

---

## Total Task Count

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 14 tasks
- **Phase 3 (User Story 1)**: 14 tasks
- **Phase 4 (User Story 2)**: 12 tasks
- **Phase 5 (User Story 3)**: 14 tasks
- **Phase 6 (User Story 4)**: 14 tasks
- **Phase 7 (User Story 5)**: 8 tasks
- **Phase 8 (Visual Documentation)**: 6 tasks
- **Phase 9 (Polish)**: 14 tasks

**Total**: 100 tasks

**Tasks per User Story**:
- US1 (Core Generator): 14 tasks
- US2 (Firmware Filtering): 12 tasks
- US3 (Extensions): 14 tasks
- US4 (Migration): 14 tasks
- US5 (Add Board): 8 tasks

**Parallel Opportunities**: 35+ tasks marked [P] can run in parallel within their phases

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) + Phase 6 (User Story 4) = 46 tasks

**Format Validation**: ✅ All tasks follow checklist format (checkbox, ID, optional [P], optional [Story], description with file paths)

### Future Enhancement: Board-Specific GAME Layer Toggle

- [ ] FUTURE: Design board-specific GAME layer toggle mechanism
  - Document approach for each board type (combo, dedicated key, etc.)
  - For 58-key boards: implement combo (e.g., upper-right + lower-left for 2s)
  - For smaller boards: may need different approach or no GAME layer
  - Store board-specific combo/toggle config in boards.yaml or board-specific files
  - Generate QMK combo code when board has GAME layer

