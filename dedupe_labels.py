"""dedupe_labels.py - Xóa dòng nhãn trùng y hệt trong data/labels_all (giữ thứ tự).  Chạy: python dedupe_labels.py"""
import os

LBL = "data/labels_all"
total = 0
for f in sorted(os.listdir(LBL)):
    if not f.endswith(".txt"):
        continue
    path = os.path.join(LBL, f)
    lines = [l.strip() for l in open(path) if l.strip()]
    uniq = list(dict.fromkeys(lines))
    if len(uniq) != len(lines):
        print(f"{f}: bỏ {len(lines) - len(uniq)} dòng trùng")
        total += len(lines) - len(uniq)
        with open(path, "w") as o:
            o.write("\n".join(uniq) + ("\n" if uniq else ""))
print("Tổng dòng trùng đã xóa:", total)
