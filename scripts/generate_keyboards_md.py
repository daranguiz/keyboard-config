#!/usr/bin/env python3
"""
Generate KEYBOARDS.md from config/boards.yaml

This ensures the keyboard inventory documentation stays in sync with the actual
board configuration (Principle IV: Keyboard Inventory Transparency).

Usage:
    python3 scripts/generate_keyboards_md.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config_parser import YAMLConfigParser


def generate_keyboards_md(boards_yaml_path: Path, output_path: Path):
    """
    Generate KEYBOARDS.md from boards.yaml

    Args:
        boards_yaml_path: Path to config/boards.yaml
        output_path: Path to output KEYBOARDS.md file
    """
    # Parse boards configuration
    board_inventory = YAMLConfigParser.parse_boards(boards_yaml_path)

    # Group boards by firmware and status
    qmk_boards = []
    zmk_boards = []

    for board_id, board in board_inventory.boards.items():
        if board.firmware == "qmk":
            qmk_boards.append((board_id, board))
        elif board.firmware == "zmk":
            zmk_boards.append((board_id, board))

    # Sort by name
    qmk_boards.sort(key=lambda x: x[1].name)
    zmk_boards.sort(key=lambda x: x[1].name)

    # Generate markdown content
    content = f"""# Keyboard Inventory

**Auto-generated from `config/boards.yaml`** - Do not edit manually

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This document lists all keyboards configured in this repository with their firmware types and build configurations.

## Summary

- **Total keyboards**: {len(board_inventory.boards)}
- **QMK firmwares**: {len(qmk_boards)}
- **ZMK firmwares**: {len(zmk_boards)}

---

## QMK Keyboards ({len(qmk_boards)})

"""

    if qmk_boards:
        for board_id, board in qmk_boards:
            content += f"### {board.name}\n\n"
            content += f"**Board ID**: `{board_id}`  \n"
            content += f"**Firmware**: QMK  \n"
            content += f"**Keyboard**: `{board.qmk_keyboard}`  \n"
            content += f"**Layout**: {board.layout_size}  \n"

            if board.extra_layers:
                content += f"**Extra Layers**: {', '.join(board.extra_layers)}  \n"

            content += f"\n**Build command**:\n"
            content += f"```bash\n"
            content += f"qmk compile -kb {board.qmk_keyboard} -km dario\n"
            content += f"```\n\n"

            # Link to config
            content += f"**Configuration**: `qmk/config/boards/{board_id}.mk`\n\n"
            content += "---\n\n"
    else:
        content += "*No QMK keyboards configured*\n\n"

    content += f"""## ZMK Keyboards ({len(zmk_boards)})

"""

    if zmk_boards:
        for board_id, board in zmk_boards:
            content += f"### {board.name}\n\n"
            content += f"**Board ID**: `{board_id}`  \n"
            content += f"**Firmware**: ZMK  \n"
            content += f"**Shield**: `{board.zmk_shield}`  \n"
            content += f"**Layout**: {board.layout_size}  \n"

            if board.extra_layers:
                content += f"**Extra Layers**: {', '.join(board.extra_layers)}  \n"

            content += "\n**Configuration**: `zmk/config/boards/{board_id}.conf`\n\n"
            content += "---\n\n"
    else:
        content += "*No ZMK keyboards configured*\n\n"

    content += """
## Adding a New Keyboard

To add a new keyboard to this inventory:

### Option 1: Manual Configuration

1. Add an entry to `config/boards.yaml`:
   ```yaml
   <board_id>:
     name: "Board Name"
     firmware: qmk  # or zmk
     qmk_keyboard: "manufacturer/board/variant"  # for QMK
     # OR
     zmk_shield: "shield_name"  # for ZMK
     layout_size: "3x5_3"  # or 3x6_3, custom_*, etc.
     extra_layers: []  # optional board-specific layers
   ```

2. Create board-specific config:
   - **QMK**: `qmk/config/boards/<board_id>.mk` (feature flags)
   - **ZMK**: `zmk/config/boards/<board_id>.conf` (ZMK settings)

3. If the board has extensions, add them to layers in `config/keymap.yaml`:
   ```yaml
   layers:
     BASE:
       extensions:
         3x6_3:  # for 42-key boards
           outer_pinky_left: [TAB, GRV, CAPS]
           outer_pinky_right: [QUOT, BSLS, ENT]
   ```

4. Generate keymaps:
   ```bash
   python3 scripts/generate.py
   ```

5. Add to build targets:
   ```bash
   qmk userspace-add -kb <keyboard> -km dario
   ```

6. Update this file:
   ```bash
   python3 scripts/generate_keyboards_md.py
   ```

### Option 2: Helper Script

```bash
bash scripts/add_board.sh <board_id> <firmware> <keyboard_path> <layout_size>
```

Example:
```bash
bash scripts/add_board.sh corne zmk corne 3x6_3
```

This will automatically:
- Add entry to `config/boards.yaml`
- Create config template
- Regenerate this file

---

## Layout Sizes

- **3x5_3**: 36-key (3x5 fingers + 3 thumbs per hand) - Base layout
- **3x6_3**: 42-key (3x6 fingers + 3 thumbs per hand) - Corne, etc.
- **custom_***: Custom layouts with board-specific wrappers (Lulu, Lily58)

---

## Configuration Files

### Per-Board Configuration (Firmware-Specific Features)

**QMK**: `qmk/config/boards/<board_id>.mk`
- Feature flags (OLED, RGB Matrix, etc.)
- Build-time settings
- Board-specific QMK options

**ZMK**: `zmk/config/boards/<board_id>.conf`
- ZMK settings (Bluetooth, display, etc.)
- Shield-specific configuration

### Unified Keymap Configuration

**All keyboards share the same keymap** defined in `config/keymap.yaml`.

The 36-key core layout is identical across all keyboards. Larger boards automatically receive extensions based on their `layout_size`.

---

## Build All Keyboards

```bash
# Generate keymaps for all boards
python3 scripts/generate.py

# Build all QMK keyboards
qmk userspace-compile

# Or use the combined script
./build_all.sh
```

---

## Further Reading

- **Main documentation**: `CLAUDE.md` (repository root)
- **Keymap configuration guide**: `config/README.md`
- **Project constitution**: `.specify/memory/constitution.md`
- **Implementation plan**: `specs/003-unified-keymap-codegen/plan.md`
"""

    # Write output file
    output_path.write_text(content)
    print(f"✅ Generated {output_path}")


def main():
    """Main entry point"""
    # Determine paths
    repo_root = Path(__file__).parent.parent
    boards_yaml = repo_root / "config" / "boards.yaml"
    output_file = repo_root / "KEYBOARDS.md"

    if not boards_yaml.exists():
        print(f"❌ Error: {boards_yaml} not found")
        return 1

    try:
        generate_keyboards_md(boards_yaml, output_file)
        return 0
    except Exception as e:
        print(f"❌ Error generating KEYBOARDS.md: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
