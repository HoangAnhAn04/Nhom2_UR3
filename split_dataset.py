"""split_dataset.py - Chia 60/20/20 THEO BỐ TRÍ, phân tầng theo condition (đề yêu cầu ở README mục 11.4).
Ra: data/dataset/{images,labels}/{train,val,test}, data/dataset/data.yaml, data/splits.csv
"""
import csv
import os
import random
import shutil
from collections import Counter, defaultdict

IMG, LBL, OUT = "data/images_all", "data/labels_all", "data/dataset"
SEED = 42
NAMES = ["A", "B", "C"]

cond = {r["layout_id"]: r["condition"]
        for r in csv.DictReader(open("data/shoot_plan.csv", encoding="utf-8-sig"))}
layouts = defaultdict(list)
for f in sorted(os.listdir(IMG)):
    if f.lower().endswith(".jpg"):
        layouts[f[:4]].append(os.path.splitext(f)[0])

groups = defaultdict(list)          # khay trống (nhãn rỗng) chia riêng, còn lại theo condition
for lay, stems in sorted(layouts.items()):
    empty = all(os.path.getsize(f"{LBL}/{s}.txt") == 0 for s in stems)
    groups["trong" if empty else cond[lay]].append(lay)

rng = random.Random(SEED)
assign = {}
for key, lays in sorted(groups.items()):
    rng.shuffle(lays)
    n = len(lays)
    n_val = n_test = max(1, round(0.2 * n)) if n >= 3 else 0
    for i, lay in enumerate(lays):
        assign[lay] = "val" if i < n_val else "test" if i < n_val + n_test else "train"

n_test_imgs = sum(len(layouts[l]) for l, s in assign.items() if s == "test")
assert n_test_imgs >= 60, f"Test chỉ có {n_test_imgs} ảnh (đề yêu cầu >= 60)"

if os.path.exists(OUT):
    shutil.rmtree(OUT)
rows = []
for lay, stems in sorted(layouts.items()):
    sp = assign[lay]
    for sub in ("images", "labels"):
        os.makedirs(f"{OUT}/{sub}/{sp}", exist_ok=True)
    for s in stems:
        shutil.copy2(f"{IMG}/{s}.jpg", f"{OUT}/images/{sp}/{s}.jpg")
        shutil.copy2(f"{LBL}/{s}.txt", f"{OUT}/labels/{sp}/{s}.txt")
        rows.append((s + ".jpg", lay, sp))

with open("data/splits.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["filename", "layout_id", "split"])
    w.writerows(rows)

with open(f"{OUT}/data.yaml", "w", encoding="utf-8") as f:
    f.write("train: images/train\nval: images/val\ntest: images/test\nnc: 3\nnames:\n")
    for i, n in enumerate(NAMES):
        f.write(f"  {i}: {n}\n")

print(f"{'tập':<6}{'bố trí':>8}{'ảnh':>6}{'A':>6}{'B':>6}{'C':>6}{'ảnh trống':>11}")
for sp in ("train", "val", "test"):
    stems = [r[0][:-4] for r in rows if r[2] == sp]
    cnt, empty = Counter(), 0
    for s in stems:
        c = [l.split()[0] for l in open(f"{LBL}/{s}.txt") if l.strip()]
        cnt.update(int(x) for x in c)
        empty += not c
    print(f"{sp:<6}{len({r[1] for r in rows if r[2] == sp}):>8}{len(stems):>6}"
          f"{cnt['0']+cnt[0]:>6}{cnt[1]:>6}{cnt[2]:>6}{empty:>11}")
print("\ncondition theo tập (số bố trí):")
for key, lays in sorted(groups.items()):
    c = Counter(assign[l] for l in lays)
    print(f"  {key:8} train {c['train']:2} | val {c['val']:2} | test {c['test']:2}")
