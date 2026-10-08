import json
import re

pages = [json.loads(l) for l in open("data/main_pages.jsonl", encoding="utf-8")]

low = [(p["page"], len(p["text"])) for p in pages if len(p["text"]) < 200]
print("pages with <200 chars:", len(low))
print(low[:80])

print("\n--- structure of p1194-1250 (first 120 chars each) ---")
for p in pages:
    if 1194 <= p["page"] <= 1250:
        head = " / ".join(x.strip() for x in p["text"].splitlines()[:4] if x.strip())
        print("p%-5d %s" % (p["page"], head[:110]))

print("\n--- where are 附录A / 附录B / 术语汇编 / 索引 as headings ---")
for kw in ("附录A", "附录B", "术语汇编", "索引", "附录 1", "附录 2", "危险货物一览表"):
    hits = [p["page"] for p in pages if kw in p["text"][:200]]
    if hits:
        print("%-10s %s" % (kw, hits[:12]))