# Generating text

A post XSLT often has to write a file in some format: C++, HTML, Markdown, JSON. Writing that text with `xsl:text` and `xsl:value-of` inside the XSLT mixes two things: the *logic* (which aggregates, which order) and the *text* (the shape of a struct). The text gets hard to read, and a change of formatting means a change of logic.

The recommended way is to keep the text in an **XML template** and let the XSLT fill it.

The text can be in any language or format. The examples below produce HTML and C++, but a template for Java, SQL, JSON or a configuration file works the same way. Galimatron does not know or care what is inside.

## A template file

A template is a small XML file. Its text is copied as it is, and elements in the `code` namespace are marks that the XSLT fills in.

`xslt/templates/page.xml` (from the `galimatron_hello` project):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<code:template xmlns:code="galimatron-code-generation">
<html>
<head>
<title>Galimatron</title>
</head>
<body>
<p>Counter: <code:counter/></p>
<p><code:greetings/></p>
</body>
</html>
</code:template>
```

`<code:counter/>` is a hole. The XSLT knows the value and puts it there.

A template for C++, from the UUID protocol:

```xml
<code:template xmlns:code="galimatron-code-generation">
struct <code:struct-name/>
{
<code:hpp-fields/>};
<code:when-uuid>uuid_t get_uuid(std::type_identity &lt;<code:struct-name/>&gt;);
void handle_client(const <code:struct-name/>&amp;, const any_state_t &amp;);
</code:when-uuid>
</code:template>
```

You can read the generated shape directly. `<code:hpp-fields/>` is a hole that the XSLT fills with a list. `<code:when-uuid>` keeps its content only when the struct has a uuid.

## The XSLT that fills it

The simplest filler is short:

```xml
<!-- the values the page needs -->
<xsl:variable name="version" select="(//root-aggregate-version-definition)[1]"/>

<xsl:result-document href="@@page@@hello.html@@" method="html" html-version="5">
    <xsl:apply-templates select="document('templates/page.xml')" mode="page">
        <xsl:with-param name="ctx" tunnel="yes" select="map {
            'counter': string(gal:tagvalue($version, 'counter')),
            'greetings': string(gal:tagvalue($version, 'greetings'))
        }"/>
    </xsl:apply-templates>
</xsl:result-document>

<!-- a code:* mark is replaced by the value of that name -->
<xsl:template match="code:*" mode="page">
    <xsl:param name="ctx" as="map(xs:string, xs:string)" tunnel="yes"/>
    <xsl:value-of select="$ctx(local-name())"/>
</xsl:template>
```

The idea:

1. `document('templates/page.xml')` loads the template. The path is relative to the XSLT folder.
2. `apply-templates` walks it. Text and ordinary elements are copied. A `code:*` element is matched by a template of yours.
3. The values travel as a **map** in a tunnel parameter, so every template down the tree can read them.
4. A mark whose name is a value in the map is replaced. A mark that is a list (like `hpp-fields`) gets a template of its own, which loops over the tags and writes the lines.

`gal:ctx($version, ('struct-name', 'uuid'))` builds such a map from the tags of a version. A hyphen in the mark name is an underscore in the tag name.

## Why this way

- **Readable.** The template looks like the output. A person who knows C++ and not XSLT can edit it.
- **Separate.** Change the formatting in the template and leave the logic. Change the logic and leave the formatting.
- **Checked.** The template is XML, so a missing closing mark is an error when the XSLT loads it.
- **Reusable.** The same marks, the same templates, in many generators.

## Escaping

A template is XML, so `<`, `>` and `&` in the output must be written as `&lt;`, `&gt;` and `&amp;`. Set `replace-escaped-form-to-original-symbols` to `true` in the `other-files` entry for the generated folder, and Galimatron turns them back when it writes the file. The [`gal.cfg` of the UUID protocol](configuration.md#where-your-xslt-may-write) does this for `.hpp` and `.cpp`, and leaves it `false` for `.html` and `.md`.

!!! note
    The `code` namespace and the mark names are a convention used by the examples. Galimatron does not interpret them. Your XSLT decides what each mark means.

## Strings inside tags

A string in a tag can also be a template. A string followed by `_te` replaces `{{name}}` with the value of the tag `name` in the same version, when the data is compiled. See [Tags](tags.md#template-strings). Use `_te` for a sentence inside the data, and an XML template for a whole file.
