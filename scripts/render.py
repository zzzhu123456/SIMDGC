import pymupdf
MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)
for pno, name in ((890, "p890"), (958, "p958")):
    page = doc[pno - 1]
    clip = pymupdf.Rect(60, 150, 790, 420)
    pix = page.get_pixmap(clip=clip, dpi=190)
    pix.save("data/%s.png" % name)
    print("saved", name, pix.width, pix.height)
doc.close()