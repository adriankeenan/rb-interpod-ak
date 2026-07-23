"""Shared c00..c99 <-> colour mapping for the Interpod-ak WPS.

The WPS drives its background (ID3 comment tag) and accent foreground (ID3
composer tag) from values named ``c00`` .. ``c99``. The palette is a 10x10 grid,
snapped to the iPod Video's RGB565 display colour space:

  * the **units** digit selects the hue
    (0 red, 1 orange, 2 yellow, 3 yellow-green, 4 green, 5 cyan, 6 blue,
     7 violet, 8 magenta, 9 neutral/grey)
  * the **tens** digit selects the shade, from pale/light (0) to dark (9)

so every hue is available at ten different saturation/brightness levels.

Both the WPS generator (tools/generate_palette.py) and the album tagger
(tools/tag_album_colors.py) import this module so they agree on one mapping.
Stdlib only.
"""

# Row-major, index = tens*10 + units (c00 .. c99). Values are RGB565-snapped.
PALETTE = [
    # c0x  pale
    "f7aead", "f7c7ad", "f7dbad", "d6f3ad", "adf3d6",
    "adf3f7", "add3f7", "c6aef7", "f7aee7", "efefef",
    # c1x
    "de9294", "deae94", "dec794", "bddf94", "94dfbd",
    "94dfde", "94bade", "ad92de", "de92d6", "dedbde",
    # c2x
    "ce797b", "ce9a7b", "ceb27b", "a5cf7b", "7bcfa5",
    "7bcfce", "7ba6ce", "9479ce", "ce79c6", "c6c3c6",
    # c3x
    "bd6163", "bd8263", "bd9e63", "8cba63", "63ba94",
    "63babd", "6392bd", "7b61bd", "bd61ad", "adaead",
    # c4x
    "ad4d4a", "ad6d4a", "ad8a4a", "7baa4a", "4aaa7b",
    "4aaaad", "4a7dad", "6b4dad", "ad4d9c", "949694",
    # c5x
    "943c39", "945d39", "947939", "6b9639", "39966b",
    "399694", "396994", "5a3c94", "943c8c", "7b7d7b",
    # c6x
    "842c29", "844d29", "846529", "5a8629", "29865a",
    "298684", "295984", "4a2c84", "842c73", "6b696b",
    # c7x
    "732021", "733c21", "735521", "4a7121", "21714a",
    "217173", "214973", "392073", "732063", "525152",
    # c8x  dark
    "5a1410", "5a3010", "5a4510", "395d10", "105d39",
    "105d5a", "10385a", "29145a", "5a1452", "393c39",
    # c9x  darkest
    "4a0c08", "4a2008", "4a3408", "294d08", "084d29",
    "084d4a", "082c4a", "210c4a", "4a0c42", "212421",
]

# Number of palette entries: c00 .. c99.
STEPS = len(PALETTE)

# Grid dimensions (columns = hues, rows = shades).
COLS = 10
ROWS = STEPS // COLS


def cn_to_hex(n):
    """Return the lowercase 6-digit hex string for palette index ``n`` (0..99)."""
    return PALETTE[max(0, min(STEPS - 1, int(n)))]


def cn_to_rgb(n):
    """Return the (r, g, b) tuple (0-255) for palette index ``n`` (0..99)."""
    h = cn_to_hex(n)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def cn_name(n):
    """Return the zero-padded tag value string, e.g. ``c05`` or ``c73``."""
    return "c%02d" % int(n)


def nearest_cn(rgb):
    """Return the palette index whose colour is closest to ``rgb``.

    Plain squared-Euclidean distance in RGB - good enough for matching a
    cover-art colour to the nearest swatch (hue and shade together).
    """
    r, g, b = rgb
    best_i = 0
    best_d = None
    for i in range(STEPS):
        pr, pg, pb = cn_to_rgb(i)
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if best_d is None or d < best_d:
            best_d = d
            best_i = i
    return best_i
