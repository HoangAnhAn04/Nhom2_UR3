"""check_tray.py - Kiểm tra khay 4 ô (A1, A2, B1, C1) và sinh lệnh bổ sung.

Đầu vào : danh sách phát hiện, mỗi phần tử {"cls": "A", "box": [x1,y1,x2,y2], "conf": 0.93}
          (từ YOLO thật hoặc box giả trong tests/scenarios.py).
Đầu ra  : dict {status, cls, slot, conf, reason, states}
          status 1 = lệnh cấp phôi (cls, slot) | 2 = cần kiểm tra/ngoại lệ
                 3 = khay đủ, đúng loại, đúng ô | (4 do bridge.py phát khi lỗi)

Trạng thái từng ô: empty | ok | wrong_type | extra | unknown
Quy tắc confidence trả về: min(conf) của các vật được chấp nhận; không có vật nào -> 1.0.
"""
import json
import os

CLASS_CODE = {"A": 1, "B": 2, "C": 3}
CODE_CLASS = {v: k for k, v in CLASS_CODE.items()}


def load_config(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def slot_rects(cfg):
    return {int(k): v for k, v in cfg["tray"]["slots"].items()}


def expected_map(cfg):
    return {int(k): v for k, v in cfg["tray"]["expected"].items()}


def center(box):
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def dedup(dets, thr):
    """Loại phát hiện trùng (kể cả khác lớp): giữ box conf cao hơn."""
    keep = []
    for d in sorted(dets, key=lambda d: -d["conf"]):
        if all(iou(d["box"], k["box"]) < thr for k in keep):
            keep.append(d)
    return keep


def locate(c, rects, margin):
    """Trả ('slot', n) | ('boundary', None) | ('outside', None)."""
    cx, cy = c
    inside = [n for n, r in rects.items() if r[0] <= cx <= r[2] and r[1] <= cy <= r[3]]
    near = [n for n, r in rects.items()
            if r[0] - margin <= cx <= r[2] + margin and r[1] - margin <= cy <= r[3] + margin]
    if len(near) >= 2:
        return "boundary", None
    if len(inside) == 1:
        return "slot", inside[0]
    return "outside", None


def analyze(dets, cfg):
    th = cfg["thresholds"]
    rects, exp = slot_rects(cfg), expected_map(cfg)
    margin = th["boundary_margin_px"]

    accepted = dedup([d for d in dets if d["conf"] >= th["conf_min"]], th["nms_iou"])
    # vật conf thấp (không phải bản trùng của vật đã chấp nhận) -> ô đó thành "unknown"
    uncertain = [d for d in dets
                 if th["conf_low"] <= d["conf"] < th["conf_min"]
                 and all(iou(d["box"], a["box"]) < th["nms_iou"] for a in accepted)]

    unknown_slots = set()
    for d in uncertain:
        kind, n = locate(center(d["box"]), rects, margin)
        if kind == "slot":
            unknown_slots.add(n)

    per_slot = {n: [] for n in rects}
    outside, boundary = [], []
    for d in accepted:
        kind, n = locate(center(d["box"]), rects, margin)
        if kind == "slot":
            per_slot[n].append(d)
        elif kind == "boundary":
            boundary.append(d)
        else:
            outside.append(d)

    states = {}
    for n in rects:
        objs = per_slot[n]
        if n in unknown_slots:
            states[n] = "unknown"
        elif not objs:
            states[n] = "empty"
        elif len(objs) >= 2:
            states[n] = "extra"
        elif objs[0]["cls"] == exp[n]:
            states[n] = "ok"
        else:
            states[n] = "wrong_type"

    conf = min((d["conf"] for d in accepted), default=1.0)
    return {"states": states, "outside": outside, "boundary": boundary,
            "uncertain": uncertain, "conf": conf}


def decide(an, cfg, prev=None):
    """prev = (cls_code, slot) của lệnh vừa DONE; ô đó phải 'ok' trong ảnh mới."""
    states = an["states"]
    reasons = []
    if an["uncertain"]:
        reasons.append("low_confidence")
    if an["boundary"]:
        reasons.append("between_slots")
    if an["outside"]:
        reasons.append("object_outside_slots")
    for n, s in states.items():
        if s in ("unknown", "extra", "wrong_type"):
            reasons.append(f"slot{n}_{s}")
    if prev and states.get(prev[1]) != "ok":
        reasons.append(f"placed_slot{prev[1]}_not_confirmed")

    def out(status, cls, slot):
        return {"status": status, "cls": cls, "slot": slot, "conf": an["conf"],
                "reason": ";".join(reasons), "states": dict(states)}

    if reasons:
        return out(2, 0, 0)
    exp = expected_map(cfg)
    missing = [n for n in cfg["tray"]["order"] if states[n] == "empty"]
    if not missing:
        return out(3, 0, 0)
    n = missing[0]
    return out(1, CLASS_CODE[exp[n]], n)


def compatible(cls_code, slot, cfg):
    """A chỉ ô 1/2, B chỉ ô 3, C chỉ ô 4 (theo config)."""
    return slot in cfg["tray"]["allowed"].get(CODE_CLASS.get(cls_code), [])


def check_tray(dets, cfg, prev=None):
    return decide(analyze(dets, cfg), cfg, prev)