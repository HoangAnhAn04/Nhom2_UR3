"""split_batches.py - Chia ảnh thành đợt gán nhãn theo số bố trí (copy, không di chuyển)."""
import os
import shutil

SRC = "data/images_all"
BATCHES = {1: (1, 30), 2: (31, 60), 3: (61, 90), 4: (91, 110)}

for b, (lo, hi) in BATCHES.items():
    dst = f"data/label_batches/batch{b}"
    os.makedirs(dst, exist_ok=True)
    n = 0
    for f in sorted(os.listdir(SRC)):
        if f.lower().endswith(".jpg") and f.startswith("L") and lo <= int(f[1:4]) <= hi:
            shutil.copy2(os.path.join(SRC, f), dst)
            n += 1
    print(f"batch{b}: L{lo:03d}-L{hi:03d} -> {n} ảnh")
