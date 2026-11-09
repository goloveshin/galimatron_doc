"""Renders each given SVG whole, with headless Edge, into the scratch folder as <name>.png."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svg_tools import region, svg_size, SCRATCH

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
for name in sys.argv[1:]:
    svg = os.path.join(ROOT, "source", "images", name + ".svg")
    w, h = svg_size(svg)
    out = os.path.join(SCRATCH, name + ".png")
    region(svg, 0, 0, w, h, out)
    print(name, w, h)
