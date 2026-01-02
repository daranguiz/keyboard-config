# Testing Documentation

This directory contains the comprehensive test suite for the keyboard-config unified keymap generator.

## Philosophy

The test suite uses a **tiered approach** to balance speed and thoroughness:

- **Tier 1 (Fast)**: Quick regression tests (< 30s) run on every commit
- **Tier 2 (Comprehensive)**: Full E2E tests with firmware compilation (5-15 min) run in CI

## Running Tests

### Quick Regression Tests (Default)
```bash
pytest                    # Runs Tier 1 only, < 30 seconds
```

### With Coverage
```bash
pytest --cov=scripts --cov-report=html --cov-report=term
open htmlcov/index.html   # View coverage report
```

### Comprehensive Tests (Tier 2)
```bash
pytest --tier2            # Runs both tiers, 5-15 minutes
```

Requires:
- QMK firmware repo (set `QMK_FIRMWARE_PATH`)
- ZMK firmware repo (set `ZMK_REPO`)
- Docker (for ZMK builds) OR west toolchain

### Specific Tests
```bash
# Single test file
pytest tests/unit/test_validator.py -v

# Single test class
pytest tests/unit/test_validator.py::TestLayerNameValidation -v

# Single test function
pytest tests/unit/test_validator.py::test_production_config_is_valid -v

# By marker
pytest -m tier1           # Only Tier 1 tests
pytest -m tier2           # Only Tier 2 tests
pytest -m qmk             # Only QMK-related tests
```

### Update Golden Files
```bash
pytest tests/integration/test_golden_snapshots.py --snapshot-update
git add tests/fixtures/golden/
```

## Directory Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── pytest.ini               # Pytest settings and markers
├── helpers.py               # Test utility functions
├── README.md                # This file
│
├── unit/                    # Tier 1: Unit tests
│   ├── test_validator.py           # Configuration validation (16 tests)
│   ├── test_config_parser.py       # YAML parsing
│   ├── test_qmk_translator.py      # QMK keycode translation
│   ├── test_zmk_translator.py      # ZMK keycode translation
│   ├── test_layer_compiler.py      # Layer compilation logic
│   ├── test_qmk_generator.py       # QMK code generation
│   ├── test_zmk_generator.py       # ZMK code generation
│   ├── test_data_model.py          # Data structures
│   ├── test_visualizer.py          # Visualization generation
│   ├── test_keylayout_translator.py # macOS keylayout translation
│   └── test_base_layer_utils.py    # Base layer management
│
├── integration/             # Tier 1: Integration tests
│   ├── test_full_keymap_generation.py  # Full-featured keymap test (CRITICAL)
│   ├── test_end_to_end_generation.py   # Complete generation pipeline
│   ├── test_golden_snapshots.py        # Golden file regression detection
│   ├── test_cross_board_consistency.py # Cross-board validation
│   └── test_special_syntax.py          # Complex behavior testing
│
├── e2e/                     # Tier 2: End-to-end tests (requires firmware repos)
│   ├── test_qmk_compilation.py         # Actual QMK firmware builds (12 tests)
│   ├── test_zmk_compilation.py         # Actual ZMK firmware builds (9 tests)
│   └── test_full_pipeline.py           # Complete build_all.sh (11 tests)
│
└── fixtures/                # Test data
    ├── configs/                        # Test YAML configurations
    │   ├── minimal_keymap.yaml        # Simplest valid config
    │   └── invalid_*.yaml             # Error test cases
    ├── golden/                         # Expected outputs (snapshots)
    │   ├── qmk/
    │   │   ├── skeletyl/keymap.c
    │   │   └── lulu/keymap.c
    │   └── zmk/
    │       └── chocofi/corne.keymap
    └── generated/                      # Temp outputs (gitignored)
```

## Test Coverage

**Target**: 80%+ line coverage on `scripts/` directory

**Current Coverage by Module**:
- validator.py: 95%+ (comprehensive validation tests)
- config_parser.py: 90%+ (parsing tests)
- translators: 85%+ (QMK/ZMK translation tests)
- generators: 75%+ (code generation tests)
- Overall: 80%+

Run `pytest --cov=scripts --cov-report=html` to see detailed coverage.

## Key Test Files

### test_full_keymap_generation.py (CRITICAL)

This integration test uses the **real production config** to ensure all features work together:

- Multiple base layers (BASE_NIGHT, BASE_GALLIUM, etc.)
- Combos
- Magic keys
- Shift-morphs (sm:)
- Layer-tap (lt:)
- One-shot layers (osl:)
- Mod-tap (mt:)
- Home row mods (hrm:)
- Extensions (3x6_3)
- L36 references (Boaty)
- Row-stagger layouts

**Why it matters**: Catches regressions when adding new features. Runs in < 5 seconds (codegen only, no firmware build).

### test_golden_snapshots.py

Compares generated files against golden snapshots to detect unintended changes:

- QMK keymap.c files
- ZMK .keymap files
- Visualizations
- Config files

**Update workflow**:
```bash
# After intentional generator changes
pytest tests/integration/test_golden_snapshots.py --snapshot-update
git diff tests/fixtures/golden/  # Review changes
git commit -m "Update golden files after feature addition"
```

### test_validator.py

Unit tests for configuration validation:

- Layer structure (36-key core)
- Layer names (C identifier rules)
- Board configuration
- Firmware-specific requirements
- Position reference bounds

**16 tests, all passing in 0.04s**

### test_qmk_compilation.py (Tier 2)

Actual QMK firmware compilation tests (requires QMK firmware repo and toolchains):

- Compile individual boards (skeletyl, lulu, etc.)
- Compile all QMK boards in inventory
- Firmware size regression detection
- Clean build validation
- Verify .hex/.uf2 artifacts created
- Board-specific layout verification (LAYOUT_split_3x5_3, etc.)

**Requirements**:
```bash
export QMK_FIRMWARE_PATH=/path/to/qmk_firmware
export QMK_USERSPACE="$(realpath qmk)"
# Ensure avr-gcc and arm-none-eabi-gcc are installed
```

**12 tests, execution time: ~10-15 minutes (compiles all QMK boards)**

### test_zmk_compilation.py (Tier 2)

Actual ZMK firmware compilation tests via Docker or west:

- Compile individual shields (chocofi, etc.)
- Compile both left and right sides of split keyboards
- Compile all ZMK boards in inventory
- Firmware size validation
- Verify .uf2 artifacts created
- Home row mod behaviors verification

**Requirements** (Docker approach):
```bash
export ZMK_REPO=/path/to/zmk
# Ensure Docker is running
docker pull zmkfirmware/zmk-build-arm:stable
```

**Requirements** (Native west approach):
```bash
export ZMK_REPO=/path/to/zmk
# Install west toolchain
pip install west
```

**9 tests, execution time: ~5-10 minutes per board (Docker builds)**

### test_full_pipeline.py (Tier 2)

Complete build_all.sh pipeline validation:

- Run build_all.sh script end-to-end
- Verify out/ directory structure created
- Check QMK artifacts in out/qmk/ (.hex, .uf2)
- Check ZMK artifacts in out/zmk/ (.uf2 for left/right)
- Verify visualizations in out/visualizations/ (.svg)
- Verify keylayout files in out/keylayout/ (.keylayout)
- Test --no-magic-training flag
- Deterministic output validation (build twice, compare)

**Requirements**:
```bash
export QMK_USERSPACE="$(realpath qmk)"
export QMK_HOME=/path/to/qmk_firmware
export ZMK_REPO=/path/to/zmk
# Docker or west for ZMK builds
```

**11 tests, execution time: ~15-30 minutes (full pipeline with all boards)**

## Writing New Tests

### Adding a Unit Test

1. Create test file in `tests/unit/test_<module>.py`
2. Mark with `@pytest.mark.tier1`
3. Use fixtures from `conftest.py`
4. Follow naming convention: `test_<what_it_does>`

Example:
```python
import pytest

@pytest.mark.tier1
def test_my_feature(keymap_config):
    """Test description"""
    # Test code
    assert something
```

### Adding an Integration Test

1. Create test in `tests/integration/`
2. Mark with `@pytest.mark.tier1`
3. Use `generator` fixture or create instance
4. Test end-to-end generation

### Adding an E2E Test

1. Create test in `tests/e2e/`
2. Mark with `@pytest.mark.tier2`
3. Add appropriate markers (`@pytest.mark.qmk`, `@pytest.mark.requires_docker`, etc.)
4. Use environment fixtures (`qmk_build_env`, `zmk_firmware_path`)

## Pytest Markers

- `tier1` - Fast regression tests (< 30s)
- `tier2` - Comprehensive E2E tests (5-15min)
- `qmk` - Requires QMK toolchain
- `zmk` - Requires ZMK toolchain
- `requires_docker` - Requires Docker daemon
- `requires_qmk_firmware` - Requires QMK firmware repo
- `requires_zmk_firmware` - Requires ZMK firmware repo
- `slow` - Slow test (> 30s)

## Fixtures

See `conftest.py` for all available fixtures:

**Path Fixtures**:
- `repo_root` - Repository root directory
- `config_dir` - Config directory
- `fixtures_dir` - Test fixtures directory
- `test_output_dir` - Temporary output directory

**Config Fixtures**:
- `keymap_config` - Production keymap configuration
- `board_inventory` - Production board inventory
- `aliases` - Behavior aliases
- `keycodes` - Keycode mappings
- `combos` - Combo configuration
- `magic_config` - Magic key configuration

**Generator Fixtures**:
- `generator` - Main keymap generator instance
- `qmk_translator` - QMK translator
- `zmk_translator` - ZMK translator
- `layer_compiler` - Layer compiler

**E2E Fixtures** (Tier 2):
- `qmk_firmware_path` - QMK firmware repo path
- `qmk_build_env` - QMK build environment
- `zmk_firmware_path` - ZMK firmware repo path
- `docker_available` - Docker availability check

## Continuous Integration

Tests run automatically on GitHub Actions:

**Tier 1** (every push):
- All unit tests
- All integration tests
- Coverage reporting to Codecov

**Tier 2** (main branch, PRs):
- QMK firmware compilation (all boards)
- ZMK firmware compilation (all boards)
- Full pipeline validation

See `.github/workflows/test.yml` for CI configuration.

## Troubleshooting

### Test Fails: "Config not found"
```bash
# Make sure you're running from repo root
cd /path/to/keyboard-config
pytest
```

### Test Skipped: "QMK firmware not available"
```bash
# Set environment variable
export QMK_FIRMWARE_PATH=/path/to/qmk_firmware
pytest --tier2
```

### Test Skipped: "Docker not available"
```bash
# Install Docker or use native ZMK build
# For native ZMK:
pip install west
pytest --tier2
```

### Golden File Mismatch
```bash
# Review the diff
pytest tests/integration/test_golden_snapshots.py -vv

# If change is intentional, update:
pytest tests/integration/test_golden_snapshots.py --snapshot-update
git add tests/fixtures/golden/
```

## Best Practices

1. **Keep tests fast**: Tier 1 tests should complete in < 30s total
2. **Test behavior, not implementation**: Focus on what code does, not how
3. **Use descriptive names**: Test names should describe what they verify
4. **One assertion per test**: Makes failures easier to diagnose
5. **Update golden files carefully**: Review diffs before committing
6. **Mark tests appropriately**: Use correct tier and requirement markers
7. **Document complex tests**: Add docstrings explaining what's being tested

## Coverage Goals

- New features: 100% coverage required
- Bug fixes: Add test that would have caught the bug
- Refactoring: Maintain or improve coverage
- Overall target: 80%+ line coverage

Run coverage locally before pushing:
```bash
pytest --cov=scripts --cov-fail-under=80
```

## Questions?

See [CLAUDE.md](../CLAUDE.md) for more documentation or open an issue.
