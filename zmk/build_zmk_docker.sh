#!/bin/bash

# ZMK Firmware Build Script (Docker-based for CI/CD)
# Uses ZMK's official Docker image for builds

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ZMK_REPO="${ZMK_REPO:-$HOME/git/zmk}"
OUTPUT_DIR="$REPO_ROOT/out/zmk"
DOCKER_IMAGE="zmkfirmware/zmk-build-arm:stable"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ZMK Firmware Build (Docker)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify ZMK repository exists
if [ ! -d "$ZMK_REPO" ]; then
    echo -e "${RED}ERROR: ZMK repository not found at $ZMK_REPO${NC}"
    echo "Set ZMK_REPO to the ZMK firmware checkout, e.g.:"
    echo "  ZMK_REPO=\$HOME/git/zmk ./build_zmk_docker.sh"
    echo "or clone the repository first:"
    echo "  git clone https://github.com/zmkfirmware/zmk.git \"$ZMK_REPO\""
    exit 1
fi

# Verify build.yaml exists
if [ ! -f "$SCRIPT_DIR/build.yaml" ]; then
    echo -e "${RED}ERROR: build.yaml not found at $SCRIPT_DIR/build.yaml${NC}"
    exit 1
fi

# Verify Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker not found${NC}"
    echo "Install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Pull Docker image
echo -e "${YELLOW}Pulling ZMK Docker image...${NC}"
docker pull "$DOCKER_IMAGE"
echo ""

# Parse build.yaml to get build targets
echo -e "${YELLOW}Reading build targets from build.yaml...${NC}"

declare -a BOARDS
declare -a SHIELDS

while IFS= read -r line; do
    if [[ $line =~ board:\ *([a-zA-Z0-9_]+) ]]; then
        BOARDS+=("${BASH_REMATCH[1]}")
    fi
    if [[ $line =~ shield:\ *([a-zA-Z0-9_]+) ]]; then
        SHIELDS+=("${BASH_REMATCH[1]}")
    fi
done < "$SCRIPT_DIR/build.yaml"

if [ ${#BOARDS[@]} -eq 0 ]; then
    echo -e "${RED}ERROR: No build targets found in build.yaml${NC}"
    exit 1
fi

while [ ${#SHIELDS[@]} -lt ${#BOARDS[@]} ]; do
    SHIELDS+=("none")
done

echo -e "${GREEN}Found ${#BOARDS[@]} build target(s):${NC}"
for i in "${!BOARDS[@]}"; do
    if [ "${SHIELDS[$i]}" != "none" ]; then
        echo "  - ${BOARDS[$i]} + ${SHIELDS[$i]}"
    else
        echo "  - ${BOARDS[$i]}"
    fi
done
echo ""

# Create temporary build directory
TEMP_BUILD_DIR=$(mktemp -d)
trap "rm -rf $TEMP_BUILD_DIR" EXIT

# Build each target
BUILD_COUNT=0
FAILED_BUILDS=()

for i in "${!BOARDS[@]}"; do
    BOARD="${BOARDS[$i]}"
    SHIELD="${SHIELDS[$i]}"

    if [ "$SHIELD" = "none" ]; then
        BUILD_NAME="$BOARD"
        SHIELD_ARG=""
        OUTPUT_NAME="${BOARD}.uf2"
    else
        BUILD_NAME="${SHIELD}"
        SHIELD_ARG="-DSHIELD=$SHIELD"
        OUTPUT_NAME="${SHIELD}.uf2"
    fi

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Building: $BUILD_NAME${NC}"
    echo -e "${BLUE}Board: $BOARD${NC}"
    if [ -n "$SHIELD_ARG" ]; then
        echo -e "${BLUE}Shield: $SHIELD${NC}"
    fi
    echo -e "${BLUE}========================================${NC}"

    # Determine keymap directory
    if [ "$SHIELD" = "none" ]; then
        BASE_NAME=$(echo "$BOARD" | sed 's/_v[0-9]_left$//' | sed 's/_v[0-9]_right$//' | sed 's/_left$//' | sed 's/_right$//')
    else
        BASE_NAME=$(echo "$SHIELD" | sed 's/_left$//' | sed 's/_right$//')
    fi
    ZMK_CONFIG="$SCRIPT_DIR/keymaps/${BASE_NAME}_dario"

    if [ ! -d "$ZMK_CONFIG" ]; then
        echo -e "${RED}ERROR: Keymap directory not found: $ZMK_CONFIG${NC}"
        echo "Run 'python3 scripts/generate.py' to generate keymaps first"
        FAILED_BUILDS+=("$BUILD_NAME")
        continue
    fi

    echo -e "${BLUE}Keymap: $ZMK_CONFIG${NC}"

    # Create config directory for this build
    BUILD_CONFIG="$TEMP_BUILD_DIR/config_$i"
    mkdir -p "$BUILD_CONFIG"
    cp -r "$ZMK_CONFIG"/* "$BUILD_CONFIG/"
    cp "$SCRIPT_DIR/config/dario_behaviors.dtsi" "$BUILD_CONFIG/"

    # Copy west manifest if it exists (for custom modules like adaptive-key)
    if [ -f "$SCRIPT_DIR/config/west.yml" ]; then
        cp "$SCRIPT_DIR/config/west.yml" "$BUILD_CONFIG/west.yml"
    fi

    # Run West build in Docker
    if docker run --rm \
        -v "$ZMK_REPO:/zmk" \
        -v "$BUILD_CONFIG:/config" \
        -w /zmk \
        "$DOCKER_IMAGE" \
        sh -c "
            set -e
            git config --global --add safe.directory /zmk
            west init -l app/ 2>/dev/null || true
            # Configure west to use custom manifest if present
            if [ -f /config/west.yml ]; then
                west config manifest.path /config
                west config manifest.file west.yml
            fi
            west update
            west build -p -s app -b $BOARD -- $SHIELD_ARG -DZMK_CONFIG=/config
        " 2>&1 | grep -v "cmake" | grep -E "Building|-- |ERROR|error|✓|✗|$"; then

        # Copy firmware out
        if [ -f "$ZMK_REPO/build/zephyr/zmk.uf2" ]; then
            cp "$ZMK_REPO/build/zephyr/zmk.uf2" "$OUTPUT_DIR/$OUTPUT_NAME"
            echo -e "${GREEN}✓ Build successful: $OUTPUT_NAME${NC}"
            BUILD_COUNT=$((BUILD_COUNT + 1))
        else
            echo -e "${RED}✗ Build failed: firmware file not found${NC}"
            FAILED_BUILDS+=("$BUILD_NAME")
        fi
    else
        echo -e "${RED}✗ Build failed: $BUILD_NAME${NC}"
        FAILED_BUILDS+=("$BUILD_NAME")
    fi

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Build Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successful builds: $BUILD_COUNT${NC}"

if [ ${#FAILED_BUILDS[@]} -gt 0 ]; then
    echo -e "${RED}Failed builds: ${#FAILED_BUILDS[@]}${NC}"
    for build in "${FAILED_BUILDS[@]}"; do
        echo -e "${RED}  - $build${NC}"
    done
    exit 1
fi

echo ""
echo -e "${GREEN}All builds complete!${NC}"
echo -e "${GREEN}Firmware files are in: $OUTPUT_DIR${NC}"
ls -lh "$OUTPUT_DIR"/*.uf2 2>/dev/null || echo "No .uf2 files found"
