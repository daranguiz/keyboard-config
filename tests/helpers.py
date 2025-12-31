#!/usr/bin/env python3
"""
Test helper functions for keyboard-config tests.

Provides utilities for:
- File existence assertions
- Syntax validation (C, devicetree)
- File comparison (semantic diffs)
- Pattern counting
"""

import subprocess
from pathlib import Path
from typing import Optional, List
import difflib


def assert_file_exists(path: Path, message: str = None):
    """
    Assert that a file exists with a helpful error message.

    Args:
        path: Path to check
        message: Optional custom error message

    Raises:
        AssertionError: If file doesn't exist
    """
    if not path.exists():
        msg = message or f"Expected file not found: {path}"
        raise AssertionError(msg)


def assert_valid_c_syntax(c_file: Path):
    """
    Validate C file syntax using gcc.

    Args:
        c_file: Path to C file to validate

    Raises:
        AssertionError: If syntax is invalid
    """
    result = subprocess.run(
        ["gcc", "-fsyntax-only", "-std=c11", str(c_file)],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Invalid C syntax in {c_file}:\n{result.stderr}"
        )


def compare_files_semantic(
    generated: Path,
    golden: Path,
    ignore_whitespace: bool = True
) -> Optional[str]:
    """
    Compare files with semantic diffing, return diff if different.

    Args:
        generated: Path to generated file
        golden: Path to golden file
        ignore_whitespace: If True, normalize whitespace before comparing

    Returns:
        None if files match, unified diff string if different
    """
    with open(generated) as f1, open(golden) as f2:
        gen_lines = f1.readlines()
        gold_lines = f2.readlines()

    # Optionally normalize whitespace
    if ignore_whitespace:
        gen_normalized = [line.strip() for line in gen_lines if line.strip()]
        gold_normalized = [line.strip() for line in gold_lines if line.strip()]
    else:
        gen_normalized = gen_lines
        gold_normalized = gold_lines

    if gen_normalized == gold_normalized:
        return None

    # Generate unified diff
    diff = difflib.unified_diff(
        gold_normalized,
        gen_normalized,
        fromfile=str(golden),
        tofile=str(generated),
        lineterm=''
    )
    return '\n'.join(diff)


def count_occurrences(text: str, pattern: str) -> int:
    """
    Count occurrences of pattern in text.

    Args:
        text: Text to search
        pattern: Pattern to count

    Returns:
        Number of occurrences
    """
    return text.count(pattern)


def count_occurrences_in_file(file_path: Path, pattern: str) -> int:
    """
    Count occurrences of pattern in a file.

    Args:
        file_path: Path to file
        pattern: Pattern to count

    Returns:
        Number of occurrences
    """
    with open(file_path) as f:
        content = f.read()
    return count_occurrences(content, pattern)


def assert_contains(text: str, pattern: str, message: str = None):
    """
    Assert that text contains pattern.

    Args:
        text: Text to search
        pattern: Pattern to find
        message: Optional custom error message

    Raises:
        AssertionError: If pattern not found
    """
    if pattern not in text:
        msg = message or f"Pattern '{pattern}' not found in text"
        raise AssertionError(msg)


def assert_not_contains(text: str, pattern: str, message: str = None):
    """
    Assert that text does NOT contain pattern.

    Args:
        text: Text to search
        pattern: Pattern that should not be present
        message: Optional custom error message

    Raises:
        AssertionError: If pattern is found
    """
    if pattern in text:
        msg = message or f"Pattern '{pattern}' should not be in text"
        raise AssertionError(msg)


def get_layers_from_keymap_c(keymap_c_path: Path) -> List[str]:
    """
    Extract layer names from QMK keymap.c file.

    Args:
        keymap_c_path: Path to keymap.c

    Returns:
        List of layer names found in enum or layer definitions
    """
    with open(keymap_c_path) as f:
        content = f.read()

    # Look for layer enum or [LAYER_NAME] = { patterns
    import re
    layer_pattern = r'\[([A-Z_]+)\]\s*='
    matches = re.findall(layer_pattern, content)
    return list(dict.fromkeys(matches))  # Remove duplicates while preserving order


def get_combos_from_keymap_c(keymap_c_path: Path) -> List[str]:
    """
    Extract combo names from QMK keymap.c file.

    Args:
        keymap_c_path: Path to keymap.c

    Returns:
        List of combo names (from enum or combo definitions)
    """
    with open(keymap_c_path) as f:
        content = f.read()

    # Look for COMBO_ or MACRO_ definitions
    import re
    combo_pattern = r'(COMBO_\w+|MACRO_\w+)'
    matches = re.findall(combo_pattern, content)
    return list(dict.fromkeys(matches))


def assert_auto_generated_warning(file_path: Path):
    """
    Assert that file contains AUTO-GENERATED warning.

    Args:
        file_path: Path to file to check

    Raises:
        AssertionError: If warning not found
    """
    with open(file_path) as f:
        content = f.read()

    if "AUTO-GENERATED" not in content:
        raise AssertionError(
            f"File {file_path} missing AUTO-GENERATED warning"
        )


def get_file_line_count(file_path: Path) -> int:
    """
    Get number of lines in a file.

    Args:
        file_path: Path to file

    Returns:
        Number of lines
    """
    with open(file_path) as f:
        return len(f.readlines())
