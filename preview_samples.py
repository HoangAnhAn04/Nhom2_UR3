"""preview_samples.py - Ghép tối đa 12 ảnh để kiểm tra bằng mắt, vẽ 4 ô lên.
  python preview_samples.py              -> 12 ảnh rải đều toàn bộ bộ dữ liệu
  python preview_samples.py ngoai_khay   -> ảnh có chữ này trong cột note của metadata.csv
"""
import csv
import os
import sys

import cv2
import numpy as np

from check_tray import load_config

cfg = load_config()
N, COLS = 12, 4
all_files = sorted(f for f in os.listdir("data/images_all") if f.lower().endswith(".jpg"))
if len(sys.argv) > 1:
    key = sys.argv[1]
    with open("data/metadata.csv", newline="", encoding="utf-8-sig") as f:
        files = [r["filename"] for r in csv.DictReader(f)
                 if key in r["note"] and r["filename"].endswith("_1.jpg")][:N]
    out = f"data/preview_{key}.jpg"
else:
    files = [all_files[i] for i in np.linspace(0, len(all_files) - 1, N).round().astype(int)]
    out = "data/preview_samples.jpg"
if not files:
    sys.exit("Không có ảnh nào khớp")

tiles = []
for fn in files:
    img = cv2.imread(os.path.join("data/images_all", fn))
    for x1, y1, x2, y2 in cfg["tray"]["slots"].values():
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    cv2.putText(img, fn, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    tiles.append(img)
while len(tiles) % COLS:
    tiles.append(np.zeros_like(tiles[0]))
sheet = np.vstack([np.hstack(tiles[r * COLS:(r + 1) * COLS]) for r in range(len(tiles) // COLS)])
cv2.imwrite(out, cv2.resize(sheet, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA))
print(f"Đã ghi {out} ({len(files)} ảnh)")
