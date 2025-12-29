#!/bin/bash
# Release discovery script - gathers info for release planning
# Outputs JSON-like summary for easy parsing

set -e

echo "========================================"
echo "Release Discovery"
echo "========================================"
echo ""

# Fetch latest tags from remote
echo "## Fetching tags..."
git fetch --tags origin 2>/dev/null || echo "⚠️  Could not fetch tags"
echo ""

# Git status
echo "## Git Status"
UNCOMMITTED=$(git status --porcelain)
if [ -z "$UNCOMMITTED" ]; then
  echo "✅ Clean working directory"
else
  echo "⚠️  Uncommitted changes:"
  echo "$UNCOMMITTED" | sed 's/^/   /'
fi
echo ""

# GitHub auth
echo "## GitHub CLI"
if gh auth status >/dev/null 2>&1; then
  echo "✅ Authenticated"
else
  echo "❌ Not authenticated - run: gh auth login"
fi
echo ""

# Extract base layout name from keymap.yaml
echo "## Layout Info"
LAYOUT_NAME=$(grep -A 3 "^  BASE_PRIMARY:" config/keymap.yaml 2>/dev/null | grep "display_name" | sed 's/.*display_name: "//' | sed 's/".*//' | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')
if [ -z "$LAYOUT_NAME" ]; then
  LAYOUT_NAME="Release"
fi
echo "Layout: $LAYOUT_NAME"

# Generate tag name
TODAY=$(date +%Y-%m-%d)
TAG_NAME="${LAYOUT_NAME}-${TODAY}"

# Check if tag exists, increment if needed
SUFFIX=""
COUNT=1
while git tag -l "${TAG_NAME}${SUFFIX}" | grep -q .; do
  COUNT=$((COUNT + 1))
  SUFFIX="-${COUNT}"
done
TAG_NAME="${TAG_NAME}${SUFFIX}"
echo "Suggested tag: $TAG_NAME"
echo ""

# Previous tag and commits
echo "## Commits Since Last Release"
LAST_TAG=$(git describe --tags --abbrev=0 HEAD 2>/dev/null || echo "")
if [ -z "$LAST_TAG" ]; then
  echo "No previous tags found"
  COMMITS=$(git log --pretty=format:"- %s (%h)" --no-merges HEAD)
else
  echo "Last tag: $LAST_TAG"
  COMMITS=$(git log ${LAST_TAG}..HEAD --pretty=format:"- %s (%h)" --no-merges)
fi
echo ""
if [ -z "$COMMITS" ]; then
  echo "(no new commits)"
else
  echo "$COMMITS"
fi
echo ""

# Build artifacts
echo "## Build Artifacts"
if [ ! -d "out" ]; then
  echo "❌ out/ directory not found - run ./build_all.sh first"
else
  QMK_COUNT=$(find out/qmk -type f -name "*.uf2" 2>/dev/null | wc -l | tr -d ' ')
  QMK_HEX=$(find out/qmk -type f -name "*.hex" 2>/dev/null | wc -l | tr -d ' ')
  ZMK_COUNT=$(find out/zmk -type f -name "*.uf2" 2>/dev/null | wc -l | tr -d ' ')
  VIZ_COUNT=$(find out/visualizations -type f \( -name "*.svg" -o -name "*.pdf" \) 2>/dev/null | wc -l | tr -d ' ')
  KEYLAYOUT_COUNT=$(find out/keylayout -type f -name "*.keylayout" 2>/dev/null | wc -l | tr -d ' ')

  echo "QMK firmware:    $QMK_COUNT .uf2, $QMK_HEX .hex"
  echo "ZMK firmware:    $ZMK_COUNT .uf2"
  echo "Visualizations:  $VIZ_COUNT files"
  echo "Keylayouts:      $KEYLAYOUT_COUNT files"
fi
echo ""

# Summary for copy/paste
echo "========================================"
echo "Ready to release:"
echo "========================================"
echo "Tag:   $TAG_NAME"
echo "Title: $LAYOUT_NAME"
echo ""
echo "Run: ./scripts/do-release.sh \"$TAG_NAME\" \"$LAYOUT_NAME\""
echo "========================================"
