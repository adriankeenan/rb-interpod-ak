"""Shared c0..c100 <-> colour mapping for the Interpod-ak WPS.

The WPS drives its background (ID3 comment tag) and accent foreground (ID3
composer tag) from values named ``c0`` .. ``c100``. Each value is a position
on a vivid rainbow: hue = N * 3.6 degrees at full saturation and value, so
``c0`` is red and the sweep wraps back to red at ``c100``.

Both the WPS generator (tools/generate_palette.py) and the album tagger
(tools/tag_album_colors.py) import this module so they agree on one mapping.
Stdlib only.
"""

import colorsys

# Number of distinct steps: c0 .. c100 inclusive.
STEPS = 101


def cn_to_rgb(n):
    """Return the (r, g, b) tuple (0-255) for palette index ``n`` (0..100)."""
    n = max(0, min(STEPS - 1, int(n)))
    hue = (n * 3.6) / 360.0  # colorsys hue is 0..1
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return (round(r * 255), round(g * 255), round(b * 255))


def cn_to_hex(n):
    """Return the lowercase 6-digit hex string for palette index ``n``."""
    r, g, b = cn_to_rgb(n)
    return "%02x%02x%02x" % (r, g, b)


def hue_to_cn(hue):
    """Map a hue in degrees (0..360) to the nearest palette index (0..100)."""
    return int(round((hue % 360.0) / 3.6)) % STEPS


def cn_name(n):
    """Return the tag value string, e.g. ``c50``."""
    return "c%d" % int(n)
