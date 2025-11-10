# Feature Specification: QMK Keymap Refactoring & Modularization

**Feature Branch**: `002-keymap-refactor`
**Created**: 2025-11-09
**Status**: Draft
**Input**: User description: "Refactor QMK keymap configuration to create a modular, maintainable system with a single source of truth for shared layouts across multiple keyboards, implement keymap visualization tools, and standardize naming conventions for all custom keymaps."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Modular Base Layout Management (Priority: P1)

As a keyboard user with multiple QMK keyboards, I want to maintain a single source of truth for my core 3x5_3 layout so that when I update my keymap preferences, the changes automatically apply to all my keyboards without manual duplication.

**Why this priority**: This is the foundational requirement that eliminates the maintenance burden and enables all other improvements. Without this, every other feature would need to be maintained separately across keyboards.

**Independent Test**: Can be fully tested by modifying the core 3x5_3 layout definition once, compiling firmware for different keyboards (e.g., Lulu, Lily58), and verifying that all keyboards receive identical base layer behavior.

**Acceptance Scenarios**:

1. **Given** I have multiple keyboards that support 3x5_3 layouts, **When** I modify the base layer keymap in the shared source, **Then** all keyboards compile with the identical base layer without manual file edits
2. **Given** I have a shared base layer definition, **When** I compile firmware for any supported keyboard, **Then** the build system automatically includes the correct base layer
3. **Given** I want to change a key binding in my base layer, **When** I make a single change to the shared layout, **Then** the next firmware build for any keyboard reflects this change

---

### User Story 2 - Keyboard-Specific Customization (Priority: P2)

As a keyboard user with different keyboard models, I want to customize hardware-specific features (extra keys, OLED screens, encoders) for each keyboard while keeping the base layout shared, so that I can take advantage of each keyboard's unique capabilities without duplicating common configuration.

**Why this priority**: This builds on the modular base (P1) by enabling hardware differentiation. It's essential for utilizing advanced hardware features but depends on having the shared base working first.

**Independent Test**: Can be tested by configuring OLED display settings for Lulu without affecting other keyboards, verifying that the base layer remains identical while hardware-specific code executes correctly.

**Acceptance Scenarios**:

1. **Given** my Lulu keyboard has an OLED screen, **When** I add OLED display code to Lulu-specific configuration, **Then** the OLED functions correctly and other keyboards are unaffected
2. **Given** my Lulu and Lily58 have extra keys beyond the 3x5_3 base, **When** I define mappings for these extra keys, **Then** only those keyboards include the extra key definitions
3. **Given** I have keyboard-specific features configured, **When** I update the base layer, **Then** the keyboard-specific features remain intact and functional

---

### User Story 3 - Keymap Visualization (Priority: P3)

As a keyboard user, I want to generate visual diagrams of my keymap that I can print or share, so that I can have a physical reference for my layout and easily see what all my layers do without reading code.

**Why this priority**: This is a quality-of-life feature that improves documentation but isn't required for the keyboard to function. It's valuable after the core refactoring is complete.

**Independent Test**: Can be tested by running a visualization generation command and verifying that the output image accurately represents the keymap definition with proper layer labels and key symbols.

**Acceptance Scenarios**:

1. **Given** I have completed keymap configuration, **When** I run the visualization tool, **Then** it generates a visual diagram showing all layers with correct key labels
2. **Given** I have ASCII art keymap comments in my source files, **When** I view the keymap files, **Then** the ASCII art clearly shows the layout structure
3. **Given** I have generated a keymap visualization, **When** I update my keymap, **Then** I can regenerate the visualization to reflect the changes
4. **Given** I want to share my layout, **When** I generate a visualization, **Then** the output format is suitable for printing or digital sharing (PNG/SVG)

---

### User Story 4 - Code Cleanup and Maintainability (Priority: P1)

As a developer maintaining QMK keymaps, I want all legacy experimental code, dead code, and redundant configurations removed, so that the codebase is easy to understand, modify, and maintain without confusion from outdated features.

**Why this priority**: This is foundational work that must happen alongside or before P1. Clean code is essential for implementing the modular system effectively and avoiding bugs from dead code.

**Independent Test**: Can be tested by reviewing the codebase for commented-out code, unused feature flags, and old experiment references, verifying none exist, and confirming all remaining code is actively used.

**Acceptance Scenarios**:

1. **Given** the existing keymap contains old experiment code, **When** I review the refactored codebase, **Then** no commented-out experimental code exists
2. **Given** there are redundant keymap definitions across keyboards, **When** I inspect the refactored structure, **Then** common definitions exist only once in the shared source
3. **Given** there are unused configuration flags, **When** I review rules.mk and config.h files, **Then** only actively used settings remain
4. **Given** I want to understand the current keymap, **When** I read the code, **Then** all present code is clearly documented and serves a current purpose

---

### User Story 5 - Consistent Naming Convention (Priority: P1)

As a keyboard user maintaining multiple keymap configurations, I want all my custom keymaps to use the consistent name "dario" instead of variations like "daranguiz", "daranguiz_miryoku", or other inconsistent names, so that I can easily identify and manage my keymaps across all keyboards.

**Why this priority**: This is a foundational organizational improvement that should be done as part of the initial cleanup (P1). Inconsistent naming makes it harder to locate files and creates confusion about which keymaps are current vs. experimental.

**Independent Test**: Can be tested by searching the codebase for keymap directories, verifying that all custom keymaps use exactly "dario" as the directory name, and confirming that no legacy naming patterns remain.

**Acceptance Scenarios**:

1. **Given** keymaps currently exist with names like "daranguiz" or "daranguiz_miryoku", **When** I complete the refactoring, **Then** all custom keymap directories are named exactly "dario"
2. **Given** I want to compile firmware for any of my keyboards, **When** I use the build command with `:dario`, **Then** the firmware compiles correctly with consistent naming
3. **Given** I search for my keymaps in the repository, **When** I look for directories named "dario", **Then** I find all my custom configurations without searching for name variations

---

### Edge Cases

- What happens when a keyboard doesn't support the full 3x5_3 layout (fewer keys)?
- How does the system handle keyboards with different layouts that share some but not all layers?
- What happens if keyboard-specific code conflicts with shared base layer definitions?
- How are features handled when they're available on some keyboards but not others (e.g., RGB, OLED)?
- **Clarified**: When the visualization tool encounters custom keycodes or macros not in its symbol set, it will display them with their macro name or ID in placeholder symbols
- What happens when compiling for a keyboard that wasn't explicitly configured for the modular system?
- What happens to existing firmware builds and git history when renaming keymap directories?
- How are references to old keymap names handled in documentation or build scripts?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single shared source file containing the core 3x5_3 base layer keymap that can be included by multiple keyboard configurations
- **FR-002**: System MUST support keyboard-specific configuration files that can add or override features without modifying the shared base layer
- **FR-003**: System MUST enable keyboard-specific hardware features (OLED, encoders, extra keys) through separate configuration without affecting other keyboards
- **FR-004**: System MUST include ASCII art representations of keymap layers within source code comments for quick reference
- **FR-005**: System MUST provide a tool or script to generate visual keymap diagrams (PNG or SVG format) from keymap definitions, displaying unknown custom keycodes with their macro name or ID in placeholder symbols
- **FR-006**: System MUST remove all commented-out code, unused experimental features, and dead configuration options from keymap files
- **FR-007**: System MUST eliminate redundant keymap definitions across different keyboard directories
- **FR-008**: System MUST rename all custom keymap directories to use exactly "dario" as the keymap name
- **FR-009**: System MUST remove all legacy keymap directories with names like "daranguiz", "daranguiz_miryoku", or other historical variations
- **FR-010**: System MUST maintain compatibility with QMK build system (make and qmk compile commands) after renaming
- **FR-011**: System MUST preserve all currently-used functionality while reorganizing code structure
- **FR-012**: System MUST document the new modular structure with clear instructions for adding new keyboards

### Key Entities

- **Shared Base Layout**: The common 3x5_3 keymap definition that applies identically across all keyboards, including all base layers (alpha, navigation, symbols, etc.)
- **Keyboard Profile**: Configuration specific to each keyboard model, including hardware capabilities (OLED, encoders, RGB), physical layout (number of keys, rows), and custom layer definitions
- **Keymap Visualization**: Visual representation of the keyboard layout showing all layers, key labels, modifiers, and tap/hold behaviors in printable format
- **Keymap Identity**: Standardized naming convention ("dario") used consistently across all keyboard directories to identify custom configurations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Modifying the shared base layer requires editing only a single source file to affect all keyboards
- **SC-002**: Adding a new keyboard to the modular system requires creating one small configuration file without duplicating the entire keymap
- **SC-003**: Compilation time remains within 10% of current build times after refactoring
- **SC-004**: All existing keymap functionality (current working features) continues to work identically after refactoring
- **SC-005**: Codebase size is reduced by at least 40% through elimination of redundant definitions
- **SC-006**: Keymap visualization can be generated in under 5 seconds and accurately represents all defined layers
- **SC-007**: ASCII art in source files allows a developer to understand the layout structure in under 30 seconds without compiling
- **SC-008**: Zero commented-out code blocks or unused configuration flags exist in the final codebase
- **SC-009**: Documentation enables a new keyboard to be added to the modular system in under 15 minutes
- **SC-010**: 100% of custom keymap directories use the name "dario" with no legacy name variations remaining
- **SC-011**: Build commands using `:dario` work consistently across all keyboards without needing to remember different naming patterns

## Assumptions *(if applicable)*

- The user is maintaining keymaps for multiple keyboards (at minimum: Lulu, Lily58, and at least one other)
- All keyboards share a compatible 3x5_3 core layout (3 rows, 5 columns per hand, 3 thumb keys per hand)
- The current keymaps have similar base layers that can be unified into a single source
- The user has access to standard QMK build tools and toolchain
- Visualization output format (PNG/SVG) is sufficient; interactive web-based visualization not required
- Current keymap contains legacy experimental code from previous features (e.g., bilateral combinations patch work)
- The refactoring will be done on QMK firmware with standard community layout support available
- Existing keymap names include variations like "daranguiz", "daranguiz_miryoku" that need standardization
- No external documentation or tools depend on the specific legacy keymap names (safe to rename)

## Dependencies *(if applicable)*

- QMK Firmware build system (Makefile, build scripts)
- QMK CLI tools (if used for visualization or layout processing)
- Existing keyboard hardware definitions in QMK (info.json, config.h, rules.mk)
- C preprocessor capabilities for conditional compilation based on keyboard features
- Git for version control of the refactored structure

## Out of Scope *(if applicable)*

- Creating new key behaviors or custom keycodes beyond what currently exists
- Porting keymaps to keyboards not currently owned or used by the user
- Web-based interactive keymap editors
- Real-time keymap switching without recompilation
- Automated testing framework for keymap behavior
- Integration with VIA or other dynamic keymap tools
- Multi-language keyboard layouts
- Firmware size optimization beyond what's achieved through code deduplication
- Backward compatibility with old keymap names (clean break to "dario" naming)

## Clarifications

### Session 2025-11-09

- Q: How should the visualization tool handle unknown/custom keycodes? → A: Display unknown keycodes with their macro name or ID in placeholder symbols

## Future Work *(deferred features)*

### Gaming Layer for Extended Keyboards

A dedicated gaming layer with QWERTY layout utilizing all available keys (including number rows) on keyboards like Lulu and Lily58 has been identified as a valuable feature but is deferred to future work. Before implementation, the following needs to be determined:

- Layer activation mechanism (which key combination to use for toggling into gaming mode)
- Layer deactivation method (return to typing layout)
- Whether to use momentary layer switch, toggle, or one-shot behavior

This feature should be implemented after the core modular system is complete, as it will benefit from the keyboard-specific customization framework established in this refactor.
