import json
import re
import time

import pymupdf

MAIN = r"D:/xwechat_files/wxid_hcz66g6exhgc22_cfa1/msg/file/2026-09/《国际海运危险货物规则》(IMDG Code)修正案(42-24) (INTERNATIONAL MARITIME ORGANIZATION) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
FIRST, LAST = 837, 1146
XB = [71.4, 94.1, 173.1, 194.5, 216.5, 238.2, 260.0, 281.8, 303.5, 338.9, 368.5, 390.0,
      418.3, 438.2, 468.0, 496.0, 530.3, 574.1, 616.8, 652.2, 749.9, 778.4]
FIELDS = ["un", "psn", "cls", "sub", "pg", "sp", "lq", "eq", "pkg", "pkgprov", "ibc", "ibcprov",
          "x12a", "reserved12", "tank", "tankprov", "ems", "stow", "seg", "prop", "un18"]
UN_RE = re.compile(r"^\d{4}$")


def cluster(vals, tol=1.5):
    out = []
    for v in sorted(vals):
        if out and v - out[-1][-1] <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [round(sum(g) / len(g), 1) for g in out]


def hsegs(page):
    segs = []
    for item in page.get_drawings():
        for sub in item["items"]:
            if sub[0] == "l":
                a, b = sub[1], sub[2]
                if abs(a.y - b.y) < 0.8 and abs(a.x - b.x) > 2:
                    segs.append((round((a.y + b.y) / 2, 1), min(a.x, b.x), max(a.x, b.x)))
            elif sub[0] == "re":
                r = sub[1]
                if r.height < 3 and r.width > 2:
                    segs.append((round((r.y0 + r.y1) / 2, 1), r.x0, r.x1))
    return segs


def col_of(x):
    for i in range(len(XB) - 1):
        if XB[i] - 1.5 <= x < XB[i + 1] - 1.5:
            return i
    return None


def cell_text(words):
    if not words:
        return ""
    lines = {}
    for x0, y0, txt in words:
        for key in lines:
            if abs(key - y0) < 4:
                lines[key].append((x0, txt))
                break
        else:
            lines[y0] = [(x0, txt)]
    return "\n".join(" ".join(t for _, t in sorted(lines[y])) for y in sorted(lines))


def main():
    doc = pymupdf.open(MAIN)
    records = []
    started = time.time()
    for pno in range(FIRST, LAST + 1):
        page = doc[pno - 1]
        segs = hsegs(page)
        ys = cluster([y for y, _, _ in segs])
        head = [y for y in ys if 150 <= y <= 178]
        if not head:
            continue
        data_top = max(head)
        cand = [y for y in ys if data_top + 2 < y <= page.rect.height - 50]
        if not cand:
            continue
        table_bottom = max(cand)
        B = [data_top] + [y for y in cand if y < table_bottom] + [table_bottom]

        words = []
        for w in page.get_text("words"):
            x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
            yc = (y0 + y1) / 2
            ci = col_of((x0 + x1) / 2)
            if ci is None or not (data_top <= yc <= table_bottom):
                continue
            if (x1 - x0) > (XB[ci + 1] - XB[ci]) + 5:
                continue
            words.append((x0, y0, x1, y1, txt, ci))

        anchors = sorted([round((w[1] + w[3]) / 2, 1) for w in words
                          if UN_RE.match(w[4]) and w[5] == 0])
        for i in range(len(B) - 1):
            lo, hi = B[i], B[i + 1]
            rows = [a for a in anchors if lo <= a < hi]
            if not rows:
                continue
            cells = {}
            for ci, field in enumerate(FIELDS):
                cells[field] = cell_text([(x0, y0, txt) for x0, y0, x1, y1, txt, wci in words
                                          if wci == ci and lo - 1 <= (y0 + y1) / 2 < hi + 1])
            for a in rows:
                rec = {"page": pno, "pages": [pno], "y": a}
                rec.update(cells)
                records.append(rec)
    print("records:", len(records), "elapsed %.1fs" % (time.time() - started))

    out = []
    for r in records:
        d = {"un": r["un"].strip(), "page": r["page"], "pages": r["pages"]}
        for f in FIELDS[1:]:
            v = r[f]
            d[f] = v.strip() if f == "psn" else re.sub(r"\s+", " ", v.replace("\n", " ")).strip()
        out.append(d)
    with open("data/dgl.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    print("unique UN:", len({r['un'] for r in out}),
          "| bad un:", sum(1 for r in out if not UN_RE.match(r["un"])),
          "| empty psn:", sum(1 for r in out if not r["psn"]),
          "| empty cls:", sum(1 for r in out if not r["cls"]))
    doc.close()


if __name__ == "__main__":
    main()