"""contact_sheet.py - Ghép ảnh thu nhỏ có đánh số để rà ảnh thừa/hỏng bằng mắt.
python contact_sheet.py data/phone_dump   -> data/sheets/sheet_01.jpg, sheet_02.jpg ...
"""
import os
import sys

import cv2
import numpy as np

COLS, ROWS = 5, 4          # 20 ảnh mỗi tờ
TW, TH, LABEL_H = 300, 225, 24

if len(sys.argv) < 2:
    sys.exit(__doc__)
src = sys.argv[1]
files = sorted(f for f in os.listdir(src) if f.lower().endswith((".jpg", ".jpeg")))
os.makedirs("data/sheets", exist_ok=True)
per = COLS * ROWS
for s in range(0, len(files), per):
    sheet = np.full((ROWS * (TH + LABEL_H), COLS * TW, 3), 255, np.uint8)
    for i, f in enumerate(files[s:s + per]):
        img = cv2.imread(os.path.join(src, f))
        if img is None:
            continue
        if img.shape[0] > img.shape[1]:  # ảnh dọc -> xoay sang trái cho dễ nhìn
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        thumb = cv2.resize(img, (TW, TH), interpolation=cv2.INTER_AREA)
        r, c = divmod(i, COLS)
        y0, x0 = r * (TH + LABEL_H), c * TW
        sheet[y0 + LABEL_H:y0 + LABEL_H + TH, x0:x0 + TW] = thumb
        cv2.putText(sheet, f"{s + i + 1} | {os.path.splitext(f)[0]}", (x0 + 4, y0 + 17),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
    out = f"data/sheets/sheet_{s // per + 1:02d}.jpg"
    cv2.imwrite(out, sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
print(f"Đã tạo {(len(files) + per - 1) // per} tờ trong data/sheets/")
