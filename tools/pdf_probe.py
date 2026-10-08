import json

import pymupdf

PATHS = {
    "main": r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "annex": r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/附件：《国际海运危险货物规则》第42—24修正案 .pdf",
}


def main():
    for key, path in PATHS.items():
        doc = pymupdf.open(path)
        print("=" * 78)
        print(key, "| pages =", doc.page_count, "| encrypted =", doc.is_encrypted)
        print("metadata:", json.dumps(doc.metadata, ensure_ascii=False))
        toc = doc.get_toc()
        print("toc entries:", len(toc))
        for i in range(min(4, doc.page_count)):
            page = doc[i]
            text = page.get_text().strip()
            print("--- page", i, "textlen =", len(text), "images =", len(page.get_images(full=True)))
            print(text[:400].replace("\n", " | "))
        print("--- TOC (first 60) ---")
        for entry in toc[:60]:
            print("   ", entry)
        doc.close()


if __name__ == "__main__":
    main()