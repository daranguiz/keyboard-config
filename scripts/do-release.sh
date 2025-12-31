#!/bin/bash
set -e

# Release script for keyboard firmware
# Usage: ./scripts/do-release.sh <tag_name> <release_title> [release_notes]
#
# Release notes can be provided as a string, or omitted to auto-generate from commits:
#   Direct string: ./do-release.sh tag title "notes text here"
#   Auto-generate: ./do-release.sh tag title

TAG_NAME="$1"
RELEASE_TITLE="$2"
RELEASE_NOTES_TEXT="$3"

if [ -z "$TAG_NAME" ] || [ -z "$RELEASE_TITLE" ]; then
  echo "Usage: $0 <tag_name> <release_title> [release_notes]"
  echo ""
  echo "Examples:"
  echo "  $0 Night-2025-12-28 \"Night\" \"Release notes here\""
  echo "  $0 Night-2025-12-28 \"Night\"  # auto-generates notes"
  exit 1
fi

# Handle release notes input
RELEASE_NOTES_FILE=""
CLEANUP_NOTES_FILE=false

if [ -n "$RELEASE_NOTES_TEXT" ]; then
  # Direct string provided - write to temp file
  RELEASE_NOTES_FILE=".release-notes-tmp-$$"
  CLEANUP_NOTES_FILE=true
  echo "$RELEASE_NOTES_TEXT" > "$RELEASE_NOTES_FILE"
fi

ZIP_NAME="keyboard-firmware-${TAG_NAME}.zip"

echo "========================================"
echo "Creating Keyboard Firmware Release"
echo "========================================"
echo "Tag:     ${TAG_NAME}"
echo "Title:   ${RELEASE_TITLE}"
echo "Zip:     ${ZIP_NAME}"
echo "========================================"
echo ""

# Check if out/ directory exists
if [ ! -d "out" ]; then
  echo "❌ Error: out/ directory not found. Run ./build_all.sh first."
  exit 1
fi

# Check if out/ has content
if [ -z "$(ls -A out)" ]; then
  echo "❌ Error: out/ directory is empty. Run ./build_all.sh first."
  exit 1
fi

# Create tag
echo "📝 Creating git tag: ${TAG_NAME}..."
if git tag -a "${TAG_NAME}" -m "Release: ${RELEASE_TITLE}"; then
  echo "✅ Tag created successfully"
else
  echo "❌ Failed to create tag (it may already exist)"
  exit 1
fi

# Push tag
echo ""
echo "⬆️  Pushing tag to GitHub..."
if git push origin "${TAG_NAME}"; then
  echo "✅ Tag pushed successfully"
else
  echo "❌ Failed to push tag"
  echo "💡 You may need to delete the local tag: git tag -d ${TAG_NAME}"
  exit 1
fi

# Create zip
echo ""
echo "📦 Creating firmware archive..."
if (cd out && zip -r "../${ZIP_NAME}" . && cd ..); then
  echo "✅ Archive created: ${ZIP_NAME}"
  echo "   Size: $(du -h "${ZIP_NAME}" | cut -f1)"
else
  echo "❌ Failed to create zip archive"
  exit 1
fi

# Create GitHub release
echo ""
echo "🚀 Creating GitHub release..."
if [ -n "$RELEASE_NOTES_FILE" ] && [ -f "$RELEASE_NOTES_FILE" ]; then
  # Use release notes file
  gh release create "${TAG_NAME}" \
    --title "${RELEASE_TITLE}" \
    --notes-file "${RELEASE_NOTES_FILE}" \
    "${ZIP_NAME}"
else
  # Auto-generate release notes
  gh release create "${TAG_NAME}" \
    --title "${RELEASE_TITLE}" \
    --generate-notes \
    "${ZIP_NAME}"
fi

if [ $? -eq 0 ]; then
  echo "✅ Release created successfully"
else
  echo "❌ Failed to create GitHub release"
  exit 1
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
rm "${ZIP_NAME}"
if [ "$CLEANUP_NOTES_FILE" = true ] && [ -f "$RELEASE_NOTES_FILE" ]; then
  rm "$RELEASE_NOTES_FILE"
fi
echo "✅ Cleanup complete"

# Get the release URL
REPO_URL=$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
RELEASE_URL="https://github.com/${REPO_URL}/releases/tag/${TAG_NAME}"

echo ""
echo "========================================"
echo "✅ Release Created Successfully!"
echo "========================================"
echo "🏷️  Tag:   ${TAG_NAME}"
echo "📦 Title: ${RELEASE_TITLE}"
echo "🔗 URL:   ${RELEASE_URL}"
echo "========================================"
