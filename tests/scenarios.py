"""Kịch bản ảnh giả (box giả) cho bridge.py --mode script.
Mỗi kịch bản = danh sách "khung" theo thứ tự; bridge chỉ sang khung kế sau khi nhận DONE.
Đây là cảnh thử được quản lý theo kịch bản, KHÔNG phải kết quả AI thật - ghi rõ trong báo cáo.
"""


def make_at(cfg):
    rects = {int(k): v for k, v in cfg["tray"]["slots"].items()}

    def at(cls, slot, conf=0.95, size=60, dx=0, dy=0):
        r = rects[slot]
        cx, cy = (r[0] + r[2]) / 2 + dx, (r[1] + r[3]) / 2 + dy
        return {"cls": cls, "box": [cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2],
                "conf": conf}
    return at


def build(cfg):
    at = make_at(cfg)
    full = [at("A", 1), at("A", 2), at("B", 3), at("C", 4)]
    return {
        # Ca bắt buộc 1: chỉ có B ở ô 3 -> A->1, A->2, C->4, rồi status 3
        "only_B": [
            [at("B", 3)],
            [at("B", 3), at("A", 1)],
            [at("B", 3), at("A", 1), at("A", 2)],
            full,
        ],
        # Ca 2: khay đủ ngay từ đầu -> status 3, không cấp thêm
        "full": [full],
        # Ca 3: đủ số lượng (4 vật) nhưng sai ô -> status 2
        "wrong_slot": [[at("A", 1), at("B", 2), at("A", 3), at("C", 4)]],
        # Ca 4a: sau DONE ảnh không đổi -> status 2, không coi là đủ
        "unchanged_after_done": [[at("B", 3)], [at("B", 3)]],
        # Ca 4b: bị che/conf thấp ở ô 1 -> status 2
        "occluded": [[at("B", 3), at("A", 1, conf=0.30)]],
        # Ca bất thường: vật nằm giữa hai ô
        "between_slots": [[at("B", 3), at("A", 1, dx=160)]],
    }