import json
import os
import re
from collections import Counter, OrderedDict

dgl = json.load(open("data/dgl.json", encoding="utf-8"))
clauses = json.load(open("data/clauses.json", encoding="utf-8"))
idx = json.load(open("data/index_entries.json", encoding="utf-8"))
change = json.load(open("data/changelog.json", encoding="utf-8"))
sindex = json.load(open("web/data/search_index.json", encoding="utf-8"))

parts = OrderedDict()
for c in clauses:
    p = c["part"] or "其他"
    ch = c["chapter"] or "其他"
    parts.setdefault(p, {"title": c.get("partTitle", ""), "chapters": OrderedDict()})
    pd = parts[p]["chapters"]
    if ch not in pd:
        pd[ch] = {"title": c.get("chapterTitle", ""), "count": 0, "page": c["page"], "last": c["page"]}
    pd[ch]["count"] += 1
    pd[ch]["last"] = max(pd[ch]["last"], c["page"])

catalog = {
    "generated": "IMDG Code 42-24 (中文版 MSC.556(108))",
    "stats": {
        "dglRows": len(dgl),
        "dglUn": len({r["un"] for r in dgl}),
        "clauses": len(clauses),
        "sp": len([c for c in clauses if c["kind"] == "sp"]),
        "codes": len([c for c in clauses if c["kind"] == "code"]),
        "indexEntries": len(idx),
        "pages": 1372,
    },
    "parts": [{"id": p, "title": v["title"],
               "chapters": [{"id": k, "title": v2["title"], "count": v2["count"],
                             "page": v2["page"], "last": v2["last"]}
                            for k, v2 in v["chapters"].items()]}
              for p, v in parts.items()],
    "changelogStats": change["stats"],
}
with open("web/data/catalog.js", "w", encoding="utf-8") as fh:
    fh.write("window.IMDG_CATALOG=" + json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + ";\n")


def wrap(name, obj):
    with open("web/data/%s.js" % name, "w", encoding="utf-8") as fh:
        fh.write("window.%s=%s;\n" % (name.upper().replace("-", "_"),
                                      json.dumps(obj, ensure_ascii=False, separators=(",", ":"))))


wrap("dgl", dgl)
wrap("clauses", clauses)
wrap("idx", idx)
wrap("changelog", change)
wrap("sindex", sindex)
for f in ("catalog", "dgl", "clauses", "idx", "changelog", "sindex"):
    print("web/data/%s.js  %.2f MB" % (f, os.path.getsize("web/data/%s.js" % f) / 1e6))
print(json.dumps(catalog["stats"], ensure_ascii=False))
print("parts:", [(p["id"], len(p["chapters"])) for p in catalog["parts"]])