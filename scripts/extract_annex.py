import json

import pymupdf

ANNEX = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/附件：《国际海运危险货物规则》第42—24修正案 .pdf"

doc = pymupdf.open(ANNEX)
out = []
for i in range(doc.page_count):
    out.append({"page": i + 1, "text": doc[i].get_text("text")})
with open("data/annex_pages.jsonl", "w", encoding="utf-8") as fh:
    for p in out:
        fh.write(json.dumps(p, ensure_ascii=False) + "\n")
print("annex pages:", doc.page_count, "chars:", sum(len(p["text"]) for p in out))
print("=" * 78)
print(out[0]["text"][:2500])
doc.close()