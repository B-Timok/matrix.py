#!/usr/bin/env python3
"""Matrix digital rain for the terminal.

Usage:
    python3 matrix.py [options]

Press 'q' or Ctrl-C to quit. Press your terminal's fullscreen key
(often F11, or Cmd/Ctrl+Enter) for the full effect.

Options:
    --color {green,cyan,red,purple,white,yellow}  Rain color (default: green)
    --speed N        Animation speed, 1 (slow) to 10 (fast). Default: 8
    --density F      Fraction of columns active, 0.1 to 1.0. Default: 0.9
    --fade / --no-fade  Smooth multi-step brightness gradient down each trail,
                     with subtle flicker, for extra texture. On by default.
    --ascii          Use ASCII characters instead of katakana
"""

import argparse
import curses
import locale
import random
import time

# Authentic-looking glyphs: half-width katakana plus a few digits/symbols.
KATAKANA = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789:.\"=*+-<>"
ASCII = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.\"=*+-<>|!?#$%&"

COLORS = {
    "green": curses.COLOR_GREEN,
    "cyan": curses.COLOR_CYAN,
    "red": curses.COLOR_RED,
    "purple": curses.COLOR_MAGENTA,
    "white": curses.COLOR_WHITE,
    "yellow": curses.COLOR_YELLOW,
}

# RGB (0-1000 scale) used to build a smooth fade ramp when --fade is on and the
# terminal can redefine colors.
COLOR_RGB = {
    "green": (0, 1000, 0),
    "cyan": (0, 1000, 1000),
    "red": (1000, 40, 40),
    "purple": (800, 0, 1000),
    "white": (1000, 1000, 1000),
    "yellow": (1000, 1000, 0),
}

# Populated by init_colors(): the attribute for the leading glyph, and the list
# of attributes used down the trail (brightest first, dimmest last).
HEAD_ATTR = 0
TRAIL_ATTRS = []


def parse_args():
    p = argparse.ArgumentParser(
        description="Matrix digital rain for the terminal.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--color", choices=sorted(COLORS), default="green", help="rain color"
    )
    p.add_argument(
        "--speed", type=int, default=8, help="animation speed, 1 (slow) to 10 (fast)"
    )
    p.add_argument(
        "--density",
        type=float,
        default=0.9,
        help="fraction of columns active, 0.1 to 1.0",
    )
    p.add_argument(
        "--fade",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="smooth multi-step fade down each trail, with flicker, for texture",
    )
    p.add_argument(
        "--ascii", action="store_true", help="use ASCII characters instead of katakana"
    )
    args = p.parse_args()

    if not 1 <= args.speed <= 10:
        p.error("--speed must be between 1 and 10")
    if not 0.1 <= args.density <= 1.0:
        p.error("--density must be between 0.1 and 1.0")
    return args


class Column:
    """A single vertical stream of falling glyphs."""

    def __init__(self, x, height, charset):
        self.x = x
        self.height = height
        self.charset = charset
        self.reset(start_above=True)

    def reset(self, start_above=False):
        # Head starts somewhere above the screen so columns don't all begin together.
        self.head = random.randint(-self.height, 0) if start_above else -1
        self.length = random.randint(self.height // 3, self.height)
        self.fall_rate = random.choice((1, 1, 1, 2))  # rows advanced per tick
        self.tick = 0
        # The glyphs currently shown in this column, indexed by row.
        self.chars = {}

    def step(self):
        self.tick += 1
        if self.tick < self.fall_rate:
            return
        self.tick = 0

        # Occasionally mutate an existing glyph in place for a "glitch" flicker.
        if self.chars and random.random() < 0.15:
            row = random.choice(list(self.chars))
            self.chars[row] = random.choice(self.charset)

        self.head += 1
        if 0 <= self.head < self.height:
            self.chars[self.head] = random.choice(self.charset)

        # Drop glyphs that have fallen off the tail of the trail.
        tail = self.head - self.length
        self.chars.pop(tail, None)

        # Once the whole trail has passed the bottom, recycle the column.
        if self.head - self.length > self.height:
            self.reset()

    def cells(self):
        """Yield (row, char, depth, length); depth is rows behind the head (0 = head)."""
        for row, ch in self.chars.items():
            if not 0 <= row < self.height:
                continue
            yield row, ch, self.head - row, self.length


def init_monochrome(fade):
    """Fallback for terminals with no color: shape the rain with bold/dim only."""
    global HEAD_ATTR, TRAIL_ATTRS
    HEAD_ATTR = curses.A_BOLD | curses.A_REVERSE
    if fade:
        TRAIL_ATTRS = [
            curses.A_BOLD,
            curses.A_NORMAL,
            curses.A_NORMAL,
            curses.A_DIM,
            curses.A_DIM,
        ]
    else:
        TRAIL_ATTRS = [curses.A_BOLD, curses.A_NORMAL, curses.A_DIM]


def init_colors(name, fade):
    """Set up HEAD_ATTR and the TRAIL_ATTRS gradient for the chosen color/mode."""
    global HEAD_ATTR, TRAIL_ATTRS

    # Terminals with no color support (e.g. TERM=dumb, some CI/log shells) can't
    # do color pairs at all; fall back to a bold/dim-only look instead of crashing.
    try:
        if not curses.has_colors():
            init_monochrome(fade)
            return
        curses.start_color()
        curses.use_default_colors()
    except curses.error:
        init_monochrome(fade)
        return

    # The leading glyph is always a bright white.
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    HEAD_ATTR = curses.color_pair(1) | curses.A_BOLD

    base = COLORS[name]

    can_ramp = False
    if fade and curses.can_change_color() and curses.COLORS >= 32:
        # Smooth ramp of custom shades from bright down to nearly black. Some
        # terminals advertise can_change_color() but still reject init_color(),
        # so fall through to the bold/dim approximation if it raises.
        try:
            steps = 10
            r, g, b = COLOR_RGB[name]
            attrs = []
            for i in range(steps):
                factor = 1.0 - (i / steps) * 0.85  # 1.0 -> ~0.15
                color_num = 16 + i
                pair_num = 2 + i
                curses.init_color(
                    color_num, int(r * factor), int(g * factor), int(b * factor)
                )
                curses.init_pair(pair_num, color_num, -1)
                attrs.append(
                    curses.color_pair(pair_num) | (curses.A_BOLD if i < 2 else 0)
                )
            TRAIL_ATTRS = attrs
            can_ramp = True
        except curses.error:
            can_ramp = False

    if can_ramp:
        pass
    elif fade:
        # Terminal can't redefine colors: approximate texture with bold/dim.
        curses.init_pair(2, base, -1)
        p = curses.color_pair(2)
        TRAIL_ATTRS = [p | curses.A_BOLD, p, p, p | curses.A_DIM, p | curses.A_DIM]
    else:
        # Classic three-level look: bright head-trail, then dim body.
        curses.init_pair(2, base, -1)
        p = curses.color_pair(2)
        TRAIL_ATTRS = [p | curses.A_BOLD, p, p]


def trail_attr(depth, length, fade):
    """Pick a trail attribute for a glyph `depth` rows behind a head, trail `length` long."""
    n = len(TRAIL_ATTRS)
    frac = depth / length if length else 1.0
    idx = min(n - 1, int(frac * n))
    # Subtle flicker between adjacent shades adds texture in fade mode.
    if fade and idx < n - 1 and random.random() < 0.12:
        idx += 1
    return TRAIL_ATTRS[idx]


def build_columns(width, height, density, charset):
    active = max(1, int(width * density))
    xs = random.sample(range(width), min(active, width))
    return [Column(x, height, charset) for x in xs]


def draw(stdscr, columns, fade):
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    for col in columns:
        for row, ch, depth, length in col.cells():
            # Guard the bottom-right cell: writing there raises on many terminals.
            if row == height - 1 and col.x == width - 1:
                continue
            attr = HEAD_ATTR if depth == 0 else trail_attr(depth, length, fade)
            try:
                stdscr.addstr(row, col.x, ch, attr)
            except curses.error:
                pass
    stdscr.noutrefresh()
    curses.doupdate()


def main(stdscr, args):
    # Some minimal terminals (e.g. TERM=vt100/dumb) lack cursor-visibility
    # capabilities and raise here; hiding the cursor is cosmetic, so skip it.
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.nodelay(True)
    init_colors(args.color, args.fade)
    charset = ASCII if args.ascii else KATAKANA

    height, width = stdscr.getmaxyx()
    columns = build_columns(width, height, args.density, charset)
    delay = 0.11 - (args.speed - 1) * 0.01  # speed 1 -> 0.11s, speed 10 -> 0.02s

    # Pace by an absolute schedule and subtract render time, so --speed stays
    # consistent on large terminals where drawing a frame isn't free.
    next_frame = time.monotonic()
    while True:
        ch = stdscr.getch()
        if ch in (ord("q"), ord("Q")):
            break
        if ch == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()
            columns = build_columns(width, height, args.density, charset)

        for col in columns:
            col.step()
        draw(stdscr, columns, args.fade)

        next_frame += delay
        remaining = next_frame - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        else:
            # Behind schedule (slow terminal / big screen); resync to avoid
            # accumulating drift and a "catch-up" burst of frames.
            next_frame = time.monotonic()


if __name__ == "__main__":
    args = parse_args()
    # curses only renders multibyte glyphs (the katakana) correctly when the
    # locale is initialized from the environment. Without this, non-ASCII chars
    # show up as boxes/garbage and --ascii becomes the only usable mode.
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass
    try:
        curses.wrapper(main, args)
    except KeyboardInterrupt:
        pass
