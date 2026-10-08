import json
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
lows = []
tails = {}
for pno in range(843, 1147):
    page = doc[pno - 1]
    maxun = 0
    for w in page.get_text("words"):
        xc = (w[0] + w[2]) / 2
        if re.fullmatch(r"\d{4}", w[4]) and col_of(xc) == 20:
            maxun = max(maxun, w[3])
        if w[1] > 540:
            tails.setdefault(pno, []).append((round(w[1], 1), round(w[0], 1), w[4][:30]))
    lows.append((pno, round(maxun, 1)))
lo = sorted(lows, key=lambda t: -t[1])[:8]
print("pages with largest trailing-UN y:", lo)
print("\npages with words below y=540:", len(tails))
for pno in list(tails)[:6]:
    print("  p", pno, tails[pno][:5])
doc.close()