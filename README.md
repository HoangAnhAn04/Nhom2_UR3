# Nhóm 2 – Kiểm tra đủ bộ sản phẩm và điều phối bổ sung (UR3 + AI)

Môn: ... | GVHD: PGS.TS. Võ Thanh Hà | Thành viên: (điền tên, MSV, phần việc)

## Phiên bản phần mềm

- URSim UR3 CB-Series, PolyScope **3.15.6** (VMware Workstation)
- Python: (điền) | ultralytics: (điền) | Thiết bị train: CPU/GPU (điền)
- Sau khi cài xong: `python -m pip freeze > requirements.txt`

## Cách chạy nhanh (chưa cần AI)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python tests/test_check_tray.py                       # test logic khay
python bridge.py --mode script --scenario only_B      # terminal 1
python tests/fake_robot.py --host 127.0.0.1           # terminal 2 (robot giả)
```

Kịch bản: `only_B`, `full`, `wrong_slot`, `unchanged_after_done`, `occluded`, `between_slots`.
Thêm `--dup-get --dup-done` cho `fake_robot.py` để thử GET/DONE lặp.

Khi có model: `python bridge.py --mode ai --images data/demo_seq` (ảnh trong thư mục đọc theo thứ tự tên;
bridge chỉ sang ảnh kế sau khi nhận DONE – đây là cảnh thử được quản lý theo kịch bản).

## Mạng

- Python (server, cổng 5000, cấu hình trong `config.json`) chạy trên **Windows host**.
- URSim trong VM là client: `socket_open("<IP Windows>", 5000)`. **Không dùng 127.0.0.1** trong URSim.
- NAT: dùng IP của VMware Network Adapter VMnet8 (`ipconfig`), dạng 192.168.x.1. Bridged: IP LAN Windows.
- Nếu không kết nối được: mở inbound rule Windows Firewall cho cổng 5000.
- Mỗi máy trong nhóm có IP khác nhau -> sửa IP trong chương trình URSim cho đúng máy đang chạy.
- (Ghi chế độ mạng đã dùng vào báo cáo.)

## Giao thức gói tin (mỗi gói kết thúc bằng `\n`)

| Hướng          | Gói                                         | Ý nghĩa                                                               |
| -------------- | ------------------------------------------- | --------------------------------------------------------------------- |
| Robot → Python | `GET,<id>`                                  | Yêu cầu lệnh cho chu kỳ `<id>` (id tăng dần, không trùng trong phiên) |
| Python → Robot | `(id,status,class,x,y,yaw,confidence,slot)` | 8 số, có ngoặc tròn                                                   |
| Robot → Python | `DONE,<id>`                                 | Đã đặt xong. Python **không** trả lời DONE                            |
| Robot → Python | `RESET,<id>`                                | Người vận hành xác nhận đặt lại lệnh đang chờ. Python trả `status=0`  |

- `status`: 0 chờ | 1 lệnh hợp lệ | 2 cần kiểm tra lại | 3 khay hoàn tất | 4 lỗi
- `class`: A=1, B=2, C=3 (0 khi không có lệnh)
- `slot`: 1=A1, 2=A2, 3=B1, 4=C1 (0 khi không có lệnh); A chỉ ô 1/2, B chỉ ô 3, C chỉ ô 4
- `x,y,yaw`: luôn 0 (dùng Waypoint cố định)
- `confidence`: min(conf) của các vật được chấp nhận trong ảnh; không có vật nào thì 1.0. Client kiểm tra lại ngưỡng.
- Ví dụ: `(17,1,1,0,0,0,0.93,2)` = chu kỳ 17, lấy A đặt vào ô 2.

### Quy tắc bắt tay

1. `GET` lặp cùng id → trả đúng dòng đã trả trước đó (không suy luận lại).
2. `DONE` lặp → ghi log, không đổi trạng thái lần hai.
3. Lệnh status 1/3 chưa DONE mà robot hỏi id mới → trả `status=4` (không tự chạy lại lệnh chưa rõ đã xong); cần `RESET`.
4. status 0/2/4: robot không gửi DONE; chờ/chụp lại rồi dùng **id mới**.
5. Sau DONE của lệnh (class, slot), ảnh kế phải cho thấy ô đó `ok`; nếu không → status 2
   (không coi là đủ chỉ vì robot vừa chạy lệnh).
6. Mất kết nối: bridge giữ nguyên trạng thái phiên khi robot nối lại.
7. Server đọc theo bộ đệm đến `\n` (một `recv` có thể nửa dòng hoặc nhiều dòng).

## Logic kiểm tra khay (`check_tray.py`)

Ô: `empty | ok | wrong_type | extra | unknown`. Có vật ngoài ô, tâm sát ranh giới 2 ô, confidence thấp
(`conf_low ≤ conf < conf_min`), ô dư/sai loại → **status 2**. Chỉ khi mọi ô `ok` mới **status 3**.
Còn ô trống → lệnh cho ô thiếu đầu tiên theo thứ tự A1→A2→B1→C1.

## Log

`logs/session_*.csv`: thời gian, sự kiện, id, nguồn ảnh, trạng thái 4 ô, gói trả về, lý do.

## Cấu trúc

```
bridge.py  check_tray.py  infer.py  train.py  evaluate.py  config.json
tests/ (scenarios.py, test_check_tray.py, fake_robot.py)   ursim/ (.urp, .installation, bảng Waypoint/I-O)
data/  weights/  logs/  docs/
```

## Quy ước làm việc nhóm

- File `.urp`/`.installation` chỉ **một người** sửa và commit (dễ xung đột).
- Dữ liệu (ảnh) chia train/val/test theo mã bố trí khay; ảnh tăng cường chỉ từ train. (Điền nguồn, số ảnh từng tập.)
