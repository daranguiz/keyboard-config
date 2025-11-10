# Implementation Plan: QMK Keymap Refactoring & Modularization

**Branch**: `002-keymap-refactor` | **Date**: 2025-11-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-keymap-refactor/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refactor QMK keymap configuration to create a modular, maintainable system with a single source of truth for the core 3x5_3 layout shared across multiple keyboards (Lulu, Lily58, Skeletyl). The refactoring will:

1. **Eliminate duplication** by extracting the common 36-key base layer into a shared source file
2. **Enable keyboard-specific customization** through a clean separation between shared base layout and hardware-specific features (OLED, extra keys, encoders)
3. **Standardize naming** by consolidating all custom keymaps to use "dario" instead of variations like "daranguiz_miryoku"
4. **Improve maintainability** by removing dead code, experimental features, and redundant configuration
5. **Enhance documentation** through ASCII art visualizations and automated keymap diagram generation tools

The technical approach leverages QMK's existing preprocessor-based configuration system and file inclusion capabilities to create a hierarchical keymap structure compatible with the standard QMK build system.

## Technical Context

**Language/Version**: C99 (QMK firmware codebase)
**Primary Dependencies**: QMK Firmware build system (Make-based), avr-gcc/arm-none-eabi-gcc (MCU toolchains)
**Storage**: N/A (embedded firmware, configuration in source files)
**Testing**: Manual compilation and firmware flashing tests
**Target Platform**: Embedded keyboard controllers (ATmega32U4, RP2040)
**Project Type**: Embedded firmware with modular configuration system
**Performance Goals**: Compilation time within 10% of current baseline, no runtime performance impact
**Constraints**:
- Must maintain compatibility with QMK build system (`make keyboard:keymap` commands)
- Must not modify upstream QMK source (Constitution Principle I)
- Must preserve existing keyboard functionality during refactor
- Limited to C preprocessor for conditional compilation (no external build tools)

**Scale/Scope**:
- 3 keyboards (Lulu 58-key, Lily58 58-key, Skeletyl 36-key)
- 7 layers per keyboard (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON)
- ~150-200 lines of keymap array definitions per keyboard
- Estimated 40% code reduction through deduplication

**Architecture Approach**: ✅ RESOLVED - Hybrid approach using QMK userspace + layout wrapper macros:
1. **Userspace** (`users/dario/`) for shared C code and layer content definitions
2. **Layout wrapper macros** in each keymap's `keymap_config.h` for 3x5_3 abstraction
3. **Local keyboard files** for keyboard-specific features (OLED, RGB, encoders)
- See [research.md](research.md) for detailed analysis and rationale

**Visualization Tools**: ✅ RESOLVED - keymap-drawer (Python tool):
- Production-ready, actively maintained
- Input: QMK JSON (via `qmk c2json`)
- Output: SVG (convertible to PNG)
- Custom keycode mapping via configuration file
- See [research.md](research.md) for installation and usage details

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Upstream Modularity ✅ PASS

**Requirement**: All personal customizations MUST be isolated from upstream QMK code.

**Verification**:
- ✅ All changes will be in `keyboards/*/keymaps/dario/` directories only
- ✅ If using userspace, will be in `users/dario/` (QMK standard location for user code)
- ✅ Community layouts (if used) will be in `layouts/community/split_3x5_3/dario/`
- ✅ No modifications to upstream keyboard definitions, quantum/ code, or build system files
- ✅ Build scripts in repository root (acceptable per constitution)

**Impact**: No conflicts with upstream QMK updates.

### Principle II: Core 36-Key Layout Consistency (NON-NEGOTIABLE) ✅ PASS

**Requirement**: The fundamental 36-key layout MUST be identical across all keyboards.

**Verification**:
- ✅ This refactor's PRIMARY GOAL is to enforce this principle through shared source
- ✅ All keyboards (Lulu, Lily58, Skeletyl) will use identical core layout
- ✅ Layer definitions (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON) will be identical
- ✅ Home row mods positioning will be consistent: LGUI_T(A), LALT_T(R), LCTL_T(S), LSFT_T(T)

**Impact**: This feature directly implements and enforces this constitutional requirement.

### Principle III: Extension Modularity for Larger Keyboards ✅ PASS

**Requirement**: Keyboards with extra keys MAY add supplementary functionality while preserving core layout.

**Verification**:
- ✅ Lulu and Lily58 (58-key) can add gaming layer with extra keys
- ✅ OLED functionality is keyboard-specific extension (Lulu, Lily58 only)
- ✅ Extra keys beyond 36-key core preserved as additive features
- ✅ Extensions documented in keyboard-specific keymap files

**Impact**: Modular system will cleanly separate core layout from extensions.

### Principle IV: Keyboard Inventory Transparency ✅ PASS

**Requirement**: KEYBOARDS.md MUST list all personal keyboards and be updated with changes.

**Verification**:
- ✅ Existing KEYBOARDS.md will be updated as part of this refactor
- ✅ Each renamed keymap will be documented in same commit
- ✅ Build script references will be updated

**Impact**: KEYBOARDS.md update required as part of implementation.

### Principle V: Visual Keymap Documentation (MANDATORY) ✅ PASS

**Requirement**: Every keymap change MUST be accompanied by visual representation.

**Verification**:
- ✅ ASCII art keymap visualizations will be added to all keymap directories
- ✅ Each layer will have visual representation per constitutional format
- ✅ Automated visualization tool generation is a core feature requirement
- ✅ Documentation updated in same commits as keymap changes

**Impact**: Visualization generation is a primary deliverable of this feature.

### Overall Constitution Compliance: ✅ PASS

This feature is **highly aligned** with constitutional principles. It directly implements:
- Principle II enforcement (core layout consistency)
- Principle III support (clean extension modularity)
- Principle V fulfillment (visual documentation tooling)

No violations or exceptions required.

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

```text
# QMK Firmware - Embedded Project Structure

# Shared keymap code (approach TBD in Phase 0 research)
users/dario/                      # QMK userspace for shared code (option 3)
├── dario.h                       # Shared layer definitions, custom keycodes
├── dario.c                       # Shared keymap logic
└── rules.mk                      # Feature flags for shared code

OR

layouts/community/split_3x5_3/    # Community layout system (option 1)
└── dario/
    ├── keymap.c                  # Shared base keymap
    ├── config.h                  # Shared configuration
    └── rules.mk

# Keyboard-specific keymaps
keyboards/boardsource/lulu/keymaps/dario/
├── keymap.c                      # Lulu-specific (uses shared base)
├── config.h                      # Lulu hardware config
├── rules.mk                      # Lulu feature flags
├── oled.c                        # OLED display code (Lulu-specific)
├── README.md                     # Keymap documentation with ASCII art
└── features/                     # Optional modular features

keyboards/lily58/keymaps/dario/   # Renamed from daranguiz_miryoku
├── keymap.c                      # Lily58-specific (uses shared base)
├── config.h                      # Lily58 hardware config
├── rules.mk                      # Lily58 feature flags
├── oled.c                        # OLED display code (Lily58-specific)
├── README.md                     # Keymap documentation with ASCII art
└── features/

keyboards/bastardkb/skeletyl/keymaps/dario/  # Renamed from daranguiz_miryoku
├── keymap.c                      # Pure 36-key layout
├── config.h                      # Skeletyl hardware config
├── rules.mk                      # Skeletyl feature flags
└── README.md                     # Keymap documentation with ASCII art

# Visualization tooling
tools/                            # New directory for custom scripts
└── generate-keymap-viz.py        # Keymap visualization generator (TBD)

# Build automation
build_lulu.sh                     # Existing Lulu build script (updated)
build_lily58.sh                   # New Lily58 build script
build_skeletyl.sh                 # New Skeletyl build script

# Documentation
KEYBOARDS.md                      # Updated inventory
CLAUDE.md                         # Updated with refactor patterns
```

**Structure Decision**:

The exact approach for shared keymap code will be determined in Phase 0 research. Three primary options exist in QMK:

1. **Community Layouts** (`layouts/community/split_3x5_3/dario/`) - Standard QMK mechanism for shared layouts across keyboards
2. **Userspace** (`users/dario/`) - Standard QMK mechanism for shared user code
3. **Header Includes** - Simple header files with macro-based keymap definitions

All keyboard-specific code remains in `keyboards/*/keymaps/dario/` per Constitution Principle I.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations. This feature is fully compliant with all constitutional principles.

---

## Post-Design Constitution Review

**Status**: Phase 1 Complete (Research + Design)
**Review Date**: 2025-11-09

### Architectural Decisions Validation

After completing research and design phases, re-evaluating constitutional compliance:

#### Principle I: Upstream Modularity ✅ CONFIRMED

**Design Decision**: Hybrid approach (Userspace + Layout Wrappers)

**Compliance**:
- ✅ All shared code in `users/dario/` (QMK standard userspace location)
- ✅ All keyboard keymaps in `keyboards/*/keymaps/dario/` (isolated from upstream)
- ✅ No modifications to upstream QMK source
- ✅ Build scripts in repository root (acceptable per constitution)
- ✅ Visualization tooling is external (keymap-drawer, not in QMK repo)

**Impact**: Design maintains perfect upstream isolation. Future QMK updates will not conflict.

#### Principle II: Core 36-Key Layout Consistency ✅ CONFIRMED

**Design Decision**: Shared layer content via `users/dario/layers.h`

**Compliance**:
- ✅ Layer content defined once in `LAYER_BASE`, `LAYER_NAV`, etc. macros
- ✅ All keyboards use identical layer content via shared includes
- ✅ Wrapper macros map 36-key layout to physical keyboards without changing content
- ✅ Home row mods pattern enforced in shared layer definitions

**Impact**: Design achieves constitutional goal of consistent typing experience across keyboards. Single edit to `layers.h` updates all keyboards.

#### Principle III: Extension Modularity ✅ CONFIRMED

**Design Decision**: Local keyboard files for extensions + wrapper macros for extra keys

**Compliance**:
- ✅ Lulu and Lily58 can add OLED via local `oled.c` files
- ✅ Extra keys beyond 36-key core handled by wrapper macros
- ✅ Gaming layer can be added to specific keyboards without affecting others
- ✅ Core 36-key positions preserved in wrapper macros

**Impact**: Design enables keyboard-specific features while protecting core layout.

#### Principle IV: Keyboard Inventory Transparency ✅ CONFIRMED

**Design Decision**: Update KEYBOARDS.md as part of implementation

**Compliance**:
- ✅ File structure contract specifies KEYBOARDS.md update requirement
- ✅ Quickstart guide includes KEYBOARDS.md update in "Adding a New Keyboard" workflow
- ✅ Validation checklist includes KEYBOARDS.md verification

**Impact**: Design enforces constitutional documentation requirement.

#### Principle V: Visual Keymap Documentation ✅ CONFIRMED

**Design Decision**: keymap-drawer for automated generation + ASCII art in README.md

**Compliance**:
- ✅ File structure contract mandates ASCII art in README.md for each keymap
- ✅ Automated SVG generation via keymap-drawer (scriptable, repeatable)
- ✅ Visualization format matches constitutional example (layer-by-layer)
- ✅ Custom keycode handling preserves visual clarity

**Impact**: Design exceeds constitutional requirement with both ASCII art (in-repo) and automated SVG generation (for printing/sharing).

### Design-Specific Findings

**New capability enabled by design**: The data model (Section 5: Keymap Visualization) formalizes visualization as a first-class entity with defined fields, relationships, and validation rules. This goes beyond constitutional requirement to create a robust system.

**Risk mitigation**: File structure contract (contracts/file-structure.md) provides validation checklist to prevent accidental constitutional violations during implementation.

### Final Verdict: ✅ FULLY COMPLIANT

All five constitutional principles are satisfied by the designed architecture. No exceptions or waivers required.

**Ready to proceed to Phase 2 (Task Generation)**: Yes ✅

---

## Phase 1 Deliverables Summary

The following artifacts have been generated and are ready for implementation:

### Research Phase (Phase 0)
- ✅ [research.md](research.md) - Architectural decisions and tool selection

### Design Phase (Phase 1)
- ✅ [data-model.md](data-model.md) - Entity definitions and relationships
- ✅ [contracts/file-structure.md](contracts/file-structure.md) - Mandatory file structure and contracts
- ✅ [quickstart.md](quickstart.md) - Developer onboarding guide
- ✅ Agent context updated in CLAUDE.md

### Design Quality Gates
- ✅ All NEEDS CLARIFICATION items resolved
- ✅ Constitution Check passed (pre-design)
- ✅ Constitution Check re-validated (post-design)
- ✅ No complexity violations requiring justification

**Next step**: Run `/speckit.tasks` to generate implementation task breakdown.
