import json
import re
from collections import Counter

chg = json.load(open("data/changelog.json", encoding="utf-8"))
items = [it for it in chg["items"] if it["kind"] in ("clause", "sp", "un")]

colnames = [("第1栏", "UN编号"), ("第2栏", "正确运输名称"), ("第3栏", "类别"), ("第4栏", "副危险"),
            ("第5栏", "包装类"), ("第6栏", "特殊规定"), ("第7a栏", "限量"), ("第7b栏", "可免除量"),
            ("第7(a)栏", "限量"), ("第7(b)栏", "可免除量"), ("第8栏", "包装导则"), ("第9栏", "包装特殊规定"),
            ("第10栏", "IBC导则"), ("第11栏", "IBC特殊规定"), ("第13栏", "罐柜导则"), ("第14栏", "罐柜特殊规定"),
            ("第15栏", "EmS"), ("第16a栏", "积载与操作"), ("第16b栏", "隔离"), ("第17栏", "特性与注意事项")]
cols = Counter()
for it in items:
    for key, name in colnames:
        if it["text"].count(key):
            cols[name] += it["text"].count(key)
print("=== 改动涉及的“栏”（一览表列）出现次数 ===")
for k, v in cols.most_common(14):
    print("  %-14s %d" % (k, v))

print("\n=== 按章节的改动条目数（前 15）===")
cc = Counter()
for it in items:
    cc[it["chapter"] or it["part"]] += 1
for k, v in cc.most_common(15):
    print("  %-10s %d" % (k, v))

print("\n=== 改动“动作”分布 ===")
verbs = ["增加", "删除", "替换", "插入", "修改", "新增", "整体替换", "重新编号"]
vc = Counter()
for it in items:
    for v in verbs:
        if v in it["text"]:
            vc[v] += 1
print("  ", dict(vc))

print("\n=== 典型改动样本（一览表）===")
uns = [it for it in items if it["kind"] == "un"]
for it in uns[:3] + uns[-4:]:
    print("  UN %s: %s" % (it["ref"], it["text"].replace("\n", " / ")[:120]))

print("\n=== 条款级改动样本 ===")
for it in [i for i in items if i["kind"] == "clause"][:8]:
    print("  %-10s %s" % (it["ref"], it["text"].replace("\n", " / ")[:110]))

print("\n=== 改动到的特殊规定 ===")
print("  ", ", ".join(sorted(chg["bySp"], key=lambda s: int(s[2:]))))