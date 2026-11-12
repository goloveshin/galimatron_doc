# Conventions

The project writes its rules down as **skills** in `.cursor/skills/`. They are plain Markdown files that people and tools read before they change code. This page is a map of them, with the reason for each rule. When a rule here and a skill disagree, the skill wins; fix this page.

| Skill | Applies to |
|---|---|
| `coding-style` | every C++ change |
| `boost-string` | C++ that searches, splits or rewrites a string |
| `ranges` | C++ that maps, filters or sorts a collection |
| `exception-using` | every throw, catch, and exception type |
| `log-subsystems` | anything that logs |
| `content-hash` | hashes and `important` tags |
| `wizard-closed-version` | any Wizard command that writes |
| `xslt` | every `.xsl` file |
| `gal-cfg` | every `gal.cfg` |
| `test-gal` | `.gal` fixtures |
| `tests` | product and slice tests |
| `expected-files` | oracle files |

## Code style (`coding-style`)

- **Comments.** A comment above a function, class or struct ends with a blank `//` line. A `// testing:` line (`no`, `yes (unit)`, `will (unit)`) is a separate comment with a blank `//` before and after. A comment above `wizard {` in a `.gal` file ends with a blank `//` too, which is the form `comment_executed_command` produces.
- **Names.** The suffixes of [Architecture](architecture.md#naming); enumerators in SCREAMING_SNAKE; data members end with `_`; exception structs have no `_t`.
- **Includes.** Grouped, each group with a one-line comment (`// galimatron`, `// global`, `// Logme`, `// std`), written from the repository root. Standard headers come from the precompiled header only. `global` never includes `galimatron`.
- **Layout.** 4 spaces, braces on their own lines, `}// namespace x::y` to close a namespace, the closing `)` of a multi-line call or definition on its own line indented like the first line, designated initializers where they help, a space before `...` in a parameter pack.
- **Tests.** The suite name is the feature path; the case name is a short English phrase.
- **Scope.** Change only what the task needs.
- **MSVC.** The list in [Build, packaging, CI](build-ci.md#msvc-constraints).

## Strings (`boost-string`)

Use Boost.Algorithm for text: `boost::contains`, `starts_with`, `ends_with`, `replace_all`, `erase_all`, `trim`, `split` with `is_any_of`, `join`. Do not scan text with `find`, `rfind`, `find_first_of`, a `substr` loop, or `npos`. A line split first normalizes CRLF and CR to LF and drops one trailing newline. Map and set `find` are not strings and are left alone. Convert only the function you edit.

## Ranges (`ranges`)

A loop that only maps or filters into a container becomes a pipeline: `ranges::views::transform | ranges::views::filter | ranges::to<T>()`. Sort with `ranges::actions::sort` (`|=` on an lvalue, or continue a pipe), never `std::sort` or `std::ranges::sort`. Pass an lvalue into `views::transform`. A loop with side effects or an early return stays a loop.

## Errors (`exception-using`)

See [Errors, logging, crashes](errors-logging.md). In short: types only in `exception_declaration.hpp`; throw with `leaf::throw_exception` only inside `galimatron`; catch only through `galimatron::runtime::try_catch`; the full message in `e_what_info`; context through the `augment_*` guards, kept alive; on a worker, inside `capture_or_rethrow`; in tests, `print_leaf_exception`.

## Logging (`log-subsystems`)

One `Logme::SID SUBSID = Logme::SID::Build(global::log_subsystems::<id>)` per `.cpp` that logs, alone in its anonymous namespace. A new id needs `brief:` and `part:` comments in `log_subsystems.hpp` and an entry in `subsystems.allowed` of **every** `log.cfg` in the repository.

## Hashes (`content-hash`)

A version hash covers only the values of tags marked `important`. Aggregate names, labels, tag names, tag modes and paths are out. Each live aggregate stores a content hash; the root stores `hash_of_hashes` over the sorted hashes, deleted declarations excluded. `create hash ... force` and `delete hash ... force` skip the "does not match" and "absent" checks for the named versions. A user xslt must not rewrite a stored hash, and the language is validated again after it. See [Hashes and the seal](seal-hash.md).

## Closed versions (`wizard-closed-version`)

A closed version is a root version at or before the last hashed declaration. Every Wizard command that writes into a version must say what it does with a closed one. The table is in [The validator and the Wizard](validate-wizard.md#closed-versions); check a new command against it.

## xslt (`xslt`)

- Say "xslt", not "stylesheet". The processor is SaxonC-HE 13; write `version="3.0"`.
- Prefer an XML template for generated text (`templates/<name>.xml`, root `code:template` in the namespace `galimatron-code-generation`). The code and the text stay apart; see [Generating text](../templates.md).
- Reuse and extend `gal-functions.xsl` instead of writing the same paths in each file.
- Put a function call in a **predicate**, not as the whole `match`.
- Remember the two XML flavors: the language XML has labels and `label-refs`; the compiled XML has label values as attributes.

## Configuration (`gal-cfg`)

A `gal.cfg` names its folders `incoming_gal/`, `actual_gal/`, `actual_xml/`, `intermediate/` and `actual_summary/`. `intermediate/` is for scratch. `actual_xml/`, `actual_summary/` and `actual_log/` are used when those results are kept or compared: a test config compares XML and summary but leaves the log in `intermediate/`; an example that compares nothing keeps all three in `intermediate/`.

## Tests

- `// good` and `// bad` marks in automated `.gal` fixtures (`test-gal`).
- Product and slice tests never touch file bytes (`tests`).
- Oracle files hold no absolute path (`expected-files`).

See [Testing](testing.md).

## How a change is made

Small, one purpose, with the skills open. A change to the language touches the grammar, the parser listener, the builder, the printers (`cpp2gal`, `cpp2xml`, `xml2cpp_saxon` and, if you keep it in sync, `xml2cpp`), the validator or the compiler, the tests, and these docs. [Recipes](recipes.md) lists those places for the common changes.
