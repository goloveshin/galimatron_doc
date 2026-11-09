import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from drawgen import *

W = 5140
LABEL_X, LABEL_W = 40, 236
COL0, PITCH, COLW = 316, 316, 300
NCOL = 15


def cx(i):
    return COL0 + PITCH * i


d = Diagram("31_dev_pipeline_map", W, 6200)

# ------------------------------------------------------------------ title
d.text(40, 24, 1800, "Galimatron: one run, step by step", font=28, bold=True)
d.text(40, 66, 3200,
       "What `galimatron --gal-config-file gal.cfg --log-config-file log.cfg` does, for a project that has a wizard command, "
       "a language xslt and a post xslt. Read it top to bottom: the runtime wraps the run, the translator runs fifteen steps "
       "one after another, and the panels below open the steps that hide the most.",
       font=13, color="#555555")

# legend
lx = 40
ly = 128
legend = [("built-in step", BLUE), ("your xslt", YELLOW), ("state in memory", GREEN), ("file on disk", ORANGE),
          ("saxon", PURPLE), ("failure", RED)]
for name, (f, s) in legend:
    d.box(lx, ly, 150, name, h=26, fill=f, stroke=s, font=11)
    lx += 166
d.text(lx + 10, ly + 3, 1500,
       "Source code names are in `code font`. Directories are relative to `galimatron/translator_library/` or `galimatron/runtime_library/`.",
       font=11, color="#666666")

# ------------------------------------------------------------------ S1 runtime prelude
y = 190
frame1_ix = len(d.cells)
bx = 70
by = y + 52
bw = 800
gap = 52
pre = [
    ("**command line**",
     "`galimatron --gal-config-file gal.cfg --log-config-file log.cfg`\n"
     "`executable/main.cpp` parses the arguments (`executable_library/command_line.cpp`, Boost.Program_options). "
     "`--help` prints and exits.",
     GREY),
    ("**rt::translate(args)**",
     "`runtime_library/translate/detail/translate.cpp`\n"
     "• `crash::install()`: SEH filter or signals\n"
     "• log to the console until log.cfg is read\n"
     "• `apply_log_config`, then `crash::arm_log()`: name a crash log beside the log\n"
     "• read gal.cfg: three passes, paths made absolute\n"
     "• set the path report (`committed-report`)\n"
     "• **outer** `leaf_spy::try_catch`: prints and logs every error",
     BLUE),
    ("**translate_by_config**",
     "`translate/detail/translate_by_config.cpp`\n"
     "• `filesystem_decorator_t` with **places**: the .gal place(s), the intermediate place, one place per `other-files` store (panel I)\n"
     "• `summary builder` and a scope guard that always writes `galimatron_summary.xml`\n"
     "• `process_result`: routes the output of every step to a place",
     BLUE),
    ("**start of the run**",
     "• `fsd.do_jobs_at_begin()`: create folders, delete the files of places marked `at_begin` (the intermediate folder; the output .gal in separate mode)\n"
     "• `crash::arm_summary()`\n"
     "• add six directory `xsl:param`s to every enabled user transform\n"
     "• read the `.gal` files lazily from the input place, read `gal.version`",
     BLUE),
    ("**translator::translate(config)**",
     "`translator/detail/translate.cpp`\n"
     "• `prepare_transforms()`: builds the list of steps (panel A)\n"
     "• one Taskflow task per step, chained with `precede`: strictly one after another\n"
     "• one static `tf::Executor` for the process (Saxon attaches a Graal thread to each worker)\n"
     "• `executor().run(taskflow).get()`",
     BLUE),
]
ids = []
pre_w = 960
pre_gap = 50
bx = 70
pre_h = max(d.height_for(t + "\n" + body, pre_w, 13) for t, body, _ in pre)
for t, body, (f, s) in pre:
    cid = d.box(bx, by, pre_w, t + "\n" + body, h=pre_h, fill=f, stroke=s, font=13, align="left", valign="top")
    ids.append(cid)
    bx += pre_w + pre_gap
for a, b in zip(ids, ids[1:]):
    d.edge(a, b, straight=True)
frame1_h = 52 + pre_h + 30
d.frame(40, y, W - 80, frame1_h, "1  The runtime: before the translator  (galimatron/executable, executable_library, runtime_library)", fill="#fcfcfb")
_c = d.cells.pop(); d.cells.insert(frame1_ix, _c)

# ------------------------------------------------------------------ S2 the matrix
y = y + frame1_h + 50
m_top = y
# the run goes from the last runtime box into the matrix
_last_cx = 70 + 4 * (pre_w + pre_gap) + pre_w // 2
d.line(_last_cx, y - 50, _last_cx, y, color="#333333", width=2.5)
steps = [
    # (index text, name, user?, in, out, code, does, files, failure)
    dict(name="gal2cpp", user=False, inn="GaL", out="CPP", dom="L",
         code="`transforms/gal2cpp/gal2cpp.cpp`",
         does="• one ANTLR parse per `.gal` file, one `chunk` vertex per file\n"
              "• `listener_t` walks the tree, `builder_t` adds vertices and registers them in the holder\n"
              "• keeps source text and comments on the vertices\n"
              "• skipped when `language_state_` is already set",
         fail="syntax: `ParseCancellationException`, with a friendlier text from `explains.cpp`; LEAF `gal2cpp` for a misplaced wizard command"),
    dict(name="cpp2cpp_validate", user=False, inn="CPP", out="CPP", dom="L",
         code="`transforms/cpp2cpp_validate/cpp2cpp_validate.cpp`",
         does="• a Taskflow **subflow** of twelve checks: shape of versions, anchors, hashes (panel B)\n"
              "• then `compile_for_validation` = `cpp2post_cpp::translate`\n"
              "• checks the file as it is. The wizard command is checked later, by the wizard step\n"
              "• prints lang-parsed.xml",
         fail="`validation_error_code_et` raised by `fail()` inside `capture_or_rethrow` (a worker thread has no LEAF context); compile errors: `throw_compiler`"),
    dict(name="cpp2cpp_wizard", user=False, inn="CPP", out="CPP", dom="L", cond="only if a wizard statement exists",
         code="`transforms/cpp2cpp_wizard/detail/command.cpp`",
         does="• exactly one statement: `is_wizard_command_single`\n"
              "• `apply_one(type)` or the batch loop with `refresh_checks()` (panel C)\n"
              "• each command calls `may_execute_wizard_command()` first\n"
              "• at the end the command text becomes `//` lines at the top of its chunk",
         fail="`WIZARD_*` codes from `cpp2cpp_validate_t`, raised the same way"),
    dict(name="cpp2cpp_before_xslt", user=False, inn="CPP", out="CPP", dom="L", cond="language xslt",
         code="`translator/detail/transforms/cpp2cpp_before_xslt.cpp`",
         does="• `language_before_xslt_ = language_state_`: one more pointer to the same graph\n"
              "• the seal will compare the xslt's result with it",
         fail="none"),
    dict(name="cpp2xml", user=False, inn="CPP", out="XML", dom="L", cond="language xslt",
         code="`transforms/cpp2xml/detail/translate.cpp`",
         does="• the job is empty: `execute_transform` prints the principal XML\n"
              "• `document_cpp2xml(false)`: `ensure_compiled`, the **language** XML, `<history>`, layout marks (panel E)\n"
              "• the language XML keeps labels, `_te` templates and wizard marks",
         fail="LEAF `cpp2xml`: a wizard statement is not an xml node"),
    dict(name="xml2saxon", user=False, inn="XML", out="SAXON", dom="L", cond="language xslt",
         code="`transforms/xml2xml/detail/xml2xml_impl.cpp`",
         does="• a new Saxon session: processor, catalog from `share/galimatron/`\n"
              "• prints the language XML again and parses it into an `XdmValue`\n"
              "• production resets `language_state_`: the graph is now held by `language_before_xslt_`",
         fail="none"),
    dict(name="your language xslt", user=True, inn="SAXON", out="SAXON", dom="L", cond="language xslt",
         code="`transforms/xml2xml/detail/xml2xml_impl.cpp`",
         does="• parameters: those of `gal.cfg` plus the six directory params\n"
              "• `compileFromString`, `applyTemplatesReturningValue`: the result replaces the document, so the next xslt reads it\n"
              "• `xsl:result-document` outputs are captured into `produced_files`\n"
              "• one step per enabled transform, in config order",
         fail="`SaxonApiException` → `throw_translator`, with the xslt path, line and message"),
    dict(name="xml2cpp", user=False, inn="SAXON", out="CPP", dom="L", cond="language xslt",
         code="`transforms/xml2cpp_saxon/detail/xml2cpp_saxon.cpp`",
         does="• `node_t` wraps `XdmNode*`; `builder_t` builds a **new** `language_part_t`\n"
              "• `restore_layout`: stored source text returns only if the node's fingerprint is unchanged\n"
              "• `compiled_state_` is reset, the Saxon session is reset",
         fail="LEAF `xml2cpp`: unexpected xml node, no index, no name, unknown mode"),
    dict(name="cpp2cpp_after_xslt", user=False, inn="CPP", out="CPP", dom="L", cond="language xslt",
         code="`translator/detail/xslt_seal.cpp`",
         does="• `reassign_sealed_edits(before, after)`: closed versions stay closed (panel G)\n"
              "• then `validate_language` again. A user xslt never rewrites a hash\n"
              "• `language_before_xslt_` is released",
         fail="seal errors (removed aggregate, inserted version) and `validation_error_code_et`"),
    dict(name="cpp2gal", user=False, inn="CPP", out="GaL", dom="L",
         code="`transforms/cpp2gal/detail/cpp2gal_impl.cpp`",
         does="• `cpp2gal_t` prints one text per chunk\n"
              "• stored source text wins; wizard-made statements are generated (100 columns, 4 spaces)\n"
              "• the texts go to the .gal place (panels F and I)",
         fail="LEAF `cpp2gal`: unexpected entity, chunk has no path"),
    dict(name="gal2cpp  (skipped)", user=False, inn="GaL", out="CPP", dom="L", skipped=True,
         code="`translator/detail/transforms/gal2cpp.cpp`",
         does="• inserted by the sequence builder as the way from GaL back to CPP, so that the post part can start\n"
              "• `is_skipping`: `language_state_` is set, so it only logs `skip transformation`\n"
              "• in the summary: status SKIPPED",
         fail="none"),
    dict(name="cpp2post_cpp", user=False, inn="CPP", out="CPP", dom="T",
         code="`transforms/cpp2post_cpp/detail/translate.cpp`",
         does="• `ensure_compiled()`: build `compiled_part_t` unless it is cached\n"
              "• merge versions, compile tags, names, labels, templates, ranks (panel D)\n"
              "• skipped when there is no root aggregate",
         fail="`throw_compiler`: label and naming errors, bad ordering, deleting a label; `template_engine`: a template failed"),
    dict(name="post_cpp2post_xml", user=False, inn="CPP", out="XML", dom="P",
         code="`transforms/cpp2xml/detail/translate.cpp`",
         does="• the job is empty: `execute_transform` prints the **compiled** XML, `document_cpp2xml(true)`\n"
              "• values carry label attributes, templates are rendered, `<orderings>` carry ranks, `<history>` is included\n"
              "• this file exists on every run, with or without xslt",
         fail="as cpp2xml"),
    dict(name="post_xml2saxon", user=False, inn="XML", out="SAXON", dom="P", cond="post xslt",
         code="`transforms/xml2xml/detail/xml2xml_impl.cpp`",
         does="• a new Saxon session; prints the compiled XML and parses it\n"
              "• inserted only before a post xslt\n"
              "• skipped when there is no compiled state",
         fail="none"),
    dict(name="your post xslt", user=True, inn="SAXON", out="SAXON", dom="P", cond="post xslt",
         code="`transforms/xml2xml/detail/xml2xml_impl.cpp`",
         does="• the same `xml2xml::apply` as in step 6, on the compiled document\n"
              "• `xsl:result-document` outputs go through `process_result`: alias → store, relative → intermediate, absolute → direct write\n"
              "• cannot change the `.gal` files",
         fail="as step 6; plus `no store-dir-string-alias` raised by `process_result` (runtime)"),
]
files = [
    None,
    "intermediate/**lang-parsed.xml**\n(language XML)",
    None, None,
    "intermediate/**lang-wizard.xml**\n(language XML)",
    None,
    "principal XML, if the config names one\nfiles written with `xsl:result-document`",
    "intermediate/**lang-xslt.xml**\n(language XML)",
    None,
    "intermediate/**lang-final.xml**\nthe new `.gal` texts, one per chunk",
    None, None,
    "intermediate/**post-compiled.xml**\n(compiled XML)",
    None,
    "principal XML, if the config names one\nyour generated files (code, documents, test data)",
]
lanes = [
    ("language_state_", [
        ("new", "the parsed graph"), ("live", "read"), ("edit", "edited in place, if a command ran"),
        ("live", "also pointed at by language_before_xslt_"), ("live", "printed"),
        ("reset", "printed into Saxon, then reset"), ("none", "the document lives in Saxon"),
        ("new", "rebuilt from the Saxon document"), ("edit", "the seal rewrites it"),
        ("live", "printed as .gal"), ("live", ""), ("live", ""), ("live", "printed"), ("live", ""), ("live", "")]),
    ("language_before_xslt_", [
        ("none", ""), ("none", ""), ("none", ""), ("new", "= language_state_"), ("live", ""),
        ("live", "keeps the old graph alive"), ("live", ""), ("live", ""),
        ("reset", "compared by the seal, then reset"), ("none", ""), ("none", ""), ("none", ""),
        ("none", ""), ("none", ""), ("none", "")]),
    ("compiled_state_", [
        ("reset", "reset"), ("new", "compiled by validate"), ("reset", "reset, if a command ran"),
        ("none", ""), ("new", "ensure_compiled, for the history"), ("live", ""), ("live", "not used by xslt"),
        ("reset", "reset"), ("new", "compiled by validate"), ("live", ""), ("live", ""),
        ("live", "cached: nothing to do"), ("live", "printed as compiled XML"), ("live", "printed into Saxon"), ("live", "")]),
    ("SAXON_SESSION", [
        ("none", ""), ("none", ""), ("none", ""), ("none", ""), ("none", ""),
        ("new", "created, adopts the XML"), ("edit", "each xslt replaces the document"),
        ("reset", "read by xml2cpp, then reset"), ("none", ""), ("none", ""), ("none", ""), ("none", ""),
        ("none", ""), ("new", "created, adopts the compiled XML"), ("edit", "each xslt replaces the document")]),
    ("layout table", [
        ("none", ""), ("touch", "cleared and refilled"), ("none", ""), ("none", ""), ("touch", "cleared and refilled"),
        ("touch", "refilled: the copy xml2cpp reads"), ("live", "held"),
        ("edit", "read by restore_layout"), ("none", ""), ("touch", "refilled"), ("none", ""), ("none", ""),
        ("touch", "refilled"), ("touch", "refilled"), ("none", "")]),
]
lane_style = {
    "none": ("#fafafa", "#d0d0d0", "#aaaaaa"),
    "live": ("#e6f2e0", "#a9cf9b", "#333333"),
    "new": ("#c5e1b8", "#5d9b4a", "#111111"),
    "edit": ("#fff2cc", "#d6b656", "#333333"),
    "reset": ("#f8cecc", "#b85450", "#333333"),
    "touch": ("#e3f1f1", "#7ab5b5", "#333333"),
}

# matrix frame is drawn later (height known). collect rows first
row_defs = {}
domain_h = 34
cond_h = 26
name_h = 40
inout_h = 30
code_h = 40
does_h = max(d.height_for(s["does"], COLW, 12) for s in steps)
files_h = 58
fail_h = max(d.height_for(s["fail"], COLW, 11, pad_v=8) for s in steps)
lane_h = 38

row_y = {}
yy = m_top + 52
row_y["domain"] = yy; yy += domain_h + 8
row_y["cond"] = yy; yy += cond_h + 8
row_y["name"] = yy; yy += name_h + 6
row_y["inout"] = yy; yy += inout_h + 6
row_y["code"] = yy; yy += code_h + 6
row_y["does"] = yy; yy += does_h + 10
row_y["lane"] = yy; yy += len(lanes) * (lane_h + 4) + 8
row_y["files"] = yy; yy += files_h + 8
row_y["fail"] = yy; yy += fail_h + 8
m_bottom = yy + 16
d.frame(40, m_top, W - 80, m_bottom - m_top, "2  The translator: fifteen steps, in the order of the Taskflow chain  (galimatron/translator_library)",
        fill="#ffffff")

# row labels
labels = [("domain", "domain", domain_h), ("cond", "present when", cond_h), ("name", "step", name_h),
          ("inout", "state type in → out", inout_h), ("code", "where it lives", code_h),
          ("does", "what it does", does_h)]
for key, text, h in labels:
    d.box(LABEL_X + 14, row_y[key], LABEL_W - 14, text, h=h, fill="#f2f2f2", stroke="#cccccc", font=12, bold=True, align="left")
for i, (lname, _) in enumerate(lanes):
    ly = row_y["lane"] + i * (lane_h + 4)
    d.box(LABEL_X + 14, ly, LABEL_W - 14, "`%s`" % lname, h=lane_h, fill="#f2f2f2", stroke="#cccccc", font=12, bold=True,
          align="left")
d.box(LABEL_X + 14, row_y["files"], LABEL_W - 14, "files written", h=files_h, fill="#f2f2f2", stroke="#cccccc", font=12,
      bold=True, align="left")
d.box(LABEL_X + 14, row_y["fail"], LABEL_W - 14, "how it fails", h=fail_h, fill="#f2f2f2", stroke="#cccccc", font=12,
      bold=True, align="left")
d.text(LABEL_X + 14, row_y["lane"] - 18, LABEL_W, "memory of `translator_t`", font=10, color="#777777", italic=True)

# domain band
d.box(cx(0), row_y["domain"], PITCH * 11 - (PITCH - COLW), "LANGUAGE domain: GaL is read, checked, edited, written back", h=domain_h,
      fill="#dae8fc", stroke="#6c8ebf", font=13, bold=True)
d.box(cx(11), row_y["domain"], COLW, "LANGUAGE → POST_LANGUAGE (no way back)", h=domain_h, fill="#e1d5e7", stroke="#9673a6",
      font=11, bold=True)
d.box(cx(12), row_y["domain"], PITCH * 3 - (PITCH - COLW), "POST_LANGUAGE domain: compiled picture, XML only", h=domain_h,
      fill="#ffe6cc", stroke="#d79b00", font=13, bold=True)

# conditional band
def band(a, b, text, fill, stroke):
    d.box(cx(a), row_y["cond"], PITCH * (b - a + 1) - (PITCH - COLW), text, h=cond_h, fill=fill, stroke=stroke, font=11,
          dashed=True)

d.box(cx(0), row_y["cond"], COLW, "always", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=11, dashed=True)
d.box(cx(1), row_y["cond"], COLW, "always", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=11, dashed=True)
d.box(cx(2), row_y["cond"], COLW, "only if a wizard statement exists", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=11, dashed=True)
band(3, 8, "only when a language xslt is enabled: the seal and the round trip through Saxon", "#fff9e0", "#d6b656")
d.box(cx(9), row_y["cond"], COLW, "always", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=11, dashed=True)
d.box(cx(10), row_y["cond"], COLW, "inserted by the builder, skipped at run time", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=10, dashed=True)
d.box(cx(11), row_y["cond"], COLW, "always (skipped without a root)", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=11, dashed=True)
d.box(cx(12), row_y["cond"], COLW, "always", h=cond_h, fill="#f5f5f5", stroke="#bbbbbb", font=11, dashed=True)
band(13, 14, "only when a post xslt is enabled", "#fff9e0", "#d6b656")

type_fill = {"GaL": ("#ffffff", "#666666"), "CPP": ("#dae8fc", "#6c8ebf"), "XML": ("#d5e8d4", "#82b366"),
             "SAXON": ("#e1d5e7", "#9673a6")}

name_ids = []
for i, s in enumerate(steps):
    x = cx(i)
    f, st = (YELLOW if s["user"] else BLUE)
    if s.get("skipped"):
        f, st = "#f5f5f5", "#aaaaaa"
    nid = d.box(x, row_y["name"], COLW, "**%d  %s**" % (i, s["name"]), h=name_h, fill=f, stroke=st, font=13,
                dashed=bool(s.get("skipped")), sw=2)
    name_ids.append(nid)
    # in -> out chips
    cw = 112
    d.box(x, row_y["inout"], cw, s["inn"], h=inout_h, fill=type_fill[s["inn"]][0], stroke=type_fill[s["inn"]][1], font=12, bold=True)
    d.text(x + cw, row_y["inout"] + 2, COLW - 2 * cw, "→", font=18, bold=True, align="center", valign="middle", h=inout_h - 4)
    d.box(x + COLW - cw, row_y["inout"], cw, s["out"], h=inout_h, fill=type_fill[s["out"]][0], stroke=type_fill[s["out"]][1], font=12, bold=True)
    d.box(x, row_y["code"], COLW, s["code"], h=code_h, fill="#fbfbfb", stroke="#cccccc", font=11, mono=False, align="left")
    d.box(x, row_y["does"], COLW, s["does"], h=does_h, fill="#ffffff", stroke="#cfcfcf", font=12, align="left", valign="top")
    # files
    fl = files[i]
    if fl:
        d.box(x, row_y["files"], COLW, fl, h=files_h, fill=ORANGE[0], stroke=ORANGE[1], font=11)
    else:
        d.box(x, row_y["files"], COLW, "", h=files_h, fill="#fcfcfc", stroke="#e0e0e0", dashed=True)
    # failure
    fa = s["fail"]
    if fa == "none":
        d.box(x, row_y["fail"], COLW, "", h=fail_h, fill="#fcfcfc", stroke="#e0e0e0", dashed=True)
    else:
        d.box(x, row_y["fail"], COLW, fa, h=fail_h, fill="#fdeeed", stroke="#d9a3a0", font=11, align="left", valign="top")
    # lifelines
    for li, (lname, cells) in enumerate(lanes):
        kind, txt = cells[i]
        f2, st2, fc = lane_style[kind]
        d.box(x, row_y["lane"] + li * (lane_h + 4), COLW, txt, h=lane_h, fill=f2, stroke=st2, font=11, fontcolor=fc,
              dashed=(kind == "none"), sw=1 if kind not in ("new", "reset") else 2)

for a, b in zip(name_ids, name_ids[1:]):
    d.edge(a, b, straight=True, width=2, color="#333333")

# ------------------------------------------------------------------ S3 after the run
y = m_bottom + 50
post_top = y
d.line(560, y - 50, 560, y, color="#333333", width=2.5)
post_ix = len(d.cells)
bx = 70
by = y + 52
post = [
    ("**the run succeeded**",
     "• `summary_xml.set_result(true)`\n• `fsd.do_jobs_at_end()`: write the **delayed .gal** (normal mode: only the files whose text changed), "
     "remove stale files: the `.gal` of aggregates that no longer exist, and generated files of stores with `delete-if-not-rewrited`",
     GREEN),
    ("**the guard writes the summary**",
     "• always, success or failure: `galimatron_summary.xml`\n• one `<transformation>` per step with its status, produced XML and files, the `user-data-for-info` text, and the error text, if any",
     GREEN),
    ("**after `translate()`**",
     "• `taskflow.dot` through `notify_taskflow_graph`\n• private-memory delta logged as `all state: …` (skipped with `committed-report`)\n• `flush_log()`\n• exit code: **0** after success, **1** after any error",
     GREEN),
    ("**the run failed**",
     "• the exception is a LEAF exception; on a worker it became a `captured_leaf_exception`\n• the inner `try_catch` copies its text into the summary `<error>`\n• `do_jobs_at_end` does **not** run: delayed `.gal` are dropped, stale files stay\n• the outer `try_catch` logs the text; the exit code is 1",
     RED),
    ("**the program crashed**",
     "• `crash.cpp`: `report()` writes `galimatron.crash.log` (`Logme::CrashWrite`, stacktrace) and a summary with `status=\"crash\"`, by direct OS calls\n• then `TerminateProcess` or `_exit(128 + signal)`: no destructors, so nothing overwrites the crash summary",
     RED),
]
pids = []
post_h = max(d.height_for(t + "\n" + body, 960, 13) for t, body, _ in post)
bx = 70
for t, body, (f, s) in post:
    cid = d.box(bx, by, 960, t + "\n" + body, h=post_h, fill=f, stroke=s, font=13, align="left", valign="top")
    pids.append(cid)
    bx += 960 + 50
for a, b in zip(pids[:2], pids[1:3]):
    d.edge(a, b, straight=True)
post_frame_h = 52 + post_h + 30
d.frame(40, post_top, W - 80, post_frame_h, "3  The runtime: after the translator", fill="#fcfcfb")
_c = d.cells.pop(); d.cells.insert(post_ix, _c)

panel_top = post_top + post_frame_h + 60

d.height = panel_top + 100

# the panels below the matrix. ROWS limits how many rows of panels are drawn (for bisecting a slow export)
_src = open(os.path.join(HERE, "panels.py"), encoding="utf-8").read()
_skip = os.environ.get("SKIP", "")


def _cut(src, a, b, repl):
    i = src.index(a)
    j = src.index(b)
    return src[:i] + repl + src[j:]


if "G" in _skip:
    _src = _cut(_src, "GX, GW = 1700", "HX, HW = 1790", "g_h = 0\nixG = begin_panel()\nGX, GW = 40, 1700\n")
if "H" in _skip:
    _src = _cut(_src, "HX, HW = 1790", "IX, IW = 3540", "h_h = 0\nixH = begin_panel()\nHX, HW = 1790, 1700\n")
if "I" in _skip:
    _src = _cut(_src, "IX, IW = 3540", "row4_h = max", "i_h = 0\nixI = begin_panel()\nIX, IW = 3540, 1560\n")
try:
    exec(_src)
except Exception as _e:
    if type(_e).__name__ != "StopPanels":
        raise

out = os.path.normpath(os.path.join(HERE, "..", "..", "drawio", "31_dev_pipeline_map.drawio"))
d.save(out)
print("saved", out, "panel_top", panel_top, "cells", len(d.cells))

