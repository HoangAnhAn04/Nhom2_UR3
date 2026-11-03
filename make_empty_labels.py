"""make_empty_labels.py - Tạo file nhãn rỗng cho ảnh đã xác nhận là khay trống.
Dùng: python make_empty_labels.py L005_1 L005_2 L005_3
"""
import os
import sys

LBL = "data/labels_all"
os.makedirs(LBL, exist_ok=True)
for name in sys.argv[1:]:
    path = os.path.join(LBL, name + ".txt")
    if os.path.exists(path):
        print("Đã có, bỏ qua:", name)
    else:
        open(path, "w").close()
        print("Tạo file rỗng:", name)
