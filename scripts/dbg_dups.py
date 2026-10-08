import json

recs = json.load(open("data/dgl.json", encoding="utf-8"))
print("total", len(recs))
seen = {}
for i, r in enumerate(recs):
    seen.setdefault(r["un"], []).append(i)
dups = {k: v for k, v in seen.items() if len(v) > 1}
print("dup UN count:", len(dups), "extra recs:", sum(len(v) - 1 for v in dups.values()))
for k in list(dups)[:5]:
    print("=" * 70)
    for i in dups[k]:
        r = recs[i]
        print(" idx", i, "page", r["page"], "pages", r["pages"])
        print("   psn:", r["psn"][:60].replace("\n", "/"))
        print("   cls:", r["cls"], "pg:", r["pg"], "sp:", r["sp"].replace("\n","/")[:40])
        print("   ems:", r["ems"], "stow:", r["stow"].replace(chr(10),"/")[:40], "seg:", r["seg"].replace(chr(10),"/")[:40])