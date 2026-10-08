import json
import re

lines = []
for l in open("data/annex_pages.jsonl", encoding="utf-8"):
    p = json.loads(l)
    for s in p["text"].splitlines():
        s = s.strip()
        if s:
            lines.append((p["page"], s))

PART = re.compile(r"^第\s?(\d)\s?部分\s*(.*)$")
CHAP = re.compile(r"^第\s?(\d+\.\d+)\s?章\s*(.*)$")
CLAUSE = re.compile(r"^(\d+\.\d+\.\d+(?:\.\d+)*)\b\s*(.*)$")
NUMONLY = re.compile(r"^(\d+\.\d+\.\d+(?:\.\d+)*)$")
UNNUM = re.compile(r"UN\s?(\d{4})")

verbs = ["增加", "删除", "替换", "修改", "修订", "改为", "新增", "插入", "合并", "拆分",
         "新注", "新的一段", "整段替换", "全部替换", "重新编号"]

print("total content lines:", len(lines))
print("\n--- PART lines ---")
for pg, s in lines:
    if PART.match(s):
        print("  p%-3d %s" % (pg, s))
print("\n--- CHAPTER lines ---")
chaps = [(pg, s) for pg, s in lines if CHAP.match(s)]
print("count:", len(chaps))
for pg, s in chaps[:80]:
    print("  p%-3d %s" % (pg, s))

clauses = [(pg, s) for pg, s in lines if CLAUSE.match(s) or NUMONLY.match(s)]
print("\n--- clause-ish lines:", len(clauses))
for pg, s in clauses:
    print("  p%-3d %s" % (pg, s[:70]))