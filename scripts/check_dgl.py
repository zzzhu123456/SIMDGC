import json
from collections import Counter
import re

recs = json.load(open("data/dgl.json", encoding="utf-8"))
print("records:", len(recs), "unique UN:", len({r['un'] for r in recs}))
print("records spanning page break:", sum(1 for r in recs if len(r["pages"]) > 1))
print("records with un18 != un:", sum(1 for r in recs if r["un18"].strip() and r["un18"].strip() != r["un"]))
print("empty psn:", [(r["un"], r["page"]) for r in recs if not r["psn"].strip()][:5])
print("empty cls:", [(r["un"], r["page"]) for r in recs if not r["cls"].strip()][:5])
cls = Counter(r["cls"].strip() for r in recs)
print("class distribution:", cls.most_common(25))

print("\n--- spot checks ---")
for want in ("0004", "1005", "1203", "1263", "1352", "1835", "1993", "3082", "3480", "3559", "3560"):
    for r in recs:
        if r["un"] == want and r["page"] in (843, 867, 885, 890, 900, 958, 971, 1074, 1135, 1146):
            print("UN %s p%-4d | %-30s | cls=%-4s sub=%-4s pg=%-3s sp=%-16s lq=%-4s eq=%-3s pkg=%-7s ems=%-8s stow=%-6s seg=%s" % (
                r["un"], r["page"], r["psn"].replace("\n", "")[:30], r["cls"], r["sub"], r["pg"],
                r["sp"].replace("\n", "/")[:16], r["lq"], r["eq"], r["pkg"], r["ems"],
                r["stow"].replace("\n", "/")[:6], r["seg"].replace("\n", "/")[:16]))

print("\n--- a full record dump (UN 1352) ---")
for r in recs:
    if r["un"] == "1352" and r["page"] == 900:
        for k, v in r.items():
            print("  %-10s %s" % (k, str(v).replace("\n", " ⏎ ")[:150]))