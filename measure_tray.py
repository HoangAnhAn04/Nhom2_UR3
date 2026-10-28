"""measure_tray.py - Đo vùng cắt (crop_norm) và 4 ô (tray.slots) bằng cách bấm chuột.
Chạy từ thư mục gốc repo:
  python measure_tray.py crop  data/refs/REF_00.jpg   (bấm 2 góc vùng cần cắt trên ảnh gốc)
  python measure_tray.py slots data/refs/REF_00.jpg   (bấm 2 góc của từng ô, trên ảnh đã cắt)
Phím: u = hoàn tác điểm vừa bấm | Enter = xác nhận khi đủ điểm | Esc = thoát
"""
import json
import sys

import cv2

from check_tray import load_config
from imgio import read_oriented

COLORS = [(0, 255, 0), (0, 200, 255), (255, 120, 0), (255, 0, 255)]


def collect_points(img, prompts, scale, pairs=False):
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    base = cv2.resize(img, None, fx=scale, fy=scale, interpolation=interp)
    pts, n, win = [], len(prompts), "measure_tray"

    def redraw():
        d = base.copy()
        for i, (x, y) in enumerate(pts):
            c = COLORS[(i // 2) % 4] if pairs else (0, 0, 255)
            cv2.circle(d, (round(x * scale), round(y * scale)), 4, c, -1)
            if pairs and i % 2 == 1:
                (xa, ya) = pts[i - 1]
                cv2.rectangle(d, (round(xa * scale), round(ya * scale)),
                              (round(x * scale), round(y * scale)), c, 2)
        msg = prompts[len(pts)] if len(pts) < n else "Du diem. Enter = luu, u = hoan tac"
        cv2.putText(d, msg, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        cv2.imshow(win, d)

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(pts) < n:
            pts.append((x / scale, y / scale))
            redraw()

    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)
    redraw()
    result = None
    while True:
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break
        if k == ord("u") and pts:
            pts.pop()
            redraw()
        if k == 13 and len(pts) == n:
            result = list(pts)
            break
    cv2.destroyAllWindows()
    return result


def to_final(img, cfg):
    h, w = img.shape[:2]
    x1n, y1n, x2n, y2n = cfg["image"]["crop_norm"]
    crop = img[round(h * y1n):round(h * y2n), round(w * x1n):round(w * x2n)]
    return cv2.resize(crop, (cfg["image"]["width"], cfg["image"]["height"]),
                      interpolation=cv2.INTER_AREA)


def run_crop(path, cfg):
    img = read_oriented(path, cfg)
    if img is None:
        sys.exit(f"Không đọc được {path}")
    h, w = img.shape[:2]
    print(f"Ảnh sau khi xoay: {w}x{h}")
    pts = collect_points(img, ["Bam GOC TREN-TRAI vung can cat", "Bam GOC DUOI-PHAI vung can cat"],
                         min(1.0, 1100 / w, 800 / h))
    if not pts:
        return
    (xa, ya), (xb, yb) = pts
    x1, x2 = sorted((xa, xb))
    y1, y2 = sorted((ya, yb))
    cx, cy, bw, bh = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
    if bw / bh > w / h:      # ép đúng tỉ lệ của ảnh gốc (4:3) bằng cách nới cạnh ngắn
        bh = bw * h / w
    else:
        bw = bh * w / h
    if bw > w or bh > h:
        bw, bh = w, h
    x1 = min(max(0.0, cx - bw / 2), w - bw)
    y1 = min(max(0.0, cy - bh / 2), h - bh)
    norm = [round(x1 / w, 4), round(y1 / h, 4), round((x1 + bw) / w, 4), round((y1 + bh) / h, 4)]
    print('\nDán vào config.json, mục "image":')
    print(f'  "crop_norm": {json.dumps(norm)}')
    crop = img[round(y1):round(y1 + bh), round(x1):round(x1 + bw)]
    out = cv2.resize(crop, (cfg["image"]["width"], cfg["image"]["height"]), interpolation=cv2.INTER_AREA)
    cv2.imwrite("data/preview_crop.jpg", out)
    print("Ảnh xem trước vùng cắt: data/preview_crop.jpg")


def overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def run_slots(path, cfg):
    img = read_oriented(path, cfg)
    if img is None:
        sys.exit(f"Không đọc được {path}")
    W, H = cfg["image"]["width"], cfg["image"]["height"]
    if img.shape[1] != W or img.shape[0] != H:
        img = to_final(img, cfg)   # ảnh gốc: cắt theo crop_norm hiện có trong config.json
    prompts = []
    for s in (1, 2, 3, 4):
        name = cfg["tray"]["names"][str(s)]
        prompts += [f"Slot {s} ({name}): bam GOC TREN-TRAI", f"Slot {s} ({name}): bam GOC DUOI-PHAI"]
    pts = collect_points(img, prompts, 1.5, pairs=True)
    if not pts:
        return
    rects = {}
    for i in range(4):
        (xa, ya), (xb, yb) = pts[2 * i], pts[2 * i + 1]
        rects[str(i + 1)] = [round(min(xa, xb)), round(min(ya, yb)), round(max(xa, xb)), round(max(ya, yb))]
    for i in range(1, 5):
        for j in range(i + 1, 5):
            if overlaps(rects[str(i)], rects[str(j)]):
                print(f"CẢNH BÁO: ô {i} và ô {j} chồng lên nhau, hãy đo lại")
    print('\nDán vào config.json, mục "tray" -> "slots":')
    print('    "slots": {' + ", ".join(f'"{k}": {v}' for k, v in rects.items()) + "},")
    for (k, (x1, y1, x2, y2)), c in zip(rects.items(), COLORS):
        cv2.rectangle(img, (x1, y1), (x2, y2), c, 2)
        cv2.putText(img, f"{k}:{cfg['tray']['names'][k]}", (x1 + 6, y1 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, c, 2)
    cv2.imwrite("data/preview_slots_measured.jpg", img)
    print("Ảnh kiểm tra: data/preview_slots_measured.jpg")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("crop", "slots"):
        sys.exit(__doc__)
    cfg = load_config()
    (run_crop if sys.argv[1] == "crop" else run_slots)(sys.argv[2], cfg)
