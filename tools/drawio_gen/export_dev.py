"""Exports the developer diagrams (30_dev_* to 43_dev_*) to source/images/*.svg, without the fallback PNGs."""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svg_tools import export

ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
only = sys.argv[1:]
for src in sorted(glob.glob(os.path.join(ROOT, "drawio", "[34][0-9]_dev_*.drawio"))):
    name = os.path.splitext(os.path.basename(src))[0]
    if only and not any(o in name for o in only):
        continue
    dst = os.path.join(ROOT, "source", "images", name + ".svg")
    export(src, dst)
