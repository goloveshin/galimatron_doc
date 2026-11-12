# Tags

A tag is a name with values. Everything you describe is a tag. The language does not know "integer", "message" or "price". It knows names and values, and your XSLT decide what they mean.

```
price = { "3" };
```

The tag `price` has one value, the string `3`. All values are text, even a number. Your XSLT convert it when they need a number.

## Values

A tag has a list of values in `{ }`. Each value is a string, a record, or an array.

```
empty      = { };
currency   = { "EUR" };
two        = { "int", "price" };
shape      = { { "k": "v", "n": ["a", "b"] }, "plain" };
```

| Value | Written as | In the compiled XML |
|---|---|---|
| string | `"text"`, `'text'`, `R"(text)"` | `<string>` |
| record | `{ "key": value, ... }` | `<record>` with `<key>` |
| array | `[ value, ... ]` | `<array>` |

A raw string `R"(...)"` takes every character as it is, including quotes and new lines, so it fits a block of code or markup. `R"--(...)--"` allows `)"` inside.

## A tag with no name of its own

A name is optional. A tag can be written with labels only:

```
field important { "int", "price" };
```

This tag has no name that you typed. A [label](labels.md) can name it from one of its values (`tag-name-from`). Here the value labeled `name` is `price`, so the tag is called `price`.

The reason: a generator wants a list of *fields*, and wants to find a field by its name. You do not want to invent a tag name for each field, and you do not want the name to be written twice.

## Labels in front of the values

Words before the values are labels:

```
version_number = important { "2" };
field important { "text", "message" };
```

`important` is built in. It marks the values that [hashes](hashes.md) cover. `field` is a label that you declared (see [Labels](labels.md)). A tag may have several.

## Important

An `important` tag is part of the identity of a version. Its values are summed into the hash that closes the version. A tag without `important` can change in a closed version without breaking the hash. Use `important` for what you publish, and nothing else.

```
uuid = need_new_uuid important { "6f1e0001-0000-4000-8000-000000000001" };
version_namespace = { "v2" };
```

Here `uuid` is part of the published identity. `version_namespace` is not marked, so a later fix of it will not break the hash.

## Tag modes: once and local

By default a tag stays: version 1 sees what version 0 wrote. A **tag mode** limits where one tag lives.

```
published = once important { };
```

| Mode | Lives in | Flows from the root to the aggregates |
|---|---|---|
| (none) | its version and all later versions | yes |
| `once` | its version only | yes, in the same version |
| `local` | its version only | no |

`once` is the right mode for a fact about one version: this version is published. Written in the root, it marks every aggregate of that version, and does not leak into the next one. In the [Example: messages that grow](example-messages.md) every version restates `published = once important { }`.

`local` is for a fact about this file: a note for the person who reads the aggregate, a switch that the other aggregates must not inherit.

## Deleting a tag

```
delete price;
```

The tag is absent from this version on. An earlier version still has it, and a later version may write it again. `wizard delete tag apple price` writes this for you. See [The Wizard](wizard.md).

## Template strings

A string followed by `_te` is a template. The compiled value is the string with `{{name}}` replaced by the value of the tag `name` in the same version:

```
station = { "North Light" };
greeting = { "{{station}} on watch"_te };
```

The `.gal` file keeps `{{station}}`. The compiled XML holds `North Light on watch`. Use it for a text that quotes another value, so the value is written once.

!!! note
    `_te` renders a string inside the data. A template for a whole generated file is another feature: see [Generating text](templates.md).
