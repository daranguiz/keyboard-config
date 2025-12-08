[![Build All Firmwares (QMK + ZMK)](https://github.com/daranguiz/qmk_userspace/actions/workflows/build-all.yml/badge.svg)](https://github.com/daranguiz/qmk_userspace/actions/workflows/build-all.yml)

# Keyboard Configuration

Custom keyboard firmware for split ergonomic keyboards using a unified keymap code generation system.

## Combos

### Bootloader Entry (DFU)
- Left hand: B + Q + Z
- Right hand: P + . + '

### GitHub URL
- Keys: G + O + U + .
- Outputs: `https://github.com/daranguiz/keyboard-config?tab=readme-ov-file#readme`

## Keymap Visualizations

### Split Ergonomic Keyboards

#### NIGHT Layout
![NIGHT Layout](docs/night.svg)

#### DUSK Layout
![DUSK Layout](docs/dusk.svg)

#### Colemak Layout
![Colemak Layout](docs/colemak.svg)

### Row-Staggered Keyboards (macOS .keylayout)

#### Nightlight
![Nightlight Layout](docs/nightlight_rowstagger.svg)

#### Rain
![Rain Layout](docs/rain_rowstagger.svg)

#### Sturdy
![Sturdy Layout](docs/sturdy_rowstagger.svg)

## About

This repository uses a unified YAML configuration to generate keymaps for both QMK and ZMK firmware. All keymaps are defined in `config/keymap.yaml` and automatically generated for each keyboard.

See [CLAUDE.md](CLAUDE.md) for detailed documentation.
