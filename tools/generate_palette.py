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
