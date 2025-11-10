# Userspace configuration
USER_NAME := dario

# Keyboard-specific features (common features in users/dario/rules.mk)
AUTO_SHIFT_ENABLE = yes     # Auto Shift
OLED_ENABLE = yes
WPM_ENABLE = yes

# Disabled features
COMBO_ENABLE = no  # TODO: Re-enable after fixing introspection errors

# Keyboard-specific source files
# NOTE: mods.c removed - using userspace version from users/dario/dario.c
SRC += ./oled.c
