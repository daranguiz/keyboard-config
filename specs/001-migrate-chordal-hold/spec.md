# Feature Specification: QMK Branch Consolidation and Chordal Hold Migration

**Feature Branch**: `001-migrate-chordal-hold`
**Created**: 2025-11-07
**Status**: Draft
**Input**: User description: "FIrst task is to clean up my horrible mess of branches and configs and whatever. I have two branches that I care about: lily58/miryoku-bilateral-combinations and master (specifically, everything including e3794835136f539e166cf9f7b3dcee7b47d55148 and after). Overall, my primary goal after going through this work is to end up with a fork of QMK that is fully up to date with upstream. I'm currently using a patch from manna_harbour called 'bilateral combinations' that manually modifies QMK source directly. That is the main source of merge conflicts. I want to remove that, and I want to switch to use the built-in support that QMK added for this concept earlier this year called 'chordal hold'. Across the two branches I have listed, I want to combine the various changes on those branches onto a single branch (master). For the moment, other than the bilateral combinations thing, I don't necessarily want to make material changes to the keymaps themselves. They may be out of sync with each other, have redundant settings, etc etc, but I want to address that once I get everything cleaned up and onto a single branch with no patches etc."

## Clarifications

### Session 2025-11-07

- Q: What git strategy should be used to consolidate the branches? → A: Manually move over changes as one new commit, no git history preservation needed (note: current master was originally based on lily58 branch)
- Q: After consolidating branches into one commit, what should be the base for syncing with upstream? → A: Reset master to latest upstream, then apply consolidated changes on a new `personal` branch on top (master stays clean for tracking upstream)
- Q: Which keymaps should be migrated to chordal hold? → A: Only personal keymaps actively used on keyboards
- Q: What should happen if a bilateral combination feature has no chordal hold equivalent? → A: Document limitation and accept behavior change
- Q: What should happen to the old branches after successful consolidation? → A: Keep branches around as backup

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remove Bilateral Combinations Patch (Priority: P1)

As a QMK fork maintainer, I need to remove the manually-applied "bilateral combinations" patch from the codebase so that I can eliminate the source of merge conflicts with upstream QMK and use the native chordal hold feature instead.

**Why this priority**: This is the root cause of merge conflicts and blocks staying up to date with upstream. Without removing this patch, the fork cannot sync with upstream cleanly.

**Independent Test**: Can be fully tested by verifying that all bilateral combinations patch modifications have been removed from QMK core files, the fork compiles successfully, and no references to the patch remain in the codebase.

**Acceptance Scenarios**:

1. **Given** the QMK fork contains manual bilateral combinations patches in core files, **When** I identify all modified core files, **Then** I can see a complete list of files that need patch removal
2. **Given** I have identified all patched files, **When** I remove the bilateral combinations modifications, **Then** the core QMK files match upstream versions (for those specific modifications)
3. **Given** the patch has been removed, **When** I compile any existing keymap, **Then** the build system completes without errors related to missing bilateral combinations code

---

### User Story 2 - Migrate to Chordal Hold Feature (Priority: P2)

As a keyboard user, I need my keymaps updated to use QMK's native chordal hold feature instead of the bilateral combinations patch so that I retain the same keyboard functionality without custom patches.

**Why this priority**: This preserves the desired keyboard behavior after removing the patch. Without this migration, keymaps would lose their bilateral combinations functionality.

**Independent Test**: Can be fully tested by configuring chordal hold in keymaps, compiling them, flashing to keyboards, and verifying that bilateral key combinations work identically to the previous patch-based behavior.

**Acceptance Scenarios**:

1. **Given** a keymap previously using bilateral combinations, **When** I enable and configure chordal hold settings, **Then** the keymap configuration includes the appropriate chordal hold parameters
2. **Given** chordal hold is configured, **When** I press bilateral key combinations (e.g., both shift keys simultaneously), **Then** the keyboard behaves identically to the previous bilateral combinations patch
3. **Given** the migration is complete, **When** I compare the before and after keyboard behavior, **Then** all bilateral combination triggers function as expected

---

### User Story 3 - Consolidate Branches into Personal Branch (Priority: P3)

As a QMK fork maintainer, I need to merge changes from lily58/miryoku-bilateral-combinations and recent master commits into a single `personal` branch so that I have one unified branch containing all my customizations without scattered changes across multiple branches.

**Why this priority**: This organizational cleanup enables easier maintenance going forward, but the fork is still functional even if branches remain separate temporarily.

**Independent Test**: Can be fully tested by verifying that all unique changes from both branches exist on the `personal` branch as a single consolidated commit, and no functionality is lost.

**Acceptance Scenarios**:

1. **Given** I have changes on lily58/miryoku-bilateral-combinations and master branches, **When** I identify unique changes on each branch, **Then** I can see a clear list of what needs to be preserved from each branch
2. **Given** I know what changes to preserve, **When** I manually apply changes onto the `personal` branch, **Then** all unique keymap configurations, keyboard definitions, and customizations exist on `personal` in a single new commit
3. **Given** all changes are on the `personal` branch, **When** I verify the consolidated branch, **Then** no functionality from either original branch has been lost

---

### User Story 4 - Sync Fork with Upstream QMK (Priority: P4)

As a QMK fork maintainer, I need my fork to be fully synchronized with the latest upstream QMK repository so that I benefit from bug fixes, new features, and community improvements while maintaining my customizations on a separate `personal` branch.

**Why this priority**: This is the ultimate goal but depends on completing the patch removal and migration first. It delivers maximum long-term value by keeping the fork current.

**Independent Test**: Can be fully tested by resetting master to latest upstream, creating/updating the `personal` branch from master with consolidated changes, compiling all keymaps, and verifying the fork is synchronized with upstream.

**Acceptance Scenarios**:

1. **Given** the bilateral combinations patch has been removed and changes are consolidated, **When** I fetch the latest upstream QMK, **Then** I can reset master to point to latest upstream
2. **Given** master is reset to upstream, **When** I create/update the `personal` branch from master and apply the consolidated customizations, **Then** all unique keymap configurations and customizations are preserved on `personal`
3. **Given** changes are applied on the `personal` branch, **When** I compile all affected keymaps, **Then** all builds succeed
4. **Given** the fork is synchronized, **When** I check the fork status, **Then** master tracks upstream QMK cleanly and `personal` branch contains only custom changes on top of master

---

### Edge Cases

- When a keymap depends on bilateral combinations patch code that doesn't have a direct chordal hold equivalent, document the limitation and accept the behavior change
- How does the system handle keymaps that have diverged significantly between branches (different key assignments, layers, or features)?
- What happens when upstream QMK has made breaking changes to APIs or configuration formats used by the custom keymaps?
- How are build scripts or tooling that reference the bilateral combinations patch updated?
- What happens when commits on lily58/miryoku-bilateral-combinations conflict with commits on master after e3794835136f539e166cf9f7b3dcee7b47d55148?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify all QMK core files modified by the bilateral combinations patch
- **FR-002**: System MUST remove all bilateral combinations patch code from QMK core files
- **FR-003**: System MUST identify personal keymaps actively used that rely on bilateral combinations functionality
- **FR-004**: System MUST configure chordal hold settings in personal keymaps to replicate bilateral combinations behavior where possible; document any limitations where chordal hold cannot replicate patch functionality
- **FR-005**: System MUST identify unique changes on lily58/miryoku-bilateral-combinations branch not present on master
- **FR-006**: System MUST identify commits on master from e3794835136f539e166cf9f7b3dcee7b47d55148 onward
- **FR-007**: System MUST manually apply all unique changes from both branches onto the `personal` branch as a single consolidated commit
- **FR-008**: System MUST maintain existing keymap configurations without unintended modifications beyond chordal hold migration
- **FR-009**: System MUST verify all affected keymaps compile successfully after changes
- **FR-010**: System MUST reset master branch to latest upstream QMK and create `personal` branch from master with consolidated changes on top

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All bilateral combinations patch code is removed from QMK core files (verified by comparing core files to upstream)
- **SC-002**: All personal keymaps compile without errors after patch removal and chordal hold migration
- **SC-003**: Bilateral key combinations on physical keyboards function as closely as possible to previous behavior; any differences are documented (verified by manual testing)
- **SC-004**: All unique changes from lily58/miryoku-bilateral-combinations and master (from e3794835136f539e166cf9f7b3dcee7b47d55148 onward) exist on the `personal` branch
- **SC-005**: Master branch is reset to latest upstream QMK and tracks it cleanly
- **SC-006**: The `personal` branch is created from master with consolidated customizations applied cleanly on top
- **SC-007**: All keyboard builds that previously succeeded continue to succeed after consolidation

## Assumptions

- QMK's chordal hold feature provides equivalent or near-equivalent functionality to the bilateral combinations patch; minor behavior differences are acceptable
- Documentation exists for configuring chordal hold to replicate bilateral combinations behavior
- Keymap files (keymap.c, config.h, rules.mk) may differ between branches but contain the primary customizations to preserve
- The commit e3794835136f539e166cf9f7b3dcee7b47d55148 on master is the starting point for recent work to preserve
- No other branches contain critical changes that need to be preserved
- Standard git conflict resolution approaches are acceptable for resolving any conflicts during branch consolidation
- Upstream QMK repository is at github.com/qmk/qmk_firmware or similar canonical location
- Personal keymaps are identifiable and distinguishable from default/community keymaps

## Dependencies

- Access to both lily58/miryoku-bilateral-combinations and master branches
- QMK build tools and environment functional (make, qmk cli)
- Documentation or knowledge of chordal hold configuration parameters
- Physical keyboards available for testing bilateral combinations functionality
- Git repository with commit history intact

## Out of Scope

- Refactoring or optimizing keymap configurations beyond the chordal hold migration
- Synchronizing keymap settings that have diverged between branches (this is explicitly deferred for later)
- Removing redundant settings or cleaning up keymap inconsistencies (deferred for future work)
- Adding new keyboard features or capabilities beyond restoring bilateral combinations functionality
- Updating to newer QMK features unrelated to chordal hold
- Modifying keyboard hardware definitions or adding support for new keyboards
- Deleting old branches (lily58/miryoku-bilateral-combinations and previous master) - these will be kept as backup
