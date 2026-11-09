# Ordering

Files have no order. Aggregates are separate files, found by name. Generated code often needs an order anyway: an enumeration before the struct that uses it, a base type before a derived one, a table before the tables that refer to it.

An **ordering** says it in the data.

```
ordering precedes = { Item, Pong }, { Pong, Ping };
```

An ordering is a statement of the **root** aggregate. It has a name and one or more parts. A part is a chain: each name comes before the next one.

![Ordering ranks](images/16_ordering.svg)

## From chains to ranks

Galimatron turns the chains into a **rank** for every aggregate: the length of the longest chain of predecessors. `Item` has none, so its rank is 0. `Pong` follows `Item`, rank 1. `Ping` follows `Pong`, rank 2.

The rank is written into the compiled XML. Each aggregate version carries its rank in an `orderings` element:

```xml
<orderings>
    <ordering name="precedes" index="1"/>
</orderings>
```

Your post XSLT sort by it:

```xml
<xsl:for-each select="$items">
    <xsl:sort select="xs:integer(orderings/ordering[@name = 'precedes']/@index)" data-type="number"/>
    ...
</xsl:for-each>
```

The [UUID protocol](uuid-protocol.md) does exactly that: the ordering `enum_precedes_struct` puts the enumeration `sea_state_enum` before the struct `fog` that uses it, so the generated header compiles.

An aggregate that no part names gets a rank after the named ones. Your XSLT should decide what to do with such an item. The UUID protocol gives it a very large number, so a version without the ordering stays sorted by name.

## What is checked

An ordering must be a **strict weak order**:

- If two names have different ranks, a chain must connect them. Otherwise the ordering says "A is before B" with nothing to support it, and Galimatron rejects it and names the pair.
- A cycle (`A` before `B` before `A`) is rejected, and the message names it.

Names in an ordering must be aggregates that are present in that version. `wizard delete aggregate` refuses to remove an aggregate that a version's ordering still names. Remove the name from the ordering first.

## Writing an ordering

```
ordering precedes = { Item, Pong };
```

in the root version, or

```
wizard create ordering protocol precedes = { Item, Pong };
```

(`protocol` is the root aggregate here.) A later statement of the same ordering name in a later version replaces the earlier one. An ordering cannot be deleted.

!!! note
    The [benchmark](benchmark.md) rewrites the ordering of its root in every new version, with every aggregate named in it, to measure the cost.
