import json
recs = json.load(open("data/dgl.json", encoding="utf-8"))
print("total:", len(recs))
for want in ("0004", "1005", "1203", "1263", "1352", "1835", "1993", "3082", "3480", "3559", "3560"):
    for r in recs:
        if r["un"] == want:
            print("UN %s p%-4d | %-42s | cls=%-4s sub=%-3s pg=%-3s sp=%-18s lq=%-5s eq=%-3s pkg=%-8s ibc=%-6s tank=%-4s ems=%-9s stow=%-7s seg=%s" % (
                r["un"], r["page"], r["psn"].replace("\n", "")[:42], r["cls"], r["sub"], r["pg"],
                r["sp"][:18], r["lq"], r["eq"], r["pkg"][:8], r["ibc"][:6], r["tank"][:4],
                r["ems"], r["stow"][:7], r["seg"][:20]))
    print()
print("--- full dump UN 3082 ---")
for r in recs:
    if r["un"] == "3082":
        for k, v in r.items():
            print("  %-11s %s" % (k, str(v).replace("\n", " ⏎ ")[:170]))