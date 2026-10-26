# HƯỚNG DẪN LÀM TIẾP – Nhóm 2 (UR3 + AI)

> Đọc file này từ trên xuống dưới một lượt rồi mới bắt tay vào làm.
> File `README.md` là tài liệu kỹ thuật (giao thức, cách chạy). File này là **việc cần làm, ai làm, làm thế nào**.

**Đề của nhóm:** Kiểm tra đủ bộ sản phẩm và điều phối bổ sung (mức Nâng cao, nhóm AI).
Khay đơn hàng cần 2 linh kiện A, 1 B, 1 C đặt vào 4 ô **A1, A2, B1, C1** (slot 1, 2, 3, 4).
AI nhìn ảnh khay → Python lập lệnh bổ sung ô thiếu → UR3 (URSim) lấy từ 3 vị trí cấp cố định, đặt vào ô được chỉ định → chụp/kiểm tra lại → chỉ báo khay hoàn tất khi AI xác nhận đủ, đúng loại, đúng ô.

---

## 0. Cả nhóm phải nắm (vì vấn đáp từng người)

Mỗi sinh viên phải giải thích được phần của mình. Tối thiểu cả 3 người đều phải trả lời được:

1. Luồng một chu kỳ: robot `GET` → Python phân tích ảnh → trả lệnh `(id,status,class,x,y,yaw,confidence,slot)` → robot gắp/đặt → `DONE` → Python lấy ảnh mới → kiểm tra lại.
2. Vì sao có `status` 0/1/2/3/4 và robot làm gì ở từng trạng thái.
3. Vì sao `GET` lặp phải trả cùng lệnh, `DONE` lặp không được đếm lần hai.
4. Vì sao không được coi khay đủ chỉ vì robot vừa chạy xong lệnh (phải có ảnh mới xác nhận).
5. Vì sao chia tập theo **bố trí khay** chứ không chia ngẫu nhiên từng ảnh.
6. Ngưỡng confidence chọn bằng tập nào, khóa lúc nào.

---

## 1. Hiện trạng (cập nhật mục này khi xong việc)

| Hạng mục                                                                  | Trạng thái                                             |
| ------------------------------------------------------------------------- | ------------------------------------------------------ |
| Cấu trúc repo, `.gitignore`, `requirements.txt`                           | Xong                                                   |
| `check_tray.py` (logic ô, sinh lệnh bổ sung) + `tests/test_check_tray.py` | Xong, 10/10 test qua                                   |
| `bridge.py` (TCP server, GET/DONE/RESET, log CSV, kịch bản ảnh giả)       | Xong, chạy với robot giả `tests/fake_robot.py`         |
| Nối URSim ↔ bridge: `socket_open`, gửi `GET`, đọc 8 số                    | Xong, URSim nhận đúng `[8, 1, 1, 1, 0, 0, 0, 0.95, 1]` |
| URSim: TCP `Kep`                                                          | Đã tạo (người 1)                                       |
| URSim: Waypoint, SubProgram, vòng lặp chính, bộ đếm                       | **Chưa**                                               |
| Dữ liệu ảnh, gán nhãn, chia tập                                           | **Chưa**                                               |
| Huấn luyện YOLO, đánh giá, khóa ngưỡng                                    | **Chưa**                                               |
| Chuỗi ảnh trước–sau, chạy tích hợp `--mode ai`                            | **Chưa**                                               |
| Báo cáo 12–20 trang, video 5–7 phút                                       | **Chưa**                                               |

Môi trường URSim: **URSim UR3 CB-Series, PolyScope 3.15.6.106324** (VMware Workstation). Ghi đúng phiên bản này vào báo cáo.

---

## 2. Việc phải hỏi giảng viên (làm ngay, 1 tin nhắn)

- Mốc **28/10** là **nghiệm thu cuối** hay **kiểm tra tiến độ**? Cần nộp/trình bày gì ở mốc đó?
- Đề ghi 6 tuần cho đề AI nhưng nhóm được chia ngày 15/10, nên thời hạn thực tế cần xác nhận lại.
- Dùng **ảnh chụp điện thoại + ảnh tĩnh quản lý theo kịch bản** (không cần webcam/robot thật) có được không? (đề cho phép, nhưng nên xác nhận).
- Lớp A/B/C là vật tự chọn, đơn giản (ví dụ 3 màu/hình khác nhau) có được không?

---

## 3. Phân công

Điền tên/MSV. Có thể đổi vai nhưng mỗi mảng phải có **một người chịu trách nhiệm**.

| Vai                         | Người  | Phần việc                                                                                           | Sản phẩm bàn giao                                                                                 |
| --------------------------- | ------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **P1 – URSim**              | (điền) | TCP, Waypoint, SubProgram, vòng lặp chính, bộ đếm, DO0/DO1/DO2, nhánh lỗi, 4 ca bắt buộc trên URSim | `ursim/nhom2_main.urp`, `ursim/nhom2.installation`, bảng Waypoint, bảng I/O, ảnh cây chương trình |
| **P2 – Dữ liệu**            | (điền) | Chụp ảnh, ghi `metadata.csv`, gán nhãn bbox, chia tập, chụp chuỗi ảnh trước–sau                     | `data/` đủ ảnh + nhãn + `splits.csv`, README dữ liệu                                              |
| **P3 – Mô hình & đánh giá** | (điền) | Train YOLO, chọn/khóa ngưỡng, đánh giá test, phân tích ca sai, chạy `--mode ai` tích hợp            | `weights/best.pt`, kết quả train/test, `logs/` đánh giá, ảnh sai dự đoán                          |
| **Cả nhóm**                 |        | Ghép, chạy ca thử, quay video, viết báo cáo (chia chương theo phần mình làm)                        | Báo cáo, video                                                                                    |

Chia báo cáo gợi ý: P1 viết bố trí/TCP/Waypoint/cây chương trình/kiểm thử URSim; P2 viết dữ liệu; P3 viết mô hình/đánh giá/sai số; chương giao thức, thuật toán, kết luận viết chung.

---

## 4. Chuẩn bị chung

### 4.1 Git

```
git clone <link-repo>
cd Nhom2_UR3
git pull                      # LUÔN pull trước khi làm
# ... làm việc ...
git add <file>                # tránh "git add ." nếu lỡ có file nặng
git commit -m "P2: them 120 anh khay + metadata"
git push
```

Quy tắc:

- File `.urp` và `.installation` **chỉ P1 sửa và commit**. Hai người kia không mở lưu đè.
- Không commit `.venv/`, `__pycache__/`, `runs/`. (Đã có trong `.gitignore`.)
- Ảnh nhỏ (vài chục MB) cho lên repo. Quá nặng thì để Google Drive và ghi link vào `data/README.md` (đề cho phép "cách truy cập đã thống nhất với giảng viên").
- `weights/best.pt` của YOLOv8n nặng khoảng vài MB nên commit được.
- Commit ít và thường xuyên, câu commit nói rõ làm gì.

### 4.2 Python (mỗi người một lần)

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python tests/test_check_tray.py        # phải ra 10/10 OK
```

Cuối dự án, một người chạy `python -m pip freeze > requirements.txt` để ghi phiên bản đã dùng.

### 4.3 Chạy thử bridge (để hiểu hệ thống)

```
python bridge.py --mode script --scenario only_B        # terminal 1
python tests/fake_robot.py                              # terminal 2
```

Kết quả đúng: `A→1`, `A→2`, `C→4`, rồi status 3. Mỗi lần chạy sinh một file `logs/session_*.csv`.

---

## 5. PHẦN AI (P2 và P3)

### 5.1 Dựng cảnh chụp (P2, khoảng 1 giờ)

- **Khay:** tờ bìa/hộp giấy, kẻ 4 ô (2×2). Đánh dấu A1, A2, B1, C1 (slot 1, 2, 3, 4). Dán cố định xuống bàn.
- **3 loại linh kiện A, B, C:** chọn vật **cực dễ phân biệt** (khác màu và hình, ví dụ nắp chai đỏ / đồng xu / khối giấy xanh). Vật đơn giản thì ghi hạn chế đại diện của dữ liệu vào báo cáo.
- **Camera:** điện thoại gác cố định, nhìn thẳng xuống khay. **Không đổi góc/độ cao** trong suốt quá trình chụp, vì 4 hình chữ nhật ô trong `config.json` là cố định trên ảnh.
- Tắt chế độ tự làm đẹp/HDR/zoom thay đổi. Khóa lấy nét nếu được.
- Chụp cùng độ phân giải cho mọi ảnh (ví dụ 1280×960, tỉ lệ 4:3). Sau đó `config.json` → `image` và `tray.slots` phải khớp độ phân giải dùng để suy luận (xem 5.9).

### 5.2 Chụp dữ liệu (cả nhóm, một buổi)

Mục tiêu **tối thiểu 300 ảnh khay**; nên chụp **khoảng 330** để có dư. Đề yêu cầu đủ các tình huống:

| Tình huống                | Mục tiêu (ảnh) | Ví dụ                                 |
| ------------------------- | -------------- | ------------------------------------- |
| Đủ bộ (A, A, B, C đúng ô) | 80             | A ở A1 và A2, B ở B1, C ở C1          |
| Thiếu một hoặc nhiều vật  | 90             | chỉ có B; thiếu C; thiếu 1 trong 2 A… |
| Sai ô                     | 60             | B nằm ở A1; đủ 4 vật nhưng đảo ô      |
| Dư vật                    | 60             | 5 vật; 2 vật trong cùng một ô         |
| Che khuất                 | 40             | tay/giấy che một phần ô               |

Quy tắc chụp để chia tập đúng:

- Mỗi **bố trí khay** (một cách xếp vật) có một mã `L001`, `L002`… Chụp **mỗi bố trí 3 ảnh** (đổi nhẹ ánh sáng/độ nghiêng bóng, **không** đổi góc camera). Cần khoảng **110 bố trí khác nhau**.
- Đặt tên ảnh: `L{mã_bố_trí}_{số}.jpg`, ví dụ `L012_1.jpg`, `L012_2.jpg`, `L012_3.jpg`.
- Đa dạng: đổi vị trí vật trong ô, xoay vật, bật/tắt đèn, ánh sáng gần cửa sổ/xa cửa sổ, đổi người chụp. Chia đều ba người để có nhiều phiên.
- **Tất cả ảnh cùng một mã bố trí phải nằm cùng một tập** khi chia (xem 5.4).

Ghi **`data/metadata.csv`** ngay khi chụp (đừng để sau):

```
filename,layout_id,session,photographer,condition,A1,A2,B1,C1,note
L012_1.jpg,L012,S02,Nguoi2,thieu,-,-,B,-,chi co B
L013_1.jpg,L013,S02,Nguoi2,sai_o,B,A,A,C,B o A1
L014_1.jpg,L014,S03,Nguoi3,du_vat,A+A,A,B,C,2 vat o A1
```

- Cột `A1,A2,B1,C1` là **trạng thái thật** của ô: `-` (trống), `A`/`B`/`C`, hoặc `A+B` (nhiều vật).
- `condition`: `du`, `thieu`, `sai_o`, `du_vat`, `che`.
- Trạng thái thật ghi theo **thực tế vật lý** (kể cả khi bị che).

### 5.3 Gán nhãn bounding box (P2, khoảng nửa ngày)

Công cụ (chọn một): **Roboflow**, **CVAT**, **LabelImg**. Mỗi vật được vẽ **một bbox** với lớp `A`, `B`, `C`.

- **Tên lớp phải đúng `A`, `B`, `C`** (code `check_tray.py` so sánh theo tên). Thứ tự id trong YOLO: `0=A, 1=B, 2=C`.
- Vẽ bbox sát vật, kể cả vật ở sai ô và vật dư. Vật bị che một phần: vẽ phần nhìn thấy. Vật bị che hoàn toàn thì không vẽ (nhưng `metadata.csv` vẫn ghi trạng thái thật).
- **Xuất định dạng YOLOv8/YOLO.** Nếu dùng Roboflow, **không** để nó tự chia tập ngẫu nhiên (nó sẽ tách ảnh cùng bố trí vào nhiều tập); xuất toàn bộ rồi tự chia bằng script ở 5.4.
- Mẹo tiết kiệm thời gian: gán tay khoảng 50 ảnh, train thử (5.5), rồi cho model dự đoán sẵn bbox ở các ảnh còn lại và chỉ sửa lại.
- Kiểm tra lại ngẫu nhiên khoảng 10% ảnh sau khi gán, vì nhãn sai làm hỏng cả huấn luyện.

Định dạng nhãn YOLO: mỗi ảnh có một file `.txt` cùng tên, mỗi dòng một vật: `class_id cx cy w h` (đều chuẩn hóa 0–1).

### 5.4 Chia tập train/val/test theo bố trí (P2)

Quy tắc đề: chia **60/20/20% theo khay/phiên bố trí**; ảnh gần giống và ảnh tăng cường của cùng một ảnh gốc ở **cùng tập**; ảnh tăng cường chỉ tạo từ **train**.

Cách làm:

1. Lấy danh sách mã bố trí (`layout_id`) từ `metadata.csv`.
2. Xáo ngẫu nhiên với seed cố định (ví dụ `seed=42`), chia 60/20/20 **theo bố trí**. Cố gắng giữ các `condition` có mặt ở cả ba tập (chia riêng trong từng `condition` rồi gộp lại là cách tốt).
3. Tất cả ảnh của một bố trí đi cùng tập.
4. Ghi kết quả vào **`data/splits.csv`** (cột `filename,layout_id,split`). Đề yêu cầu nộp danh sách chia tập này.
5. Tạo cấu trúc YOLO:

```
data/yolo/
  images/train  images/val  images/test
  labels/train  labels/val  labels/test
```

6. Kiểm tra: **tập test phải có ít nhất 60 ảnh** (đề yêu cầu đánh giá trên ≥ 60 ảnh test) và đủ các tình huống. Với 330 ảnh, test khoảng 66 ảnh.
7. Ghi vào báo cáo: số ảnh, số bố trí, số bbox từng lớp ở mỗi tập.

> Script `split_dataset.py` chưa viết. Xem mục 11.

Tạo `data/data.yaml`:

```
path: data/yolo
train: images/train
val: images/val
test: images/test
names:
  0: A
  1: B
  2: C
```

### 5.5 Huấn luyện YOLO (P3)

Dùng Ultralytics YOLOv8n (nhẹ, đủ cho dữ liệu này), tinh chỉnh từ trọng số có sẵn.

**Trên máy cá nhân (hoặc Colab, có GPU T4 miễn phí):**

```
python -m pip install ultralytics
yolo detect train data=data/data.yaml model=yolov8n.pt imgsz=640 epochs=60 batch=16 seed=42 name=baseline
```

- Trên Colab: tải thư mục `data/` lên (nén zip cho nhanh), `pip install ultralytics`, chạy lệnh trên, rồi tải `runs/detect/baseline/weights/best.pt` về, bỏ vào `weights/best.pt` của repo.
- Augmentation mặc định của Ultralytics chỉ áp dụng lúc huấn luyện trên tập train, phù hợp với yêu cầu "tăng cường chỉ từ train". Tập val/test không bị augment.
- Ghi vào báo cáo: kiến trúc (YOLOv8n), trọng số khởi tạo (`yolov8n.pt`, COCO), kích thước ảnh, epochs, batch, seed, thiết bị (CPU/GPU), phiên bản `ultralytics`/`torch`, thời gian train.
- Nếu kết quả kém: thêm ảnh ở các tình huống model hay sai, kiểm tra nhãn, tăng epochs, hoặc đổi sang `yolov8s.pt`. Mỗi lần thử đổi **một thứ** và ghi lại.

Chọn mô hình tốt nhất bằng **tập val** (không dùng test). Khi đã chọn xong, **không train lại** sau khi nhìn kết quả test.

### 5.6 Chọn và khóa ngưỡng (P3)

Ngưỡng nằm trong `config.json` → `thresholds`: `conf_low` (dưới mức này bỏ), `conf_min` (từ mức này mới chấp nhận), `nms_iou` (loại box trùng), `boundary_margin_px` (vùng sát ranh giới 2 ô).

Quy trình:

1. Chạy suy luận trên **tập val** với nhiều giá trị `conf_min` (ví dụ 0.3 đến 0.8, bước 0.05).
2. Với mỗi giá trị, tính: tỷ lệ nhận định đúng trạng thái khay (đủ/thiếu/sai) và **số khay thiếu/sai bị nhận nhầm là đủ**.
3. Ưu tiên **không để khay thiếu/sai bị nhận là đủ** (đây là lỗi nghiêm trọng nhất của bài), sau đó mới tối đa độ đúng.
4. Chọn ngưỡng, ghi vào `config.json`, **commit**, và từ đó **không đổi** nữa.
5. Lập bảng ảnh hưởng của ngưỡng (đưa vào báo cáo).

`boundary_margin_px` và 4 hình chữ nhật ô cũng chọn trên val/quan sát ảnh, không chỉnh theo test.

### 5.7 Đánh giá trên tập test (P3)

Chạy **một lần** sau khi đã khóa mô hình và ngưỡng. Báo cáo:

1. **Chỉ số phát hiện:** mAP50, mAP50-95, precision/recall từng lớp (A, B, C).
   ```
   yolo detect val model=weights/best.pt data=data/data.yaml split=test
   ```
2. **Chỉ số cấp khay (quan trọng nhất của bài):** chạy `check_tray` trên từng ảnh test, so với trạng thái thật trong `metadata.csv`:
   - Ánh xạ: `status 3` → "đủ"; `status 1` → "thiếu"; `status 2` → "sai/không rõ".
   - **Độ đúng cấp khay** = số ảnh nhận định đúng / tổng ảnh test. Tiêu chí đối chiếu của đề: **≥ 90% trên ít nhất 60 ảnh test**.
   - **Số khay thiếu/sai bị nhận nhầm là đủ** (báo cáo riêng, cả số tuyệt đối và tỉ lệ).
   - **Tỷ lệ từ chối (status 2)**, tách riêng; liệt kê các ảnh đủ nhưng bị từ chối nhầm.
   - Confusion matrix 3 trạng thái (đủ/thiếu/sai).
3. **Phân tích ca sai:** lưu ảnh sai vào thư mục (ví dụ `logs/test_errors/`), nêu nguyên nhân (che khuất, bóng, vật gần ranh giới ô, bbox lệch…).
4. **Tách bạch:** độ đúng của **mô hình/AI so với nhãn thật** khác với độ đúng **robot thực hiện lệnh đã nhận**. Hai phần này báo cáo riêng.
5. Nếu chưa đạt 90%, **ghi đúng số đo được** và phân tích vì sao. Các mục tiêu định lượng của đề là tiêu chí đối chiếu, không phải số liệu có sẵn.

> Script `evaluate.py` chưa viết. Xem mục 11.

### 5.8 Chuỗi ảnh trước–sau (P2 chụp, P3 dùng)

Đề yêu cầu **tối thiểu 10 chuỗi ảnh trước–sau**, quản lý theo kịch bản: chỉ đổi sang ảnh bước kế sau khi robot gửi `DONE`. Đây là "cảnh thử được quản lý theo kịch bản" (nói rõ như vậy trong báo cáo).

- Mỗi chuỗi một thư mục: `data/demo_seq/S01/`, `S02/`, … Ảnh trong chuỗi đặt tên `step0.jpg`, `step1.jpg`, `step2.jpg`… (bridge sắp xếp theo tên).
- Ảnh chuỗi **không đưa vào train/val/test**. Chụp riêng bằng cùng camera cố định.
- Chuỗi mẫu `S01` (ca bắt buộc "chỉ có B ở ô 3"):
  - `step0`: chỉ B ở ô 3
  - `step1`: B ở ô 3 + A ở ô 1
  - `step2`: thêm A ở ô 2
  - `step3`: đủ bộ (thêm C ở ô 4)
- Các chuỗi còn lại phủ các ca bổ sung: thiếu A, thiếu C, thiếu hai A, khay đủ ngay (chuỗi 1 ảnh), sai ô (1 ảnh), ảnh không đổi sau DONE (2 ảnh giống nhau), bị che (1 ảnh), v.v.
- Ghi `data/demo_seq/README.md`: mỗi chuỗi mô tả ca gì, lệnh dự kiến.

### 5.9 Tích hợp AI vào bridge (P3, sau khi có `best.pt`)

1. Đặt `weights/best.pt`. Sửa `config.json` → `model.weights` nếu đổi tên.
2. Kiểm tra `config.json` → `tray.slots` khớp **đúng độ phân giải và góc camera** thật. Mở một ảnh bất kỳ, đọc tọa độ pixel 4 ô, điền lại (định dạng `[x1, y1, x2, y2]`). Đây là việc dễ sai nhất khi chuyển từ box giả sang ảnh thật.
3. Thử suy luận một ảnh để chắc `infer.py` chạy (in ra số vật và thời gian ms).
4. Chạy bridge với một chuỗi ảnh:
   ```
   python bridge.py --mode ai --images data/demo_seq/S01
   ```
   Robot (hoặc `tests/fake_robot.py`) sẽ nhận lệnh theo ảnh thật. Ảnh chỉ chuyển sang `step` kế sau khi nhận `DONE`.
5. Mỗi lần chạy một chuỗi, **restart bridge** (Ctrl+C rồi chạy lại) để xóa trạng thái phiên.
6. Ghi **thời gian suy luận** (infer.py in ra ms) **riêng** với thời gian chu kỳ mô phỏng URSim, vì đề yêu cầu tách hai số này.
7. Khi nghiệm thu **không dùng gói gõ tay** thay phần AI: video phải cho thấy lệnh sinh ra từ ảnh.

---

## 6. PHẦN URSIM (P1; hai người kia cần hiểu để hỗ trợ)

Môi trường: PolyScope 3.15.6, **Installation → TCP Configuration** (không phải "General → TCP").

### 6.1 Việc đã kiểm chứng

Chương trình thử đã chạy được và đọc đúng gói:

```
okk := False
Script:  okk = socket_open("192.168.61.1", 5000, "py")
Popup:   okk                                    -> True
cid := 0 ; r := [0,0,0,0,0,0,0,0,0] ; cid := cid + 1
Script:  socket_send_line(str_cat("GET,", to_str(cid)), "py")
Script:  r = socket_read_ascii_float(8, "py", 5)
Popup:   r                                      -> [8, 1, 1, 1, 0, 0, 0, 0.95, 1]
Script:  socket_close("py")
```

Đã xác nhận trên bản này: `socket_read_ascii_float` có tham số timeout, `str_cat`, `to_str`, `socket_send_line` dùng được. IP `192.168.61.1` là IP Windows (VMnet8). IP máy khác có thể khác, kiểm tra bằng `ipconfig`.

**Quan trọng:** biến dùng trong Script **phải tạo trước bằng node Assignment** (`okk := False`), nếu không Popup/If không thấy biến. Trong Script chỉ gán giá trị, **không dùng `global`**. Node Script ở chế độ **Line** (một dòng một node).

### 6.2 TCP và Installation

- Installation → TCP Configuration → **New** → **Rename** `Kep` → **Z = 100 mm**, các giá trị khác = 0 → **Set as default**.
- Đặt TCP **trước khi dạy Waypoint**. Đổi TCP sau sẽ làm lệch các điểm đã dạy.
- Installation → Load/Save → Save As `nhom2`. Chuyển file `.installation` vào `ursim/` trong repo.
- Ghi vào báo cáo: phiên bản URSim, TCP đã đặt, hệ tọa độ dùng (Base), cách chọn vị trí.

### 6.3 Bố trí và Waypoint

Bố trí gợi ý (tự chọn trong vùng với tới của UR3, tầm với khoảng 500 mm):

- Khay 2×2 đặt trước robot, cách gốc khoảng 250–300 mm, các ô cách nhau khoảng 60 mm.
- 3 vị trí cấp A, B, C xếp hàng bên cạnh khay.
- Tư thế đầu kẹp hướng xuống bàn, **giữ nguyên hướng** ở mọi điểm (chỉ tịnh tiến) để tránh lỗi "không với tới".

Cần dạy **8 điểm cố định** (mỗi điểm trong một node `MoveJ`):
`Home`, `Cap_A_Approach`, `Cap_B_Approach`, `Cap_C_Approach`, `O1_Approach`, `O2_Approach`, `O3_Approach`, `O4_Approach`.
Điểm tiếp cận cao hơn mặt bàn khoảng 100 mm.

Đoạn hạ/nâng dùng `MoveL`. Dùng Waypoint dạng **Relative position** (đổi kiểu trong node Waypoint) với Z = −0,1 m (hạ) và +0,1 m (nâng). Nếu bản này khác, có thể dùng cặp điểm cố định "tiếp cận" và "chạm". Kiểm tra trong URSim và ghi lại cách đã dùng.

Trong khi dạy: giảm Speed (30–50%), xoay khớp thận trọng, quan sát khung 3D.

### 6.4 SubProgram

Tạo 4 SubProgram (Advanced → SubProgram):

- `Lay_A`, `Lay_B`, `Lay_C`:
  ```
  MoveJ  Cap_X_Approach
  MoveL  Relative Z = -0.1      (hạ)
  Set DO0 = On                  (đóng kẹp)
  Wait 0.5 s
  MoveL  Relative Z = +0.1      (nâng)
  ```
- `Dat_VaoO` (dùng biến `slot`):
  ```
  If slot == 1: MoveJ O1_Approach ; MoveL Relative Z -0.1 ; Set DO0 = Off ; Wait 0.5 ; MoveL Relative Z +0.1
  ElseIf slot == 2: (tương tự O2)
  ElseIf slot == 3: (tương tự O3)
  ElseIf slot == 4: (tương tự O4)
  ```
  Chạy thử **từng SubProgram một mình** bằng node Call, tốc độ thấp, xem đèn DO0 ở tab I/O, kiểm tra không báo lỗi với tới.

Đề yêu cầu tối thiểu hai SubProgram; nhóm này có 4.

### 6.5 Biến chương trình

Tạo bằng Assignment ở đầu chương trình (hoặc trong BeforeStart nếu có):

| Biến                | Giá trị đầu                     | Ý nghĩa                         |
| ------------------- | ------------------------------- | ------------------------------- |
| `ip`                | `"192.168.61.1"` (sửa theo máy) | IP máy chạy Python              |
| `cid`               | 0                               | mã chu kỳ, tăng mỗi lần GET mới |
| `r`                 | `[0,0,0,0,0,0,0,0,0]`           | kết quả đọc socket              |
| `n_read`, `rid`     | 0                               | số phần tử đọc được, id nhận về |
| `ok`                | False                           | gói hợp lệ                      |
| `st`, `cls`, `slot` | 0                               | status, class, slot nhận về     |
| `conf`              | 0.0                             | confidence                      |
| `n_dat`             | 0                               | số linh kiện đã đặt xong        |
| `n_khay_xong`       | 0                               | số khay hoàn tất                |
| `n_cho`             | 0                               | số lần chờ/ngoại lệ             |
| `n_loi`             | 0                               | số lần lỗi quy trình/kết nối    |
| `retries`           | 0                               | số lần status 2/0/4 liên tiếp   |
| `chay`              | True                            | cờ chạy vòng lặp                |

Đầu chương trình: `Set DO0, DO1, DO2 = Off` và `MoveJ Home`.

### 6.6 Vòng lặp chính

```
Loop  chay == True
  cid := cid + 1
  ok  := False
  Script:  socket_send_line(str_cat("GET,", to_str(cid)), "py")
  Script:  r = socket_read_ascii_float(8, "py", 5)
  Script:  n_read = r[0]
  If n_read == 8
     Script:  rid = r[1]
     If rid == cid                       (id phải khớp, không dùng dữ liệu cũ)
        Script:  st = r[2]
        Script:  cls = r[3]
        Script:  conf = r[7]
        Script:  slot = r[8]
        ok := True
  If ok == False
     Set DO1 = On ; n_loi := n_loi + 1
     Script: socket_close("py")  ;  Wait 1  ;  Script: socket_open(ip, 5000, "py")   (mở lại, có giới hạn số lần)
  ElseIf st == 1 and conf >= 0.5 and ((cls==1 and (slot==1 or slot==2)) or (cls==2 and slot==3) or (cls==3 and slot==4))
     Set DO1 = Off ; retries := 0
     If cls == 1: Call Lay_A  / ElseIf cls == 2: Call Lay_B / ElseIf cls == 3: Call Lay_C
     Call Dat_VaoO
     Script:  socket_send_line(str_cat("DONE,", to_str(cid)), "py")
     n_dat := n_dat + 1                  (chỉ tăng SAU khi đặt xong)
     Set DO2 = On ; Wait 0.2 ; Set DO2 = Off   (xung hoàn tất một lần đặt)
  ElseIf st == 3
     Set DO1 = Off
     Script:  socket_send_line(str_cat("DONE,", to_str(cid)), "py")
     n_khay_xong := n_khay_xong + 1      (đúng một lần)
     chay := False
  Else                                   (status 0, 2, 4 hoặc lệnh không hợp lệ)
     n_cho := n_cho + 1 ; retries := retries + 1
     Wait 0.5                            (KHÔNG gửi DONE; vòng sau dùng cid mới)
     If retries >= 3: Popup "Cần người vận hành kiểm tra" (Halt) ; chay := False
Popup: hiện n_dat, n_khay_xong, n_cho, n_loi (để chụp bộ đếm)
Script: socket_close("py")
```

Chú ý khi dựng:

- Mở socket **một lần** trước vòng lặp: `Script: okk = socket_open(ip, 5000, "py")` rồi Popup/If kiểm tra `okk`. Nếu mất kết nối thì mở lại trong nhánh lỗi.
- Biểu thức nhiều điều kiện dùng `and`/`or` và ngoặc trong ô expression của If.
- `socket_read_ascii_float` trả list; **chỉ đọc `r[1]…r[8]` khi `r[0] == 8`** (đã tách thành If lồng nhau ở trên để tránh lỗi chỉ số).
- DO0: On = đóng kẹp, Off = mở kẹp. DO1: lỗi quy trình/kết nối. DO2: xung hoàn tất một lần đặt. **Không dùng DO2 làm bộ đếm khay** (khay hoàn tất do biến `n_khay_xong`).
- Khi gặp status 4 vì "lệnh chưa DONE" (sau mất kết nối): người vận hành kiểm tra rồi robot gửi `RESET,<cid>`; bridge trả status 0 và xóa lệnh đang chờ.
- Chạy chậm khi quan sát, kiểm tra Waypoint trước khi bấm Play.
- Lưu chương trình thường xuyên: File → Save. Chuyển `.urp` ra thư mục `ursim/` của repo và commit (chỉ P1).

### 6.7 Bảng I/O

| Tín hiệu    | Ý nghĩa                                      |
| ----------- | -------------------------------------------- |
| DO0         | On = đóng kẹp; Off = mở kẹp                  |
| DO1         | Báo lỗi chương trình/quy trình/kết nối       |
| DO2         | Xung hoàn tất một lần đặt                    |
| DO3 trở lên | Chưa dùng (nếu dùng thêm thì lập bảng riêng) |

---

## 7. Ghép và chạy 4 ca bắt buộc + ca bất thường

**Trước mỗi ca: Ctrl+C rồi chạy lại `bridge.py`** (bridge nhớ lệnh chưa DONE, nếu không restart sẽ trả status 4).

### 7.1 Giai đoạn 1 – với kịch bản box giả (chưa cần model)

| Ca                       | Lệnh bridge                       | Kết quả dự kiến                                |
| ------------------------ | --------------------------------- | ---------------------------------------------- |
| Ban đầu chỉ có B ở ô 3   | `--mode script --scenario only_B` | A→1, A→2, C→4, rồi status 3, `n_khay_xong = 1` |
| Khay đủ ngay từ đầu      | `--scenario full`                 | Không cấp thêm, `n_khay_xong = 1` đúng một lần |
| Đủ số lượng nhưng sai ô  | `--scenario wrong_slot`           | status 2, không gắp, `n_cho` tăng              |
| Ảnh không đổi sau DONE   | `--scenario unchanged_after_done` | A→1 rồi status 2, không coi là đủ              |
| Bị che / confidence thấp | `--scenario occluded`             | status 2                                       |
| Vật nằm giữa hai ô       | `--scenario between_slots`        | status 2                                       |

### 7.2 Giai đoạn 2 – với ảnh thật và model

Chạy lại các ca trên bằng chuỗi ảnh thật: `--mode ai --images data/demo_seq/Sxx`. Phải có đủ trong video và log: **khay thiếu hai A và một C**, **khay đủ**, **khay sai ô**.

### 7.3 Ít nhất hai ca bất thường (tự chọn, đề bắt buộc)

Gợi ý:

- Tắt `bridge.py` giữa chu kỳ (mất kết nối) → robot vào nhánh lỗi, DO1 bật, không dùng dữ liệu cũ, sau khi bật lại và `RESET` thì tiếp tục an toàn.
- Sửa IP sai trong `ip` → `socket_open` thất bại → nhánh lỗi.
- `DONE` lặp / `GET` lặp (`tests/fake_robot.py --dup-get --dup-done`) → không đếm lặp.
- Gói trả về sai cú pháp / thiếu trường → robot không gắp.
- Ảnh bị che bằng tay giữa chuỗi.
- Đổi ánh sáng mạnh khiến confidence thấp.

### 7.4 Ghi kết quả

Với **mỗi ca**: ghi **kết quả dự kiến** (trước khi chạy), **kết quả quan sát** (sau khi chạy), **đạt/chưa đạt** ở ba cột riêng. Lưu: ảnh cây chương trình, ảnh bộ đếm (dùng Popup hoặc Wait trước khi dừng để chụp), file log `logs/session_*.csv` (copy sang `docs/` vì `.gitignore` bỏ `logs/*.csv`).

---

## 8. Bảng ca thử mẫu (điền vào báo cáo)

| Ca  | Đầu vào                            | Kết quả dự kiến                                           | Kết quả quan sát | Đạt |
| --- | ---------------------------------- | --------------------------------------------------------- | ---------------- | --- |
| T1  | Chỉ có B ở ô 3                     | A→1, A→2, C→4, sau mỗi lần có ảnh mới, cuối cùng status 3 |                  |     |
| T2  | Khay đủ từ đầu                     | Không phát lệnh bổ sung, đếm khay hoàn tất một lần        |                  |     |
| T3  | Đủ số lượng nhưng sai ô            | Phát hiện sai, nhánh ngoại lệ, không gắp                  |                  |     |
| T4  | Ảnh không đổi sau DONE hoặc bị che | Không coi đủ chỉ vì lệnh vừa chạy                         |                  |     |
| T5  | (ca bất thường 1 của nhóm)         |                                                           |                  |     |
| T6  | (ca bất thường 2 của nhóm)         |                                                           |                  |     |

Với nhóm AI, thêm vào bảng hoặc log CSV: mã ảnh, nhãn thật, confidence, gói tin, trạng thái DONE.

---

## 9. Báo cáo, video và hồ sơ nộp

### 9.1 Yêu cầu của đề cho đề AI

- **Báo cáo 12–20 trang.** Mục: đầu bài; bố trí và thông số; bảng I/O/biến; thuật toán; cây chương trình; **dữ liệu, mô hình, giao thức, sai số**; kết quả kiểm thử; nhận xét; kết luận; tài liệu tham khảo.
- **Video 5–7 phút:** hiện **ảnh AI (có bbox), gói tin và chuyển động robot**; có ca bình thường và ít nhất một ca bất thường.
- **Nộp:** `.urp`, `.installation` và tệp liên quan; báo cáo; video; bảng ca thử, đánh giá AI, log CSV, hiệu chuẩn nếu có; mã Python, `requirements.txt`, config mẫu, README, trọng số, danh sách chia tập. **Không** nộp `.venv`. Không chỉ nộp ảnh cây chương trình/video mà thiếu tệp chương trình.
- Ghi nhóm, đề gốc, thành viên, mã sinh viên và **phần việc từng người** trên báo cáo.

### 9.2 Thang điểm đề AI (để biết ưu tiên)

| Nội dung                                       | Điểm |
| ---------------------------------------------- | ---- |
| Dữ liệu, chia tập, gán nhãn, khả năng chạy lại | 2    |
| Huấn luyện AI, đánh giá, phân tích sai số      | 2,5  |
| URSim, Waypoint, If, SubProgram                | 2    |
| TCP, bắt tay, kiểm thử, nhánh lỗi              | 2    |
| Báo cáo, video, giải thích, trình diễn         | 1,5  |

### 9.3 Điểm hay mất điểm (cần ghi rõ trong báo cáo)

- Ghi phiên bản phần mềm (URSim 3.15.6.106324, Python, ultralytics, torch).
- Nói rõ **URSim chỉ kiểm chứng lệnh/chuyển động mô phỏng**, không kiểm chứng va chạm hay lực giữ phôi. Camera/ảnh chạy riêng trong Python.
- Nói rõ **chuỗi ảnh trước–sau là cảnh quản lý theo kịch bản**, không phải ảnh sinh ra từ robot.
- Tách **độ đúng của AI** khỏi **độ đúng robot thực hiện lệnh**.
- Báo cáo **số mẫu, số ca sai** (không chỉ phần trăm), tỉ lệ từ chối, và riêng số khay thiếu/sai bị nhận nhầm là đủ.
- Nguồn dữ liệu, cách tự tạo ảnh và giới hạn đại diện của dữ liệu (vật đơn giản, một bối cảnh).
- Khai báo bộ test **không dùng** để chọn mô hình/ngưỡng.
- Mục tiêu định lượng trong đề (≥ 90% trên ≥ 60 ảnh test, v.v.) là tiêu chí đối chiếu: báo cáo số **đo được thật**, kể cả khi chưa đạt.
- Mô tả cách xử lý: thiếu phôi, khay sai/không rõ, gói tin sai, quá thời gian, mất kết nối, **điều kiện phục hồi cụ thể**.

### 9.4 Checklist nộp

- [ ] `ursim/nhom2_main.urp`, `ursim/nhom2.installation`
- [ ] Bảng Waypoint, bảng I/O, bảng biến, sơ đồ trạm, ảnh cây chương trình
- [ ] `bridge.py`, `check_tray.py`, `infer.py`, `train.py`, `evaluate.py`, `config.json`, `requirements.txt`, `README.md`
- [ ] `weights/best.pt`
- [ ] `data/` (hoặc link Drive đã thống nhất) + `data/metadata.csv` + `data/splits.csv`
- [ ] Log CSV các ca thử (copy vào `docs/`)
- [ ] Bảng ca thử đầy đủ (dự kiến/quan sát/đạt)
- [ ] Báo cáo 12–20 trang
- [ ] Video 5–7 phút (có ca bình thường + bất thường, hiện ảnh AI, gói tin, chuyển động)
- [ ] Không có `.venv` trong hồ sơ

---

## 10. Lỗi hay gặp

| Hiện tượng                                | Nguyên nhân thường gặp                                                                 | Cách xử lý                                                                                |
| ----------------------------------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| URSim `socket_open` trả False             | Firewall chặn cổng 5000; sai IP; bridge chưa chạy                                      | Mở inbound rule TCP 5000 cho Windows; `ipconfig` lấy lại IP VMnet8/LAN; chạy bridge trước |
| Popup không liệt kê biến                  | Biến chưa tạo bằng Assignment                                                          | Thêm node Assignment `tên := giá trị` trước                                               |
| Bridge in `BAD_PACKET`                    | Robot gửi sai cú pháp (ví dụ `GET,1.0`)                                                | Dùng `to_str` trên biến nguyên `cid`; kiểm tra chuỗi gửi                                  |
| Bridge trả `status 4`                     | Còn lệnh chưa DONE từ lần chạy trước                                                   | Ctrl+C và chạy lại bridge, hoặc robot gửi `RESET,<cid>` có xác nhận                       |
| Bridge luôn trả status 2 với ảnh thật     | Hình chữ nhật ô trong `config.json` không khớp ảnh thật; ngưỡng cao; vật sát ranh giới | Vẽ lại tọa độ ô theo ảnh thật; kiểm tra `conf_min`, `boundary_margin_px`                  |
| Lệnh đúng nhưng sau DONE lại báo status 2 | Ảnh bước kế chưa có vật vừa đặt, hoặc thứ tự ảnh trong thư mục sai                     | Kiểm tra tên ảnh (`step0, step1, …`); đúng kịch bản                                       |
| Robot báo "không với tới"                 | Waypoint quá xa/góc quá khó                                                            | Dịch điểm lại gần gốc robot, giữ hướng đầu kẹp cố định                                    |
| MoveL lệch sau khi đổi TCP                | Đổi TCP sau khi dạy điểm                                                               | Đặt TCP trước; dạy lại điểm nếu lỡ đổi                                                    |
| `yolo` không nhận lệnh                    | Chưa kích hoạt `.venv` hoặc chưa cài ultralytics                                       | `.venv\Scripts\activate`, `pip install ultralytics`                                       |
| Kết quả test quá cao bất thường           | Ảnh cùng bố trí nằm ở cả train và test (rò rỉ dữ liệu)                                 | Chia lại theo `layout_id`                                                                 |
| Git conflict trên `.urp`                  | Hai người cùng sửa                                                                     | Chỉ P1 sửa/commit `.urp`; người khác không lưu đè                                         |

---

## 11. Việc còn thiếu trong code (cần viết)

Những file/chức năng sau **chưa có**, ai nhận thì ghi vào bảng phân công:

| Việc                                                                                                                     | Người đề xuất | Ghi chú                                                        |
| ------------------------------------------------------------------------------------------------------------------------ | ------------- | -------------------------------------------------------------- |
| `split_dataset.py`: đọc `metadata.csv`, chia 60/20/20 theo `layout_id`, sinh `splits.csv` và cấu trúc `data/yolo/`       | P2            | Seed cố định, giữ các `condition` ở cả 3 tập                   |
| `train.py`: bọc lệnh huấn luyện YOLO, lưu cấu hình                                                                       | P3            | Có thể chỉ gọi `ultralytics.YOLO(...).train(...)`              |
| `evaluate.py`: chạy test, tính độ đúng cấp khay, số khay thiếu/sai nhận nhầm đủ, confusion matrix, lưu ảnh sai, xuất CSV | P3            | Dùng `infer.detect` + `check_tray.check_tray` + `metadata.csv` |
| Vẽ bbox/ô trạng thái lên ảnh và hiển thị/lưu khi bridge chạy (để quay video "hiện ảnh AI")                               | P3            | Có thể dùng OpenCV                                             |
| Ghi thời gian suy luận vào log CSV (hiện chỉ in ra console)                                                              | P3            | Cột riêng với thời gian chu kỳ                                 |
| Chương trình URSim hoàn chỉnh (mục 6)                                                                                    | P1            |                                                                |

---

## 12. Thứ tự ưu tiên khi thiếu thời gian

1. **P2 chụp ảnh ngay** (nút thắt: dữ liệu → gán nhãn → train). Đừng chờ.
2. **P1 hoàn thành URSim chạy được ca `only_B` với bridge box giả** → có bản demo đầu tiên.
3. **P3 viết `split_dataset.py` + train baseline** ngay khi có khoảng 50–100 ảnh đã gán nhãn, rồi cải thiện dần.
4. Ghép AI vào bridge (mục 5.9) khi có `best.pt` đầu tiên (chưa cần tốt).
5. Chạy 4 ca bắt buộc + 2 ca bất thường, **ghi bảng ca thử ngay lúc chạy**.
6. Viết báo cáo, quay video. Dành ít nhất 2 ngày cuối, không bỏ.

Nếu phải cắt: giữ **pipeline chạy được từ đầu đến cuối** (ảnh → YOLO → check_tray → bridge → URSim → DONE) với dữ liệu ít hơn, và **báo cáo trung thực** giới hạn đã đạt. Mọi mục tiêu định lượng trong đề là tiêu chí đối chiếu, không phải kết quả có sẵn.
