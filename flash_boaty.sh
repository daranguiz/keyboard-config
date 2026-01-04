#!/bin/bash
# Flash script for Jels Boaty keyboard
# Processor: atmega328p
# Bootloader: usbasploader

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRMWARE_FILE="$SCRIPT_DIR/out/qmk/jels_boaty_dario.hex"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Jels Boaty Flash Script${NC}"
echo "================================"

# Check if firmware file exists
if [ ! -f "$FIRMWARE_FILE" ]; then
    echo -e "${RED}Error: Firmware file not found at $FIRMWARE_FILE${NC}"
    echo "Run ./build_all.sh first to build the firmware"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found firmware: $FIRMWARE_FILE"
echo ""

# Show instructions
echo -e "${YELLOW}To flash:${NC}"
echo "  1. Unplug the keyboard"
echo "  2. Hold the BOOT button while plugging in USB"
echo "  3. Release BOOT after plugging in"
echo "  4. QMK will auto-detect and flash"
echo ""
echo -e "${CYAN}QMK is waiting for bootloader...${NC}"
echo "(Hold BOOT and plug in now)"
echo ""

# QMK flash will wait for the bootloader device
qmk flash -m atmega328p "$FIRMWARE_FILE"

echo ""
echo -e "${GREEN}✓ Flash complete!${NC}"
echo "Your Boaty keyboard should now be running the new firmware."
