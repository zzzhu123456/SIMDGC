import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)
for pno in (900, 1146):
    page = doc[pno - 1]
    d = page.get_drawings()
    vert, horiz = set(), set()
    for item in d:
        for sub in item["items"]:
            if sub[0] == "l":
                p1, p2 = sub[1], sub[2]
                if abs(p1.x - p2.x) < 0.5 and abs(p1.y - p2.y) > 5:
                    vert.add(round(p1.x, 1))
                elif abs(p1.y - p2.y) < 0.5 and abs(p1.x - p2.x) > 5:
                    horiz.add(round(p1.y, 1))
            elif sub[0] == "re":
                r = sub[1]
                vert.add(round(r.x0, 1)); vert.add(round(r.x1, 1))
                horiz.add(round(r.y0, 1)); horiz.add(round(r.y1, 1))
    print("=" * 70)
    print("page", pno, "drawings:", len(d), "vlines:", len(vert), "hlines:", len(horiz))
    print("  v x:", sorted(vert))
    print("  h y:", sorted(horiz)[:40])
doc.close()