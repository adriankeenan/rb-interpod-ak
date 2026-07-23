"""Shared c0..c100 <-> colour mapping for the Interpod-ak WPS.

The WPS drives its background (ID3 comment tag) and accent foreground (ID3
composer tag) from values named ``c0`` .. ``c100``. Each value's hue is a fixed
position on the wheel (hue = N * 3.6 degrees), so ``c0`` is red and the sweep
wraps back to red at ``c100``.

Saturation and brightness are **per hue**, not global: a flat, fully saturated
rainbow reads as too neon, and some hues (yellow/green/cyan) look harsher than
others at the same saturation. Both are defined by anchor points that are
linearly interpolated across c0..c100 -- edit the anchors below to taste and
re-run tools/generate_palette.py to regenerate the WPS tables and the palette
image.

Both the WPS generator (tools/generate_palette.py) and the album tagger
(tools/tag_album_colors.py) import this module so they agree on one mapping.
Stdlib only.
"""

import colorsys

# Number of distinct steps: c0 .. c100 inclusive.
STEPS = 101

# Per-hue saturation as (cN index, saturation 0..1) anchor points. Values
# between anchors are linearly interpolated. Lower = more muted. The harsher
# hues (yellow c17, green c33, cyan c50) are pulled down further than the
# deeper reds/blues/magentas.
SATURATION_ANCHORS = [
    (0, 0.72),    # red
    (17, 0.55),   # yellow
    (33, 0.60),   # green
    (50, 0.52),   # cyan
    (67, 0.78),   # blue
    (83, 0.70),   # magenta
    (100, 0.72),  # red (wrap)
]

# Per-hue brightness, same anchor format. Flat by default; drop individual
# hues here if any read as too bright.
VALUE_ANCHORS = [
    (0, 1.0),
    (100, 1.0),
]


def _interp(anchors, n):
    """Linearly interpolate an anchor table at index ``n``."""
    n = max(0, min(STEPS - 1, n))
    for i in range(len(anchors) - 1):
        x0, y0 = anchors[i]
        x1, y1 = anchors[i + 1]
        if x0 <= n <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (n - x0) / (x1 - x0)
    return anchors[-1][1]


def saturation_for(n):
    """Saturation (0..1) for palette index ``n``."""
    return _interp(SATURATION_ANCHORS, int(n))


def value_for(n):
    """Brightness (0..1) for palette index ``n``."""
    return _interp(VALUE_ANCHORS, int(n))


def cn_to_rgb(n):
    """Return the (r, g, b) tuple (0-255) for palette index ``n`` (0..100)."""
    n = max(0, min(STEPS - 1, int(n)))
    hue = (n * 3.6) / 360.0  # colorsys hue is 0..1
    r, g, b = colorsys.hsv_to_rgb(hue, saturation_for(n), value_for(n))
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
