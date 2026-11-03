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
    res = _model(
        image_path,
        imgsz=cfg["model"]["imgsz"],
        conf=cfg["thresholds"]["conf_low"],
        verbose=False,
    )[0]
    dets = []
    for b in res.boxes:
        x1, y1, x2, y2 = (float(v) for v in b.xyxy[0])
        dets.append(
            {
                "cls": res.names[int(b.cls)],
                "box": [x1, y1, x2, y2],
                "conf": float(b.conf),
            }
        )
    print(
        f"[infer] {image_path}: {len(dets)} vật, {1000 * (time.perf_counter() - t0):.0f} ms"
    )
    return dets


if __name__ == "__main__":
    import argparse
    import os

    import cv2

    from check_tray import check_tray, load_config, slot_rects

    ap = argparse.ArgumentParser(
        description="Chạy YOLO + check_tray trên ảnh hoặc thư mục, lưu ảnh có vẽ khung"
    )
    ap.add_argument("source", help="đường dẫn ảnh .jpg hoặc thư mục ảnh")
    ap.add_argument("--out", default="runs/infer")
    a = ap.parse_args()

    cfg = load_config()
    th = cfg["thresholds"]
    os.makedirs(a.out, exist_ok=True)
    files = (
        [
            os.path.join(a.source, f)
            for f in sorted(os.listdir(a.source))
            if f.lower().endswith(".jpg")
        ]
        if os.path.isdir(a.source)
        else [a.source]
    )

    for path in files:
        dets = detect(path, cfg)
        res = check_tray(dets, cfg)
        img = cv2.imread(path)
        for x1, y1, x2, y2 in slot_rects(cfg).values():
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 1)
        for d in dets:
            x1, y1, x2, y2 = map(int, d["box"])
            color = (
                (0, 0, 255) if d["conf"] >= th["conf_min"] else (160, 160, 160)
            )  # xám = dưới conf_min
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                img,
                f"{d['cls']} {d['conf']:.2f}",
                (x1, max(y1 - 4, 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )
        cv2.putText(
            img,
            f"status={res['status']} cls={res['cls']} slot={res['slot']}",
            (8, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2,
        )
        cv2.putText(
            img,
            res["reason"][:60],
            (8, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            1,
        )
        cv2.imwrite(os.path.join(a.out, os.path.basename(path)), img)
        print(
            f"  -> status={res['status']} cls={res['cls']} slot={res['slot']} "
            f"conf={res['conf']:.2f} states={res['states']} reason={res['reason'] or '-'}"
        )
