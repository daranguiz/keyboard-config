#!/bin/bash
# Add a new keyboard to the unified keymap system
# Usage: ./add_board.sh --id <board_id> --name "<board name>" --firmware <qmk|zmk> --keyboard <qmk_path> --layout <layout_size>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
BOARD_ID=""
BOARD_NAME=""
FIRMWARE=""
QMK_KEYBOARD=""
ZMK_SHIELD=""
LAYOUT_SIZE="3x5_3"
EXTRA_LAYERS=""

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Add a new keyboard to the unified keymap configuration system.

OPTIONS:
    --id <board_id>           Board identifier (required, e.g., "skeletyl", "corne")
    --name "<board name>"     Human-readable name (required, e.g., "Bastard Keyboards Skeletyl")
    --firmware <qmk|zmk>      Target firmware (required)
    --keyboard <path>         QMK keyboard path (required if firmware=qmk, e.g., "bastardkb/skeletyl/promicro")
    --shield <name>           ZMK shield name (required if firmware=zmk, e.g., "corne")
    --layout <size>           Layout size (optional, default: "3x5_3")
                              Options: "3x5_3" (36-key), "3x5_3_pinky" (38-key), "3x6_3" (42-key), "custom_*"
    --extra-layers <layers>   Comma-separated extra layer names (optional, e.g., "GAME,MACRO")
    -h, --help                Show this help message

EXAMPLES:
    # Add a 36-key QMK board
    $0 --id skeletyl --name "Bastard Keyboards Skeletyl" \\
       --firmware qmk --keyboard "bastardkb/skeletyl/promicro" --layout "3x5_3"

    # Add a 42-key ZMK board
    $0 --id corne --name "Corne (CRKBD)" \\
       --firmware zmk --shield "corne" --layout "3x6_3"

    # Add a 58-key board with gaming layer
    $0 --id lulu --name "Boardsource Lulu" \\
       --firmware qmk --keyboard "boardsource/lulu/rp2040" \\
       --layout "custom_58" --extra-layers "GAME"

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --id)
            BOARD_ID="$2"
            shift 2
            ;;
        --name)
            BOARD_NAME="$2"
            shift 2
            ;;
        --firmware)
            FIRMWARE="$2"
            shift 2
            ;;
        --keyboard)
            QMK_KEYBOARD="$2"
            shift 2
            ;;
        --shield)
            ZMK_SHIELD="$2"
            shift 2
            ;;
        --layout)
            LAYOUT_SIZE="$2"
            shift 2
            ;;
        --extra-layers)
            EXTRA_LAYERS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$BOARD_ID" ]]; then
    echo -e "${RED}Error: --id is required${NC}"
    usage
fi

if [[ -z "$BOARD_NAME" ]]; then
    echo -e "${RED}Error: --name is required${NC}"
    usage
fi

if [[ -z "$FIRMWARE" ]]; then
    echo -e "${RED}Error: --firmware is required${NC}"
    usage
fi

if [[ "$FIRMWARE" != "qmk" && "$FIRMWARE" != "zmk" ]]; then
    echo -e "${RED}Error: --firmware must be 'qmk' or 'zmk'${NC}"
    usage
fi

if [[ "$FIRMWARE" == "qmk" && -z "$QMK_KEYBOARD" ]]; then
    echo -e "${RED}Error: --keyboard is required for QMK firmware${NC}"
    usage
fi

if [[ "$FIRMWARE" == "zmk" && -z "$ZMK_SHIELD" ]]; then
    echo -e "${RED}Error: --shield is required for ZMK firmware${NC}"
    usage
fi

# Print summary
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Adding New Keyboard to Unified Keymap System ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Board ID:${NC}        $BOARD_ID"
echo -e "${YELLOW}Board Name:${NC}      $BOARD_NAME"
echo -e "${YELLOW}Firmware:${NC}        $FIRMWARE"
if [[ "$FIRMWARE" == "qmk" ]]; then
    echo -e "${YELLOW}QMK Keyboard:${NC}    $QMK_KEYBOARD"
else
    echo -e "${YELLOW}ZMK Shield:${NC}      $ZMK_SHIELD"
fi
echo -e "${YELLOW}Layout Size:${NC}     $LAYOUT_SIZE"
[[ -n "$EXTRA_LAYERS" ]] && echo -e "${YELLOW}Extra Layers:${NC}    $EXTRA_LAYERS"
echo ""

# Confirm
read -p "$(echo -e ${YELLOW}Proceed with adding this board? [y/N]:${NC} )" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted.${NC}"
    exit 1
fi

# Step 1: Add board to config/boards.yaml
echo -e "${BLUE}📝 Adding board to config/boards.yaml...${NC}"

BOARDS_YAML="$REPO_ROOT/config/boards.yaml"

# Check if board already exists
if grep -q "^  $BOARD_ID:" "$BOARDS_YAML" 2>/dev/null; then
    echo -e "${RED}Error: Board '$BOARD_ID' already exists in boards.yaml${NC}"
    exit 1
fi

# Build YAML entry
YAML_ENTRY="\n  $BOARD_ID:\n"
YAML_ENTRY+="    name: \"$BOARD_NAME\"\n"
YAML_ENTRY+="    firmware: $FIRMWARE\n"

if [[ "$FIRMWARE" == "qmk" ]]; then
    YAML_ENTRY+="    qmk_keyboard: \"$QMK_KEYBOARD\"\n"
else
    YAML_ENTRY+="    zmk_shield: \"$ZMK_SHIELD\"\n"
fi

YAML_ENTRY+="    layout_size: \"$LAYOUT_SIZE\"\n"

if [[ -n "$EXTRA_LAYERS" ]]; then
    YAML_ENTRY+="    extra_layers:\n"
    IFS=',' read -ra LAYERS <<< "$EXTRA_LAYERS"
    for layer in "${LAYERS[@]}"; do
        YAML_ENTRY+="      - $layer\n"
    done
fi

# Append to boards.yaml (before the last line if it exists, or at the end)
if [[ -f "$BOARDS_YAML" ]]; then
    echo -e "$YAML_ENTRY" >> "$BOARDS_YAML"
else
    echo -e "boards:$YAML_ENTRY" > "$BOARDS_YAML"
fi

echo -e "${GREEN}✅ Added board to boards.yaml${NC}"

# Step 2: Create firmware-specific config file
if [[ "$FIRMWARE" == "qmk" ]]; then
    echo -e "${BLUE}📝 Creating QMK board config file...${NC}"

    CONFIG_FILE="$REPO_ROOT/qmk/config/boards/${BOARD_ID}.mk"
    TEMPLATE_FILE="$SCRIPT_DIR/templates/qmk_board.mk.template"

    if [[ -f "$CONFIG_FILE" ]]; then
        echo -e "${YELLOW}Warning: $CONFIG_FILE already exists, skipping template creation${NC}"
    else
        # Create config from template
        mkdir -p "$REPO_ROOT/qmk/config/boards"

        sed -e "s|{{BOARD_NAME}}|$BOARD_NAME|g" \
            -e "s|{{BOARD_ID}}|$BOARD_ID|g" \
            -e "s|{{QMK_KEYBOARD}}|$QMK_KEYBOARD|g" \
            -e "s|{{TIMESTAMP}}|$(date -u +"%Y-%m-%d %H:%M:%S UTC")|g" \
            "$TEMPLATE_FILE" > "$CONFIG_FILE"

        echo -e "${GREEN}✅ Created $CONFIG_FILE${NC}"
    fi
else
    echo -e "${BLUE}📝 Creating ZMK board config file...${NC}"

    CONFIG_FILE="$REPO_ROOT/zmk/config/boards/${BOARD_ID}.conf"
    TEMPLATE_FILE="$SCRIPT_DIR/templates/zmk_board.conf.template"

    if [[ -f "$CONFIG_FILE" ]]; then
        echo -e "${YELLOW}Warning: $CONFIG_FILE already exists, skipping template creation${NC}"
    else
        # Create config from template
        mkdir -p "$REPO_ROOT/zmk/config/boards"

        sed -e "s|{{BOARD_NAME}}|$BOARD_NAME|g" \
            -e "s|{{BOARD_ID}}|$BOARD_ID|g" \
            -e "s|{{ZMK_SHIELD}}|$ZMK_SHIELD|g" \
            -e "s|{{TIMESTAMP}}|$(date -u +"%Y-%m-%d %H:%M:%S UTC")|g" \
            "$TEMPLATE_FILE" > "$CONFIG_FILE"

        echo -e "${GREEN}✅ Created $CONFIG_FILE${NC}"
    fi
fi

# Step 3: Test keymap generation
echo -e "${BLUE}🔨 Testing keymap generation...${NC}"
cd "$REPO_ROOT"
python3 scripts/generate.py

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Keymap generation successful!${NC}"
else
    echo -e "${RED}❌ Keymap generation failed${NC}"
    exit 1
fi

# Step 4: Show next steps
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Board Added Successfully! 🎉         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Edit board-specific features:"
if [[ "$FIRMWARE" == "qmk" ]]; then
    echo -e "   ${BLUE}$CONFIG_FILE${NC}"
    echo "   (Enable OLED, RGB, encoders, etc.)"
else
    echo -e "   ${BLUE}$CONFIG_FILE${NC}"
    echo "   (Enable display, RGB, battery settings, etc.)"
fi
echo ""
echo "2. Add board-specific extensions to config/keymap.yaml (if needed):"
echo "   For larger boards, add extension definitions under each layer."
echo ""
echo "3. Generate keymaps:"
echo -e "   ${BLUE}python3 scripts/generate.py${NC}"
echo ""
echo "4. Build firmware:"
if [[ "$FIRMWARE" == "qmk" ]]; then
    echo -e "   ${BLUE}qmk compile -kb $QMK_KEYBOARD -km dario${NC}"
else
    echo "   (Configure ZMK build in your ZMK environment)"
fi
echo ""
echo -e "${GREEN}Done!${NC}"
