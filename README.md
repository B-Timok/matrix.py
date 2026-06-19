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

## Running from different environments

It needs **Python 3.4+** and a real, interactive terminal (a TTY). No `pip
install` — `curses` ships with Python on Linux and macOS.

### Get the code

```bash
git clone https://github.com/B-Timok/matrix.py.git
cd matrix.py
python3 matrix.py
```

### Linux / macOS terminal

Works out of the box in any standard terminal (GNOME Terminal, Konsole,
iTerm2, macOS Terminal, Alacritty, kitty, …). For the richest fade gradient,
use a 256-color terminal:

```bash
TERM=xterm-256color ./matrix.py        # smoothest fade
```

On bare/limited terminals (`TERM=vt100`, `TERM=dumb`, serial consoles) it
degrades gracefully to a bold/dim monochrome look instead of crashing.

### Windows

`curses` is **not** bundled with Python on Windows. Pick one:

- **WSL** (recommended) — run it inside a WSL Linux distro exactly as above.
- **Git Bash / MSYS2** — works with their Python builds.
- **Native Windows Python** — install the curses port:
  ```powershell
  pip install windows-curses
  python matrix.py
  ```
  Use **Windows Terminal** for proper colors and Unicode katakana.

### SSH / remote servers

Just run it over your SSH session — it reads the remote `TERM`. If glyphs look
wrong, your local terminal font is the thing that matters; add `--ascii`.

### tmux / screen

Works inside multiplexers. For full color inside tmux, enable 256-color
support (e.g. `set -g default-terminal "screen-256color"` in `~/.tmux.conf`).

### Run without cloning

```bash
curl -sSL https://raw.githubusercontent.com/B-Timok/matrix.py/main/matrix.py | python3 -
```

> Piping a script straight into an interpreter runs it immediately — give it a
> read first if you don't trust the source.

### Where it won't run

It needs an interactive TTY, so it can't display in non-terminal contexts:
plain CI logs, `cron` jobs, Jupyter notebooks, or anything without a real
terminal attached. In those cases curses has nothing to draw to.

## Options

```
$ python3 matrix.py --help
usage: matrix.py [-h] [--color {cyan,green,purple,red,white,yellow}]
                 [--speed SPEED] [--density DENSITY] [--fade | --no-fade]
                 [--ascii]

Matrix digital rain for the terminal.

options:
  -h, --help            show this help message and exit
  --color {cyan,green,purple,red,white,yellow}
                        rain color (default: green)
  --speed SPEED         animation speed, 1 (slow) to 10 (fast) (default: 8)
  --density DENSITY     fraction of columns active, 0.1 to 1.0 (default: 0.9)
  --fade, --no-fade     smooth multi-step fade down each trail, with flicker,
                        for texture (default: True)
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

### `--fade` / `--no-fade`

Fade is **on by default**. The trail is rendered as a smooth 10-step
brightness gradient from full color down to nearly black, with a subtle
flicker between adjacent shades for extra texture. On terminals that support
redefinable colors (most 256-color terminals) this produces a soft, glowing
falloff; on simpler terminals it falls back to a bold→dim approximation.

Pass `--no-fade` for the simpler classic three-level look
(white head → bright → dim).

## Examples

```bash
./matrix.py --color cyan               # smooth cyan rain (fade is on by default)
./matrix.py --speed 9 --density 0.6    # fast and sparse
./matrix.py --color purple             # glowing violet falloff
./matrix.py --no-fade                  # classic three-level look
./matrix.py --ascii                    # if your font lacks katakana glyphs
```

## Notes

- If you see boxes instead of katakana, your terminal font doesn't include
  those glyphs — add `--ascii`.
- Resizing the terminal is handled live; the column grid rebuilds to fit.
