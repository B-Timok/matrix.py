# matrix.py

A terminal Matrix digital rain animation. Zero dependencies — just Python 3's
built-in `curses` module.

## Run it

```bash
python3 matrix.py        # or, since it's executable:
./matrix.py
```

Press your terminal's fullscreen key (usually **F11**, or **Cmd/Ctrl+Enter**)
for the full effect. Press **q** or **Ctrl-C** to quit.

## Options

```
$ python3 matrix.py --help
usage: matrix.py [-h] [--color {cyan,green,purple,red,white,yellow}]
                 [--speed SPEED] [--density DENSITY] [--fade] [--ascii]

Matrix digital rain for the terminal.

options:
  -h, --help            show this help message and exit
  --color {cyan,green,purple,red,white,yellow}
                        rain color (default: green)
  --speed SPEED         animation speed, 1 (slow) to 10 (fast) (default: 5)
  --density DENSITY     fraction of columns active, 0.1 to 1.0 (default: 0.9)
  --fade                smooth multi-step fade down each trail, with flicker,
                        for texture (default: False)
  --ascii               use ASCII characters instead of katakana (default: False)
```

### Colors

`--color` accepts any of:

| Value    | Look          |
|----------|---------------|
| `green`  | classic (default) |
| `cyan`   | icy blue-green |
| `red`    | alarm red     |
| `purple` | magenta/violet |
| `white`  | monochrome    |
| `yellow` | amber         |

### `--fade`

By default each trail uses a three-level look (white head → bright → dim).
With `--fade`, the trail is rendered as a smooth 10-step brightness gradient
from full color down to nearly black, with a subtle flicker between adjacent
shades for extra texture. On terminals that support redefinable colors (most
256-color terminals) this produces a soft, glowing falloff; on simpler
terminals it falls back to a bold→dim approximation.

## Examples

```bash
./matrix.py --color cyan --fade        # smooth cyan rain
./matrix.py --speed 9 --density 0.6    # fast and sparse
./matrix.py --color purple --fade      # glowing violet falloff
./matrix.py --ascii                    # if your font lacks katakana glyphs
```

## Notes

- If you see boxes instead of katakana, your terminal font doesn't include
  those glyphs — add `--ascii`.
- Resizing the terminal is handled live; the column grid rebuilds to fit.
