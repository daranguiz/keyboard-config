#!/bin/bash
set -e

echo "================================================"
echo "Building All Keyboard Firmware"
echo "================================================"
echo ""

# Get repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$REPO_ROOT/out"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Prefer Python 3.11 (PyYAML is installed there) but fall back to python3
if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN="python3.11"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo -e "${YELLOW}✗ Python 3 is required but not found${NC}"
    exit 1
fi
echo "Using Python interpreter: $PYTHON_BIN"

# Clean and create output directory
echo -e "${BLUE}Preparing output directory...${NC}"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/qmk"
mkdir -p "$OUTPUT_DIR/zmk"
mkdir -p "$OUTPUT_DIR/visualizations"
mkdir -p "$OUTPUT_DIR/keylayout"
echo -e "${GREEN}✓ Output directory ready: $OUTPUT_DIR${NC}"
echo ""

# Track build results
KEYGEN_SUCCESS=false
QMK_SUCCESS=false
ZMK_SUCCESS=false

# Generate keymaps first (runs once for both QMK and ZMK)
echo "================================================"
echo "Phase 0: Generating Keymaps"
echo "================================================"
echo ""

echo -e "${BLUE}Running keymap generator...${NC}"
if "$PYTHON_BIN" "$REPO_ROOT/scripts/generate.py"; then
    echo -e "${GREEN}✓ Keymap generation successful${NC}"
    echo ""
    KEYGEN_SUCCESS=true
else
    echo -e "${YELLOW}✗ Keymap generation failed${NC}"
    echo "Cannot proceed with builds without generated keymaps"
    exit 1
fi

# Build QMK firmware
echo ""
echo "================================================"
echo "Phase 1: QMK Firmware"
echo "================================================"
echo ""

if bash "$REPO_ROOT/qmk/build_qmk.sh"; then
    QMK_SUCCESS=true
else
    echo -e "${YELLOW}⚠ QMK builds failed${NC}"
    echo ""
fi

# Build ZMK firmware
echo ""
echo "================================================"
echo "Phase 2: ZMK Firmware"
echo "================================================"
echo ""

# Choose build script based on environment
if [ "$USE_DOCKER_BUILD" = "1" ]; then
    ZMK_BUILD_SCRIPT="$REPO_ROOT/zmk/build_zmk_docker.sh"
else
    ZMK_BUILD_SCRIPT="$REPO_ROOT/zmk/build_zmk.sh"
fi

if [ -f "$ZMK_BUILD_SCRIPT" ]; then
    if bash "$ZMK_BUILD_SCRIPT"; then
        ZMK_SUCCESS=true
    else
        echo -e "${YELLOW}⚠ ZMK builds failed${NC}"
        echo ""
    fi
else
    echo -e "${YELLOW}ZMK build script not found, skipping ZMK builds${NC}"
    echo ""
fi

# Summary
echo ""
echo "================================================"
echo "Build Summary"
echo "================================================"

if [ "$KEYGEN_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ Keymap generation: SUCCESS${NC}"
else
    echo -e "${YELLOW}✗ Keymap generation: FAILED${NC}"
fi

if [ "$QMK_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ QMK builds: SUCCESS${NC}"
else
    echo -e "${YELLOW}✗ QMK builds: FAILED${NC}"
fi

if [ "$ZMK_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ ZMK builds: SUCCESS${NC}"
elif [ -f "$REPO_ROOT/zmk/build_zmk.sh" ]; then
    echo -e "${YELLOW}✗ ZMK builds: FAILED${NC}"
else
    echo -e "${BLUE}○ ZMK builds: SKIPPED${NC}"
fi

echo ""

# Show all firmware files
echo "Build artifacts in: $OUTPUT_DIR"
echo ""
echo "QMK firmware:"
ls -1 "$OUTPUT_DIR/qmk"/*.hex "$OUTPUT_DIR/qmk"/*.uf2 2>/dev/null | xargs -n1 basename || echo "  (no QMK firmware files found)"

echo ""
echo "ZMK firmware:"
ls -1 "$OUTPUT_DIR/zmk"/*.uf2 2>/dev/null | xargs -n1 basename || echo "  (no ZMK firmware files found)"

echo ""
echo "Visualizations:"
ls -1 "$OUTPUT_DIR/visualizations"/*.svg 2>/dev/null | xargs -n1 basename || echo "  (no visualizations found)"

echo ""
echo "Row-staggered .keylayout files (macOS):"
ls -1 "$OUTPUT_DIR/keylayout"/*.keylayout 2>/dev/null | xargs -n1 basename || echo "  (no .keylayout files found)"

echo ""

# Exit with appropriate code
if [ "$QMK_SUCCESS" = true ] && [ "$ZMK_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ Build completed successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}✗ Build failed${NC}"
    exit 1
fi
