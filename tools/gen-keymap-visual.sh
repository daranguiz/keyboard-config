#!/usr/bin/env bash
set -euo pipefail

# -------------------------------
# CONFIG (adjust for your machine)
# -------------------------------
QMK_FW="${QMK_FW:-$HOME/git/qmk_firmware}"      # path to qmk_firmware clone
QMK_US="${QMK_US:-$HOME/git/qmk_userspace}"     # path to qmk_userspace clone
KEYMAP="${KEYMAP:-dario}"                        # keymap name under keyboard/keymaps/
CONFIG="${CONFIG:-.keymap-drawer-config.yaml}"   # keymap-drawer config file
OUTDIR="${OUTDIR:-./docs/keymaps}"              # where to write .json/.svg

# -------------------------------
# USAGE
#   gen-keymap-visual.sh <keyboard> [<keymap>]
# EXAMPLE
#   gen-keymap-visual.sh bastardkb/skeletyl/promicro dario
#   gen-keymap-visual.sh boardsource/lulu/rp2040 dario
#   gen-keymap-visual.sh lily58/rev1 dario
# -------------------------------

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <keyboard> [keymap]"
  exit 1
fi

KB="$1"
KM="${2:-$KEYMAP}"

# Derive filesystem paths
# Try full path first, then parent directories (some keyboards have variant in build target but not in filesystem)
KEYMAP_DIR="$QMK_US/keyboards/$KB/keymaps/$KM"
if [[ ! -d "$KEYMAP_DIR" ]]; then
  # Try removing last path component (variant like promicro, rp2040, rev1)
  KB_PARENT="$(dirname "$KB")"
  KEYMAP_DIR="$QMK_US/keyboards/$KB_PARENT/keymaps/$KM"
  if [[ ! -d "$KEYMAP_DIR" ]]; then
    echo "Keymap directory not found at: $QMK_US/keyboards/$KB/keymaps/$KM"
    echo "                         or at: $KEYMAP_DIR"
    exit 1
  fi
fi

KEYMAP_C="$KEYMAP_DIR/keymap.c"
KMAP_CFG="$KEYMAP_DIR/keymap_config.h"
if [[ ! -f "$KEYMAP_C" ]]; then
  echo "Missing keymap.c in: $KEYMAP_DIR"
  exit 1
fi
if [[ ! -f "$KMAP_CFG" ]]; then
  echo "Missing keymap_config.h in: $KEYMAP_DIR"
  exit 1
fi

# The board header used by QMK via QMK_KEYBOARD_H; we set it explicitly.
# Most boards follow keyboards/<vendor>/<board>/<variant>.h
# For the three keyboards mentioned:
case "$KB" in
  bastardkb/skeletyl/promicro)
    KB_HEADER="keyboards/bastardkb/skeletyl/promicro.h"
    ;;
  boardsource/lulu/rp2040)
    KB_HEADER="keyboards/boardsource/lulu/rp2040.h"
    ;;
  lily58/rev1)
    KB_HEADER="keyboards/lily58/rev1.h"
    ;;
  *)
    # Generic fallback: try "<KB>.h"
    KB_HEADER="keyboards/${KB}.h"
    ;;
esac

# Validation for the chosen header (warn if missing; some boards generate headers)
if [[ ! -f "$QMK_FW/$KB_HEADER" ]]; then
  echo "Warning: board header not found at $QMK_FW/$KB_HEADER"
  echo "         If build still works normally, this can still be fine (header may be generated or deeply included)."
fi

mkdir -p "$OUTDIR"

# Temp workdir
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

# Create a stub QMK header that defines just what we need for preprocessing
STUB_HEADER="$WORKDIR/qmk_stub.h"
cat > "$STUB_HEADER" <<'STUB_EOF'
// Minimal QMK stub for preprocessing keymaps
#include <stdint.h>
#include <stdbool.h>

// Keycode type
typedef uint16_t keycode_t;

// PROGMEM stub - keep it so c2json can find the keymaps array
#define PROGMEM

// Matrix dimensions (overridden by keymap_config.h)
#ifndef MATRIX_ROWS
#define MATRIX_ROWS 10
#endif
#ifndef MATRIX_COLS
#define MATRIX_COLS 10
#endif

// DO NOT define LAYOUT_split_3x5_3 here - let it pass through unexpanded
// so that c2json can see the macro calls

STUB_EOF

# Wrapper file that includes stub then keymap.c
WRAP="$WORKDIR/keymap_wrapper.c"
cat > "$WRAP" <<EOF
#include "${STUB_HEADER}"
#include "${KEYMAP_C}"
EOF

# Preprocessor selection (clang preferred)
CPP_BIN="$(command -v clang || true)"
if [[ -z "$CPP_BIN" ]]; then
  CPP_BIN="$(command -v gcc || true)"
fi
if [[ -z "$CPP_BIN" ]]; then
  echo "clang/gcc not found"
  exit 1
fi

# Preprocess:
#  -E: preprocess only
#  -P: omit linemarkers
#  -CC: keep comments (harmless, avoids stripping certain macro args comments)
#  -I: include roots QMK relies on
#  -D: define QMK_KEYBOARD_H path (redundant but explicit)
#  -include: force keymap_config.h so LAYOUT_wrapper(...) resolves
PP_OUT="$WORKDIR/keymap.pp.c"

# Output names
BASENAME="$(echo "$KB" | tr '/' '_')_${KM}"
JSON_OUT="$OUTDIR/${BASENAME}.json"
SVG_OUT="$OUTDIR/${BASENAME}.svg"

# Define QMK_KEYBOARD_H to point to our stub header
# This prevents dario.h from trying to include the real (complex) QMK headers
"$CPP_BIN" -E -P -CC \
  -I"$WORKDIR" \
  -I"$QMK_US/users" \
  -I"$QMK_US/users/dario" \
  -I"$KEYMAP_DIR" \
  -DQMK_KEYBOARD_H='"qmk_stub.h"' \
  -include "$KMAP_CFG" \
  -o "$PP_OUT" "$WRAP"

# Clean up preprocessed file to only include keymaps array
# We only need the keymaps array, not all the expanded header content
CLEAN_OUT="$WORKDIR/keymap.clean.c"
cat > "$CLEAN_OUT" <<'CLEAN_HEADER'
#include <stdint.h>
#include <stdbool.h>
#define PROGMEM
CLEAN_HEADER

# Extract just the keymaps array and related definitions from preprocessed output
# Find the line with "const uint16_t keymaps" and everything after
sed -n '/const uint16_t.*keymaps\[\]/,$ p' "$PP_OUT" >> "$CLEAN_OUT"

# Use custom Python parser to convert preprocessed C to JSON
# qmk c2json doesn't work properly with preprocessed files or --no-cpp mode
cat > "$WORKDIR/parse_keymap.py" <<'PYEOF'
import sys, re, json

content = sys.stdin.read()

# Find all layers - match each line separately
layers = []
layout_name = None
for line in content.split('\n'):
    # Match with optional trailing comma
    # Support different layout macro names: LAYOUT_split_3x5_3, LAYOUT, LAYOUT_split, etc.
    m = re.match(r'\s*\[(\w+)\]\s*=\s*(LAYOUT[_\w]*)\((.*)\),?\s*$', line)
    if not m:
        continue

    layer_name = m.group(1)
    if layout_name is None:
        layout_name = m.group(2)  # Remember layout from first layer
    layer_content = m.group(3)

    # Tokenize by splitting on commas, but respecting parentheses
    keycodes = []
    current = ""
    depth = 0
    for ch in layer_content:
        if ch == '(':
            depth += 1
            current += ch
        elif ch == ')':
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0:
            # End of keycode
            kc = current.strip().split('/*')[0].strip()
            if kc:
                keycodes.append(kc)
            current = ""
        else:
            current += ch

    # Don't forget last one
    kc = current.strip().split('/*')[0].strip()
    if kc:
        keycodes.append(kc)

    print(f"{layer_name}: {len(keycodes)} keycodes", file=sys.stderr)
    layers.append(keycodes)

result = {
    "keyboard": sys.argv[1] if len(sys.argv) > 1 else "unknown",
    "keymap": sys.argv[2] if len(sys.argv) > 2 else "unknown",
    "layout": layout_name if layout_name else "LAYOUT_split_3x5_3",
    "layers": layers
}

json.dump(result, sys.stdout, indent=2)
PYEOF

# Parse preprocessed C to JSON (stderr goes to terminal, stdout to file)
cat "$CLEAN_OUT" | python3 "$WORKDIR/parse_keymap.py" "$KB" "$KM" > "$JSON_OUT"

# Validate JSON looks expanded: ensure "layers" contains many keycodes, not bare macro names
if grep -q '"layers"' "$JSON_OUT" && ! grep -q 'LAYER_' "$JSON_OUT"; then
  echo "Generated JSON: $JSON_OUT"
else
  echo "Warning: JSON likely unexpanded. Inspect: $JSON_OUT"
fi

# Draw SVG with layer names
keymap -c "$CONFIG" parse --layer-names BASE NUM SYM NAV MEDIA FUN -q "$JSON_OUT" | \
  keymap -c "$CONFIG" draw - > "$SVG_OUT"
echo "Wrote SVG: $SVG_OUT"
