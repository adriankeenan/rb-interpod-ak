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
    """Flat conditionals: comment tag cN -> full-screen fill of that colour."""
    lines = []
    for n in range(palette.STEPS):
        lines.append(
            "%%?if(%%iC,=,%s)<%%dr(0,0,%d,%d,%s)>"
            % (palette.cn_name(n), SCREEN_W, SCREEN_H, palette.cn_to_hex(n))
        )
    return lines


def _fg_block():
    """Flat conditionals: composer tag cN -> accent foreground of that colour."""
    lines = []
    for n in range(palette.STEPS):
        lines.append(
            "%%?if(%%ic,=,%s)<%%Vf(%s)>" % (palette.cn_name(n), palette.cn_to_hex(n))
        )
    return lines


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

COLS = 10
SWATCH = 96
PAD = 8
LABEL_H = 26


def _render_png(path):
    from PIL import Image, ImageDraw, ImageFont

    rows = (palette.STEPS + COLS - 1) // COLS
    cell_w = SWATCH + PAD
    cell_h = SWATCH + LABEL_H + PAD
    width = COLS * cell_w + PAD
    height = rows * cell_h + PAD
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    for n in range(palette.STEPS):
        col = n % COLS
        row = n // COLS
        x = PAD + col * cell_w
        y = PAD + row * cell_h
        draw.rectangle([x, y, x + SWATCH, y + SWATCH], fill=palette.cn_to_rgb(n))
        label = "%s  #%s" % (palette.cn_name(n), palette.cn_to_hex(n))
        draw.text((x, y + SWATCH + 6), label, fill=(0, 0, 0), font=font)
    img.save(path)
    print("wrote %s" % os.path.relpath(path, REPO_ROOT))


def _render_bmp(path):
    """Dependency-free fallback: a simple 101-column colour strip as a BMP."""
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
