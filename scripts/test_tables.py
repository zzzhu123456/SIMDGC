import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(MAIN)

for pg in (843, 900):
    page = doc[pg - 1]
    tf = page.find_tables()
    print("=" * 78)
    print("page", pg, "tables found:", len(tf.tables))
    for t in tf.tables:
        print("  bbox:", [round(v, 1) for v in t.bbox], "rows:", t.row_count, "cols:", t.col_count)
        ex = t.extract()
        for r in ex[:8]:
            print("   ROW:", [ (c or "").replace("\n", "|")[:28] for c in r ])
        print("   ...")
        for r in ex[-3:]:
            print("   ROW:", [ (c or "").replace("\n", "|")[:28] for c in r ])
        break
doc.close()