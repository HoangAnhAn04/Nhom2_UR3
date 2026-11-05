import csv
from check_tray import load_config, slot_rects, locate
cfg = load_config(); rects = slot_rects(cfg); m = cfg["thresholds"]["boundary_margin_px"]
COL = {1: "A1", 2: "A2", 3: "B1", 4: "C1"}; NAME = {0: "A", 1: "B", 2: "C"}
meta = {r["filename"]: r for r in csv.DictReader(open("data/metadata.csv", encoding="utf-8-sig"))}
import re
checked = skipped = 0
bad_skip = []
for fn, r in meta.items():
    cells = {n: [] for n in rects}; odd = 0
    for line in open(f"data/labels_all/{fn[:-4]}.txt"):
        if not line.strip():
            continue
        c, cx, cy = line.split()[:3]
        kind, n = locate((float(cx) * 640, float(cy) * 480), rects, m)
        if kind == "slot":
            cells[n].append(NAME[int(c)])
        else:
            odd += 1
    if odd:
        skipped += 1
        if not re.search(r"[ABC]_giua_|ngoai_khay", r["note"]):
            bad_skip.append(fn)
        continue
    checked += 1
    got = {n: "+".join(sorted(v)) if v else "-" for n, v in cells.items()}
    exp = {n: "+".join(sorted(r[COL[n]].split("+"))) for n in rects}
    if got != exp:
        print(fn, "| metadata:", [r[COL[n]] for n in rects], "| nhãn:", [got[n] for n in rects])
print(f"Đã kiểm tra {checked} ảnh, bỏ qua {skipped} ảnh có vật giữa ô/ngoài khay")
print("Bỏ qua nhưng note không nói giữa ô/ngoài khay:", bad_skip)