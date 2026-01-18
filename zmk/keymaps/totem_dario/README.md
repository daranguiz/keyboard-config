# GEIGEIGEIST TOTEM - ZMK Keymap

# Keymap Visualization: GEIGEIGEIST TOTEM

## BASE_PRIMARY Layer

```
 0: &kp B
 1: &kp F
 2: &kp L
 3: &kp K
 4: &kp Q
 5: &kp P

 6: &kp G
 7: &kp O
 8: &kp U
 9: &sm_dot_grv
10: &hmr LGUI N
11: &hmr LALT S

12: &hml LCTL H
13: &hml LSFT T
14: &kp M
15: &kp Y
16: &hml LSFT C
17: &hml LCTL A

18: &hmr LALT E
19: &hmr LGUI I
20: &key_repeat
21: &kp X
22: &kp V
23: &kp J

24: &kp D
25: &kp Z
26: &kp SQT
27: &kp W
28: &kp MINUS
29: &kp FSLH

30: &sm_comm_at
31: &key_repeat
32: &lt_ak_primary NUM 0
33: &lt SYM R
34: &mt LSFT BSPC
35: &mt LSFT TAB

36: &lt NAV SPACE
37: &lt MEDIA ENTER
```

## BASE_ALT Layer

```
 0: &kp B
 1: &kp F
 2: &kp L
 3: &kp K
 4: &kp Q
 5: &kp J

 6: &kp G
 7: &kp O
 8: &kp U
 9: &sm_dot_grv
10: &hmr LGUI N
11: &hmr LALT S

12: &hml LCTL H
13: &hml LSFT T
14: &kp D
15: &kp Y
16: &hml LSFT C
17: &hml LCTL A

18: &hmr LALT E
19: &hmr LGUI I
20: &none
21: &kp X
22: &kp V
23: &kp M

24: &kp P
25: &kp Z
26: &kp SQT
27: &kp W
28: &kp MINUS
29: &kp FSLH

30: &sm_comm_at
31: &none
32: &lt_ak_alt NUM 0
33: &lt SYM R
34: &mt LSFT BSPC
35: &mt LSFT TAB

36: &lt NAV SPACE
37: &lt MEDIA ENTER
```

## BASE_ALT2 Layer

```
 0: &kp B
 1: &kp L
 2: &kp M
 3: &kp C
 4: &kp Z
 5: &kp J

 6: &kp F
 7: &kp O
 8: &kp U
 9: &sm_dot_grv
10: &hmr LGUI N
11: &hmr LALT R

12: &hml LCTL T
13: &hml LSFT D
14: &kp P
15: &kp Y
16: &hml LSFT H
17: &hml LCTL A

18: &hmr LALT E
19: &hmr LGUI I
20: &key_repeat
21: &kp X
22: &kp Q
23: &kp V

24: &kp G
25: &kp W
26: &kp SQT
27: &kp K
28: &kp MINUS
29: &kp FSLH

30: &sm_comm_at
31: &key_repeat
32: &lt_ak_alt2 NUM 0
33: &lt SYM S
34: &mt LSFT BSPC
35: &mt LSFT TAB

36: &lt NAV SPACE
37: &lt MEDIA ENTER
```

## SYM Layer

```
 0: &kp AMPERSAND
 1: &kp PERCENT
 2: &kp DOLLAR
 3: &sl NUM
 4: &none
 5: &kp HASH

 6: &kp PLUS
 7: &kp LBRC
 8: &kp RBRC
 9: &kp EQUAL
10: &hmr LGUI LT
11: &hmr LALT GT

12: &hml LCTL LBKT
13: &hml LSFT RBKT
14: &none
15: &kp SEMI
16: &kp EXCL
17: &kp LPAR

18: &kp RPAR
19: &kp COLON
20: &trans
21: &kp CARET
22: &kp PIPE
23: &kp TILDE

24: &kp BSLH
25: &none
26: &kp DQT
27: &kp ASTERISK
28: &kp UNDERSCORE
29: &kp QUESTION

30: &kp COMMA
31: &trans
32: &none
33: &none
34: &none
35: &ak_primary

36: &kp SPACE
37: &kp ENTER
```

## NUM Layer

```
 0: &kp AMPERSAND
 1: &kp PERCENT
 2: &kp DOLLAR
 3: &sl SYM_SHADOW
 4: &none
 5: &kp HASH

 6: &kp N7
 7: &kp N8
 8: &kp N9
 9: &kp DOT
10: &hmr LGUI LT
11: &hmr LALT GT

12: &hml LCTL LBKT
13: &hml LSFT RBKT
14: &none
15: &kp SEMI
16: &kp N1
17: &kp N2

18: &kp N3
19: &kp N0
20: &trans
21: &kp LG(Z)
22: &kp LG(X)
23: &kp LG(C)

24: &kp LG(V)
25: &kp LG(LS(Z))
26: &kp DQT
27: &kp N4
28: &kp N5
29: &kp N6

30: &kp COMMA
31: &trans
32: &none
33: &none
34: &none
35: &ak_primary

36: &kp SPACE
37: &kp ENTER
```

## NAV Layer

```
 0: &none
 1: &kp PG_UP
 2: &none
 3: &caps_word
 4: &kp ESC
 5: &none

 6: &none
 7: &none
 8: &none
 9: &none
10: &none
11: &kp LEFT

12: &kp UP
13: &kp RIGHT
14: &kp CAPS
15: &none
16: &kp LSHFT
17: &kp LCTRL

18: &kp LALT
19: &kp LGUI
20: &trans
21: &kp END
22: &kp PG_DN
23: &kp DOWN

24: &kp HOME
25: &kp INS
26: &none
27: &none
28: &none
29: &none

30: &none
31: &trans
32: &kp DEL
33: &kp ENTER
34: &kp BSPC
35: &none

36: &none
37: &none
```

## MEDIA Layer

```
 0: &to BASE_PRIMARY
 1: &to BASE_ALT
 2: &to BASE_ALT2
 3: &none
 4: &none
 5: &bt BT_SEL 0

 6: &bt BT_SEL 1
 7: &bt BT_SEL 2
 8: &bt BT_SEL 3
 9: &bt BT_CLR
10: &kp C_NEXT
11: &kp C_VOL_UP

12: &kp C_VOL_DN
13: &kp C_PREV
14: &none
15: &none
16: &kp LSHFT
17: &kp LCTRL

18: &kp LALT
19: &kp LGUI
20: &trans
21: &kp LG(Z)
22: &kp LG(X)
23: &kp LG(C)

24: &kp LG(V)
25: &kp LG(LS(Z))
26: &none
27: &none
28: &none
29: &none

30: &bootloader
31: &trans
32: &kp C_MUTE
33: &kp C_PLAY_PAUSE
34: &kp C_STOP
35: &none

36: &none
37: &none
```

## SYM_SHADOW Layer

```
 0: &kp AMPERSAND
 1: &kp PERCENT
 2: &kp DOLLAR
 3: &sl NUM
 4: &none
 5: &kp HASH

 6: &kp PLUS
 7: &kp LBRC
 8: &kp RBRC
 9: &kp EQUAL
10: &hmr LGUI LT
11: &hmr LALT GT

12: &hml LCTL LBKT
13: &hml LSFT RBKT
14: &none
15: &kp SEMI
16: &kp EXCL
17: &kp LPAR

18: &kp RPAR
19: &kp COLON
20: &trans
21: &kp CARET
22: &kp PIPE
23: &kp TILDE

24: &kp BSLH
25: &none
26: &kp DQT
27: &kp ASTERISK
28: &kp UNDERSCORE
29: &kp QUESTION

30: &kp COMMA
31: &trans
32: &none
33: &none
34: &none
35: &ak_primary

36: &kp SPACE
37: &kp ENTER
```

## Magic Key Mappings
### BASE_PRIMARY
- default: REPEAT
- timeout_ms: 1000
- mappings:
  -   → THE
  - , →  BUT
  - - → >
  - . → /
  - C → Y
  - G → Y
  - / → *
  - * → /

### BASE_ALT
- default: REPEAT
- timeout_ms: 0
- mappings:
  -   → THE
  - , →  BUT
  - - → >
  - . → /
  - / → *
  - * → /

### BASE_ALT2
- default: REPEAT
- timeout_ms: 0
- mappings:
  -   → THE
  - , →  BUT
  - - → >
  - . → /
  - / → *
  - * → /
