import json
pages = {json.loads(l)["page"]: json.loads(l)["text"] for l in open("data/annex_pages.jsonl", encoding="utf-8")}
for pg in (16, 17, 18, 19):
    t = pages[pg]
    # drop the repeated column-header block
    i = t.find("(18)")
    print("=" * 78)
    print("ANNEX PAGE", pg, "| chars", len(t))
    print(t[i + 4:][:1500] if i >= 0 else t[:1500])