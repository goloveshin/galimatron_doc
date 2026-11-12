"""The smaller developer diagrams, part B: sequence, validation, Wizard, compile, XML, places, tests, build."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from drawgen import *
from small_a import save, rhombus


# ---------------------------------------------------------------- 36 sequence builder
def sequence():
    d = Diagram("36_dev_sequence_builder", 2300, 1000)
    d.text(30, 16, 1500, "The list of steps is built, not written", font=20, bold=True)
    seed = d.box(30, 90, 520, "**the seed**: what is configured\n• `cpp2cpp_validate`\n• `cpp2cpp_wizard`\n• with a language xslt: `cpp2cpp_before_xslt`, your xslts, `cpp2cpp_after_xslt`\n• your post xslts", fill=BLUE[0], stroke=BLUE[1], font=12, align="left", valign="top", h=190)
    cat = d.box(600, 90, 640, "**the catalog**: eight edges (domain, state)\n• `gal2cpp`  GaL → CPP\n• `cpp2gal`  CPP → GaL\n• `cpp2xml`  CPP → XML\n• `xml2saxon`  XML → SAXON\n• `xml2cpp`  SAXON → CPP\n• `cpp2post_cpp`  LANGUAGE CPP → POST CPP\n• `post_cpp2post_xml`  POST CPP → POST XML\n• `post_xml2saxon`  POST XML → POST SAXON", fill="#f2f7fc", stroke=BLUE[1], font=12, align="left", valign="top", dashed=True, h=190)
    bld = d.box(1290, 90, 980, "**builder_t**\n1. check the domain order (LANGUAGE, then POST_LANGUAGE)\n2. check the catalog has the seven edges\n3. before each seed step: **breadth-first shortest path** over the catalog, language part stays in LANGUAGE\n"
                "4. language part done: append `cpp2gal` unless the last step is one\n5. no post step: path to POST XML; a post xslt: path to POST SAXON", fill=GREEN[0], stroke=GREEN[1], font=12, align="left", valign="top", h=190)
    d.edge(seed, bld, exit_xy=(0.5, 0), entry_xy=(0.1, 0), points=[(290, 60), (1388, 60)])
    d.edge(cat, bld, straight=True)
    names = [("gal2cpp", "auto"), ("validate", "seed"), ("Wizard", "seed"), ("before_xslt", "seed"), ("cpp2xml", "auto"), ("xml2saxon", "auto"),
             ("your xslt", "user"), ("xml2cpp", "auto"), ("after_xslt", "seed"), ("cpp2gal", "auto"), ("gal2cpp (skip)", "skip"),
             ("cpp2post_cpp", "auto"), ("post_cpp2post_xml", "auto"), ("post_xml2saxon", "auto"), ("your post xslt", "user")]
    rows = [("no xslt  (7)", [0, 1, 2, 9, 10, 11, 12]), ("language xslt only  (13)", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
            ("post xslt only  (9)", [0, 1, 2, 9, 10, 11, 12, 13, 14]), ("both  (15)", list(range(15)))]
    d.text(30, 320, 1500, "**Result** (solid: the seed; dashed: inserted by the builder; yellow: your xslt)", font=13)
    y = 360
    for label, idxs in rows:
        d.box(30, y, 250, label, h=34, fill="#f2f2f2", stroke="#cccccc", font=12, bold=True, align="left")
        x = 300
        prev = None
        for i in idxs:
            nm, k = names[i]
            f, s, dash = {"seed": (BLUE[0], BLUE[1], False), "user": (YELLOW[0], YELLOW[1], False),
                          "auto": ("#f2f7fc", BLUE[1], True), "skip": ("#f5f5f5", "#aaaaaa", True)}[k]
            c = d.box(x, y, 126, nm, h=34, fill=f, stroke=s, font=10, dashed=dash, sw=1.5)
            if prev:
                d.edge(prev, c, straight=True, width=1)
            prev = c
            x += 132
        y += 48
    d.text(30, y + 10, 2200, "The second `gal2cpp` is the way from GaL back to CPP for the post part. It is skipped at run time because `language_state_` is set.\n"
           "The testing path (`prepare_testing_transforms`) runs the builder with `finish_sequence = false`: the seed is only the flagged steps, and an edge is inserted only where two seed steps do not meet.", font=11, color="#555555")
    d.box(30, y + 80, 2240, "**Domains**: `LANGUAGE` (the language graph) → `POST_LANGUAGE` (the compiled view); `cpp2post_cpp` is the one edge that changes the domain, and there is no way back.\n"
          "**State types**: `GaL` text · `CPP` the graph in memory · `XML` pugixml text · `SAXON` the document held for an xslt.", h=64, fill="#fbfbfb", stroke="#cccccc", font=12, align="left", valign="top")
    save(d, "36_dev_sequence_builder")


# ---------------------------------------------------------------- 37 validation DAG
def validate_dag():
    d = Diagram("37_dev_validate_dag", 2100, 800)
    d.text(30, 16, 1500, "The twelve checks of cpp2cpp_validate", font=20, bold=True)
    d.text(30, 50, 1900, "A Taskflow subflow. An arrow means \"runs after\". A failure is thrown on a worker and rethrown by `subflow.join()`.", font=12, color="#555555")
    nw, nh, step = 420, 46, 62
    x0 = [40, 520, 1000, 1480]
    y0 = 110
    def n(x, i, t, kind="check"):
        f, s = ("#eef4fb", "#6c8ebf") if kind == "check" else (GREEN[0], GREEN[1])
        return d.box(x, y0 + i * step, nw, t, h=nh, fill=f, stroke=s, font=11, sw=1.5)
    root = n(x0[0], 3, "is root aggregate single")
    c = ["root declarations from zero, continuous", "root definitions repeat declarations", "aggregate declarations: deleted continuous",
         "aggregate definitions not deleted", "aggregate definitions repeat declarations", "anonymous versions owned",
         "aggregate names unique", "aggregate indices unique, continuous"]
    nodes = [n(x0[1], i, t) for i, t in enumerate(c)]
    match = n(x0[2], 0, "aggregate declarations match root")
    hm = n(x0[3], 1, "version hashes match")
    hp = n(x0[3], 3, "version hashes present")
    join = d.box(1480, y0 + 5 * step, nw, "join → `compile_for_validation`\n(`cpp2post_cpp::translate`)", h=nh + 10, fill=GREEN[0], stroke=GREEN[1], font=11, sw=1.5)
    mid = nh // 2
    b1, b2, b3, b4 = x0[0] + nw + 40, x0[1] + nw + 40, x0[2] + nw + 40, x0[3] + nw + 30
    ry = y0 + 3 * step + mid
    for i, nd in enumerate(nodes):
        d.edge(root, nd, width=1.2, exit_xy=(1, 0.5), entry_xy=(0, 0.5), points=[(b1, ry), (b1, y0 + i * step + mid)])
    d.edge(nodes[0], match, straight=True, width=1.2)
    for i in (1, 2, 3, 4, 5):
        for tgt, ty in ((hm, y0 + step + mid), (hp, y0 + 3 * step + mid)):
            d.edge(nodes[i], tgt, width=1.0, color="#999999", exit_xy=(1, 0.5), entry_xy=(0, 0.5), points=[(b2, y0 + i * step + mid), (b2, ty)])
    for tgt, ty in ((hm, y0 + step + mid), (hp, y0 + 3 * step + mid)):
        d.edge(match, tgt, width=1.0, color="#999999", exit_xy=(1, 0.5), entry_xy=(0, 0.5), points=[(b3, y0 + mid), (b3, ty)])
    jy = y0 + 5 * step + (nh + 10) // 2
    for src, sy in ((hm, y0 + step + mid), (hp, y0 + 3 * step + mid), (nodes[6], y0 + 6 * step + mid), (nodes[7], y0 + 7 * step + mid)):
        d.edge(src, join, dashed=True, color="#3b6ea5", width=1.2, exit_xy=(1, 0.5), entry_xy=(1, 0.5), points=[(b4, sy), (b4, jy)])
    d.box(40, y0 + 8 * step + 20, 1900,
          "• With `create root aggregate` in the command (or a batch), **seven** checks do nothing: the four root checks, `anonymous versions owned`, both hash checks.\n"
          "• `validate_memo_t` caches only the three root gate checks. The Wizard replaces memo and checker together.\n"
          "• The Wizard's own checks (`may_execute_wizard_command`) are not in this graph.", h=84,
          fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
    save(d, "37_dev_validate_dag")


# ---------------------------------------------------------------- 38 Wizard flow
def wizard_flow():
    d = Diagram("38_dev_wizard_flow", 2100, 860)
    d.text(30, 16, 1500, "The Wizard step", font=20, bold=True)
    a = d.box(30, 90, 420, "`cpp2cpp_wizard::translate(language)`\nno Wizard statement: return unchanged", h=60, fill=BLUE[0], stroke=BLUE[1], font=11)
    b = d.box(30, 190, 420, "`validate_->is_wizard_command_single()`\none statement in the whole graph", h=60, fill=BLUE[0], stroke=BLUE[1], font=11)
    s = rhombus(d, 70, 290, 340, 80, "batch?")
    one = d.box(30, 420, 420, "`apply_one(type)`: a `switch` over `command_et`", h=50, fill=BLUE[0], stroke=BLUE[1], font=11)
    bat = d.box(520, 280, 640, "**apply_wizard_batch**\n• `may_execute_wizard_command()`: the batch context\n• for each item: `refresh_checks()` (new memo, new checker, re-snapshot) → overwrite the stored statement's `type` and `data` → `is_wizard_batch_command_create()` → `apply_one(item.type)`\n• restore the statement",
                h=130, fill=BLUE[0], stroke=BLUE[1], font=11, align="left", valign="top")
    ap = d.box(30, 520, 1130, "**an `apply_*` function**: `validate_->may_execute_wizard_command()` (the per-command checks, in order; the first failure throws) → change the graph with `builder_t` (new vertices get `created_by_wizard`) → `refresh_live_and_hashed(vd_aggregate)` after structural edits",
               h=76, fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    cm = d.box(30, 640, 1130, "`comment_executed_command()`: the text of the statement becomes `//` lines at the **top of its chunk**; `cpp2gal` prints only comments for a Wizard statement, so the command disappears", h=60,
               fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    d.edge(a, b, straight=True); d.edge(b, s, straight=True)
    d.edge(s, one, text="no", exit_xy=(0.5, 1), entry_xy=(0.5, 0))
    d.edge(s, bat, text="yes", exit_xy=(1, 0.5), entry_xy=(0, 0.5))
    d.edge(one, ap, straight=True); d.edge(bat, ap, exit_xy=(0.5, 1), entry_xy=(0.8, 0))
    d.edge(ap, cm, straight=True)
    cmds = [("CREATE_ROOT_AGGREGATE", "P"), ("CREATE_AGGREGATE", "P"), ("COPY_AGGREGATE", "P"), ("CONTINUE_AGGREGATE", "P"), ("DELETE_AGGREGATE", "H"),
            ("CREATE_VERSION", "P"), ("DELETE_VERSION", "P"), ("COLLAPSE_VERSION", "P"), ("CREATE_LABEL", "P"), ("CREATE_TAG", "P"), ("DELETE_TAG", "H"),
            ("CREATE_ORDERING", "P"), ("CREATE_HASH", "P"), ("DELETE_HASH", "P"), ("BATCH", "–")]
    d.text(1260, 90, 800, "**the commands**  (P: the graph changes · H: a `delete` is written into the history)", font=12)
    for i, (c, k) in enumerate(cmds):
        y = 124 + i * 36
        d.box(1260, y, 330, "`%s`" % c, h=30, fill="#ffffff", stroke="#cfcfcf", font=10, align="left")
        d.box(1594, y, 40, k, h=30, fill="#ffffff", stroke="#cfcfcf", font=10, bold=True)
        d.box(1638, y, 400, "`apply_wizard_%s`" % c.lower(), h=30, fill="#eef7ee", stroke="#cfcfcf", font=10, align="left")
    d.box(30, 740, 1130, "**closed versions**: a root version at or before `last_hashed`. The validator protects them; the `apply_*` functions assume the checks passed. A batch refreshes the checker between commands so the next one sees the new seal.", h=60,
          fill=YELLOW[0], stroke=YELLOW[1], font=11, align="left", valign="top")
    save(d, "38_dev_wizard_flow")


# ---------------------------------------------------------------- 39 compile flow
def compile_flow():
    d = Diagram("39_dev_compile_flow", 2200, 900)
    d.text(30, 16, 1500, "The compile step: language graph → compiled_part_t", font=20, bold=True)
    chain = [
        ("**1 root aggregate**\n`create_merged_versions_entities`: per root version, parked bodies first, then its statements", BLUE),
        ("**2 `compile_merged_versions_entities`**\n`naming_unnamed_tags` → `remember_resolved_tag_names` → `remember_values_before` →\nper version: `check_labels_in_version` → `compile_tags_in_version` → `template_engine::render` → `tag_container`\nroot only: `compile_orderings_in_version`", BLUE),
        ("**3 every other aggregate**\nthe same two calls, with the root's statements copied in first (unless the version is `local` or `own`)", BLUE),
        ("**4 `notify_default_aggregates_ordering`**\n`ranks_of_ordering`: topological sort, longest chain, strict weak order check → the position of each aggregate", BLUE),
        ("**5 `force_resolve_labels`**\nlabel references become static values", BLUE),
    ]
    y = 90
    ids = []
    for t, (f, s) in chain:
        ids.append(d.box(30, y, 900, t, fill=f, stroke=s, font=12, align="left", valign="top"))
        y += d.last_h + 30
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b, straight=True)
    d.text(1010, 90, 1100, "**which statements reach a version**", font=13)
    rows = [("same version", "yes"), ("later version", "no"), ("earlier, mode `inherit`", "yes"), ("earlier, mode `local`", "no"),
            ("earlier, mode `own`", "only this aggregate's"), ("earlier, mode `once`", "only the root's"), ("tag mode `once` / `local`", "only where written")]
    for i, (a, b) in enumerate(rows):
        d.box(1010, 124 + i * 44, 480, a, h=36, fill="#f7f7f7", stroke="#cccccc", font=11, align="left")
        d.box(1494, 124 + i * 44, 400, b, h=36, fill="#eef7ee" if b == "yes" else "#fdf3f2" if b == "no" else "#fff9e0", stroke="#cccccc", font=11, align="left")
    d.box(1010, 450, 884, "**last declaration wins.** `compile_tags_in_version` walks from the end; the first statement seen per name is kept, `delete name;` consumes the name.\n"
          "**an example**\nroot v0 `currency = EUR` · Apple v0 `price = 3` · Apple v1 `price = 4`\ncompiled Apple v0: `currency = EUR`, `price = 3`\ncompiled Apple v1: `currency = EUR` (copied from the root), `price = 4`", h=170,
          fill=GREEN[0], stroke=GREEN[1], font=12, align="left", valign="top")
    save(d, "39_dev_compile_flow")


# ---------------------------------------------------------------- 40 XML round trip
def xml_roundtrip():
    d = Diagram("40_dev_xml_roundtrip", 2400, 760)
    d.text(30, 16, 1500, "The XML round trip", font=20, bold=True)
    boxes = [
        ("**language_part_t**\nvertices keep `user_formatting` and `user_comments`", GREEN, 340),
        ("**cpp2xml::translate**\nclear the layout table; for each vertex with text or comments write `layout-mark=\"N\"` and store {text, comments, fingerprint}", BLUE, 460),
        ("**language XML**\nprinted, then parsed into Saxon by `xml2saxon`", PURPLE, 340),
        ("**your xslt**\nchanges, adds, deletes", YELLOW, 300),
        ("**xml2cpp_saxon**\n`builder_t` builds a new graph; `restore_layout`: comments always; text only if the fingerprint is unchanged", BLUE, 520),
    ]
    x = 30
    ids = []
    for t, (f, s), w in boxes:
        ids.append(d.box(x, 90, w, t, h=130, fill=f, stroke=s, font=11, align="left", valign="top"))
        x += w + 40
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b, straight=True)
    half = 1140
    d.box(30, 270, half, "**language XML**  `<galimatron><language>`", h=32, fill=BLUE[0], stroke=BLUE[1], font=12)
    d.box(30 + half + 40, 270, half, "**compiled XML**  `<galimatron><compiled>`", h=32, fill=ORANGE[0], stroke=ORANGE[1], font=12)
    lang = ("`<chunk><location>` per file\n`<root-aggregate>` / `<aggregate>` with declarations and definitions\n`<tag index name mode layout-mark>` with `<label-refs>` and `<values>` (`template-engine`)\n"
            "`<label>` static or dynamic · `<ordering>` · `<delete>`\nWizard marks: `<dynamic wizard=\"...\"/>`, `<dynamic labelname=\"value\"/>`\n`<string-delimiters>` · `<history>`")
    comp = ("the same skeleton; each version lists only the **effective tags**\na tag always has its name\nlabels are **attributes on `<value>`**: `<value index=\"0\" field=\"type\">`\n"
            "`<string>` holds the **rendered** text\n`<orderings><ordering name index=\"position\"/>` per aggregate version\nno Wizard marks · `<history>`")
    d.box(30, 306, half, lang, h=170, fill="#f4f8fd", stroke="#cccccc", font=11, align="left", valign="top")
    d.box(30 + half + 40, 306, half, comp, h=170, fill="#fff8ee", stroke="#cccccc", font=11, align="left", valign="top")
    d.box(30, 510, 2320, "**fingerprint**: element name, attributes except `layout-mark` (sorted), children, non-blank text. Two implementations (`layout::fingerprint` on pugixml, `fingerprint` on `node_t`) must produce the same text.\n"
          "**the table** lives in `any_transform_states_` for the whole run and is cleared and refilled by every print of XML; it matters between the print in `xml2saxon` and the read in `xml2cpp`.", h=80,
          fill="#fbfbfb", stroke="#cccccc", font=12, align="left", valign="top")
    save(d, "40_dev_xml_roundtrip")


# ---------------------------------------------------------------- 41 places
def places():
    d = Diagram("41_dev_places", 2200, 800)
    d.text(30, 16, 1500, "The places of the filesystem decorator", font=20, bold=True)
    d.text(30, 50, 2000, "Every file the translator writes goes through a place, except the summary, `taskflow.dot`, and absolute paths from a user xslt.", font=12, color="#555555")
    heads = [("place", 380), ("folder", 300), ("read", 120), ("write", 440), ("remove", 440)]
    x = 30
    for t, w in heads:
        d.box(x, 100, w - 4, t, h=30, fill="#f2f2f2", stroke="#cccccc", font=12, bold=True)
        x += w
    rows = [
        ("input/output .gal  (normal mode)", "`input-gal-dir` (= output)", "cached", "**delayed** until `do_jobs_at_end`; only if the text changed; once", "files not rewritten: removed at the end", GREEN),
        ("input .gal  (separate)", "`input-gal-dir`", "not cached", "–", "–", GREEN),
        ("output .gal  (separate)", "`output-gal-dir`", "–", "at once; once", "every .gal removed at the **start**", GREEN),
        ("intermediate xml", "`intermediate-xml-dir`  (.xml, .html)", "not cached", "at once; once", "everything removed at the **start**", ORANGE),
        ("store of `other-files`  (one per entry)", "`store-dir`  (the `extentions` of the entry)", "not cached", "at once; only if the text changed; once", "not rewritten: removed at the end, unless `delete-if-not-rewrited` is false", ORANGE),
    ]
    y = 136
    for name, folder, rd, wr, rm, (f, s) in rows:
        x = 30
        for t, w in zip((name, folder, rd, wr, rm), [w for _, w in heads]):
            d.box(x, y, w - 4, t, h=64, fill=f if x == 30 else "#ffffff", stroke=s if x == 30 else "#cfcfcf", font=11, align="left")
            x += w
        y += 70
    d.box(30, y + 20, 2120,
          "**once**: writing the same path twice in one run is an error · **roots may not be nested** (`add_place`) · **\"at the end\"** runs in `do_jobs_at_end`, only after a run that succeeded · the log folder is opened by Logme and is not a place\n"
          "**routing** (`process_result`): the principal XML → intermediate; `cpp2gal` output → the output .gal place; `@@alias@@relative@@` → the store with that alias; a relative path → intermediate; an absolute path → written directly",
          h=100, fill="#fbfbfb", stroke="#cccccc", font=12, align="left", valign="top")
    save(d, "41_dev_places")


# ---------------------------------------------------------------- 42 test layout
def tests_flow():
    d = Diagram("42_dev_tests", 2200, 720)
    d.text(30, 16, 1500, "How a product test runs", font=20, bold=True)
    bx = [
        ("**configure**\nCMake copies `galimatron/tests/test_data` to `<build>/bin/galimatron_test_data` (deleting the old copy), copies the shared `gal.cfg`, `log.cfg`, `xslt/config.xml` into the cases, and on Windows the `expected-xml-windows` files over `expected-xml`", BLUE, 560),
        ("**the test**\n`translate_production(case_root)` runs `runtime::translate` with the case's `gal.cfg` and `log.cfg`, `is_testing_mode = true`", GREEN, 420),
        ("**the run writes**\n`actual_gal/`, `actual_xml/`, `intermediate/`, `actual_summary/`, `actual_log/`: inside the build copy", ORANGE, 420),
        ("**the check**\n`compare_directories` (`git diff --no-index`): `actual_gal` against `expected-gal`, `actual_xml` against `expected-xml`. For a failing case: `print_leaf_exception` with a handler", YELLOW, 560),
    ]
    x = 30
    ids = []
    for t, (f, s), w in bx:
        ids.append(d.box(x, 90, w, t, h=190, fill=f, stroke=s, font=11, align="left", valign="top"))
        x += w + 40
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b, straight=True)
    axes = [("product", "full integration: gal.cfg, log.cfg, `translate_production`"), ("translator_slice", "chosen built-in steps: `translate_slice`"),
            ("parser", "the grammar and the version rule"), ("component", "one helper"), ("process", "the crash handler in a child process")]
    d.text(30, 320, 800, "**test axes**  (`test_axes::mark(...)` in the suite description)", font=13)
    for i, (a, t) in enumerate(axes):
        d.box(30, 354 + i * 44, 220, "`%s`" % a, h=36, fill="#f2f2f2", stroke="#cccccc", font=11, bold=True, align="left")
        d.box(254, 354 + i * 44, 700, t, h=36, fill="#ffffff", stroke="#cfcfcf", font=11, align="left")
    d.box(1020, 320, 1150, "**the rules**\n• product and slice tests never touch file bytes: only `compare_directories` and exception checks\n• oracles hold no absolute path: a path is relative to the `gal.cfg` folder with `/` (`report_path`, `committed-report`)\n"
          "• `// good` and `// bad` mark the line of an automated `.gal` fixture\n• change a file that has a Windows twin → change both\n• names must match in case (Linux)", h=190, fill="#fbfbfb", stroke="#cccccc", font=12, align="left", valign="top")
    d.box(30, 600, 2140, "`run_tests` = `global_tests` → `galimatron_tests` → `uuid_protocol_tests`, in one cmake process, working directory `bin/`; on CI with `--abort-after=1`.", h=44, fill=GREEN[0], stroke=GREEN[1], font=12, align="left")
    save(d, "42_dev_tests")


# ---------------------------------------------------------------- 43 build
def build_flow():
    d = Diagram("43_dev_build", 2200, 780)
    d.text(30, 16, 1500, "From source to installer", font=20, bold=True)
    bx = [
        ("**configure**\n`cmake -S . -B build -G Ninja`\n`dependencies.cmake`: FetchContent for Boost, logme, ANTLR (+ jar), range-v3, pugixml, nlohmann_json, inja, alpaca, doctest, magic_enum, Taskflow, leaf_spy, multi_index_lookup; SaxonC-HE from `externals/Saxon`\npatches: ANTLR, doctest, inja, Saxon cmake", BLUE, 760),
        ("**build**\n`global_pch_library` owns the PCH\nANTLR generates the lexer and parser\nlibraries: global → common → translator → runtime → executable\ntests and examples", GREEN, 560),
        ("**test**\n`run_tests`\n(three executables, `bin/` as the working directory)", YELLOW, 380),
        ("**package**\n`package` target\nWindows: ZIP, NSIS\nLinux: TGZ, DEB, RPM", ORANGE, 360),
    ]
    x = 30
    ids = []
    for t, (f, s), w in bx:
        ids.append(d.box(x, 90, w, t, h=210, fill=f, stroke=s, font=11, align="left", valign="top"))
        x += w + 40
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b, straight=True)
    d.box(30, 340, 1060, "**what the installer holds**\n`bin/`: `galimatron`, `saxonc-he`, `saxonc-core-he` (and the MSVC runtime on Windows)\n`share/galimatron/xslt/gal-functions.xsl` · `share/galimatron/catalog.xml` (maps the GitHub URL of `gal-functions.xsl` to that file)\n`share/doc/galimatron/`: `LICENSE`, `THIRD_PARTY_NOTICES.md`, `third_party_licenses/`", h=130, fill="#fbfbfb", stroke="#cccccc", font=12, align="left", valign="top")
    d.box(1130, 340, 1040, "**CI** (`.github/workflows`)\nWindows: MSVC Debug, MSVC Release (+ package)\nLinux: GCC Debug, GCC Release (+ package), Clang Debug, Clang Release\neach: configure → build → `run_tests` → (package) → upload artifacts", h=130, fill="#fbfbfb", stroke="#cccccc", font=12, align="left", valign="top")
    d.box(30, 500, 2140, "**release**: `scripts/release.py` copies this repository into the checkout of the public one, minus `.cursor/rules`, `.vscode`, the `TODO*.txt` files, the benchmark's outputs and the build products.\n"
          "**mind**: the Saxon core binary is Release-only (a Debug build uses it); the CRT is dynamic; after you add or remove a source file, run CMake again.", h=84, fill=YELLOW[0], stroke=YELLOW[1], font=12, align="left", valign="top")
    save(d, "43_dev_build")


if __name__ == "__main__":
    sequence()
    validate_dag()
    wizard_flow()
    compile_flow()
    xml_roundtrip()
    places()
    tests_flow()
    build_flow()
