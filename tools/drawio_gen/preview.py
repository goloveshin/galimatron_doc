import subprocess, sys, os, glob
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

src = sys.argv[1]
tile_w = int(sys.argv[2]) if len(sys.argv) > 2 else 1600
tile_h = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
scale = sys.argv[4] if len(sys.argv) > 4 else "1"
base = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "galdraw", "prev")
os.makedirs(base, exist_ok=True)
for f in glob.glob(base + r"\tile_*.png"):
    os.remove(f)
png = os.path.join(base, "full.png")
subprocess.run([r"C:\Program Files\draw.io\draw.io.exe", "-x", "-f", "png", "-s", scale, "-b", "10", "-o", png, src],
               check=True, capture_output=True, timeout=int(os.environ.get("EXPORT_TIMEOUT", "240")))
im = Image.open(png)
W, H = im.size
print("size", W, H)
for yi, y in enumerate(range(0, H, tile_h)):
    for xi, x in enumerate(range(0, W, tile_w)):
        t = im.crop((x, y, min(x + tile_w, W), min(y + tile_h, H)))
        t.save(base + r"\tile_%d_%d.png" % (yi, xi))
print("tiles", (H + tile_h - 1) // tile_h, "x", (W + tile_w - 1) // tile_w)
