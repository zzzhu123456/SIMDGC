import json
import re
import time

import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"

HEADER_RE = re.compile(r"^(MSC \d+/\d+/Add\.\d+|附件 ?\d*，?第 ?\d+ ?页|DANKA\\CHINESE\\\S+|附录 ?\d)\s*$")


def clean_headers(lines):
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            out.append("")
            continue
        if HEADER_RE.match(s):
            continue
        out.append(s)
    return out


def main():
    doc = pymupdf.open(MAIN)
    started = time.time()
    with open("data/main_pages.jsonl", "w", encoding="utf-8") as fh:
        for i in range(doc.page_count):
            raw = doc[i].get_text("text")
            lines = clean_headers(raw.splitlines())
            text = "\n".join(lines).strip("\n")
            fh.write(json.dumps({"page": i + 1, "text": text}, ensure_ascii=False) + "\n")
            if (i + 1) % 200 == 0:
                print("page", i + 1, "elapsed %.1fs" % (time.time() - started), flush=True)
    print("done pages", doc.page_count, "%.1fs" % (time.time() - started))
    doc.close()


if __name__ == "__main__":
    main()