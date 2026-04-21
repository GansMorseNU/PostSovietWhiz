"""Generate 4 candidate phone-app icons at 512x512.

Each variant uses the same hammer-and-sickle / cracked-concrete photo as the
landing-page hero band, with 'Post-Soviet Whiz' rendered on top in a
different layout. Outputs to icon_candidates/icon_v{1..4}.png and an
icon_candidates_preview.html grid for side-by-side viewing.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
SRC = ROOT / "the-hammer-and-sickle-symbol-on-an-old-cracked-concrete-wall-photo.jpg"
SIZE = 512

FONT_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_GEO_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
FONT_IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"

# Downloaded Soviet-style fonts (all free for commercial use):
FONT_PROPAGANDA = str(ROOT / "fonts" / "propaganda" / "propaganda.ttf")
FONT_MOLOT = str(ROOT / "fonts" / "molot" / "Molot.otf")
FONT_USSR_STENCIL = str(ROOT / "fonts" / "ussr-stencil" / "USSR STENCIL" / "USSR STENCIL.otf")

BURGUNDY = (139, 30, 30)
CREAM = (244, 241, 234)
DARK_OVERLAY = (12, 10, 10)


def square_crop(img: Image.Image) -> Image.Image:
    """Crop a square centered so the hammer-and-sickle sits ~horizontally
    centered and slightly below vertical center. H&S centroid in the source
    (525x350) is at (342, 160); we take a 300x300 window at (192, 0) so the
    centroid lands at normalized (0.50, 0.53)."""
    crop_size = 300
    left = 192
    upper = 0
    return img.crop((left, upper, left + crop_size, upper + crop_size)).resize(
        (SIZE, SIZE), Image.LANCZOS
    )


def add_text(draw, xy, text, font, fill, anchor="mm", shadow=True):
    if shadow:
        sx, sy = xy
        draw.text((sx + 3, sy + 3), text, font=font, fill=(0, 0, 0, 200), anchor=anchor)
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def variant_1_bottom_band(base: Image.Image) -> Image.Image:
    """Image fills the icon; bottom 30% is a burgundy band with the title."""
    icon = base.copy()
    band_h = int(SIZE * 0.30)
    band = Image.new("RGBA", (SIZE, band_h), BURGUNDY + (235,))
    icon.paste(band, (0, SIZE - band_h), band)
    draw = ImageDraw.Draw(icon)
    f1 = ImageFont.truetype(FONT_BLACK, 60)
    f2 = ImageFont.truetype(FONT_BLACK, 80)
    add_text(draw, (SIZE // 2, SIZE - band_h + 50), "POST-SOVIET", f1, CREAM, shadow=False)
    add_text(draw, (SIZE // 2, SIZE - band_h + 115), "WHIZ", f2, CREAM, shadow=False)
    return icon


def fit_font(font_path: str, text: str, max_width: int, ceiling: int = 200) -> ImageFont.FreeTypeFont:
    """Largest font size where `text` rendered in `font_path` fits within max_width."""
    lo, hi = 10, ceiling
    best = ImageFont.truetype(font_path, lo)
    probe_img = Image.new("RGB", (10, 10))
    pd = ImageDraw.Draw(probe_img)
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(font_path, mid)
        bbox = pd.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_width:
            best = f
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def variant_2_full_overlay(base: Image.Image, font_path: str) -> Image.Image:
    """Image filling the icon with a soft dark gradient. POST-SOVIET sits near
    the top, WHIZ near the bottom, sized to the same point size and sized a
    bit below full width so the title feels like a poster caption, not a
    wall of text."""
    icon = base.copy().convert("RGBA")
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(SIZE):
        a = int(140 * (abs(y - SIZE / 2) / (SIZE / 2)) ** 1.5)
        od.line([(0, y), (SIZE, y)], fill=(0, 0, 0, a))
    icon = Image.alpha_composite(icon, overlay)
    draw = ImageDraw.Draw(icon)

    # Smaller than full width so the text doesn't dominate.
    max_text_w = int(SIZE * 0.72)
    font = fit_font(font_path, "POST-SOVIET", max_text_w)

    add_text(draw, (SIZE // 2, 40), "POST-SOVIET", font, CREAM, anchor="mt")
    add_text(draw, (SIZE // 2, SIZE - 40), "WHIZ", font, CREAM, anchor="mb")
    return icon


def variant_3_top_strip(base: Image.Image) -> Image.Image:
    """Top 65% image, bottom 35% cream stripe with burgundy serif title."""
    icon = Image.new("RGB", (SIZE, SIZE), CREAM)
    img_h = int(SIZE * 0.65)
    img = base.resize((SIZE, SIZE), Image.LANCZOS).crop((0, 0, SIZE, img_h))
    icon.paste(img, (0, 0))
    # Soft fade between image and stripe
    fade = Image.new("RGBA", (SIZE, 40), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(40):
        fd.line([(0, y), (SIZE, y)], fill=CREAM + (int(255 * y / 40),))
    icon.paste(fade, (0, img_h - 40), fade)
    draw = ImageDraw.Draw(icon)
    f1 = ImageFont.truetype(FONT_GEO_BOLD, 56)
    f2 = ImageFont.truetype(FONT_GEO_BOLD, 90)
    add_text(draw, (SIZE // 2, img_h + 45), "Post-Soviet", f1, BURGUNDY, shadow=False)
    add_text(draw, (SIZE // 2, img_h + 125), "WHIZ", f2, BURGUNDY, shadow=False)
    return icon


def variant_4_circle_emblem(base: Image.Image) -> Image.Image:
    """Burgundy background with a circular cut-out of the H&S in the center,
    arched 'POST-SOVIET WHIZ' text around it."""
    icon = Image.new("RGB", (SIZE, SIZE), BURGUNDY)
    diameter = int(SIZE * 0.62)
    img = base.resize((diameter, diameter), Image.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter, diameter), fill=255)
    cx = (SIZE - diameter) // 2
    cy = (SIZE - diameter) // 2 + 10
    icon.paste(img, (cx, cy), mask)
    draw = ImageDraw.Draw(icon)
    # Cream ring around emblem
    draw.ellipse(
        (cx - 6, cy - 6, cx + diameter + 6, cy + diameter + 6),
        outline=CREAM,
        width=4,
    )
    f1 = ImageFont.truetype(FONT_BLACK, 44)
    f2 = ImageFont.truetype(FONT_BLACK, 72)
    add_text(draw, (SIZE // 2, 50), "POST-SOVIET", f1, CREAM, shadow=False)
    add_text(draw, (SIZE // 2, SIZE - 55), "WHIZ", f2, CREAM, shadow=False)
    return icon


PWA_PUBLIC = ROOT.parent / "app" / "public"
FINAL_FONT = FONT_MOLOT


def build_final_pwa_icons(base: Image.Image) -> None:
    """Render the chosen (Molot) icon at the 3 sizes the PWA manifest needs
    and drop them into app/public/, replacing the placeholder icons."""
    master = variant_2_full_overlay(base, FINAL_FONT).convert("RGB")
    targets = {
        "pwa-512x512.png": 512,
        "pwa-192x192.png": 192,
        "apple-touch-icon.png": 180,
    }
    for name, px in targets.items():
        out = PWA_PUBLIC / name
        img = master if px == SIZE else master.resize((px, px), Image.LANCZOS)
        img.save(out, "PNG", optimize=True)
        print(f"wrote {out} ({px}x{px})")


def main():
    if not SRC.exists():
        raise SystemExit(f"missing source image: {SRC}")
    base = square_crop(Image.open(SRC).convert("RGB"))

    variants = {
        "icon_v2_impact.png": variant_2_full_overlay(base, FONT_IMPACT),
        "icon_v2_propaganda.png": variant_2_full_overlay(base, FONT_PROPAGANDA),
        "icon_v2_molot.png": variant_2_full_overlay(base, FONT_MOLOT),
        "icon_v2_ussr_stencil.png": variant_2_full_overlay(base, FONT_USSR_STENCIL),
    }
    for name, img in variants.items():
        out = ROOT / name
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(out, "PNG", optimize=True)
        print(f"wrote {out}")

    # Side-by-side preview HTML
    html = ROOT / "icon_candidates_preview.html"
    html.write_text(
        """<!doctype html>
<html><head><meta charset=utf-8><title>Icon candidates</title>
<style>
  body { font-family: -apple-system, sans-serif; background:#1a1a1a; color:#eee; margin:20px; }
  h1 { font-weight:600; }
  .grid { display:grid; grid-template-columns: repeat(2, 1fr); gap:24px; max-width:900px; }
  .card { background:#2a2a2a; padding:16px; border-radius:12px; text-align:center; }
  .card img { width:200px; height:200px; border-radius:38px; box-shadow: 0 8px 20px rgba(0,0,0,.5); }
  .card .small { width:60px; height:60px; border-radius:14px; margin-top:12px; box-shadow:0 2px 4px rgba(0,0,0,.4); }
  .label { margin-top:12px; font-size:14px; color:#ccc; }
</style></head><body>
<h1>PostSovietWhiz icon candidates</h1>
<p>Each tile shows the icon at ~200px (close to phone home-screen size) and a 60px thumbnail underneath for legibility check.</p>
<div class="grid">
  <div class="card"><img src="icon_v2_impact.png"><img class="small" src="icon_v2_impact.png"><div class="label">Impact (baseline)</div></div>
  <div class="card"><img src="icon_v2_propaganda.png"><img class="small" src="icon_v2_propaganda.png"><div class="label">Propaganda</div></div>
  <div class="card"><img src="icon_v2_molot.png"><img class="small" src="icon_v2_molot.png"><div class="label">Molot</div></div>
  <div class="card"><img src="icon_v2_ussr_stencil.png"><img class="small" src="icon_v2_ussr_stencil.png"><div class="label">USSR Stencil</div></div>
</div>
</body></html>
"""
    )
    print(f"wrote {html}")

    build_final_pwa_icons(base)


if __name__ == "__main__":
    main()
