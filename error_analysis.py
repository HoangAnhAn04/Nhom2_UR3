"""error_analysis.py - So dự đoán với nhãn trên một tập, lưu ảnh có lỗi, in độ tin cậy TP/FP.
  python error_analysis.py --split val
"""
import argparse
import os

import cv2
import numpy as np
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--weights", default="weights/best.pt")
ap.add_argument("--root", default="data/dataset")
ap.add_argument("--split", default="val", choices=["val", "test"])
ap.add_argument("--conf", type=float, default=0.25)
ap.add_argument("--iou", type=float, default=0.5)
a = ap.parse_args()

model = YOLO(a.weights)
NAMES = model.names
img_dir = f"{a.root}/images/{a.split}"
lbl_dir = f"{a.root}/labels/{a.split}"
out = f"data/errors_{a.split}"
os.makedirs(out, exist_ok=True)


def iou(a_, b_):
    x1, y1 = max(a_[0], b_[0]), max(a_[1], b_[1])
    x2, y2 = min(a_[2], b_[2]), min(a_[3], b_[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    u = (a_[2] - a_[0]) * (a_[3] - a_[1]) + (b_[2] - b_[0]) * (b_[3] - b_[1]) - inter
    return inter / u if u > 0 else 0


tp_conf, fp_list, wrong_list, fn_list = {}, [], [], []
for fn in sorted(os.listdir(img_dir)):
    if not fn.lower().endswith(".jpg"):
        continue
    stem = os.path.splitext(fn)[0]
    img = cv2.imread(os.path.join(img_dir, fn))
    h, w = img.shape[:2]
    gt = []
    for line in open(os.path.join(lbl_dir, stem + ".txt")):
        p = line.split()
        if len(p) == 5:
            c, cx, cy, bw, bh = int(p[0]), *(float(v) for v in p[1:])
            gt.append((c, [(cx - bw / 2) * w, (cy - bh / 2) * h, (cx + bw / 2) * w, (cy + bh / 2) * h]))
    r = model.predict(img, conf=a.conf, verbose=False)[0]
    preds = sorted(zip(r.boxes.cls.int().tolist(), r.boxes.conf.tolist(), r.boxes.xyxy.tolist()),
                   key=lambda t: -t[1])
    used, err = set(), False
    for c, cf, box in preds:
        best, bi = 0, None
        for i, (gc, gb) in enumerate(gt):
            if i not in used and iou(box, gb) > best:
                best, bi = iou(box, gb), i
        if bi is not None and best >= a.iou:
            used.add(bi)
            if gt[bi][0] == c:
                tp_conf.setdefault(NAMES[c], []).append(cf)
                continue
            wrong_list.append((stem, NAMES[gt[bi][0]], NAMES[c], cf))
            color = (0, 165, 255)
        else:
            fp_list.append((stem, NAMES[c], cf))
            color = (0, 0, 255)
        err = True
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"{NAMES[c]} {cf:.2f}", (x1, max(y1 - 4, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    for i, (gc, gb) in enumerate(gt):
        if i not in used:
            fn_list.append((stem, NAMES[gc]))
            err = True
            cv2.rectangle(img, tuple(map(int, gb[:2])), tuple(map(int, gb[2:])), (255, 0, 0), 2)
            cv2.putText(img, f"MISS {NAMES[gc]}", (int(gb[0]), int(gb[3]) + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    if err:
        cv2.imwrite(os.path.join(out, fn), img)

print(f"\nTập {a.split}, conf>={a.conf}, IoU>={a.iou}")
print("Dự đoán thừa (đỏ):", len(fp_list), "| nhầm lớp (cam):", len(wrong_list), "| bỏ sót (xanh dương):", len(fn_list))
for s, c, cf in sorted(fp_list, key=lambda t: -t[2]):
    print(f"  THỪA  {s}: {c} conf={cf:.2f}")
for s, g, p, cf in wrong_list:
    print(f"  NHẦM  {s}: nhãn {g}, đoán {p} conf={cf:.2f}")
for s, c in fn_list:
    print(f"  SÓT   {s}: {c}")
print("\nĐộ tin cậy dự đoán ĐÚNG (min / trung bình):")
for c, v in sorted(tp_conf.items()):
    print(f"  {c}: {min(v):.2f} / {np.mean(v):.2f}  (n={len(v)})")
if fp_list:
    print(f"Dự đoán thừa có conf cao nhất: {max(t[2] for t in fp_list):.2f}")
print(f"Ảnh lỗi lưu ở {out}")
