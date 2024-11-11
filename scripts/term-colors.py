#!/usr/bin/env python

import json
import sys


BACKGROUND = 0, 0, 0
FOREGROUND = 255, 255, 212
CURSOR = FOREGROUND

BLACK = 24, 24, 24
BRIGHT_BLACK = 96, 96, 96
RED = 192, 109, 68
BRIGHT_RED = 222, 124, 76
GREEN = 175, 185, 122
BRIGHT_GREEN = 204, 216, 140
YELLOW = 194, 168, 108
BRIGHT_YELLOW = 226, 196, 126
BLUE = 107, 149, 191
BRIGHT_BLUE = 127, 177, 227
MAGENTA = 164, 124, 190
BRIGHT_MAGENTA = 177, 142, 199
CYAN = 119, 131, 133
BRIGHT_CYAN = 138, 152, 155
WHITE = FOREGROUND
BRIGHT_WHITE = 255, 255, 255


def hex_color(r, g, b):
    return f"#{r:x}{g:x}{b:x}"


def alacritty():
    normal = {
        "black": BLACK,
        "blue": BLUE,
        "cyan": CYAN,
        "green": GREEN,
        "magenta": MAGENTA,
        "red": RED,
        "white": WHITE,
        "yellow": YELLOW,
    }
    bright = {
        "black": BRIGHT_BLACK,
        "blue": BRIGHT_BLUE,
        "cyan": BRIGHT_CYAN,
        "green": BRIGHT_GREEN,
        "magenta": BRIGHT_MAGENTA,
        "red": BRIGHT_RED,
        "white": BRIGHT_WHITE,
        "yellow": BRIGHT_YELLOW,
    }

    print("[colors.normal]")
    for color, rgb in normal.items():
        print(f'{color} = "{hex_color(*rgb)}"')

    print("\n[colors.bright]")
    for color, rgb in bright.items():
        print(f'{color} = "{hex_color(*rgb)}"')

    print("\n[colors.primary]")
    print(f'background = "{hex_color(*BACKGROUND)}"')
    print(f'foreground = "{hex_color(*FOREGROUND)}"')


def mintty():
    colors = {
        "BackgroundColour": BACKGROUND,
        "ForegroundColour": FOREGROUND,
        "CursorColour": CURSOR,
        "Black": BLACK,
        "Red": RED,
        "Green": GREEN,
        "Yellow": YELLOW,
        "Blue": BLUE,
        "Magenta": MAGENTA,
        "Cyan": CYAN,
        "White": WHITE,
        "BoldBlack": BRIGHT_BLACK,
        "BoldRed": BRIGHT_RED,
        "BoldGreen": BRIGHT_GREEN,
        "BoldYellow": BRIGHT_YELLOW,
        "BoldBlue": BRIGHT_BLUE,
        "BoldMagenta": BRIGHT_MAGENTA,
        "BoldCyan": BRIGHT_CYAN,
        "BoldWhite": BRIGHT_WHITE,
    }
    for name, (r, g, b) in colors.items():
        print(f"{name}={r},{g},{b}")


def termux():
    colors = {
        0: BLACK,
        1: RED,
        2: GREEN,
        3: YELLOW,
        4: BLUE,
        5: MAGENTA,
        6: CYAN,
        7: WHITE,
        8: BRIGHT_BLACK,
        9: BRIGHT_RED,
        10: BRIGHT_GREEN,
        11: BRIGHT_YELLOW,
        12: BRIGHT_BLUE,
        13: BRIGHT_MAGENTA,
        14: BRIGHT_CYAN,
        15: BRIGHT_WHITE,
    }
    print(f"background: {hex_color(*BACKGROUND)}")
    print(f"foreground: {hex_color(*FOREGROUND)}")
    for index, rgb in colors.items():
        print(f"color{index}: {hex_color(*rgb)}")


def vscode():
    colors = {
        "Black": BLACK,
        "Red": RED,
        "Green": GREEN,
        "Yellow": YELLOW,
        "Blue": BLUE,
        "Magenta": MAGENTA,
        "Cyan": CYAN,
        "White": WHITE,
        "BrightBlack": BRIGHT_BLACK,
        "BrightRed": BRIGHT_RED,
        "BrightGreen": BRIGHT_GREEN,
        "BrightYellow": BRIGHT_YELLOW,
        "BrightBlue": BRIGHT_BLUE,
        "BrightMagenta": BRIGHT_MAGENTA,
        "BrightCyan": BRIGHT_CYAN,
        "BrightWhite": BRIGHT_WHITE,
    }
    inner_dict = {}
    outer_dict = {
        "workbench.colorCustomizations": inner_dict
    }
    inner_dict["terminal.background"] = hex_color(*BACKGROUND)
    inner_dict["terminal.foreground"] = hex_color(*FOREGROUND)
    for name, rgb in colors.items():
        inner_dict[f"terminal.ansi{name}"] = hex_color(*rgb)
    print(json.dumps(outer_dict, indent=4))


if __name__ == "__main__":
    def invalid_args():
        name = sys.argv[0] or "term-colors.py"
        print(f"Usage: {name} {{ alacritty | mintty | termux | vscode }}", file=sys.stderr)
        sys.exit(2)

    if len(sys.argv) < 2:
        invalid_args()
    arg = sys.argv[1]
    if arg == "alacritty":
        alacritty()
    elif arg == "mintty":
        mintty()
    elif arg == "termux":
        termux()
    elif arg == "vscode":
        vscode()
    else:
        invalid_args()
