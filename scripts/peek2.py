import json

pages = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/main_pages.jsonl", encoding="utf-8")}

for pg in (838, 839, 1146, 1200, 1300, 1372):
    print("=" * 78)
    print("PAGE", pg)
    print(pages[pg][:1200])