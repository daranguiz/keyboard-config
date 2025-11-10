# Shared feature flags for all keyboards
BOOTMAGIC_ENABLE = yes      # Enable Bootmagic Lite
MOUSEKEY_ENABLE = yes       # Mouse keys
EXTRAKEY_ENABLE = yes       # Audio control and System control
NKRO_ENABLE = yes           # N-Key Rollover
SPLIT_KEYBOARD = yes        # Split keyboard support
LTO_ENABLE = yes            # Link Time Optimization for smaller firmware

# User preference features
COMBO_ENABLE = no           # Key combos
CONSOLE_ENABLE = no         # Console for debug
COMMAND_ENABLE = no         # Commands for debug and configuration

# Include shared source files
SRC += dario.c
