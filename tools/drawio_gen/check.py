import sys, re
import xml.dom.minidom as m
path = sys.argv[1]
doc = m.parse(path)
print("xml ok, cells:", len(doc.getElementsByTagName("mxCell")))
t = open(path, encoding="utf-8").read()
print(re.search(r'pageWidth="(\d+)" pageHeight="(\d+)"', t).groups())
# every edge source/target must exist
ids = set(re.findall(r'<mxCell id="([^"]+)"', t))
bad = [(s, tg) for s, tg in re.findall(r'source="([^"]+)" target="([^"]+)"', t) if s not in ids or tg not in ids]
print("bad edges:", bad[:5], len(bad))
