# Tools

Helper scripts for the ID3-driven colours in the Interpod-ak WPS.

The theme drives two colours from the currently playing track's ID3 tags:

| Element                  | ID3 tag  | WPS tag |
|--------------------------|----------|---------|
| Full-screen background   | Comment  | `%iC`   |
| Accent foreground (artist) | Composer | `%ic`   |

Each tag holds a value `c00` .. `c99` from a 10×10 palette that is snapped to the
iPod Video's RGB565 display colours: the **units** digit picks the hue (0 red,
1 orange, 2 yellow, 3 yellow-green, 4 green, 5 cyan, 6 blue, 7 violet, 8 magenta,
9 neutral) and the **tens** digit picks the shade, from pale (0) to dark (9), so
every hue is available at ten saturation/brightness levels. See the reference
image at [`../docs/palette.png`](../docs/palette.png).

## `palette.py`

Shared, stdlib-only mapping (the `PALETTE` table plus `cn_to_hex`, `cn_to_rgb`,
`nearest_cn`) imported by
both scripts so the theme and the tagger agree on one palette.

## `generate_palette.py`

Regenerates the theme's colour tables and the reference image:

```sh
python tools/generate_palette.py
```

- Injects the 101 background conditionals into `.rockbox/wps/Interpod-ak.wps`
  between the `# BEGIN comment-bg` / `# END comment-bg` markers.
- Injects the 101 accent conditionals between `# BEGIN composer-fg` / `# END composer-fg`.
- Writes `docs/palette.png` (needs [Pillow]; falls back to a dependency-free
  `docs/palette.bmp` colour strip if Pillow is missing).

Re-running is idempotent. Run it after changing the palette formula in `palette.py`.

## `tag_album_colors.py`

Scans a music library and writes the colour tags into your FLAC files, deriving
them from each album's `cover.jpg`:

```sh
python tools/tag_album_colors.py /path/to/music
```

For every folder that contains a `cover.jpg` and one or more `.flac` files it:

- picks the **background** as the colour covering the most of the cover,
- picks the **accent** as the most vibrant colour on the cover,

snaps both to the nearest palette swatch, and writes `COMMENT` (background) and `COMPOSER`
(accent) into every FLAC in that folder.

Colour extraction uses [ColorThief]; tags are written with [pytaglib].

### Dependencies

```sh
pip install colorthief pytaglib
```

`generate_palette.py` additionally uses [Pillow] (installed as a ColorThief
dependency) for the labelled PNG.

[Pillow]: https://python-pillow.org/
[ColorThief]: https://github.com/fengsp/color-thief-py
[pytaglib]: https://github.com/supermihi/pytaglib
