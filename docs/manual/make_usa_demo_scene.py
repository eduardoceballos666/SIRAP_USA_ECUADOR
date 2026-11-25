"""Compose the manual's US demo scene: repository sample image + an ORIGINAL, drawn plate (no third-party crop).

Usage: python docs/manual/make_usa_demo_scene.py data/samples/garita1_GSA-1234.jpg us_demo_scene.jpg
The plate (TEXAS / KDM4827 / DEMO PLATE) is fictitious and drawn here; it covers the sample's own plate.
"""
import sys
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
scene = Image.open(src).convert('RGB')
K = 6                                  # supersampling
W, H = 100 * K, 50 * K                 # a US plate is 12 x 6 in (2:1)
plate = Image.new('RGB', (W, H), (246, 247, 244))
d = ImageDraw.Draw(plate)
d.rounded_rectangle((0, 0, W - 1, H - 1), radius=4 * K, outline=(24, 40, 92), width=int(1.6 * K), fill=(246, 247, 244))
bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f_small = ImageFont.truetype(bold, int(7 * K))
size = 24
while True:
    f_big = ImageFont.truetype(bold, int(size * K))
    if d.textlength('KDM4827', font=f_big) <= 88 * K: break
    size -= 1
f_foot = ImageFont.truetype(bold, int(5 * K))
def centered(text, y, font, fill):
    w = d.textlength(text, font=font)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
centered('TEXAS', 4 * K, f_small, (24, 40, 92))
centered('KDM4827', 16 * K, f_big, (20, 24, 34))
centered('DEMO PLATE', 41 * K, f_foot, (24, 40, 92))
plate = plate.resize((100, 50), Image.LANCZOS)
# slight softness so it blends with the (already soft) sample photograph
from PIL import ImageFilter
plate = plate.filter(ImageFilter.GaussianBlur(0.35))
cx, cy = 364, 254
scene.paste(plate, (cx - 50, cy - 25))
scene.save(out, quality=92)
print('plate box', [cx - 50, cy - 25, cx + 50, cy + 25], scene.size)
