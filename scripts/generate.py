#!/usr/bin/env python3
"""
Main entry point for unified keymap code generation

This script generates QMK and ZMK keymaps from unified YAML configuration.

Usage:
    python3 scripts/generate.py [--board BOARD_ID] [--validate-only]

Examples:
    # Generate for all boards
    python3 scripts/generate.py

    # Generate for specific board
    python3 scripts/generate.py --board skeletyl

    # Validate configuration without generating
    python3 scripts/generate.py --validate-only
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config_parser import YAMLConfigParser
from data_model import ValidationError
from qmk_translator import QMKTranslator
from zmk_translator import ZMKTranslator
from layer_compiler import LayerCompiler
from qmk_generator import QMKGenerator
from zmk_generator import ZMKGenerator
from file_writer import FileSystemWriter
from validator import ConfigValidator
from visualizer import KeymapVisualizer


class KeymapGenerator:
    """Main generator orchestrator"""

    def __init__(self, repo_root: Path):
        """
        Initialize generator

        Args:
            repo_root: Repository root directory
        """
        self.repo_root = repo_root
        self.config_dir = repo_root / "config"

        # Parse configuration
        print("📖 Parsing configuration...")
        self.keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )
        self.board_inventory = YAMLConfigParser.parse_boards(
            self.config_dir / "boards.yaml"
        )
        self.aliases = YAMLConfigParser.parse_aliases(
            self.config_dir / "aliases.yaml"
        )
        self.special_keycodes = YAMLConfigParser.parse_special_keycodes(
            self.config_dir / "aliases.yaml"
        )

        print(f"✅ Loaded {len(self.keymap_config.layers)} layers, "
              f"{len(self.board_inventory.boards)} boards")

        # Validate configuration
        print("🔍 Validating configuration...")
        validator = ConfigValidator()
        validator.validate_keymap_config(self.keymap_config.layers)
        validator.validate_board_config(list(self.board_inventory.boards.values()))
        print("✅ Configuration is valid")

        # Initialize translators
        self.qmk_translator = QMKTranslator(self.aliases, self.special_keycodes)
        self.zmk_translator = ZMKTranslator(self.aliases, self.special_keycodes)

        # Set layer indices for ZMK translator
        layer_names = list(self.keymap_config.layers.keys())
        self.zmk_translator.set_layer_indices(layer_names)

        # Initialize compiler
        self.compiler = LayerCompiler(self.qmk_translator, self.zmk_translator)

    def generate_for_board(self, board_id: str) -> bool:
        """
        Generate keymap for a specific board

        Args:
            board_id: Board identifier

        Returns:
            True if successful, False otherwise
        """
        board = self.board_inventory.get_by_id(board_id)
        if not board:
            print(f"❌ Board '{board_id}' not found in config/boards.yaml")
            return False

        print(f"\n🔨 Generating keymap for {board.name}...")

        try:
            # Compile all layers for this board
            compiled_layers = []
            for layer in self.keymap_config.layers.values():
                # Check if this is a board-specific layer
                # If the layer has full_layout, it's only for boards with extra_layers
                if layer.full_layout is not None:
                    # Skip if board doesn't explicitly request this layer
                    if layer.name not in board.extra_layers:
                        continue

                compiled_layer = self.compiler.compile_layer(
                    layer, board, board.firmware
                )
                compiled_layers.append(compiled_layer)

            # Generate files based on firmware
            if board.firmware == "qmk":
                self._generate_qmk(board, compiled_layers)
            elif board.firmware == "zmk":
                self._generate_zmk(board, compiled_layers)
            else:
                print(f"❌ Unknown firmware: {board.firmware}")
                return False

            print(f"✅ Generated keymap for {board.name}")
            return True

        except ValidationError as e:
            print(f"❌ Validation error for {board.name}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error generating keymap for {board.name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _generate_qmk(self, board, compiled_layers):
        """Generate QMK keymap files"""
        generator = QMKGenerator()
        output_dir = self.repo_root / board.get_output_directory()

        # Generate all files
        files = generator.generate_keymap(board, compiled_layers, output_dir)

        # Write files
        FileSystemWriter.write_all(output_dir, files)

        print(f"  📝 Wrote {len(files)} files to {output_dir}")

    def _generate_zmk(self, board, compiled_layers):
        """Generate ZMK keymap files"""
        generator = ZMKGenerator()
        output_dir = self.repo_root / board.get_output_directory()

        # Generate keymap file
        keymap_content = generator.generate_keymap(board, compiled_layers)
        visualization = generator.generate_visualization(board, compiled_layers)

        # Prepare files to write
        files = {
            f"{board.zmk_shield}.keymap": keymap_content,
            "README.md": f"# {board.name} - ZMK Keymap\n\n{visualization}"
        }

        # Write files
        FileSystemWriter.write_all(output_dir, files)

        print(f"  📝 Wrote {len(files)} files to {output_dir}")

    def generate_all(self) -> int:
        """
        Generate keymaps for all boards

        Returns:
            0 if successful, 1 if any errors
        """
        success_count = 0
        failure_count = 0
        compiled_layers_by_board = {}  # Store compiled layers for visualization

        for board_id in self.board_inventory.boards.keys():
            board = self.board_inventory.boards[board_id]

            # Compile layers for this board
            compiled_layers = []
            for layer in self.keymap_config.layers.values():
                # If the layer has full_layout, it's only for boards with extra_layers
                if layer.full_layout is not None:
                    # Skip if board doesn't explicitly request this layer
                    if layer.name not in board.extra_layers:
                        continue

                compiled_layer = self.compiler.compile_layer(
                    layer, board, board.firmware
                )
                compiled_layers.append(compiled_layer)

            # Store for visualization
            compiled_layers_by_board[board_id] = compiled_layers

            # Generate keymap files
            if self.generate_for_board(board_id):
                success_count += 1
            else:
                failure_count += 1

        print(f"\n{'='*60}")
        print(f"✅ Successfully generated: {success_count} boards")
        if failure_count > 0:
            print(f"❌ Failed: {failure_count} boards")
        print(f"{'='*60}")

        # Generate visualizations for all boards
        print(f"\n📊 Generating keymap visualizations...")
        visualizer = KeymapVisualizer(self.repo_root)

        if visualizer.is_available():
            viz_results = visualizer.generate_all(self.board_inventory, compiled_layers_by_board)
            viz_success = sum(1 for path in viz_results.values() if path is not None)

            if viz_success > 0:
                print(f"✅ Generated {viz_success} visualizations in docs/keymaps/")
            else:
                print(f"⚠️  No visualizations generated")
        else:
            print(f"⚠️  keymap-drawer not available, skipping visualization")

        return 0 if failure_count == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate QMK and ZMK keymaps from unified YAML configuration"
    )
    parser.add_argument(
        "--board",
        help="Generate for specific board only",
        metavar="BOARD_ID"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate configuration without generating files"
    )

    args = parser.parse_args()

    # Determine repository root
    repo_root = Path(__file__).parent.parent

    try:
        # Initialize generator (this validates configuration)
        generator = KeymapGenerator(repo_root)

        if args.validate_only:
            print("\n✅ Configuration is valid!")
            return 0

        # Generate keymaps
        if args.board:
            success = generator.generate_for_board(args.board)
            return 0 if success else 1
        else:
            return generator.generate_all()

    except ValidationError as e:
        print(f"\n❌ Configuration error: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
