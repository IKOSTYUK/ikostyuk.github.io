"""Downscale and re-encode the full-size travel photos in place.

These come straight off a phone at ~12 MP, which is far larger than the
lightbox can display. Resizing to a 2048px long edge halves the payload with
no visible loss at the size they are actually viewed.

    .venv/Scripts/python.exe scripts/optimize_photos.py

Photos already within the target dimensions are skipped, so re-running is safe
and will not stack generation loss from repeated JPEG encodes.

Note: this rewrites the originals in place. EXIF is stripped (after baking in
the rotation flag), which also removes embedded GPS coordinates.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

SOURCE_DIR = Path(__file__).resolve().parent.parent / "img" / "travel"
EXTENSIONS = {".jpeg", ".jpg"}
MAX_EDGE = 2048
QUALITY = 82


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-edge", type=int, default=MAX_EDGE)
    parser.add_argument("--quality", type=int, default=QUALITY)
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args()

    if not SOURCE_DIR.is_dir():
        print(f"No such directory: {SOURCE_DIR}", file=sys.stderr)
        return 1

    before = after = 0
    done = skipped = 0

    for path in sorted(SOURCE_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue

        start = path.stat().st_size
        with Image.open(path) as im:
            width, height = im.size
            if max(width, height) <= args.max_edge:
                skipped += 1
                before += start
                after += start
                continue

            # Bake in the camera rotation flag before EXIF is dropped on save.
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((args.max_edge, args.max_edge), Image.LANCZOS)
            new_size = im.size
            if not args.dry_run:
                im.save(path, "JPEG", quality=args.quality, optimize=True, progressive=True)

        end = path.stat().st_size if not args.dry_run else start
        before += start
        after += end
        done += 1
        print(
            f"{path.name:14} {width}x{height} -> {new_size[0]}x{new_size[1]}"
            f"   {start // 1024} KB -> {end // 1024} KB"
        )

    verb = "would resize" if args.dry_run else "resized"
    print(f"\n{done} {verb}, {skipped} already within {args.max_edge}px")
    print(f"total: {before / 1048576:.1f} MB -> {after / 1048576:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
