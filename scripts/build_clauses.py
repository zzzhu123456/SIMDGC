import json
import re

pages = [json.loads(l) for l in open("data/main_pages.jsonl", encoding="utf-8")]
PT = {p["page"]: p["text"] for p in pages}

TEXT_RANGES = [(13, 226), (227, 812), (813, 836), (1147, 1198), (1199, 1222)]

PART_RE = re.compile(r"^第\s?(\d)\s?部分\s*[–\-—]?\s*(.*)$")
CHAP_RE = re.compile(r"^第\s?(\d+\.\d+)\s?章\s*[–\-—]?\s*(.*)$")
SKIP_RE = re.compile(r"^(DANKA\\|MSC ?\d|附件 ?8|索\s*引|附\s*录\s*$|■+$|_{3,}$|第\s?\d+\s?部分\s*[–\-—]|第\s?\d+\.\d+\s?章\s*[–\-—])")
CLAUSE_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,3}){1,4})(?:\s+(\S.*))?$")
CODE_RE = re.compile(r"^(P\d{3}|LP\d{3}|IBC\d{2,3}|BK\d|T\d{1,2})(?:（([a-c])）)?$")
NUM_RE = re.compile(r"^(\d{1,3})$")

# page -> (part, chapter) from running headers, forward filled
ctx = {}
cur_part = cur_chap = None
for p in pages:
    for line in p["text"].splitlines()[:6]:
        s = line.strip()
        m = PART_RE.match(s)
        if m:
            cur_part = ("第%s部分" % m.group(1), m.group(2).strip())
        m = CHAP_RE.match(s)
        if m:
            cur_chap = ("第%s章" % m.group(1), m.group(2).strip())
    ctx[p["page"]] = (cur_part, cur_chap)

clauses = []
for lo, hi in TEXT_RANGES:
    unit = None
    for pno in range(lo, hi + 1):
        part, chap = ctx.get(pno, (None, None))
        lines = PT[pno].splitlines()
        prev_skipped = False
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if SKIP_RE.match(s):
                prev_skipped = True
                continue
            if re.fullmatch(r"[1-7]", s) and prev_skipped:
                continue
            prev_skipped = False
            chap_num = chap[0][1:-1] if chap else ""
            new = None
            m = CLAUSE_RE.match(s)
            if m:
                new = (m.group(1), "clause")
                rest = (m.group(2) or "").strip()
            elif CODE_RE.match(s):
                new = (CODE_RE.match(s).group(1), "code")
                rest = ""
            elif chap_num == "3.3" and NUM_RE.match(s):
                new = ("SP" + s, "sp")
                rest = ""
            if new:
                uid, kind = new
                if unit:
                    clauses.append(unit)
                unit = {"id": uid, "kind": kind, "page": pno, "part": part[0] if part else "",
                        "partTitle": part[1] if part else "", "chapter": chap[0] if chap else "",
                        "chapterTitle": chap[1] if chap else "", "text": rest}
            elif unit is not None:
                unit["text"] = (unit["text"] + "\n" + s).strip("\n")
    if unit:
        clauses.append(unit)
        unit = None

print("clauses:", len(clauses))
from collections import Counter
print("kinds:", Counter(c["kind"] for c in clauses))
print("chapters:", Counter(c["chapter"] for c in clauses).most_common(30))
for c in clauses[:3]:
    print("  ", c["id"], c["chapter"], c["text"][:60].replace("\n", " | "))
sp = [c for c in clauses if c["kind"] == "sp"]
print("SP units:", len(sp), "e.g.", [c["id"] for c in sp[:12]], "max", max((int(c["id"][2:]) for c in sp), default=0))
with open("data/clauses.json", "w", encoding="utf-8") as fh:
    json.dump(clauses, fh, ensure_ascii=False)