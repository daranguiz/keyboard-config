[![Build All Firmwares (QMK + ZMK)](https://github.com/daranguiz/qmk_userspace/actions/workflows/build-all.yml/badge.svg)](https://github.com/daranguiz/qmk_userspace/actions/workflows/build-all.yml)

# Keyboard Configuration

Custom keyboard firmware for split ergonomic keyboards using a unified keymap code generation system.

## Keymap Visualizations

### Split Ergonomic Keyboards

#### NIGHT Layout
![NIGHT Layout](docs/night.svg)

#### Colemak Layout
![Colemak Layout](docs/colemak.svg)

### Row-Staggered Keyboards (macOS .keylayout)

#### Nightlight
![Nightlight Layout](docs/nightlight_rowstagger.svg)

#### Rain
![Rain Layout](docs/rain_rowstagger.svg)

## About

This repository uses a unified YAML configuration to generate keymaps for both QMK and ZMK firmware. All keymaps are defined in `config/keymap.yaml` and automatically generated for each keyboard.

See [CLAUDE.md](CLAUDE.md) for detailed documentation.
