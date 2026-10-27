"""make_plan.py - Sinh data/shoot_plan.csv (metadata) và data/shoot_order.csv (thứ tự chụp, có REF).
Quy ước: A1,A2,B1,C1 chỉ ghi vật có TÂM trong ô. Vật giữa ô / ngoài khay chỉ ghi trong note.
Chạy: python make_plan.py
"""
import csv
import os
import random
import sys
from collections import Counter
from itertools import product

START = 1
SESSION = "S02"
PHOTOGRAPHER = "Nam"
SEED = 42
SHOTS = 3
REF_EVERY = 20
PLAN, ORDER = "data/shoot_plan.csv", "data/shoot_order.csv"

COUNTS = {"du": 20, "thieu": 32, "sai_o": 28, "du_vat": 16, "che": 14}  # tổng 110
HINTS = ["giua_o", "lech_len", "lech_xuong", "lech_trai", "lech_phai", "xoay_45", "xoay_90"]
FULL = ("A", "A", "B", "C")
CELLS = ("A1", "A2", "B1", "C1")


def build_patterns():
    thieu = [tuple(c if m else "-" for c, m in zip(FULL, mask)) + ("",)
             for mask in product((0, 1), repeat=4) if not all(mask)]
    thieu.reverse()  # khay trống xuống cuối; các kiểu thiếu 1 vật được lặp nhiều hơn
    che = [FULL + (f"che_{cell}_{pct}",) for cell in CELLS for pct in (30, 60, 80)]
    return {
        "du": [FULL + ("",)],
        "thieu": thieu,
        "sai_o": [
            ("B", "A", "A", "C", ""), ("A", "B", "A", "C", ""),
            ("C", "A", "B", "A", ""), ("A", "C", "B", "A", ""),
            ("A", "A", "C", "B", ""),
            ("-", "-", "B", "C", "A_giua_A1-A2"),
            ("A", "A", "-", "C", "B_giua_B1-C1"),
            ("A", "-", "B", "C", "A_ngoai_khay"),
        ],
        "du_vat": [  # cần pin thứ 3; B và C chỉ có 1
            ("A+A", "A", "B", "C", ""), ("A", "A+A", "B", "C", ""),
            ("A", "A", "B+A", "C", ""), ("A", "A", "B", "C+A", ""),
        ],
        "che": che,
    }


def main():
    if os.path.exists(PLAN) or os.path.exists(ORDER):
        sys.exit("Đã có shoot_plan.csv / shoot_order.csv. Đổi tên file cũ trước khi sinh lại.")
    patterns = build_patterns()
    layouts = []
    for cond, n in COUNTS.items():
        pats = patterns[cond]
        for i in range(n):
            layouts.append((cond,) + pats[i % len(pats)])
    random.Random(SEED).shuffle(layouts)

    rows, order = [], [{"order": 0, "filename": "REF_00.jpg", "kind": "ref"}]
    ref_n = 0
    for k, (cond, a1, a2, b1, c1, note) in enumerate(layouts):
        lid = f"L{START + k:03d}"
        full_note = ";".join(x for x in (note, "dat_" + HINTS[k % len(HINTS)]) if x)
        for s in range(1, SHOTS + 1):
            fn = f"{lid}_{s}.jpg"
            rows.append({"filename": fn, "layout_id": lid, "session": SESSION,
                         "photographer": PHOTOGRAPHER, "condition": cond,
                         "A1": a1, "A2": a2, "B1": b1, "C1": c1, "note": full_note})
            order.append({"order": len(order), "filename": fn, "kind": "photo"})
        if (k + 1) % REF_EVERY == 0 and k + 1 < len(layouts):
            ref_n += 1
            order.append({"order": len(order), "filename": f"REF_{ref_n:02d}.jpg", "kind": "ref"})
    ref_n += 1
    order.append({"order": len(order), "filename": f"REF_{ref_n:02d}.jpg", "kind": "ref"})

    os.makedirs("data", exist_ok=True)
    for path, data in ((PLAN, rows), (ORDER, order)):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)

    print(f"{len(layouts)} bố trí, {len(rows)} ảnh, {ref_n + 1} ảnh mốc REF, tổng {len(order)} lần bấm máy")
    print("Theo condition:", dict(Counter(l[0] for l in layouts)))
    objs = Counter()
    for l in layouts:
        for cell in l[1:5]:
            for o in cell.split("+"):
                if o != "-":
                    objs[o] += SHOTS
    print("Số vật theo lớp (chưa tính vật giữa ô/ngoài khay):", dict(objs))


if __name__ == "__main__":
    main()
