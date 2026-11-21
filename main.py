#!/usr/bin/env python3
"""Write the Amartha passport spread to /output/entry.png.

The spread is drawn by render.py in this repository (Pillow): it lays
out the data page and the visas page of a passport from the Kingdom
of Amartha, an underground kingdom of the hollow earth that does not
exist, and pastes in the portrait from assets/portrait.jpg, a portrait
made by an image model in the session that built this entry. The
finished spread is stored as assets/entry.png, and this program writes
those exact bytes to the output path, after checking the gate limits.

The program uses the standard library only and is deterministic:
every run writes the same bytes.

Gate limits from the bounty rules: one whole PNG or JPEG, at most
1,048,576 bytes and 1024 by 1024 pixels.
"""

import os
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "assets" / "entry.png"
MAX_BYTES = 1_048_576
MAX_DIM = 1024


def png_dimensions(path):
    with open(path, "rb") as f:
        header = f.read(33)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if header[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_path = out_dir / "entry.png"
    if not SOURCE.is_file():
        print(f"missing source image: {SOURCE}", file=sys.stderr)
        return 1
    size = SOURCE.stat().st_size
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the {MAX_BYTES} limit",
              file=sys.stderr)
        return 1
    width, height = png_dimensions(SOURCE)
    if width > MAX_DIM or height > MAX_DIM:
        print(f"entry.png is {width}x{height}, over the {MAX_DIM} limit",
              file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, out_path)
    print(f"wrote {out_path} ({width}x{height}, {size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
