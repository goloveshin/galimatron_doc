# Parsing and printing

The text of a `.gal` file becomes graph vertices in `gal2cpp`, and the graph becomes text again in `cpp2gal`. A file must survive that round trip with its comments and its formatting, because Galimatron rewrites the files you edit.

Code: `translator_library/parser/` (the grammar and the ANTLR session), `transforms/gal2cpp/`, `transforms/cpp2gal/`.

## The grammar

`parser/g_lexer.g4`, `parser/g_parser.g4`. ANTLR 4, C++ target, namespace `galimatron`, listener on, visitor off.

### Lexer

- Keywords: `root aggregate versions version before label static dynamic tag tag-name-from once local own ordering comment hash deleted delete wizard create in copy to continue physically force collapse`.
- Punctuation: `: ; { } ( ) [ ] = . , - < >`.
- `IDENTIFIER` is `[A-Za-z][A-Za-z0-9_]*`. The lexer also exposes `identifier_pattern`, the same text as a constant. ANTLR cannot use a constant inside a rule, so the pattern is written twice; `cpp2post_cpp/detail/naming.cpp` uses the constant to check a tag name that comes from a label. That is why `CMakeLists.txt` makes `naming.cpp` depend on the generated `g_lexer.h`.
- Comments (`//` and `/* */`) go to a hidden channel named `COMMENTS`. White space is skipped.
- `TEMPLATE_ENGINE` is the literal `_te`, the suffix of a template string.
- **Strings** can be `'..'`, `".."`, or raw: `R"(...)"` and `R"-(...)-"` with any number of dashes. An embedded action `remember_string_lexeme()` splits the lexeme into `{raw, quote, dashes, value}`, stores it by token start index, and sets the token text to the **unquoted** value. The original quoting is recovered with `lexer.string_lexeme_at(startIndex)` and becomes a `string_delimiter_t` in the state.

### Parser

- Entry points: `productionEntryPoint : chunk EOF`, and `testStringEntryPoint : STRING EOF` (unit tests).
- **A file is a "chunk"**: Wizard statements only, or one aggregate (root or ordinary), or nothing. So a file holds exactly one aggregate, and a Wizard file holds no aggregate.
- An aggregate is its name, a `versions { ... }` list (the **declarations**) and, after it, any number of `version [mode] N { ... }` bodies (the **definitions**) or `version [mode] before N { ... }` (parked bodies). Declaration headers use semantic predicates, so `comment` and `hash` each appear at most once.
- A root version body may hold tags, labels, orderings and operations. A non-root one holds no orderings.
- Tags: `[name =] [once|local] label* { values } ;`. Values are strings (optionally `_te`), records `{ "k": v }` and arrays `[ ... ]`. The label `important` is not special in the grammar.
- Labels: `label x = static { a, b }` with an optional `, tag-name-from { a }`, and `label x = dynamic { id }`.
- Orderings: `ordering name = { A, B }, { C, D };` (each part needs at least two names).
- Operations: `delete;` (the version) and `delete tag_name;`.
- Wizard: `wizard <command>;` and `wizard { <command>; ... }`. The commands are listed in [The validator and the Wizard](validate-wizard.md#the-wizard-step).
- Modes: `tagMode` is `once` or `local`; `versionMode` is `once`, `local` or `own`.

### `parser::state_t`

An ANTLR session that is also the error listener. It owns the streams, the lexer, the parser and the tree. The constructor replaces the default error listeners with itself, sets the prediction mode to `LL_EXACT_AMBIG_DETECTION`, and `syntaxError` **throws** `antlr4::ParseCancellationException`. For a parser error it first asks `explains::explain(rule_stack, message)` for a friendlier text.

`ParseCancellationException` is **not** a LEAF exception. The `leaf_spy` printer has a special case for it, and the parser tests expect it.

`parser.cpp` has `parse(content)`, `parse(gal_version, content)` and `walk(state, listener)`. A parse state travels as a `std::any` that holds `shared_ptr<state_t>`, so the tree lives as long as the `any`.

### `explains.cpp`

A table of `{rule, ANTLR message, friendly text}`: "a version cannot come before its aggregate", "a root aggregate and an aggregate cannot share a file", "an ordering part needs at least two names", "a label cannot be static and dynamic at the same time", and so on. `explain` walks the rule invocation stack from the innermost rule outward and uses the first rule that is in the table; a known rule keeps its own sentence. The table compares the exact English text of ANTLR, so a new version of ANTLR can silently turn a friendly message back into the raw one.

### `gal_version`

`gal.version` is an optional file in the input folder with a positive integer. `from_input_dir` returns `current` (1) if it is missing. `require_supported` throws `unknown GaL version: N` for anything else. Today there is one parser; the number is the hook for a second.

## `fill_state_from_content`

A type-erased driver (`parser/fill_state_from_content.{hpp,cpp}`): for each `(path, deferred content)` it calls `parse_content`, then `get_listener`, then `walk`. It sets `augment_domain(translator_library, parser)` and `augment_path(file.path)` around each file, so every error carries the file. The only production caller is `gal2cpp`.

## `gal2cpp`

`transforms/gal2cpp/gal2cpp.cpp`, `detail/listener.{hpp,cpp}`. `translate({gal_state, gal_version})` creates a `language_part_t`, a `builder_t` over it, an `aggregate_index = 0` shared by all files, and calls `fill_state_from_content` with a `listener_t` per file.

`listener_t : g_parserBaseListener` keeps a stack of parent descriptors and counters: `aggregate_index` (the order in which files were scanned becomes the `index` of non-root aggregates, and the validator requires `0..n-1`), `entity_index_in_version_`, `entity_index_in_versions_`, `tag_value_level_`, `tag_value_index_`, and the current `tag_statement_`.

| Parse event | What it does |
|---|---|
| `enterChunk` | `create_chunk` with the path; push it. `exitChunk` clears the current aggregate |
| `enterRootAggregate`, `enterAggregate` | `create_*aggregate`; the aggregate gets `aggregate_index++` |
| `enter...VersionDeclaration` | the declaration with index, status, hash, comment |
| `enter...VersionDefinition` | the definition with index or owner, and mode; resets `entity_index_in_version_` |
| `exit...VersionDefinitions` | `bind_anonymous_owners` |
| `exitAggregateVersionDefinition` | `apply_aggregate_version_delete` |
| `enterTagStatement` | the tag with name, labels, mode |
| `enterTagJSON*` | values, records, key-values, arrays, strings. A zero-level string is also put in `string_values_at_zero_level` (the code has a note: the "1 and -1" arithmetic is ugly) |
| labels, orderings, operations | the matching `create_*` |
| `enterWizardCommand`, `enterWizardBatch` | one `wizard_statement_t`; a command inside a batch is not its own vertex; a tag inside a Wizard command does not create vertices but is stored as `Wizard::json_t` in the command data |

### Keeping the source text

`assign_user_comments(vd, ctx)` is called for each statement-like vertex:

- `user_formatting = original_user_formatting(ctx, stop_index)`: the exact source from the first token to the last, including a trailing comment on the same line (`statement_stop_index` extends over it). CRLF and CR are normalized to `\n`, so a text-mode write gives one platform line end.
- `user_comments = leading_user_comments(...)`: the comment-channel tokens to the left of the rule, except one that shares a line with the previous statement (that belongs to the previous statement).
- If a parent vertex starts at the same token and has the same comments, the parent's list is cleared and the **innermost** vertex keeps them, because that is the one `cpp2gal` prints.
- A Wizard statement gets the comments of the statement around it, because the command rule starts after `wizard` and stops before the `;`.

### Errors in `gal2cpp`

Only `wizard.cpp` throws: `wizard command is outside of a wizard context`, `unknown wizard command`, with LEAF `gal2cpp`. Syntax errors come from the parser. Everything about structure (versions, hashes, aggregates) is checked later by the validator, not by the listener.

## `cpp2gal`

`transforms/cpp2gal/cpp2gal.cpp`, `detail/cpp2gal_impl.cpp` and the printers. `cpp2gal_t` builds `std::deque<line_t>` (`{tab_count, content}`), with a stack of indents starting at `-8` so that the chunk level is 0, and `tab_size = 4`.

- `emit(vd)` is a `std::visit` over the entity. An unhandled entity throws `unexpected entity '...' in cpp2gal`.
- A chunk walks its children, joins the lines into one text, appends `\n`, and pushes `{content, path}`. A chunk without a path throws `chunk has no path`.
- An aggregate prints `aggregate NAME`, `{`, the declarations, `}`, and **after** the closing brace its version definitions (the `*_VERSION_DEFINITIONS` node is skipped by `walk_children` and emitted later). A blank line precedes each aggregate and each definition.
- Declarations print `N;`, `N = deleted;` or `N = { comment = '...', hash = '...' };`.
- A Wizard statement prints only its comments. The command itself is never printed back: that is how a command disappears from `console.gal` (see `comment_executed_command` in [The validator and the Wizard](validate-wizard.md)).

### The layout rules

1. **Stored source wins.** If a vertex has non-empty `user_formatting`, that text is printed as one line instead of generated text. This applies to tags, labels, operations and the declarations. A vertex that the Wizard or an xslt made has none, so it is generated.
2. Comments are printed above each vertex (`append_user_comments`).
3. **Orderings** are always generated (`ordering_printer_t`): one line if `indent + text <= 100` columns, otherwise broken like a tag. A trailing comment is kept: `append_statement_comment` finds the last `;` in the stored text and keeps a `//` or `/*` after it.
4. **Tags without stored text** (`tag_printer_t`): a one-line `{ ... }` body when every value is "flat" (a string, an array of strings, a record of strings) and it fits in 100 columns. Otherwise the header, then `{`, then each payload indented by 4 with commas, and `};`. A tag header is `[name =] [once|local] label1 label2 ...`.
5. **Strings** (`quote_text`): the original quote is used. If the delimiter was raw, or the text now contains the quote, a raw string `R"dashes(text)dashes"` is used with enough dashes that the closing sequence is not in the text. A template adds `_te`.
6. Output order is the adjacency order of the graph: nothing is sorted, so the builder must keep the parse order.

!!! note
    When an xslt changes a node, `xml2cpp_saxon` drops the stored text of that node (the fingerprint differs), and `cpp2gal` prints it fresh with rule 4. That is the only reason a node of yours may be re-formatted after a run. See [XML and Saxon](xml.md#the-layout-table).

### Errors in `cpp2gal`

All errors are `leaf::throw_exception(translator_library, cpp2gal, e_what_info{...})`, with `augment_domain` in scope.
