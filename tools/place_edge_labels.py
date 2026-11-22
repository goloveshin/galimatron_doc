"""Place edge labels beside their arrows (not on top of them). Dry run by default, --write to edit drawio files."""
import glob, html, math, os, re, sys
import xml.etree.ElementTree as ET

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
WRITE = "--write" in sys.argv
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]

# the label goes below / right of the arrow instead of above / left (back arrows next to a forward arrow)
# edges that fan out of one box: the label sits near the start, where the arrows are far apart
LABEL_T = {"26_": 0.3, "27_": 0.3, "28_": 0.3, "29_": 0.3}
FLIP = {("10_", "a2"), ("20_", "a4")}


def style_of(cell):
    d = {}
    for part in (cell.get("style") or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
    return d


def label_size(cell):
    st = style_of(cell)
    text = re.sub(r"<[^>]+>", "", (cell.get("value") or "").replace("<br>", "\n"))
    text = html.unescape(text)
    lines = text.split("\n")
    fs = float(st.get("fontSize", 11))
    cw = fs * (0.58 if "fontStyle" in st and st["fontStyle"] in ("1", "3") else 0.53)
    return max(len(l) for l in lines) * cw + 8, len(lines) * fs * 1.25 + 4


def abs_rect(cells, c):
    g = c.find("mxGeometry")
    x, y, w, h = (float(g.get(k, 0)) for k in ("x", "y", "width", "height"))
    p = cells.get(c.get("parent"))
    while p is not None and p.get("id") not in ("0", "1"):
        pg = p.find("mxGeometry")
        x += float(pg.get("x", 0)); y += float(pg.get("y", 0))
        p = cells.get(p.get("parent"))
    return x, y, w, h


def clip(rect, frm, to):
    """point where the segment from the centre of rect towards `to` leaves rect"""
    x, y, w, h = rect
    cx, cy = x + w / 2, y + h / 2
    dx, dy = to[0] - cx, to[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    t = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
    return cx + dx * t, cy + dy * t


def endpoints(cells, e):
    st = style_of(e)
    s, t = cells[e.get("source")], cells[e.get("target")]
    rs, rt = abs_rect(cells, s), abs_rect(cells, t)
    cs = (rs[0] + rs[2] / 2, rs[1] + rs[3] / 2)
    ct = (rt[0] + rt[2] / 2, rt[1] + rt[3] / 2)
    if "exitX" in st:
        a = (rs[0] + float(st["exitX"]) * rs[2], rs[1] + float(st["exitY"]) * rs[3])
    else:
        a = clip(rs, cs, ct)
    if "entryX" in st:
        b = (rt[0] + float(st["entryX"]) * rt[2], rt[1] + float(st["entryY"]) * rt[3])
    else:
        b = clip(rt, ct, cs)
    return a, b


def plan(path):
    tree = ET.parse(path).getroot()
    cells = {c.get("id"): c for c in tree.iter("mxCell")}
    verts = [c for c in cells.values() if c.get("vertex") == "1" and c.find("mxGeometry") is not None]
    out = {}
    segs = {}
    for e in cells.values():
        if e.get("edge") == "1" and e.get("source") and e.get("target") and e.find("mxGeometry").find("Array") is None:
            segs[e.get("id")] = endpoints(cells, e)
    for e in cells.values():
        if e.get("edge") != "1" or not (e.get("value") or "").strip():
            continue
        g = e.find("mxGeometry")
        has_pts = g.find("Array") is not None
        st = style_of(e)
        straight = False
        if not has_pts and e.get("source") and e.get("target"):
            a0, b0 = endpoints(cells, e)
            straight = abs(a0[0] - b0[0]) < 1 or abs(a0[1] - b0[1]) < 1
        if has_pts or (st.get("edgeStyle") == "orthogonalEdgeStyle" and not straight) or e.get("source") is None or e.get("target") is None:
            out[e.get("id")] = ("MANUAL", None, None)
            continue
        a, b = endpoints(cells, e)
        t_at = LABEL_T.get(os.path.basename(path)[:3], 0.5)
        mid = (a[0] + (b[0] - a[0]) * t_at, a[1] + (b[1] - a[1]) * t_at)
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        tx, ty = dx / L, dy / L
        w, h = label_size(e)
        if abs(dx) >= abs(dy):
            nx, ny = (ty, -tx) if tx > 0 else (-ty, tx)   # normal that points up
            if ny > 0: nx, ny = -nx, -ny
        else:
            nx, ny = (-ty, tx)
            if nx < 0: nx, ny = -nx, -ny
        d = (w / 2) * abs(nx) + (h / 2) * abs(ny) + 4
        best = None
        for sign in ((-1, 1) if (os.path.basename(path)[:3], e.get("id")) in FLIP else (1, -1)):
            off = (round(sign * nx * d), round(sign * ny * d))
            cx, cy = mid[0] + off[0], mid[1] + off[1]
            rect = (cx - w / 2, cy - h / 2, w, h)
            warn = []
            for v in verts:
                vr = abs_rect(cells, v)
                ix = min(rect[0] + rect[2], vr[0] + vr[2]) - max(rect[0], vr[0])
                iy = min(rect[1] + rect[3], vr[1] + vr[3]) - max(rect[1], vr[1])
                if ix > 1 and iy > 1:
                    inside = rect[0] >= vr[0] and rect[1] >= vr[1] and rect[0] + rect[2] <= vr[0] + vr[2] and rect[1] + rect[3] <= vr[1] + vr[3]
                    if not inside:
                        warn.append(v.get("id"))
            for sid, (sa, sb) in segs.items():
                if sid == e.get("id"):
                    continue
                n = int(math.hypot(sb[0] - sa[0], sb[1] - sa[1]) / 2) + 1
                for i in range(n + 1):
                    px, py = sa[0] + (sb[0] - sa[0]) * i / n, sa[1] + (sb[1] - sa[1]) * i / n
                    if rect[0] <= px <= rect[0] + rect[2] and rect[1] <= py <= rect[1] + rect[3]:
                        warn.append("edge " + sid)
                        break
            if best is None or len(warn) < len(best[2]):
                best = (off, rect, warn)
            if not warn:
                break
        off, rect, warn = best
        if L < w + 10 and abs(dx) >= abs(dy):
            warn.append("TIGHT")
        out[e.get("id")] = ("OK", (off[0], off[1], t_at), (round(w), round(h), warn, round(L)))
    return out


def apply(path, p):
    text = open(path, encoding="utf-8").read()
    for eid, (kind, off, _) in p.items():
        if kind != "OK":
            continue
        m = re.search(r'<mxCell id="%s"[^>]*edge="1".*?</mxCell>' % re.escape(eid), text, re.S)
        block = m.group(0)
        nb = block.replace("labelBackgroundColor=#ffffff;", "")
        geo = re.search(r"<mxGeometry[^>]*>.*?</mxGeometry>|<mxGeometry[^>]*/>", nb, re.S).group(0)
        new_geo = '<mxGeometry%s relative="1" as="geometry"><mxPoint x="%d" y="%d" as="offset"/></mxGeometry>' % (' x="%g"' % (2 * off[2] - 1) if off[2] != 0.5 else "", off[0], off[1])
        nb = nb.replace(geo, new_geo)
        text = text.replace(block, nb)
    open(path, "w", encoding="utf-8", newline="").write(text)


for f in sorted(glob.glob(os.path.join(ROOT, "drawio", "*.drawio"))):
    base = os.path.basename(f)
    if ONLY and not any(base.startswith(o) for o in ONLY):
        continue
    p = plan(f)
    if not p:
        continue
    for eid, (kind, off, info) in p.items():
        print(base[:18], eid, kind, off, info)
    if WRITE:
        apply(f, p)
