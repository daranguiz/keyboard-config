# Contextual Hold-Tap (whitespace-conditional)

Hold-tap behavior that changes its flavor after specific prior keycodes (e.g., whitespace) within a timeout window. Defaults to `balanced` but switches to `hold-preferred` when the last emitted keycode matches the configured set and is recent enough.

## Devicetree usage
```dts
/ {
  behaviors {
    ws_ht: ws_ht {
      compatible = "dario,behavior-contextual-hold-tap";
      label = "WS_HT";
      #binding-cells = <0>;

      tap-bindings  = <&kp MAGIC>;
      hold-bindings = <&kp LSHIFT>;

      normal-flavor   = "balanced";
      after-flavor    = "hold-preferred";
      prior-keycodes  = <SPACE TAB ENTER KP_ENTER>;
      prior-timeout-ms = <300>;
      tapping-term-ms = <200>;
      quick-tap-ms    = <0>;
    };
  };
};
```

Bind in the keymap with `&ws_ht`.

### Supported properties
- `tap-bindings` / `hold-bindings` (required) — phandle arrays invoked in order.
- `normal-flavor` (default `balanced`), `after-flavor` (default `hold-preferred`) — one of `balanced`, `tap-preferred`, `hold-preferred`.
- `prior-keycodes` (default `<SPACE>`) and `prior-timeout-ms` (default `300`).
- Tuning: `tapping-term-ms` (default `200`), `quick-tap-ms` (default `0`), `require-prior-idle-ms` (default `-1`), `hold-trigger-key-positions`, `hold-trigger-on-release`, `hold-while-undecided`, `hold-while-undecided-linger`, `retro-tap`.

### Split note
Designed to behave like a monoboard: tracking uses emitted keycode events (press, non-mod). No explicit cross-half sync beyond ZMK’s event propagation.

### Logging
Enable `CONFIG_DARIO_CONTEXTUAL_HT_LOG=y` for debug messages (flavor selection, decisions).

## Integrating the module
- As a Zephyr module: add the path (e.g. `<config>/modules/dario/contextual-hold-tap`) to `ZMK_EXTRA_MODULES` or `ZEPHYR_EXTRA_MODULES`.
- Via `west.yml`: add a project pointing at the module repo/path, or keep it checked into your config and point `ZMK_EXTRA_MODULES` at it.
