import json
pages = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/annex_pages.jsonl", encoding="utf-8")}
for pg in (14, 15, 16, 17, 18):
    print("=" * 78)
    print("ANNEX PAGE", pg)
    print(pages[pg][:1400])