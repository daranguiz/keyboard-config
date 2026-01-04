#!/bin/bash
# Flash script for Bastard Keyboards Skeletyl
# Processor: atmega32u4 (Pro Micro)
# Bootloader: caterina

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_FILE="$SCRIPT_DIR/out/qmk/bastardkb_skeletyl_promicro_dario.hex"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}Bastard Keyboards Skeletyl Flash Script${NC}"
echo "========================================="

# Check if firmware file exists
if [ ! -f "$FIRMWARE_FILE" ]; then
    echo -e "${RED}Error: Firmware file not found at $FIRMWARE_FILE${NC}"
    echo "Run ./build_all.sh first to build the firmware"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found firmware: $FIRMWARE_FILE"
echo ""

# Instructions for split keyboard
echo -e "${CYAN}Note: This is a split keyboard - you need to flash each half separately.${NC}"
echo ""
echo -e "${YELLOW}To flash:${NC}"
echo "  1. Run this script"
echo "  2. Double-tap the reset button on the Pro Micro"
echo "     (or use your DFU combo if configured)"
echo "  3. QMK will auto-detect and flash"
echo ""
echo -e "${CYAN}QMK is waiting for bootloader...${NC}"
echo "(Double-tap reset now)"
echo ""

# QMK flash with caterina bootloader will wait for device automatically
qmk flash -bl caterina "$FIRMWARE_FILE"

echo ""
echo -e "${GREEN}✓ Flash complete for this half!${NC}"
echo ""
echo -e "${YELLOW}Don't forget to flash the other half with the same process.${NC}"
