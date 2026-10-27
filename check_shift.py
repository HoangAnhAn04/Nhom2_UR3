"""check_shift.py - Đo độ lệch của ảnh khay trống REF_xx so với REF_00,
tính theo pixel của ảnh đã cắt 640x480 (cùng đơn vị với tray.slots).
Chạy từ thư mục gốc repo:  python check_shift.py
"""
import glob
import os
import sys

import cv2
import numpy as np

from check_tray import load_config
from imgio import read_oriented

cfg = load_config()
W, H = cfg["image"]["width"], cfg["image"]["height"]
x1n, y1n, x2n, y2n = cfg["image"]["crop_norm"]


def load_crop(path):
    img = read_oriented(path, cfg, cv2.IMREAD_GRAYSCALE)
    if img is None:
        sys.exit(f"Không đọc được {path}")
    h, w = img.shape
    crop = img[round(h * y1n):round(h * y2n), round(w * x1n):round(w * x2n)]
    return np.float32(cv2.resize(crop, (W, H), interpolation=cv2.INTER_AREA))


paths = sorted(glob.glob("data/refs/REF_*.jpg"))
if not paths:
    sys.exit("Không thấy data/refs/REF_*.jpg")
ref = load_crop(paths[0])
win = cv2.createHanningWindow((W, H), cv2.CV_32F)
print(f"Tham chiếu: {os.path.basename(paths[0])} (đơn vị: pixel ảnh 640x480 đã cắt)")
for p in paths:
    (dx, dy), resp = cv2.phaseCorrelate(ref, load_crop(p), win)
    flag = "LECH" if max(abs(dx), abs(dy)) > 3 else "ok"
    print(f"{os.path.basename(p)}  dx={dx:+.1f}  dy={dy:+.1f}  resp={resp:.2f}  {flag}")
