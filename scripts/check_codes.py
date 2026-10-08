import json
from collections import Counter
cl = json.load(open("data/clauses.json", encoding="utf-8"))
codes = [c for c in cl if c["kind"] == "code"]
pre = Counter()
for c in codes:
    pre["".join(ch for ch in c["id"] if ch.isalpha())] += 1
print("code units by prefix:", pre.most_common())
print("examples:", {k: [c["id"] for c in codes if c["id"].startswith(k)][:4] for k in ("P", "LP", "IBC", "T", "BK")})
sp = [c for c in cl if c["kind"] == "sp"]
print("SP count:", len(sp), "with text:", sum(1 for c in sp if c["text"].strip()))
print("empty clause texts:", sum(1 for c in cl if not c["text"].strip()))