"""
API Contract: Generator Interface

Defines the core interfaces for the unified keymap code generation system.
These interfaces establish contracts between components and enable testing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Literal
from pathlib import Path


# ============================================================================
# Data Types (from data-model.md)
# ============================================================================

@dataclass
class KeyGrid:
    """Represents a grid of keys as nested lists"""
    rows: List[List[str]]

    def flatten(self) -> List[str]:
        """Flatten to single list of keycodes"""
        return [key for row in self.rows for key in row]


@dataclass
class LayerExtension:
    """Additional keys for boards larger than 36-key"""
    extension_type: str
    keys: Dict[str, str | List[str]]


@dataclass
class Layer:
    """Single keyboard layer (e.g., BASE, NAV, NUM)"""
    name: str
    core: KeyGrid
    extensions: Dict[str, LayerExtension]


@dataclass
class Board:
    """Physical keyboard configuration"""
    id: str
    name: str
    firmware: Literal["qmk", "zmk"]
    layout_size: str
    extensions: List[str]
    features: List[str]
    extra_layers: List[str]
    status: str

    # Firmware-specific
    qmk_keyboard: Optional[str] = None
    zmk_shield: Optional[str] = None


@dataclass
class CompiledLayer:
    """Layer after extensions applied and keycodes translated"""
    name: str
    board: Board
    keycodes: List[str]
    firmware: Literal["qmk", "zmk"]


@dataclass
class GeneratedFile:
    """Represents a generated output file"""
    path: Path
    content: str
    should_overwrite: bool = True


# ============================================================================
# Parser Interface
# ============================================================================

class IConfigParser(ABC):
    """
    Interface for parsing YAML configuration files.

    Implementations:
    - YAMLConfigParser: Parse config/keymap.yaml and config/boards.yaml
    """

    @abstractmethod
    def parse_keymap(self, yaml_path: Path) -> Dict[str, Layer]:
        """
        Parse keymap.yaml and return dictionary of layers.

        Args:
            yaml_path: Path to config/keymap.yaml

        Returns:
            Dict[layer_name, Layer] - All defined layers

        Raises:
            ValidationError: If YAML is malformed or invalid
        """
        pass

    @abstractmethod
    def parse_boards(self, yaml_path: Path) -> List[Board]:
        """
        Parse boards.yaml and return list of board configurations.

        Args:
            yaml_path: Path to config/boards.yaml

        Returns:
            List[Board] - All defined boards

        Raises:
            ValidationError: If YAML is malformed or invalid
        """
        pass

    @abstractmethod
    def parse_aliases(self, yaml_path: Path) -> Dict[str, "BehaviorAlias"]:
        """
        Parse aliases.yaml and return behavior alias definitions.

        Args:
            yaml_path: Path to config/aliases.yaml

        Returns:
            Dict[alias_name, BehaviorAlias] - All defined aliases

        Raises:
            ValidationError: If YAML is malformed or invalid
        """
        pass


# ============================================================================
# Keycode Translator Interface
# ============================================================================

class IKeycodeTranslator(ABC):
    """
    Interface for translating unified keycode syntax to firmware-specific syntax.

    Implementations:
    - QMKTranslator: Translate to QMK C syntax
    - ZMKTranslator: Translate to ZMK devicetree syntax
    """

    @abstractmethod
    def translate(self, unified_keycode: str) -> str:
        """
        Translate a single unified keycode to firmware-specific syntax.

        Args:
            unified_keycode: Unified format (e.g., "hrm:LGUI:A", "lt:NAV:SPC", "KC_Q")

        Returns:
            Firmware-specific keycode string
            - QMK: "LGUI_T(KC_A)", "LT(NAV, KC_SPC)", "KC_Q"
            - ZMK: "&hrm LGUI A", "&lt NAV SPC", "&kp Q"

        Examples:
            QMK:
                translate("hrm:LGUI:A") -> "LGUI_T(KC_A)"
                translate("bt:next") -> "KC_NO"  # Bluetooth filtered

            ZMK:
                translate("hrm:LGUI:A") -> "&hrm LGUI A"
                translate("bt:next") -> "&bt BT_NXT"
        """
        pass

    @abstractmethod
    def validate_keybinding(self, unified_keycode: str) -> None:
        """
        Validate that a keybinding is supported by this firmware.

        For simple keycodes: Silent filtering (no error)
        For complex keybindings (hrm, lt): Strict validation (raise error if unsupported)

        Args:
            unified_keycode: Unified format keycode

        Raises:
            ValidationError: If complex keybinding uses unsupported firmware features (FR-007)

        Examples:
            QMK validator:
                validate_keybinding("bt:next")  # No error (simple keycode, silently filtered)
                validate_keybinding("hrm:LGUI:A")  # No error (supported)

            ZMK validator:
                validate_keybinding("rgb:toggle")  # No error (simple, silently filtered)
                validate_keybinding("hrm:LGUI:A")  # No error (supported)
        """
        pass


# ============================================================================
# Layer Compiler Interface
# ============================================================================

class ILayerCompiler(ABC):
    """
    Interface for compiling layers with extensions applied.

    Implementation:
    - LayerCompiler: Apply board extensions and translate keycodes
    """

    @abstractmethod
    def compile_layer(
        self,
        layer: Layer,
        board: Board,
        translator: IKeycodeTranslator
    ) -> CompiledLayer:
        """
        Compile a layer for a specific board by applying extensions and translating keycodes.

        Process:
        1. Start with layer.core (36 keys)
        2. Apply extensions from board.extensions
        3. Translate all keycodes using translator
        4. Validate complex keybindings (FR-007)

        Args:
            layer: Layer definition with core + extensions
            board: Target board configuration
            translator: Firmware-specific keycode translator

        Returns:
            CompiledLayer with translated keycodes ready for code generation

        Raises:
            ValidationError: If extension compilation fails or keybinding validation fails
        """
        pass

    @abstractmethod
    def get_extension_keys(
        self,
        layer: Layer,
        extension_type: str,
        board: Board
    ) -> List[str]:
        """
        Extract keys from a layer extension for a specific board.

        Args:
            layer: Layer with extensions
            extension_type: Extension identifier (e.g., "3x6_3")
            board: Target board

        Returns:
            List of keycode strings for the extension

        Raises:
            ValidationError: If extension_type not found in layer
        """
        pass


# ============================================================================
# Code Generator Interface
# ============================================================================

class ICodeGenerator(ABC):
    """
    Interface for generating firmware-specific keymap files.

    Implementations:
    - QMKGenerator: Generate QMK C/header files
    - ZMKGenerator: Generate ZMK devicetree files
    """

    @abstractmethod
    def generate_keymap(
        self,
        board: Board,
        compiled_layers: List[CompiledLayer]
    ) -> List[GeneratedFile]:
        """
        Generate firmware keymap files for a board.

        Args:
            board: Board configuration
            compiled_layers: All layers compiled for this board

        Returns:
            List of GeneratedFile objects to write to disk

        QMK Output:
            - keymap.c: Layer definitions
            - config.h: Layer enums and includes
            - rules.mk: Build rules
            - README.md: ASCII visualization

        ZMK Output:
            - <shield>.keymap: Devicetree keymap
            - <shield>.conf: Configuration
            - README.md: Visualization
        """
        pass

    @abstractmethod
    def format_layer_definition(self, layer: CompiledLayer) -> str:
        """
        Format a single layer as firmware-specific code.

        Args:
            layer: Compiled layer with translated keycodes

        Returns:
            Formatted layer definition string

        QMK:
            Returns "[BASE] = LAYOUT_split_3x5_3(\n    KC_Q, KC_W, ...\n)"

        ZMK:
            Returns "base_layer {\n    bindings = <\n        &kp Q &kp W ...\n    >;\n}"
        """
        pass

    @abstractmethod
    def generate_visualization(self, compiled_layers: List[CompiledLayer]) -> str:
        """
        Generate ASCII art visualization of layers.

        Args:
            compiled_layers: All layers to visualize

        Returns:
            Multi-line ASCII art string showing all layers

        Example output:
            ```
            Layer: BASE
            ┌─────┬─────┬─────┬─────┬─────┐
            │  Q  │  W  │  F  │  P  │  G  │
            ├─────┼─────┼─────┼─────┼─────┤
            │GUI/A│ALT/R│CTL/S│SFT/T│  D  │
            ...
            ```
        """
        pass


# ============================================================================
# File Writer Interface
# ============================================================================

class IFileWriter(ABC):
    """
    Interface for writing generated files to disk.

    Implementation:
    - FileSystemWriter: Write to actual filesystem
    - MockFileWriter: In-memory storage for testing
    """

    @abstractmethod
    def write_file(self, generated_file: GeneratedFile) -> None:
        """
        Write a generated file to disk.

        Args:
            generated_file: File to write with path and content

        Raises:
            IOError: If file cannot be written
        """
        pass

    @abstractmethod
    def ensure_directory(self, directory: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path to create

        Raises:
            IOError: If directory cannot be created
        """
        pass

    @abstractmethod
    def write_all(self, generated_files: List[GeneratedFile]) -> None:
        """
        Write multiple generated files to disk.

        Args:
            generated_files: List of files to write

        Raises:
            IOError: If any file cannot be written
        """
        pass


# ============================================================================
# Validator Interface
# ============================================================================

class IValidator(ABC):
    """
    Interface for validating configuration and generated code.

    Implementation:
    - ConfigValidator: Validate YAML schemas and business logic
    - CodeValidator: Validate generated code syntax
    """

    @abstractmethod
    def validate_keymap_config(self, layers: Dict[str, Layer]) -> None:
        """
        Validate keymap configuration.

        Checks:
        - At least one layer defined
        - BASE layer exists
        - Layer names are valid C identifiers
        - Core layouts have exactly 36 keys

        Args:
            layers: Dict of layer definitions

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_board_config(self, boards: List[Board], layers: Dict[str, Layer]) -> None:
        """
        Validate board configuration.

        Checks:
        - Unique board IDs
        - Required firmware-specific fields present
        - Referenced extensions exist in layers
        - Features are valid for firmware type

        Args:
            boards: List of board configurations
            layers: Dict of layer definitions (to validate extension references)

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def validate_generated_code(self, generated_file: GeneratedFile) -> None:
        """
        Validate generated code syntax.

        QMK: Basic C syntax checks
        ZMK: Basic devicetree syntax checks

        Args:
            generated_file: Generated file to validate

        Raises:
            ValidationError: If syntax is invalid
        """
        pass


# ============================================================================
# Main Orchestrator Interface
# ============================================================================

class IKeymapGenerator(ABC):
    """
    Main orchestrator interface for the entire generation pipeline.

    Implementation:
    - KeymapGenerator: Coordinates all components
    """

    @abstractmethod
    def generate_all(
        self,
        config_dir: Path,
        output_dir: Path,
        boards_filter: Optional[List[str]] = None
    ) -> None:
        """
        Generate keymaps for all boards (or filtered subset).

        Pipeline:
        1. Parse configuration files (keymap.yaml, boards.yaml, aliases.yaml)
        2. Validate configuration
        3. For each board:
           a. Select appropriate translator (QMK/ZMK)
           b. Compile all layers with extensions
           c. Generate firmware files
           d. Write files to disk
           e. Generate visualizations

        Args:
            config_dir: Directory containing config/*.yaml files
            output_dir: Root output directory (contains qmk/, zmk/)
            boards_filter: Optional list of board IDs to generate (None = all)

        Raises:
            ValidationError: If configuration is invalid
            GenerationError: If code generation fails
        """
        pass

    @abstractmethod
    def generate_for_board(
        self,
        board_id: str,
        config_dir: Path,
        output_dir: Path
    ) -> None:
        """
        Generate keymap for a single board.

        Args:
            board_id: Board identifier (e.g., "skeletyl")
            config_dir: Directory containing config/*.yaml files
            output_dir: Root output directory

        Raises:
            ValidationError: If board not found or configuration invalid
            GenerationError: If code generation fails
        """
        pass


# ============================================================================
# CLI Interface
# ============================================================================

class ICLInterface(ABC):
    """
    Interface for command-line tool.

    Implementation:
    - GeneratorCLI: Main CLI entrypoint
    """

    @abstractmethod
    def generate_command(
        self,
        boards: Optional[List[str]] = None,
        config_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        verbose: bool = False
    ) -> int:
        """
        Main generate command.

        Args:
            boards: Optional list of board IDs to generate
            config_dir: Override default config directory
            output_dir: Override default output directory
            verbose: Enable verbose logging

        Returns:
            Exit code (0 = success, non-zero = error)
        """
        pass

    @abstractmethod
    def validate_command(
        self,
        config_dir: Optional[Path] = None
    ) -> int:
        """
        Validate configuration without generating code.

        Args:
            config_dir: Override default config directory

        Returns:
            Exit code (0 = valid, non-zero = validation errors)
        """
        pass

    @abstractmethod
    def add_board_command(
        self,
        board_id: str,
        firmware: Literal["qmk", "zmk"],
        keyboard: str,
        layout_size: str = "3x5_3"
    ) -> int:
        """
        Add a new board to boards.yaml.

        Args:
            board_id: Unique board identifier
            firmware: Target firmware (qmk or zmk)
            keyboard: QMK keyboard path or ZMK shield name
            layout_size: Base layout size (default: 3x5_3)

        Returns:
            Exit code (0 = success, non-zero = error)
        """
        pass


# ============================================================================
# Exceptions
# ============================================================================

class ValidationError(Exception):
    """Raised when configuration or code validation fails"""
    pass


class GenerationError(Exception):
    """Raised when code generation fails"""
    pass


class ParseError(Exception):
    """Raised when YAML parsing fails"""
    pass
