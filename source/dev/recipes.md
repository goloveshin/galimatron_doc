# Recipes

Each recipe lists the places you have to touch. Run CMake again after you add a file, and run `run_tests` before you finish.

## Add a Wizard command

1. **Grammar**: `parser/g_parser.g4`, a new `wizardCommand...` rule, and a keyword in `g_lexer.g4` if you need one.
2. **Model**: `state/wizard/command.hpp`: a value in `command_et`, a block comment (syntax, context, examples), and an entry in the `entities_t` and `commands_t` tables (the four `static_assert`s fail until the table is consistent). Data goes in `data.hpp`, messages in `tags.hpp`.
3. **Parse**: `transforms/gal2cpp/detail/wizard.cpp`: build the command data (`command_of`, `json_of`).
4. **Codes**: new `WIZARD_<COMMAND>_...` values in `validation_error_code_et` (`common_library/exception_declaration.hpp`).
5. **Checks**: functions in `cpp2cpp_validate/detail/wizard/wizard_*.cpp`, declared in `cpp2cpp_validate.hpp`, and a call in the dispatcher `may_execute_wizard_command()` in `wizard_root.cpp`. Decide the **closed-version** behavior ([table](validate-wizard.md#closed-versions)).
6. **Execution**: `apply_wizard_<command>` in `cpp2cpp_wizard/detail/*.cpp`, declared in `cpp2cpp_wizard_impl.hpp`, a case in `apply_one`. Start with `validate_->may_execute_wizard_command()`. Call `refresh_live_and_hashed` after structural edits.
7. **Batch**: decide whether it may be in a batch (`is_wizard_batch_command_create`).
8. **Tests**: a `test_wizard_<command>.cpp` and fixtures with `// good` and `// bad` lines. Also the `validate` area if a check is new.
9. **Docs**: [The Wizard](../wizard.md), and this guide if the rules change.

## Add a validation check

1. A member in `cpp2cpp_validate.hpp`, implemented in `structure.cpp` or `hash.cpp`.
2. A task in `build()` (`build.cpp`) with its edges. A check that needs a trusted root must run after `is root aggregate single`. If it is skipped for `create root aggregate`, follow `skip_root_checks`.
3. A code in `validation_error_code_et`, and `fail(code, message, where)`. Remember that checks run in parallel, so do not make two checks report the same fault.
4. A case in `test_data/translator_library/validate/` with `// good` and `// bad` marks, and a `SUBCASE` in `test_validate.cpp`.

## Add an error or a code

1. The type or the value in `exception_declaration.hpp`. A new mark or payload also needs a `const T*` in `spy_handler_t::operator()` (`runtime_library/leaf_spy/leaf_spy.hpp`), or the printer will not load it.
2. Throw with `leaf::throw_exception` and put the full text in `e_what_info`. Attach the path through `report_path`.
3. A test with `print_leaf_exception`.

## Add a log subsystem

1. A `const char*` in `global/common_library/log_subsystems.hpp` with `brief:` and `part:` comments.
2. The same id in `subsystems.allowed` of **every** `log.cfg` (the repository's tests, examples, and the user-facing docs).
3. In the `.cpp`: `Logme::SID SUBSID = Logme::SID::Build(global::log_subsystems::<id>);`.

## Add a `gal.cfg` key

1. The field in the struct (`translator_library/galimatron_config_declaration.hpp`) and the key name in `runtime_library/galimatron_config/detail/galimatron_config_tags.hpp`.
2. `from_json` and `to_json` in `galimatron_config.cpp`. If the value is a path, decide which of the three passes corrects it.
3. Use it in `translate_by_config.cpp`.
4. Tests in `test_galimatron_config.cpp` and `test_galimatron_config_tags.cpp`.
5. [Configuration](../configuration.md) and [Reference](../reference.md).

## Add a built-in step

1. A factory `translator_t::get_<name>_transform()` in `translator/detail/transforms/<name>.cpp`, declared in `translator_impl.hpp`, with the domain and state types, a name constant in `builtin_transform_name.hpp`, and, if it prints XML, a file name and description in `builtin_transform_xml.hpp`.
2. Decide: **seed** (it must run in a fixed place; add it in `prepare_prod_transforms`) or **catalog** (the builder inserts it between representations; add it to the catalog and, if the run needs it, to the list in `check_state_transforms`).
3. Add it to `prepare_testing_transforms()` and to `testing_t` if a slice test should run it.
4. A job that may throw on a worker: wrap it in `capture_or_rethrow`.
5. `test_transform_sequence_builder.cpp`, and the maps and docs ([The pipeline](pipeline.md), the diagram in `drawio/31_dev_pipeline_map.drawio`).

## Add a construct to the language

1. Grammar (`g_parser.g4`), and the `explains.cpp` table if there is a common mistake.
2. `state/entity/entity.hpp`: the struct, the `entity_et` value, the variant alternative. `builder.{hpp,cpp}` and `detail/<entity>.cpp`: a `create_*` that also registers in the containers.
3. `gal2cpp`: the listener events. Keep source text and comments (`assign_user_comments`).
4. `cpp2gal`: print it, honoring `user_formatting`.
5. XML: the names in `state/gal_and_xml_tags.hpp`, `cpp2xml/detail/<entity>.cpp`, `xml2cpp_saxon` (and, to keep the pair in sync, `xml2cpp`), and the fingerprints (`layout::fingerprint`, `node.cpp::fingerprint`).
6. Validator and compiler: structure checks, `cpp2post_cpp` merge and compile, the history, the seal's `definition_payload` (`vertex_payload`), and `content_hash` if values must be hashed.
7. Tests: `parser/test_data` for the grammar, a `cpp2gal` slice, `cpp2post_cpp` cases, a round-trip product test.
8. Docs: [Entities](../entities.md) and the language pages.

## Add a function to `gal-functions.xsl`

Follow the `xslt` skill: namespace `gal`, a typed signature, a comment saying which XML (language or compiled) it reads. A function that is only for the UUID example belongs with the others of that group. Test it through a product case that uses it.

## Add a test case

1. A folder under `test_data/translator_library/<area>/<case>/` with `incoming_gal/`, and the oracles (`expected-gal`, `expected-xml`, and `expected-xml-windows` only where the print differs).
2. Do **not** copy `gal.cfg`, `log.cfg` or `xslt/config.xml` if the common ones fit: add the case to the list in `galimatron/tests/CMakeLists.txt` instead.
3. A `SUBCASE` calling `translate_production` (or `translate_slice`) and `compare_directories`. No byte-level file work.
4. Mark `.gal` fixtures with `// good` and `// bad`.

## Change a diagram

The `.drawio` files in `drawio/` are the source; the `.svg` files in `source/images/` are generated by `export_drawio.ps1`. The big map (`31_dev_pipeline_map.drawio`) and a few of the developer diagrams are written by the scripts in `tools/drawio_gen/`; edit the script and run it, rather than moving boxes by hand.
