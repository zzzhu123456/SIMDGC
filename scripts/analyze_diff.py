import json
import re

# 生效日期等：在主文件前几页里找线索
pages = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/main_pages.jsonl", encoding="utf-8")}
for pg in (1, 2):
    t = pages[pg]
    for kw in ("生效", "2026", "2025", "适用", "通过"):
        for m in re.finditer(kw, t):
            s = max(0, m.start() - 90)
            print("p%d [%s] ...%s..." % (pg, kw, t[s:m.start() + 90].replace("\n", " ")))
    print("-" * 60)

annex = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/annex_pages.jsonl", encoding="utf-8")}
print("\n=== 附件中“整条替换”的一览表条目（第16—19页）===")
uns = []
for pg in range(16, 20):
    t = annex[pg]
    for m in re.finditer(r"(?m)^(\d{4})\s+(\S[^\n]*)", t):
        uns.append((pg, m.group(1), m.group(2)[:24]))
for u in uns:
    print("  p%-3d UN %s  %s" % u)

chg = json.load(open("data/changelog.json", encoding="utf-8"))
clauses = json.load(open("data/clauses.json", encoding="utf-8"))
dgl = json.load(open("data/dgl.json", encoding="utf-8"))
cids = {c["id"].upper() for c in clauses}
print("\n=== 变更清单与语料的对应率 ===")
hit = sum(1 for k in chg["byClause"] if k.upper() in cids)
print("条款改动 %d 条，其中 %d 条能在正文里定位到原文 (%.0f%%)" % (len(chg["byClause"]), hit, 100 * hit / len(chg["byClause"])))
sp_hit = sum(1 for k in chg["bySp"] if k.upper() in cids)
print("特殊规定改动 %d 条，其中 %d 条能定位 (%.0f%%)" % (len(chg["bySp"]), sp_hit, 100 * sp_hit / len(chg["bySp"])))
duns = {r["un"] for r in dgl}
un_hit = sum(1 for k in chg["byUn"] if k in duns)
print("UN 条目改动 %d 个，其中 %d 个能在正文一览表里找到 (%.0f%%)" % (len(chg["byUn"]), un_hit, 100 * un_hit / len(chg["byUn"])))
print("一览表 UN 总数 %d，被改动 %d 个，占比 %.1f%%" % (len(duns), len([u for u in chg["byUn"] if u in duns]), 100 * len([u for u in chg["byUn"] if u in duns]) / len(duns)))
print("\n改动涉及的全部 UN：", ", ".join(sorted(chg["byUn"])))