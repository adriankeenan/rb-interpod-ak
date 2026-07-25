#!/usr/bin/env python3
"""Tag FLAC albums with the WPS colour values derived from their cover art.

For every ``cover.jpg`` found under a start directory, a Material You theme is
built from the cover and two of its roles are written into the tags the
Interpod-ak WPS reads, for each FLAC in the same folder:

  * background -> COMMENT   (the light scheme's ``primary``)
  * accent     -> COMPOSER  (the light scheme's ``tertiary``)

The light scheme is used so the accent stays legible on the theme's light info
panels. Both colours are snapped to the nearest palette swatch (tools/palette.py)
and stored as a ``c00`` .. ``c99`` value.

Usage:
    python tools/tag_album_colors.py <start_folder>

Requires: material-color-utilities-python, pytaglib
"""

import glob
import os
import sys

from material_color_utilities_python import themeFromImage, hexFromArgb, Image
import taglib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette  # noqa: E402


def _rgb(hex_str):
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/tag_album_colors.py <start_folder>")
    start = sys.argv[1]

    for cover in sorted(glob.glob(os.path.join(start, "**", "cover.jpg"), recursive=True)):
        scheme = themeFromImage(Image.open(cover))["schemes"]["light"]
        bg = palette.cn_name(palette.nearest_cn(_rgb(hexFromArgb(scheme.primary))))
        accent = palette.cn_name(palette.nearest_cn(_rgb(hexFromArgb(scheme.tertiary))))

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
