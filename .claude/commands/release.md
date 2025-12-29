---
description: Create a GitHub release with firmware builds from out/ folder
---

## Purpose

Automate the process of creating a GitHub release for keyboard firmware builds:
1. Build all firmware (QMK + ZMK)
2. Extract current base layout name (e.g., "Night")
3. Generate a git tag with format `{Layout}-YYYY-MM-DD`
4. Generate release notes from recent commits
5. Execute `scripts/do-release.sh` to create and push the release

## User Input

```text
$ARGUMENTS
```

Optional arguments:
- Custom tag name (default: auto-generated from base layout + date)
- Custom release title (default: current base layout name)
- Custom release notes (default: auto-generated from commits)

## Execution Steps

### 1. Pre-flight Checks

Check git status:

```bash
git status --porcelain
```

If there are uncommitted changes, warn the user and ask:
- **Option A**: Show me the changes (run `git status` and `git diff --stat`)
- **Option B**: Continue anyway (create release from current HEAD)
- **Option C**: Abort

Check if `gh` CLI is authenticated:

```bash
gh auth status
```

If not authenticated, provide instructions:
```bash
gh auth login
```

### 2. Build All Firmware

Run the build script to generate all artifacts:

```bash
./build_all.sh
```

Verify that `out/` directory exists and contains build artifacts:
- `out/qmk/` with firmware files
- `out/zmk/` with firmware files
- `out/visualizations/` with diagrams

If build fails, abort and report the error.

### 3. Determine Release Name

Extract the current base layout name from `config/keymap.yaml`:

```bash
grep "^base_layers:" -A 10 config/keymap.yaml | grep "BASE_" | head -1 | sed 's/.*BASE_//' | sed 's/:.*//' | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}'
```

This extracts the layout name and converts it to title case (e.g., "NIGHT" → "Night").

If `$ARGUMENTS` contains a custom release name, use that instead.

Default release title: `{layout_name}` (e.g., "Night")

### 4. Generate Tag Name

Generate tag name with format: `{layout_name}-YYYY-MM-DD`

Example: `Night-2025-12-28`

Check if tag already exists:

```bash
git tag -l "{tag_name}"
```

If tag exists, suggest incrementing:
- `Night-2025-12-28-2`
- `Night-2025-12-28-3`
- etc.

Ask user to confirm or provide custom tag name.

### 5. Generate Release Notes

Auto-generate release notes from commits since last tag:

```bash
# Get the last release tag
LAST_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")

# Get commits since last tag (or all commits if no previous tag)
if [ -z "$LAST_TAG" ]; then
  COMMITS=$(git log --pretty=format:"- %s (%h)" --no-merges HEAD)
else
  COMMITS=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges)
fi

# Count firmware files
QMK_COUNT=$(find out/qmk -type f \( -name "*.hex" -o -name "*.uf2" \) 2>/dev/null | wc -l | tr -d ' ')
ZMK_COUNT=$(find out/zmk -type f -name "*.uf2" 2>/dev/null | wc -l | tr -d ' ')
```

Create `release-notes.md`:

```markdown
# Keyboard Firmware - {release_title}

## What's Changed

${COMMITS}

## Build Artifacts

This release includes firmware for:
- **QMK**: ${QMK_COUNT} keyboard(s)
- **ZMK**: ${ZMK_COUNT} keyboard(s)

Download `keyboard-firmware-{tag_name}.zip` and extract to find firmware files for your keyboard.

## Installation

1. Download `keyboard-firmware-{tag_name}.zip`
2. Extract the zip file
3. Find your keyboard's firmware in `qmk/` or `zmk/` folder
4. Flash to your keyboard using QMK Toolbox or your preferred method

---

**Full Changelog**: https://github.com/{owner}/{repo}/compare/{last_tag}...{tag_name}
```

If user provided custom release notes in `$ARGUMENTS`, use those instead.

### 6. Execute Release Script

Display a summary and ask for user approval:

```
Ready to create release:
├─ Tag:     {tag_name}
├─ Title:   {release_title}
├─ QMK:     {qmk_count} keyboards
└─ ZMK:     {zmk_count} keyboards

This will:
1. Create and push git tag: {tag_name}
2. Create zip: keyboard-firmware-{tag_name}.zip
3. Create GitHub release with zip attached

Proceed? (y/n)
```

If approved, execute the release script:

```bash
bash scripts/do-release.sh "{tag_name}" "{release_title}" release-notes.md
```

The script will:
1. Create the git tag
2. Push the tag to GitHub
3. Create the zip file
4. Create the GitHub release
5. Upload the zip as a release asset
6. Clean up temporary files

### 7. Report Success

After the script completes, display the release URL and summary:

```
✅ Release created successfully!

📦 Release: {release_title}
🏷️  Tag: {tag_name}
🔗 URL: https://github.com/{user}/{repo}/releases/tag/{tag_name}

Build artifacts:
- QMK: {qmk_count} keyboards
- ZMK: {zmk_count} keyboards
- Visualizations: {viz_count} SVG files

Total size: {zip_size}
```

## Error Handling

Handle common failure scenarios:

1. **Build fails**: Report build errors, don't create release
2. **Tag already exists**:
   - Check with `git tag -l {tag_name}`
   - Suggest incrementing tag name or using custom name
   - Offer to delete existing tag if it wasn't pushed
3. **No gh CLI**:
   - Check with `gh --version`
   - Provide installation instructions: `brew install gh` and `gh auth login`
4. **Not authenticated with gh**:
   - Check with `gh auth status`
   - Provide login instructions: `gh auth login`
5. **out/ directory empty**:
   - Verify with `ls -A out/`
   - Remind user to run `./build_all.sh` first
6. **Uncommitted changes**:
   - Show changes with `git status`
   - Ask user to commit first or continue anyway
7. **Script execution fails**:
   - The script has error handling built-in
   - Will report which step failed (tag creation, push, zip, release)
   - Provides recovery instructions (e.g., delete local tag if push failed)

## Prerequisites

This skill requires:
- `gh` CLI installed and authenticated (`gh auth status`)
- Git repository with remote configured
- `out/` directory with build artifacts (run `./build_all.sh` first)
- `scripts/do-release.sh` script in the repository

If any prerequisite is missing, provide clear installation/setup instructions.

## Examples

**Basic usage** (auto-detect layout, auto-generate tag and notes):
```
/release
```

**Custom release title**:
```
/release "Night v2.0"
```

**Custom tag**:
```
/release tag=v2.0.0
```

**Custom tag and title**:
```
/release tag=v2.0.0 "Night - Major Update"
```

**With custom release notes**:
```
/release "Night v2.0" "Major update with new magic key features and improved home row mods"
```

## Notes

- Release naming follows the current base layout (e.g., "Night", "Gallium", "Dusk")
- Tags are date-based by default: `{Layout}-YYYY-MM-DD`
- The entire `out/` folder is zipped, including QMK, ZMK, and visualizations
- Release notes auto-generate from commit messages since last tag
- The `scripts/do-release.sh` script handles all git and GitHub operations
- This skill does NOT commit changes - ensure your changes are committed first
- The script will clean up temporary files (zip and release-notes.md) after completion

## Script Details

The release process uses `scripts/do-release.sh`, which:
- Creates annotated git tag
- Pushes tag to remote
- Creates zip archive from `out/` directory
- Creates GitHub release with auto-generated or custom notes
- Attaches zip file to release
- Cleans up temporary files
- Provides detailed progress output and error handling
