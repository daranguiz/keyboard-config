# API Contracts

This directory contains interface definitions (contracts) for the unified keymap code generation system.

## Purpose

These interfaces establish clear contracts between components, enabling:
- **Testability**: Mock implementations for unit testing
- **Modularity**: Swap implementations without changing dependents
- **Documentation**: Self-documenting API through type hints
- **Validation**: Type checking via mypy/pylance

## Contracts Defined

### Core Interfaces

1. **`IConfigParser`** - Parse YAML configuration files
   - `parse_keymap()`: Load config/keymap.yaml
   - `parse_boards()`: Load config/boards.yaml
   - `parse_aliases()`: Load config/aliases.yaml

2. **`IKeycodeTranslator`** - Translate unified → firmware syntax
   - `translate()`: Convert single keycode
   - `validate_keybinding()`: Check firmware compatibility

3. **`ILayerCompiler`** - Compile layers with extensions
   - `compile_layer()`: Apply extensions + translate keycodes
   - `get_extension_keys()`: Extract extension keys

4. **`ICodeGenerator`** - Generate firmware files
   - `generate_keymap()`: Create all output files for a board
   - `format_layer_definition()`: Format single layer
   - `generate_visualization()`: Create ASCII art

5. **`IValidator`** - Validate configuration and code
   - `validate_keymap_config()`: Check keymap structure
   - `validate_board_config()`: Check board definitions
   - `validate_generated_code()`: Basic syntax checks

6. **`IFileWriter`** - Write files to disk
   - `write_file()`: Write single file
   - `ensure_directory()`: Create directories
   - `write_all()`: Batch write

7. **`IKeymapGenerator`** - Main orchestrator
   - `generate_all()`: Full pipeline for all boards
   - `generate_for_board()`: Generate single board

8. **`ICLInterface`** - Command-line tool
   - `generate_command()`: Main generate command
   - `validate_command()`: Validate-only mode
   - `add_board_command()`: Add new board

## Data Types

All data types are defined as `@dataclass` for clarity:
- `Layer`: Keyboard layer with core + extensions
- `Board`: Physical keyboard configuration
- `CompiledLayer`: Layer after compilation
- `GeneratedFile`: Output file representation

## Usage in Implementation

```python
# Implementation classes implement the interfaces
class QMKTranslator(IKeycodeTranslator):
    def translate(self, unified_keycode: str) -> str:
        # Implementation here
        pass

# Testing with mocks
class MockTranslator(IKeycodeTranslator):
    def translate(self, unified_keycode: str) -> str:
        return f"MOCK_{unified_keycode}"
```

## Validation

Type checking can be enforced using mypy:
```bash
mypy scripts/ --strict
```

## Next Steps

After contracts are defined:
1. Implement concrete classes (scripts/*)
2. Write unit tests (tests/*)
3. Integration tests (end-to-end generation)
