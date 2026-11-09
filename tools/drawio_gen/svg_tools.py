"""Export a .drawio to .svg with draw.io, strip the fallback PNGs, and preview regions with headless Edge.

usage:
  python svg_tools.py export <in.drawio> <out.svg>
  python svg_tools.py tiles  <in.svg> [tile_w tile_h]     # writes tiles to the scratch folder
  python svg_tools.py region <in.svg> x y w h             # one region
"""
import os
import re
import subprocess
import sys

DRAWIO = r"C:\Program Files\draw.io\draw.io.exe"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCRATCH = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "galdraw", "prev")

FALLBACK = re.compile(r'<image [^>]*xlink:href="data:image/png;base64,[^"]*"[^>]*/>')


def export(src, dst, timeout=300):
    subprocess.run([DRAWIO, "-x", "-f", "svg", "-b", "10", "-o", dst, src], check=True, capture_output=True,
                   timeout=timeout)
    with open(dst, encoding="utf-8") as f:
        text = f.read()
    before = len(text)
    text = FALLBACK.sub("", text)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("exported", dst, before, "->", len(text), "bytes")


def svg_size(svg):
    with open(svg, encoding="utf-8") as f:
        head = f.read(2000)
    m = re.search(r'width="(\d+)px" height="(\d+)px"', head)
    return int(m.group(1)), int(m.group(2))


def region(svg, x, y, w, h, out):
    os.makedirs(SCRATCH, exist_ok=True)
    page = os.path.join(SCRATCH, "wrap.html")
    full_w, full_h = svg_size(svg)
    with open(page, "w", encoding="utf-8") as f:
        f.write('<html><body style="margin:0;overflow:hidden;background:#fff">'
                '<img src="file:///%s" style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx"></body></html>'
                % (svg.replace("\\", "/"), -x, -y, full_w, full_h))
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=4000",
                    "--screenshot=" + out, "--window-size=%d,%d" % (w, h), "file:///" + page.replace("\\", "/")],
                   check=True, capture_output=True, timeout=120)


def tiles(svg, tw=1700, th=1000):
    full_w, full_h = svg_size(svg)
    os.makedirs(SCRATCH, exist_ok=True)
    for name in os.listdir(SCRATCH):
        if name.startswith("tile_"):
            os.remove(os.path.join(SCRATCH, name))
    print("svg", full_w, full_h)
    for yi, y in enumerate(range(0, full_h, th)):
        for xi, x in enumerate(range(0, full_w, tw)):
            region(svg, x, y, max(300, min(tw, full_w - x)), max(300, min(th, full_h - y)),
                   os.path.join(SCRATCH, "tile_%d_%d.png" % (yi, xi)))
    print("tiles", (full_h + th - 1) // th, "x", (full_w + tw - 1) // tw)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "export":
        export(sys.argv[2], sys.argv[3])
    elif cmd == "tiles":
        tiles(sys.argv[2], *(int(a) for a in sys.argv[3:5]))
    elif cmd == "region":
        x, y, w, h = (int(a) for a in sys.argv[3:7])
        region(sys.argv[2], x, y, w, h, os.path.join(SCRATCH, "region.png"))
