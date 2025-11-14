# Feature Specification: Unified QMK/ZMK Keymap Configuration with Code Generation

**Feature Branch**: `003-unified-keymap-codegen`
**Created**: 2025-11-13
**Status**: Draft - In Review (reviewed through User Story 3)
**Input**: User description: "I have this repo, QMK userspace, as well as a separate ZMK repo. Right now, I have to maintain these two manually. If I make a change in one, I have to make a change in the other. It's a very manual process, very error prone, and usually just means my keymaps get out of date. I want to merge these into a single repo (or have a submodule or something, really whatever fits the model best), and I want to have a single common place where I can update my keymap. After I do so, it should auto-codegen for both QMK and ZMK."

---

## Review Notes

**Last Reviewed**: User Stories 1-4 (2025-11-13)

**Decisions Made**:
1. **Repository Architecture** [DECIDED]: Using **Monorepo** approach
   - Everything in one repository (can rename current qmk_userspace)
   - Structure: `config/` (unified keymap), `qmk/` (generated + settings), `zmk/` (generated + settings), `scripts/` (codegen)
   - Unified GitHub Actions builds binaries for all firmwares
   - Simpler than submodules, cleaner CI/CD, one repo to manage

2. **Configuration Format** [DECIDED]: Using **YAML** for unified keymap configuration
   - File: `config/keymap.yaml`
   - **Rationale**:
     - Human-readable with natural layout visualization
     - Comments for documentation
     - Excellent tooling support (schema validation, LSP, syntax highlighting)
     - Hierarchical structure fits keyboard layout organization well
     - Wide ecosystem support
   - **Alternatives considered**: JSON (too verbose, no comments), TOML (less intuitive for nested data), Custom DSL (too much implementation overhead)

3. **Core Layout Size Strategy** [DECIDED]: Using **per-layer optional extensions** approach for handling multiple board sizes

   **Context**: User has multiple board sizes that are variations on a core 36-key (3x5_3) layout:
   - **36-key (3x5_3)**: Base layout (e.g., Skeletyl)
   - **38-key (3x5_3_pinky)**: 36-key + 1 outer pinky key per side (hypothetical example)
   - **42-key (3x6_3)**: 36-key + full outer pinky column (3 keys per side) (e.g., Corne)
   - **58-key**: Completely different layout with number row (e.g., Lulu, Lily58 - uses board-specific wrappers, not extensions)

   **Approach**: Per-layer optional extensions grouped by layout notation
   - Core layout: 36 keys (3x5_3) as the minimal common denominator
   - Each layer can optionally define extension groups (e.g., `extensions.3x5_3_pinky`, `extensions.3x6_3`)
   - Extension names use layout notation matching QMK conventions (rows×cols or variants)
   - Each extension group defines position-based keys (e.g., `outer_pinky_left`, `outer_pinky_right`)
   - Boards reference which extension groups to include during generation
   - All keyboard sizes are defined in one place, making it easy to maintain consistency

   **Why this approach**:
   - 38/42-key boards feel like "36-key plus extras" rather than different layouts
   - Different layers can use extra keys differently (BASE vs NAV might want different outer pinky keys)
   - 38-key has single outer pinky key per side; 42-key has full pinky column (3 keys per side)
   - No wasted definitions on smaller boards
   - Scales to different extension patterns (thumb keys vs pinky columns vs both)
   - Makes conflicts impossible by construction for small additions
   - For large differences (58-key gaming layer), allow pure board-level overrides

   **YAML Schema Example**:
   ```yaml
   layers:
     BASE:
       core:
         # Left hand (3x5)
         - [Q,              W,              F,              P,              B]
         - [hrm:LGUI:A,     hrm:LALT:R,     hrm:LCTL:S,     hrm:LSFT:T,     G]
         - [Z,              X,              C,              D,              V]
         # Right hand (3x5)
         - [J,              L,              U,              Y,              SCLN]
         - [M,              hrm:RSFT:N,     hrm:RCTL:E,     hrm:RALT:I,     hrm:RGUI:O]
         - [K,              H,              COMM,           DOT,            SLSH]
         # Thumbs (3+3)
         - [lt:MEDIA:ESC,   lt:NAV:SPC,     lt:MOUSE:TAB]
         - [lt:SYM:RET,     lt:NUM:BSPC,    lt:FUN:DEL]

       extensions:
         3x5_3_pinky:  # 38-key: 3x5_3 + 1 outer pinky key per side
           outer_pinky_left: TAB
           outer_pinky_right: QUOT
         3x6_3:  # 42-key: 3x6 + 3 thumbs (full pinky column)
           outer_pinky_left: [TAB, GRV, CAPS]
           outer_pinky_right: [QUOT, BSLS, ENT]

     NAV:
       core:
         # Left hand (3x5)
         - [NONE,        NONE,        NONE,        NONE,        NONE]
         - [LGUI,        LALT,        LCTL,        LSFT,        NONE]
         - [NONE,        NONE,        NONE,        NONE,        NONE]
         # Right hand (3x5)
         - [U_RDO,       U_PST,       U_CPY,       U_CUT,       U_UND]
         - [CAPS,        LEFT,        DOWN,        UP,          RGHT]
         - [INS,         HOME,        PGDN,        PGUP,        END]
         # Thumbs (3+3)
         - [NONE,        NONE,        NONE]
         - [RET,         BSPC,        DEL]

       extensions:
         3x5_3_pinky:  # 38-key: single outer pinky key
           outer_pinky_left: NONE
           outer_pinky_right: HOME
         3x6_3:  # 42-key: full pinky column
           outer_pinky_left: [NONE, NONE, NONE]
           outer_pinky_right: [HOME, PGDN, END]
   ```

   **Supported configurations**:
   - 36-key (3x5_3): Use only `core` (no extensions)
   - 38-key (3x5_3_pinky): Use `core` + `extensions.3x5_3_pinky` (1 outer pinky key per side)
   - 42-key (3x6_3): Use `core` + `extensions.3x6_3` (full 3-key pinky column per side)
   - 58-key gaming: Board-level override with complete custom layout

**Open Questions**:

## Clarifications

### Session 2025-11-14

- Q: How should the system handle complex keybindings like mod-tap or layer-tap keys when one firmware doesn't support a specific modifier or layer behavior? → A: Fail generation entirely when any component of a complex keybinding is incompatible (strict mode for complex keybindings only; simple firmware-specific keys like Bluetooth are silently filtered)
- Q: What happens to the existing ZMK repository after migration to the monorepo? → A: User will handle it
- Q: What file format should be used for firmware-specific settings (tap-hold timings, OLED, encoders) in qmk/config/ and zmk/config/? → A: Keep native firmware config files (QMK's config.h/rules.mk, ZMK's .conf/.dtsi)
- Q: How should behavior syntax (homerow mods, layer-tap) be represented in the unified YAML config given QMK and ZMK use different syntax? → A: Define firmware-agnostic aliases (e.g., `hrm:`, `lt:`) that generator translates to both syntaxes
- Q: Where does the mapping between physical boards and their extension requirements live (e.g., "Lily58 uses 3x6_3 extensions")? → A: Central board inventory file (e.g., `config/boards.yaml`) listing all boards with their extension requirements

**Review Status**: User has reviewed and refined User Stories 1-4. User Story 5 and remaining sections pending review.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single-Source Keymap Updates (Priority: P1)

As a keyboard enthusiast maintaining multiple firmware configurations, I want to update my keymap definition in one place and have both QMK and ZMK keymaps automatically generated, so that I don't have to manually synchronize changes across two repositories.

**Why this priority**: This is the core value proposition - eliminating manual duplication is the primary goal. Without this, the feature provides no value.

**Independent Test**: Can be fully tested by modifying a single keymap source file (e.g., changing a key binding), running the code generation, and verifying that both QMK and ZMK keymaps reflect the change correctly.

**Acceptance Scenarios**:

1. **Given** I have a unified keymap configuration with a 3x5_3 layout, **When** I change a key binding in the source configuration, **Then** both QMK and ZMK generated keymaps reflect this change
2. **Given** I have multiple keyboards defined (different boards, same core layout), **When** I update a layer definition, **Then** all keyboards' keymaps are regenerated with the updated layer
3. **Given** I have made changes to the source keymap, **When** I run the code generation command, **Then** the generation completes without errors and produces valid QMK and ZMK keymap files

---

### User Story 2 - Firmware-Specific Feature Handling (Priority: P2)

As a user working with both QMK and ZMK firmwares, I want to define a superset keymap configuration that includes all possible keybindings (both QMK-specific and ZMK-specific features), with the system automatically filtering out unsupported keybindings for each firmware during generation, so that I can maintain one comprehensive source of truth that works for both firmwares.

**Why this priority**: This enables the unified keymap to handle real-world differences between firmwares bidirectionally. Without it, users would be forced to maintain separate configurations or sacrifice firmware-specific features. The superset approach future-proofs the system for any firmware-specific capabilities.

**Independent Test**: Can be tested by adding firmware-specific keybindings (e.g., ZMK Bluetooth keys, QMK-specific combo keys) to the unified keymap, generating both firmwares, and verifying that each firmware output only includes its supported features with unsupported features replaced by appropriate fallbacks.

**Acceptance Scenarios**:

1. **Given** I define a ZMK-specific keybinding (e.g., Bluetooth control) in my unified keymap, **When** I generate QMK configuration, **Then** the key is replaced with a no-op or alternative keybinding
2. **Given** I define a ZMK-specific keybinding in my unified keymap, **When** I generate ZMK configuration, **Then** the key appears with proper ZMK syntax
3. **Given** I define a QMK-specific keybinding (e.g., QMK combo) in my unified keymap, **When** I generate ZMK configuration, **Then** the key is replaced with a no-op or alternative keybinding
4. **Given** I define a QMK-specific keybinding in my unified keymap, **When** I generate QMK configuration, **Then** the key appears with proper QMK syntax
5. **Given** I add a bootloader key to my unified keymap, **When** I generate both QMK and ZMK configurations, **Then** both include the appropriate reset/bootloader key for their respective firmware

---

### User Story 3 - Board-Specific Layout Extensions (Priority: P2)

As a user with keyboards of different sizes (36-key, 58-key), I want to define board-specific additional keys in the unified configuration layer (not in the QMK/ZMK directories), and have the code generator compile these extensions down into the appropriate board's generated keymap, so that larger keyboards can utilize their extra keys while keeping all configuration centralized and preventing manual edits from being overwritten.

**Why this priority**: Enables the system to support multiple keyboard sizes while maintaining a consistent core layout and keeping all user configuration at the unified config level. Critical for users with diverse keyboard collections and essential to ensure generated QMK/ZMK files remain completely auto-generated.

**Independent Test**: Can be tested by defining a board-specific extension (e.g., number row for a 58-key board) in the unified configuration layer, running code generation, and verifying that: (1) only that board's generated keymap includes the extra keys, (2) the core layout remains identical across all boards, and (3) the board-specific configuration does NOT exist within the QMK/ZMK directories.

**Acceptance Scenarios**:

1. **Given** I have a 36-key board and a 58-key board configured, **When** I define extra keys for the 58-key board in the unified configuration layer, **Then** only the 58-key board's generated keymap includes these keys
2. **Given** I update the core 3x5_3 layout in the unified configuration, **When** I regenerate keymaps for all boards, **Then** all boards reflect the core layout change while preserving their board-specific extensions
3. **Given** I add a gaming layer with number row for a specific larger board in the unified configuration, **When** I generate its keymap, **Then** the gaming layer appears only in that board's generated QMK/ZMK files
4. **Given** I have defined board-specific extensions in the unified configuration, **When** I examine the generated QMK/ZMK directories, **Then** those directories contain ONLY generated code with no user-editable board-specific configuration files
5. **Given** I regenerate keymaps after modifying board-specific extensions, **When** the generation completes, **Then** my board-specific changes are preserved because they live in the unified config layer, not in generated files

---

### User Story 4 - Repository Initialization and Migration (Priority: P1)

As a user with existing QMK userspace and ZMK repositories, I want to migrate to a unified monorepo structure that contains my configuration and both firmware outputs, with unified GitHub Actions building binaries for all keyboards, so that I can manage everything in one place without losing my existing configurations or build automation.

**Why this priority**: This is a prerequisite for adopting the system. Without a clear migration path and repository structure, users cannot begin using the feature.

**Repository Structure** (Monorepo Approach):

```
keyboard-config/                    # Root (renamed from qmk_userspace)
├── config/                         # Unified keymap configuration
│   ├── keymap.yaml                # Core keymap definition with layers and extensions
│   ├── boards.yaml                # Board inventory with extension requirements
│   └── layers/                    # Layer definitions (optional organization)
├── qmk/                           # QMK-specific
│   ├── keymaps/                   # Generated QMK keymaps (auto-generated)
│   └── config/                    # QMK-specific settings (tap-hold, OLED, encoders)
├── zmk/                           # ZMK-specific
│   ├── keymaps/                   # Generated ZMK keymaps (auto-generated)
│   └── config/                    # ZMK-specific settings (behaviors, etc.)
├── scripts/                       # Code generation scripts
│   └── generate.sh                # Main codegen entry point
└── .github/workflows/             # Unified CI/CD for all firmwares
    └── build-all.yml              # Build QMK + ZMK binaries
```

**Design Rationale**:
- **Everything in one repo**: Simpler mental model, single clone, no submodule complexity
- **Unified CI/CD**: Single GitHub Actions workflow builds all firmwares
- **Clear separation**: `config/` for user edits, `qmk/keymaps/` and `zmk/keymaps/` are generated
- **Firmware-specific settings**: `qmk/config/` and `zmk/config/` for non-keymap settings (tap-hold timings, OLED, etc.)

**Upstream Sync Strategy**:
- Add upstream QMK/ZMK as git remotes when needed
- Manually merge/cherry-pick relevant changes into `qmk/` or `zmk/` directories
- This is infrequent and gives full control over what changes are adopted

**Independent Test**: Can be tested by running a migration command that transforms the current QMK userspace repo into the chosen structure, migrates the ZMK config, and verifies that keymap generation and CI/CD work correctly.

**Acceptance Scenarios**:

1. **Given** I have existing QMK userspace and ZMK repositories, **When** I run the migration command, **Then** the repository is restructured with config/, qmk/, zmk/, and scripts/ directories
2. **Given** migration is complete, **When** I generate keymaps, **Then** the output matches my original QMK and ZMK configurations functionally
3. **Given** the unified repository is set up, **When** I push changes, **Then** GitHub Actions builds binaries for all QMK and ZMK keyboards in a single workflow
4. **Given** I need to update from upstream QMK/ZMK, **When** I add upstream remotes and merge selected changes, **Then** the updates integrate without breaking my generated keymaps
5. **Given** I want to build locally, **When** I run the unified build command, **Then** all QMK and ZMK firmware binaries are built successfully

---

### User Story 5 - Easy Board Addition (Priority: P3)

As a user acquiring new keyboards, I want to easily add a new board to my unified configuration by providing minimal information (board identifier, size, firmware type), so that I can quickly get a working keymap without manual file creation.

**Why this priority**: Improves long-term maintainability and user experience. Less critical for initial adoption but important for sustained use.

**Independent Test**: Can be tested by running an "add board" command with board details, and verifying that the necessary configuration structure is created and keymap generation works for the new board.

**Acceptance Scenarios**:

1. **Given** I acquire a new QMK-compatible 36-key keyboard, **When** I run the add-board command with the board identifier, **Then** a board-specific configuration is created using the default 3x5_3 layout
2. **Given** I acquire a new ZMK-compatible keyboard with a different size, **When** I specify the layout size during board addition, **Then** the system creates appropriate configuration with the specified layout
3. **Given** a new board has been added, **When** I run keymap generation, **Then** the new board is included in the build process alongside existing boards

---

### Edge Cases

- **Firmware-incompatible simple keycodes**: When a simple keycode doesn't exist in a firmware (e.g., Bluetooth keys in QMK), the default behavior is to silently drop/replace with no-op (KC_NO in QMK, &none in ZMK). This allows superset configurations where firmware-specific simple keys are automatically filtered during generation.

- **Complex keybinding incompatibility**: When complex keybindings (mod-tap, layer-tap, combos) contain firmware-incompatible components, generation must fail entirely with a clear error message. For example, if a mod-tap uses a ZMK-only behavior, QMK generation fails rather than silently degrading to a simpler keybinding. This strict validation ensures explicit user control over complex behavior fallbacks and prevents unexpected behavior changes.

- **Feature detection**: No explicit registry needed - the code generator distinguishes between simple keycodes (which can be silently filtered) and complex keybindings (which require strict validation). Simple firmware-specific keys are detected and filtered gracefully; complex keybinding incompatibilities halt generation with clear error messages.

- **Filtered key fallback**: Simple firmware-specific keys (e.g., Bluetooth controls) automatically fall back to no-op (KC_NO in QMK, &none in ZMK). Complex keybindings have no automatic fallback - users must explicitly provide firmware-compatible alternatives or remove incompatible complex keybindings.

- **Core layout extensions design**: For small additions (36→38→42 key), the extension system should make conflicts impossible by construction (e.g., defining "outer pinky column" as a separate namespace). For larger differences (58-key gaming layer), allow pure overrides at the board level.

- **Accidental edits to generated files**: Add clear header comments to generated files indicating they are auto-generated. Beyond documentation, there's no technical prevention needed for single-user repo.

- **Firmware-specific behaviors**: Settings like tap-hold timings, homerow mod parameters (e.g., ZMK `&hrm` behavior), OLED, encoders remain manually defined in `qmk/config/` and `zmk/config/` using native firmware config files (QMK's config.h/rules.mk, ZMK's .conf/.dtsi). The unified config uses firmware-agnostic aliases (e.g., `hrm:LALT:I`, `lt:NAV:SPC`) which the code generator translates to firmware-specific syntax (ZMK's `&hrm LALT I` or QMK's `LALT_T(KC_I)`). Behavior definitions themselves remain firmware-specific and out of scope for unified management.

- **Upstream syntax breaking changes**: Manual fix required when QMK or ZMK introduce breaking changes. Code generator needs to be updated to match new syntax. No automatic handling.

- **New firmware features**: When upstream introduces new features (e.g., new ZMK behavior), user can start using them in unified config. The code generator passes through unknown keycodes/behaviors, allowing adoption without updating the generator (assuming syntax compatibility).

- **Existing custom code migration**: Case-by-case basis. Recommended approach: backup everything, establish working unified config with basic keymaps, then selectively reintroduce custom code (OLED, encoders, etc.) into `qmk/config/` and `zmk/config/` directories.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST maintain a single source of truth for core keymap layout that generates both QMK and ZMK keymaps
- **FR-002**: System MUST support a core 3x5_3 (36-key) layout definition that is consistent across all keyboards
- **FR-003**: System MUST allow the core layout size to be configurable (not hardcoded to 3x5_3)
- **FR-004**: System MUST generate valid QMK C/header files from the unified keymap configuration
- **FR-005**: System MUST generate valid ZMK keymap files from the unified keymap configuration
- **FR-006**: System MUST support a superset keymap configuration that includes both QMK-specific and ZMK-specific keybindings
- **FR-007**: System MUST bidirectionally filter simple firmware-incompatible keycodes during generation (strip ZMK-only simple keys from QMK output and QMK-only simple keys from ZMK output), while strictly validating complex keybindings (mod-tap, layer-tap, combos) and failing generation with clear error messages when complex keybindings contain firmware-incompatible components
- **FR-008**: System MUST support board-specific layout extensions (additional keys beyond the core layout)
- **FR-009**: Board-specific layout extensions MUST be defined in the unified configuration layer and compiled down during generation; they MUST NOT exist in the QMK/ZMK directories
- **FR-010**: Generated QMK and ZMK keymap files MUST be completely auto-generated with no user-editable configuration (all user configuration lives in the unified config layer)
- **FR-011**: System MUST keep firmware-specific settings (homerow mod timings, tap-hold parameters, OLED, encoders) separate from keymap configuration
- **FR-012**: System MUST support multiple keyboards of different sizes using the same core layout
- **FR-013**: System MUST provide a command or script to generate all configured keymaps (QMK and ZMK) in a single operation
- **FR-014**: System MUST validate keymap configuration before generation and report errors clearly
- **FR-015**: System MUST preserve bootloader key bindings across both firmwares with firmware-appropriate syntax
- **FR-016**: System MUST provide an initialization process to set up the unified repository structure
- **FR-017**: System MUST support easy addition of new keyboards with minimal configuration via central board inventory
- **FR-022**: System MUST maintain a central board inventory file (`config/boards.yaml`) that maps physical keyboards to their extension requirements and firmware types
- **FR-018**: System MUST support layer definitions including modifiers, layer-tap keys, and custom keycodes using firmware-agnostic aliases
- **FR-019**: System MUST translate firmware-agnostic aliases (e.g., `hrm:`, `lt:`) to firmware-specific syntax during generation (ZMK's `&hrm`/`&lt` behaviors, QMK's `*_T()` macros)
- **FR-020**: System MUST maintain consistency of modifier keys (Cmd, Alt, Ctrl, Shift) and layer-tap behaviors across firmwares through translation layer
- **FR-021**: Generated keymaps MUST be completely reproducible (re-running generation produces identical output)
- **FR-023**: System MUST generate visual keymap documentation (SVG/PNG/image diagrams) for all generated keymaps, integrated into the generation pipeline
- **FR-024**: System MUST automatically generate visual diagrams after keymap generation (may use keymap-drawer, custom generator, or other suitable visualization tools)
- **FR-025**: Generated visual diagrams MUST be placed in docs/keymaps/ directory
- **FR-026**: Visualization generation MUST be part of the main generate.sh pipeline, not a separate manual step
- **FR-027**: System MUST only include firmware-agnostic settings in unified config (config/); firmware-specific settings (feature flags, timings, hardware config) MUST remain in firmware-specific directories (qmk/config/, zmk/config/)
- **FR-028**: Unified config abstraction MUST be limited to concepts that are reasonably generalizable between QMK and ZMK (keymaps, layers, basic keycodes, layout sizes)
- **FR-029**: Board configuration MUST be minimal and non-redundant; boards specify layout_size, and the system automatically infers which extensions to apply based on layout_size (e.g., layout_size "3x6_3" → apply extensions["3x6_3"])

### Design Principles

**Unified Config Scope (What Goes in `config/`)**:
Only include settings that are **portable and generalizable** between QMK and ZMK:
- ✅ Keymap layouts (translates between firmwares)
- ✅ Layer definitions (conceptually identical)
- ✅ Core keycodes and behaviors (translatable via aliases like `hrm:`, `lt:`)
- ✅ Board inventory (which boards exist)
- ✅ Layout sizes and extensions (3x5_3, 3x6_3, etc.)

**Firmware-Specific Config Scope (What Stays in `qmk/config/` and `zmk/config/`)**:
Keep settings that are **firmware-specific and non-portable**:
- ❌ Feature flags (BOOTMAGIC_ENABLE, MOUSEKEY_ENABLE, CONFIG_ZMK_MOUSE, etc.)
- ❌ Behavior timings (tapping terms, hold delays)
- ❌ Hardware-specific config (OLED settings, RGB config, encoders)
- ❌ Firmware-specific behaviors (QMK combos, ZMK macros with different syntax)
- ❌ Build system settings (compiler flags, optimization levels)

**Rationale**: Attempting to abstract firmware-specific features creates a "shadow reimplementation" that adds complexity without portability benefits. Keep the abstraction layer focused on what truly translates between firmwares (keymaps), and let users manage firmware-specific settings directly in their native formats.

### Key Entities

- **Unified Keymap Configuration**: The single-source-of-truth definition of the keyboard layout, including layers, key positions, and bindings. Contains the core layout (e.g., 3x5_3) that applies to all keyboards.

- **Board Configuration**: Per-keyboard settings defined in the central board inventory file (`config/boards.yaml`) that specify the physical characteristics (keyboard identifier, firmware type, layout size) and which extension groups from the unified keymap each board uses. The board inventory maps physical keyboards to their extension requirements (e.g., "Lily58 uses 3x6_3 extensions"). Firmware-specific settings (feature flags, OLED config, etc.) are NOT included in boards.yaml and remain in firmware-specific config directories (qmk/config/, zmk/config/).

- **Firmware Profile**: Defines firmware-specific capabilities and limitations (QMK vs ZMK feature sets) to enable proper keycode translation and filtering during generation.

- **Layer Definition**: A named collection of key bindings (e.g., BASE, NAV, NUM, SYM) that applies across all keyboards. Includes modifiers, tap-hold keys, and layer activation keys.

- **Keycode Mapping**: Translation rules between unified keymap representation and firmware-specific keycode syntax (e.g., how a "Bluetooth Next Profile" key maps to ZMK syntax and is stripped from QMK).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can update a key binding in the unified configuration and successfully generate both QMK and ZMK keymaps in under 1 minute
- **SC-002**: Generated keymaps are functionally identical to hand-written configurations (verified through compilation and flashing to physical keyboards)
- **SC-003**: User can add a new keyboard to the system in under 5 minutes with a single command
- **SC-004**: Firmware-specific features (both QMK-specific and ZMK-specific) are correctly filtered and appear only in their supported firmware outputs 100% of the time
- **SC-005**: Board-specific customizations persist across regeneration without manual file edits being overwritten
- **SC-006**: System successfully handles at least 5 different keyboard configurations with varying sizes (36-key to 58-key) from a single source
- **SC-007**: User reports 90% reduction in time spent synchronizing keymap changes across firmwares
- **SC-008**: Generated keymaps compile without errors for both QMK and ZMK 100% of the time (assuming valid input configuration)

## Assumptions *(optional - include if making significant assumptions)*

- The user has basic familiarity with their existing QMK and ZMK repository structures
- The user is comfortable running command-line tools for keymap generation and repository migration
- The user is comfortable editing YAML files
- The unified keymap will be defined in `config/keymap.yaml` using a structured YAML schema
- Board inventory and extension mappings will be stored in `config/boards.yaml` as a central registry of all keyboards
- Generated files will include clear warnings/markers indicating they are auto-generated and should not be manually edited
- The system will use a **monorepo structure** with `config/` (unified keymap), `qmk/` (QMK-specific), and `zmk/` (ZMK-specific) directories
- Firmware-specific settings (tap-hold timings, OLED configuration, encoders) will remain in `qmk/config/` and `zmk/config/` and are out of scope for unified management
- The user's ZMK repository contents will be migrated into the `zmk/` directory of the monorepo during initialization
- The current QMK userspace repository can be renamed/restructured to become the unified monorepo

## Out of Scope *(optional - include if needed to clarify boundaries)*

- Unifying firmware-specific behavior settings (homerow mod timings, debounce, polling rates) - these remain firmware-specific
- Automatic upstream synchronization with QMK/ZMK repositories - user manually manages upstream updates
- Migration of git history from existing repositories - only current configuration state is migrated
- Support for firmwares other than QMK and ZMK
- Complex macro definitions or behavior scripts that differ significantly between firmwares - simple macros supported, complex ones remain firmware-specific
- Automated testing of generated keymaps on actual hardware - user responsible for flashing and testing
