"""One-off relabeling of the user diagrams: lowercase aggregate names, no "protocol", no C++, "Wizard" as a concept."""
import os
import re

DRAWIO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drawio"))

# (file, [(old, new), ...]) exact text replacements
EXACT = {
    "01_one_description.drawio": [
        ("message list&lt;br&gt;(wiki page)", "product list&lt;br&gt;(wiki page)"),
        ('value="C++ structs"', 'value="source code"'),
        ('value="protocol docs"', 'value="documentation"'),
    ],
    "02_history_in_data.drawio": [
        ("protocol.json", "shop.json"),
        ("protocol.gal", "shop.gal"),
    ],
    "03_run_pipeline.drawio": [
        ("3 wizard&lt;br&gt;", "3 Wizard&lt;br&gt;"),
    ],
    "04_folders.drawio": [
        ("You write them, the wizard writes them", "You write them, the Wizard writes them"),
    ],
    "15_dynamic_label.drawio": [
        ("The next-uuid step of the UUID protocol example does exactly that.", "The next-uuid step of the messages example does exactly that."),
    ],
    "16_ordering.drawio": [
        ("ordering precedes = { Item, Pong }, { Pong, Ping };", "ordering shelf = { apple, pear }, { pear, plum };"),
        ('id="i" value="Item"', 'id="i" value="apple"'),
        ('id="po" value="Pong"', 'id="po" value="pear"'),
        ('id="pi" value="Ping"', 'id="pi" value="plum"'),
        ('value="rank 0"', 'value="position 0"'),
        ('value="rank 1"', 'value="position 1"'),
        ('value="rank 2"', 'value="position 2"'),
        ('value="precedes"', 'value="before"'),
        ("The rank is the length of the longest chain of predecessors. An XSLT sorts by it. If two names have different ranks, a chain must connect them; otherwise the ordering is rejected as not a strict weak order. A cycle is rejected too.",
         "Each aggregate gets a position. It comes after everything that precedes it in a chain; aggregates that no chain separates keep the default order. An XSLT sorts by it. If two names get different positions, a chain must connect them; otherwise the ordering is rejected as not a strict weak order. A cycle is rejected too."),
    ],
    "18_alias.drawio": [
        ("generated_dto/v6/v6.hpp", "generated_sql/v6/schema.sql"),
        ("generated-dto", "generated-sql"),
    ],
    "21_diagnostics.drawio": [
        ("after the wizard", "after the Wizard"),
    ],
    "22_uuid_steps.drawio": [
        ("and the C++ code written by hand", "and the code written by hand"),
    ],
}

# whole-word replacements in several files
WORDS = {
    "05_two_views.drawio": [("Apple", "apple"), ("Pear", "pear")],
    "07_gal_file_anatomy.drawio": [("Apple", "apple")],
    "11_hash.drawio": [("Apple", "apple")],
}

for name in sorted(set(EXACT) | set(WORDS)):
    path = os.path.join(DRAWIO, name)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    changed = 0
    for old, new in EXACT.get(name, []):
        n = text.count(old)
        if n == 0:
            print("  NOT FOUND in", name, ":", old[:60])
        changed += n
        text = text.replace(old, new)
    for old, new in WORDS.get(name, []):
        text, n = re.subn(r"\b%s\b" % old, new, text)
        changed += n
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(name, changed)
