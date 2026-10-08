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


def cluster(vals, tol=1.0):
    vals = sorted(vals)
    out = []
    for v in vals:
        if out and v - out[-1][-1] <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(g) / len(g) for g in out]


def hlines(page):
    """Return merged horizontal segments as (y, x0, x1)."""
    segs = []
    for item in page.get_drawings():
        for sub in item["items"]:
            if sub[0] == "l":
                p1, p2 = sub[1], sub[2]
                if abs(p1.y - p2.y) < 0.6 and abs(p1.x - p2.x) > 2:
                    segs.append((round((p1.y + p2.y) / 2, 1), min(p1.x, p2.x), max(p1.x, p2.x)))
            elif sub[0] == "re":
                r = sub[1]
                if r.height < 2 and r.width > 2:
                    segs.append((round((r.y0 + r.y1) / 2, 1), r.x0, r.x1))
    merged = {}
    for y, x0, x1 in segs:
        for key in merged:
            if abs(key - y) < 1.0:
                merged[key].append((x0, x1))
                break
        else:
            merged[y] = [(x0, x1)]
    out = []
    for y, ivs in merged.items():
        ivs.sort()
        cur0, cur1 = ivs[0]
        for a, b in ivs[1:]:
            if a <= cur1 + 2:
                cur1 = max(cur1, b)
            else:
                out.append((y, cur0, cur1))
                cur0, cur1 = a, b
        out.append((y, cur0, cur1))
    return sorted(out)


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
        hl = hlines(page)
        full = [y for y, x0, x1 in hl if x0 <= XB[0] + 3 and x1 >= XB[-1] - 3]
        if not full:
            continue
        data_top = min(y for y in full if y > 120)
        table_bottom = max(full)
        words = [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")
                 if w[3] > data_top and w[1] < table_bottom]
        anchors = sorted({round((w[1] + w[3]) / 2, 1) for w in words
                          if UN_RE.match(w[4]) and col_of((w[0] + w[2]) / 2) in (0, 20)})
        if not anchors:
            continue
        # per-column cell bands
        bands = {}
        for ci in range(len(XB) - 1):
            cx = (XB[ci] + XB[ci + 1]) / 2
            cuts = cluster([y for y, x0, x1 in hl if x0 - 2 <= cx <= x1 + 2 and data_top - 1 <= y <= table_bottom + 1])
            cuts = [data_top] + [c for c in cuts if data_top + 2 < c < table_bottom - 2] + [table_bottom]
            bands[ci] = [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)]
        for i, a in enumerate(anchors):
            rowlo = (anchors[i - 1] + a) / 2 if i > 0 else data_top
            rowhi = (a + anchors[i + 1]) / 2 if i + 1 < len(anchors) else table_bottom
            rec = {"un": "", "page": pno, "pages": [pno], "y": a}
            for ci, field in enumerate(FIELDS):
                ws = []
                for lo, hi in bands[ci]:
                    if hi <= rowlo + 1 or lo >= rowhi - 1:
                        continue
                    for x0, y0, x1, y1, txt in words:
                        if lo - 1 <= (y0 + y1) / 2 < hi + 1 and col_of((x0 + x1) / 2) == ci:
                            ws.append((x0, y0, txt))
                rec[field] = cell_text(ws)
            rec["un"] = rec["un"].strip()
            if not rec["un"]:
                continue
            if records and records[-1]["page"] == pno and records[-1]["y"] == a:
                continue
            records.append(rec)
    print("records:", len(records), "elapsed %.1fs" % (time.time() - started))
    out = []
    for r in records:
        d = {"un": r["un"], "page": r["page"], "pages": r["pages"]}
        for f in FIELDS:
            d[f] = re.sub(r"\s+", " ", r[f].replace("\n", " ")).strip() if f != "psn" else r[f].strip()
        out.append(d)
    with open("data/dgl.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    print("unique UN:", len({r['un'] for r in out}))
    print("empty psn:", sum(1 for r in out if not r["psn"]), "empty cls:", sum(1 for r in out if not r["cls"]))
    doc.close()


if __name__ == "__main__":
    main()