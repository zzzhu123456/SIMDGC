import json
import re

lines = []
for l in open("data/annex_pages.jsonl", encoding="utf-8"):
    p = json.loads(l)
    for s in p["text"].splitlines():
        s = s.strip()
        if s:
            lines.append((p["page"], s))

PART_RE = re.compile(r"^第\s?(\d)\s?部分\s*(.*)$")
CHAP_RE = re.compile(r"^第\s?(\d+\.\d+)\s*章\s*(.*)$")
SEC_RE = re.compile(r"^(\d+\.\d+(?:\.\d+){1,3})$")
ITEM_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,3}){1,4})\s+(\S.*)$")
SP_RE = re.compile(r"^SP\s?(\d{1,3})\s*(.*)$")
UN_RE = re.compile(r"^(\d{3,4})(?:\s+(.*))?$")
VERBS = ["增加", "删除", "替换", "修改", "新增", "插入", "改为", "整体替换", "重新编号", "调整"]

marks = []
state = {"part": "", "chapter": "", "section": ""}
for idx, (pg, s) in enumerate(lines):
    m = PART_RE.match(s)
    if m:
        state["part"] = "第%s部分" % m.group(1)
        state["chapter"] = ""
        state["section"] = ""
        marks.append((idx, "part", state["part"], m.group(2).strip(), pg, dict(state)))
        continue
    m = CHAP_RE.match(s)
    if m and len(s) < 40:
        state["chapter"] = "第%s章" % m.group(1)
        state["section"] = ""
        marks.append((idx, "chapter", state["chapter"], m.group(2).strip(), pg, dict(state)))
        continue
    m = SEC_RE.match(s)
    if m:
        state["section"] = m.group(1)
        marks.append((idx, "section", m.group(1), "", pg, dict(state)))
        continue
    m = SP_RE.match(s)
    if m:
        marks.append((idx, "sp", "SP" + m.group(1), m.group(2).strip(), pg, dict(state)))
        continue
    m = ITEM_RE.match(s)
    if m and "." in m.group(1) and len(m.group(1)) >= 5:
        marks.append((idx, "clause", m.group(1), m.group(2).strip(), pg, dict(state)))
        continue
    m = UN_RE.match(s)
    if m and len(m.group(1)) == 4 and state["chapter"] == "第3.2章":
        marks.append((idx, "un", m.group(1), (m.group(2) or "").strip(), pg, dict(state)))
        continue

items = []
for k, (idx, kind, ref, rest, pg, st) in enumerate(marks):
    end = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
    body = [rest] if rest else []
    for j in range(idx + 1, end):
        body.append(lines[j][1])
    text = "\n".join(b for b in body if b).strip()
    items.append({"kind": kind, "ref": ref, "text": text, "page": pg,
                  "part": st["part"], "chapter": st["chapter"], "section": st["section"]})

kinds = {}
for it in items:
    kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
print("marks:", len(marks), kinds)

verb_counts = {v: 0 for v in VERBS}
for it in items:
    for v in VERBS:
        if v in it["text"]:
            verb_counts[v] += 1
print("change verbs:", verb_counts)

uns = [it for it in items if it["kind"] == "un"]
print("DGL change rows:", len(uns), "distinct UN:", len({u["ref"] for u in uns}))
cl = [it for it in items if it["kind"] == "clause"]
print("clause-level changes:", len(cl), "distinct refs:", len({c["ref"] for c in cl}))
print("SP changes:", len([it for it in items if it["kind"] == "sp"]))
bypart = {}
for it in items:
    if it["kind"] in ("clause", "sp", "un"):
        bypart.setdefault(it["part"], set()).add(it["ref"])
print("refs per part:", {k: len(v) for k, v in sorted(bypart.items())})

byUn = {}
for it in uns:
    byUn.setdefault(it["ref"], []).append(it["text"])
byClause = {}
for it in cl:
    byClause.setdefault(it["ref"], []).append(it["text"])
bySp = {}
for it in items:
    if it["kind"] == "sp":
        bySp.setdefault(it["ref"], []).append(it["text"])

out = {"stats": {"items": len(items), "kinds": kinds, "verbs": verb_counts,
                 "unChanged": len(byUn), "clausesChanged": len(byClause), "spChanged": len(bySp)},
       "items": items, "byUn": byUn, "byClause": byClause, "bySp": bySp}
with open("data/changelog.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=0)
for u in uns[:6]:
    print("  UN", u["ref"], "|", u["text"].replace("\n", " / ")[:100])
print("  ...")
print("  chapter counts:", {})
from collections import Counter
print(Counter(it["chapter"] for it in cl).most_common(30))