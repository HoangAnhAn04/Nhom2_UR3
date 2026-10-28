"""rename_photos.py - Đổi tên ảnh theo thứ tự chụp trong data/shoot_order.csv.
  python rename_photos.py data/phone_dump                              (chạy thử, chỉ in)
  python rename_photos.py data/phone_dump "--skip=IMG_0612,IMG_0745"   (bỏ qua ảnh thừa/hỏng)
  thêm --apply để copy thật; --by-time để sắp theo thời gian sửa file thay vì theo tên file
"""
import csv
import os
import shutil
import sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
src = sys.argv[1]
apply = "--apply" in sys.argv
by_time = "--by-time" in sys.argv
skip = set()
for a in sys.argv[2:]:
    if a.startswith("--skip="):
        skip |= {s.strip().upper() for s in a[len("--skip="):].split(",") if s.strip()}

with open("data/shoot_order.csv", encoding="utf-8-sig") as f:
    order = list(csv.DictReader(f))
key = os.path.getmtime if by_time else (lambda p: os.path.basename(p).lower())
all_files = sorted((os.path.join(src, n) for n in os.listdir(src)
                    if n.lower().endswith((".jpg", ".jpeg"))), key=key)


def stem(p):
    return os.path.splitext(os.path.basename(p))[0].upper()


missing = skip - {stem(p) for p in all_files}
if missing:
    sys.exit(f"--skip có tên không tồn tại trong {src}: {sorted(missing)}")
files = [p for p in all_files if stem(p) not in skip]
print(f"Tổng {len(all_files)} ảnh, bỏ qua {len(all_files) - len(files)}, "
      f"còn {len(files)}; kế hoạch cần {len(order)}")
if len(files) != len(order):
    sys.exit("Số lượng chưa khớp. Tìm tiếp ảnh thừa (hoặc ảnh bị thiếu). Không đổi tên.")

pairs = []
for path, row in zip(files, order):
    folder = "data/refs" if row["kind"] == "ref" else "data/raw"
    pairs.append((path, os.path.join(folder, row["filename"]), row["kind"]))
clash = [d for _, d, _ in pairs if os.path.exists(d)]
if clash:
    sys.exit(f"{len(clash)} file đích đã tồn tại (ví dụ {clash[0]}). Chuyển file cũ đi trước.")

n = len(pairs)
for i, (p, dst, kind) in enumerate(pairs):
    if kind == "ref" or i < 8 or i >= n - 8:  # in mọi ảnh REF, 8 ảnh đầu và 8 ảnh cuối
        print(os.path.basename(p), "->", dst)
if not apply:
    print(f"\nChạy thử xong ({n} ảnh). Mở các ảnh REF ở trên: tất cả phải là khay TRỐNG. "
          "Rồi chạy lại với --apply.")
else:
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/refs", exist_ok=True)
    for p, dst, _ in pairs:
        shutil.copy2(p, dst)
    print(f"\nĐã copy {n} ảnh.")
