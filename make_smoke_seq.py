"""make_smoke_seq.py - Chuỗi thử khói từ ảnh có sẵn để kiểm tra bridge --mode ai (KHÔNG phải chuỗi nộp bài).
Ra: data/smoke_seq/S01/step0..3.jpg
"""
import csv
import os
import shutil

PATTERNS = [("-", "-", "B", "-"), ("A", "-", "B", "-"), ("A", "A", "B", "-"), ("A", "A", "B", "C")]
rows = [r for r in csv.DictReader(open("data/shoot_plan.csv", encoding="utf-8-sig"))
        if r["filename"].endswith("_1.jpg")]
os.makedirs("data/smoke_seq/S01", exist_ok=True)
for i, pat in enumerate(PATTERNS):
    for r in rows:
        if (r["condition"] in ("thieu", "du") and r["layout_id"] != "L013"
                and (r["A1"], r["A2"], r["B1"], r["C1"]) == pat):
            shutil.copy2(f"data/images_all/{r['filename']}", f"data/smoke_seq/S01/step{i}.jpg")
            print(f"step{i}: {r['filename']}  {pat}  {r['note']}")
            break
    else:
        raise SystemExit(f"Không có ảnh cho mẫu {pat}")
