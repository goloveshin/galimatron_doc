"""A tiny helper that writes draw.io (mxGraph) files. Boxes know how to wrap their text."""
import html
import re
import textwrap
from xml.sax.saxutils import quoteattr

# palette
BLUE = ("#dae8fc", "#6c8ebf")      # built-in step
YELLOW = ("#fff2cc", "#d6b656")    # user step
GREEN = ("#d5e8d4", "#82b366")     # state in memory
ORANGE = ("#ffe6cc", "#d79b00")    # files
RED = ("#f8cecc", "#b85450")       # failure
PURPLE = ("#e1d5e7", "#9673a6")    # saxon
GREY = ("#f5f5f5", "#999999")
WHITE = ("#ffffff", "#666666")
TEAL = ("#d0ecec", "#3b8f8f")

CHAR_W = {10: 5.6, 11: 6.1, 12: 6.6, 13: 7.2, 14: 7.7, 16: 9.0, 20: 11.2, 28: 15.5}


def _code_only(text):
    """`code` -> html. A backtick must never reach draw.io: it is the AsciiMath delimiter."""
    out = []
    pos = 0
    for m in re.finditer(r"`(.+?)`", text):
        out.append(html.escape(text[pos:m.start()], quote=False))
        out.append('<font face="Consolas">%s</font>' % html.escape(m.group(1), quote=False))
        pos = m.end()
    out.append(html.escape(text[pos:], quote=False))
    return "".join(out).replace("`", "&#96;")


def _inline(text):
    """**bold**, `code` -> html. Everything else is escaped."""
    out = []
    pos = 0
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        out.append(_code_only(text[pos:m.start()]))
        out.append("<b>%s</b>" % _code_only(m.group(1)))
        pos = m.end()
    out.append(_code_only(text[pos:]))
    return "".join(out)


def _plain_len(text):
    return len(re.sub(r"\*\*|`", "", text))


def wrap_lines(text, width_px, font=11, mono=False, pad=12):
    """Greedy wrap by estimated character width. Returns a list of source lines (markup kept)."""
    cw = CHAR_W.get(font, font * 0.56) * (1.0 if mono else 1.0)
    limit = max(8, int((width_px - pad) / cw))
    lines = []
    for raw in text.split("\n"):
        if raw == "":
            lines.append("")
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        bullet = raw.lstrip(" ").startswith("• ")
        words = raw.strip(" ").split(" ")
        cur = ""
        for w in words:
            cand = (cur + " " + w) if cur else w
            if _plain_len(cand) + indent > limit and cur:
                lines.append(" " * indent + cur)
                cur = ("  " if bullet else "") + w
            else:
                cur = cand
        lines.append(" " * indent + cur)
    return lines


def lines_html(lines):
    return "<br>".join(_inline(l).replace("  ", "&nbsp;&nbsp;") if l.startswith(" ") or "  " in l else _inline(l) for l in lines)


class Diagram:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.cells = []
        self.n = 1

    def _id(self):
        self.n += 1
        return "c%d" % self.n

    # -- measuring --
    def height_for(self, text, width, font=11, mono=False, pad_v=10, lh=None):
        lh = lh or int(font * 1.32) + 1
        n = len(wrap_lines(text, width, font, mono))
        return n * lh + pad_v

    # -- vertices --
    def box(self, x, y, w, text="", h=None, fill=WHITE[0], stroke=WHITE[1], font=11, bold=False,
            align="center", valign="middle", dashed=False, rounded=True, mono=False, sw=1,
            fontcolor="#222222", italic=False, pad_v=10, arc=8, extra="", parent="1", wrap=True,
            spacing_left=4, opacity=None, shadow=False):
        if h is None:
            h = self.height_for(text, w, font, mono, pad_v)
        lines = wrap_lines(text, w, font, mono) if wrap else text.split("\n")
        val = lines_html(lines)
        fs = 0
        if bold:
            fs |= 1
        if italic:
            fs |= 2
        style = ["whiteSpace=wrap", "html=1", "fillColor=%s" % fill, "strokeColor=%s" % stroke,
                 "strokeWidth=%s" % sw, "fontSize=%d" % font, "fontColor=%s" % fontcolor,
                 "align=%s" % align, "verticalAlign=%s" % valign, "spacingLeft=%d" % spacing_left,
                 "spacingRight=4", "spacingTop=2", "spacingBottom=2"]
        if rounded:
            style += ["rounded=1", "arcSize=%d" % arc]
        else:
            style += ["rounded=0"]
        if dashed:
            style += ["dashed=1", "dashPattern=5 3"]
        if fs:
            style.append("fontStyle=%d" % fs)
        if mono:
            style.append("fontFamily=Consolas")
        if opacity is not None:
            style.append("opacity=%d" % opacity)
        if shadow:
            style.append("shadow=1")
        if extra:
            style.append(extra)
        cid = self._id()
        self.cells.append(
            '<mxCell id="%s" value=%s style=%s vertex="1" parent="%s"><mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
            % (cid, quoteattr(val), quoteattr(";".join(style)), parent, x, y, w, h))
        self.last_h = h
        return cid

    def text(self, x, y, w, text, h=None, font=11, bold=False, color="#222222", align="left",
             italic=False, mono=False, valign="top", wrap=True):
        return self.box(x, y, w, text, h=h, fill="none", stroke="none", font=font, bold=bold,
                        align=align, valign=valign, rounded=False, mono=mono, fontcolor=color,
                        italic=italic, pad_v=4, extra="strokeColor=none;fillColor=none", wrap=wrap,
                        spacing_left=0)

    def frame(self, x, y, w, h, title="", fill="#ffffff", stroke="#bdbdbd", dashed=False,
              font=14, title_color="#222222", sw=1.5, arc=2):
        cid = self._id()
        style = ("rounded=1;arcSize=%d;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;strokeWidth=%s;"
                 "verticalAlign=top;align=left;spacingLeft=14;spacingTop=8;fontSize=%d;fontStyle=1;fontColor=%s;"
                 % (arc, fill, stroke, sw, font, title_color))
        if dashed:
            style += "dashed=1;dashPattern=6 4;"
        self.cells.append(
            '<mxCell id="%s" value=%s style=%s vertex="1" parent="1"><mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
            % (cid, quoteattr(_inline(title)), quoteattr(style), x, y, w, h))
        return cid

    # -- edges --
    def edge(self, s, t, text="", color="#555555", dashed=False, width=1.5, points=None, curved=False,
             exit_xy=None, entry_xy=None, style_extra="", end="block", start="none", font=10,
             straight=False):
        cid = self._id()
        style = ["html=1", "rounded=1", "strokeColor=%s" % color, "strokeWidth=%s" % width,
                 "endArrow=%s" % end, "endFill=1", "startArrow=%s" % start, "fontSize=%d" % font,
                 "fontColor=#444444", "labelBackgroundColor=#ffffff"]
        if not straight:
            style.insert(0, "edgeStyle=orthogonalEdgeStyle")
        if dashed:
            style += ["dashed=1", "dashPattern=5 3"]
        if exit_xy:
            style += ["exitX=%s" % exit_xy[0], "exitY=%s" % exit_xy[1], "exitDx=0", "exitDy=0"]
        if entry_xy:
            style += ["entryX=%s" % entry_xy[0], "entryY=%s" % entry_xy[1], "entryDx=0", "entryDy=0"]
        if style_extra:
            style.append(style_extra)
        pts = ""
        if points:
            pts = "<Array as=\"points\">%s</Array>" % "".join('<mxPoint x="%s" y="%s"/>' % p for p in points)
        self.cells.append(
            '<mxCell id="%s" value=%s style=%s edge="1" parent="1" source="%s" target="%s"><mxGeometry relative="1" as="geometry">%s</mxGeometry></mxCell>'
            % (cid, quoteattr(_inline(text)), quoteattr(";".join(style)), s, t, pts))
        return cid

    def line(self, x1, y1, x2, y2, color="#555555", dashed=False, width=1.5, end="block", text=""):
        """a free edge between two points"""
        cid = self._id()
        style = ["html=1", "rounded=0", "strokeColor=%s" % color, "strokeWidth=%s" % width,
                 "endArrow=%s" % end, "endFill=1", "fontSize=10", "labelBackgroundColor=#ffffff"]
        if dashed:
            style += ["dashed=1", "dashPattern=5 3"]
        self.cells.append(
            '<mxCell id="%s" value=%s style=%s edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
            '<mxPoint x="%s" y="%s" as="sourcePoint"/><mxPoint x="%s" y="%s" as="targetPoint"/></mxGeometry></mxCell>'
            % (cid, quoteattr(_inline(text)), quoteattr(";".join(style)), x1, y1, x2, y2))
        return cid

    def xml(self):
        head = ('<mxfile host="app.diagrams.net">\n  <diagram name="%s" id="%s">\n'
                '    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" '
                'arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0">\n'
                '      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
                % (self.name, self.name, self.width, self.height))
        body = "".join("        " + c + "\n" for c in self.cells)
        tail = "      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n"
        return head + body + tail

    def save(self, path):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(self.xml())
