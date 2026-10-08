import base64
import json
import re
from collections import defaultdict

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN = re.compile(r"[A-Za-z0-9]")


def normalize(s):
    """Collapse spacing inserted by the PDF between CJK and Latin, keep Latin word gaps."""
    s = s.replace("\u00a0", " ")
    out = []
    for i, ch in enumerate(s):
        if ch == " ":
            prev = s[i - 1] if i else ""
            nxt = s[i + 1] if i + 1 < len(s) else ""
            if CJK.search(prev) or CJK.search(nxt):
                continue
            out.append(" ")
        else:
            out.append(ch)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def tokenize(text):
    toks = []
    i, n = 0, len(text)
    while i < n:
        if CJK.match(text[i]):
            j = i
            while j < n and CJK.match(text[j]):
                j += 1
            run = text[i:j]
            for k in range(len(run) - 1):
                toks.append(run[k:k + 2])
            i = j
        elif LATIN.match(text[i]):
            j = i
            while j < n and LATIN.match(text[j]):
                j += 1
            toks.append(text[i:j].lower())
            i = j
        else:
            i += 1
    return toks


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def main():
    dgl = json.load(open("data/dgl.json", encoding="utf-8"))
    clauses = json.load(open("data/clauses.json", encoding="utf-8"))
    idx = json.load(open("data/index_entries.json", encoding="utf-8"))

    docs = []
    search = []
    for r in dgl:
        t = normalize(" ".join([r["un"], r["psn"], r["cls"], r.get("sub", ""), r.get("sp", ""),
                                r.get("pkg", ""), r.get("pkgprov", ""), r.get("ibc", ""),
                                r.get("tank", ""), r.get("ems", ""), r.get("stow", ""),
                                r.get("seg", ""), r.get("prop", "")]))
        docs.append({"k": "d", "title": "UN %s %s" % (r["un"], r["psn"]),
                     "sub": "%s / 包装类%s / %s" % (r["cls"], r.get("pg", "-"), r.get("ems", "")),
                     "page": r["page"]})
        search.append(t)
    for c in clauses:
        t = normalize(" ".join([c["id"], c.get("chapterTitle", ""), c["text"]]))
        title = c["id"] + (" " + c["text"].split("\n")[0][:40] if c["text"] else "")
        docs.append({"k": "c", "title": title.strip(),
                     "sub": "%s %s" % (c["chapter"], c.get("chapterTitle", "")), "page": c["page"]})
        search.append(t)
    for e in idx:
        t = normalize(" ".join([e["name"], e["un"], e["cls"]]))
        docs.append({"k": "i", "title": e["name"], "sub": "UN %s / 第%s类" % (e["un"], e["cls"]),
                     "page": e["page"]})
        search.append(t)

    postings = defaultdict(list)
    lengths = []
    for did, text in enumerate(search):
        toks = tokenize(text)
        lengths.append(len(toks))
        if not toks:
            continue
        counts = defaultdict(int)
        for tk in toks:
            counts[tk] += 1
        for tk, c in counts.items():
            postings[tk].append((did, c))

    terms = sorted(postings)
    blobs = []
    for tk in terms:
        buf = bytearray()
        prev = 0
        for did, tf in postings[tk]:
            buf += varint(did - prev)
            buf += varint(tf)
            prev = did
        blobs.append(base64.b64encode(bytes(buf)).decode("ascii"))

    out = {"docCount": len(docs), "avgLen": sum(lengths) / max(1, len(lengths)),
           "terms": terms, "postings": blobs, "lengths": lengths}
    with open("web/data/search_index.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    with open("web/data/docs.json", "w", encoding="utf-8") as fh:
        json.dump({"docs": docs, "dgl": dgl, "clauses": clauses, "index": idx},
                  fh, ensure_ascii=False, separators=(",", ":"))
    import os
    print("docs:", len(docs), "terms:", len(terms), "avg len: %.1f" % out["avgLen"])
    print("search_index.json: %.2f MB" % (os.path.getsize("web/data/search_index.json") / 1e6))
    print("docs.json: %.2f MB" % (os.path.getsize("web/data/docs.json") / 1e6))


if __name__ == "__main__":
    main()