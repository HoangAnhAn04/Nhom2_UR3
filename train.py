"""train.py - Huấn luyện YOLOv8n. Chạy trên Colab (GPU) hoặc máy local.
  python train.py --data /content/dataset/data.yaml
"""
import argparse

from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--epochs", type=int, default=100)
ap.add_argument("--imgsz", type=int, default=640)
ap.add_argument("--batch", type=int, default=16)
ap.add_argument("--device", default=None, help="0 cho GPU, cpu cho CPU; mặc định tự chọn")
ap.add_argument("--project", default="runs")
ap.add_argument("--name", default="tray_v1")
a = ap.parse_args()

model = YOLO("yolov8n.pt")  # trọng số tiền huấn luyện COCO, tự tải về
model.train(
    data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
    patience=30,          # dừng sớm nếu val không cải thiện 30 epoch
    seed=0, deterministic=True,
    flipud=0.0,           # không lật dọc
    project=a.project, name=a.name, device=a.device,
)
print("Trọng số tốt nhất:", f"{a.project}/{a.name}/weights/best.pt")
