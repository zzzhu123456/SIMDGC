import re
import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)
LABELS = ["(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7a)", "(7b)", "(8)", "(9)", "(10)",
          "(11)", "(12)", "(13)", "(14)", "(15)", "(16a)", "(16b)", "(17)", "(18)"]

for pno in (900, 1146):
    page = doc[pno - 1]
    print("=" * 78)
    print("PAGE", pno, "rect", page.rect)
    t = page.find_tables().tables[0]
    print("table bbox", [round(v, 1) for v in t.bbox], "rows", t.row_count, "cols", t.col_count)
    print("-- header cells (first 3 grid rows) with bbox --")
    for ri in range(3):
        row = t.rows[ri]
        for gi, c in enumerate(row.cells):
            if c is None:
                continue
            txt = page.get_textbox(pymupdf.Rect(c)).strip().replace("\n", "|")
            if txt:
                print("   r%d c%d x[%.1f-%.1f] y[%.1f-%.1f] %s" % (ri, gi, c[0], c[2], c[1], c[3], txt[:24]))
    print("-- words matching 4 digits, first 12 by y --")
    ws = [w for w in page.get_text("words") if re.fullmatch(r"\d{4}", w[4])]
    ws.sort(key=lambda w: (round(w[1], 1), w[0]))
    for w in ws[:12]:
        print("   x0=%.1f x1=%.1f y0=%.1f y1=%.1f %s" % (w[0], w[2], w[1], w[3], w[4]))
    print("   total 4-digit words:", len(ws))
doc.close()