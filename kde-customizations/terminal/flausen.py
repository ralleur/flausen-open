#!/usr/bin/env python3
"""flausen. -- an ASCII mobile for a terminal greeting. Python 3, no packages.

Artwork and palette adapted from the supplied flausen. reference.
The animation owns its reserved lines only while this foreground process runs.
"""

import argparse
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import time


ESC = "\x1b["
PALETTES = {
    "dark": {
        "ink": (239, 237, 231), "wire": (160, 156, 151),
        "blue": (57, 121, 237), "orange": (246, 135, 57),
        "teal": (54, 174, 174), "brown": (177, 119, 83),
        "muted": (163, 161, 156),
    },
    "light": {
        "ink": (25, 24, 25), "wire": (80, 74, 71),
        "blue": (31, 99, 217), "orange": (221, 102, 27),
        "teal": (27, 132, 136), "brown": (146, 91, 58),
        "muted": (100, 97, 94),
    },
}

# All glyphs are deliberately ASCII. The tall ascenders, hairlines and serifs
# echo the reference instead of substituting an unrelated block/FIGlet font.
GLYPHS = [
    (6, ["  .-.", " /  )", " |", " |", " |", "-+--", " |", " |", " |", " |", " |", " |", "_|_"]),
    (4, [" .", " ||", " ||", " ||", " ||", " ||", " ||", " ||", " ||", " ||", " ||", " ||", "_||_"]),
    (7, [""] * 5 + [" .--.", "'   ||", "    ||", " .--||", "||  ||", "||  ||", "||  ||", " '__.'|"]),
    (7, [""] * 5 + [" .   .", "||  ||", "||  ||", "||  ||", "||  ||", "||  ||", "||  ||", " \\__.'|"]),
    (6, [""] * 5 + [" .--.", "(   '", " \\", "  \\", "   \\", "    )", "|   |", "'._.'"]),
    (7, [""] * 5 + [" .--.", "/   ||", "||  ||", "||--'", "||", "||", "||  |", " '._.'"]),
    (7, [""] * 5 + [" .--.", "||  |", "||  |", "||  |", "||  |", "||  |", "||  |", "_||__|_"]),
    (4, [""] * 11 + ["  .", " (_)"]),
]
WORDMARK = ["".join(rows[y].ljust(width) for width, rows in GLYPHS).rstrip() for y in range(13)]


def rotate(point, origin, angle):
    x, y = point[0] - origin[0], point[1] - origin[1]
    c, s = math.cos(angle), math.sin(angle)
    return origin[0] + c * x - s * y, origin[1] + s * x + c * y


def inside(x, y, polygon):
    result = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            result = not result
        j = i
    return result


class Canvas:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.cells = [[(" ", "ink") for _ in range(width)] for _ in range(height)]

    def put(self, x, y, char, role="ink"):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = char, role

    def text(self, x, y, value, role="ink"):
        for offset, char in enumerate(value):
            self.put(x + offset, y, char, role)

    def line(self, p, q, ox, oy):
        # Physical coordinates: one terminal cell is roughly twice as tall as wide.
        dx, dy = q[0] - p[0], q[1] - p[1]
        steps = max(1, math.ceil(max(abs(dx), abs(dy)) * 10))
        slope = abs(dy) / max(abs(dx), 0.001)
        char = "-" if slope < 0.35 else ("|" if slope > 2.2 else ("\\" if dx * dy > 0 else "/"))
        for i in range(steps + 1):
            f = i / steps
            self.put(round(ox + p[0] + f * dx), int(oy + (p[1] + f * dy) / 2), char, "wire")

    def polygon(self, polygon, role, ox, oy, holes=()):
        left = max(0, math.floor(ox + min(p[0] for p in polygon)))
        right = min(self.width, math.ceil(ox + max(p[0] for p in polygon)))
        top = max(0, math.floor(oy + min(p[1] for p in polygon) / 2))
        bottom = min(self.height, math.ceil(oy + max(p[1] for p in polygon) / 2))
        ramp = " .:+#"
        for y in range(top, bottom):
            for x in range(left, right):
                count = 0
                for sy in range(4):
                    for sx in range(3):
                        px, py = x - ox + (sx + 0.5) / 3, 2 * (y - oy + (sy + 0.5) / 4)
                        if inside(px, py, polygon) and not any(inside(px, py, hole) for hole in holes):
                            count += 1
                char = ramp[round(count * 4 / 12)]
                if char != " ":
                    self.put(x, y, char, role)

    def plain(self):
        return "\n".join("".join(c for c, _ in row).rstrip() for row in self.cells)

    def ansi(self, theme="dark", color=True):
        output = []
        palette = PALETTES[theme]
        for row in self.cells:
            end = len(row)
            while end and row[end - 1][0] == " ":
                end -= 1
            active = None
            line = []
            for char, role in row[:end]:
                if color and char != " " and role != active:
                    r, g, b = palette[role]
                    line.append(f"{ESC}38;2;{r};{g};{b}m")
                    active = role
                line.append(char)
            if color:
                line.append(ESC + "0m")
            output.append("".join(line))
        return output


def mobile(canvas, ox, oy, phase=0.0, amplitude=1.0):
    # A slow, closed six-second cycle. The two bars and four pendants have
    # different phases, with every cord kept attached to its moving support.
    a = amplitude * 0.035 * math.sin(phase)
    b = amplitude * 0.055 * math.sin(phase + 0.8)
    pivot = (12.0, 2.1)
    main = lambda p: rotate(p, pivot, a)
    left, junction = main((5.0, 3.9)), main((15.4, 5.9))
    second = lambda p: rotate((p[0] + junction[0] - 15.4, p[1] + junction[1] - 5.9), junction, a + b)
    teal_hook, tab_hook = second((19.8, 7.2)), second((26.1, 9.9))
    canvas.line((12.0, 0.0), pivot, ox, oy)
    # The lightly bowed main rod.
    control = (13.7, 1.6)
    previous = left
    for i in range(1, 41):
        t = i / 40
        p = tuple((1 - t) ** 2 * left[k] + 2 * (1 - t) * t * control[k] + t * t * junction[k] for k in (0, 1))
        canvas.line(previous, p, ox, oy)
        previous = p
    canvas.line(junction, teal_hook, ox, oy)
    canvas.line(teal_hook, tab_hook, ox, oy)
    canvas.put(round(ox + pivot[0]), int(oy + pivot[1] / 2), "o", "wire")

    def pendant(shape, anchor, support, length, role, angle, holes=()):
        attach = (support[0], support[1] + length)
        transform = lambda p: rotate((p[0] + attach[0] - anchor[0], p[1] + attach[1] - anchor[1]), attach, angle)
        canvas.line(support, attach, ox, oy)
        canvas.polygon([transform(p) for p in shape], role, ox, oy,
                       [[transform(p) for p in hole] for hole in holes])

    # Blue: the large, bent shape with its characteristic opening.
    blue = [(4.2, 0), (6.1, .2), (6.9, 1.2), (7.3, 3), (8.0, 6.7),
            (9.1, 7.8), (14.0, 9.5), (14.8, 10.4), (17.4, 16.9),
            (14.1, 19.4), (12.1, 13.7), (11.3, 12.8), (6.5, 12.2),
            (2.1, 13.7), (1.5, 12.7), (0, 4.4), (.2, 3.7)]
    hole = [(2.6, 7.5), (5.5, 6.2), (6.4, 10), (3.0, 11.5)]
    pendant(blue, (5.0, .4), left, 1.3, "blue",
             amplitude * .055 * math.sin(phase - .5), [hole])
    orange = [(13.5, 0), (15.6, 1.1), (17.8, 4.9), (14.6, 5.8)]
    pendant(orange, (15.4, 1.1), junction, 3.5, "orange",
             amplitude * .09 * math.sin(phase + 1.1))
    ribbon = [(20.1, 0), (20.3, 5.7), (19.9, 7.7), (20.0, 8.5),
              (21.3, 11.5), (21.7, 19.2), (19.9, 17.8), (19.9, 13.9),
              (19.1, 10.4), (19.0, 8.9), (19.4, 6.9), (19.2, 1.0)]
    pendant(ribbon, (19.8, .6), teal_hook, 4.6, "teal",
             amplitude * .05 * math.sin(phase - 1.0))
    tab = [(25.8, -.4), (27.9, .6), (27.7, 2.2), (25.5, 1.2)]
    pendant(tab, (26.1, 0), tab_hook, 0, "brown",
             amplitude * .065 * math.sin(phase + 2.0))


def make_frame(width=80, phase=0.0, amplitude=0.0):
    width = max(12, int(width))
    if width >= 79:
        canvas = Canvas(width, 19)
        x = (width - 78) // 2
        for y, row in enumerate(WORDMARK):
            canvas.text(x, y + 2, row)
        mobile(canvas, x + 50, 0, phase, amplitude)
        canvas.text(x + 1, 17, "Runs. Off script.", "muted")
        return canvas
    if width >= 50:
        canvas = Canvas(width, 33)
        mobile(canvas, (width - 28) // 2, 0, phase, amplitude)
        for y, row in enumerate(WORDMARK):
            canvas.text((width - 48) // 2, y + 17, row)
        canvas.text((width - 16) // 2, 31, "Runs. Off script.", "muted")
        return canvas
    canvas = Canvas(width, 4)
    canvas.text(1, 1, "flausen.")
    if width >= 20:
        canvas.text(1, 3, "Runs. Off script.", "muted")
    return canvas


def theme_from_environment():
    # COLORFGBG is optional; an explicit --theme always wins.
    try:
        bg = int(os.environ.get("COLORFGBG", "").split(";")[-1])
        return "light" if bg in (7, 15) else "dark"
    except ValueError:
        return "dark"


def finite_positive(value):
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="print a still greeting")
    parser.add_argument("--loop", action="store_true", help="continuous preview; Ctrl-C exits")
    parser.add_argument("--duration", type=finite_positive, default=3.2, help="startup animation in seconds (default: 3.2)")
    parser.add_argument("--fps", type=finite_positive, default=20, help="animation rate, capped at 30 (default: 20)")
    parser.add_argument("--width", type=int, help="artwork width (adapts to terminal by default)")
    parser.add_argument("--theme", choices=("dark", "light"), default=theme_from_environment())
    parser.add_argument("--no-color", action="store_true", help="plain ASCII, without colour")
    parser.add_argument("--system-info", action="store_true", help="show existing Fastfetch information during the animation")
    args = parser.parse_args(argv)

    tty = sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"
    columns, lines = shutil.get_terminal_size((80, 24))
    requested = args.width if args.width is not None else 80
    # Leave a column unused to prevent auto-wrap at the terminal's right edge.
    width = min(max(12, requested), max(1, columns - 1)) if tty else max(12, requested)
    frame = make_frame(width)
    color = tty and not args.no_color and "NO_COLOR" not in os.environ
    footer = []
    if args.system_info and shutil.which("fastfetch"):
        command = ["fastfetch", "--key-padding-left", "5", "--pipe", "false" if color else "true"]
        if shutil.which("fish"):
            # Fastfetch detects its parent as the shell. Keep Fish as its
            # parent, rather than reporting this Python greeting as the shell.
            command = ["fish", "--no-config", "-c", "command fastfetch $argv; true", "--"] + command[1:]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE, text=True, check=False,
        )
        footer = result.stdout.splitlines()
    # Count wrapped info rows too: cursor-up redraws must stay in the viewport.
    ansi = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    footer_height = sum(max(1, math.ceil(len(ansi.sub("", row)) / columns)) for row in footer)
    total_height = frame.height + footer_height
    animated = tty and not args.static and width >= 50 and lines >= total_height + 2

    def render(current):
        return current.ansi(args.theme, color) + footer
    # Respect the familiar reduced-motion conventions without depending on a GUI.
    if os.environ.get("REDUCE_MOTION", "").lower() in ("1", "true", "yes") or os.environ.get("FLAUSEN_MOTION", "").lower() in ("0", "off", "false"):
        animated = False
    if not animated:
        sys.stdout.write("\n".join(render(frame)) + "\n")
        return 0

    stopped = [False]
    def stop(signum, current_frame):
        stopped[0] = True

    old_handlers = {}
    for sig in (signal.SIGINT, signal.SIGTERM):
        old_handlers[sig] = signal.signal(sig, stop)
    period = 1 / min(30, args.fps)
    start, next_frame = time.monotonic(), time.monotonic()
    previous_height = total_height
    old_size = (columns, lines)
    first = True
    try:
        sys.stdout.write(ESC + "?25l")
        while not stopped[0]:
            elapsed = time.monotonic() - start
            if not args.loop and elapsed >= args.duration:
                break
            size = shutil.get_terminal_size((80, 24))
            if tuple(size) != old_size:
                # Stop on resize: cursor positions may already have reflowed.
                # Do not try to erase or redraw lines at guessed positions.
                break
            if args.loop:
                amplitude = 1.0
            else:
                # Gentle start and end; the last frame is the same resting pose
                # as the static text export, so nothing snaps before the prompt.
                progress = min(1.0, elapsed / args.duration)
                amplitude = math.sin(math.pi * progress) ** 2
            current = make_frame(width, elapsed * math.tau / 6, amplitude)
            if not first:
                sys.stdout.write(f"{ESC}{previous_height}A")
            sys.stdout.write("".join("\r" + line + ESC + "K\n" for line in render(current)))
            sys.stdout.flush()
            previous_height, first = total_height, False
            next_frame += period
            time.sleep(max(0, next_frame - time.monotonic()))
        if not first and tuple(shutil.get_terminal_size((80, 24))) == old_size:
            sys.stdout.write(f"{ESC}{previous_height}A")
            sys.stdout.write("".join("\r" + line + ESC + "K\n" for line in render(frame)))
    finally:
        sys.stdout.write(ESC + "0m" + ESC + "?25h")
        sys.stdout.flush()
        for sig, previous in old_handlers.items():
            signal.signal(sig, previous)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # A consumer such as `head` closing stdout is a normal pipeline event.
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        raise SystemExit(0)
