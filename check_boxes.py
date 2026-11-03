"""check_boxes.py - Liệt kê khung quá nhỏ/quá lớn và bố trí có số khung lệch giữa các ảnh _1/_2/_3."""
import os
from collections import Counter, defaultdict

LBL = "data/labels_all"
per_layout = defaultdict(dict)
odd = []
for f in sorted(os.listdir(LBL)):
    if not f.endswith(".txt"):
        continue
    stem = f[:-4]
    cnt = Counter()
    for line in open(os.path.join(LBL, f)):
        p = line.split()
        if len(p) != 5:
            continue
        c, w, h = int(p[0]), float(p[3]), float(p[4])
        cnt[c] += 1
        if w < 0.03 or h < 0.03 or w > 0.5 or h > 0.5:
            odd.append(f"{stem}: lớp {c}, w={w:.3f}, h={h:.3f}")
    per_layout[stem[:4]][stem] = tuple(cnt.get(i, 0) for i in range(3))

print("Khung nhỏ/lớn bất thường:", odd or "không")
print("\nBố trí có (A,B,C) khác nhau giữa các ảnh (cần xem lại, chưa chắc là lỗi):")
for lay, d in per_layout.items():
    if len(set(d.values())) > 1:
        print(lay, d)
