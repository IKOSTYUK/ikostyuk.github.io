"""Generate square thumbnails for the travel gallery.

The gallery grid loads img/travel/thumbs/<name>, while the lightbox loads the
full-size original. Re-run this after adding photos to img/travel/:

    .venv/Scripts/python.exe scripts/make_thumbs.py

Existing thumbnails are skipped unless the original is newer (or --force).
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

SOURCE_DIR = Path(__file__).resolve().parent.parent / "img" / "travel"
THUMB_DIR = SOURCE_DIR / "thumbs"
EXTENSIONS = {".jpeg", ".jpg", ".png"}
SIZE = 600
QUALITY = 80


def build(source: Path, dest: Path) -> None:
    with Image.open(source) as im:
        # Honour the camera's rotation flag, otherwise phone shots come out sideways.
        im = ImageOps.exif_transpose(im)
        im = im.convert("RGB")
        # Centre-crop to a square and resize in one pass.
        im = ImageOps.fit(im, (SIZE, SIZE), method=Image.LANCZOS, centering=(0.5, 0.5))
        im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="rebuild every thumbnail")
    args = parser.parse_args()

    if not SOURCE_DIR.is_dir():
        print(f"No such directory: {SOURCE_DIR}", file=sys.stderr)
        return 1

    THUMB_DIR.mkdir(exist_ok=True)
    built = skipped = 0

    for source in sorted(SOURCE_DIR.iterdir()):
        if not source.is_file() or source.suffix.lower() not in EXTENSIONS:
            continue

        dest = THUMB_DIR / source.name
        if not args.force and dest.exists() and dest.stat().st_mtime >= source.stat().st_mtime:
            skipped += 1
            continue

        build(source, dest)
        built += 1
        print(f"{source.name}: {source.stat().st_size // 1024} KB -> {dest.stat().st_size // 1024} KB")

    print(f"\n{built} built, {skipped} up to date -> {THUMB_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
