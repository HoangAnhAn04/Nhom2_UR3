"""audit_plan.py - So số vật mỗi lớp theo shoot_plan.csv với số khung trong labels_all."""
import csv, os
from collections import Counter

sp = {r["image"]: r["split"] for r in csv.DictReader(open("data/splits.csv", encoding="utf-8-sig"))}
for r in csv.DictReader(open("data/shoot_plan.csv", encoding="utf-8-sig")):
    stem = r["filename"][:-4]
    exp = Counter()
    for col in ("A1", "A2", "B1", "C1"):
        for t in r[col].split("+"):
            if t.strip() in ("A", "B", "C"):
                exp["ABC".index(t.strip())] += 1
    got = Counter(int(l.split()[0]) for l in open(f"data/labels_all/{stem}.txt") if l.strip())
    if exp != got:
        print(f"{stem:8} {sp.get(stem,'?'):5} {r['condition']:7} {r['note']:32} "
              f"kế hoạch A/B/C={exp[0]}/{exp[1]}/{exp[2]}  nhãn={got[0]}/{got[1]}/{got[2]}")
