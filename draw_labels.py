"""draw_labels.py - Vẽ nhãn YOLO lên ảnh, ghép thành bảng để kiểm tra bằng mắt.
  python draw_labels.py            -> 12 ảnh rải đều
  python draw_labels.py L004_1 L076_1 L106_1 ...   -> các ảnh chỉ định
Ra: data/preview_labels.jpg
"""
import os
import sys

import cv2
import numpy as np

IMG, LBL = "data/images_all", "data/labels_all"
NAMES = ["A", "B", "C"]
COLORS = [(0, 128, 255), (255, 0, 255), (0, 200, 0)]
N, COLS = 12, 4
all_names = sorted(os.path.splitext(f)[0] for f in os.listdir(IMG) if f.lower().endswith(".jpg"))
names = sys.argv[1:] or [all_names[i] for i in np.linspace(0, len(all_names) - 1, N).round().astype(int)]

tiles = []
for n in names:
    img = cv2.imread(os.path.join(IMG, n + ".jpg"))
    h, w = img.shape[:2]
    with open(os.path.join(LBL, n + ".txt")) as f:
        for line in f:
            p = line.split()
            if len(p) != 5:
                continue
            c = int(p[0])
            cx, cy, bw, bh = (float(v) for v in p[1:])
            x1, y1 = int((cx - bw / 2) * w), int((cy - bh / 2) * h)
            x2, y2 = int((cx + bw / 2) * w), int((cy + bh / 2) * h)
            cv2.rectangle(img, (x1, y1), (x2, y2), COLORS[c], 2)
            cv2.putText(img, NAMES[c], (x1, max(y1 - 4, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS[c], 2)
    cv2.putText(img, n, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    tiles.append(img)
while len(tiles) % COLS:
    tiles.append(np.zeros_like(tiles[0]))
sheet = np.vstack([np.hstack(tiles[r * COLS:(r + 1) * COLS]) for r in range(len(tiles) // COLS)])
cv2.imwrite("data/preview_labels.jpg", cv2.resize(sheet, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA))
print(f"Đã ghi data/preview_labels.jpg ({len(names)} ảnh)")
