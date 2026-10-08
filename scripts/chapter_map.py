import json
import re

pages = [json.loads(l) for l in open("data/main_pages.jsonl", encoding="utf-8")]

CHAP = re.compile(r"^第\s?(\d+\.\d+)\s?章\s*[–\-—]?\s*(.*)$")
PART = re.compile(r"^第\s?(\d)\s?部分\s*[–\-—]?\s*(.*)$")

recs = []
for p in pages:
    chap = part = None
    for line in p["text"].splitlines()[:6]:
        s = line.strip()
        if chap is None:
            m = CHAP.match(s)
            if m:
                chap = ("第%s章" % m.group(1), m.group(2).strip())
                continue
        if part is None:
            m = PART.match(s)
            if m:
                part = ("第%s部分" % m.group(1), m.group(2).strip())
                continue
    recs.append({"page": p["page"], "chap": chap, "part": part})

# forward-fill chapter
cur = None
for r in recs:
    if r["chap"]:
        cur = r["chap"]
    r["chap_filled"] = cur
# backward-fill for the front matter
nxt = None
for r in reversed(recs):
    if r["chap_filled"]:
        nxt = r["chap_filled"]
    else:
        r["chap_filled"] = nxt

curp = None
for r in recs:
    if r["part"]:
        curp = r["part"]
    r["part_filled"] = curp

ranges = []
for r in recs:
    key = r["chap_filled"]
    if ranges and ranges[-1][0] == key:
        ranges[-1][2] = r["page"]
    else:
        ranges.append([key, r["page"], r["page"]])

print("chapter ranges:", len(ranges))
big = 0
for key, a, b in ranges:
    n = b - a + 1
    big += n
    flag = "   <== BIG" if n >= 20 else ""
    print("  p%-5d-p%-5d (%4d pp)  %s%s" % (a, b, n, key[0] if key else "?", flag))
print("sum pages:", big)