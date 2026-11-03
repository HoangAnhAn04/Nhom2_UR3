"""polygon_to_yolo.py - Đổi COCO JSON (polygon) của makesense.ai sang nhãn YOLO dạng khung.
Dùng: python polygon_to_yolo.py duong_dan/labels.json
Tên lớp phải là A, B, C (thứ tự 0, 1, 2).
"""
import json
import os
import sys

CLASSES = {"A": 0, "B": 1, "C": 2}
OUT = "data/labels_all"
os.makedirs(OUT, exist_ok=True)

data = json.load(open(sys.argv[1], encoding="utf-8"))
cat = {c["id"]: c["name"] for c in data["categories"]}
img = {i["id"]: i for i in data["images"]}
lines = {}

for a in data["annotations"]:
    name = cat[a["category_id"]]
    if name not in CLASSES:
        print("Bỏ qua lớp lạ:", name)
        continue
    im = img[a["image_id"]]
    W, H = im["width"], im["height"]
    pts = a["segmentation"][0]
    xs, ys = pts[0::2], pts[1::2]
    x1, x2, y1, y2 = min(xs), max(xs), min(ys), max(ys)
    row = f"{CLASSES[name]} {(x1+x2)/2/W:.6f} {(y1+y2)/2/H:.6f} {(x2-x1)/W:.6f} {(y2-y1)/H:.6f}"
    stem = os.path.splitext(os.path.basename(im["file_name"]))[0]
    lines.setdefault(stem, []).append(row)

for stem, rows in lines.items():
    path = os.path.join(OUT, stem + ".txt")
    existed = os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if existed and os.path.getsize(path) > 0:
            f.write("\n")
        f.write("\n".join(rows) + "\n")
print(f"Đã ghi {sum(map(len, lines.values()))} khung vào {len(lines)} file")
