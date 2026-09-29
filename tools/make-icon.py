#!/usr/bin/env python3
"""The application icon: a dark panel, a gold cross, the wordmark's colours."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "studytools-wallpaper.png")
S = 256
GOLD = (224, 171, 106); BG1 = (30, 24, 19); BG2 = (14, 11, 10)

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
for y in range(S):
    t = y / (S - 1)
    d.line([(0, y), (S, y)], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * t) for i in range(3)) + (255,))

mask = Image.new("L", (S * 4, S * 4), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S * 4 - 1, S * 4 - 1], radius=int(S * 4 * 0.22), fill=255)
mask = mask.resize((S, S), Image.LANCZOS)
img.putalpha(mask)

d = ImageDraw.Draw(img)
# the cross, as the header draws it
t = 15
d.rectangle([S // 2 - t // 2, 58, S // 2 + t // 2 - 1, 186], fill=GOLD + (255,))
d.rectangle([S // 2 - 46, 92, S // 2 + 46, 92 + t - 1], fill=GOLD + (255,))
# a hairline frame
d.rounded_rectangle([6, 6, S - 7, S - 7], radius=int(S * 0.2), outline=GOLD + (70,), width=2)

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
img.save(OUT)
for size in (48, 128, 512):
    img.resize((size, size), Image.LANCZOS).save(OUT.replace(".png", "-%d.png" % size))
print("wrote %s and 48/128/512 px copies" % OUT)
