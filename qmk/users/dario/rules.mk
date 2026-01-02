# Shared feature flags for all keyboards
BOOTMAGIC_ENABLE = yes      # Enable Bootmagic Lite
EXTRAKEY_ENABLE = yes       # Audio control and System control
NKRO_ENABLE = yes           # N-Key Rollover
LTO_ENABLE = yes            # Link Time Optimization for smaller firmware
REPEAT_KEY_ENABLE = yes     # QK_REP / QK_AREP support
CAPS_WORD_ENABLE = yes      # Caps word (CW_TOGG) support

# User preference features
COMBO_ENABLE = yes          # Key combos
KEY_OVERRIDE_ENABLE = yes   # Shift-morph (sm:) key overrides
COMMAND_ENABLE = no         # Commands for debug and configuration

# Console for magic debugging:
#  - Disable on V-USB (endpoint conflict)
#  - Disable on AVR (size) ; keep on for other MCUs
ifeq ($(strip $(PROTOCOL)), VUSB)
  CONSOLE_ENABLE = no
else ifeq ($(strip $(MCU)), atmega32u4)
  CONSOLE_ENABLE = no
else
  CONSOLE_ENABLE = yes
endif

# Include shared source files
SRC += dario.c magic.c

# Magic logging always on
CPPFLAGS += -DMAGIC_DEBUG
