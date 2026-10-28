"""add_missing_label.py - Thêm khung mô hình dự đoán (conf>=0.7) mà chưa có nhãn trùng. Phải kiểm tra bằng mắt sau đó.
  python add_missing_label.py L010_1 L010_2 L010_3
"""
import os, sys
import cv2
from ultralytics import YOLO

IMG, LBL = "data/images_all", "data/labels_all"
model = YOLO("weights/best.pt")

def iou(a, b):
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    i = max(0, x2 - x1) * max(0, y2 - y1)
    u = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - i
    return i / u if u else 0

for stem in sys.argv[1:]:
    img = cv2.imread(f"{IMG}/{stem}.jpg"); h, w = img.shape[:2]
    path = f"{LBL}/{stem}.txt"
    gt = []
    for l in open(path):
        p = l.split()
        if len(p) == 5:
            cx, cy, bw, bh = (float(v) for v in p[1:])
            gt.append(((cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h))
    r = model.predict(img, conf=0.7, verbose=False)[0]
    new = []
    for c, box in zip(r.boxes.cls.int().tolist(), r.boxes.xyxy.tolist()):
        if all(iou(box, g) < 0.3 for g in gt):
            x1, y1, x2, y2 = box
            new.append(f"{c} {(x1+x2)/2/w:.6f} {(y1+y2)/2/h:.6f} {(x2-x1)/w:.6f} {(y2-y1)/h:.6f}")
    if new:
        with open(path, "a") as f:
            f.write(("\n" if gt else "") + "\n".join(new) + "\n")
    print(stem, "thêm", len(new), "khung")
