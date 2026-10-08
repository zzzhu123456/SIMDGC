import json
pages = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/main_pages.jsonl", encoding="utf-8")}
for pg, n in ((1148, 1100), (228, 900), (814, 700)):
    print("=" * 78)
    print("PAGE", pg)
    print(pages[pg][:n])