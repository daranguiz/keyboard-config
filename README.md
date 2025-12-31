[![Build All Firmwares (QMK + ZMK)](https://github.com/daranguiz/qmk_userspace/actions/workflows/build-all.yml/badge.svg)](https://github.com/daranguiz/qmk_userspace/actions/workflows/build-all.yml)

# Keyboard Configuration

Custom keyboard firmware for split ergonomic keyboards using a unified keymap code generation system.

## Combos

### Bootloader Entry (DFU)
- Left hand: `B` + `Q` + `Z`
- Right hand: `P` + `.` + `'`

### GitHub URL
- Keys: `G` + `O` + `U` + `.`
- Outputs: `https://github.com/daranguiz/keyboard-config?tab=readme-ov-file#readme`

## Keymap Visualizations

Magic key mappings are included at the bottom of each layout visualization.

### Split Ergonomic Keyboards

![PRIMARY Layout](docs/split/primary.svg)

### Row-Staggered Keyboards (macOS .keylayout)

#### Gallium
![Gallium Layout](docs/rowstagger/gallium.svg)

#### Nightlight
![Nightlight Layout](docs/rowstagger/nightlight.svg)

#### Rain
![Rain Layout](docs/rowstagger/rain.svg)

#### Rainy Racket
![Rainy Racket Layout](docs/rowstagger/rainy_racket.svg)

#### Sturdy
![Sturdy Layout](docs/rowstagger/sturdy.svg)

## Testing

The project includes a comprehensive tiered testing suite:

### Quick Regression Tests (Tier 1)
```bash
pytest                    # < 30 seconds
```

Runs unit tests and integration tests (without firmware compilation) to catch regressions quickly.

### Comprehensive Tests (Tier 2)
```bash
pytest --tier2            # 5-15 minutes, requires QMK/ZMK setup
```

Compiles actual firmware for all boards to ensure generated code builds successfully.

### Coverage Report
```bash
pytest --cov=scripts --cov-report=html
open htmlcov/index.html
```

See [CLAUDE.md](CLAUDE.md) for detailed testing documentation.

## About

This repository uses a unified YAML configuration to generate keymaps for both QMK and ZMK firmware. All keymaps are defined in `config/keymap.yaml` and automatically generated for each keyboard.

See [CLAUDE.md](CLAUDE.md) for detailed documentation.
