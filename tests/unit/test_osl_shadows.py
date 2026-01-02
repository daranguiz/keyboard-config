#!/usr/bin/env python3
"""
Unit tests for auto-generated OSL shadow layers
"""

import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from data_model import KeyGrid, Layer, KeymapConfiguration, ValidationError
from generate import apply_osl_shadows


def _blank_core_rows():
    return [
        ["NONE"] * 5,
        ["NONE"] * 5,
        ["NONE"] * 5,
        ["NONE"] * 5,
        ["NONE"] * 5,
        ["NONE"] * 5,
        ["NONE"] * 3,
        ["NONE"] * 3,
    ]


def _make_layer(name: str, keycode: str = None) -> Layer:
    rows = _blank_core_rows()
    if keycode is not None:
        rows[0][0] = keycode
    return Layer(name=name, core=KeyGrid(rows=rows))


@pytest.mark.tier1
def test_osl_shadow_created_and_rewritten():
    layers = {
        "BASE": _make_layer("BASE"),
        "SYM": _make_layer("SYM"),
        "NUM": _make_layer("NUM", "osl:SYM"),
    }
    original = KeymapConfiguration(layers=layers)

    updated = apply_osl_shadows(original)

    assert "SYM_SHADOW" in updated.layers
    assert updated.layers["NUM"].core.rows[0][0] == "osl:SYM_SHADOW"
    assert updated.layers["SYM"].core.rows[0][0] == "NONE"

    # Original config should not be mutated
    assert original.layers["NUM"].core.rows[0][0] == "osl:SYM"


@pytest.mark.tier1
def test_osl_missing_target_raises():
    layers = {
        "BASE": _make_layer("BASE"),
        "NUM": _make_layer("NUM", "osl:DOES_NOT_EXIST"),
    }
    original = KeymapConfiguration(layers=layers)

    with pytest.raises(ValidationError):
        apply_osl_shadows(original)
