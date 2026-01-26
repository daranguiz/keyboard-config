# How to Update the Ripple Matrix from a New Cosmos Export

When a new reference folder is provided (like `dario_dactyl3innercheekyoffsetsymmetric/`), update these files:

## 1. keyboard.json — Matrix Pins and Layout

Source: `<new_folder>/keyboards/<board_name>/keyboard.json`

Copy these sections into `qmk/keyboards/ripple/keyboard.json`:

- **`matrix_pins.cols`** — GPIO column pins
- **`matrix_pins.rows`** — GPIO row pins
- **`layouts.LAYOUT_split_3x5_3.layout`** — All 36 key entries with `matrix` coordinates and `x`/`y` positions

Important: The Cosmos export uses layout name `"LAYOUT"`. Our file uses `"LAYOUT_split_3x5_3"` (required by the codegen). Keep our name, just replace the `layout` array contents.

The Cosmos export may have broken matrix entries (e.g. many keys sharing the same `[row, col]`). If so, the new export should fix these — verify each of the 36 entries has a unique `[row, col]` pair.

## 2. config.h — Hardware Pins

Source: `<new_folder>/keyboards/<board_name>/config.h`

Copy pin definitions into `qmk/keyboards/ripple/config.h`:

- `SERIAL_USART_TX_PIN` / `SERIAL_USART_RX_PIN` — split communication
- `VIK_SPI_*`, `VIK_I2C_*`, `VIK_GPIO_*`, `VIK_WS2812_DI_PIN` — VIK connector pins

The `#include` paths must stay as `keyboards/ripple/vik/...` (not the Cosmos path).

## 3. VIK Module (unlikely to change)

The `vik/` directory contains generic VIK infrastructure. Only update if the Cosmos export includes a newer version. Files are identical across all Cosmos boards.

## 4. Nothing Else Changes

These files are unaffected by a matrix update:
- `config/boards.yaml` — board definition (already correct)
- `qmk/qmk.json` — build targets (already correct)
- `qmk/config/boards/ripple.mk` — feature flags (already correct)
- `qmk/keyboards/ripple/rules.mk` — VIK inclusion (already correct)
- `qmk/keyboards/ripple/keymaps/dario/*` — auto-generated, will be regenerated

## 5. After Updating

```bash
python3 scripts/generate.py   # regenerate keymaps (no matrix changes here, but good practice)
./build_all.sh                 # build firmware to verify compilation
```
