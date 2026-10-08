import json
import re
from collections import Counter

pages = [json.loads(line) for line in open("data/main_pages.jsonl", encoding="utf-8")]
total_chars = sum(len(p["text"]) for p in pages)
print("pages:", len(pages), "total chars:", total_chars)

PART_RE = re.compile(r"^第\s?(\d)\s?部分\s*(.*)$")
CHAP_RE = re.compile(r"^第\s?(\d+\.\d+)\s?章\s*(.*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+(?:\.\d+){0,4})\s+\S")
UN_RE = re.compile(r"\bUN\s?(\d{4})\b")

parts = []
chaps = []
clause_lines = 0
un_numbers = Counter()

for p in pages:
    for line in p["text"].splitlines():
        s = line.strip()
        if not s:
            continue
        m = PART_RE.match(s)
        if m and len(s) < 40:
            parts.append((p["page"], s))
            continue
        m = CHAP_RE.match(s)
        if m and len(s) < 40:
            chaps.append((p["page"], s))
            continue
        if CLAUSE_RE.match(s):
            clause_lines += 1
        for u in UN_RE.findall(s):
            un_numbers[u] += 1

print("\n--- parts (host headings) ---")
for pg, s in parts[:60]:
    print("  p%-5d %s" % (pg, s))
print("total part-like lines:", len(parts))

print("\n--- chapters: first 40 ---")
for pg, s in chaps[:40]:
    print("  p%-5d %s" % (pg, s))
print("total chapter-like lines:", len(chaps))

print("\nclause-number lines:", clause_lines)
print("distinct UN numbers found:", len(un_numbers), "total mentions:", sum(un_numbers.values()))

keywords = ["联合国编号", "正确运输名称", "特殊规定", "包装导则", "积载", "隔离", "限量", "例外数量", "海洋污染物",
            "危险货物一览表", "索引", "附录A", "附录B", "术语汇编", "隔离表", "字母顺序索引"]
for kw in keywords:
    hits = [p["page"] for p in pages if kw in p["text"]]
    print("kw %-12s pages=%4d first=%s last=%s" % (kw, len(hits), hits[0] if hits else "-", hits[-1] if hits else "-"))