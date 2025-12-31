#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
MODE="tier1"
COVERAGE=false
VERBOSE=false
MARKER=""
TEST_PATH=""
UPDATE_SNAPSHOTS=false
FAIL_UNDER=80

# Help text
show_help() {
    cat << EOF
${BLUE}Test Runner for keyboard-config${NC}

Usage: $0 [OPTIONS]

${YELLOW}Test Modes:${NC}
  -1, --tier1           Run Tier 1 tests only (fast, < 2 min) [default]
  -2, --tier2           Run Tier 2 tests only (E2E, 15-30 min)
  -a, --all             Run all tests (Tier 1 + Tier 2)

${YELLOW}Coverage Options:${NC}
  -c, --coverage        Run with coverage report
  --cov-html            Generate HTML coverage report (opens in browser)
  --fail-under N        Fail if coverage < N% (default: 80)

${YELLOW}Test Selection:${NC}
  -m, --marker MARKER   Run tests with specific marker (tier1, tier2, qmk, zmk, etc.)
  -t, --test PATH       Run specific test file or directory
  -u, --update-snapshots Update golden snapshot files

${YELLOW}Output Options:${NC}
  -v, --verbose         Verbose output (show all test details)
  -q, --quiet           Quiet output (minimal)
  -s, --show            Show print statements (don't capture)

${YELLOW}Utility:${NC}
  -h, --help            Show this help message
  --list-markers        List all available pytest markers
  --check-env           Check environment setup for Tier 2 tests

${YELLOW}Examples:${NC}
  $0                                    # Run Tier 1 tests
  $0 --tier2                            # Run Tier 2 E2E tests
  $0 --all --coverage                   # Run all tests with coverage
  $0 --marker qmk --verbose             # Run QMK-related tests with verbose output
  $0 --test tests/unit/test_validator.py  # Run specific test file
  $0 --coverage --cov-html              # Generate and open HTML coverage report
  $0 --update-snapshots                 # Update golden snapshot files

${YELLOW}Environment Variables (for Tier 2):${NC}
  QMK_FIRMWARE_PATH     Path to QMK firmware repository
  QMK_USERSPACE         Path to QMK userspace (usually: \$(realpath qmk))
  ZMK_REPO              Path to ZMK firmware repository

EOF
}

# Check environment for Tier 2 tests
check_env() {
    echo -e "${BLUE}Checking environment for Tier 2 tests...${NC}\n"

    local all_good=true

    # Check QMK
    if [ -n "$QMK_FIRMWARE_PATH" ] && [ -d "$QMK_FIRMWARE_PATH" ]; then
        echo -e "${GREEN}✓${NC} QMK_FIRMWARE_PATH: $QMK_FIRMWARE_PATH"
    else
        echo -e "${RED}✗${NC} QMK_FIRMWARE_PATH: Not set or invalid"
        all_good=false
    fi

    if [ -n "$QMK_USERSPACE" ] && [ -d "$QMK_USERSPACE" ]; then
        echo -e "${GREEN}✓${NC} QMK_USERSPACE: $QMK_USERSPACE"
    else
        echo -e "${RED}✗${NC} QMK_USERSPACE: Not set or invalid"
        all_good=false
    fi

    # Check QMK toolchains
    if command -v qmk &> /dev/null; then
        echo -e "${GREEN}✓${NC} qmk CLI installed: $(qmk --version 2>/dev/null || echo 'version unknown')"
    else
        echo -e "${RED}✗${NC} qmk CLI not found"
        all_good=false
    fi

    if command -v avr-gcc &> /dev/null; then
        echo -e "${GREEN}✓${NC} avr-gcc installed: $(avr-gcc --version | head -n1)"
    else
        echo -e "${YELLOW}⚠${NC} avr-gcc not found (needed for AVR boards)"
    fi

    if command -v arm-none-eabi-gcc &> /dev/null; then
        echo -e "${GREEN}✓${NC} arm-none-eabi-gcc installed: $(arm-none-eabi-gcc --version | head -n1)"
    else
        echo -e "${YELLOW}⚠${NC} arm-none-eabi-gcc not found (needed for ARM boards)"
    fi

    # Check ZMK
    if [ -n "$ZMK_REPO" ] && [ -d "$ZMK_REPO" ]; then
        echo -e "${GREEN}✓${NC} ZMK_REPO: $ZMK_REPO"
    else
        echo -e "${RED}✗${NC} ZMK_REPO: Not set or invalid"
        all_good=false
    fi

    # Check Docker
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            echo -e "${GREEN}✓${NC} Docker installed and running"
        else
            echo -e "${YELLOW}⚠${NC} Docker installed but not running"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Docker not found (needed for ZMK builds)"
    fi

    # Check west
    if command -v west &> /dev/null; then
        echo -e "${GREEN}✓${NC} west toolchain installed (alternative to Docker for ZMK)"
    else
        echo -e "${YELLOW}⚠${NC} west not found (alternative to Docker for ZMK builds)"
    fi

    # Check pytest
    if command -v pytest &> /dev/null; then
        echo -e "${GREEN}✓${NC} pytest installed: $(pytest --version 2>&1 | head -n1)"
    else
        echo -e "${RED}✗${NC} pytest not found"
        all_good=false
    fi

    echo ""
    if [ "$all_good" = true ]; then
        echo -e "${GREEN}Environment looks good for Tier 2 tests!${NC}"
        return 0
    else
        echo -e "${RED}Some required components are missing.${NC}"
        echo -e "See tests/README.md for setup instructions."
        return 1
    fi
}

# List pytest markers
list_markers() {
    echo -e "${BLUE}Available pytest markers:${NC}\n"
    pytest --markers 2>/dev/null | grep "^@pytest.mark" || echo "Run 'pytest --markers' for full list"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -1|--tier1)
            MODE="tier1"
            shift
            ;;
        -2|--tier2)
            MODE="tier2"
            shift
            ;;
        -a|--all)
            MODE="all"
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        --cov-html)
            COVERAGE=true
            COV_HTML=true
            shift
            ;;
        --fail-under)
            FAIL_UNDER="$2"
            shift 2
            ;;
        -m|--marker)
            MARKER="$2"
            shift 2
            ;;
        -t|--test)
            TEST_PATH="$2"
            shift 2
            ;;
        -u|--update-snapshots)
            UPDATE_SNAPSHOTS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -s|--show)
            SHOW_OUTPUT=true
            shift
            ;;
        --check-env)
            check_env
            exit $?
            ;;
        --list-markers)
            list_markers
            exit 0
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
cd "$SCRIPT_DIR"

PYTEST_ARGS=()

# Add test path or default based on mode
if [ -n "$TEST_PATH" ]; then
    PYTEST_ARGS+=("$TEST_PATH")
elif [ "$UPDATE_SNAPSHOTS" = true ]; then
    PYTEST_ARGS+=("tests/integration/test_golden_snapshots.py")
else
    PYTEST_ARGS+=("tests/")
fi

# Add marker based on mode
if [ -n "$MARKER" ]; then
    PYTEST_ARGS+=("-m" "$MARKER")
elif [ "$MODE" = "tier1" ]; then
    PYTEST_ARGS+=("-m" "tier1")
elif [ "$MODE" = "tier2" ]; then
    PYTEST_ARGS+=("-m" "tier2")
fi
# For "all" mode, don't add marker (runs everything)

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-vv")
elif [ "$QUIET" = true ]; then
    PYTEST_ARGS+=("-q")
else
    PYTEST_ARGS+=("-v")
fi

# Add output capture
if [ "$SHOW_OUTPUT" = true ]; then
    PYTEST_ARGS+=("-s")
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS+=("--cov=scripts")
    PYTEST_ARGS+=("--cov-report=term")
    if [ "$COV_HTML" = true ]; then
        PYTEST_ARGS+=("--cov-report=html")
    fi
    PYTEST_ARGS+=("--cov-fail-under=$FAIL_UNDER")
fi

# Add snapshot update
if [ "$UPDATE_SNAPSHOTS" = true ]; then
    PYTEST_ARGS+=("--snapshot-update")
fi

# Print what we're doing
echo -e "${BLUE}Running tests...${NC}"
echo -e "Mode: ${YELLOW}$MODE${NC}"
if [ "$COVERAGE" = true ]; then
    echo -e "Coverage: ${YELLOW}enabled (fail-under: $FAIL_UNDER%)${NC}"
fi
if [ -n "$MARKER" ]; then
    echo -e "Marker: ${YELLOW}$MARKER${NC}"
fi
if [ -n "$TEST_PATH" ]; then
    echo -e "Path: ${YELLOW}$TEST_PATH${NC}"
fi
echo ""

# Run pytest
set +e
pytest "${PYTEST_ARGS[@]}"
EXIT_CODE=$?
set -e

# Open coverage report if requested
if [ "$COV_HTML" = true ] && [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Opening coverage report...${NC}"
    if command -v open &> /dev/null; then
        open htmlcov/index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    else
        echo -e "${YELLOW}Coverage report generated at: htmlcov/index.html${NC}"
    fi
fi

# Summary
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
fi

exit $EXIT_CODE
