# executed inside pipeline_map.py: uses d, panel_top, W and the palette
PW = 5060
ROWS = int(os.environ.get("ROWS", "9"))


class StopPanels(Exception):
    pass



def begin_panel():
    return len(d.cells)


def end_panel(index, x, y, w, h, title, fill="#ffffff", stroke="#bdbdbd"):
    d.frame(x, y, w, h, title, fill=fill, stroke=stroke)
    cell = d.cells.pop()
    d.cells.insert(index, cell)


def close_row(y, h, panels):
    for (ix, x, w, title) in sorted(panels, key=lambda t: -t[0]):
        d.frame(x, y, w, h, title)
        cell = d.cells.pop()
        d.cells.insert(ix, cell)


def chip(x, y, w, text, kind="seed", h=30, font=10):
    if kind == "seed":
        f, s, dash = BLUE[0], BLUE[1], False
    elif kind == "user":
        f, s, dash = YELLOW[0], YELLOW[1], False
    elif kind == "auto":
        f, s, dash = "#f2f7fc", BLUE[1], True
    elif kind == "skip":
        f, s, dash = "#f5f5f5", "#aaaaaa", True
    else:
        f, s, dash = WHITE[0], WHITE[1], False
    return d.box(x, y, w, text, h=h, fill=f, stroke=s, font=font, dashed=dash, sw=1.5 if not dash else 1)


# ================================================================== A: the sequence builder
ay = panel_top
ixA = begin_panel()
AX, AW = 40, 2500
d.text(AX + 30, ay + 44, AW - 60,
       "The list of steps is **built**, not written. You configure the interesting steps (the seed). "
       "`transform_sequence_builder` inserts the conversions between them, so that each step gets the representation it needs.",
       font=12, color="#444444")
bx, by = AX + 30, ay + 100
b1 = d.box(bx, by, 520,
           "**the seed**: what is configured\n"
           "• `cpp2cpp_validate`\n"
           "• `cpp2cpp_wizard`\n"
           "• only with a language xslt: `cpp2cpp_before_xslt`, your language xslts (`xml2xml`, in config order), `cpp2cpp_after_xslt`\n"
           "• your post xslts (`xml2xml`)\n"
           "They keep their order. A step with `\"enable\": false` is not in the seed.",
           fill=BLUE[0], stroke=BLUE[1], font=12, align="left", valign="top")
hb1 = d.last_h
b2 = d.box(bx + 560, by, 760,
           "**the catalog**: state transforms, one edge each (domain, state type)\n"
           "• `gal2cpp`   LANGUAGE GaL → CPP\n"
           "• `cpp2gal`   LANGUAGE CPP → GaL\n"
           "• `cpp2xml`   LANGUAGE CPP → XML\n"
           "• `xml2saxon`   LANGUAGE XML → SAXON\n"
           "• `xml2cpp`   LANGUAGE SAXON → CPP\n"
           "• `cpp2post_cpp`   LANGUAGE CPP → POST CPP\n"
           "• `post_cpp2post_xml`   POST CPP → POST XML\n"
           "• `post_xml2saxon`   POST XML → POST SAXON",
           fill="#f2f7fc", stroke=BLUE[1], font=12, align="left", valign="top", dashed=True)
hb2 = d.last_h
b3 = d.box(bx + 1360, by, 1050,
           "**builder_t::complete_transform_sequence**  (`translator/detail/transform_sequence_builder.cpp`, unit-tested)\n"
           "1. `check_transform_sequence`: LANGUAGE steps first, then POST_LANGUAGE steps. A return to LANGUAGE is an error\n"
           "2. `check_state_transforms`: the catalog must hold the seven edges a run needs\n"
           "3. before each seed step, `ensure_state`: a breadth-first search over the catalog finds the shortest path from the current representation (the language part may not leave LANGUAGE)\n"
           "4. when the language part is done: append `cpp2gal`, unless the last step already is one\n"
           "5. no post xslt: continue to POST XML. A post xslt needs SAXON, so the path ends in `post_xml2saxon`",
           fill=GREEN[0], stroke=GREEN[1], font=12, align="left", valign="top")
hb3 = d.last_h
d.edge(b2, b3, straight=True, text="catalog")
d.edge(b1, b3, text="seed", exit_xy=(0.5, 0), entry_xy=(0.2, 0),
       points=[(bx + 260, by - 24), (bx + 1360 + 210, by - 24)])
ey = by + max(hb1, hb2, hb3) + 40
d.text(AX + 30, ey, 1200, "**What comes out**, for four common projects (solid: the seed, dashed: inserted by the builder)", font=13)
ey += 30
names = [
    ("gal2cpp", "auto"), ("validate", "seed"), ("Wizard", "seed"), ("before_xslt", "seed"), ("cpp2xml", "auto"),
    ("xml2saxon", "auto"), ("your xslt", "user"), ("xml2cpp", "auto"), ("after_xslt", "seed"), ("cpp2gal", "auto"),
    ("gal2cpp (skip)", "skip"), ("cpp2post_cpp", "auto"), ("post_cpp2post_xml", "auto"), ("post_xml2saxon", "auto"),
    ("your post xslt", "user")]
rows = [
    ("no xslt (7 steps)", [0, 1, 2, 9, 10, 11, 12]),
    ("language xslt only (13)", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("post xslt only (9)", [0, 1, 2, 9, 10, 11, 12, 13, 14]),
    ("both (15)", list(range(15))),
]
chip_w, chip_pitch = 128, 134
for label, idxs in rows:
    d.box(AX + 30, ey, 270, label, h=30, fill="#f2f2f2", stroke="#cccccc", font=12, bold=True, align="left")
    px = AX + 320
    prev = None
    for i in idxs:
        nm, kind = names[i]
        c = chip(px, ey, chip_w, nm, kind)
        if prev:
            d.edge(prev, c, straight=True, width=1)
        prev = c
        px += chip_pitch
    ey += 40
d.text(AX + 30, ey + 4, AW - 60,
       "The seed steps are in the Taskflow chain as they are. The Wizard step is skipped at run time when no `wizard` statement exists. "
       "Tests use `prepare_testing_transforms()` instead: the seed is only the steps that a `testing_t` flag switches on, and the builder "
       "inserts a conversion only where two seed steps do not meet.",
       font=11, color="#555555")
a_h = ey + 60 - ay
# ---- B: validation DAG
ixB = begin_panel()
BX, BW = 2580, 2520
bx0 = BX + 30
by0 = ay + 56
d.text(bx0, by0 - 8, BW - 60,
       "`cpp2cpp_validate_t::build()` puts twelve checks in a Taskflow **subflow**. They run on worker threads. "
       "An arrow means \"runs after\". The edges are those of `intermediate/taskflow.dot`.",
       font=12, color="#444444")
nw, nh = 400, 44
col = [bx0, bx0 + 470, bx0 + 940, bx0 + 1410, bx0 + 1900]
node_y0 = by0 + 56
step = 62


def vnode(x, y, text, kind="check"):
    f, s = (WHITE[0], "#6c8ebf") if kind == "check" else ((GREEN[0], GREEN[1]) if kind == "end" else (YELLOW[0], YELLOW[1]))
    return d.box(x, y, nw, text, h=nh, fill="#eef4fb" if kind == "check" else f, stroke=s, font=10, sw=1.5)


n_root = vnode(col[0], node_y0 + 3 * step, "is root aggregate single")
c1 = [
    "is root aggregate version declarations from zero continuous",
    "is root aggregate version definitions repeat declarations",
    "is aggregate version declarations deleted continuous",
    "is aggregate version definitions not deleted",
    "is aggregate version definitions repeat declarations",
    "is anonymous versions owned",
    "is aggregate names unique",
    "is aggregate indices unique continuous",
]
n1 = [vnode(col[1], node_y0 + i * step, t) for i, t in enumerate(c1)]
n_match = vnode(col[2], node_y0 + 0 * step, "is aggregate version declarations match root")
n_hm = vnode(col[3], node_y0 + 1 * step, "is version hashes match")
n_hp = vnode(col[3], node_y0 + 3 * step, "is version hashes present")
join_y = node_y0 + 4 * step + nh // 2 - 20
n_end = vnode(col[4] - 20, node_y0 + 4 * step - 20, "join: compile_for_validation\n(`cpp2post_cpp::translate`)", kind="end")
mid = nh // 2
bus1 = col[0] + nw + 35          # between the root check and column 1
bus2 = col[1] + nw + 35          # right of column 1
bus3 = col[2] + nw + 35          # right of the match-root check
bus4 = col[3] + nw + 35          # right of the hash checks
ry_ = node_y0 + 3 * step + mid
for i, n in enumerate(n1):
    yi = node_y0 + i * step + mid
    d.edge(n_root, n, width=1.2, exit_xy=(1, 0.5), entry_xy=(0, 0.5), points=[(bus1, ry_), (bus1, yi)])
d.edge(n1[0], n_match, width=1.2, straight=True)
hm_y = node_y0 + 1 * step + mid
hp_y = node_y0 + 3 * step + mid
mt_y = node_y0 + 0 * step + mid
for src, ys in [(n1[1], node_y0 + 1 * step + mid), (n1[2], node_y0 + 2 * step + mid), (n1[3], node_y0 + 3 * step + mid),
                (n1[4], node_y0 + 4 * step + mid), (n1[5], node_y0 + 5 * step + mid)]:
    for tgt, yt in [(n_hm, hm_y), (n_hp, hp_y)]:
        d.edge(src, tgt, width=1.0, color="#999999", exit_xy=(1, 0.5), entry_xy=(0, 0.5), points=[(bus2, ys), (bus2, yt)])
for tgt, yt in [(n_hm, hm_y), (n_hp, hp_y)]:
    d.edge(n_match, tgt, width=1.0, color="#999999", exit_xy=(1, 0.5), entry_xy=(0, 0.5), points=[(bus3, mt_y), (bus3, yt)])
for src, ys in [(n_hm, hm_y), (n_hp, hp_y), (n1[6], node_y0 + 6 * step + mid), (n1[7], node_y0 + 7 * step + mid)]:
    d.edge(src, n_end, dashed=True, color="#3b6ea5", width=1.2, exit_xy=(1, 0.5), entry_xy=(0, 0.5),
           points=[(bus4, ys), (bus4, node_y0 + 4 * step - 20 + mid)])
notes_y = node_y0 + 8 * step + 10
d.box(bx0, notes_y, BW - 60,
      "• Seven checks (the four root checks, `is anonymous versions owned`, both hash checks) do **nothing** when the Wizard command is, or contains, `create root aggregate`: the root does not exist yet.\n"
      "• A hash of a version named by `create hash … force` or `delete hash … force` is not checked in this run.\n"
      "• A failure is thrown on a worker: `fail(code, what, where)` runs `augment_where` **inside** `capture_or_rethrow`, and `subflow.join()` rethrows on the caller.\n"
      "• Which error is reported first is not deterministic when several checks fail.\n"
      "• `validate_memo_t` caches only the three root gate checks (shared mutex, success only). It is replaced together with the checker (`refresh_checks`).\n"
      "• Wizard commands are **not** in this graph. The Wizard step calls `may_execute_wizard_command()` itself (panel C).",
      fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
b_h = notes_y + d.last_h + 30 - ay
row1_h = max(a_h, b_h)
d.height = ay + row1_h + 60
close_row(ay, row1_h, [(ixA, AX, AW, "A  How the list of steps is built"), (ixB, BX, BW, "B  The twelve checks of `cpp2cpp_validate`")])
if ROWS < 2:
    raise StopPanels()

# ================================================================== C: Wizard, D: compile
cy = ay + row1_h + 50
ixC = begin_panel()
CX, CW = 40, 2500
cx0 = CX + 30
cy0 = cy + 56
d.text(cx0, cy0 - 12, 1180,
       "`cpp2cpp_wizard::translate` works **in place** on the language graph, through the same `builder_t` that the parser uses. "
       "There is no dry run: the checks run on the real graph right before each change.",
       font=12, color="#444444")
f0 = d.box(cx0, cy0 + 44, 540, "`translate()`: no Wizard statement → return the graph unchanged", h=44, fill=BLUE[0], stroke=BLUE[1], font=11)
f1 = d.box(cx0, cy0 + 110, 540, "`validate_->is_wizard_command_single()`: one statement in the whole graph, not one per file", h=44, fill=BLUE[0], stroke=BLUE[1], font=11)
f2 = d.box(cx0, cy0 + 176, 540, "single command: `apply_one(type)`  — a `switch` over `command_et`", h=44, fill=BLUE[0], stroke=BLUE[1], font=11)
f3 = d.box(cx0 + 600, cy0 + 110,  560,
           "**batch** (`apply_wizard_batch`)\n"
           "• `may_execute_wizard_command()`: batch context is a chunk\n"
           "• for each item:  `refresh_checks()`  (new memo, new checker, **re-snapshot** of aggregates)\n"
           "• overwrite the stored statement: `type`, `data` = the item\n"
           "• `is_wizard_batch_command_create()`\n"
           "• `apply_one(item.type)`\n"
           "• restore the statement",
           fill=BLUE[0], stroke=BLUE[1], font=11, align="left", valign="top")
f4 = d.box(cx0, cy0 + 252, 540, "`apply_*` begin with `validate_->may_execute_wizard_command()`, then change the graph with `builder_t` (vertices get `created_by_wizard = true`) and call `refresh_live_and_hashed()` after structural edits", h=76,
           fill=GREEN[0], stroke=GREEN[1], font=11)
f5 = d.box(cx0, cy0 + 346, 540, "`comment_executed_command()`: the statement text becomes `//` lines at the top of its chunk. `cpp2gal` prints only comments, never the command", h=60,
           fill=GREEN[0], stroke=GREEN[1], font=11)
d.edge(f0, f1, straight=True); d.edge(f1, f2, straight=True); d.edge(f1, f3, text="batch")
d.edge(f2, f4, straight=True); d.edge(f3, f4); d.edge(f4, f5, straight=True)
d.box(cx0 + 600, cy0 + 252, 560,
      "**closed versions**\n"
      "closed = a root version at or before the last hashed declaration (`last_hashed`).\n"
      "The protection is entirely in the validator (`wizard-closed-version` rules). The `apply_*` functions assume it passed, "
      "and after any change of hashes or declarations they must refresh `last_hashed`, or the next command of a batch sees a stale seal.",
      fill=YELLOW[0], stroke=YELLOW[1], font=11, align="left", valign="top")
# command table
tx = cx0 + 1240
d.text(tx, cy0 - 12, 1180, "**command → check → change**  (P: the graph changes, H: a `delete` is written into the history)", font=12)
cmds = [
    ("CREATE_ROOT_AGGREGATE", "P", "is_wizard_create_root_aggregate_*", "apply_wizard_create_root_aggregate"),
    ("CREATE_AGGREGATE", "P", "is_wizard_create_aggregate_*", "apply_wizard_create_aggregate"),
    ("COPY_AGGREGATE", "P", "is_wizard_copy_aggregate_*", "apply_wizard_copy_aggregate"),
    ("CONTINUE_AGGREGATE", "P", "is_wizard_continue_aggregate_*", "apply_wizard_continue_aggregate"),
    ("DELETE_AGGREGATE", "H", "is_wizard_delete_aggregate_*", "apply_wizard_delete_aggregate"),
    ("CREATE_VERSION", "P", "is_wizard_create_version_*", "apply_wizard_create_version → add_next_version"),
    ("DELETE_VERSION", "P", "is_wizard_delete_version_*", "apply_wizard_delete_version"),
    ("COLLAPSE_VERSION", "P", "is_wizard_collapse_version_*", "apply_wizard_collapse_version"),
    ("CREATE_LABEL", "P", "is_wizard_version_statement", "apply_wizard_create_label"),
    ("CREATE_TAG", "P", "is_wizard_version_statement", "apply_wizard_create_tag"),
    ("DELETE_TAG", "H", "is_wizard_version_statement", "apply_wizard_delete_tag"),
    ("CREATE_ORDERING", "P", "is_wizard_version_statement", "apply_wizard_create_ordering"),
    ("CREATE_HASH", "P", "is_wizard_create_hash_*", "apply_wizard_create_hash → write_version_hash"),
    ("DELETE_HASH", "P", "is_wizard_delete_hash_*", "apply_wizard_delete_hash → clear_hashes_of_version"),
    ("BATCH", "–", "is_wizard_batch_*", "apply_wizard_batch"),
]
ty = cy0 + 22
d.box(tx, ty, 230, "command", h=26, fill="#f2f2f2", stroke="#cccccc", font=11, bold=True)
d.box(tx + 234, ty, 40, "", h=26, fill="#f2f2f2", stroke="#cccccc", font=11, bold=True)
d.box(tx + 278, ty, 400, "checked by (`cpp2cpp_validate_t`)", h=26, fill="#f2f2f2", stroke="#cccccc", font=11, bold=True)
d.box(tx + 682, ty, 560, "applied by (`cpp2cpp_wizard_t`)", h=26, fill="#f2f2f2", stroke="#cccccc", font=11, bold=True)
ty += 30
for name, kind, chk, app in cmds:
    d.box(tx, ty, 230, "`%s`" % name, h=26, fill="#ffffff", stroke="#cfcfcf", font=10, align="left")
    d.box(tx + 234, ty, 40, kind, h=26, fill="#ffffff", stroke="#cfcfcf", font=10, bold=True)
    d.box(tx + 278, ty, 400, "`%s`" % chk, h=26, fill="#eef4fb", stroke="#cfcfcf", font=10, align="left")
    d.box(tx + 682, ty, 560, "`%s`" % app, h=26, fill="#eef7ee", stroke="#cfcfcf", font=10, align="left")
    ty += 30
d.text(tx, ty + 2, 1240,
       "Files: checks in `cpp2cpp_validate/detail/wizard/wizard_{root,aggregate,version,statement}.cpp`, "
       "changes in `cpp2cpp_wizard/detail/{aggregate,version,statement,hash}.cpp`. Messages are the constants of `state/wizard/tags.hpp`.",
       font=10, color="#666666")
c_h = max(ty + 40, cy0 + 460) - cy

# ---- D compile
DX, DW = 2580, 2520
dx0 = DX + 30
dy0 = cy + 56
ixD = begin_panel()
d.text(dx0, dy0 - 12, DW - 60,
       "`cpp2post_cpp` turns the language graph (what each version **says**) into `compiled_part_t` (what each version **is**). "
       "The language graph is not changed.",
       font=12, color="#444444")
dw = 760
chain = [
    ("**1  register** the label callback; **root aggregate first**",
     "`create_merged_versions_entities` (merge.cpp): for each root version, first the parked bodies (`version before N`) it owns, then its own statements. "
     "`delete;` is skipped.", BLUE),
    ("**2  `compile_merged_versions_entities`** (compile_merged.cpp), once per aggregate",
     "a. `naming_unnamed_tags`: a tag without a name takes it from a `tag-name-from` label (must match `identifier_pattern`)\n"
     "b. `remember_values_before`: the value just before each statement, for the history\n"
     "c. per version: `check_labels_in_version` → `compile_tags_in_version` → `template_engine::render` → write `tag_container`\n"
     "d. root only: `compile_orderings_in_version`", BLUE),
    ("**3  each other aggregate**, in file order",
     "the same two calls. The root's statements of each version are copied in first, so an aggregate can override them. "
     "Not copied: a root tag with mode `local`; nothing at all when the aggregate's version mode is `local` or `own`. A deleted version has no body.", BLUE),
    ("**4  `notify_default_aggregates_ordering`**",
     "`ranks_of_ordering`: a directed graph from the `{A, B, C}` chains, topological sort, rank = longest chain of predecessors, and a check that the result is a strict weak order. "
     "Unnamed aggregates follow, in file order. The stored index is the final **position**.", BLUE),
    ("**5  `force_resolve_labels`**", "every label reference becomes its static value. The compiled part keeps no label references.", BLUE),
]
cyy = dy0 + 36
cids = []
for t, body, (f, s) in chain:
    cid = d.box(dx0, cyy, dw, t + "\n" + body, fill=f, stroke=s, font=11, align="left", valign="top")
    cids.append(cid)
    cyy += d.last_h + 22
for a, b in zip(cids, cids[1:]):
    d.edge(a, b, straight=True)
# visibility table
vx = dx0 + dw + 40
d.text(vx, dy0 + 22, 1000, "**which statements reach a version**  (`statement_reaches_version`)", font=12)
vis = [
    ("the statement is in the same version", "visible"),
    ("the statement is in a later version", "never"),
    ("earlier version, version mode `inherit`", "visible"),
    ("earlier version, version mode `local`", "invisible"),
    ("earlier version, version mode `own`", "only statements of this aggregate (the root is dropped)"),
    ("earlier version, version mode `once`", "only statements of the root (this aggregate's earlier ones drop)"),
    ("tag mode `once` or `local`", "only in the version where it is written (never from a parked body)"),
]
vy = dy0 + 52
for a, b in vis:
    d.box(vx, vy, 400, a, h=34, fill="#f7f7f7", stroke="#cccccc", font=10, align="left")
    d.box(vx + 404, vy, 560, b, h=34, fill="#eef7ee" if b.startswith("visible") else "#fdf3f2" if b in ("never", "invisible") else "#fff9e0",
          stroke="#cccccc", font=10, align="left")
    vy += 38
vy += 8
d.box(vx, vy, 964,
      "**last declaration wins**: `compile_tags_in_version` walks the statements from the end; the first one seen per resolved name is kept, "
      "and a `delete name;` consumes the name. Deleting a label is an error. Deleting an absent tag only logs a warning.\n"
      "**templates**: `template_engine::render` builds JSON from the version's tags (several values → an array, `{{name}}` means `{{name.0}}`) and renders each `_te` string with inja. "
      "The result is stored per (version, string); the language graph keeps the raw text.\n"
      "**errors**: `throw_compiler(text)` = LEAF `cpp2post_cpp` + `e_what_info`, with path (through `report_path`), aggregate and version attached.",
      fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
vy += d.last_h + 20
d.box(vx, vy, 964,
      "**a small example**\n"
      "language: root `version 0 { currency = { \"EUR\" }; }`, `Apple` `version 0 { price = { \"3\" }; }`, `Apple` `version 1 { price = { \"4\" }; }`\n"
      "compiled `Apple`, version 0:  `currency = EUR`, `price = 3`\n"
      "compiled `Apple`, version 1:  `currency = EUR` (from the root, copied in), `price = 4` (the last declaration wins)\n"
      "Version 1 of `Apple` never repeated the currency: the compiled XML says it for every version.",
      fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
d_h = max(cyy, vy + d.last_h) + 30 - cy
row2_h = max(c_h, d_h)
d.height = cy + row2_h + 60
close_row(cy, row2_h, [(ixC, CX, CW, "C  The Wizard step"), (ixD, DX, DW, "D  The compile step (`cpp2post_cpp`)")])
if ROWS < 3:
    raise StopPanels()

# ================================================================== E: xml, F: routing
ey2 = cy + row2_h + 50
ixE = begin_panel()
EX, EW = 40, 2500
ex0 = EX + 30
ee0 = ey2 + 56
d.text(ex0, ee0 - 12, EW - 60,
       "The XML is the only thing an xslt sees, but the **source text and comments** live on graph vertices. "
       "A side table carries them across the round trip.",
       font=12, color="#444444")
e1 = d.box(ex0, ee0 + 40, 360, "**`language_part_t`**\nvertices keep `user_formatting` (source text) and `user_comments`", fill=GREEN[0], stroke=GREEN[1], font=11, h=96)
e2 = d.box(ex0 + 440, ee0 + 40, 440, "**`cpp2xml::translate`**\nclears the layout table. For each vertex that has text or comments: counts `++next`, writes `layout-mark=\"N\"`, stores `{formatting, comments, fingerprint}` under N", fill=BLUE[0], stroke=BLUE[1], font=11, h=96)
e3 = d.box(ex0 + 960, ee0 + 40, 330, "**language XML**\nprinted, then parsed into Saxon by `xml2saxon`", fill=PURPLE[0], stroke=PURPLE[1], font=11, h=96)
e4 = d.box(ex0 + 1370, ee0 + 40, 330, "**your xslt**\nmay change, add or delete any element", fill=YELLOW[0], stroke=YELLOW[1], font=11, h=96)
e5 = d.box(ex0 + 1780, ee0 + 40, 650, "**`xml2cpp_saxon`**: `builder_t` builds a new graph. `restore_layout`: comments always come back; the source text comes back only when `fingerprint(node)` still equals the stored one, "
           "so an edited node is printed fresh by `cpp2gal`", fill=BLUE[0], stroke=BLUE[1], font=11, h=96)
for a, b in [(e1, e2), (e2, e3), (e3, e4), (e4, e5)]:
    d.edge(a, b, straight=True)
fp = ("**fingerprint**: element name, attributes except `layout-mark` (sorted), children, and non-blank text. Two implementations "
      "(`layout::fingerprint` on pugixml, `fingerprint` on `node_t`) must give the same text for the same XML.")
d.box(ex0, ee0 + 160, EW - 60, fp, fill="#fbfbfb", stroke="#cccccc", font=11, align="left", h=46)
# language vs compiled
ly0 = ee0 + 226
half = (EW - 80) // 2
d.box(ex0, ly0, half, "**language XML**  `<galimatron><language>`", h=30, fill=BLUE[0], stroke=BLUE[1], font=12)
d.box(ex0 + half + 20, ly0, half, "**compiled XML**  `<galimatron><compiled>`", h=30, fill=ORANGE[0], stroke=ORANGE[1], font=12)
lang_txt = (
    "`<chunk><location><filesystem path root relative …/></location>` per file\n"
    "`<root-aggregate name>` / `<aggregate name index>` with `…-version-declarations` (`index status comment hash`) and `…-version-definitions` (`index` or `owner`, `mode`)\n"
    "`<tag index name mode layout-mark>` with `<label-refs><static><label-ref name index/>`, `<values><value index><string delimiter template-engine>`, records, arrays\n"
    "`<label index name>` with `<static><values>…<tag-name-from/>` or `<dynamic value/>`\n"
    "`<ordering index name>`, `<delete index name?/>`\n"
    "Wizard marks: `<dynamic wizard=\"new-version|new-aggregate|new-root-aggregate\"/>`, and `<dynamic labelname=\"value\"/>` on a copied tag that uses a dynamic label\n"
    "`<string-delimiters>`, and `<history>` beside `<language>`")
comp_txt = (
    "the same skeleton, but each version lists only the **effective tags** of the compiled state, in order\n"
    "a tag **always has its name** (resolved from `tag-name-from`)\n"
    "no label statements, no `label-refs`: each static label becomes an **attribute on `<value>`**, `<value index=\"0\" field=\"type\">`\n"
    "`<string>` holds the **rendered** text and no `template-engine` mark\n"
    "`<orderings><ordering name index=\"position\"/></orderings>` under each aggregate version definition\n"
    "no Wizard marks\n"
    "`<history>`: per version, per aggregate, the changes (`add`, `replace`, `delete`, `label`, `ordering`, `create-aggregate`, `delete-version`)")
h_e = max(d.height_for(lang_txt, half, 11), d.height_for(comp_txt, half, 11))
d.box(ex0, ly0 + 34, half, lang_txt, h=h_e, fill="#f4f8fd", stroke="#cccccc", font=11, align="left", valign="top")
d.box(ex0 + half + 20, ly0 + 34, half, comp_txt, h=h_e, fill="#fff8ee", stroke="#cccccc", font=11, align="left", valign="top")
e_h = ly0 + 34 + h_e + 30 - ey2

FX, FW = 2580, 2520
ixF = begin_panel()
fx0 = FX + 30
fy0 = ey2 + 56
d.text(fx0, fy0 - 12, FW - 60,
       "`process_result` (runtime) receives every step's output **while the run goes on** and sends it to a place of the filesystem decorator.",
       font=12, color="#444444")
g0 = d.box(fx0, fy0 + 40, 330, "**step result**\n`produced_xml`, `produced_files`,\nstatus, config transform", fill=BLUE[0], stroke=BLUE[1], font=11, h=76)
g1 = d.box(fx0 + 400, fy0 + 40, 400, "`produced_xml` → **intermediate place**\nseparate mode: `<filesystem>` elements are dropped from the text, so no absolute path is written", fill=ORANGE[0], stroke=ORANGE[1], font=11, h=76)
d.edge(g0, g1, straight=True)
rt = [
    ("step is `cpp2gal` (named CPP2GAL)", "old path is split by the **output .gal place** root; written there (normal mode: held until the end)"),
    ("path `@@alias@@relative@@` (an `xsl:result-document href`)", "the store with that alias (**its own place**), `replace-escaped-form-to-original-symbols` applied if set"),
    ("a relative path", "**intermediate place**"),
    ("an absolute path", "`filesystem.write` directly: the decorator is **bypassed**"),
]
ry = fy0 + 140
d.text(fx0, ry - 6, 600, "`produced_files`, each one by the kind of its path:", font=11, bold=True)
ry += 20
for a, b in rt:
    k = d.box(fx0, ry, 880, a, h=36, fill=PURPLE[0], stroke=PURPLE[1], font=10, align="left")
    t = d.box(fx0 + 920, ry, 1000, b, h=36, fill=ORANGE[0], stroke=ORANGE[1], font=10, align="left")
    d.edge(k, t, straight=True)
    ry += 44
d.box(fx0, ry + 8, FW - 60,
      "**the decorator's `printout`** (`filesystem_decorator.cpp`): split the old path by the owning place → merge with the new parts (the place root wins) → "
      "`write.once` and already saved? **error** → mark the file as rewritten (so the end-of-run cleanup keeps it) → `if_content_differ`: compare with cache or disk → write now, or set `pending_write` for `do_jobs_at_end`.\n"
      "It returns `finally_path`. `process_result` turns those paths into the summary entry (relative to `gal.cfg` with `committed-report`).",
      fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
ry += 8 + d.last_h + 14
d.box(fx0, ry, FW - 60,
      "**Saxon side** (`saxon_session_t`): parameters are set before compiling and are strings only; `setCaptureResultDocuments(true)`; `xsl:message` text goes to the log between "
      "`begin messages from Saxon` and `end messages from Saxon`; each result document becomes `{content = node->toString(), path = href}`. "
      "A `SaxonApiException` is turned into text first (`printout_native_saxon_exception`), then thrown as LEAF `translator`.",
      fill=PURPLE[0], stroke=PURPLE[1], font=11, align="left", valign="top")
ry += d.last_h
f_h = ry + 30 - ey2
row3_h = max(e_h, f_h)
d.height = ey2 + row3_h + 60
close_row(ey2, row3_h, [(ixE, EX, EW, "E  The XML round trip and the layout table"), (ixF, FX, FW, "F  Where the output of a step goes")])
if ROWS < 4:
    raise StopPanels()

# ================================================================== G seal, H exceptions, I places
gy = ey2 + row3_h + 50
GX, GW = 40, 1700
ixG = begin_panel()
gx0 = GX + 30
gy0 = gy + 56
d.text(gx0, gy0 - 12, GW - 60,
       "`reassign_sealed_edits(before, after)` keeps closed versions closed when your language xslt changes them.",
       font=12, color="#444444")
seal = [
    ("no root, or no hashed version (`last_hashed`) → return `after`", BLUE),
    ("`reject_sealed_shape`: an aggregate removed, or a version inserted into the sealed history → **error**", RED),
    ("`sealed_history_differs`? compare hash, comment, status and `definition_payload` of every sealed version. No → return `after`", BLUE),
    ("`effective_edits`: compile both graphs, diff the **effective tags** of the last sealed version → `REASSIGN` or `DELETE_TAG` per aggregate", BLUE),
    ("only Wizard copies that use a dynamic label? Then the xslt only finished them: `write_version_hash(after, last_sealed)` refreshes the hash and return", GREEN),
    ("`restore_sealed_history`: every sealed version of `after` is replaced by a clone from `before` (hash, comment, status, presentation, children)", BLUE),
    ("no effective edits → return (the xslt changes were only formatting)", BLUE),
    ("`destination_version`: the first open version after `last_sealed`, or `open_next_version` creates one for every live aggregate", BLUE),
    ("`write_edits`: clone each changed tag into that version (marked `created_by_wizard`), or write `delete name;`. A tag already named there is not touched", GREEN),
]
seal = seal[:int(os.environ.get("SEALN", len(seal)))]
sy = gy0 + 36
sids = []
for t, (f, s) in seal:
    sid = d.box(gx0, sy, GW - 60, t, fill=f, stroke=s, font=11, align="left")
    sids.append(sid)
    sy += d.last_h + 14
for a, b in zip(sids, sids[1:]):
    d.edge(a, b, straight=True)
g_h = sy + 20 - gy

HX, HW = 1790, 1700
ixH = begin_panel()
hx0 = HX + 30
hy0 = gy + 56
d.text(hx0, hy0 - 12, HW - 60,
       "Errors are Boost.LEAF exceptions with a **domain**, a **subdomain** and payloads. Thrown inside `galimatron`, caught in the runtime, printed once.",
       font=12, color="#444444")
h1 = d.box(hx0, hy0 + 40, 760,
           "**throw**: `leaf::throw_exception(domain, subdomain, e_what_info, [code], …)`\n"
           "context by RAII guards: `augment_domain`, `augment_path`, `augment_aggregate`, `augment_version`, `augment_where` (keep the returned object alive)\n"
           "types only in `common_library/exception_declaration.hpp`", fill=BLUE[0], stroke=BLUE[1], font=11, align="left", valign="top")
h2 = d.box(hx0 + 800, hy0 + 40, 810,
           "**on the main thread** the exception travels to the nearest `try_catch`.\n"
           "**on a Taskflow worker** there is no LEAF context: `capture_or_rethrow` runs the code under `leaf::try_capture_all` and throws `captured_leaf_exception`. "
           "`subflow.join()` or `future.get()` rethrows it on the caller's thread, and `leaf_spy` unloads the payloads there.",
           fill=YELLOW[0], stroke=YELLOW[1], font=11, align="left", valign="top")
d.edge(h1, h2, straight=True)
h3 = d.box(hx0, hy0 + 200, 760,
           "**inner catch**: `translate_by_config` → `runtime::try_catch`, `is_throw_out = true`. `leaf_spy::spy_handler_t` loads every domain, subdomain, enum and payload, prints "
           "`Exception details:` into a stream; `notify_printed` copies the text into the summary `<error>`; the exception goes on.",
           fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
h4 = d.box(hx0 + 800, hy0 + 200, 810,
           "**outer catch**: `translate_impl_t::translate` → the same wrapper; the text is logged with `fLogmeE`; the result is 1. "
           "`is_testing_mode` lets the exception leave `translate()` in tests, which print it with `print_leaf_exception`.",
           fill=GREEN[0], stroke=GREEN[1], font=11, align="left", valign="top")
d.edge(h3, h4, straight=True)
d.edge(h2, h3)
d.box(hx0, hy0 + 360, HW - 60,
      "Not LEAF: syntax errors are `antlr4::ParseCancellationException` (the spy prints them with a `dynamic_cast`); a bad log config or a failed `merge_paths` is `std::runtime_error`. "
      "Both show \"NO DOMAIN-SPECIFIC EXCEPTION CATEGORY MATCHED\" in the printout.\n"
      "The path in the printed text is spelled from copies in `e_path_info` (`committed_report`, `config_dir`), because the run's path report may be gone when the text is built.",
      fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
h_h = hy0 + 360 + d.last_h + 30 - gy

IX, IW = 3540, 1560
ixI = begin_panel()
ix0 = IX + 30
iy0 = gy + 56
d.text(ix0, iy0 - 12, IW - 60,
       "A **place** is a folder with rules. Every file the translator writes goes through one, except the summary, `taskflow.dot` and absolute user paths.",
       font=12, color="#444444")
cols = [("place", 340), ("read", 100), ("write", 360), ("remove", 330)]
hx_ = ix0
for t, w in cols:
    d.box(hx_, iy0 + 40, w - 4, t, h=26, fill="#f2f2f2", stroke="#cccccc", font=11, bold=True)
    hx_ += w
prow = [
    ("input/output .gal  (normal mode)", "cached", "held until the end of a **successful** run; only if the text changed; once", "files not rewritten: removed at the end"),
    ("input .gal  (separate)", "not cached", "–", "–"),
    ("output .gal  (separate)", "–", "at once; once", "all .gal removed at the start"),
    ("intermediate xml  (.xml, .html)", "not cached", "at once; once", "all removed at the start"),
    ("store of `other-files`  (one per entry)", "not cached", "at once; only if the text changed; once", "not rewritten: removed at the end, unless `delete-if-not-rewrited` is false"),
]
py_ = iy0 + 70
for row in prow:
    hx_ = ix0
    hmax = max(d.height_for(c, w - 4, 10) for c, (t, w) in zip(row, cols))
    for c, (t, w) in zip(row, cols):
        d.box(hx_, py_, w - 4, c, h=hmax, fill="#ffffff", stroke="#cfcfcf", font=10, align="left", valign="middle")
        hx_ += w
    py_ += hmax + 4
d.box(ix0, py_ + 10, IW - 60,
      "• \"once\": writing the same path twice in one run is an error.\n"
      "• Roots of places may not be nested (checked in `add_place`).\n"
      "• \"at the end\" runs in `do_jobs_at_end`, only after a run that succeeded.\n"
      "• The log folder is opened by Logme from `log.cfg`. It is not a place.\n"
      "• Nothing checks that a relative `..` path stays in its place, so confinement is by construction.",
      fill="#fbfbfb", stroke="#cccccc", font=11, align="left", valign="top")
i_h = py_ + 10 + d.last_h + 30 - gy
row4_h = max(g_h, h_h, i_h)
close_row(gy, row4_h, [(ixG, GX, GW, "G  The seal (`cpp2cpp_after_xslt`)"), (ixH, HX, HW, "H  Errors"), (ixI, IX, IW, "I  The places of the filesystem decorator")])

final_h = gy + row4_h + 60
d.height = final_h
