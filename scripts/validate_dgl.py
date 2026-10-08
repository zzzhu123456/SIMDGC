import json
import re

recs = json.load(open("data/dgl.json", encoding="utf-8"))
pages = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/main_pages.jsonl", encoding="utf-8")}

# independent count: a row terminator is a line containing exactly a 4-digit UN number
term = 0
per_page = {}
for pno in range(843, 1147):
    c = sum(1 for line in pages[pno].splitlines() if re.fullmatch(r"\d{4}", line.strip()))
    per_page[pno] = c
    term += c
print("row terminators (843-1146):", term)

from collections import Counter
cnt = Counter(r["page"] for r in recs)
print("records by first page:", sum(cnt.values()))
diff = [(p, per_page.get(p, 0), cnt.get(p, 0)) for p in range(843, 1147) if per_page.get(p, 0) != cnt.get(p, 0)]
print("pages where terminator count != record count:", len(diff))
print(diff[:25])

print("\nunique UN:", len({r["un"] for r in recs}))
print("\n--- spot checks ---")
want = {"1203", "1263", "3480", "3481", "3082", "1005", "1993", "1835", "3560", "3559", "0004", "1352"}
for r in recs:
    if r["un"] in want:
        print("UN %s p%s | %s | cls=%s sub=%s pg=%s sp=%s | ems=%s stow=%s seg=%s" % (
            r["un"], r["page"], r["psn"].replace("\n", "")[:34], r["cls"], r["sub"], r["pg"],
            r["sp"].replace("\n", "/")[:18], r["ems"], r["stow"].replace("\n", "/")[:14], r["seg"].replace("\n", "/")[:18]))