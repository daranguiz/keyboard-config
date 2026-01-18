#!/bin/bash

# ZMK Firmware Build Script (Dev Container approach)
# Uses ZMK's official dev container for builds

set -e  # Exit on error

# CLI args
VERBOSE=0

usage() {
    echo "Usage: $(basename "$0") [-v|--verbose]"
    echo "  -v, --verbose   Show full west/cmake output (default: quiet, logs to file)"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ZMK Firmware Build (Dev Container)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verify ZMK repository exists
if [ ! -d "$ZMK_REPO" ]; then
    echo -e "${RED}ERROR: ZMK repository not found at $ZMK_REPO${NC}"
    echo "Set ZMK_REPO to the ZMK firmware checkout, e.g.:"
    echo "  ZMK_REPO=\$HOME/git/zmk ./build_all.sh"
    echo "or clone the repository first:"
    echo "  git clone https://github.com/zmkfirmware/zmk.git \"$ZMK_REPO\""
    exit 1
fi

# Verify build.yaml exists
if [ ! -f "$SCRIPT_DIR/build.yaml" ]; then
    echo -e "${RED}ERROR: build.yaml not found at $SCRIPT_DIR/build.yaml${NC}"
    exit 1
fi

# Verify devcontainer CLI is installed
if ! command -v devcontainer &> /dev/null; then
    echo -e "${RED}ERROR: devcontainer CLI not found${NC}"
    echo "Install with: npm install -g @devcontainers/cli"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Parse build.yaml to get build targets
echo -e "${YELLOW}Reading build targets from build.yaml...${NC}"

declare -a BOARDS
declare -a SHIELDS

# Parse board+shield pairs properly - each entry starts with "- board:"
# and optionally has a "shield:" line before the next entry
CURRENT_BOARD=""
while IFS= read -r line; do
    if [[ $line =~ -\ *board:\ *([a-zA-Z0-9_]+) ]]; then
        # New entry - save previous if exists
        if [ -n "$CURRENT_BOARD" ]; then
            BOARDS+=("$CURRENT_BOARD")
            SHIELDS+=("none")
        fi
        CURRENT_BOARD="${BASH_REMATCH[1]}"
    elif [[ $line =~ shield:\ *([a-zA-Z0-9_]+) ]]; then
        # Shield for current board
        if [ -n "$CURRENT_BOARD" ]; then
            BOARDS+=("$CURRENT_BOARD")
            SHIELDS+=("${BASH_REMATCH[1]}")
            CURRENT_BOARD=""
        fi
    fi
done < "$SCRIPT_DIR/build.yaml"

# Don't forget the last entry if it had no shield
if [ -n "$CURRENT_BOARD" ]; then
    BOARDS+=("$CURRENT_BOARD")
    SHIELDS+=("none")
fi

if [ ${#BOARDS[@]} -eq 0 ]; then
    echo -e "${RED}ERROR: No build targets found in build.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}Found ${#BOARDS[@]} build target(s):${NC}"
for i in "${!BOARDS[@]}"; do
    if [ "${SHIELDS[$i]}" != "none" ]; then
        echo "  - ${BOARDS[$i]} + ${SHIELDS[$i]}"
    else
        echo "  - ${BOARDS[$i]}"
    fi
done
echo ""

# Stop any existing dev containers
echo -e "${YELLOW}Stopping any existing dev containers...${NC}"
EXISTING_CONTAINER=$(docker ps -a --filter "label=devcontainer.local_folder=$ZMK_REPO" --format "{{.ID}}" | head -1)
if [ -n "$EXISTING_CONTAINER" ]; then
    docker stop "$EXISTING_CONTAINER" > /dev/null 2>&1 || true
    docker rm "$EXISTING_CONTAINER" > /dev/null 2>&1 || true
    echo -e "${GREEN}Stopped and removed existing container${NC}"
fi

# Start dev container
echo -e "${YELLOW}Starting fresh ZMK dev container...${NC}"
devcontainer up --workspace-folder "$ZMK_REPO" > /dev/null 2>&1

# Get container ID
CONTAINER_ID=$(docker ps --filter "label=devcontainer.local_folder=$ZMK_REPO" --format "{{.ID}}" | head -1)

if [ -z "$CONTAINER_ID" ]; then
    echo -e "${RED}ERROR: Could not find running dev container${NC}"
    exit 1
fi

echo -e "${GREEN}Dev container started: $CONTAINER_ID${NC}"
echo ""

# Initialize workspace (only needed first time, but safe to run)
echo -e "${YELLOW}Initializing Zephyr workspace...${NC}"
docker exec -w /workspaces/zmk "$CONTAINER_ID" /bin/bash -c \
    "west init -l app/ 2>/dev/null || true; west config manifest.path app; west config manifest.file west.yml; west update"
echo ""

# Build each target
BUILD_COUNT=0
FAILED_BUILDS=()
MANIFEST_CONFIGURED=0

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

    # Determine keymap directory based on shield or board name
    # Shield names are like "corne_left" or "chocofi_right"
    # Board names are like "corneish_zen_v2_left"
    # Extract base name by removing _left/_right and version suffixes
    if [ "$SHIELD" = "none" ]; then
        # For integrated boards, extract from board name
        BASE_NAME=$(echo "$BOARD" | sed 's/_v[0-9]_left$//' | sed 's/_v[0-9]_right$//' | sed 's/_left$//' | sed 's/_right$//')
    else
        # For shields, extract from shield name
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

    # Copy config into container (keymap + behaviors + global configs)
    docker exec "$CONTAINER_ID" rm -rf /tmp/zmk-config >/dev/null 2>&1
    docker exec "$CONTAINER_ID" mkdir -p /tmp/zmk-config >/dev/null 2>&1
    docker cp "$ZMK_CONFIG/." "$CONTAINER_ID:/tmp/zmk-config/" >/dev/null 2>&1
    docker cp "$SCRIPT_DIR/config/dario_behaviors.dtsi" "$CONTAINER_ID:/tmp/zmk-config/" >/dev/null 2>&1
    # Always copy west manifest so manifest.path remains valid after cleanup
    if [ -f "$SCRIPT_DIR/config/west.yml" ]; then
        docker cp "$SCRIPT_DIR/config/west.yml" "$CONTAINER_ID:/tmp/zmk-config/west.yml" >/dev/null 2>&1
    fi
    # Optional global/project config
    if [ -f "$SCRIPT_DIR/config/prj.conf" ]; then
        docker cp "$SCRIPT_DIR/config/prj.conf" "$CONTAINER_ID:/tmp/zmk-config/" >/dev/null 2>&1
    fi
    # Optional board/shield Kconfig fragments
    if [ -d "$SCRIPT_DIR/config/boards" ]; then
        docker cp "$SCRIPT_DIR/config/boards/." "$CONTAINER_ID:/tmp/zmk-config/boards/" >/dev/null 2>&1
    fi
    # Optional west manifest (adds custom modules like adaptive-key)
    if [ $MANIFEST_CONFIGURED -eq 0 ] && [ -f "$SCRIPT_DIR/config/west.yml" ]; then
        docker exec -w /workspaces/zmk "$CONTAINER_ID" /bin/bash -c \
            "west config manifest.path /tmp/zmk-config && west config manifest.file west.yml && west update" >/dev/null 2>&1
        MANIFEST_CONFIGURED=1
    fi

    LOG_FILE="$OUTPUT_DIR/${BUILD_NAME}_build.log"

    # Build inside container
    if [[ $VERBOSE -eq 1 ]]; then
        echo -e "${YELLOW}Verbose build output enabled${NC}"
        docker exec -w /workspaces/zmk "$CONTAINER_ID" /bin/bash -c \
            "west build -p -s app -b $BOARD -- $SHIELD_ARG -DZMK_CONFIG=/tmp/zmk-config -DOVERLAY_CONFIG=/tmp/zmk-config/prj.conf" \
            2>&1 | tee "$LOG_FILE"
        BUILD_EXIT=${PIPESTATUS[0]}
    else
        docker exec -w /workspaces/zmk "$CONTAINER_ID" /bin/bash -c \
            "west build -p -s app -b $BOARD -- $SHIELD_ARG -DZMK_CONFIG=/tmp/zmk-config -DOVERLAY_CONFIG=/tmp/zmk-config/prj.conf" \
            >"$LOG_FILE" 2>&1
        BUILD_EXIT=$?
    fi

    if [[ $BUILD_EXIT -eq 0 ]]; then

        # Copy firmware out of container
        docker cp "$CONTAINER_ID:/workspaces/zmk/build/zephyr/zmk.uf2" "$OUTPUT_DIR/$OUTPUT_NAME" 2>/dev/null && \
            echo -e "${GREEN}✓ Build successful: $OUTPUT_NAME${NC}" && \
            BUILD_COUNT=$((BUILD_COUNT + 1)) || \
            (echo -e "${RED}✗ Build failed: firmware file not found${NC}" && FAILED_BUILDS+=("$BUILD_NAME"))
        # Drop build log on success to keep workspace clean
        rm -f "$LOG_FILE"
    else
        echo -e "${RED}✗ Build failed: $BUILD_NAME${NC}"
        echo -e "${YELLOW}Last 40 lines of build log (${LOG_FILE}):${NC}"
        tail -n 40 "$LOG_FILE" 2>/dev/null || true
        FAILED_BUILDS+=("$BUILD_NAME")
    fi

    echo ""
done

# Stop container
echo -e "${YELLOW}Stopping dev container...${NC}"
docker stop "$CONTAINER_ID" > /dev/null
echo ""

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
