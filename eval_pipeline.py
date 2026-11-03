"""eval_pipeline.py - Đánh giá cấp khay (YOLO + check_tray) so với kết quả mong đợi từ shoot_plan.csv.
  python -X utf8 eval_pipeline.py val --sweep   bảng ảnh hưởng conf_min (chọn ngưỡng TRÊN VAL)
  python -X utf8 eval_pipeline.py val           dùng conf_min trong config.json
  python -X utf8 eval_pipeline.py test          CHỈ chạy một lần, sau khi đã khóa mô hình và ngưỡng
Mong đợi (GIẢ ĐỊNH, đổi CHE_EXPECT nếu nhóm chốt khác):
  du                -> status 3 (đủ)
  che               -> CHE_EXPECT
  sai_o, du_vat     -> status 2 (sai / không rõ)
  thieu             -> status 1 với ô trống đầu tiên theo tray.order và lớp đúng của ô đó
"""
import contextlib
import copy
import csv
import io
import sys
from collections import Counter

from check_tray import CLASS_CODE, check_tray, load_config
from infer import detect

CHE_EXPECT = 3
STATE = {3: "đủ", 1: "thiếu", 2: "sai/không rõ"}
split = sys.argv[1] if len(sys.argv) > 1 else "val"
sweep = "--sweep" in sys.argv
cfg = load_config()
COL = {"A1": 1, "A2": 2, "B1": 3, "C1": 4}
exp_cls = {int(k): v for k, v in cfg["tray"]["expected"].items()}
plan = {r["filename"]: r for r in csv.DictReader(open("data/shoot_plan.csv", encoding="utf-8-sig"))}
rows = [r for r in csv.DictReader(open("data/splits.csv", encoding="utf-8-sig")) if r["split"] == split]


def expected(p):
    c = p["condition"]
    if c in ("sai_o", "du_vat"):
        return (2, 0, 0)
    if c == "du":
        return (3, 0, 0)
    if c == "che":
        return (CHE_EXPECT, 0, 0)
    if c == "thieu":
        for n in cfg["tray"]["order"]:
            col = next(k for k, v in COL.items() if v == n)
            if p[col].strip() == "-":
                return (1, CLASS_CODE[exp_cls[n]], n)
    return None


items = []
for s in rows:
    p = plan[s["filename"]]
    with contextlib.redirect_stdout(io.StringIO()):
        dets = detect(f"data/dataset/images/{split}/{s['filename']}", cfg)
    items.append((s["filename"], p, expected(p), dets))
if any(i[2] is None for i in items):
    print("CẢNH BÁO: ảnh không suy ra được kết quả mong đợi:", [i[0] for i in items if i[2] is None])
items = [i for i in items if i[2] is not None]


def run(conf_min):
    c = copy.deepcopy(cfg)
    c["thresholds"]["conf_min"] = conf_min
    out = []
    for fn, p, exp, dets in items:
        r = check_tray(dets, c)
        out.append((fn, p, exp, (r["status"], r["cls"], r["slot"]), r["reason"]))
    return out


def summary(res):
    n = len(res)
    exact = sum(e == g for _, _, e, g, _ in res)
    state = sum(e[0] == g[0] for _, _, e, g, _ in res)
    false_full = sum(e[0] != 3 and g[0] == 3 for _, _, e, g, _ in res)
    false_rej = sum(e[0] == 3 and g[0] == 2 for _, _, e, g, _ in res)
    return n, exact, state, false_full, false_rej, sum(g[0] == 2 for _, _, _, g, _ in res)


if sweep:
    print(f"Tập {split}, {len(items)} ảnh. conf_low={cfg['thresholds']['conf_low']}")
    print(f"{'conf_min':>8} {'đúng lệnh':>10} {'đúng trạng thái':>16} {'thiếu/sai->đủ':>14} {'đủ->từ chối':>12} {'từ chối':>8}")
    for t in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
        n, ex, st, ff, fr, rj = summary(run(t))
        print(f"{t:>8.2f} {ex:>5}/{n:<4} {st:>11}/{n:<4} {ff:>14} {fr:>12} {rj:>8}")
    sys.exit()

res = run(cfg["thresholds"]["conf_min"])
n, ex, st, ff, fr, rj = summary(res)
print(f"\nTập {split}, conf_min={cfg['thresholds']['conf_min']}, {n} ảnh")
print(f"  Đúng lệnh (status+lớp+ô): {ex}/{n} = {100*ex/n:.1f}%")
print(f"  Đúng trạng thái khay:     {st}/{n} = {100*st/n:.1f}%")
print(f"  Khay thiếu/sai bị nhận nhầm là ĐỦ: {ff}")
print(f"  Khay đủ bị từ chối nhầm:           {fr}")
print(f"  Tổng số ảnh bị từ chối (status 2): {rj}")
conf = Counter((e[0], g[0]) for _, _, e, g, _ in res)
print("\nConfusion matrix (hàng = mong đợi, cột = hệ thống):")
print(f"{'':>14}" + "".join(f"{STATE[c]:>14}" for c in (3, 1, 2)))
for r_ in (3, 1, 2):
    print(f"{STATE[r_]:>14}" + "".join(f"{conf[(r_, c)]:>14}" for c in (3, 1, 2)))
by = {}
for _, p, e, g, _ in res:
    by.setdefault(p["condition"], Counter())["đúng" if e == g else "sai"] += 1
print("\nTheo condition:")
for c, v in sorted(by.items()):
    print(f"  {c:8} đúng {v['đúng']:3} / sai {v['sai']:3}")
print("\nCa sai:")
with open(f"logs/pipeline_eval_{split}.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["filename", "condition", "note", "expected", "got", "reason"])
    for fn, p, e, g, why in res:
        w.writerow([fn, p["condition"], p["note"], e, g, why])
        if e != g:
            print(f"  {fn}  {p['condition']}  {p['note']}  mong đợi {e}  được {g}  {why}")
