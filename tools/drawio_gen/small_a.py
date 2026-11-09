"""The smaller developer diagrams, part A: layers, state model, seal, errors, run construction."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from drawgen import *

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "drawio"))


def save(d, name):
    d.save(os.path.join(OUT, name + ".drawio"))
    print("saved", name, len(d.cells))


def rhombus(d, x, y, w, h, text, fill="#fff2cc", stroke="#d6b656", font=11):
    return d.box(x, y, w, text, h=h, fill=fill, stroke=stroke, font=font, rounded=False,
                 extra="shape=rhombus;perimeter=rhombusPerimeter", wrap=True)


# ---------------------------------------------------------------- 30 layers
def layers():
    d = Diagram("30_dev_layers", 1500, 860)
    d.text(30, 16, 900, "The libraries of Galimatron", font=20, bold=True)
    d.text(30, 50, 1300, "An arrow: links PUBLIC to. The dependency runs one way, down. Dashed boxes are external libraries.", font=12, color="#555555")
    bw = 380
    exe = d.box(420, 100, bw, "**galimatron_executable**\n`main.cpp`  →  `galimatron`", fill=GREEN[0], stroke=GREEN[1], font=12, h=56)
    exl = d.box(60, 100, 340, "**galimatron_executable_library**\nthe command line (Boost.Program_options)", fill=BLUE[0], stroke=BLUE[1], font=12, h=60)
    rt = d.box(420, 220, bw, "**galimatron_runtime_library**\nconfig, filesystem decorator, summary, crash handler, error printing, `translate`", fill=BLUE[0], stroke=BLUE[1], font=12, h=76)
    tr = d.box(420, 360, bw, "**galimatron_translator_library**\nparser, state, wizard, validator, compiler, XML, seal, the sequence of steps", fill=BLUE[0], stroke=BLUE[1], font=12, h=76)
    cm = d.box(420, 500, bw, "**galimatron_common_library**\nexception vocabulary, path report", fill=BLUE[0], stroke=BLUE[1], font=12, h=60)
    gfs = d.box(60, 620, 340, "**global_filesystem_library**\nthe filesystem as a struct of functions", fill=TEAL[0], stroke=TEAL[1], font=12, h=60)
    gcm = d.box(420, 620, bw, "**global_common_library**\ntype aliases, logging helpers, scope guard, private memory", fill=TEAL[0], stroke=TEAL[1], font=12, h=60)
    pch = d.box(420, 750, bw, "**global_pch_library**\nowns the precompiled header (`pch.hpp`)", fill=TEAL[0], stroke=TEAL[1], font=12, h=60)
    d.edge(exe, exl, straight=True)
    d.edge(exe, rt, straight=True)
    d.edge(rt, tr, straight=True)
    d.edge(tr, cm, straight=True)
    d.edge(exl, cm, exit_xy=(0.5, 1), entry_xy=(0, 0.5), points=[(230, 530)])
    d.edge(rt, gfs, exit_xy=(0, 0.5), entry_xy=(0, 0.5), points=[(30, 258), (30, 650)])
    d.edge(cm, gcm, straight=True)
    d.edge(gfs, gcm, straight=True)
    d.edge(gcm, pch, straight=True)
    # externals
    ex = 900
    d.text(ex, 100, 560, "**External libraries**", font=13)
    ext = [
        (ex, 130, "SaxonC-HE · Taskflow · inja  (private to the translator)", tr),
        (ex, 190, "ANTLR runtime · pugixml · range-v3 · Boost.Graph, Hash2, ...  (public)", tr),
        (ex, 250, "leaf_spy  (translator and runtime)", rt),
        (ex, 310, "multi_index_lookup · base64 · magic_enum  (global_common_library)", gcm),
        (ex, 370, "Boost (algorithm, graph, leaf, multi_index, uuid, asio) · Logme · nlohmann_json · pugixml · range-v3  (the PCH makes these visible everywhere)", pch),
        (ex, 450, "Boost.Program_options", exl),
        (ex, 500, "Boost.Units · Boost.Process (tests)", rt),
    ]
    for x, y, t, tgt in ext:
        h = 44 if len(t) < 90 else 62
        b = d.box(x, y, 540, t, h=h, fill="#f7f7f7", stroke="#aaaaaa", font=11, dashed=True, align="left")
    d.text(900, 580, 560,
           "`multi_index_lookup` and `leaf_spy` are separate repositories, fetched at configure time.\n"
           "Tests are separate targets: `global_tests`, `galimatron_tests` (and `galimatron_crash_child`), `uuid_protocol_tests`.",
           font=11, color="#555555")
    save(d, "30_dev_layers")


# ---------------------------------------------------------------- 32 state model
def state_model():
    d = Diagram("32_dev_state_model", 1900, 900)
    d.text(30, 16, 1200, "The state of the translator", font=20, bold=True)
    d.text(30, 50, 1700, "The graph holds the truth. The containers are indexes over it. The compiled part is derived and can be dropped at any time.", font=12, color="#555555")
    # writers
    wr = d.box(30, 120, 300, "**who adds vertices**\nthrough `builder_t`", fill=BLUE[0], stroke=BLUE[1], font=13, h=60)
    ws = ["gal2cpp  (the parser listener)", "xml2cpp_saxon  (an xslt's result)", "cpp2cpp_wizard  (a command)", "xslt_seal  (restore and reassign)"]
    wb = []
    for i, t in enumerate(ws):
        wb.append(d.box(30, 210 + i * 56, 300, t, h=44, fill="#f2f7fc", stroke=BLUE[1], font=11))
    bld = d.box(390, 210, 280, "**builder_t**\n`create_*`, `clone_under`, `clone_from`, `apply_aggregate_version_delete`.\nEach `create_*` adds the vertex and registers it in the containers", h=130,
                fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    for b in wb:
        d.edge(b, bld, color="#777777", width=1)
    # language part
    lp_x, lp_y = 730, 110
    d.frame(lp_x, lp_y, 620, 700, "language_part_t   (`state/holder/holder.hpp`)", fill="#fbfdf9", stroke="#82b366")
    g = d.box(lp_x + 20, lp_y + 50, 580, "**graph_t**  `boost::adjacency_list<listS, containerS, bidirectionalS, vertex_t>`\n"
              "vertices live in a `multi_index_container`: random access, by `entity_type`, by `(vd_parent, entity_type)`\n"
              "`vertex_t {entity_type, entity, location, vd_parent, vd_self, user_comments, user_formatting}`\n"
              "edges parent → child; **vertices are never removed**, only detached", h=118, fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    cont = [
        ("aggregate_container", "name, vd, is_root, chunk, index, `first_live`, **`last_hashed`**"),
        ("version_container", "(aggregate, version): declaration + definition + status, hash, comment, `definition_payload`; parked bodies"),
        ("version_statement_container", "the direct statements of a body: entity, name, `index_in_version`"),
        ("ordering_link_container", "which aggregates a root ordering names"),
        ("wizard_statements_", "the descriptors of wizard statements"),
        ("string_delimiters_", "how strings were quoted; index 0 is a plain \""),
    ]
    cy = lp_y + 190
    for n, t in cont:
        d.box(lp_x + 20, cy, 230, "`%s`" % n, h=56, fill="#ffffff", stroke="#82b366", font=11, align="left")
        d.box(lp_x + 254, cy, 346, t, h=56, fill="#f4faf1", stroke="#cfe3c8", font=10, align="left")
        cy += 64
    d.text(lp_x + 20, cy + 6, 580, "The containers are kept in sync by the builder and by explicit calls: `refresh_live_and_hashed`, `note_version_child`, `forget_version_child`, `rebind_version_definitions`, `refresh_version_records`.", font=10, color="#555555")
    d.edge(bld, g, straight=True)
    # compiled part
    cp_x = 1420
    d.frame(cp_x, lp_y, 450, 700, "compiled_part_t", fill="#fffaf2", stroke="#d79b00")
    comp = [
        ("tag_container", "per version: the effective tags {vd_version, vd_tag, name, body}"),
        ("tag_labels / static_label / tag_name", "the labels a tag resolved to, and the name of an unnamed tag"),
        ("ordering_container, ordering_rank_container", "orderings per version, and the **position** of each aggregate"),
        ("merged_ (per aggregate)", "the merged timeline of statements, and version → definition"),
        ("rendered_strings_", "rendered `_te` text per (version, string)"),
        ("value_before_", "the value just before each statement (history)"),
    ]
    cy = lp_y + 50
    for n, t in comp:
        d.box(cp_x + 16, cy, 418, "**%s**\n%s" % (n, t), h=76, fill="#ffffff", stroke="#d79b00", font=10, align="left", valign="top")
        cy += 84
    d.text(cp_x + 16, cy + 4, 418, "It refers to the graph by descriptors only: do not use it with another graph.", font=10, color="#555555")
    d.line(1352, 430, 1418, 430, color="#555555", width=2)
    d.text(1352, 436, 66, "cpp2post_cpp", font=10, align="center")
    d.frame(30, 470, 640, 330, "who reads", fill="#ffffff", stroke="#bdbdbd")
    readers = ["cpp2gal  → .gal text (stored source text wins)", "cpp2xml  → the language or the compiled XML",
               "cpp2cpp_validate  → checks, and a compile", "cpp2post_cpp  → `compiled_part_t`", "history  → the `<history>` element",
               "xslt_seal  → compares before and after"]
    for i, t in enumerate(readers):
        d.box(50, 520 + i * 44, 600, t, h=36, fill="#f7f7f7", stroke="#cccccc", font=11, align="left")
    save(d, "32_dev_state_model")


# ---------------------------------------------------------------- 33 seal
def seal():
    d = Diagram("33_dev_seal", 1600, 1180)
    d.text(30, 16, 1200, "The seal: reassign_sealed_edits(before, after)", font=20, bold=True)
    d.text(30, 50, 1500, "Runs in `cpp2cpp_after_xslt`, only when a language xslt is enabled. Left: the ways out that return `after` as it is.", font=12, color="#555555")
    x, w = 520, 560
    y = 110
    def step(text, fill=BLUE[0], stroke=BLUE[1], h=None):
        nonlocal y
        b = d.box(x, y, w, text, fill=fill, stroke=stroke, font=11, h=h, align="left")
        y += d.last_h + 36
        return b
    def dec(text):
        nonlocal y
        b = rhombus(d, x + 40, y, w - 80, 76, text)
        y += 76 + 34
        return b
    s0 = dec("a root on both sides, and a hashed version (`last_hashed`)?")
    s1 = step("`refresh_version_records()` on both: rebuild every `definition_payload`")
    s2 = step("`reject_sealed_shape`: an aggregate of `before` is missing in `after`, or a version was inserted into the sealed range", RED[0], RED[1])
    s3 = dec("`sealed_history_differs`: declaration, hash, comment, status or payload of a sealed version?")
    s4 = step("`effective_edits`: compile both graphs, diff the **effective tags** of the last sealed version: `REASSIGN` or `DELETE_TAG` per aggregate")
    s5 = dec("only `REASSIGN` of tags the wizard copied (`created_by_wizard`, dynamic label)?")
    s6 = step("`restore_sealed_history`: every sealed version of `after` becomes a clone of `before` (declaration fields, presentation, children)")
    s7 = dec("any effective edits left?")
    s8 = step("`destination_version`: the first open version after `last_sealed`, or `open_next_version` makes one for every live aggregate")
    s9 = step("`write_edits`: clone each changed tag into it (`created_by_wizard`), or write `delete name;`. A tag already named there is left alone", GREEN[0], GREEN[1])
    for a, b in [(s0, s1), (s1, s2), (s2, s3), (s3, s4), (s4, s5), (s5, s6), (s6, s7), (s7, s8), (s8, s9)]:
        d.edge(a, b, straight=True, text="no" if a in (s0, s3, s5) and False else "")
    # exits
    ret = d.box(60, 280, 330, "**return `after`**\nnothing sealed, or nothing changed", fill=GREEN[0], stroke=GREEN[1], font=11, h=56)
    d.edge(s0, ret, text="no", exit_xy=(0, 0.5), entry_xy=(1, 0.5), straight=False)
    d.edge(s3, ret, text="no", exit_xy=(0, 0.5), entry_xy=(1, 0.5))
    fin = d.box(60, 560, 330, "**return `after`** after `write_version_hash(after, last_sealed)`\nthe xslt only finished wizard copies: the hash is refreshed", fill=GREEN[0], stroke=GREEN[1], font=11, h=78)
    d.edge(s5, fin, text="yes", exit_xy=(0, 0.5), entry_xy=(1, 0.5))
    ret2 = d.box(60, 900, 330, "**return `after`**\nonly formatting changed: the sealed text is back, the log says `restored the sealed text`", fill=GREEN[0], stroke=GREEN[1], font=11, h=78)
    d.edge(s7, ret2, text="no", exit_xy=(0, 0.5), entry_xy=(1, 0.5))
    d.box(1160, 320, 400, "After the seal, `cpp2cpp_after_xslt` runs `validate_language` again.\n\n**A user xslt never rewrites a hash.** The language is checked as it is. `force` does not apply in this run.", fill=YELLOW[0], stroke=YELLOW[1], font=11, align="left", valign="top")
    d.box(1160, 520, 400, "What the user sees: an xslt may \"edit\" an old version, and the edit shows up in the **next open version**, while the old text stays as it was.", fill="#f7f7f7", stroke="#cccccc", font=11, align="left", valign="top")
    d.box(1160, 660, 400, "Cost: the seal compiles **both** graphs, which is the most expensive part of the step on a large project.", fill="#f7f7f7", stroke="#cccccc", font=11, align="left", valign="top")
    save(d, "33_dev_seal")


# ---------------------------------------------------------------- 34 errors
def errors():
    d = Diagram("34_dev_errors", 1700, 760)
    d.text(30, 16, 1200, "The path of an error", font=20, bold=True)
    thr = d.box(30, 100, 400, "**throw site**\n`leaf::throw_exception(domain, subdomain, e_what_info, [code], ...)`\nguards: `augment_domain`, `augment_path`, `augment_aggregate`, `augment_version`, `augment_where`", h=120, fill=BLUE[0], stroke=BLUE[1], font=11, align="left", valign="top")
    main = d.box(520, 90, 420, "**on the main thread**\nthe exception travels to the nearest `try_catch`", h=70, fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    wk = d.box(520, 190, 420, "**on a Taskflow worker** (no LEAF context)\n`capture_or_rethrow` → `leaf::try_capture_all` → throws `captured_leaf_exception`;\n`subflow.join()` / `future.get()` rethrows it on the caller", h=110, fill=YELLOW[0], stroke=YELLOW[1], font=11, align="left", valign="top")
    d.edge(thr, main); d.edge(thr, wk)
    inner = d.box(1040, 140, 600, "**inner catch**  `translate_by_config`\n`runtime::try_catch`, `is_throw_out = true`\n`leaf_spy` loads every domain, subdomain, enum and payload and prints `Exception details:`\n`notify_printed` → the summary `<error>`", h=130, fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    d.edge(main, inner); d.edge(wk, inner)
    outer = d.box(1040, 330, 600, "**outer catch**  `translate_impl_t::translate`\nthe same wrapper: the text is logged with `fLogmeE`; the result is 1\n`is_throw_out = is_testing_mode`", h=100, fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
    d.edge(inner, outer, text="rethrow")
    d.box(1040, 470, 600, "**after the catches**: the scope guard writes `galimatron_summary.xml` (`status=\"fail\"`), `flush_log()`, exit code 1. `do_jobs_at_end` did not run.", h=70, fill=RED[0], stroke=RED[1], font=11, align="left", valign="top")
    d.box(520, 340, 460, "**in a test**\n`print_leaf_exception(func, handlers...)` wraps the call in `runtime::try_catch`; the handler checks `domain`, `subdomain`, `e_what_info`, path, aggregate, version", h=110, fill="#f2f2f2", stroke="#cccccc", font=11, align="left", valign="top")
    d.box(30, 260, 440, "**not LEAF**\n`antlr4::ParseCancellationException` (syntax; printed by a `dynamic_cast`)\n`std::runtime_error` (`apply_log_config`, `merge_paths`)\nBoth print `NO DOMAIN-SPECIFIC EXCEPTION CATEGORY MATCHED`", h=120, fill=RED[0], stroke=RED[1], font=11, align="left", valign="top")
    d.box(30, 500, 940, "**the path in the text** is spelled from copies in `e_path_info` (`committed_report`, `config_dir`): the run's path report may be gone when the text is built. Every path in a message goes through `report_path`.", h=64, fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
    save(d, "34_dev_errors")


# ---------------------------------------------------------------- 35 run construction
def run_construction():
    d = Diagram("35_dev_run_construction", 2000, 760)
    d.text(30, 16, 1500, "How `translate_by_config` builds a run", font=20, bold=True)
    steps = [
        ("**1 filesystem**\n`physically::make_filesystem()`\n`filesystem_decorator_t fsd`", BLUE),
        ("**2 mode**\n`input-gal-dir == output-gal-dir`?\nnormal: one .gal place\nseparate: two", BLUE),
        ("**3 places**\n.gal, intermediate xml,\none per `other-files` store\n(alias unique per transform)", GREEN),
        ("**4 summary**\nbuilder + scope guard:\nalways writes\n`galimatron_summary.xml`", BLUE),
        ("**5 process_result**\nthe callback for each step:\nroutes xml and files to places,\nadds a summary entry", BLUE),
        ("**6 the job**\ninner `try_catch`", YELLOW),
    ]
    xs = 30
    ids = []
    for t, (f, s) in steps:
        ids.append(d.box(xs, 90, 290, t, h=140, fill=f, stroke=s, font=11, align="left", valign="top"))
        xs += 320
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b, straight=True)
    job = [
        "`fsd.do_jobs_at_begin()`\ncreate folders, delete the files of `at_begin` places",
        "`crash::arm_summary(path)`",
        "`add_directory_parameters`\nsix `xsl:param`s to each enabled user transform (on a copy)",
        "`translator::translate({...})`\ncallbacks: notify result, taskflow graph, state memory",
        "`summary.set_result(true)`",
        "`fsd.do_jobs_at_end()`\nwrite delayed .gal, remove stale files",
    ]
    jx = 30
    jids = []
    for i, t in enumerate(job):
        jids.append(d.box(jx, 330, 290, "**6.%d**  %s" % (i + 1, t), h=120, fill=YELLOW[0] if i != 3 else BLUE[0], stroke=YELLOW[1] if i != 3 else BLUE[1], font=11, align="left", valign="top"))
        jx += 320
    for a, b in zip(jids, jids[1:]):
        d.edge(a, b, straight=True)
    d.edge(ids[-1], jids[0], exit_xy=(0.5, 1), entry_xy=(0.5, 0))
    d.box(30, 520, 1900, "**on an error** step 6.5 and 6.6 do not run. The inner catch copies the error text into the summary, the guard of step 4 writes the summary with `status=\"fail\"`, the outer catch logs the text, the exit code is 1.\n"
          "**on success** the summary says `success`, the delayed `.gal` files are written (only if their text changed), and stale files of `delete-if-not-rewrited` stores are removed.", h=84, fill=RED[0], stroke=RED[1], font=12, align="left", valign="top")
    save(d, "35_dev_run_construction")


if __name__ == "__main__":
    layers()
    state_model()
    seal()
    errors()
    run_construction()
