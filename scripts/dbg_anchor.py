import json
import re
import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
XB = [71.4, 94.1, 173.1, 194.5, 216.5, 238.2, 260.0, 281.8, 303.5, 338.9, 368.5, 390.0,
      418.3, 438.2, 468.0, 496.0, 530.3, 574.1, 616.8, 652.2, 749.9, 778.4]
UN_RE = re.compile(r"^\d{4}$")
doc = pymupdf.open(MAIN)

total = 0
per_page = {}
for pno in range(843, 1147):
    page = doc[pno - 1]
    anchors = {}
    for w in page.get_text("words"):
        x = (w[0] + w[2]) / 2
        if UN_RE.match(w[4]) and 71.4 <= x < 94.1 and w[1] > 160:
            anchors.setdefault(round((w[1] + w[3]) / 2, 1), w[4])
    per_page[pno] = anchors
    total += len(anchors)
print("total col-1 anchors, pages 843-1146:", total)

recs = json.load(open("data/dgl.json", encoding="utf-8"))
from collections import Counter
cnt = Counter(r["page"] for r in recs)
print("v3 records:", len(recs))
diff = [(p, len(per_page.get(p, {})), cnt.get(p, 0)) for p in range(843, 1147)
        if len(per_page.get(p, {})) != cnt.get(p, 0)]
print("pages mismatching:", len(diff), diff[:15])

print("\np843 anchors:", sorted(per_page[843].values()))
print("p1146 anchors:", sorted(per_page[1146].values()))

# footer/bottom check on a page that lost rows
p = diff[0][0] if diff else 900
page = doc[p - 1]
full = []
for item in page.get_drawings():
    for sub in item["items"]:
        if sub[0] == "l":
            a, b = sub[1], sub[2]
            if abs(a.y - b.y) < 0.6 and abs(a.x - b.x) > 2:
                full.append((round((a.y + b.y) / 2, 1), min(a.x, b.x), max(a.x, b.x)))
        elif sub[0] == "re":
            r = sub[1]
            if r.height < 2 and r.width > 2:
                full.append((round((r.y0 + r.y1) / 2, 1), r.x0, r.x1))
cand = [t for t in full if t[1] <= XB[0] + 3 and t[2] >= XB[-1] - 3]
print("\npage", p, "full-width hlines:", sorted({t[0] for t in cand}))
print("  all hline y (top 40):", sorted({t[0] for t in full})[:40])
doc.close()