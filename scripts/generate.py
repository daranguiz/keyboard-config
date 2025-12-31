#!/usr/bin/env python3
"""
Main entry point for unified keymap code generation

This script generates QMK and ZMK keymaps from unified YAML configuration.

Usage:
    python3 scripts/generate.py [--board BOARD_ID] [--validate] [--verbose]

Examples:
    # Generate for all boards
    python3 scripts/generate.py

    # Generate for specific board
    python3 scripts/generate.py --board skeletyl

    # Validate configuration without generating
    python3 scripts/generate.py --validate

    # Enable verbose output
    python3 scripts/generate.py --verbose
"""

import sys
import argparse
import subprocess
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
from keylayout_translator import KeylayoutTranslator
from keylayout_generator import KeylayoutGenerator


class KeymapGenerator:
    """Main generator orchestrator"""

    def __init__(self, repo_root: Path, verbose: bool = False, magic_training: bool = True):
        """
        Initialize generator

        Args:
            repo_root: Repository root directory
            verbose: Enable verbose output
            magic_training: Enable magic-key training mode (punish direct bigrams)
        """
        self.repo_root = repo_root
        self.config_dir = repo_root / "config"
        self.verbose = verbose
        self.magic_training = magic_training

        # Parse configuration
        self._log("📖 Parsing configuration...")
        self.keymap_config = YAMLConfigParser.parse_keymap(
            self.config_dir / "keymap.yaml"
        )
        self.board_inventory = YAMLConfigParser.parse_boards(
            self.config_dir / "boards.yaml"
        )
        self.aliases = YAMLConfigParser.parse_aliases(
            self.config_dir / "aliases.yaml"
        )
        self.combos = YAMLConfigParser.parse_combos(
            self.config_dir / "keymap.yaml"
        )
        self.magic_config = YAMLConfigParser.parse_magic_keys(
            self.config_dir / "keymap.yaml"
        )
        # Keycode map (firmware translations)
        keycodes = YAMLConfigParser.parse_keycodes(
            self.config_dir / "keycodes.yaml"
        )
        self.special_keycodes = YAMLConfigParser.parse_special_keycodes(
            self.config_dir / "aliases.yaml"
        )
        # Merge aliases.yaml special section over the general keycode map
        self.special_keycodes = {**keycodes, **self.special_keycodes}

        magic_count = len(self.magic_config.mappings) if self.magic_config else 0
        self._log(f"✅ Loaded {len(self.keymap_config.layers)} layers, "
                  f"{len(self.board_inventory.boards)} boards, "
                  f"{len(self.combos.combos)} combos, "
                  f"{magic_count} magic key configs")

        if self.verbose:
            print(f"  Layers: {', '.join(self.keymap_config.layers.keys())}")
            print(f"  Boards: {', '.join(self.board_inventory.boards.keys())}")
            print(f"  Aliases: {len(self.aliases)} behavior aliases")
            print(f"  Combos: {len(self.combos.combos)} combo definitions")
            print(f"  Magic keys: {magic_count} base layer configurations")

        # Validate configuration
        self._log("🔍 Validating configuration...")
        validator = ConfigValidator()
        validator.validate_keymap_config(self.keymap_config.layers)
        validator.validate_board_config(list(self.board_inventory.boards.values()))
        self._log("✅ Configuration is valid")

        # Initialize translators
        self.qmk_translator = QMKTranslator(self.aliases, self.special_keycodes)
        self.zmk_translator = ZMKTranslator(self.aliases, self.special_keycodes, magic_config=self.magic_config)

        # Set layer indices for ZMK translator
        layer_names = list(self.keymap_config.layers.keys())
        self.zmk_translator.set_layer_indices(layer_names)

        # Initialize compiler
        self.compiler = LayerCompiler(self.qmk_translator, self.zmk_translator)

    def _log(self, message: str):
        """Print message (always shown)"""
        print(message)

    def _verbose(self, message: str):
        """Print message only if verbose mode is enabled"""
        if self.verbose:
            print(message)

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

        self._log(f"\n🔨 Generating keymap for {board.name}...")

        if self.verbose:
            print(f"  Board ID: {board_id}")
            print(f"  Firmware: {board.firmware}")
            print(f"  Layout size: {board.layout_size}")
            if board.qmk_keyboard:
                print(f"  QMK keyboard: {board.qmk_keyboard}")
            if board.zmk_shield:
                print(f"  ZMK shield: {board.zmk_shield}")

        # Load keymap with board-specific overlay if specified
        keymap_config = self.keymap_config
        if board.keymap_file:
            overlay_path = self.config_dir / board.keymap_file
            if overlay_path.exists():
                self._log(f"  📋 Loading board-specific keymap: {board.keymap_file}")
                keymap_config = YAMLConfigParser.parse_keymap(
                    self.config_dir / "keymap.yaml",
                    overlay_path
                )
            else:
                print(f"⚠️  Warning: Board specifies keymap_file '{board.keymap_file}' but file not found")

        try:
            # Clear any previously tracked shift-morphs before compiling this board
            if board.firmware == "qmk":
                self.qmk_translator.clear_shift_morphs()
            else:
                self.zmk_translator.clear_shift_morphs()

            # Compile all layers for this board
            compiled_layers = []
            for layer in keymap_config.layers.values():
                # Check if this is a board-specific layer
                # If the layer has full_layout:
                # - For boards with keymap_file (custom layouts): include all full_layout layers
                # - For other boards: only include if in extra_layers (like GAME)
                if layer.full_layout is not None:
                    if not board.keymap_file and layer.name not in board.extra_layers:
                        # Skip if board doesn't use board-specific keymap and doesn't explicitly request this layer
                        self._verbose(f"  Skipping layer {layer.name} (not in extra_layers)")
                        continue

                self._verbose(f"  Compiling layer {layer.name}...")
                compiled_layer = self.compiler.compile_layer(
                    layer, board, board.firmware
                )
                compiled_layers.append(compiled_layer)

            self._verbose(f"  Compiled {len(compiled_layers)} layers")

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
        generator = QMKGenerator(special_keycodes=self.special_keycodes)
        output_dir = self.repo_root / board.get_output_directory()

        # Get shift-morphs collected during compilation
        shift_morphs = self.qmk_translator.get_shift_morphs()

        # Generate all files (combos and magic keys are now inline in keymap.c)
        files = generator.generate_keymap(board, compiled_layers, output_dir, self.combos, self.magic_config, self.keymap_config.layers, shift_morphs)

        # Write keymap files
        FileSystemWriter.write_all(output_dir, files)
        print(f"  📝 Wrote {len(files)} files to {output_dir}")

    def _generate_zmk(self, board, compiled_layers):
        """Generate ZMK keymap files"""
        behaviors_dtsi = self.repo_root / "zmk" / "config" / "dario_behaviors.dtsi"
        generator = ZMKGenerator(
            magic_training=self.magic_training,
            special_keycodes=self.special_keycodes,
            behaviors_dtsi_path=str(behaviors_dtsi) if behaviors_dtsi.exists() else None
        )
        output_dir = self.repo_root / board.get_output_directory()

        # Get shift-morphs collected during compilation
        shift_morphs = self.zmk_translator.get_shift_morphs()

        # Generate keymap file with combos and magic keys
        keymap_content = generator.generate_keymap(board, compiled_layers, self.combos, self.magic_config, shift_morphs)
        visualization = generator.generate_visualization(board, compiled_layers)

        # Prepare files to write
        readme_sections = [f"# {board.name} - ZMK Keymap", "", visualization]

        # Add magic key mappings summary if present
        if self.magic_config and self.magic_config.mappings:
            readme_sections.append("## Magic Key Mappings")
            for base_layer, mapping in self.magic_config.mappings.items():
                readme_sections.append(f"### {base_layer}")
                readme_sections.append(f"- default: {mapping.default}")
                readme_sections.append(f"- timeout_ms: {mapping.timeout_ms}")
                readme_sections.append("- mappings:")
                for prev_key, alt_key in mapping.mappings.items():
                    readme_sections.append(f"  - {prev_key} → {alt_key}")
                readme_sections.append("")  # spacing

        readme_content = "\n".join(readme_sections).rstrip() + "\n"

        files = {
            f"{board.zmk_shield}.keymap": keymap_content,
            "README.md": readme_content,
        }

        # Write files
        FileSystemWriter.write_all(output_dir, files)

        print(f"  📝 Wrote {len(files)} files to {output_dir}")

    def _generate_rowstagger_keylayouts(self):
        """Generate macOS .keylayout files for row-staggered keyboards"""
        rowstagger_dir = self.config_dir / "rowstagger"

        # Check if rowstagger directory exists
        if not rowstagger_dir.exists():
            return  # Skip if no row-stagger configs

        # Find all YAML files
        yaml_files = list(rowstagger_dir.glob("*.yaml"))
        if not yaml_files:
            return  # No configs to generate

        self._log(f"\n🔨 Generating row-staggered .keylayout files...")
        self._log(f"  Found {len(yaml_files)} layout(s)")

        # Initialize translator and generator
        translator = KeylayoutTranslator()
        template_path = self.repo_root / "scripts" / "templates" / "rowstagger_base.keylayout"

        if not template_path.exists():
            print(f"  ⚠️  Template not found: {template_path}")
            print(f"      Skipping row-stagger generation")
            return

        generator = KeylayoutGenerator(translator, template_path)

        # Create output directories
        output_dir = self.repo_root / "out" / "keylayout"
        output_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for yaml_file in yaml_files:
            try:
                self._verbose(f"  Processing {yaml_file.name}...")

                # Parse config
                config = YAMLConfigParser.parse_rowstagger(yaml_file)

                # Generate .keylayout XML
                xml_content = generator.generate_keylayout(config)

                # Write to output
                layout_name = yaml_file.stem  # e.g., "nightlife" from "nightlife.yaml"
                output_file = output_dir / f"{layout_name}.keylayout"
                with open(output_file, 'w') as f:
                    f.write(xml_content)

                print(f"  ✅ Generated {layout_name}.keylayout")
                success_count += 1

            except Exception as e:
                print(f"  ❌ Error generating {yaml_file.name}: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()

        print(f"\n✅ Generated {success_count}/{len(yaml_files)} row-stagger layouts")

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

            # Load keymap with board-specific overlay if specified
            keymap_config = self.keymap_config
            if board.keymap_file:
                overlay_path = self.config_dir / board.keymap_file
                if overlay_path.exists():
                    keymap_config = YAMLConfigParser.parse_keymap(
                        self.config_dir / "keymap.yaml",
                        overlay_path
                    )

            # Compile layers for this board
            compiled_layers = []
            for layer in keymap_config.layers.values():
                # Check if this is a board-specific layer
                # If the layer has full_layout:
                # - For boards with keymap_file (custom layouts): include all full_layout layers
                # - For other boards: only include if in extra_layers (like GAME)
                if layer.full_layout is not None:
                    if not board.keymap_file and layer.name not in board.extra_layers:
                        # Skip if board doesn't use board-specific keymap and doesn't explicitly request this layer
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

        # Generate row-staggered .keylayout files
        self._generate_rowstagger_keylayouts()

        # Update .keymap-drawer-config.yaml with auto-generated layer metadata
        print("\n📝 Updating .keymap-drawer-config.yaml...")
        try:
            subprocess.run(
                ["python3", str(self.repo_root / "scripts" / "update_keymap_drawer_config.py")],
                check=True,
                cwd=self.repo_root
            )
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to update .keymap-drawer-config.yaml: {e}")

        # Generate visualizations (grouped by base layer)
        visualizer = KeymapVisualizer(self.repo_root, self.qmk_translator)

        if visualizer.is_available():
            visualizer.generate_superset_visualizations(self.board_inventory)
            visualizer.generate_rowstagger_visualizations()
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
        "--validate", "--validate-only",
        action="store_true",
        dest="validate_only",
        help="Validate configuration without generating files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output (detailed progress information)"
    )
    parser.add_argument(
        "--no-magic-training",
        action="store_true",
        help="Disable magic-key training (default is on; training replaces mapped bigrams with '#')"
    )

    args = parser.parse_args()

    # Determine repository root
    repo_root = Path(__file__).parent.parent

    try:
        # Initialize generator (this validates configuration)
        generator = KeymapGenerator(
            repo_root,
            verbose=args.verbose,
            magic_training=not args.no_magic_training
        )

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
