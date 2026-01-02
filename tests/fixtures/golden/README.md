# Golden Files for Regression Testing

This directory contains "golden" (expected) output files for regression testing.

## Purpose

Golden files are manually verified outputs that serve as the baseline for comparison.
When the generator produces output, we compare against these files to detect unintended changes.

## Structure

```
golden/
├── qmk/
│   └── reference_keymap.c    # Expected QMK keymap.c for reference config
└── zmk/
    └── reference.keymap      # Expected ZMK .keymap for reference config
```

## Updating Golden Files

When output format **intentionally** changes:

1. Review the changes carefully
2. Run the generator with reference config
3. Verify the new output is correct
4. Copy to this directory
5. Commit with a message explaining the change

```bash
# Regenerate and update (after verifying changes are correct):
pytest tests/integration/test_reference_golden.py --snapshot-update
```

## DO NOT

- Update golden files without understanding why output changed
- Commit golden file updates without reviewing the diff
- Auto-generate golden files without manual verification
