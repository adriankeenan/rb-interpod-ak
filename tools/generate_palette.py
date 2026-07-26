#!/usr/bin/env python3
"""Generate the Interpod-ak WPS colour blocks and a palette reference image.

Outputs, all derived from the single mapping in tools/palette.py:

  1. Injects the background block (comment tag -> full-screen %dr fill) into the
     WPS between the ``# BEGIN comment-bg`` / ``# END comment-bg`` markers.
  2. Injects the accent block (composer tag -> %Vf) between the
     ``# BEGIN composer-fg`` / ``# END composer-fg`` markers.
  3. Renders docs/palette.png (a labelled grid of all 101 swatches). Falls back
     to a dependency-free docs/palette.bmp if Pillow is not installed.

Re-running is idempotent: a second run leaves the tree unchanged.

Usage:
    python tools/generate_palette.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WPS_PATH = os.path.join(REPO_ROOT, ".rockbox", "wps", "Interpod-ak.wps")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

# iPod Video screen dimensions (the theme's target).
SCREEN_W = 320
SCREEN_H = 240


def _bg_block():
    """Comment tag cN -> full-screen fill, as a SINGLE line of conditionals.

    All conditionals live on one physical line so the viewport gains no extra
    display lines (each newline-separated line advances the skin engine's line
    counter). Exactly one conditional matches and fires its %dr fill.
    """
    conds = "".join(
        "%%?if(%%iC,=,%s)<%%dr(0,0,%d,%d,%s)>"
        % (palette.cn_name(n), SCREEN_W, SCREEN_H, palette.cn_to_hex(n))
        for n in range(palette.STEPS)
    )
    return [conds]


def _fg_block():
    """Composer tag cN -> accent foreground, as a SINGLE line of conditionals.

    Prefixed with the fallback %Vf(f24e61): %Vf is a NOBREAK tag, so a leading
    one keeps this line from advancing the line counter (the artist text on the
    next line stays at the top of its viewport), and it sets the accent back to
    the theme pink when the composer tag isn't a cNN value. A matching
    conditional overrides it; the chosen foreground persists to the text line.
    """
    conds = "".join(
        "%%?if(%%ic,=,%s)<%%Vf(%s)>" % (palette.cn_name(n), palette.cn_to_hex(n))
        for n in range(palette.STEPS)
    )
    return ["%Vf(f24e61)" + conds]


def _panel_bg_block(fallback_hex):
    """Comment tag cNN -> panel background, matching the main fill EXACTLY.

    write_line() (skin_display.c) paints an opaque background rectangle behind
    EVERY rendered line - text or icon - using the viewport's %Vb colour, so a
    solid fill can never be made transparent. The only fix is to give each
    panel the SAME colour as the main fill, so its box blends in seamlessly.

    A flat 100-way exact match (one %?if(%iC,=,cNN) per value, like the main
    fill uses) costs ~2 tokens per branch; duplicated across every panel this
    blows Rockbox's skin memory budget ("Memory limit exceeded" from checkwps
    once ~9 panels had a copy). Instead this uses %ss(start,len,TAG,number),
    which extracts a substring AND reports its numeric value as a 1-based
    branch index (skin_tokens.c: SKIN_TOKEN_SUBSTRING's expect_number path) -
    the same mechanism tags like %mp/%bl use for their own <branch|branch|...>
    forms. Nesting one 10-way selector (hue digit) inside another (shade
    digit) reconstructs the exact 100-value lookup in ~1/4 the tokens of the
    flat form, since only ~20 branches are declared instead of 100.

    Guarding this against an empty/untagged comment is trickier than it looks:
    %?if cannot wrap a nested tag that itself has 3+ pipe-branches (confirmed
    empirically - checkwps reports "Expected list close" / "Parser callback
    returned error" for that shape), so a prefix check like "does %iC start
    with c" can't be layered on top here. Instead this relies on a different,
    already-safe fallback path: when %iC is empty, %ss returns NULL *before*
    computing a branch index, so evaluate_conditional's index is left at its
    untouched default of num_options - i.e. the LAST branch. Declaring an 11th
    outer (shade) branch and putting the fallback colour there means an empty
    comment naturally lands on it, no guard needed. (A non-digit character in
    an otherwise-present comment instead lands on the FIRST branch regardless
    of branch count - Rockbox's own evaluate_conditional behaviour, not
    something decidable from the skin file - so that narrower case, e.g. a
    pre-existing comment that happens to be exactly "cX?" for digit X and
    non-digit ?, can still render an unintended colour. Anything written by
    tools/tag_album_colors.py is always exactly "cNN" and unaffected.)
    """
    shade_branches = []
    for shade in range(10):
        hue_branches = [
            "%%Vb(%s)" % palette.cn_to_hex(shade * 10 + hue) for hue in range(10)
        ]
        shade_branches.append("%%ss(-1,1,%%iC,number)<%s>" % "|".join(hue_branches))
    shade_branches.append("%%Vb(%s)" % fallback_hex)  # 11th branch: empty %iC fallback
    return ["%%ss(1,1,%%iC,number)<%s>" % "|".join(shade_branches)]


# Every other panel viewport that sets its own background colour, so it can be
# made to track the main fill instead of standing out as a mismatched box.
# (marker name, original/fallback hex). Keep in sync with Interpod-ak.wps.
PANEL_BACKGROUNDS = [
    ("panelbg-status-icon", "f8f8f8"),
    ("panelbg-battery-icon", "f8f8f8"),
    ("panelbg-hold-lock", "f8f8f8"),
    ("panelbg-hold-unlocked", "f8f8f8"),
    ("panelbg-battery-text", "f8f8f8"),
    ("panelbg-clock", "f8f8f8"),
    ("panelbg-repeat-shuffle", "f8f8f8"),
    ("panelbg-playlist-pos", "f8f8f8"),
    ("panelbg-title", "f8f8f8"),
    ("panelbg-artist", "f8f8f8"),
    ("panelbg-progress", "E0E0E0"),
    ("panelbg-progress-active", "E0E0E0"),
    ("panelbg-time-elapsed", "f8f8f8"),
    ("panelbg-codec", "f8f8f8"),
    ("panelbg-time-remaining", "f8f8f8"),
    ("panelbg-volumebar", "ededed"),
]


def _inject(text, begin_marker, end_marker, block_lines):
    """Replace the content between two marker lines with block_lines."""
    lines = text.splitlines()
    try:
        begin = next(i for i, l in enumerate(lines) if l.strip() == begin_marker)
        end = next(i for i, l in enumerate(lines) if l.strip() == end_marker)
    except StopIteration:
        raise SystemExit(
            "markers %r / %r not found in %s" % (begin_marker, end_marker, WPS_PATH)
        )
    if end < begin:
        raise SystemExit("end marker precedes begin marker in %s" % WPS_PATH)
    new_lines = lines[: begin + 1] + block_lines + lines[end:]
    trailing_nl = "\n" if text.endswith("\n") else ""
    return "\n".join(new_lines) + trailing_nl


def inject_wps():
    with open(WPS_PATH, "r") as fh:
        text = fh.read()
    updated = _inject(text, "# BEGIN comment-bg", "# END comment-bg", _bg_block())
    updated = _inject(updated, "# BEGIN composer-fg", "# END composer-fg", _fg_block())
    for name, fallback_hex in PANEL_BACKGROUNDS:
        updated = _inject(
            updated,
            "# BEGIN %s" % name,
            "# END %s" % name,
            _panel_bg_block(fallback_hex),
        )
    if updated != text:
        with open(WPS_PATH, "w") as fh:
            fh.write(updated)
        print("updated %s" % os.path.relpath(WPS_PATH, REPO_ROOT))
    else:
        print("%s already up to date" % os.path.relpath(WPS_PATH, REPO_ROOT))


# --------------------------------------------------------------------------- #
# Palette reference image
# --------------------------------------------------------------------------- #

COLS = palette.COLS
CELL = 140
GAP = 4
MARGIN = 20
TITLE_H = 44
BG = (26, 26, 26)


def _render_png(path):
    from PIL import Image, ImageDraw, ImageFont

    rows = (palette.STEPS + COLS - 1) // COLS
    width = MARGIN * 2 + COLS * CELL + (COLS - 1) * GAP
    height = MARGIN + TITLE_H + rows * CELL + (rows - 1) * GAP + MARGIN
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    try:
        name_font = ImageFont.load_default(size=20)
        hex_font = ImageFont.load_default(size=15)
        title_font = ImageFont.load_default(size=26)
    except TypeError:  # older Pillow: load_default takes no size
        name_font = hex_font = title_font = ImageFont.load_default()

    draw.text(
        (MARGIN, MARGIN),
        "Interpod-ak WPS palette - 100 colours, RGB565-snapped",
        fill=(235, 235, 235),
        font=title_font,
    )
    for n in range(palette.STEPS):
        col = n % COLS
        row = n // COLS
        x = MARGIN + col * (CELL + GAP)
        y = MARGIN + TITLE_H + row * (CELL + GAP)
        rgb = palette.cn_to_rgb(n)
        draw.rectangle([x, y, x + CELL, y + CELL], fill=rgb)
        # Readable label colour: white on dark swatches, black on light ones.
        luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
        ink = (20, 20, 20) if luminance > 140 else (245, 245, 245)
        draw.text((x + 8, y + 6), palette.cn_name(n), fill=ink, font=name_font)
        draw.text((x + 8, y + 30), palette.cn_to_hex(n), fill=ink, font=hex_font)
    img.save(path)
    print("wrote %s" % os.path.relpath(path, REPO_ROOT))


def _render_bmp(path):
    """Dependency-free fallback: a simple colour strip (one column per swatch) as a BMP."""
    strip_h = 120
    width = palette.STEPS
    height = strip_h
    row_padded = (width * 3 + 3) & ~3
    pixel_data_size = row_padded * height
    file_size = 54 + pixel_data_size

    def le(value, size):
        return value.to_bytes(size, "little")

    header = b"BM" + le(file_size, 4) + le(0, 4) + le(54, 4)
    dib = (
        le(40, 4) + le(width, 4) + le(height, 4) + le(1, 2) + le(24, 2)
        + le(0, 4) + le(pixel_data_size, 4) + le(2835, 4) + le(2835, 4)
        + le(0, 4) + le(0, 4)
    )
    rows = []
    for _ in range(height):  # every row is the same colour strip
        row = bytearray()
        for n in range(width):
            r, g, b = palette.cn_to_rgb(n)
            row += bytes((b, g, r))  # BMP is BGR
        row += b"\x00" * (row_padded - len(row))
        rows.append(bytes(row))
    with open(path, "wb") as fh:
        fh.write(header + dib)
        for row in reversed(rows):  # BMP rows are bottom-up
            fh.write(row)
    print("wrote %s (Pillow not available; text labels omitted)" % os.path.relpath(path, REPO_ROOT))


def render_image():
    if not os.path.isdir(DOCS_DIR):
        os.makedirs(DOCS_DIR)
    try:
        _render_png(os.path.join(DOCS_DIR, "palette.png"))
    except ImportError:
        _render_bmp(os.path.join(DOCS_DIR, "palette.bmp"))


def main():
    inject_wps()
    render_image()


if __name__ == "__main__":
    main()
