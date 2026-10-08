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


def cell_text(words, cx0, cx1):
    """words: (x0, x1, y0, text). Join wrapped lines; no space when the break is mid-token."""
    if not words:
        return ""
    lines = {}
    for x0, x1, y0, txt in words:
        for key in lines:
            if abs(key - y0) < 4:
                lines[key].append((x0, x1, txt))
                break
        else:
            lines[y0] = [(x0, x1, txt)]
    def join_line(seg):
        seg = sorted(seg)
        text = seg[0][2]
        prev = seg[0][1]
        for x0, x1, t in seg[1:]:
            text += (" " if x0 - prev > 1.0 else "") + t
            prev = x1
        return text

    out = ""
    prev_right = None
    for y in sorted(lines):
        seg = sorted(lines[y])
        text = join_line(seg)
        if not out:
            out = text
        else:
            out += ("" if prev_right >= cx1 - 8 else " ") + text
        prev_right = max(x1 for _, x1, _ in seg)
    return out


def main():
    doc = pymupdf.open(MAIN)
    records = []
    started = time.time()
    for pno in range(FIRST, LAST + 1):
        page = doc[pno - 1]
        ys = cluster([y for y, _, _ in hsegs(page)])
        head = [y for y in ys if 150 <= y <= 178]
        if not head:
            continue
        data_top = max(head)
        cand = [y for y in ys if data_top + 2 < y <= page.rect.height - 50]
        if not cand:
            continue
        table_bottom = max(cand)
        B = [data_top] + [y for y in cand if y < table_bottom] + [table_bottom]

        per_col = {}
        for w in page.get_text("words"):
            x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
            yc = (y0 + y1) / 2
            ci = col_of((x0 + x1) / 2)
            if ci is None or not (data_top <= yc <= table_bottom):
                continue
            if (x1 - x0) > (XB[ci + 1] - XB[ci]) + 5:
                continue
            per_col.setdefault(ci, []).append((x0, x1, y0, txt, yc))
        anchors = sorted([round(yc, 1) for x0, x1, y0, txt, yc in per_col.get(0, []) if UN_RE.match(txt)])
        for i in range(len(B) - 1):
            lo, hi = B[i], B[i + 1]
            rows = [a for a in anchors if lo <= a < hi]
            if not rows:
                continue
            cells = {}
            for ci, field in enumerate(FIELDS):
                ws = [(x0, x1, y0, txt) for x0, x1, y0, txt, yc in per_col.get(ci, []) if lo - 1 <= yc < hi + 1]
                cells[field] = cell_text(ws, XB[ci], XB[ci + 1])
            for a in rows:
                rec = {"page": pno, "pages": [pno], "y": a}
                rec.update(cells)
                records.append(rec)
    print("records:", len(records), "elapsed %.1fs" % (time.time() - started))

    keep = ["un", "psn", "cls", "sub", "pg", "sp", "lq", "eq", "pkg", "pkgprov", "ibc", "ibcprov",
            "tank", "tankprov", "ems", "stow", "seg", "prop"]
    out = []
    for r in records:
        d = {"un": r["un"].strip(), "page": r["page"]}
        for f in keep[1:]:
            d[f] = re.sub(r"\s+", " ", r[f]).strip()
        out.append(d)
    with open("data/dgl.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    print("unique UN:", len({r['un'] for r in out}), "| bad:", sum(1 for r in out if not UN_RE.match(r["un"])))
    for r in out:
        if r["un"] in ("1263", "3082", "1203", "1993") :
            print("  UN %s | %s | lq=%s pkg=%s ibc=%s tank=%s tankprov=%s seg=%s ems=%s" % (
                r["un"], r["psn"][:26], r["lq"], r["pkg"], r["ibc"], r["tank"], r["tankprov"], r["seg"], r["ems"]))
    doc.close()


if __name__ == "__main__":
    main()