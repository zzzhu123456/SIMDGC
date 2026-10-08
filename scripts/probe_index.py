import pymupdf, re
MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)
page = doc[1225]  # p1226
print("--- words on p1226 (y 150-260) ---")
for w in sorted(page.get_text("words"), key=lambda w: (round(w[1],1), w[0])):
    x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
    if 150 < y0 < 265:
        print("x[%6.1f-%6.1f] y[%6.1f] %r" % (x0, x1, y0, txt))
print("--- vertical lines ---")
xs = set()
for item in page.get_drawings():
    for s in item["items"]:
        if s[0] == "l":
            a, b = s[1], s[2]
            if abs(a.x - b.x) < 0.5 and abs(a.y - b.y) > 5:
                xs.add(round(a.x, 1))
        elif s[0] == "re":
            r = s[1]
            if r.width < 2 and r.height > 3:
                xs.add(round(r.x0, 1))
print(sorted(xs))
doc.close()