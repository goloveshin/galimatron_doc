# Known quirks

Things that surprise people who read the code for the first time. Some are design choices with a reason, some are leftovers. Knowing which is which saves a day.

## Design choices

- **The graph never forgets a vertex.** A delete detaches. Use the version containers, not a scan of all vertices.
- **The compiled part is a cache.** Anything that changes the language graph must reset `compiled_state_`, and `ensure_compiled()` rebuilds it lazily.
- **There is no dry run** for the wizard. The checks run on the real graph right before each change. A batch that fails half way leaves the graph changed, but the run aborts, so nothing is written (in normal mode).
- **Validation runs twice at most**: before the wizard, and after a language xslt. Not after the wizard alone.
- **`.gal` files are written last** in normal mode: they are delayed to `do_jobs_at_end`. XML dumps and generated files are written at once.
- **`gal2cpp` appears twice** in a run with a post part. The second is skipped.
- **`cpp2xml` and `post_cpp2post_xml` have empty jobs.** Their work is the printing done by `execute_transform`.
- **The XML is printed more than once.** `xml2saxon` prints the language XML again to feed Saxon, after `cpp2xml` printed it for `lang-wizard.xml`.
- **Two XML flavors** from one printer: `<language>` keeps labels, templates and wizard marks; `<compiled>` has none of them.
- **A wizard statement is not in XML**, and the executed command moves to the **top** of its chunk as comments.
- **Only `once` and `local` are tag modes**; `own` is a version mode only.
- **Errors on a worker** need `capture_or_rethrow`. A guard in the caller is lost.
- **`write` is text mode, `read` is binary.** On Windows a bare `\n` becomes `\r\n` on write.
- **One translation at a time per process.** Several things are global (see [Architecture](architecture.md#state-that-is-global-to-a-process)).

## Leftovers and duplicates

- `xml2cpp` (pugixml) is **dead code**, a line-for-line twin of `xml2cpp_saxon`. So are `layout::fingerprint` and `node.cpp::fingerprint`: the pair must stay equal for the same XML.
- `prepare_prod_transforms()` and `prepare_testing_transforms()` are two ways to build the list. A change to the sequence has to be checked in both.
- `entity_et::TAG_LABELS` has no variant alternative. Labels of a tag are a list inside `tag_statement_t`.
- A comment in the aggregate version declaration header (`comment = "..."` on a non-root aggregate) is allowed by the grammar but **dropped** when parsing: only the status and the hash reach the builder.
- The history's grouping code (`group_of`, the `group` attribute) is not active: the list of marker tags is empty.
- `e_stacktrace_info` is declared and printed, but nothing constructs it unless you do.
- `use_named_channel` in `logging_utils` is exported and not used by the runtime path.
- `gal-functions.xsl` mixes general functions with ones written for the UUID example (`gal:next-uuid`, `gal:is-system`, `gal:is-payload`, `gal:structs`, `gal:payload-items`, `gal:dictionary-entry`).
- Namespaces: part of the runtime is in `galimatron::executable::filesystem[_decorator]`.
- The three `dynamic` elements of the XML (label value, wizard copy marker, wizard-made entity marker) share a name.
- `state/version_status.cpp` throws with the `wizard` subdomain for an unknown status, which is probably a copy of a neighbor.
- `explains.cpp` depends on the exact English text of ANTLR messages.
- Two rows of `explains.cpp` contain the literal input of a test (`version_number;`), so the friendly text for "a tag needs a value" fires only for a tag whose first token is that word.

## Case and paths

- Names compare **with** case in some places (`aggregate_container::by_name`, `is_aggregate_names_unique`, `chunk_path_exists`) and **without** in others (`ordering_link_container`, `name_already_listed`, `command_file_is_the_aggregate`).
- The `cpp2gal/template_engine` fixtures use the folder names `incoming-gal` and `expected-gal` (with a hyphen), unlike the rest (`incoming_gal`). Their `protocol.gal` files are pinned to `eol=crlf` because the slice records a chunk end as a byte index that counts CR.
- On Linux a name that differs only in case between `actual_gal` and `expected-gal` fails the comparison.

## Paths and confinement

- The decorator does not check that a relative `..` path stays inside its place. Absolute paths from a user xslt bypass it. `galimatron_summary.xml` and `taskflow.dot` are written directly.
- `merge_paths` and `apply_log_config` throw `std::runtime_error`, not LEAF, so they print with the "no domain" warning.

## Documentation of the code that is out of date

- `cpack.cmake` says `catalog.xml` and `gal-functions.xsl` share `share/galimatron`; the xsl is in `share/galimatron/xslt/`.
- The `serialize()` comment in `xml2xml_impl.hpp` (XML declaration and indentation) does not match its body.
- The `expected-files` skill names `no_xslt` as the only log oracle; `xslt_catalog` is one too. The `log-subsystems` and `test-gal` skills name files that are not in the tree (`examples/mqtt/log.cfg`, `translator_library/uuid_protocol`).
