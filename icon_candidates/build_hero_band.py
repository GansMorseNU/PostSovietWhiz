"""Generate app/src/assets/hero-band.jpg from the source JPG.

The source (525x350) has the hammer-and-sickle pushed to the right edge,
with the top of the sickle only ~23px below the top border. Rendering it
in a wide CSS band at background-size: cover cuts off the top and bottom
of the symbol and places it right of center.

This script expands the canvas with mirror-flipped concrete on the right,
top, and bottom so the H&S ends up horizontally centered with comfortable
concrete padding on every side. The texture is noisy enough that the
mirror seams are effectively invisible in the final rendered band.
"""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent
SRC = ROOT / "the-hammer-and-sickle-symbol-on-an-old-cracked-concrete-wall-photo.jpg"
OUT = ROOT.parent / "app" / "src" / "assets" / "hero-band.jpg"

# Source H&S bbox measured earlier: x=[168, 520], y=[23, 304] in 525x350.
RIGHT_EXT = 175  # enough to mirror the ~168px of left-side concrete
TOP_EXT = 40
BOT_EXT = 30


def mirror_extend(img: Image.Image) -> Image.Image:
    w, h = img.size

    # Right: mirror-flip the leftmost RIGHT_EXT pixels and append.
    right_flip = img.crop((0, 0, RIGHT_EXT, h)).transpose(Image.FLIP_LEFT_RIGHT)
    wider = Image.new("RGB", (w + RIGHT_EXT, h))
    wider.paste(img, (0, 0))
    wider.paste(right_flip, (w, 0))

    # Top: mirror-flip the top TOP_EXT pixels of the wider image and prepend.
    top_flip = wider.crop((0, 0, wider.width, TOP_EXT)).transpose(Image.FLIP_TOP_BOTTOM)
    taller = Image.new("RGB", (wider.width, wider.height + TOP_EXT))
    taller.paste(top_flip, (0, 0))
    taller.paste(wider, (0, TOP_EXT))

    # Bottom: mirror-flip the bottom BOT_EXT pixels and append.
    bot_flip = taller.crop(
        (0, taller.height - BOT_EXT, taller.width, taller.height)
    ).transpose(Image.FLIP_TOP_BOTTOM)
    final = Image.new("RGB", (taller.width, taller.height + BOT_EXT))
    final.paste(taller, (0, 0))
    final.paste(bot_flip, (0, taller.height))

    return final


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing source image: {SRC}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.open(SRC).convert("RGB")
    out = mirror_extend(img)
    out.save(OUT, "JPEG", quality=92, optimize=True)
    print(f"wrote {OUT} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
