"""prepare_images.py - Chuẩn hóa ảnh điện thoại về 640x480 và kiểm tra metadata.csv.

Chạy từ thư mục gốc repo:  python prepare_images.py
Đầu vào : data/raw/L012_1.jpg ...      Đầu ra: data/images_all/, data/preview_slots.jpg
"""
import csv, os, re, sys, cv2
from collections import Counter
from check_tray import load_config
from imgio import read_oriented

RAW_DIR = "data/raw"
OUT_DIR = "data/images_all"
META = "data/metadata.csv"
PREVIEW = "data/preview_slots.jpg"
W, H = 640, 480
NAME_RE = re.compile(r"^(L\d{3})_(\d+)\.(jpg|jpeg|png)$", re.I)
STATE_RE = re.compile(r"^(-|[ABC](\+[ABC])*)$")
CONDITIONS = {"du", "thieu", "sai_o", "du_vat", "che"}


def crop_box(w, h, cfg):
    x1n, y1n, x2n, y2n = cfg["image"]["crop_norm"]
    return round(w * x1n), round(h * y1n), round(w * x2n), round(h * y2n)

def convert_images(cfg):
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(RAW_DIR)
                   if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if not files:
        sys.exit(f"Không thấy ảnh trong {RAW_DIR}")
    done, problems, first = [], [], None
    for f in files:
        m = NAME_RE.match(f)
        if not m:
            problems.append((f, "tên không đúng dạng L012_1.jpg"))
            continue
        img = read_oriented(os.path.join(RAW_DIR, f), cfg)
        if img is None:
            problems.append((f, "không đọc được"))
            continue
        h, w = img.shape[:2]
        if h > w:
            problems.append((f, f"ảnh dọc {w}x{h}, cần chụp ngang"))
            continue
        if abs(w / h - 4 / 3) > 0.02:
            problems.append((f, f"kích thước {w}x{h} không phải tỉ lệ 4:3"))
            continue

        # Thêm bước xoay ảnh để bù trừ góc nghiêng của camera
        (h_img, w_img) = img.shape[:2]
        center = (w_img // 2, h_img // 2)
        # Chỉnh số -1.5 (độ) này cho đến khi đường xanh dương thẳng đứng
        M = cv2.getRotationMatrix2D(center, -1.5, 1.0)
        img = cv2.warpAffine(img, M, (w_img, h_img), borderMode=cv2.BORDER_REPLICATE)

        cx1, cy1, cx2, cy2 = crop_box(w, h, cfg)
        img = img[cy1:cy2, cx1:cx2]

        out = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        name = f"{m.group(1)}_{m.group(2)}.jpg"
        cv2.imwrite(os.path.join(OUT_DIR, name), out, [cv2.IMWRITE_JPEG_QUALITY, 95])
        done.append(name)
        if first is None:
            first = out.copy()
    return done, problems, first


def draw_preview(img, cfg):
    names = cfg["tray"]["names"]
    for k, (x1, y1, x2, y2) in cfg["tray"]["slots"].items():
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(img, p1, p2, (0, 255, 0), 2)
        cv2.putText(img, f"{k}:{names[k]}", (p1[0] + 8, p1[1] + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imwrite(PREVIEW, img)


def check_metadata(done):
    if not os.path.exists(META):
        print(f"\n[metadata] Chưa có {META}")
        return
    with open(META, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    errors = []
    in_meta = set()
    for r in rows:
        fn = r.get("filename", "")
        in_meta.add(fn)
        m = NAME_RE.match(fn)
        if not m:
            errors.append(f"{fn}: tên file không đúng quy ước")
        elif m.group(1) != r.get("layout_id"):
            errors.append(f"{fn}: layout_id '{r.get('layout_id')}' không khớp tên file")
        if r.get("condition") not in CONDITIONS:
            errors.append(f"{fn}: condition '{r.get('condition')}' không hợp lệ")
        for col in ("A1", "A2", "B1", "C1"):
            if not STATE_RE.match(r.get(col, "")):
                errors.append(f"{fn}: cột {col} = '{r.get(col)}' không hợp lệ")
    for fn in sorted(set(done) - in_meta):
        errors.append(f"{fn}: có ảnh nhưng chưa có dòng trong metadata.csv")
    for fn in sorted(in_meta - set(done)):
        errors.append(f"{fn}: có trong metadata.csv nhưng chưa có ảnh đã chuẩn hóa")
    print(f"\n[metadata] {len(rows)} dòng, {len({r['layout_id'] for r in rows})} bố trí")
    print("[metadata] theo condition:", dict(Counter(r["condition"] for r in rows)))
    if errors:
        print(f"[metadata] {len(errors)} vấn đề:")
        for e in errors:
            print("  -", e)
    else:
        print("[metadata] OK, không phát hiện vấn đề")


def main():
    cfg = load_config()
    done, problems, first = convert_images(cfg)
    print(f"Đã chuẩn hóa {len(done)} ảnh -> {OUT_DIR} ({W}x{H})")
    if problems:
        print(f"{len(problems)} ảnh bị bỏ qua:")
        for f, why in problems:
            print(f"  - {f}: {why}")
    if first is not None:
        draw_preview(first, cfg)
        print(f"Ảnh xem trước 4 ô: {PREVIEW}")
    check_metadata(done)


if __name__ == "__main__":
    main()
