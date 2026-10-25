"""infer.py - Suy luận YOLO, trả danh sách phát hiện cho check_tray.py.

Khi train, đặt tên 3 lớp đúng "A", "B", "C" trong data.yaml.
Trả về: [{"cls": "A", "box": [x1,y1,x2,y2], "conf": 0.93}, ...]
Ngưỡng cuối cùng (conf_min) do check_tray.py áp dụng; ở đây chỉ lọc từ conf_low.
"""
import time

_model = None


def detect(image_path, cfg):
    global _model
    if _model is None:
        from ultralytics import YOLO  # import trễ để mode script không cần cài
        _model = YOLO(cfg["model"]["weights"])
    t0 = time.perf_counter()
    res = _model(image_path, imgsz=cfg["model"]["imgsz"],
                 conf=cfg["thresholds"]["conf_low"], verbose=False)[0]
    dets = []
    for b in res.boxes:
        x1, y1, x2, y2 = (float(v) for v in b.xyxy[0])
        dets.append({"cls": res.names[int(b.cls)], "box": [x1, y1, x2, y2], "conf": float(b.conf)})
    print(f"[infer] {image_path}: {len(dets)} vật, {1000 * (time.perf_counter() - t0):.0f} ms")
    return dets