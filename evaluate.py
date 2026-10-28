"""evaluate.py - Đánh giá trên tập test (chỉ chạy SAU khi đã chọn xong mô hình).
  python evaluate.py --weights weights/best.pt --data data/dataset/data.yaml
"""
import argparse

from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--weights", default="weights/best.pt")
ap.add_argument("--data", required=True)
ap.add_argument("--split", default="test", choices=["val", "test"])
ap.add_argument("--imgsz", type=int, default=640)
a = ap.parse_args()

m = YOLO(a.weights).val(data=a.data, split=a.split, imgsz=a.imgsz, plots=True)
print(f"\nTập {a.split}: mAP50={m.box.map50:.3f}  mAP50-95={m.box.map:.3f}  "
      f"P={m.box.mp:.3f}  R={m.box.mr:.3f}")
for i, idx in enumerate(m.box.ap_class_index):
    p, r, ap50, ap5095 = m.box.class_result(i)
    print(f"  {m.names[idx]}: P={p:.3f}  R={r:.3f}  AP50={ap50:.3f}  AP50-95={ap5095:.3f}")
