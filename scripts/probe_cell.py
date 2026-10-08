import pymupdf
MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)
page = doc[884]  # p885
for w in page.get_text("words"):
    x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
    if 360 <= x0 <= 420 and 200 < y0 < 320:
        print("x[%.1f-%.1f] y[%.1f-%.1f] %r  w=%.1f" % (x0, x1, y0, y1, txt, x1 - x0))
print("--- 限量 column (260-282) ---")
for w in page.get_text("words"):
    x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
    if 255 <= x0 <= 290 and 200 < y0 < 330:
        print("x[%.1f-%.1f] y[%.1f-%.1f] %r" % (x0, x1, y0, y1, txt))
doc.close()