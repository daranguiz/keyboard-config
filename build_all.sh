#!/bin/bash
set -e

echo "================================================"
echo "Building all QMK keyboards"
echo "================================================"
echo ""

# Set QMK_USERSPACE to the qmk/ subdirectory
# This tells QMK to treat qmk/ as the userspace root
export QMK_USERSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/qmk" && pwd)"
echo "QMK_USERSPACE set to: $QMK_USERSPACE"
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Build counters
SUCCESS_COUNT=0
FAIL_COUNT=0
KEYBOARDS=()

# Function to build a keyboard
build_keyboard() {
    local keyboard=$1
    local keymap=$2
    local name=$3

    echo -e "${BLUE}Building ${name}...${NC}"
    echo "Command: qmk compile -kb ${keyboard} -km ${keymap}"

    if qmk compile -kb "${keyboard}" -km "${keymap}" 2>&1 | grep -E "(OK|firmware size)"; then
        echo -e "${GREEN}✓ ${name} build successful${NC}"
        echo ""
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        KEYBOARDS+=("${keyboard}")
        return 0
    else
        echo -e "${YELLOW}✗ ${name} build failed${NC}"
        echo ""
        FAIL_COUNT=$((FAIL_COUNT + 1))
        return 1
    fi
}

# Generate keymaps first
echo "------------------------------------------------"
echo "Phase 0: Generating keymaps from unified config"
echo "------------------------------------------------"
echo ""

echo -e "${BLUE}Running keymap generator...${NC}"
if python3 scripts/generate.py; then
    echo -e "${GREEN}✓ Keymap generation successful${NC}"
    echo ""
else
    echo -e "${YELLOW}✗ Keymap generation failed${NC}"
    echo "Cannot proceed with builds without generated keymaps"
    exit 1
fi

# Build all keyboards
echo "------------------------------------------------"
echo "Phase 1: Building firmware"
echo "------------------------------------------------"
echo ""

build_keyboard "bastardkb/skeletyl/promicro" "dario" "Skeletyl"
build_keyboard "boardsource/lulu/rp2040" "dario" "Lulu"
build_keyboard "lily58/rev1" "dario" "Lily58"

echo ""
# Note: Keymap visualizations are now generated automatically by scripts/generate.py
# during Phase 0 (no separate phase needed)

# Summary
echo "================================================"
echo "Build Summary"
echo "================================================"
echo -e "Firmware builds: ${GREEN}${SUCCESS_COUNT} successful${NC}, ${YELLOW}${FAIL_COUNT} failed${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}All keyboard builds completed successfully!${NC}"
    echo ""
    echo "Firmware files:"
    ls -lh *.hex *.uf2 2>/dev/null || echo "  (check build output above)"
    echo ""
    echo "Visualizations:"
    ls -lh docs/keymaps/*.svg 2>/dev/null || echo "  (no visualizations generated)"
    exit 0
else
    echo -e "${YELLOW}Some builds failed. Check output above for details.${NC}"
    exit 1
fi
