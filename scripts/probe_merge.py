import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)
page = doc[889]  # p890
print("--- raw items on p890 (first 12) ---")
for i, item in enumerate(page.get_drawings()[:12]):
    print(i, item["type"], "items:", [(s[0],) for s in item["items"]][:4], "rect", [round(v,1) for v in item["rect"]])
print("\n--- horizontal segments crossing x=133.6 (PSN column) ---")
xs = 133.6
segs = []
for item in page.get_drawings():
    for sub in item["items"]:
        if sub[0] == "l":
            a, b = sub[1], sub[2]
            if abs(a.y - b.y) < 0.8:
                if min(a.x, b.x) - 1 <= xs <= max(a.x, b.x) + 1:
                    segs.append(round((a.y + b.y) / 2, 1))
        elif sub[0] == "re":
            r = sub[1]
            if r.height < 4 and r.x0 - 1 <= xs <= r.x1 + 1:
                segs.append(round((r.y0 + r.y1) / 2, 1))
print("count:", len(segs))
print(sorted(segs))
print("\n--- same for x=80 (UN column) ---")
xs = 80.0
segs = []
for item in page.get_drawings():
    for sub in item["items"]:
        if sub[0] == "l":
            a, b = sub[1], sub[2]
            if abs(a.y - b.y) < 0.8 and min(a.x, b.x) - 1 <= xs <= max(a.x, b.x) + 1:
                segs.append(round((a.y + b.y) / 2, 1))
        elif sub[0] == "re":
            r = sub[1]
            if r.height < 4 and r.x0 - 1 <= xs <= r.x1 + 1:
                segs.append(round((r.y0 + r.y1) / 2, 1))
print("count:", len(segs))
print(sorted(segs))
doc.close()