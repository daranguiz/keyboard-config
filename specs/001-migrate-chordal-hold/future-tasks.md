# Future Tasks & Ideas

This document tracks ideas and tasks for future work that are related to keyboard firmware and keymaps but are out of scope for the current feature (migrate-chordal-hold).

## Keymap Management & Organization

### Modular Keymap System
**Goal**: Create one unified, modular set of keymaps that can be deployed to all keyboards instead of manually maintaining separate keymaps.

**Benefits**:
- Single source of truth for keymap layout
- Easier maintenance and updates
- Consistent behavior across all keyboards
- Reduced duplication

**Considerations**:
- Need to handle keyboard-specific differences (number of keys, available features)
- May require abstractions for common layers/behaviors
- Build system integration for generating keyboard-specific configs from common source

---

### Cleanup & Deduplication
**Goal**: Remove redundancy and remnants of old experiments from keymap configurations.

**Areas to clean**:
- Unused keymap settings and configurations
- Old experimental features no longer in use
- Duplicate definitions across keymaps
- Dead code and commented-out sections

**Benefits**:
- Easier to understand and maintain codebase
- Faster compilation
- Clearer intent in configuration

---

## Cross-Firmware Synchronization

### QMK ↔ ZMK Keymap Sync
**Goal**: Keep keymaps synchronized between QMK repository and separate ZMK repository.

**Context**: Have a separate ZMK repo for ZMK-based keyboards that should have identical keymap layout to QMK keyboards.

**Approach Ideas**:
- Shared keymap definition format (JSON/YAML?)
- Generator scripts to produce QMK and ZMK configs from common source
- Automated sync/validation tools
- Documentation of firmware-specific features that can't be shared

**Challenges**:
- Different feature sets between QMK and ZMK
- Different configuration formats
- Different keycodes/behaviors

---

## Visualization & Documentation

### Keymap Visualization Generation
**Goal**: Generate PNG/visual representations of keyboard layouts (beyond ASCII art).

**Requirements**:
- Generate visual layout diagrams like those seen on keymap websites
- Support multiple layers
- Show modifiers, special keys, tap/hold behaviors
- Export as PNG or SVG

**Use Cases**:
- Documentation
- Sharing layouts with others
- Quick reference
- Visual validation of layout changes

**Potential Tools**:
- Custom generator using QMK's JSON data
- Integration with existing keymap viz tools
- Web-based generator for interactive viewing

---

## Notes

- These tasks are intentionally deferred until after the current migration work is complete
- Prioritization TBD based on pain points after migration
- Some tasks may become separate features with their own specs
