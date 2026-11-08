# Image Resizer (Python)

A small command-line tool that resizes images — one file, or a whole
folder at once. Built with Pillow.

## Install

```bash
pip install Pillow
```

## How to run

```bash
# One image, fit inside 800 px wide (aspect ratio kept)
python image_resizer.py photo.jpg --width 800

# Fit inside an 800 x 800 box
python image_resizer.py photo.jpg --width 800 --height 800

# Stretch to exactly 800 x 600 (ignores aspect ratio)
python image_resizer.py photo.jpg --width 800 --height 600 --stretch

# Smaller file: lower JPEG quality + convert to JPEG
python image_resizer.py photo.png --width 800 --quality 70 --format JPEG

# A whole folder (every jpg/png/webp/bmp inside it)
python image_resizer.py photos/ --width 800
python image_resizer.py photos/ --width 800 --out-dir photos-small/
```

By default the resized copy is saved next to the original as
`<name>_resized.<ext>` — the original is never overwritten.
Use `--output small.jpg` (single file) or `--out-dir` (folder mode)
to choose where the result goes.

## Options

| Option | Meaning |
| --- | --- |
| `--width` / `--height` | Target size in pixels (give one or both) |
| `--keep-aspect` | Fit inside the box without stretching (default) |
| `--stretch` | Force the exact width x height |
| `--quality 1–95` | JPEG/WebP compression (default 85) |
| `--format JPEG/PNG/WEBP/BMP` | Convert the output format |
| `--output` | Output file (single image only) |
| `--out-dir` | Output folder (folder mode only) |

## What I practiced

- Pillow: opening images, `resize()` with the LANCZOS filter, saving
  with quality/format options
- `pathlib` for file and folder handling
- `argparse` with flags that change behaviour (`--stretch`,
  `--keep-aspect`)
- Batch processing a folder with per-file error handling (one bad
  file doesn't stop the rest)
