"""split_dataset.py - Chia train/val/test THEO BỐ TRÍ, tạo data/dataset/{images,labels}/{train,val,test},
splits.csv và data.yaml.   Chạy: python split_dataset.py
"""
import csv
import os
import random
import shutil
from collections import Counter, defaultdict

IMG, LBL = "data/images_all", "data/labels_all"
OUT = "data/dataset"
SEED, VAL_FRAC, TEST_FRAC = 42, 0.15, 0.15
NAMES = ["A", "B", "C"]

# Gom ảnh theo bố trí (4 ký tự đầu của tên: L001)
layouts = defaultdict(list)
for f in sorted(os.listdir(IMG)):
    if f.lower().endswith(".jpg"):
        layouts[f[:4]].append(os.path.splitext(f)[0])


def is_empty(stem):
    return os.path.getsize(os.path.join(LBL, stem + ".txt")) == 0


# Bố trí trống = mọi ảnh của nó có file nhãn rỗng
groups = {"trong": [], "co_vat": []}
for lay, stems in sorted(layouts.items()):
    groups["trong" if all(is_empty(s) for s in stems) else "co_vat"].append(lay)

rng = random.Random(SEED)
assign = {}
for g, lays in groups.items():
    rng.shuffle(lays)
    n = len(lays)
    n_val = max(1, round(n * VAL_FRAC)) if n >= 3 else 0
    n_test = max(1, round(n * TEST_FRAC)) if n >= 3 else 0
    for i, lay in enumerate(lays):
        assign[lay] = "val" if i < n_val else "test" if i < n_val + n_test else "train"

# Copy file
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
        rows.append((s, lay, sp))

with open("data/splits.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["image", "layout", "split"])
    w.writerows(rows)

# data.yaml: cố ý KHÔNG ghi 'path' -> Ultralytics lấy thư mục chứa file yaml làm gốc
with open(f"{OUT}/data.yaml", "w", encoding="utf-8") as f:
    f.write("train: images/train\nval: images/val\ntest: images/test\n")
    f.write(f"nc: {len(NAMES)}\nnames:\n")
    for i, n in enumerate(NAMES):
        f.write(f"  {i}: {n}\n")

# Kiểm tra rò rỉ: mỗi bố trí chỉ nằm trong 1 tập
by_lay = defaultdict(set)
for _, lay, sp in rows:
    by_lay[lay].add(sp)
assert all(len(v) == 1 for v in by_lay.values()), "Rò rỉ: một bố trí nằm ở nhiều tập!"

# Thống kê
print(f"{'tập':<6}{'bố trí':>8}{'ảnh':>6}{'A':>6}{'B':>6}{'C':>6}{'ảnh trống':>11}")
for sp in ("train", "val", "test"):
    stems = [s for s, _, p in rows if p == sp]
    cnt, empty = Counter(), 0
    for s in stems:
        lines = [l.split()[0] for l in open(f"{LBL}/{s}.txt") if l.strip()]
        cnt.update(int(c) for c in lines)
        empty += not lines
    nl = len({lay for _, lay, p in rows if p == sp})
    print(f"{sp:<6}{nl:>8}{len(stems):>6}{cnt[0]:>6}{cnt[1]:>6}{cnt[2]:>6}{empty:>11}")
print("Đã ghi data/splits.csv và", f"{OUT}/data.yaml")
