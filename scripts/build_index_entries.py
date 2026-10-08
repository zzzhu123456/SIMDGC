import json
import re

import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
UN_RE = re.compile(r"^\d{4}$")
COL_NAME, COL_MP, COL_CLS, COL_UN = 340.0, 400.0, 460.0, 9999.0

doc = pymupdf.open(MAIN)
entries = []
for pno in range(1226, 1373):
    page = doc[pno - 1]
    words = [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]
    anchors = sorted({round((w[1] + w[3]) / 2, 1) for w in words
                      if UN_RE.match(w[4]) and w[0] >= COL_CLS})
    if not anchors:
        continue
    top = min(anchors) - 20
    bot = max(anchors) + 20
    for i, a in enumerate(anchors):
        lo = (anchors[i - 1] + a) / 2 if i > 0 else top
        hi = (a + anchors[i + 1]) / 2 if i + 1 < len(anchors) else bot
        name, mp, cls, un = [], [], [], ""
        for x0, y0, x1, y1, txt in words:
            yc = (y0 + y1) / 2
            if not (lo <= yc < hi):
                continue
            if x0 < COL_NAME:
                name.append((x0, y0, txt))
            elif x0 < COL_MP:
                mp.append(txt)
            elif x0 < COL_CLS:
                cls.append(txt)
            elif x0 >= COL_CLS:
                un = txt
        if not name or not UN_RE.match(un):
            continue
        name_txt = "".join(t for _, _, t in sorted(name))
        entries.append({"name": name_txt, "mp": "".join(mp), "cls": "".join(cls),
                        "un": un, "page": pno})
print("index entries:", len(entries))
print("rows with empty class:", sum(1 for e in entries if not e["cls"]))
print("distinct UN:", len({e["un"] for e in entries}))
for e in entries[:3]:
    print("  ", json.dumps(e, ensure_ascii=False))
for e in entries[-3:]:
    print("  ", json.dumps(e, ensure_ascii=False))
with open("data/index_entries.json", "w", encoding="utf-8") as fh:
    json.dump(entries, fh, ensure_ascii=False)
doc.close()