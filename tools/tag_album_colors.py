#!/usr/bin/env python3
"""Tag FLAC albums with the WPS colour values derived from their cover art.

For every ``cover.jpg`` found under a start directory, two colours are extracted
with Material You and written into the tags the Interpod-ak WPS reads, for each
FLAC in the same folder:

  * background -> COMMENT   (Material You's top-ranked colour)
  * accent     -> COMPOSER  (its second colour)

Both are snapped to the nearest palette swatch (tools/palette.py) and stored as
a ``c00`` .. ``c99`` value.

Usage:
    python tools/tag_album_colors.py <start_folder>

Requires: materialyoucolor, pytaglib
"""

import glob
import os
import sys

from materialyoucolor.quantize import ImageQuantizeCelebi
from materialyoucolor.score.score import Score
import taglib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette  # noqa: E402


def _rgb(argb):
    return ((argb >> 16) & 0xFF, (argb >> 8) & 0xFF, argb & 0xFF)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/tag_album_colors.py <start_folder>")
    start = sys.argv[1]

    for cover in sorted(glob.glob(os.path.join(start, "**", "cover.jpg"), recursive=True)):
        colours = Score.score(ImageQuantizeCelebi(cover, 1, 128))
        bg = palette.cn_name(palette.nearest_cn(_rgb(colours[0])))
        accent = palette.cn_name(palette.nearest_cn(_rgb(colours[1 % len(colours)])))

        folder = os.path.dirname(cover)
        for flac in sorted(glob.glob(os.path.join(folder, "*.flac"))):
            song = taglib.File(flac)
            song.tags["COMMENT"] = [bg]
            song.tags["COMPOSER"] = [accent]
            song.save()
            song.close()

        print("%s: bg=%s accent=%s" % (folder, bg, accent))


if __name__ == "__main__":
    main()
