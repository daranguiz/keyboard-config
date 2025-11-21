#!/bin/bash
set -e

echo "================================================"
echo "Building QMK Firmware"
echo "================================================"
echo ""

# Get the directory where this script lives (qmk/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$REPO_ROOT/out/qmk"

# Determine QMK_HOME: use env var if set, otherwise use qmk config
if [ -n "$QMK_FIRMWARE_PATH" ] && [ -d "$QMK_FIRMWARE_PATH" ]; then
    QMK_HOME="$QMK_FIRMWARE_PATH"
    echo "Using QMK_FIRMWARE_PATH: $QMK_HOME"
    # Initialize QMK setup if not already done
    if ! qmk config -ro user.qmk_home 2>/dev/null | grep -q "$QMK_HOME"; then
        echo "Initializing QMK setup..."
        qmk config user.qmk_home="$QMK_HOME"
    fi
elif [ -n "$QMK_HOME" ] && [ -d "$QMK_HOME" ]; then
    echo "Using QMK_HOME env var: $QMK_HOME"
    # Initialize QMK setup if not already done
    if ! qmk config -ro user.qmk_home 2>/dev/null | grep -q "$QMK_HOME"; then
        echo "Initializing QMK setup..."
        qmk config user.qmk_home="$QMK_HOME"
    fi
else
    QMK_HOME="$(qmk config -ro user.qmk_home 2>/dev/null | cut -d'=' -f2-)"
    if [ -z "$QMK_HOME" ] || [ ! -d "$QMK_HOME" ]; then
        echo "Error: QMK firmware not found. Please either:"
        echo "  1. Set QMK_HOME or QMK_FIRMWARE_PATH environment variable, or"
        echo "  2. Run 'qmk setup' first"
        exit 1
    fi
    echo "Using qmk config (user.qmk_home): $QMK_HOME"
fi

# Ensure QMK CLI points at this userspace (handles repo renames)
CURRENT_OVERLAY="$(qmk config -ro user.overlay_dir 2>/dev/null | cut -d'=' -f2-)"
if [ "$CURRENT_OVERLAY" != "$SCRIPT_DIR" ]; then
    echo "Updating qmk config (user.overlay_dir) -> $SCRIPT_DIR"
    qmk config user.overlay_dir="$SCRIPT_DIR"
    echo ""
fi

# Prepare upstream qmk_firmware workspace
if [ -n "$QMK_HOME" ] && [ -d "$QMK_HOME" ]; then
    BUILD_DIR="$QMK_HOME/.build"
    if [ -d "$BUILD_DIR" ]; then
        if find "$BUILD_DIR" -maxdepth 1 -name "failed.log.*" | grep -q .; then
            echo "Cleaning stale QMK failure logs..."
            find "$BUILD_DIR" -maxdepth 1 -name "failed.log.*" -delete 2>/dev/null || true
        fi
        if grep -R "qmk_userspace" "$BUILD_DIR" >/dev/null 2>&1; then
            echo "Removing stale dependency cache from previous repo name..."
            rm -rf "$BUILD_DIR"
        fi
    fi
fi

# Set QMK_USERSPACE to this directory (qmk/)
export QMK_USERSPACE="$SCRIPT_DIR"
echo "QMK_USERSPACE set to: $QMK_USERSPACE"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Build all keyboards defined in qmk.json
echo -e "${BLUE}Building keyboards from qmk.json...${NC}"
echo "Command: qmk userspace-compile"
echo ""

if qmk userspace-compile; then
    echo ""
    echo -e "${GREEN}✓ QMK builds successful${NC}"
    echo ""

    # Move firmware files to output directory
    echo "Moving firmware files to $OUTPUT_DIR..."

    # QMK outputs to both ~/qmk_firmware/ and qmk/ directory
    # Collect all firmware files and move to output
    find "$SCRIPT_DIR" -maxdepth 1 -type f \( -name "*.hex" -o -name "*.uf2" \) -exec mv {} "$OUTPUT_DIR/" \; 2>/dev/null || true
    find ~/qmk_firmware -maxdepth 1 -type f \( -name "*.hex" -o -name "*.uf2" \) -exec cp {} "$OUTPUT_DIR/" \; 2>/dev/null || true

    # Show firmware files
    echo ""
    echo "Firmware files in $OUTPUT_DIR:"
    ls -lh "$OUTPUT_DIR"/*.hex "$OUTPUT_DIR"/*.uf2 2>/dev/null || echo "  (no firmware files found)"

    exit 0
else
    echo ""
    echo -e "${YELLOW}✗ QMK builds failed${NC}"
    exit 1
fi
