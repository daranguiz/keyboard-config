# Userspace configuration
USER_NAME := dario

# Keyboard-specific features (common features in users/dario/rules.mk)
AUTO_SHIFT_ENABLE = yes     # Auto Shift

# Disabled features
COMBO_ENABLE = no  # TODO: Re-enable after fixing introspection errors
CONSOLE_ENABLE = no         # Console for debug
COMMAND_ENABLE = no         # Commands for debug and configuration
BACKLIGHT_ENABLE = no       # Enable keyboard backlight functionality
RGBLIGHT_ENABLE = no        # Enable keyboard RGB underglow
RGB_MATRIX_ENABLE = no      # Enable keyboard RGB matrix
AUDIO_ENABLE = no           # Audio output

# Hardware configuration
MCU = atmega32u4
BOOTLOADER = atmel-dfu

# Keyboard-specific source files
# NOTE: mods.c removed - using userspace version from users/dario/dario.c
# TODO: Re-enable caps_word after build is working
# SRC += ./features/caps_word.c

# Support flags
AUDIO_SUPPORTED = no
RGB_MATRIX_SUPPORTED = no
RGBLIGHT_SUPPORTED = no

LAYOUTS = split_3x5_3

