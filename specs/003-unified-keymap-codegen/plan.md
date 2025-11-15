# Implementation Plan: Unified QMK/ZMK Keymap Configuration with Code Generation

**Branch**: `003-unified-keymap-codegen` | **Date**: 2025-11-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-unified-keymap-codegen/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a unified keymap configuration system that maintains a single source of truth (YAML format) for keyboard layouts and automatically generates both QMK and ZMK firmware keymaps. The system uses a monorepo structure with `config/` (unified YAML keymap), `qmk/` (generated QMK keymaps + firmware settings), and `zmk/` (generated ZMK keymaps + firmware settings). The core 36-key (3x5_3) layout is consistent across all keyboards, with support for per-layer optional extensions for larger boards (38-key, 42-key, 58-key). Firmware-specific features are bidirectionally filtered during generation, with simple keycodes silently dropped and complex keybindings strictly validated.

## Technical Context

**Language/Version**: Python 3.11+ (decision: Python over Bash per user direction)
**Primary Dependencies**: PyYAML 6.0.3 (already installed), pytest (recommended addition for testing)
**Storage**: File-based (YAML configuration files, generated C/header files for QMK, devicetree/keymap files for ZMK)
**Testing**: unittest (stdlib) for core tests, pytest for advanced testing, integration tests verify compilation of generated keymaps
**Target Platform**: macOS/Linux development environment (code generator runs locally, output targets QMK/ZMK firmware build systems)
**Project Type**: Code generation tool (CLI script)
**Performance Goals**: Generate all keymaps (5+ keyboards, 8 layers each) in <5 seconds; minimal enough to run on every save
**Constraints**:
  - Generated keymaps must compile without errors on QMK and ZMK build systems 100% of time
  - Generator must be idempotent (reproducible output)
  - Must integrate with existing build scripts (build_all.sh, GitHub Actions)
  - Zero manual edits to generated files (all customization via config/)
**Scale/Scope**:
  - 5-10 physical keyboards with varying sizes (36-key to 58-key)
  - 8+ layers per keyboard (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON, plus gaming layers)
  - 200-400 total keybindings managed centrally
  - Single-user personal project (no multi-user considerations)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Upstream Modularity
**Status**: ✅ PASS

**Analysis**: This feature enhances upstream modularity by introducing a code generation layer that keeps personal customizations (YAML config files) completely separate from generated QMK keymaps. The generated keymaps will still reside in `keyboards/<keyboard>/keymaps/dario/`, maintaining existing isolation patterns. The monorepo structure adds `config/`, `qmk/`, and `zmk/` directories at the repository root, which do not conflict with upstream QMK code.

**Implementation Impact**:
- YAML configs in `config/` are completely isolated from upstream
- Generated keymaps remain in standard `keyboards/.../keymaps/dario/` locations
- Code generator scripts in `scripts/` are personal tools (allowed per constitution)
- No modifications to upstream quantum/ code or build system

### Principle II: Core 36-Key Layout Consistency
**Status**: ✅ PASS (ENHANCED)

**Analysis**: This feature directly enforces and strengthens Principle II by making it architecturally impossible to have inconsistent core layouts. The unified YAML configuration ensures that the 36-key layout is defined once and propagated identically to all keyboards during generation. This is a significant improvement over manual synchronization.

**Implementation Impact**:
- Single source of truth for `LAYOUT_split_3x5_3` defined in `config/keymap.yaml`
- Generator ensures identical layer definitions across all keyboards
- Home row mod positioning consistency enforced by templating
- Manual duplication errors eliminated by design

### Principle III: Extension Modularity for Larger Keyboards
**Status**: ✅ PASS (ENHANCED)

**Analysis**: The per-layer extension system (3x5_3_pinky, 3x6_3, board-specific overrides) directly implements this principle with better tooling. The YAML schema explicitly separates core layout from extensions, making the architecture self-documenting.

**Implementation Impact**:
- Extensions defined per-layer in `config/keymap.yaml` under `extensions:` key
- Core 36-key layout preserved during extension generation
- Gaming layers and number row support maintained for larger keyboards
- Extension selection managed via `config/boards.yaml` inventory

### Principle IV: Keyboard Inventory Transparency
**Status**: ✅ PASS (ENHANCED)

**Analysis**: The `config/boards.yaml` file becomes the new source of truth for keyboard inventory, replacing the need for manual `KEYBOARDS.md`. This file will list all keyboards with their firmware types, extension requirements, and build configurations.

**Implementation Impact**:
- `config/boards.yaml` provides machine-readable inventory
- Could auto-generate `KEYBOARDS.md` from `boards.yaml` for human consumption
- Adding a new keyboard requires updating `boards.yaml` (enforced by generator)

**QUESTION FOR USER**: Should we auto-generate `KEYBOARDS.md` from `boards.yaml`, or maintain both files manually?

### Principle V: Visual Keymap Documentation
**Status**: ✅ PASS (MANDATORY - IN SCOPE)

**Analysis**: Visual documentation (SVG/PNG images) is mandatory per constitution and is now explicitly required in the spec (FR-023, FR-024, FR-025, FR-026). Visualization MUST be integrated into the code generation workflow.

**Implementation Impact**:
- Visual diagrams (SVG/PNG) MUST be generated automatically after keymap generation (FR-024)
- Visual diagrams MUST be placed in `docs/keymaps/` directory (FR-025)
- Visualization MUST be part of the main `generate.sh` pipeline, not manual (FR-026)
- User wants actual images (not ASCII art)

**Spec Changes Made**:
- Added FR-023: Visual documentation (SVG/PNG/images) integrated into pipeline
- Added FR-024: Automatic visualization generation (flexible tooling - may use keymap-drawer, custom generator, or other tools)
- Added FR-025: Diagrams placed in docs/keymaps/ directory
- Added FR-026: Visualization is part of main pipeline (not manual)
- Removed "Visual keymap generation" from Out of Scope

**Visualization Options**:
1. **Use existing keymap-drawer** (via generate_keymap_diagram.sh) - if it works with generated keymaps
2. **Custom Python visualization generator** - directly from YAML using matplotlib/Pillow/SVG libraries
3. **Other suitable tools** - flexibility to choose best option during implementation

**Integration Strategy** (example using existing script):
```python
# In scripts/generate.py main()
for board in boards:
    # 1. Generate keymap files
    generate_keymap(board)

    # 2. Generate visualization (flexible approach TBD during implementation)
    # Option A: Call existing script if compatible
    # Option B: Custom Python viz generator from YAML
    generate_visualization(board, layers)
```

### Summary
- **Passing**: 5/5 principles pass ✅
- **Enhanced**: Principles II, III, IV, V are strengthened by this feature
- **Blocking Issues**: None

---

## Post-Design Constitution Re-check

**Re-evaluated after Phase 1 design (research, data model, contracts)**

### Principle I: Upstream Modularity
**Status**: ✅ PASS (CONFIRMED)

**Post-Design Analysis**: The detailed file structure confirms complete isolation:
- Generator scripts in `scripts/` (Python modules)
- Generated keymaps in `qmk/keymaps/<board>_dario/`
- Unified configs in `config/` (new directory, zero upstream conflict)
- All personal code remains out of `quantum/`, `keyboards/*/` base directories

**No changes needed**.

### Principle II: Core 36-Key Layout Consistency
**Status**: ✅ PASS (STRENGTHENED)

**Post-Design Analysis**: Data model enforces consistency:
- `Layer.core` validation requires exactly 36 keys (data-model.md)
- `LayerCompiler` ensures core is applied before extensions
- Generator contracts guarantee identical translation across all boards
- Impossible to have inconsistent core layouts (compile-time guarantee)

**Architecture improvement**: Better than manual approach (was error-prone, now impossible to violate).

### Principle III: Extension Modularity for Larger Keyboards
**Status**: ✅ PASS (ENHANCED WITH CLEAR BOUNDARIES)

**Post-Design Analysis**: Extension system is well-defined:
- `LayerExtension` dataclass with validation (data-model.md)
- Per-layer extension definitions (not global)
- Board references extensions via `boards.yaml` (clear ownership)
- Gaming layers handled via `extra_layers` in board config

**Architecture improvement**: Code generation eliminates need for wrapper macros - generator brute-forces complete keymaps for each board size, automatically padding from 36-key core to target board size (36, 42, 58 keys).

### Principle IV: Keyboard Inventory Transparency
**Status**: ✅ PASS (MACHINE-READABLE NOW)

**Post-Design Analysis**: `config/boards.yaml` provides:
- Complete board inventory in structured format
- Firmware type, features, status per board
- Machine-parseable for automation
- Auto-generate `KEYBOARDS.md` confirmed in quickstart.md

**Architecture improvement**: Inventory is now part of the build system, not just documentation.

**Answer to open question**: YES, auto-generate `KEYBOARDS.md` from `boards.yaml` (quickstart Step 5 defines this).

### Principle V: Visual Keymap Documentation
**Status**: ✅ PASS (DESIGN COMPLETE)

**Post-Design Analysis**: Visualization strategy confirmed with flexible tooling:
- Visual diagram generation (SVG/PNG images) in `ICodeGenerator.generate_visualization()` contract
- Placed in `docs/keymaps/` directory (FR-025)
- Integrated into main generation pipeline (FR-026)
- Automation confirmed: Part of `scripts/generate.py` pipeline
- Flexible implementation: May use keymap-drawer, custom Python generator, or other suitable tools

**Implementation plan**: Phase 1 includes visualization (quickstart.md).

**Spec updated**: Visual keymap generation now IN SCOPE (FR-023, FR-024, FR-025, FR-026). Removed from "Out of Scope" section.

### Final Assessment

**All Principles**: ✅ PASS

**Enhancements Delivered**:
- Principle II: Architectural guarantee of consistency (was manual, now automated)
- Principle III: Structured extension system (was ad-hoc, now typed)
- Principle IV: Machine-readable inventory (was documentation-only, now operational)
- Principle V: Automated visualization (was manual, will be automated)

**Concerns Resolved**:
- Principle V automation strategy confirmed in quickstart.md
- `KEYBOARDS.md` auto-generation confirmed (Phase 5 tooling)

**Design Approval**: Constitution check PASSED. No blocking issues for implementation.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Current State** (QMK userspace):
```text
qmk_userspace/
├── keyboards/              # Per-keyboard keymaps (hand-written)
│   ├── bastardkb/skeletyl/keymaps/dario/
│   ├── boardsource/lulu/keymaps/dario/
│   └── lily58/keymaps/dario/
├── users/dario/            # Shared userspace code
│   ├── layers.h            # Layer definitions (manual sync nightmare)
│   ├── dario.h             # Shared constants
│   └── dario.c
├── scripts/
│   └── generate_keymap_diagram.sh
├── build_all.sh
├── CLAUDE.md
└── qmk.json                # Build targets
```

**Target State** (Unified monorepo):
```text
keyboard-config/            # Root (renamed from qmk_userspace)
├── config/                 # ✨ NEW: Unified configuration (user-editable)
│   ├── keymap.yaml         # Core keymap definition with layers & extensions
│   ├── boards.yaml         # Board inventory with firmware/extension mapping
│   └── aliases.yaml        # Firmware-agnostic behavior aliases (hrm, lt, etc.)
│
├── keyboards/              # QMK keymaps (GENERATED - DO NOT EDIT)
│   │                       # NOTE: Must be in keyboards/ for QMK userspace to find them
│   ├── bastardkb/skeletyl/promicro/keymaps/dario/
│   │   ├── keymap.c        # Generated from config/keymap.yaml
│   │   ├── config.h        # Generated settings
│   │   ├── rules.mk        # Generated rules
│   │   └── README.md       # Generated with ASCII art visualization
│   ├── boardsource/lulu/rp2040/keymaps/dario/
│   └── lily58/rev1/keymaps/dario/
│
├── qmk/config/             # QMK-specific settings (user-editable)
│       ├── global/         # Shared QMK settings
│       │   ├── config.h    # Global QMK config (chordal hold, tapping terms)
│       │   └── rules.mk    # Global feature flags
│       └── boards/         # Board-specific QMK settings
│           ├── skeletyl.mk # Board-specific features (OLED, RGB, etc.)
│           ├── lulu.mk
│           └── lily58.mk
│
├── zmk/                    # ✨ NEW: ZMK-specific files (migrated from separate repo)
│   ├── keymaps/            # GENERATED: ZMK keymaps (auto-generated, do not edit)
│   │   ├── corne_dario/
│   │   │   ├── corne.keymap      # Generated from config/keymap.yaml
│   │   │   └── corne.conf        # Generated settings
│   │   └── [other_zmk_boards]/
│   │
│   └── config/             # MANUAL: ZMK-specific settings (user-editable)
│       ├── global/         # Shared ZMK behaviors
│       │   ├── behaviors.dtsi    # Homerow mod behaviors (&hrm)
│       │   └── settings.conf     # Global ZMK settings
│       └── boards/         # Board-specific ZMK settings
│           └── corne.conf        # Board-specific features
│
├── scripts/                # Code generation and build scripts
│   ├── generate.sh         # ✨ NEW: Main codegen entry point (calls all below)
│   ├── generate_qmk.py     # ✨ NEW: QMK keymap generator
│   ├── generate_zmk.py     # ✨ NEW: ZMK keymap generator
│   ├── migrate.sh          # ✨ NEW: Migrate existing configs to unified format
│   ├── add_board.sh        # ✨ NEW: Add new keyboard to system
│   └── generate_keymap_diagram.sh  # Existing visualization tool (integrated)
│
├── tests/                  # ✨ NEW: Generator tests
│   ├── test_parser.py      # Test YAML parsing
│   ├── test_qmk_gen.py     # Test QMK generation
│   ├── test_zmk_gen.py     # Test ZMK generation
│   └── fixtures/           # Test YAML fixtures
│
├── .github/workflows/
│   └── build-all.yml       # ✨ MODIFIED: Build QMK + ZMK binaries
│
├── CLAUDE.md               # Updated operational guidance
├── KEYBOARDS.md            # ✨ OPTIONAL: Auto-generated from boards.yaml
└── build_all.sh            # ✨ MODIFIED: Generate keymaps first, then build
```

**Structure Decision**:
- **Monorepo approach** with unified configuration in `config/` directory
- **Generated vs Manual files clearly separated**: `qmk/keymaps/` and `zmk/keymaps/` are fully generated, `qmk/config/` and `zmk/config/` are user-editable firmware-specific settings
- **Single source of truth**: `config/keymap.yaml` defines all layers and extensions
- **Board inventory centralized**: `config/boards.yaml` maps keyboards to extensions
- **Generator scripts in Python**: Better YAML parsing, string templating, and testing than Bash
- **Existing QMK userspace**: `users/dario/` directory becomes obsolete (replaced by generator templates)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. All principles pass or are enhanced by this feature.
