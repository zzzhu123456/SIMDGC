import json
import re
import time

import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
FIRST, LAST = 837, 1146
UN_RE = re.compile(r"^\d{4}$")
LABELS = ["(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7a)", "(7b)", "(8)", "(9)", "(10)",
          "(11)", "(12)", "(13)", "(14)", "(15)", "(16a)", "(16b)", "(17)", "(18)"]
FIELDS = ["un", "psn", "cls", "sub", "pg", "sp", "lq", "eq", "pkg", "pkgprov",
          "ibc", "ibcprov", "reserved12", "tank", "tankprov", "ems", "stow", "seg", "prop", "un18"]


def build_colmap(table):
    """Find grid index of each DGL column label from the repeated 2-row header."""
    colmap = {}
    rows = table.extract()[:4]
    for row in rows:
        for gi, cell in enumerate(row):
            if not cell:
                continue
            for token in re.split(r"[|\n]", cell):
                token = token.strip()
                if token in LABELS and token not in colmap:
                    colmap[token] = gi
    return colmap


def main():
    doc = pymupdf.open(MAIN)
    records = []
    cur = None
    colmaps = {}
    started = time.time()
    for pno in range(FIRST, LAST + 1):
        page = doc[pno - 1]
        for t in page.find_tables().tables:
            colmap = build_colmap(t)
            colmaps.setdefault(tuple(sorted(colmap.items())), 0)
            colmaps[tuple(sorted(colmap.items()))] += 1
            if len(colmap) < 18 or len(t.extract()) == 0:
                continue
            for row in t.extract():
                n = max(len(row), max(colmap.values()) + 1)
                cells = [(row[i] if i < len(row) else "") or "" for i in range(n)]
                cells = [c.strip() for c in cells]
                un_i = colmap.get("(1)")
                if un_i is None:
                    continue
                first = cells[un_i]
                if UN_RE.match(first):
                    if cur:
                        records.append(cur)
                    cur = {"un": first, "pages": [pno], "raw": {}}
                    for label, field in zip(LABELS, FIELDS):
                        gi = colmap.get(label)
                        cur["raw"][field] = cells[gi] if gi is not None and gi < len(cells) else ""
                elif cur is not None and any(cells):
                    for label, field in zip(LABELS, FIELDS):
                        gi = colmap.get(label)
                        val = cells[gi] if gi is not None and gi < len(cells) else ""
                        if val:
                            cur["raw"][field] = (cur["raw"][field] + "\n" + val) if cur["raw"][field] else val
                    if cur["pages"][-1] != pno:
                        cur["pages"].append(pno)
    if cur:
        records.append(cur)
    print("records:", len(records), "elapsed %.1fs" % (time.time() - started))

    print("\n--- colmap variants ---")
    for key, cnt in sorted(colmaps.items(), key=lambda kv: -kv[1])[:4]:
        print("  pages:", cnt, dict(key))

    out = [{"un": r["un"], "page": r["pages"][0], "pages": r["pages"], **r["raw"]} for r in records]
    with open("data/dgl.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    print("\nsaved", len(out))
    doc.close()


if __name__ == "__main__":
    main()