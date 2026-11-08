#!/usr/bin/env python3
"""
Image Resizer — resize images from the command line (Pillow).

Usage:
    python image_resizer.py photo.jpg --width 800
    python image_resizer.py photo.jpg --height 600
    python image_resizer.py photo.jpg --width 800 --height 800 --keep-aspect
    python image_resizer.py photo.jpg --width 800 --output small.jpg
    python image_resizer.py photos/ --width 800            # whole folder
    python image_resizer.py photo.png --width 800 --quality 70 --format JPEG

What it does:
    - Resizes one image, or every image in a folder (jpg/jpeg/png/webp/bmp).
    - Keeps the aspect ratio by default (fits inside the given box).
    - Optional --keep-aspect off: stretches to the exact width x height.
    - Saves next to the original as <name>_resized.<ext> unless --output
      (or --out-dir for folders) is given.
    - --quality controls JPEG/WebP compression (1-95, default 85).

Install Pillow first:
    pip install Pillow
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def target_size(img, width, height, keep_aspect):
    """Work out the (width, height) the image should become."""
    orig_w, orig_h = img.size
    if width and height:
        if not keep_aspect:
            return (width, height)
        scale = min(width / orig_w, height / orig_h)
        return (max(1, round(orig_w * scale)), max(1, round(orig_h * scale)))
    if width:
        scale = width / orig_w
        return (width, max(1, round(orig_h * scale)))
    if height:
        scale = height / orig_h
        return (max(1, round(orig_w * scale)), height)
    return img.size


def resize_one(src, width, height, keep_aspect, quality, out_format, output):
    """Resize one image file. Returns the output path."""
    with Image.open(src) as img:
        new_size = target_size(img, width, height, keep_aspect)
        resized = img.resize(new_size, Image.LANCZOS)

        fmt = (out_format or img.format or "JPEG").upper()
        if fmt == "JPG":
            fmt = "JPEG"
        ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "BMP": ".bmp"}.get(fmt, ".jpg")

        if output is None:
            output = src.with_stem(src.stem + "_resized").with_suffix(ext)
        else:
            output = Path(output)
            if output.suffix.lower() not in SUPPORTED_EXTENSIONS:
                output = output.with_suffix(ext)

        save_kwargs = {}
        if fmt in ("JPEG", "WEBP"):
            save_kwargs["quality"] = quality
            if resized.mode in ("RGBA", "LA", "P"):
                resized = resized.convert("RGB")

        resized.save(output, format=fmt, **save_kwargs)
        return output, img.size, new_size


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Resize images (single file or whole folder) with Pillow."
    )
    parser.add_argument("input", help="image file or folder of images")
    parser.add_argument("--width", type=int, help="target width in pixels")
    parser.add_argument("--height", type=int, help="target height in pixels")
    parser.add_argument("--keep-aspect", action="store_true", default=True,
                        help="fit inside width x height without stretching (default)")
    parser.add_argument("--stretch", dest="keep_aspect", action="store_false",
                        help="stretch to the exact width x height")
    parser.add_argument("--quality", type=int, default=85,
                        help="JPEG/WebP quality 1-95 (default 85)")
    parser.add_argument("--format", dest="out_format",
                        choices=["JPEG", "PNG", "WEBP", "BMP"],
                        help="output format (default: keep the original)")
    parser.add_argument("--output", help="output file (single image only)")
    parser.add_argument("--out-dir", help="output folder (folder mode only)")
    args = parser.parse_args(argv)

    if not args.width and not args.height:
        print("Error: give --width and/or --height.")
        return 1
    if args.width is not None and args.width <= 0 or args.height is not None and args.height <= 0:
        print("Error: width and height must be positive numbers.")
        return 1
    if not 1 <= args.quality <= 95:
        print("Error: --quality must be between 1 and 95.")
        return 1

    src = Path(args.input)
    if not src.exists():
        print(f"Error: {src} does not exist.")
        return 1

    if src.is_dir():
        if args.output:
            print("Error: --output works for a single image only; use --out-dir for folders.")
            return 1
        files = sorted(p for p in src.iterdir()
                       if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)
        if not files:
            print(f"No supported images found in {src} (jpg, png, webp, bmp).")
            return 1
        out_dir = Path(args.out_dir) if args.out_dir else src
        out_dir.mkdir(parents=True, exist_ok=True)
        done, failed = 0, 0
        for f in files:
            try:
                out, old, new = resize_one(
                    f, args.width, args.height, args.keep_aspect,
                    args.quality, args.out_format,
                    out_dir / f.name if args.out_dir else None)
                print(f"{f.name}: {old[0]}x{old[1]} -> {new[0]}x{new[1]}  ({out})")
                done += 1
            except Exception as exc:  # noqa: BLE001 - report per file, keep going
                print(f"{f.name}: FAILED ({exc})")
                failed += 1
        print(f"\nDone: {done} resized, {failed} failed.")
        return 0 if failed == 0 else 1

    # Single file
    try:
        out, old, new = resize_one(src, args.width, args.height,
                                   args.keep_aspect, args.quality,
                                   args.out_format, args.output)
    except FileNotFoundError:
        print(f"Error: {src} is not a readable image file.")
        return 1
    except Exception as exc:  # noqa: BLE001 - Pillow raises many error types
        print(f"Error: could not resize {src} ({exc})")
        return 1
    print(f"{src.name}: {old[0]}x{old[1]} -> {new[0]}x{new[1]}")
    print(f"Saved: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
