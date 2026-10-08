import json
import re
import statistics
import time

import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
FIRST, LAST = 837, 1146

BOUNDS = [71.4, 94.1, 173.1, 194.5, 216.5, 238.2, 260.0, 281.8, 303.5, 338.9, 368.5, 390.0,
          418.3, 438.2, 468.0, 496.0, 530.3, 574.1, 616.8, 652.2, 749.9, 778.4]
FIELDS = ["un", "psn", "cls", "sub", "pg", "sp", "lq", "eq", "pkg", "pkgprov", "ibc", "ibcprov",
          "x12a", "reserved12", "tank", "tankprov", "ems", "stow", "seg", "prop", "un18"]
UN_RE = re.compile(r"^\d{4}$")


def col_of(x):
    for i in range(len(BOUNDS) - 1):
        if BOUNDS[i] - 1.5 <= x < BOUNDS[i + 1] - 1.5:
            return i
    return None


def cell_text(words):
    """words: list of (x0, y0, text) inside one (row, column)."""
    if not words:
        return ""
    lines = {}
    for x0, y0, txt in words:
        placed = False
        for key in lines:
            if abs(key - y0) < 4:
                lines[key].append((x0, txt))
                placed = True
                break
        if not placed:
            lines[y0] = [(x0, txt)]
    out = []
    for y in sorted(lines):
        parts = [t for _, t in sorted(lines[y])]
        out.append(" ".join(parts))
    return "\n".join(out)


def main():
    doc = pymupdf.open(MAIN)
    records = []
    pending = None  # previous page's last unfinished record
    started = time.time()
    for pno in range(FIRST, LAST + 1):
        page = doc[pno - 1]
        raw = page.get_text("words")
        words = [(w[0], w[1], w[2], w[3], w[4]) for w in raw]
        # running header / repeated column header occupy the top band
        body_top = 161.7
        body = [w for w in words if w[1] >= body_top]
        if not body:
            continue
        anchors = sorted({round((w[1] + w[3]) / 2, 1) for w in body
                          if UN_RE.match(w[4]) and col_of((w[0] + w[2]) / 2) in (0, 20)})
        bands = []
        for i, a in enumerate(anchors):
            lo = (anchors[i - 1] + a) / 2 if i > 0 else body_top
            hi = (a + anchors[i + 1]) / 2 if i + 1 < len(anchors) else 10_000
            bands.append((lo, hi, a))
        lead = [w for w in body if w[1] < bands[0][0]] if bands else body
        if lead and pending is not None:
            for x0, y0, x1, y1, txt in lead:
                ci = col_of((x0 + x1) / 2)
                if ci is not None:
                    pending["w"][ci].append((x0, y0, txt))
            pending["pages"].append(pno)
        for lo, hi, a in bands:
            cells = [[] for _ in FIELDS]
            un_first = un_last = None
            for x0, y0, x1, y1, txt in body:
                if not (lo <= y0 < hi):
                    continue
                ci = col_of((x0 + x1) / 2)
                if ci is None:
                    continue
                cells[ci].append((x0, y0, txt))
            un_first = next((w[2] for w in cells[0]), "")
            un_last = next((w[2] for w in cells[20]), "")
            if not un_first:
                continue
            rec = {"un": un_first, "un18": un_last, "pages": [pno],
                   "page": pno, "y": a, "w": cells}
            if pending is not None:
                records.append(pending)
            pending = rec
    if pending:
        records.append(pending)
    print("records:", len(records), "elapsed %.1fs" % (time.time() - started))

    out = []
    for r in records:
        d = {"un": r["un"], "page": r["page"], "pages": r["pages"]}
        for f, cell in zip(FIELDS, r["w"]):
            d[f] = cell_text(cell)
        out.append(d)
    with open("data/dgl.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)

    n_un18_mismatch = sum(1 for r in out if r["un18"].strip() and r["un18"].strip() != r["un"])
    n_empty_psn = sum(1 for r in out if not r["psn"].strip())
    n_empty_cls = sum(1 for r in out if not r["cls"].strip())
    n_x12a = sum(1 for r in out if r["x12a"].strip())
    print("unique UN:", len({r['un'] for r in out}))
    print("un18 mismatch:", n_un18_mismatch, "| empty psn:", n_empty_psn, "| empty cls:", n_empty_cls,
          "| non-empty range-12a:", n_x12a)
    doc.close()


if __name__ == "__main__":
    main()