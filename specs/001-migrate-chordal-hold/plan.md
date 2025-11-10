# Implementation Plan: QMK Branch Consolidation and Chordal Hold Migration

**Branch**: `001-migrate-chordal-hold` | **Date**: 2025-11-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-migrate-chordal-hold/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Consolidate QMK fork branches (lily58/miryoku-bilateral-combinations and master from e3794835136f539e166cf9f7b3dcee7b47d55148 onward) into a single `personal` branch on top of upstream-synced master. Remove manually-applied bilateral combinations patch from QMK core and migrate personal keymaps to use QMK's native chordal hold feature instead. This eliminates the root cause of merge conflicts and enables clean syncing with upstream QMK while preserving keyboard functionality.

## Technical Context

**Language/Version**: C99 (QMK firmware), Make build system, Git 2.x
**Primary Dependencies**: QMK build system (make), avr-gcc/arm-none-eabi-gcc (MCU toolchains), git
**Storage**: Git repository (local branches, remote upstream)
**Testing**: QMK compile testing (`make <keyboard>:dario`), manual keyboard testing on physical hardware
**Target Platform**: QMK firmware repository (macOS development environment, builds target AVR/ARM microcontrollers)
**Project Type**: Repository refactoring and firmware feature migration
**Performance Goals**: N/A (not runtime performance, git/build operations only)
**Constraints**: Must preserve existing keymap functionality, must enable clean upstream sync
**Scale/Scope**:
- Two branches to consolidate (lily58/miryoku-bilateral-combinations, master from e3794835136f539e166cf9f7b3dcee7b47d55148)
- NEEDS CLARIFICATION: Number and location of personal keymaps requiring migration
- NEEDS CLARIFICATION: Location and extent of bilateral combinations patch modifications in QMK core
- NEEDS CLARIFICATION: Exact configuration syntax for chordal hold feature
- NEEDS CLARIFICATION: Feature parity between bilateral combinations and chordal hold

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Upstream Modularity ✅ PASS

**Status**: COMPLIANT

This feature REMOVES modifications to upstream QMK code (bilateral combinations patch) and consolidates all personal changes into personal keymaps and the `personal` branch structure. This directly supports the principle by eliminating the source of upstream merge conflicts.

**Actions**:
- Remove bilateral combinations patch from QMK core files
- Migrate functionality to keymap-level chordal hold configuration
- Establish clean master → personal branch structure

### Principle II: Core 36-Key Layout Consistency ⚠️ DEFERRED

**Status**: NOT EVALUATED IN THIS PHASE

The feature explicitly defers keymap refactoring and consistency checking to future work. From spec: "For the moment, other than the bilateral combinations thing, I don't necessarily want to make material changes to the keymaps themselves. They may be out of sync with each other, have redundant settings, etc etc, but I want to address that once I get everything cleaned up."

**Future Work**: After consolidation, evaluate cross-keyboard layout consistency.

### Principle III: Extension Modularity for Larger Keyboards ⚠️ DEFERRED

**Status**: NOT EVALUATED IN THIS PHASE (same rationale as Principle II)

### Principle IV: Keyboard Inventory Transparency 🔄 PENDING

**Status**: WILL BE ADDRESSED

The feature must create `KEYBOARDS.md` (per constitution requirement) after consolidation completes and all personal keymaps are identified.

**Action Required**: As part of Phase 1 deliverables, generate `KEYBOARDS.md` listing all keyboards with personal keymaps.

### Principle V: Visual Keymap Documentation ⚠️ DEFERRED

**Status**: NOT EVALUATED IN THIS PHASE

The spec explicitly defers keymap changes beyond chordal hold migration. Visual documentation updates should occur when layouts are standardized in future work.

**Future Work**: When keymap consistency work begins (addressing Principles II/III), update visual documentation.

---

**GATE DECISION**: ✅ PASS

**Rationale**:
- Primary goal (Principle I compliance) is directly addressed
- Deferred principles are explicitly out of scope per user requirements
- One actionable item (Principle IV - KEYBOARDS.md) identified for Phase 1

**No violations requiring justification in Complexity Tracking table.**

---

## Constitution Check - Post-Design Re-evaluation

*Re-evaluated after Phase 1 design completion*

### Principle I: Upstream Modularity ✅ PASS (Reconfirmed)

**Status**: FULLY COMPLIANT

Design confirms:
- Bilateral combinations patch removal from quantum/action.c eliminates all upstream modifications
- All personal code remains in keyboards/boardsource/lulu/keymaps/dario/ (keymap-level)
- KEYBOARDS.md and build scripts in repo root (allowed per constitution)
- personal branch structure keeps master clean for upstream tracking

**Outcome**: Design strengthens compliance with this principle.

### Principle IV: Keyboard Inventory Transparency ✅ PASS

**Status**: WILL BE SATISFIED

Design includes:
- KEYBOARDS.md creation as Phase 1 deliverable
- Complete inventory of personal keyboards (currently: 1 keyboard)
- All required fields per constitution (name, path, variant, key count, status)

**Outcome**: Principle will be fully satisfied upon implementation.

### Principles II, III, V: ⚠️ DEFERRED (Unchanged)

**Status**: Still out of scope for this feature

These principles remain deferred to future work per original assessment.

---

**FINAL GATE DECISION**: ✅ PASS (Reconfirmed)

Post-design evaluation confirms the plan fully satisfies all in-scope constitutional requirements. No new violations introduced.

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

This feature involves refactoring existing QMK repository structure, not adding new source code. Key areas:

```text
keyboards/
├── boardsource/lulu/
│   └── keymaps/dario/        # Personal keymap (needs chordal hold migration)
├── lily58/
│   └── keymaps/dario/        # Personal keymap (if exists)
└── [other keyboards with dario keymaps - TO BE DISCOVERED]

quantum/
└── [bilateral combinations patch locations - TO BE DISCOVERED]

tmk_core/
└── [bilateral combinations patch locations - TO BE DISCOVERED]

# Build scripts (personal, per constitution)
build_lulu.sh                  # Personal build script (existing)
[other build_*.sh scripts]     # To be discovered

# Documentation (personal, per constitution)
KEYBOARDS.md                   # TO BE CREATED (constitution requirement)
CLAUDE.md                      # Existing (may need updates)
```

**Structure Decision**: This is a repository refactoring task, not new feature development. The work involves:
1. Identifying and removing bilateral combinations patch code from QMK core (quantum/, tmk_core/)
2. Updating personal keymaps in keyboards/*/keymaps/dario/ to use chordal hold
3. Consolidating git branches into new structure (master tracks upstream, personal branch has customizations)
4. Creating KEYBOARDS.md inventory (constitution requirement)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
