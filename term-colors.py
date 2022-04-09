import json
import sys


BLACK = 20, 20, 20
BRIGHT_BLACK = 38, 38, 38
RED = 192, 109, 68
BRIGHT_RED = 222, 124, 76
GREEN = 175, 185, 122
BRIGHT_GREEN = 204, 216, 140
YELLOW = 194, 168, 108
BRIGHT_YELLOW = 226, 196, 126
BLUE = 68, 71, 74
BRIGHT_BLUE = 90, 94, 98
MAGENTA = 164, 124, 190
BRIGHT_MAGENTA = 177, 142, 199
CYAN = 119, 131, 133
BRIGHT_CYAN = 138, 152, 155
WHITE = 255, 255, 212
BRIGHT_WHITE = 255, 255, 255


def hex(r, g, b):
    return f"#{r:X}{g:X}{b:X}"


def mintty():
    colors = {
        "BackgroundColour": BLACK,
        "ForegroundColour": WHITE,
        "CursorColour": WHITE,
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
    print(f"background: {hex(*BLACK)}")
    print(f"foreground: {hex(*WHITE)}")
    for index, rgb in colors.items():
        print(f"color{index}: {hex(*rgb)}")


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
    inner_dict["terminal.background"] = hex(*BLACK)
    inner_dict["terminal.foreground"] = hex(*WHITE)
    for name, rgb in colors.items():
        inner_dict[f"terminal.ansi{name}"] = hex(*rgb)
    print(json.dumps(outer_dict, indent=4))


if __name__ == "__main__":
    def invalid_args():
        name = sys.argv[0] or "term-colors.py"
        print(f"Usage: {name} {{ mintty | termux | vscode }}", file=sys.stderr)
        sys.exit(2)

    if len(sys.argv) < 2:
        invalid_args()
    arg = sys.argv[1]
    if arg == "mintty":
        mintty()
    elif arg == "termux":
        termux()
    elif arg == "vscode":
        vscode()
    else:
        invalid_args()
