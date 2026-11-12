"""One-off vocabulary update of the user pages (not the developer guide):
the word "wizard" in prose becomes "Wizard" (code, links and fenced blocks are left alone), and the example page is renamed.
"""
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "source"))

PROTECT = re.compile(r"(`[^`]*`|\]\([^)]*\)|<[^>]*>|https?://\S+)")


def capitalize_wizard(line):
    parts = PROTECT.split(line)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(part)
        else:
            out.append(re.sub(r"\bwizard\b", "Wizard", part))
    return "".join(out)


def process(text):
    lines = text.split("\n")
    fenced = False
    result = []
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
            result.append(line)
            continue
        if fenced:
            result.append(line)
            continue
        line = capitalize_wizard(line)
        result.append(line)
    text = "\n".join(result)
    text = text.replace("uuid-protocol.md", "example-messages.md")
    text = text.replace("[UUID protocol]", "[Example: messages that grow]")
    text = text.replace("The UUID protocol", "The messages example")
    text = text.replace("the UUID protocol", "the messages example")
    text = text.replace("UUID Protocol", "messages example")
    text = text.replace("UUID protocol", "messages example")
    return text


for path in sorted(glob.glob(os.path.join(ROOT, "*.md"))):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    new = process(text)
    if new != text:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("updated", os.path.basename(path))
