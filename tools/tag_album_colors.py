#!/usr/bin/env python3
"""Tag FLAC albums with the WPS colour values derived from their cover art.

For every folder under a start directory that contains a ``cover.jpg`` and one
or more ``.flac`` files, this derives two colours from the cover and writes them
into the tags the Interpod-ak WPS reads:

  * background  -> COMMENT   (the dominant colour of the cover)
  * accent      -> COMPOSER  (the most vibrant colour of the cover)

Each is stored as a ``c0`` .. ``c100`` value using the same vivid-rainbow
mapping as the theme (tools/palette.py).

Colour extraction uses the purpose-built ColorThief library; tags are written
with pytaglib.

Usage:
    python tools/tag_album_colors.py <start_folder>

Requires: colorthief, pytaglib
"""

import colorsys
import os
import sys

from colorthief import ColorThief
from PIL import Image
import taglib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette  # noqa: E402

COVER_NAME = "cover.jpg"

# A palette entry must clear these to count as a usable accent, otherwise it is
# a near-grey or near-black that has no meaningful hue.
MIN_SAT = 0.20
MIN_VAL = 0.15


def _hue(rgb):
    r, g, b = rgb
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[0] * 360.0


def _vibrance(rgb):
    r, g, b = rgb
    _, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return s, v


def _coverage_dominant(cover_path, swatches):
    """Return the swatch that covers the most image area.

    ColorThief's get_color favours vivid colours over area, which is wrong for
    a background. So assign each (down-sampled) pixel to its nearest swatch and
    pick the swatch with the most pixels.
    """
    img = Image.open(cover_path).convert("RGB")
    img.thumbnail((120, 120))
    w, h = img.size
    counts = [0] * len(swatches)
    for count, px in img.getcolors(maxcolors=w * h):
        best_i = 0
        best_d = None
        for i, c in enumerate(swatches):
            d = (px[0] - c[0]) ** 2 + (px[1] - c[1]) ** 2 + (px[2] - c[2]) ** 2
            if best_d is None or d < best_d:
                best_d = d
                best_i = i
        counts[best_i] += count
    return swatches[counts.index(max(counts))]


def colours_for_cover(cover_path):
    """Return (bg_cn, accent_cn) for a cover image."""
    thief = ColorThief(cover_path)
    try:
        swatches = thief.get_palette(color_count=8, quality=1)
    except Exception:
        swatches = []
    if not swatches:
        swatches = [thief.get_color(quality=1)]

    # Background = the colour covering the most area of the cover.
    bg_rgb = _coverage_dominant(cover_path, swatches)
    bg_cn = palette.hue_to_cn(_hue(bg_rgb))

    # Accent = the most vibrant swatch (highest saturation * value), skipping
    # near-grey / near-black entries that have no meaningful hue.
    best = None
    best_score = -1.0
    for rgb in swatches:
        s, v = _vibrance(rgb)
        if s < MIN_SAT or v < MIN_VAL:
            continue
        score = s * v
        if score > best_score:
            best_score = score
            best = rgb
    accent_rgb = best if best is not None else bg_rgb
    accent_cn = palette.hue_to_cn(_hue(accent_rgb))

    return bg_cn, accent_cn


def flacs_in(folder):
    return sorted(
        f for f in os.listdir(folder) if f.lower().endswith(".flac")
    )


def tag_album(folder, bg_cn, accent_cn):
    bg = palette.cn_name(bg_cn)
    accent = palette.cn_name(accent_cn)
    for name in flacs_in(folder):
        path = os.path.join(folder, name)
        song = taglib.File(path)
        song.tags["COMMENT"] = [bg]
        song.tags["COMPOSER"] = [accent]
        song.save()
        song.close()


def process(start_folder):
    albums = 0
    for root, _dirs, files in os.walk(start_folder):
        names = set(files)
        if COVER_NAME not in names:
            continue
        if not any(f.lower().endswith(".flac") for f in files):
            continue
        cover_path = os.path.join(root, COVER_NAME)
        try:
            bg_cn, accent_cn = colours_for_cover(cover_path)
        except Exception as exc:  # noqa: BLE001 - keep going on a bad cover
            print("%s: SKIPPED (%s)" % (root, exc))
            continue
        tag_album(root, bg_cn, accent_cn)
        albums += 1
        print(
            "%s: bg=%s accent=%s"
            % (root, palette.cn_name(bg_cn), palette.cn_name(accent_cn))
        )
    print("Tagged %d album(s)." % albums)


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python tools/tag_album_colors.py <start_folder>\n")
        return 2
    start = argv[1]
    if not os.path.isdir(start):
        sys.stderr.write("not a directory: %s\n" % start)
        return 2
    process(start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
