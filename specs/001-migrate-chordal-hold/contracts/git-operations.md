# Contract: Git Operations

**Feature**: 001-migrate-chordal-hold
**Type**: Command-line operations contract
**Date**: 2025-11-07

## Overview

This contract defines the git operations required to consolidate branches and establish the clean master → personal branch structure.

## Operations

### OP-1: Identify Changes on lily58/miryoku-bilateral-combinations Branch

**Command**:
```bash
git checkout lily58/miryoku-bilateral-combinations
git log --oneline --decorate
git diff master...lily58/miryoku-bilateral-combinations
```

**Purpose**: Identify all unique changes on the lily58 branch not present on master

**Inputs**:
- Branch: lily58/miryoku-bilateral-combinations

**Outputs**:
- List of commits unique to lily58 branch
- Diff of all changes vs master
- Identification of which files changed

**Success Criteria**:
- Can view full commit history of lily58 branch
- Can see complete diff vs master
- Understand which changes need to be preserved

---

### OP-2: Identify Changes on master from Commit e3794835136f539e166cf9f7b3dcee7b47d55148 Onward

**Command**:
```bash
git checkout master
git log --oneline e3794835136f539e166cf9f7b3dcee7b47d55148..HEAD
git diff e3794835136f539e166cf9f7b3dcee7b47d55148..HEAD
```

**Purpose**: Identify changes on master from the specified commit onward that need preservation

**Inputs**:
- Branch: master
- Starting commit: e3794835136f539e166cf9f7b3dcee7b47d55148

**Outputs**:
- List of commits from e379483513 onward
- Diff of all changes in that range
- Files modified since that commit

**Success Criteria**:
- Can view commits from specified point to HEAD
- Understand which master changes to preserve

---

### OP-3: Add Upstream Remote (if not exists)

**Command**:
```bash
git remote -v
# If upstream not present:
git remote add upstream https://github.com/qmk/qmk_firmware.git
git fetch upstream
```

**Purpose**: Ensure upstream QMK repository is configured as a remote

**Inputs**: None

**Outputs**:
- Upstream remote configured
- Latest upstream commits fetched

**Success Criteria**:
- `git remote -v` shows upstream pointing to qmk/qmk_firmware
- `git fetch upstream` succeeds

---

### OP-4: Create Backup Branch of Current master

**Command**:
```bash
git branch master-backup-before-reset
```

**Purpose**: Create safety backup before resetting master

**Inputs**:
- Current master branch

**Outputs**:
- New branch: master-backup-before-reset

**Success Criteria**:
- Branch created successfully
- Points to same commit as current master

---

### OP-5: Reset master to Latest Upstream

**Command**:
```bash
git checkout master
git fetch upstream
git reset --hard upstream/master
```

**Purpose**: Make master track upstream QMK cleanly

**Inputs**:
- Upstream remote configured and fetched

**Outputs**:
- master branch reset to upstream/master
- All personal changes removed from master

**Success Criteria**:
- `git log master..upstream/master` shows no commits (branches in sync)
- `git status` shows clean working directory
- master now matches upstream exactly

**WARNING**: This is a destructive operation. Backup branch must exist first (OP-4).

---

### OP-6: Create personal Branch from master

**Command**:
```bash
git checkout master
git checkout -b personal
```

**Purpose**: Create new personal branch based on clean upstream master

**Inputs**:
- master branch reset to upstream (from OP-5)

**Outputs**:
- New branch: personal
- Based on upstream/master

**Success Criteria**:
- personal branch created
- Currently on personal branch
- Clean working directory

---

### OP-7: Apply Consolidated Changes to personal Branch

**Command** (manual process):
```bash
git checkout personal

# Manually recreate changes:
# 1. Copy keymap files from lily58 or master-backup-before-reset
# 2. Apply bilateral combinations patch removal
# 3. Apply chordal hold migration
# 4. Create KEYBOARDS.md
# 5. Update any other personal files

git add <files>
git commit -m "Consolidated personal changes: keymap configs, chordal hold migration

- Migrated boardsource/lulu/keymaps/dario to chordal hold
- Created KEYBOARDS.md inventory
- [Other changes from lily58 and master branches]

Replaces bilateral combinations patch with native chordal hold feature.
"
```

**Purpose**: Apply all consolidated customizations to personal branch as single commit

**Inputs**:
- Changes from lily58 branch (identified in OP-1)
- Changes from master e379483513+ (identified in OP-2)
- Chordal hold migration changes
- KEYBOARDS.md creation

**Outputs**:
- Single consolidated commit on personal branch
- All personal customizations present

**Success Criteria**:
- All unique changes from source branches preserved
- Chordal hold migration complete
- Builds succeed
- Working directory clean after commit

---

### OP-8: Merge Feature Branch to personal

**Command**:
```bash
git checkout personal
git merge 001-migrate-chordal-hold --no-ff -m "Merge branch consolidation and chordal hold migration"
```

**Purpose**: Merge this feature work into personal branch

**Inputs**:
- personal branch with consolidated changes (from OP-7)
- 001-migrate-chordal-hold branch with migration work

**Outputs**:
- Feature branch merged into personal
- All work consolidated

**Success Criteria**:
- Merge succeeds without conflicts
- Builds still succeed
- personal branch contains all work

---

## Operation Sequence

**Phase 1: Discovery**
1. OP-1: Identify lily58 branch changes
2. OP-2: Identify master changes from e379483513+

**Phase 2: Backup and Reset**
3. OP-3: Add/verify upstream remote
4. OP-4: Create backup branch
5. OP-5: Reset master to upstream (DESTRUCTIVE)

**Phase 3: Consolidation**
6. OP-6: Create personal branch
7. OP-7: Apply consolidated changes

**Phase 4: Completion**
8. OP-8: Merge feature branch to personal

## Rollback Procedures

If something goes wrong:

**If reset goes wrong** (after OP-5):
```bash
git checkout master
git reset --hard master-backup-before-reset
# Restores master to pre-reset state
```

**If personal branch work goes wrong** (after OP-6 or OP-7):
```bash
git branch -D personal
# Delete personal branch, start over from OP-6
```

**If merge goes wrong** (after OP-8):
```bash
git checkout personal
git reset --hard HEAD~1
# Un-merge the feature branch
```

## Validation

**Final State Validation**:
```bash
# master should track upstream
git checkout master
git log origin/master..upstream/master  # Should be empty or nearly empty

# personal should have customizations on top of master
git checkout personal
git log master..personal  # Should show consolidated commit(s)

# Builds should succeed
make boardsource/lulu/rp2040:dario
```

**Success Criteria**:
- master tracks upstream cleanly
- personal branch builds successfully
- All personal customizations preserved on personal branch
- Old branches preserved as backup
