"""check_labels.py - Kiểm tra nhãn YOLO trong data/labels_all so với data/images_all."""
import os
from collections import Counter

IMG, LBL = "data/images_all", "data/labels_all"
imgs = {os.path.splitext(f)[0] for f in os.listdir(IMG) if f.lower().endswith(".jpg")}
lbls = {os.path.splitext(f)[0] for f in os.listdir(LBL) if f.endswith(".txt")}

print(f"Ảnh: {len(imgs)} | File nhãn: {len(lbls)}")
print("Ảnh thiếu nhãn:", sorted(imgs - lbls) or "không")
print("Nhãn không có ảnh:", sorted(lbls - imgs) or "không")

cls, errors, per_img = Counter(), [], {}
for name in sorted(lbls & imgs):
    n = 0
    with open(os.path.join(LBL, name + ".txt")) as f:
        for i, line in enumerate(f, 1):
            p = line.split()
            if not p:
                continue
            try:
                c, vals = int(p[0]), list(map(float, p[1:]))
                assert len(p) == 5 and c in (0, 1, 2)
                assert all(0 <= v <= 1 for v in vals) and vals[2] > 0 and vals[3] > 0
            except Exception:
                errors.append(f"{name}.txt dòng {i}: {line.strip()}")
                continue
            cls[c] += 1
            n += 1
    per_img[name] = n

print("Số khung theo lớp (0=A, 1=B, 2=C):", dict(sorted(cls.items())))
print("Ảnh có 0 khung:", [k for k, v in per_img.items() if v == 0] or "không")
print("Dòng lỗi:", errors or "không")
