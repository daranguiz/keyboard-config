#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for keyboard-config tests.

This file provides:
- Session-scoped fixtures for repo/config paths
- Shared configuration loading fixtures
- Mock fixtures for testing
- Custom pytest markers and command-line options
- Skip logic based on environment availability
"""

import pytest
from pathlib import Path
import sys
import os
import shutil

# Add scripts directory to Python path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def repo_root():
    """Repository root directory"""
    return REPO_ROOT


@pytest.fixture(scope="session")
def config_dir(repo_root):
    """Config directory"""
    return repo_root / "config"


@pytest.fixture(scope="session")
def fixtures_dir():
    """Test fixtures directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def test_output_dir(tmp_path):
    """Temporary output directory for test generation (cleaned per test)"""
    output = tmp_path / "generated"
    output.mkdir(exist_ok=True)
    return output


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def keymap_config(config_dir):
    """Production keymap configuration"""
    from config_parser import YAMLConfigParser
    return YAMLConfigParser.parse_keymap(config_dir / "keymap.yaml")


@pytest.fixture(scope="session")
def board_inventory(config_dir):
    """Production board inventory"""
    from config_parser import YAMLConfigParser
    return YAMLConfigParser.parse_boards(config_dir / "boards.yaml")


@pytest.fixture(scope="session")
def aliases(config_dir):
    """Behavior aliases configuration"""
    from config_parser import YAMLConfigParser
    return YAMLConfigParser.parse_aliases(config_dir / "aliases.yaml")


@pytest.fixture(scope="session")
def keycodes(config_dir):
    """Keycode mappings"""
    from config_parser import YAMLConfigParser
    return YAMLConfigParser.parse_keycodes(config_dir / "keycodes.yaml")


@pytest.fixture(scope="session")
def combos(config_dir):
    """Combo configuration"""
    from config_parser import YAMLConfigParser
    return YAMLConfigParser.parse_combos(config_dir / "keymap.yaml")


@pytest.fixture(scope="session")
def magic_config(config_dir):
    """Magic key configuration"""
    from config_parser import YAMLConfigParser
    try:
        return YAMLConfigParser.parse_magic_keys(config_dir / "keymap.yaml")
    except Exception:
        # Magic config might be incomplete or invalid in test environment
        return None


@pytest.fixture(scope="session")
def minimal_keymap_config(fixtures_dir):
    """Minimal valid keymap configuration for testing"""
    from config_parser import YAMLConfigParser
    minimal_config_path = fixtures_dir / "configs" / "minimal_keymap.yaml"

    # Skip if minimal config doesn't exist yet
    if not minimal_config_path.exists():
        pytest.skip(f"Minimal config not yet created: {minimal_config_path}")

    return YAMLConfigParser.parse_keymap(minimal_config_path)


@pytest.fixture(scope="session")
def full_layout_config(fixtures_dir):
    """Config with full_layout layers using L36 references"""
    from config_parser import YAMLConfigParser
    config_path = fixtures_dir / "configs" / "minimal_full_layout.yaml"
    return YAMLConfigParser.parse_keymap(config_path)


@pytest.fixture(scope="session")
def no_extensions_config(fixtures_dir):
    """Config with layer missing 3x6_3 extensions"""
    from config_parser import YAMLConfigParser
    config_path = fixtures_dir / "configs" / "minimal_no_extensions.yaml"
    return YAMLConfigParser.parse_keymap(config_path)


@pytest.fixture(scope="session")
def test_board_inventory(fixtures_dir):
    """Test board inventory with 36-key and 42-key boards"""
    from config_parser import YAMLConfigParser
    config_path = fixtures_dir / "configs" / "test_boards.yaml"
    return YAMLConfigParser.parse_boards(config_path)


@pytest.fixture(scope="session")
def reference_keymap_config(fixtures_dir):
    """
    Reference keymap configuration for parity testing.

    This is a FIXED config that exercises all syntax patterns.
    Use this instead of production config for deterministic tests.
    """
    from config_parser import YAMLConfigParser
    config_path = fixtures_dir / "configs" / "reference_keymap.yaml"

    if not config_path.exists():
        pytest.skip(f"Reference config not yet created: {config_path}")

    return YAMLConfigParser.parse_keymap(config_path)


@pytest.fixture(scope="session")
def reference_board_inventory(fixtures_dir):
    """
    Reference board inventory for parity testing.

    Includes QMK and ZMK boards in 36-key and 42-key variants.
    """
    from config_parser import YAMLConfigParser
    config_path = fixtures_dir / "configs" / "reference_boards.yaml"

    if not config_path.exists():
        pytest.skip(f"Reference boards config not yet created: {config_path}")

    return YAMLConfigParser.parse_boards(config_path)


@pytest.fixture(scope="session")
def reference_magic_config(fixtures_dir):
    """Magic key configuration from reference keymap"""
    from config_parser import YAMLConfigParser
    config_path = fixtures_dir / "configs" / "reference_keymap.yaml"

    if not config_path.exists():
        return None

    try:
        return YAMLConfigParser.parse_magic_keys(config_path)
    except Exception:
        return None


# ============================================================================
# Translator Fixtures
# ============================================================================

@pytest.fixture
def qmk_translator(aliases, keycodes):
    """QMK translator instance"""
    from qmk_translator import QMKTranslator
    return QMKTranslator(aliases, keycodes)


@pytest.fixture
def zmk_translator(aliases, keycodes, magic_config):
    """ZMK translator instance"""
    from zmk_translator import ZMKTranslator
    return ZMKTranslator(aliases, keycodes, layout_size="3x5_3", magic_config=magic_config)


@pytest.fixture
def layer_compiler(qmk_translator, zmk_translator):
    """Layer compiler instance with QMK and ZMK translators"""
    from layer_compiler import LayerCompiler
    return LayerCompiler(qmk_translator, zmk_translator)


# ============================================================================
# Generator Fixtures
# ============================================================================

@pytest.fixture
def generator(repo_root):
    """Main keymap generator instance"""
    from generate import KeymapGenerator
    return KeymapGenerator(repo_root, verbose=False)


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers",
        "tier1: Fast regression tests (< 30s)"
    )
    config.addinivalue_line(
        "markers",
        "tier2: Comprehensive E2E tests with compilation (5-15min)"
    )
    config.addinivalue_line(
        "markers",
        "qmk: Requires QMK toolchain"
    )
    config.addinivalue_line(
        "markers",
        "zmk: Requires ZMK toolchain"
    )
    config.addinivalue_line(
        "markers",
        "requires_docker: Requires Docker"
    )
    config.addinivalue_line(
        "markers",
        "requires_qmk_firmware: Requires QMK firmware repository"
    )
    config.addinivalue_line(
        "markers",
        "requires_zmk_firmware: Requires ZMK firmware repository"
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow test (> 30s)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on markers and environment"""

    # Check if we should skip Tier 2
    run_tier2 = config.getoption("--tier2", default=False)
    if not run_tier2:
        tier2_skip = pytest.mark.skip(reason="Tier 2 tests skipped (use --tier2 to run)")
        for item in items:
            if "tier2" in item.keywords:
                item.add_marker(tier2_skip)

    # Check Docker availability
    docker_available = shutil.which("docker") is not None
    if not docker_available:
        docker_skip = pytest.mark.skip(reason="Docker not available")
        for item in items:
            if "requires_docker" in item.keywords:
                item.add_marker(docker_skip)

    # Check QMK firmware
    qmk_firmware = os.environ.get("QMK_FIRMWARE_PATH")
    if not qmk_firmware or not Path(qmk_firmware).exists():
        qmk_skip = pytest.mark.skip(
            reason="QMK firmware not available (set QMK_FIRMWARE_PATH)"
        )
        for item in items:
            if "requires_qmk_firmware" in item.keywords:
                item.add_marker(qmk_skip)

    # Check ZMK firmware
    zmk_repo = os.environ.get("ZMK_REPO")
    if not zmk_repo or not Path(zmk_repo).exists():
        zmk_skip = pytest.mark.skip(
            reason="ZMK firmware not available (set ZMK_REPO)"
        )
        for item in items:
            if "requires_zmk_firmware" in item.keywords:
                item.add_marker(zmk_skip)


def pytest_addoption(parser):
    """Add custom command-line options"""
    parser.addoption(
        "--tier2",
        action="store_true",
        default=False,
        help="Run Tier 2 (slow) tests including firmware compilation"
    )
    parser.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Update golden snapshots"
    )


# ============================================================================
# E2E Test Fixtures (Tier 2)
# ============================================================================

@pytest.fixture(scope="session")
def qmk_firmware_path(tmp_path_factory):
    """
    QMK firmware repository path.
    Uses QMK_FIRMWARE_PATH env var if set, otherwise skips.
    """
    qmk_path = os.environ.get("QMK_FIRMWARE_PATH")
    if qmk_path and Path(qmk_path).exists():
        return Path(qmk_path)
    pytest.skip("QMK firmware not available (set QMK_FIRMWARE_PATH)")


@pytest.fixture
def qmk_build_env(qmk_firmware_path, repo_root):
    """
    QMK build environment with correct environment variables.
    Returns a dict suitable for subprocess.run(env=...) use.
    """
    env = os.environ.copy()
    env["QMK_HOME"] = str(qmk_firmware_path)
    env["QMK_USERSPACE"] = str(repo_root / "qmk")
    return env


@pytest.fixture(scope="session")
def zmk_firmware_path():
    """
    ZMK firmware repository path.
    Uses ZMK_REPO env var if set, otherwise skips.
    """
    zmk_path = os.environ.get("ZMK_REPO")
    if zmk_path and Path(zmk_path).exists():
        return Path(zmk_path)
    pytest.skip("ZMK firmware not available (set ZMK_REPO)")


@pytest.fixture
def docker_available():
    """Check if Docker is available"""
    if not shutil.which("docker"):
        pytest.skip("Docker not available")
    return True
