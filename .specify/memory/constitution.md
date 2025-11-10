<!--
Sync Impact Report:
- Version change: [NEW] → 1.0.0
- Modified principles: N/A (initial constitution)
- Added sections:
  * Core Principles (5 principles defined)
  * Keymap Development Workflow
  * Governance
- Removed sections: N/A
- Templates requiring updates:
  ✅ plan-template.md - verified, no constitution-specific gates yet
  ✅ spec-template.md - verified, compatible with keymap feature specs
  ✅ tasks-template.md - verified, compatible with keymap implementation tasks
- Follow-up TODOs: None
-->

# Dario's QMK Firmware Fork Constitution

## Core Principles

### I. Upstream Modularity

All personal customizations MUST be isolated from upstream QMK code to enable conflict-free syncing with the main QMK repository.

**Implementation Rules:**
- All personal keymaps MUST reside in `keyboards/<keyboard>/keymaps/dario/`
- Custom code MUST use QMK's user space features when extending beyond keymap files
- Build scripts and personal tools MUST be placed in the repository root (e.g., `build_lulu.sh`)
- NEVER modify upstream keyboard definitions, core quantum/ code, or build system files
- Changes to CLAUDE.md and documentation in root are acceptable as they don't conflict with upstream

**Rationale:** QMK upstream evolves constantly with new features, bug fixes, and keyboard support. Maintaining clean separation ensures the ability to `git pull` upstream changes without merge conflicts, allowing access to the latest QMK improvements while preserving personal customizations.

### II. Core 36-Key Layout Consistency (NON-NEGOTIABLE)

The fundamental 36-key layout (3x5 matrix + 3 thumb keys per hand) MUST be identical across all keyboards, providing a consistent typing experience regardless of hardware.

**Implementation Rules:**
- The core `LAYOUT_split_3x5_3` keymap MUST be the same for every keyboard
- All base layer keys, layer definitions, and layer access keys MUST match
- Home row mods positioning MUST be consistent (LGUI_T(A), LALT_T(R), LCTL_T(S), LSFT_T(T) pattern)
- Layer functionality (NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON) MUST provide the same behavior
- When switching between keyboards, muscle memory MUST transfer without relearning

**Rationale:** Consistency enables true keyboard portability. The investment in learning optimal key positions and developing muscle memory should transfer seamlessly between different physical keyboards. This prevents the cognitive overhead of context-switching layouts.

### III. Extension Modularity for Larger Keyboards

Keyboards with keys beyond the core 36-key layout MAY add supplementary functionality, but MUST preserve the core layout mapping.

**Implementation Rules:**
- Additional outer columns or number rows are ALLOWED for extra functionality
- Gaming layers with traditional QWERTY layout are ALLOWED for keyboards with sufficient keys (e.g., Lulu 58-key)
- Extended layouts MUST NOT remap or change the core 36-key positions
- Extended keys typically used for: extra pinky keys, dedicated function keys, gaming mode layers
- Extensions MUST be documented in the keyboard's keymap with clear ASCII visualization

**Rationale:** Different keyboards serve different purposes. A 58-key Lulu can support gaming scenarios that a compact 36-key board cannot. However, the core typing layout must remain sacred to preserve principle II. Extensions are additive enhancements, not replacements.

### IV. Keyboard Inventory Transparency

At any point in time, it MUST be immediately obvious which keyboards are supported in this fork and where their configurations reside.

**Implementation Rules:**
- A `KEYBOARDS.md` file MUST exist in the repository root listing all personal keyboards
- Each entry MUST include: keyboard name, path to keymap, hardware variant, key count, and status
- The `build_lulu.sh` pattern (build scripts for specific keyboards) is ALLOWED in repository root
- When a new keyboard is added, `KEYBOARDS.md` MUST be updated in the same commit
- Deprecated or removed keyboards MUST be marked as such, not silently deleted from documentation

**Rationale:** Months may pass between keyboard usage. Clear inventory prevents confusion about which keyboards are configured, where their files are, and whether they're still maintained. This is particularly important when deciding whether to sync upstream changes that affect specific keyboards.

### V. Visual Keymap Documentation (MANDATORY)

Every keymap change MUST be accompanied by a visual representation of all layer layouts.

**Implementation Rules:**
- ASCII art keymap visualizations are REQUIRED as the minimum standard
- Each layer (BASE, NAV, MOUSE, MEDIA, NUM, SYM, FUN, BUTTON) MUST have a visual representation
- Visualizations MUST be embedded in keymap documentation (e.g., README.md in keymap directory)
- Future enhancement: Auto-generated graphical keymap images showing physical key positions
- Visualization MUST be updated in the same commit as keymap changes

**Format Example:**
```
Layer: BASE (Colemak-DH)
╭─────┬─────┬─────┬─────┬─────╮ ╭─────┬─────┬─────┬─────┬─────╮
│  Q  │  W  │  F  │  P  │  G  │ │  J  │  L  │  U  │  Y  │  '  │
├─────┼─────┼─────┼─────┼─────┤ ├─────┼─────┼─────┼─────┼─────┤
│GUI/A│ALT/R│CTL/S│SFT/T│  D  │ │  H  │SFT/N│CTL/E│ALT/I│GUI/O│
├─────┼─────┼─────┼─────┼─────┤ ├─────┼─────┼─────┼─────┼─────┤
│BTN/Z│AGR/X│  C  │  V  │  B  │ │  K  │  M  │  ,  │AGR/.│BTN//│
╰─────┴─────┼─────┼─────┼─────┤ ├─────┼─────┼─────┼─────┴─────╯
            │MED/ │NAV/ │MOU/ │ │SYM/ │NUM/ │FUN/ │
            │ ESC │ SPC │ TAB │ │ ENT │BSPC │ DEL │
            ╰─────┴─────┴─────╯ ╰─────┴─────┴─────╯
```

**Rationale:** Keymaps are complex, multi-dimensional structures. Without visual documentation, understanding or reviewing changes requires mentally parsing keymap arrays. Visual representation enables quick comprehension, easier reviews, and serves as reference documentation when returning to the codebase after time away.

## Keymap Development Workflow

### Adding a New Keyboard

1. Create keymap directory: `keyboards/<manufacturer>/<model>/keymaps/dario/`
2. Implement `keymap.c` with core 36-key layout matching existing keyboards
3. Add visual layer documentation in keymap directory README
4. Create build script if desired: `build_<keyboard>.sh` in repository root
5. Update `KEYBOARDS.md` with new entry
6. Test compilation: `make <keyboard>:dario`
7. Commit all changes together with descriptive message

### Modifying Existing Keymap

1. Make changes to `keymap.c` in target keyboard
2. Update ASCII layer visualizations in keymap documentation
3. If core 36-key layout changed, propagate to ALL keyboards (principle II)
4. Test compilation for affected keyboards
5. Commit with description of what changed and why

### Syncing with Upstream QMK

1. Review upstream changes: `git log upstream/master`
2. Pull upstream: `git pull upstream master`
3. Resolve conflicts (should be minimal per principle I)
4. Test compilation of all personal keyboards
5. Update CLAUDE.md if upstream architecture changed significantly
6. Commit merge

## Governance

### Constitution Authority

This constitution defines the mandatory rules for this personal QMK firmware fork. All keymap additions, modifications, and repository changes MUST comply with these principles.

### Amendment Procedure

1. Amendments require explicit decision and documentation
2. Version bumping follows semantic versioning:
   - **MAJOR**: Fundamental principle redefined or removed (e.g., abandoning 36-key consistency)
   - **MINOR**: New principle added or existing principle materially expanded
   - **PATCH**: Clarifications, wording improvements, non-semantic refinements
3. When constitution is amended, dependent templates in `.specify/templates/` MUST be reviewed for consistency
4. Amendment commits MUST reference version change and rationale

### Compliance Verification

- Before committing keymap changes, verify principle V (visualization updated)
- When adding keyboards, verify principle IV (inventory updated)
- When modifying core layout, verify principle II (consistency across keyboards)
- Monthly review: Ensure `KEYBOARDS.md` reflects actual repository state
- Quarterly review: Verify no upstream conflicts introduced in personal keymap directories

### Runtime Development Guidance

For day-to-day development guidance including build commands, architecture overview, and common development tasks, reference `CLAUDE.md` in the repository root. That file provides operational guidance; this constitution provides governance principles.

**Version**: 1.0.0 | **Ratified**: 2025-11-07 | **Last Amended**: 2025-11-07
