"""Crops a VS Code screenshot, rounds the corners, and adds a thin border and a soft shadow on a transparent margin.

usage: python polish_screenshot.py <raw.png> <out.png> [left top right bottom]
"""
import sys

from PIL import Image, ImageDraw, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
box = tuple(int(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else None

im = Image.open(src).convert("RGBA")
if box:
    im = im.crop(box)
w, h = im.size

radius, margin = 10, 28
canvas = Image.new("RGBA", (w + 2 * margin, h + 2 * margin), (0, 0, 0, 0))

# soft shadow
shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle((margin, margin + 5, margin + w, margin + h + 5), radius, fill=(0, 0, 0, 80))
shadow = shadow.filter(ImageFilter.GaussianBlur(9))
canvas = Image.alpha_composite(canvas, shadow)

# the picture with rounded corners
mask = Image.new("L", (w, h), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
canvas.paste(im, (margin, margin), mask)

# a thin border
ImageDraw.Draw(canvas).rounded_rectangle((margin, margin, margin + w - 1, margin + h - 1), radius, outline=(208, 215, 222, 255), width=1)

canvas.save(dst)
print(dst, canvas.size)
