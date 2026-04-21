"""Generate app/src/assets/hero-band.jpg from the source JPG.

The source (525x350) has the hammer-and-sickle pushed to the right edge,
with the top of the sickle only ~23px below the top border. To render it
in a wide CSS band that stays 220px tall but shows more surrounding
concrete (so the H&S appears smaller / more zoomed-out), we build a
larger canvas by tiling a clean concrete slab (leftmost 150px of the
source, which has no H&S) and pasting the source image on top with the
H&S centered horizontally and vertically in the canvas.

Seams are low-contrast because the slab is all concrete with cracks,
and the H&S itself covers the mid-region where seams might otherwise
meet.
"""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
SRC = ROOT / "the-hammer-and-sickle-symbol-on-an-old-cracked-concrete-wall-photo.jpg"
OUT = ROOT.parent / "app" / "src" / "assets" / "hero-band.jpg"

# H&S bbox measured in source (525x350): x=[168, 520], y=[23, 304].
HS_CX, HS_CY = 344, 164

# Target canvas. Wider+taller than source so H&S occupies a smaller
# fraction of the image, which in turn makes it smaller in the 220px
# CSS band rendered with background-size: cover.
TARGET_W = 1050
TARGET_H = 525

# Width of the clean-concrete slab taken from the left side of the
# source (H&S starts at x=168, so 150 leaves a small safety margin).
SLAB_W = 150


def build_concrete_strip(slab: Image.Image, width: int) -> Image.Image:
    """Horizontal strip of given width built by tiling slab with
    alternating left-right mirrored copies."""
    sw, sh = slab.size
    flipped = slab.transpose(Image.FLIP_LEFT_RIGHT)
    n = (width + sw - 1) // sw
    strip = Image.new("RGB", (n * sw, sh))
    for i in range(n):
        strip.paste(flipped if i % 2 else slab, (i * sw, 0))
    return strip.crop((0, 0, width, sh))


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing source image: {SRC}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGB")
    sw, sh = src.size

    px = TARGET_W // 2 - HS_CX
    py = TARGET_H // 2 - HS_CY

    slab = src.crop((0, 0, SLAB_W, sh))
    strip = build_concrete_strip(slab, TARGET_W)

    top_pad = py
    bot_pad = TARGET_H - py - sh
    top_fill = strip.crop((0, 0, TARGET_W, top_pad)).transpose(Image.FLIP_TOP_BOTTOM)
    bot_fill = strip.crop(
        (0, strip.height - bot_pad, TARGET_W, strip.height)
    ).transpose(Image.FLIP_TOP_BOTTOM)

    bg = Image.new("RGB", (TARGET_W, TARGET_H))
    bg.paste(top_fill, (0, 0))
    bg.paste(strip, (0, top_pad))
    bg.paste(bot_fill, (0, top_pad + strip.height))

    bg.paste(src, (px, py))

    bg.save(OUT, "JPEG", quality=92, optimize=True)
    print(f"wrote {OUT} ({bg.width}x{bg.height})")


if __name__ == "__main__":
    main()
