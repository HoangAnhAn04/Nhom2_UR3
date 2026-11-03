"""eval_pipeline.py - Đo YOLO + check_tray trên một tập, so với kết quả mong đợi suy ra từ shoot_plan.csv.
  python eval_pipeline.py val      |   python eval_pipeline.py test
Mong đợi (GIẢ ĐỊNH, bạn kiểm tra lại):
  du, che          -> status 3 (khay đủ)
  sai_o, du_vat    -> status 2 (cần kiểm tra)
  thieu            -> status 1 với ô trống đầu tiên theo cfg tray.order và lớp đúng của ô đó
"""
import contextlib
import csv
import io
import sys
from collections import Counter, defaultdict

from check_tray import CLASS_CODE, check_tray, load_config
from infer import detect

split = sys.argv[1] if len(sys.argv) > 1 else "val"
cfg = load_config()
COL = {"A1": 1, "A2": 2, "B1": 3, "C1": 4}
exp_cls = {int(k): v for k, v in cfg["tray"]["expected"].items()}
plan = {r["filename"][:-4]: r for r in csv.DictReader(open("data/shoot_plan.csv", encoding="utf-8-sig"))}
rows = [r for r in csv.DictReader(open("data/splits.csv", encoding="utf-8-sig")) if r["split"] == split]


def expected(r):
    if r["condition"] in ("sai_o", "du_vat"):
        return (2, 0, 0)
    if r["condition"] in ("du", "che"):
        return (3, 0, 0)
    if r["condition"] == "thieu":
        for n in cfg["tray"]["order"]:
            col = next(k for k, v in COL.items() if v == n)
            if r[col].strip() == "-":
                return (1, CLASS_CODE[exp_cls[n]], n)
    return None


stat, bad = defaultdict(Counter), []
out = open(f"logs/pipeline_eval_{split}.csv", "w", newline="", encoding="utf-8")
w = csv.writer(out)
w.writerow(["image", "condition", "note", "expected", "got", "reason"])
for s in rows:
    p = plan[s["image"]]
    exp = expected(p)
    with contextlib.redirect_stdout(io.StringIO()):
        res = check_tray(detect(f"data/dataset/images/{split}/{s['image']}.jpg", cfg), cfg)
    got = (res["status"], res["cls"], res["slot"])
    ok = got == exp
    stat[p["condition"]]["đúng" if ok else "sai"] += 1
    w.writerow([s["image"], p["condition"], p["note"], exp, got, res["reason"]])
    if not ok:
        bad.append((s["image"], p["condition"], p["note"], exp, got, res["reason"]))
out.close()

print(f"\nTập {split}")
for c, v in sorted(stat.items()):
    print(f"  {c:8} đúng {v['đúng']:3} / sai {v['sai']:3}")
print(f"\nCa sai ({len(bad)}):")
for b in bad:
    print(" ", *b, sep="  ")
