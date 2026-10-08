import re
import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
XB = [71.4, 94.1, 173.1, 194.5, 216.5, 238.2, 260.0, 281.8, 303.5, 338.9, 368.5, 390.0,
      418.3, 438.2, 468.0, 496.0, 530.3, 574.1, 616.8, 652.2, 749.9, 778.4]
doc = pymupdf.open(MAIN)
def col_of(x):
    for i in range(len(XB) - 1):
        if XB[i] - 1.5 <= x < XB[i + 1] - 1.5:
            return i
    return None
for pno in (843, 844, 900, 1146):
    page = doc[pno - 1]
    hl = []
    for item in page.get_drawings():
        for sub in item["items"]:
            if sub[0] == "l":
                a, b = sub[1], sub[2]
                if abs(a.y - b.y) < 0.6 and abs(a.x - b.x) > 2:
                    hl.append((round((a.y + b.y) / 2, 1), min(a.x, b.x), max(a.x, b.x)))
    ys = [y for y, _, _ in hl]
    head = sorted(set(y for y in ys if 140 <= y <= 178))
    data_top = max(head) if head else 160.8
    tbot = sorted(set(y for y, x0, x1 in hl if data_top < y <= page.rect.height - 55))
    print("page", pno, "head candidates:", head, "-> data_top", data_top, "| table_bottom", tbot[-1] if tbot else None)
    # anchors with width filter
    ok, dropped = [], []
    for w in page.get_text("words"):
        x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
        ci = col_of((x0 + x1) / 2)
        if ci is None or not (data_top < y0 and y1 <= (tbot[-1] if tbot else 0) + 2):
            continue
        if re.fullmatch(r"\d{4}", txt) and ci == 0:
            if (x1 - x0) > (XB[1] - XB[0]) + 4:
                dropped.append((txt, round(x1 - x0, 1)))
            else:
                ok.append(txt)
    print("   anchors kept:", len(ok), "dropped by width:", dropped[:5])
doc.close()