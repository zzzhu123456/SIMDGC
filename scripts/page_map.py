import json
import re
from collections import OrderedDict

pages = [json.loads(l) for l in open("data/main_pages.jsonl", encoding="utf-8")]

HDR = re.compile(r"^第\s?([0-9]+(?:\.[0-9]+)?)\s?(部分|章)\s*[–\-—]?\s*(.*)$")

ranges = []
for p in pages:
    hdr = None
    for line in p["text"].splitlines()[:6]:
        s = line.strip()
        m = HDR.match(s)
        if m:
            hdr = s
            break
    key = hdr or "(无页眉)"
    if ranges and ranges[-1][0] == key:
        ranges[-1][2] = p["page"]
    else:
        ranges.append([key, p["page"], p["page"]])

print("total ranges:", len(ranges))
for key, a, b in ranges:
    print("  p%-5d-p%-5d (%4d pp)  %s" % (a, b, b - a + 1, key))