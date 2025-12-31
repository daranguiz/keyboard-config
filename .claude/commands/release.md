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

### 1. Run Discovery

Run the discovery script to gather all release information:

```bash
./scripts/release-info.sh
```

This script:
- Fetches latest tags from remote
- Checks git status (uncommitted changes)
- Verifies GitHub CLI authentication
- Extracts layout name from keymap.yaml
- Generates suggested tag name (handles duplicates)
- Lists commits since last release
- Counts build artifacts

If there are issues (uncommitted changes, not authenticated, missing artifacts), address them before proceeding.

### 2. Verify Build Artifacts

The discovery script shows artifact counts. If `out/` is missing or empty, run:

```bash
./build_all.sh
```

### 3. Confirm Release Details

From the discovery output, note:
- **Suggested tag**: e.g., `Night-2025-12-28` or `Night-2025-12-28-2` if tag exists
- **Layout name**: e.g., "Night"
- **Commits**: Changes since last release
- **Artifacts**: QMK count, ZMK count, visualizations, keylayouts

### 4. Generate Release Notes

Write release notes based on the commits since the last tag. The discovery script (`scripts/release-info.sh`) shows:
- Commits since last release
- Build artifact counts (QMK, ZMK, visualizations, keylayouts)

**Guidelines for writing release notes:**

1. **Summarize the changes** - Don't just list commit messages. Write a brief, human-readable summary of what changed and why it matters.

2. **Group related changes** - If multiple commits relate to the same feature, group them together.

3. **Highlight user-facing changes** - Focus on what users will notice: new combos, layout changes, bug fixes, new keyboards supported.

4. **Keep it concise** - 2-5 sentences is usually enough. Users can check the commit log for details.

5. **Include build info** - Mention how many keyboards are included (from discovery output).

**Example release notes:**

```
Fixed forward slash position in Nightlight layout.

Includes firmware for 4 QMK keyboards and 4 ZMK keyboards, plus keylayout files for macOS.
```

**IMPORTANT**: Release notes should be prepared as a string variable that will be passed directly to the release script (not written to a file). Multi-line notes are supported.

### 5. Execute Release Script

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

If approved, execute the release script with release notes as a direct string argument:

```bash
bash scripts/do-release.sh "{tag_name}" "{release_title}" "Your release notes here.

Can include multiple lines.

Includes firmware for X QMK keyboards and Y ZMK keyboards."
```

Or omit the third argument to auto-generate notes from commits:

```bash
bash scripts/do-release.sh "{tag_name}" "{release_title}"
```

The script will:
1. Create the git tag
2. Push the tag to GitHub
3. Create the zip file
4. Create the GitHub release
5. Upload the zip as a release asset
6. Clean up temporary files (including any temp files created for release notes)

### 6. Report Success

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
- Release notes can be provided as a direct string argument or auto-generated from commits
- Multi-line release notes are fully supported - just pass them as a quoted string
- The `scripts/do-release.sh` script handles all git and GitHub operations
- This skill does NOT commit changes - ensure your changes are committed first
- The script automatically cleans up temporary files after completion

## Script Details

The release process uses `scripts/do-release.sh`, which:
- Creates annotated git tag
- Pushes tag to remote
- Creates zip archive from `out/` directory
- Creates GitHub release with auto-generated or custom notes
- Attaches zip file to release
- Cleans up temporary files
- Provides detailed progress output and error handling
