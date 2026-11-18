#!/usr/bin/env python3
# generator for the Reference diagrams (50 .. 55) and the problem page (56 .. 59); writes drawio/*.drawio
# run: python tools/gen_reference_diagrams.py, then powershell -File export_drawio.ps1
# (or open a file in draw.io and edit it by hand: the .drawio file is the source)
import os
from xml.sax.saxutils import quoteattr

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'drawio')

BLUE = 'fillColor=#dae8fc;strokeColor=#6c8ebf;'
YEL = 'fillColor=#fff2cc;strokeColor=#d6b656;'
GRN = 'fillColor=#d5e8d4;strokeColor=#82b366;'
ORG = 'fillColor=#ffe6cc;strokeColor=#d79b00;'
PUR = 'fillColor=#e1d5e7;strokeColor=#9673a6;'
RED = 'fillColor=#f8cecc;strokeColor=#b85450;'
GRY = 'fillColor=#f5f5f5;strokeColor=#aaaaaa;'
TEAL = 'fillColor=#d0f0ea;strokeColor=#14b8a6;'
WHITE = 'fillColor=#ffffff;strokeColor=#999999;'
MONO = 'fontFamily=Courier New;'
BOX = 'rounded=1;whiteSpace=wrap;html=1;'
TXT = 'text;html=1;whiteSpace=wrap;verticalAlign=middle;'
ARROW = 'endArrow=classic;html=1;edgeStyle=none;labelBackgroundColor=#ffffff;'
GREYTXT = '<font color="#666666">%s</font>'


class Doc:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.n = 1

    def _id(self):
        self.n += 1
        return 'c%d' % self.n

    def v(self, x, y, w, h, value, style, parent='1'):
        i = self._id()
        self.cells.append(
            '        <mxCell id="%s" value=%s style="%s" vertex="1" parent="%s">\n'
            '          <mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/>\n'
            '        </mxCell>\n' % (i, quoteattr(value), style, parent, x, y, w, h))
        return i

    def e(self, src, tgt, style=ARROW, value='', points=None):
        i = self._id()
        pts = ''
        if points:
            pts = '<Array as="points">%s</Array>' % ''.join(
                '<mxPoint x="%s" y="%s"/>' % p for p in points)
        self.cells.append(
            '        <mxCell id="%s" value=%s style="%s" edge="1" parent="1" source="%s" target="%s">\n'
            '          <mxGeometry relative="1" as="geometry">%s</mxGeometry>\n'
            '        </mxCell>\n' % (i, quoteattr(value), style, src, tgt, pts))
        return i

    def line(self, p1, p2, style=ARROW, value='', via=None):
        i = self._id()
        pts = ''
        if via:
            pts = '<Array as="points">%s</Array>' % ''.join(
                '<mxPoint x="%s" y="%s"/>' % p for p in via)
        self.cells.append(
            '        <mxCell id="%s" value=%s style="%s" edge="1" parent="1">\n'
            '          <mxGeometry relative="1" as="geometry">'
            '<mxPoint x="%s" y="%s" as="sourcePoint"/><mxPoint x="%s" y="%s" as="targetPoint"/>%s'
            '</mxGeometry>\n'
            '        </mxCell>\n' % (i, quoteattr(value), style, p1[0], p1[1], p2[0], p2[1], pts))
        return i

    def save(self, w, h):
        text = ('<mxfile host="app.diagrams.net">\n'
                '  <diagram name="%s" id="%s">\n'
                '    <mxGraphModel dx="900" dy="500" grid="1" gridSize="10" guides="1" tooltips="1" '
                'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" '
                'math="0" shadow="0">\n'
                '      <root>\n'
                '        <mxCell id="0"/>\n'
                '        <mxCell id="1" parent="0"/>\n'
                '%s'
                '      </root>\n'
                '    </mxGraphModel>\n'
                '  </diagram>\n'
                '</mxfile>\n' % (self.name, self.name, w, h, ''.join(self.cells)))
        with open(os.path.join(OUT, self.name + '.drawio'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)


# ---------------------------------------------------------------- chips

def graph_chip(d, x, y, style, nodes, links):
    """a small rounded square with a few connected dots: a description in memory"""
    d.v(x, y, 56, 36, '', BOX + style + 'arcSize=18;')
    ids = [d.v(x + nx, y + ny, 9, 9, '', 'ellipse;html=1;fillColor=#404040;strokeColor=none;')
           for nx, ny in nodes]
    for a, b in links:
        d.e(ids[a], ids[b], 'endArrow=none;html=1;edgeStyle=none;strokeColor=#404040;strokeWidth=1.5;')


def chip(d, kind, x, y):
    if kind == 'gal':
        d.v(x, y, 56, 36, '.gal', 'shape=document;boundedLbl=1;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;' + GRN)
    elif kind == 'galm':
        d.v(x, y, 56, 36, '.gal', 'shape=document;boundedLbl=1;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;'
            'dashed=1;fillColor=#ffffff;strokeColor=#82b366;')
    elif kind == 'graph':
        graph_chip(d, x, y, TEAL, [(9, 22), (23, 7), (38, 22)], [(0, 1), (1, 2), (0, 2)])
    elif kind == 'comp':
        graph_chip(d, x, y, ORG, [(8, 6), (23, 6), (39, 6), (15, 22), (31, 22)],
                   [(0, 1), (1, 2), (0, 3), (1, 3), (1, 4), (2, 4), (3, 4)])
    elif kind == 'saxon':
        d.v(x, y, 56, 36, '&lt;/&gt;', 'shape=hexagon;perimeter=hexagonPerimeter2;size=0.22;whiteSpace=wrap;html=1;'
            'fontSize=12;fontStyle=1;' + PUR)
    elif kind == 'xml':
        d.v(x, y, 56, 36, '&lt;/&gt;', 'shape=document;boundedLbl=1;whiteSpace=wrap;html=1;fontSize=12;fontStyle=1;' + BLUE)
    elif kind == 'files':
        d.v(x, y, 56, 36, 'files', 'shape=document;boundedLbl=1;whiteSpace=wrap;html=1;fontSize=12;' + GRN)
    else:
        raise ValueError(kind)


# ---------------------------------------------------------------- 50 one run in detail

def run_in_detail():
    d = Doc('50_run_in_detail')
    stepx, stepw = 54, 200
    inx, outx = 274, 352
    lanex, lanew = 428, 64
    filex, filew = 700, 186
    failx, failw = 900, 118

    def y(r):
        return 56 + r * 56 + (14 if r >= 8 else 0) + (14 if r >= 11 else 0)

    steps = [
        # name, caption, built-in?, optional?, in, out, file, fail
        ('parse', 'reads your .gal files', 'b', False, 'gal', 'graph', None, 'syntax error'),
        ('validate', 'checks the whole description', 'b', False, 'graph', 'graph', 'lang-parsed.xml', 'rule broken'),
        ('Wizard', 'only if there is a command', 'b', True, 'graph', 'graph', None, 'command refused'),
        ('to XML', 'only with a language xslt', 'b', True, 'graph', 'saxon', 'lang-wizard.xml', None),
        ('your language xslt', 'your transforms, in order', 'y', True, 'saxon', 'saxon', 'your files (gal.cfg)', 'xslt error'),
        ('from XML', 'takes the result back', 'b', True, 'saxon', 'graph', 'lang-xslt.xml', 'unexpected XML'),
        ('seal and validate', 'closed versions stay closed', 'b', True, 'graph', 'graph', None, 'rule broken'),
        ('write .gal', 'new text, kept in memory', 'b', False, 'graph', 'galm', 'lang-final.xml', None),
        ('compile', 'merges the versions', 'b', False, 'graph', 'comp', None, 'name or label error'),
        ('compiled XML', 'always written', 'b', False, 'comp', 'xml', 'post-compiled.xml', None),
        ('your post xslt', 'only if you list one', 'y', True, 'xml', 'files', 'your files (gal.cfg)', 'xslt error'),
    ]

    # headers
    hy = 8
    hs = 'text;html=1;whiteSpace=wrap;verticalAlign=middle;align=center;fontSize=11;fontStyle=1;fontColor=#555555;'
    d.v(inx, hy, 134, 36, 'data: in → out', hs)
    for i, t in enumerate(['description', 'seal<br>copy', 'Saxon', 'compiled<br>picture']):
        d.v(lanex + i * lanew, hy, lanew, 36, t, hs)
    d.v(filex, hy, filew, 36, 'files written', hs)
    d.v(failx, hy, failw, 36, 'a failure here', hs)

    # lane backgrounds
    last = y(10) + 44
    for i in range(4):
        d.v(lanex + i * lanew + 2, 48, lanew - 4, last - 48 + 6, '', 'rounded=1;html=1;fillColor=#f6f6f6;strokeColor=none;arcSize=10;')

    # domain bars
    bar = 'rounded=1;whiteSpace=wrap;html=1;fillColor=#eeeeee;strokeColor=#aaaaaa;horizontal=0;fontSize=12;fontStyle=1;'
    d.v(8, y(0), 24, y(7) + 44 - y(0), 'LANGUAGE', bar)
    d.v(8, y(8), 24, y(10) + 44 - y(8), 'POST-LANGUAGE', bar)

    # lifelines
    def lifebar(lane, r0, r1, style, frm=8, to=36):
        x = lanex + lane * lanew + (lanew - 24) // 2
        top = y(r0) + frm
        bottom = y(r1) + to
        d.v(x, top, 24, bottom - top, '', 'rounded=1;html=1;arcSize=30;' + style)

    lifebar(0, 0, 8, TEAL)
    lifebar(1, 3, 6, 'fillColor=#eaf8f5;strokeColor=#14b8a6;dashed=1;')
    lifebar(2, 3, 5, PUR)
    lifebar(2, 10, 10, PUR)
    lifebar(3, 8, 10, ORG)

    ids = []
    for r, (name, cap, kind, opt, cin, cout, fil, fail) in enumerate(steps):
        yy = y(r)
        style = BOX + (BLUE if kind == 'b' else YEL) + 'fontSize=13;' + ('dashed=1;' if opt else '')
        val = '<b>%s</b><br><font style="font-size:11px" color="#555555">%s</font>' % (name, cap)
        ids.append(d.v(stepx, yy, stepw, 44, val, style))
        d.v(stepx - 10, yy - 8, 24, 24, '%d' % (r + 1),
            'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#404040;strokeColor=none;fontColor=#ffffff;fontStyle=1;fontSize=12;')
        chip(d, cin, inx, yy + 4)
        chip(d, cout, outx, yy + 4)
        d.line((inx + 59, yy + 22), (outx - 3, yy + 22))
        if fil:
            fs = BOX + GRN + MONO + 'fontSize=11;' if fil.endswith('.xml') else BOX + GRN + 'fontSize=11;'
            d.v(filex, yy + 8, filew, 28, fil, fs)
        if fail:
            d.v(failx, yy + 8, failw, 28, fail, BOX + RED + 'fontSize=11;')
    # arrows between the steps
    for r in range(len(steps) - 1):
        d.line((stepx + 100, y(r) + 44), (stepx + 100, y(r + 1)))

    # check marks on the two validations
    for r in (1, 6):
        d.v(inx + 63, y(r) + 3, 18, 14, '✓', 'text;html=1;fontSize=12;fontStyle=1;fontColor=#2e7d32;align=center;verticalAlign=middle;')

    # the end of the run
    ye = y(11)
    d.line((stepx + 100, y(10) + 44), (stepx + 100, ye))
    d.v(stepx, ye, stepw, 44,
        '<b>end of the run</b><br><font style="font-size:11px" color="#555555">only if every step succeeded</font>',
        BOX + GRN + 'fontSize=13;')
    chip(d, 'galm', inx, ye + 4)
    chip(d, 'gal', outx, ye + 4)
    d.line((inx + 59, ye + 22), (outx - 3, ye + 22))
    d.v(filex, ye + 8, filew, 28, 'your .gal files, rewritten', BOX + GRN + 'fontSize=11;fontStyle=1;')

    # the failure note
    ny = ye + 44 + 22
    d.v(54, ny, 26, 26, '!', 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#b85450;strokeColor=none;fontColor=#ffffff;fontStyle=1;fontSize=14;')
    d.v(90, ny - 4, 900, 34, 'Any failure stops the run. No .gal file is changed, and the message names the cause.',
        TXT + 'align=left;fontSize=13;')

    # legend
    ly = ny + 52
    items = [('gal', '.gal text'), ('galm', '.gal text in memory'), ('graph', 'description'),
             ('saxon', 'XML in Saxon'), ('xml', 'XML'), ('comp', 'compiled picture'), ('files', 'your files')]
    x = 54
    for kind, label in items:
        chip(d, kind, x, ly)
        d.v(x + 60, ly, 90, 36, label, TXT + 'align=left;fontSize=11;')
        x += 144
    ly2 = ly + 52
    d.v(54, ly2, 26, 18, '', BOX + BLUE)
    d.v(84, ly2 - 6, 90, 30, 'built in', TXT + 'align=left;fontSize=11;')
    d.v(190, ly2, 26, 18, '', BOX + YEL)
    d.v(220, ly2 - 6, 160, 30, 'yours, listed in gal.cfg', TXT + 'align=left;fontSize=11;')
    d.v(400, ly2, 26, 18, '', BOX + BLUE + 'dashed=1;')
    d.v(430, ly2 - 6, 160, 30, 'optional: may be skipped', TXT + 'align=left;fontSize=11;')
    d.v(610, ly2, 26, 18, '', BOX + GRN)
    d.v(640, ly2 - 6, 160, 30, 'files on disk', TXT + 'align=left;fontSize=11;')
    d.save(1040, ly2 + 40)


# ---------------------------------------------------------------- 51 libraries

def libraries():
    d = Doc('51_libraries')
    st = 'fontSize=12;align=center;'

    def box(x, y, w, h, name, desc, color):
        return d.v(x, y, w, h, '<b>%s</b><br>%s' % (name, desc), BOX + color + st)

    exe_lib = box(20, 20, 300, 56, 'galimatron_executable_library', 'the command line (Boost.Program_options)', BLUE)
    exe = box(350, 20, 300, 56, 'galimatron_executable', '<font face="Courier New">main.cpp</font> → galimatron', GRN)
    runtime = box(350, 110, 300, 72, 'galimatron_runtime_library',
                  'config, filesystem decorator, summary, crash handler, error printing, translate', BLUE)
    translator = box(350, 216, 300, 72, 'galimatron_translator_library',
                     'parser, state, Wizard, validator, compiler, XML, seal, the sequence of steps', BLUE)
    common = box(350, 322, 300, 56, 'galimatron_common_library', 'exception vocabulary, path report', BLUE)
    gfs = box(20, 412, 300, 56, 'global_filesystem_library', 'the filesystem as a struct of functions', TEAL)
    gcommon = box(350, 412, 300, 72, 'global_common_library',
                  'type aliases, logging helpers, scope guard, private memory', TEAL)
    pch = box(350, 518, 300, 56, 'global_pch_library', 'owns the precompiled header (<font face="Courier New">pch.hpp</font>)', TEAL)
    a = 'html=1;rounded=0;strokeColor=#555555;strokeWidth=1.5;endArrow=classic;'
    d.e(exe, exe_lib, a + 'edgeStyle=none;')
    d.e(exe, runtime, a + 'edgeStyle=none;')
    d.e(runtime, translator, a + 'edgeStyle=none;')
    d.e(translator, common, a + 'edgeStyle=none;')
    d.e(exe_lib, common, a + 'edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;entryX=0;entryY=0.5;', points=[(170, 350)])
    d.e(runtime, gfs, a + 'edgeStyle=orthogonalEdgeStyle;exitX=0;exitY=0.5;entryX=0;entryY=0.5;', points=[(8, 146), (8, 440)])
    d.e(common, gcommon, a + 'edgeStyle=none;')
    d.e(gfs, gcommon, a + 'edgeStyle=none;')
    d.e(gcommon, pch, a + 'edgeStyle=none;')

    ex = 700
    d.v(ex, 20, 300, 22, '<b>External libraries</b>', TXT + 'align=left;fontSize=13;')
    ext = [
        ('SaxonC-HE · Taskflow · inja (private to the translator)', 44),
        ('ANTLR runtime · pugixml · range-v3 · Boost.Graph, Hash2, ... (public)', 44),
        ('leaf_spy (translator and runtime)', 30),
        ('multi_index_lookup · base64 · magic_enum (global_common_library)', 44),
        ('Boost (algorithm, graph, leaf, multi_index, uuid, asio) · Logme · nlohmann_json · pugixml · range-v3 '
         '(the PCH makes these visible everywhere)', 58),
        ('Boost.Program_options', 30),
        ('Boost.Units · Boost.Process (tests)', 30),
    ]
    y = 50
    for text, h in ext:
        d.v(ex, y, 300, h, text, BOX + 'fillColor=#f8f8f8;strokeColor=#999999;dashed=1;fontSize=11;align=left;spacingLeft=6;')
        y += h + 8
    d.v(ex, y + 6, 300, 70,
        'multi_index_lookup and leaf_spy are separate repositories, fetched at configure time. '
        'Tests are separate targets: global_tests, galimatron_tests (and galimatron_crash_child), uuid_protocol_tests.',
        TXT + 'align=left;fontSize=11;fontColor=#555555;')
    d.v(20, 600, 650, 36,
        'An arrow: links PUBLIC to. The dependency runs one way, down. Dashed boxes are external libraries.',
        TXT + 'align=left;fontSize=12;fontColor=#555555;')
    d.save(1020, 650)


# ---------------------------------------------------------------- 52 step sequences

def step_sequences():
    d = Doc('52_step_sequences')
    rows = ['gal2cpp', 'validate', 'Wizard', 'before_xslt', 'cpp2xml', 'xml2saxon', 'your xslt', 'xml2cpp',
            'after_xslt', 'cpp2gal', 'gal2cpp (skip)', 'cpp2post_cpp', 'post_cpp2post_xml', 'post_xml2saxon',
            'your post xslt']
    cols = [
        ('no XSLT', 7, {'gal2cpp', 'validate', 'Wizard', 'cpp2gal', 'gal2cpp (skip)', 'cpp2post_cpp', 'post_cpp2post_xml'}),
        ('language XSLT', 13, set(rows[:13])),
        ('post XSLT', 9, {'gal2cpp', 'validate', 'Wizard', 'cpp2gal', 'gal2cpp (skip)', 'cpp2post_cpp',
                          'post_cpp2post_xml', 'post_xml2saxon', 'your post xslt'}),
        ('both', 15, set(rows)),
    ]
    x0, lw, cw, gap = 10, 150, 112, 8
    for i, (t, n, _) in enumerate(cols):
        d.v(x0 + lw + i * (cw + gap), 8, cw, 40, '<b>%s</b><br><font color="#666666">%d steps</font>' % (t, n),
            TXT + 'align=center;fontSize=12;')
    ry = 56
    pitch = 27
    for r, name in enumerate(rows):
        y = ry + r * pitch
        d.v(x0, y, lw - 8, 23, name, TXT + MONO + 'align=right;fontSize=11;')
        for i, (_, _, have) in enumerate(cols):
            x = x0 + lw + i * (cw + gap)
            if name not in have:
                d.v(x, y, cw, 23, '', BOX + 'fillColor=none;strokeColor=#dddddd;dashed=1;arcSize=20;')
                continue
            if name == 'gal2cpp (skip)':
                style = GRY
            elif name in ('your xslt', 'your post xslt'):
                style = YEL
            else:
                style = BLUE
            d.v(x, y, cw, 23, '', BOX + style + 'arcSize=20;')
    ly = ry + len(rows) * pitch + 14
    d.v(x0 + lw, ly, 26, 16, '', BOX + BLUE)
    d.v(x0 + lw + 30, ly - 7, 90, 30, 'built in', TXT + 'align=left;fontSize=11;')
    d.v(x0 + lw + 120, ly, 26, 16, '', BOX + YEL)
    d.v(x0 + lw + 150, ly - 7, 90, 30, 'yours', TXT + 'align=left;fontSize=11;')
    d.v(x0 + lw + 240, ly, 26, 16, '', BOX + GRY)
    d.v(x0 + lw + 270, ly - 7, 190, 30, 'skipped: only logs "skip transformation"', TXT + 'align=left;fontSize=11;')
    d.save(740, ly + 30)


# ---------------------------------------------------------------- 53 wizard commands

def wizard_commands():
    d = Doc('53_wizard_command_effects')
    cmds = [('create root aggregate', 'P'), ('create aggregate', 'P'), ('copy aggregate', 'P'),
            ('continue aggregate', 'P'), ('delete aggregate', 'H'), ('create version', 'P'),
            ('delete version', 'P'), ('collapse version', 'P'), ('create label', 'P'), ('create tag', 'P'),
            ('delete tag', 'H'), ('create ordering', 'P'), ('create hash', 'P'), ('delete hash', 'P'),
            ('{ ... }  a batch of the commands above', '–')]
    d.v(10, 8, 520, 24, '<b>Wizard commands</b> &nbsp; <b>P</b>: the description changes &nbsp;·&nbsp; '
        '<b>H</b>: a delete is written into the history', TXT + 'align=left;fontSize=12;')
    y = 40
    for name, eff in cmds:
        d.v(10, y, 300, 26, name, BOX + 'fillColor=#ffffff;strokeColor=#bbbbbb;fontSize=12;align=left;spacingLeft=8;' + MONO)
        style = {'P': BLUE, 'H': ORG, '–': GRY}[eff]
        d.v(316, y, 40, 26, eff, BOX + style + 'fontSize=12;fontStyle=1;')
        y += 31
    d.save(380, y + 10)


# ---------------------------------------------------------------- 54 places

def places():
    d = Doc('54_places')
    hx = [10, 250, 480, 690]
    hw = [236, 226, 206, 300]
    hs = BOX + 'fillColor=#eeeeee;strokeColor=#aaaaaa;fontSize=12;fontStyle=1;'
    for x, w, t in zip(hx, hw, ['place', 'key in gal.cfg', 'written', 'cleaned']):
        d.v(x, 8, w, 28, t, hs)
    rows = [
        (GRN, 'your .gal files<br><font color="#666666">one folder</font>', 'input-gal-dir<br>= output-gal-dir',
         'at the end of a successful run, only if the text changed', 'files not rewritten are removed at the end'),
        (GRN, 'your .gal files<br><font color="#666666">two folders: input</font>', 'input-gal-dir',
         'never', 'never'),
        (GRN, 'your .gal files<br><font color="#666666">two folders: output</font>', 'output-gal-dir',
         'at once', 'every .gal file removed at the start'),
        (ORG, 'XML dumps', 'intermediate-xml-dir', 'at once', 'everything removed at the start'),
        (ORG, 'files of your XSLT<br><font color="#666666">one store per entry</font>', 'store-dir<br>(and its extentions)',
         'at once, only if the text changed', 'not rewritten: removed at the end, unless delete-if-not-rewrited is false'),
    ]
    y = 44
    for color, place, key, wr, cl in rows:
        h = 54
        d.v(hx[0], y, hw[0], h, place, BOX + color + 'fontSize=12;')
        d.v(hx[1], y, hw[1], h, key, BOX + WHITE + 'fontSize=11;' + MONO)
        d.v(hx[2], y, hw[2], h, wr, BOX + WHITE + 'fontSize=11;')
        d.v(hx[3], y, hw[3], h, cl, BOX + WHITE + 'fontSize=11;')
        y += h + 6
    y += 10
    d.v(10, y, 990, 36,
        '<b>at once</b>: as soon as the step finishes &nbsp;·&nbsp; <b>at the end</b>: only after the whole run succeeded '
        '&nbsp;·&nbsp; the same path written twice in one run is an error &nbsp;·&nbsp; the folders may not be nested',
        BOX + 'fillColor=#fafafa;strokeColor=#cccccc;fontSize=11;align=left;spacingLeft=8;')
    y += 56
    d.v(10, y, 300, 22, '<b>where the result of an XSLT goes</b>', TXT + 'align=left;fontSize=12;')
    y += 30
    routes = [
        ('the principal result', 'the intermediate folder', ORG),
        ('href="@@alias@@path@@"', 'the store with that alias', ORG),
    ]
    for src, dst, color in routes:
        a = d.v(10, y, 260, 34, src, BOX + YEL + 'fontSize=12;' + MONO)
        b = d.v(340, y, 230, 34, dst, BOX + color + 'fontSize=12;')
        d.e(a, b)
        y += 46
    d.save(1010, y + 10)


# ---------------------------------------------------------------- 55 test axes

def test_axes():
    d = Doc('55_test_axes')
    d.v(10, 8, 600, 24, '<b>test axes</b> &nbsp; (<font face="Courier New">test_axes::mark(...)</font> in the suite description)',
        TXT + 'align=left;fontSize=12;')
    rows = [('product', 'full integration: gal.cfg, log.cfg, translate_production'),
            ('translator_slice', 'chosen built-in steps: translate_slice'),
            ('parser', 'the grammar and the version rule'),
            ('component', 'one helper'),
            ('process', 'the crash handler in a child process')]
    y = 40
    for a, t in rows:
        d.v(10, y, 170, 30, a, BOX + GRY + MONO + 'fontSize=12;fontStyle=1;')
        d.v(186, y, 440, 30, t, BOX + WHITE + 'fontSize=12;align=left;spacingLeft=8;')
        y += 36
    d.save(640, y + 10)


# ---------------------------------------------------------------- 56 .. 59 the problem page

def badge(d, x, y, text):
    d.v(x, y, 26, 26, text, 'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#404040;strokeColor=none;'
        'fontColor=#ffffff;fontStyle=1;fontSize=11;')


def versions_side_by_side():
    d = Doc('56_versions_side_by_side')
    items = [
        ('old phone app', 'built last year', 'id, price', 'v1', GRY),
        ('files saved last year', 'on the disk', 'id, price', 'v1', GRY),
        ('tablet app', 'last spring', 'id, price, currency', 'v2', BLUE),
        ('web app', 'today', 'id, price (long), currency', 'v3', GRN),
    ]
    server = d.v(20, 190, 830, 50,
                 '<b>the server</b> must understand all of them: v1, v2 and v3',
                 BOX + YEL + 'fontSize=14;')
    for i, (name, when, shape, ver, color) in enumerate(items):
        x = 20 + i * 212
        c = d.v(x, 24, 196, 96,
                '<b>%s</b><br><font color="#666666">%s</font><br><font face="Courier New" style="font-size:11px">%s</font>'
                % (name, when, shape), BOX + color + 'fontSize=13;')
        badge(d, x - 8, 12, ver)
        d.e(c, server, ARROW)
    d.v(20, 252, 830, 30, 'Three versions of the same data are in use at the same time.',
        TXT + 'align=left;fontSize=13;fontColor=#555555;')
    d.save(880, 300)


def one_fact_many_places():
    d = Doc('57_one_fact_many_places')
    ch = d.v(20, 96, 220, 92, '<b>the change</b><br><font face="Courier New">price: int → long</font>',
             BOX + ORG + 'fontSize=14;')
    rows = [
        ('database', 'price BIGINT', True),
        ('code', 'long price;', True),
        ('documentation', 'price (int)', False),
        ('spreadsheet', 'price (int)', False),
        ('tests', 'price as an int', False),
    ]
    for i, (name, text, done) in enumerate(rows):
        y = 10 + i * 56
        b = d.v(340, y, 360, 44, '<b>%s</b> &nbsp; <font face="Courier New" style="font-size:12px">%s</font>' % (name, text),
                BOX + (GRN if done else RED) + 'fontSize=13;')
        d.v(730, y + 8, 120, 28, 'updated' if done else 'forgotten',
            BOX + (GRN if done else RED) + 'fontSize=12;fontStyle=1;')
        d.e(ch, b, ARROW + 'exitX=1;exitY=0.5;entryX=0;entryY=0.5;exitDx=0;exitDy=0;entryDx=0;entryDy=0;')
    d.v(20, 296, 830, 30, 'The same fact is typed in many places. Nobody has a list of them, so some are forgotten.',
        TXT + 'align=left;fontSize=13;fontColor=#555555;')
    d.save(880, 340)


def published_stays_closed():
    d = Doc('58_published_stays_closed')
    d.v(20, 4, 400, 24, '<b>Edited in place</b>', TXT + 'align=left;fontSize=14;')
    n1 = d.v(20, 40, 170, 70, '<b>a quick fix</b><br>price becomes long', BOX + YEL + 'fontSize=13;')
    v2a = d.v(300, 40, 190, 70, '<b>version 2</b> (shipped)<br><font face="Courier New" style="font-size:12px">price: long</font>',
              BOX + RED + 'dashed=1;fontSize=13;')
    r1 = d.v(550, 40, 300, 70, 'old apps and stored files no longer match<br><font color="#666666">and nothing warned you</font>',
             BOX + RED + 'fontSize=13;')
    d.e(n1, v2a, ARROW, 'edits')
    d.e(v2a, r1, ARROW)
    d.v(20, 150, 500, 24, '<b>Closed, then a new version</b>', TXT + 'align=left;fontSize=14;')
    v2b = d.v(20, 186, 170, 70, '<b>version 2</b> (shipped)<br><font face="Courier New" style="font-size:12px">price: int</font>',
              BOX + BLUE + 'fontSize=13;')
    v3 = d.v(300, 186, 190, 70, '<b>version 3</b> (new)<br><font face="Courier New" style="font-size:12px">price: long</font>',
             BOX + GRN + 'fontSize=13;')
    r2 = d.v(550, 186, 300, 70, 'old apps read version 2, new apps read version 3<br><font color="#666666">every version stays true</font>',
             BOX + GRN + 'fontSize=13;')
    d.e(v2b, v3, ARROW, 'new version')
    d.e(v3, r2, ARROW)
    d.v(20, 280, 830, 30, 'A published version is a promise. A change belongs in a new version.',
        TXT + 'align=left;fontSize=13;fontColor=#555555;')
    d.save(880, 320)


def chores_checklist():
    d = Doc('59_chores_checklist')
    d.v(20, 10, 440, 300, '', BOX + 'fillColor=#ffffff;strokeColor=#999999;arcSize=4;')
    d.v(36, 18, 400, 30, '<b>To make version 3</b>', TXT + 'align=left;fontSize=14;')
    chores = [
        ('copy the description of version 2', True),
        ('make the change', True),
        ('give the changed items new ids', True),
        ('write the conversion from version 2', False),
        ('update the code', False),
        ('update the documentation', False),
        ('update the tests', False),
    ]
    for i, (text, done) in enumerate(chores):
        y = 58 + i * 34
        if done:
            d.v(40, y, 22, 22, '✓', BOX + GRN + 'fontSize=13;fontStyle=1;arcSize=20;')
        else:
            d.v(40, y, 22, 22, '', BOX + 'fillColor=#ffffff;strokeColor=#b85450;strokeWidth=2;arcSize=20;')
        d.v(76, y - 4, 370, 30, text, TXT + 'align=left;fontSize=13;')
    d.v(500, 120, 330, 90,
        'Every change repeats the same chores.<br>Somebody has to remember all of them, every time.',
        TXT + 'align=left;fontSize=14;fontColor=#b85450;fontStyle=1;')
    d.save(860, 330)


if __name__ == '__main__':
    versions_side_by_side()
    one_fact_many_places()
    published_stays_closed()
    chores_checklist()
    run_in_detail()
    libraries()
    step_sequences()
    wizard_commands()
    places()
    test_axes()
    print('ok')
