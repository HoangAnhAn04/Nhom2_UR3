# Nhóm 2 – Robot UR3 + AI: kiểm tra đủ bộ khay và điều phối bổ sung linh kiện

|             |                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------- |
| Bài tập lớn | UR3 – đề của Nhóm 2: _Kiểm tra đủ bộ sản phẩm và điều phối bổ sung_ (mức Nâng cao, nhóm AI) |
| Giảng viên  | PGS. TS. Võ Thanh Hà – Bộ môn Điều khiển học, Khoa Điện–Điện tử, ĐH Giao thông Vận tải      |
| Thành viên  | (điền: họ tên – mã sinh viên – phần việc)                                                   |

**Phiên bản phần mềm (ghi nguyên văn vào báo cáo):**

| Phần mềm              | Phiên bản                                                  |
| --------------------- | ---------------------------------------------------------- |
| URSim UR3 (CB-Series) | PolyScope **3.15.6.106324**, chạy trong VMware Workstation |
| Python                | (điền sau khi chạy `python --version`)                     |
| ultralytics / torch   | (điền sau khi cài, xem `pip freeze`)                       |
| Thiết bị huấn luyện   | (điền: CPU / GPU gì, hoặc Google Colab)                    |

> **Cách dùng file này.** Mục 1–3 để hiểu bài toán và các khái niệm (đọc một lượt, không cần nhớ hết).
> Mục 4–8 là cấu trúc dự án, phân công, cài đặt. Mục 9–10 là **giao thức gói tin** và **logic kiểm tra khay** (phần cốt lõi, cả nhóm phải hiểu).
> Mục 11–12 là việc cần làm cho phần AI và phần URSim. Mục 13–19 là kiểm thử, báo cáo, nộp bài, xử lý lỗi, thứ tự ưu tiên.

## Mục lục

1. [Đề bài nói gì](#1-đề-bài-nói-gì)
2. [Sơ đồ hệ thống](#2-sơ-đồ-hệ-thống)
3. [Kiến thức nền cho người chưa học](#3-kiến-thức-nền-cho-người-chưa-học)
4. [Cấu trúc repo](#4-cấu-trúc-repo)
5. [Phân công](#5-phân-công)
6. [Hiện trạng](#6-hiện-trạng)
7. [Việc phải hỏi giảng viên](#7-việc-phải-hỏi-giảng-viên)
8. [Cài đặt môi trường và Git](#8-cài-đặt-môi-trường-và-git)
9. [Giao thức gói tin Python ↔ URSim](#9-giao-thức-gói-tin-python--ursim)
10. [Logic kiểm tra khay và file config.json](#10-logic-kiểm-tra-khay-và-file-configjson)
11. [Phần AI: dữ liệu, huấn luyện, đánh giá, tích hợp](#11-phần-ai-dữ-liệu-huấn-luyện-đánh-giá-tích-hợp)
12. [Phần URSim: TCP, Waypoint, SubProgram, vòng lặp chính](#12-phần-ursim-tcp-waypoint-subprogram-vòng-lặp-chính)
13. [Ghép hệ thống và kiểm thử](#13-ghép-hệ-thống-và-kiểm-thử)
14. [Bảng ca thử mẫu](#14-bảng-ca-thử-mẫu)
15. [Báo cáo, video, hồ sơ nộp](#15-báo-cáo-video-hồ-sơ-nộp)
16. [Câu hỏi vấn đáp mẫu](#16-câu-hỏi-vấn-đáp-mẫu)
17. [Lỗi hay gặp](#17-lỗi-hay-gặp)
18. [Việc còn thiếu trong code](#18-việc-còn-thiếu-trong-code)
19. [Thứ tự ưu tiên khi thiếu thời gian](#19-thứ-tự-ưu-tiên-khi-thiếu-thời-gian)
20. [Tài liệu tham khảo](#20-tài-liệu-tham-khảo)

---

## 1. Đề bài nói gì

Mỗi **khay đơn hàng** cần đúng bốn linh kiện đặt vào bốn ô cố định:

| Ô   | Tên | `slot` | Linh kiện cần có |
| --- | --- | ------ | ---------------- |
| 1   | A1  | 1      | A                |
| 2   | A2  | 2      | A                |
| 3   | B1  | 3      | B                |
| 4   | C1  | 4      | C                |

(Tức là mỗi khay cần **hai A, một B, một C**.)

Quy trình mà hệ thống phải làm:

1. **Camera** (nhóm dùng điện thoại gác cố định hoặc ảnh có sẵn) chụp toàn khay.
2. **AI (YOLO) trong Python** nhìn ảnh, tìm các linh kiện A/B/C và vị trí của chúng, rồi xác định mỗi ô đang **trống / đúng / sai loại / dư / không rõ**.
3. Python **lập danh sách ô còn thiếu** theo thứ tự A1 → A2 → B1 → C1 và **phát từng lệnh một** cho robot dưới dạng `(class, slot)`, ví dụ "lấy A đặt vào ô 2".
4. **Robot UR3 (mô phỏng bằng URSim)** lấy linh kiện từ **ba vị trí cấp cố định** (một chỗ cho A, một cho B, một cho C), đặt vào ô được chỉ định, rồi báo `DONE`.
5. Python **yêu cầu ảnh mới**, chạy AI lại, quyết định lệnh kế tiếp.
6. Khi ảnh mới cho thấy khay **đủ, đúng loại, đúng ô** thì mới báo **hoàn tất khay** (`status = 3`).

Các ràng buộc quan trọng của đề (hay bị mất điểm):

- **Không cấp phôi** vào ô đã có vật, ô sai loại, hoặc ô chưa xác định được tình trạng.
- **Lệnh sai cặp class/slot không được chạy**: A chỉ được đặt vào ô 1 hoặc 2; B chỉ ô 3; C chỉ ô 4.
- **Robot không tự cấp hết danh sách** trong một lần. Mỗi lần chỉ làm một lệnh, rồi chờ ảnh mới kiểm tra.
- **Không được sửa kết quả AI thành "đủ bộ" chỉ vì robot vừa chạy xong lệnh.** Phải có ảnh mới và AI nhìn thấy thật.
- Xung **DO2** (báo hoàn tất một lần đặt) **tách khỏi** bộ đếm khay hoàn tất; mỗi khay chỉ tăng bộ đếm **một lần**.
- Khay có vật dư / sai loại / bị che khuất → chuyển sang **nhánh xử lý ngoại lệ**, không tự xác nhận hoàn tất.
- Mục tiêu đối chiếu của đề: **tỷ lệ nhận định đúng trạng thái đầy đủ/thiếu/sai ≥ 90% trên ít nhất 60 ảnh test**; báo cáo riêng số khay thiếu/sai bị nhận nhầm là đủ. Đây là **tiêu chí đối chiếu, không phải số liệu có sẵn**: báo cáo số đo được thật, kể cả khi chưa đạt.
- Ca mẫu bắt buộc: khay ban đầu chỉ có B ở ô 3 → phải phát đúng **ba lệnh A→1, A→2, C→4**, kiểm tra ảnh mới sau mỗi lần đặt.

**Điều URSim làm được và không làm được** (phải nói rõ trong báo cáo): URSim chỉ kiểm tra chương trình và chuyển động mô phỏng. URSim **không tự nhận dạng ảnh**, không kiểm chứng va chạm, không kiểm chứng lực giữ phôi. Camera và ảnh chạy riêng trong Python.

---

## 2. Sơ đồ hệ thống

```
   ảnh khay (điện thoại / ảnh có sẵn)
        │
        ▼
┌─────────────────────────────  MÁY WINDOWS (Python)  ─────────────────────────────┐
│                                                                                  │
│  infer.py ──► check_tray.py ──► bridge.py  (TCP SERVER, cổng 5000)               │
│  YOLO tìm     phân tích 4 ô,     nhận GET/DONE, trả lệnh                         │
│  vật A/B/C    sinh lệnh          nhớ id, ghi log CSV, quản lý thứ tự ảnh         │
└──────────────────────────────────────────┬───────────────────────────────────────┘
                                           │  mạng nội bộ (TCP), chữ thường, mỗi gói 1 dòng
                                           ▼
┌──────────────────────  MÁY ẢO VMware: URSim UR3 / PolyScope 3.15.6  ─────────────┐
│  Chương trình .urp (TCP CLIENT): GET → đọc lệnh → Lay_A/B/C → Dat_VaoO → DONE    │
│  Waypoint, SubProgram, DO0 (kẹp), DO1 (lỗi), DO2 (xung hoàn tất), bộ đếm         │
└──────────────────────────────────────────────────────────────────────────────────┘
```

Phân vai dễ nhớ:

- **Python là "mắt và não"**: nhìn ảnh, quyết định làm gì tiếp theo.
- **URSim là "tay"**: nhận lệnh, di chuyển, báo xong.
- Hai bên **chỉ nói chuyện qua các dòng chữ** (gói tin). Quy ước các dòng chữ đó là mục 9.

---

## 3. Kiến thức nền cho người chưa học

### 3.1 Robot và URSim

- **UR3**: tay máy 6 khớp của Universal Robots, tầm với khoảng 500 mm.
- **URSim**: phần mềm mô phỏng robot UR trên máy tính. Nó chạy giao diện **PolyScope** giống robot thật nhưng robot chỉ là hình 3D.
- **PolyScope**: giao diện lập trình robot UR, có các tab **Program** (chương trình), **Installation** (cài đặt robot), **Move** (di chuyển tay), **I/O** (tín hiệu vào/ra), **Log** (nhật ký).
- **Chương trình dạng cây**: chương trình là một cây các **node** (lệnh), robot chạy từ trên xuống. Thêm node ở tab **Structure** (nhóm Basic: Move, Waypoint, Wait, Set, Popup, Loop, If, Assignment; nhóm Advanced: Script, SubProgram...).
- **Waypoint**: một "điểm dạy", lưu vị trí các khớp (và vị trí đầu kẹp). Robot di chuyển giữa các Waypoint.
- **MoveJ**: di chuyển theo khớp, đường đi cong, nhanh, dùng để chuyển giữa các vùng.
- **MoveL**: di chuyển thẳng theo đường thẳng của đầu kẹp, dùng để **hạ xuống / nâng lên** chính xác.
- **Điểm tiếp cận (approach)**: điểm nằm cao hơn vị trí gắp/đặt khoảng 100 mm. Robot đi tới điểm này trước, rồi hạ thẳng xuống bằng MoveL, nâng thẳng lên, tránh va vào vật.
- **TCP (Tool Center Point) – điểm tâm công cụ**: điểm mà robot coi là "đầu kẹp". Mặc định là mặt bích cuối tay. Đặt TCP lệch ra 100 mm theo trục Z nghĩa là robot hiểu đầu kẹp dài 100 mm. Bắt buộc đặt TCP **trước khi dạy Waypoint**.
  > **Cẩn thận nhầm lẫn:** chữ "TCP" trong bài này có **hai nghĩa khác nhau**. (1) _Tool Center Point_ là điểm đầu kẹp của robot (Installation → TCP Configuration). (2) _TCP/IP_ là giao thức mạng để Python và URSim gửi chữ cho nhau (mục 9). Hai thứ không liên quan.
- **SubProgram**: chương trình con có tên riêng (ví dụ `Lay_A`), được gọi từ chương trình chính. Đề yêu cầu tối thiểu hai SubProgram.
- **Biến chương trình**: nơi lưu số (bộ đếm, mã chu kỳ...). Tạo bằng node **Assignment** (`tên := giá trị`).
- **I/O**: tín hiệu số. **DO** = Digital Output (robot bật/tắt). Bài này quy ước:

| Tín hiệu    | Ý nghĩa trong bài                                 |
| ----------- | ------------------------------------------------- |
| DO0         | **On = đóng kẹp, Off = mở kẹp** (giả lập)         |
| DO1         | **Báo lỗi** chương trình / quy trình / kết nối    |
| DO2         | **Xung báo hoàn tất một lần đặt** (bật rồi tắt)   |
| DO3 trở lên | Chức năng thêm nếu nhóm cần (phải lập bảng riêng) |

### 3.2 Mạng và socket (để hiểu phần gói tin)

- **IP**: địa chỉ một máy trong mạng, ví dụ `192.168.61.1`. **Cổng (port)**: "số cửa" trên máy đó, bài này dùng **5000**.
- **Socket**: kết nối giữa hai chương trình qua mạng. Một bên là **server** (ngồi chờ ở một IP:cổng), bên kia là **client** (chủ động gọi tới).
  - Ở bài này **Python là server**, **URSim là client** (đề quy định như vậy). Server phải **chạy trước**, client mới nối vào được.
- **TCP/IP là "dòng byte", không phải "tin nhắn"**: dữ liệu gửi qua TCP không có ranh giới tự nhiên. Một lần nhận có thể được **nửa dòng**, hoặc **hai dòng dính nhau**. Vì vậy mỗi gói của nhóm **kết thúc bằng ký tự xuống dòng `\n`** (newline) để biết gói đã hết. Phía Python đọc vào bộ đệm và chỉ xử lý khi đã thấy `\n`.
- **Máy ảo (VMware)**: URSim chạy trong "máy khác" nên địa chỉ `127.0.0.1` (chính máy đó) **sai**. Phải dùng IP của máy Windows mà máy ảo nhìn thấy (xem mục 9.12).
- **Firewall** của Windows có thể chặn cổng 5000, khiến URSim không nối được.

### 3.3 AI nhận dạng ảnh (YOLO)

- **Phát hiện đối tượng (object detection)**: đưa vào một ảnh, mô hình trả về một danh sách các **hộp (bounding box)**, mỗi hộp gồm: **vị trí** (góc trên trái x1,y1 và góc dưới phải x2,y2, đơn vị pixel), **lớp** (A, B hay C), và **độ tin cậy (confidence)** từ 0 đến 1.
- **YOLO** ("You Only Look Once"): một họ mô hình phát hiện đối tượng nhanh. Bài dùng **YOLOv8n** (bản nhỏ nhất, đủ cho dữ liệu ít).
- **Tinh chỉnh (fine-tune)**: không huấn luyện từ số 0, mà lấy mô hình đã học sẵn nhiều thứ (`yolov8n.pt`, học trên bộ ảnh COCO) rồi dạy thêm bằng ảnh của nhóm để nó nhận ra A, B, C.
- **Gán nhãn (labeling)**: người vẽ hộp quanh từng vật trong ảnh huấn luyện và ghi đó là A/B/C. Mô hình học từ các hộp này.
- **Tập train / validation / test**:
  - **train**: ảnh để mô hình học.
  - **validation (val)**: ảnh để **chọn mô hình và chọn ngưỡng** trong lúc làm.
  - **test**: ảnh **chưa từng dùng để chọn gì cả**, chỉ để chấm điểm cuối cùng một lần.
  - Chia **60 / 20 / 20 %**.
- **Rò rỉ dữ liệu (data leakage)**: nếu hai ảnh gần giống nhau (cùng một cách xếp khay, chụp hơi khác) lọt vào hai tập khác nhau (một ảnh ở train, một ở test), mô hình "thuộc bài" nên điểm test cao ảo. Vì vậy phải **chia theo bố trí khay**, không chia ngẫu nhiên từng ảnh.
- **Tăng cường dữ liệu (augmentation)**: tự biến đổi ảnh (đổi sáng, lật...) để có thêm biến thể. Đề quy định **chỉ làm trên tập train**. Ultralytics tự làm khi huấn luyện, và chỉ áp dụng cho train.
- **Confidence và ngưỡng**: mô hình luôn trả ra confidence. Ta đặt **ngưỡng** (ví dụ 0,5): dưới ngưỡng thì coi là không tin cậy. Ngưỡng chọn bằng tập **val**, sau đó **khóa** (không đổi nữa) rồi mới chấm test.
- **IoU (Intersection over Union)**: độ chồng lấn giữa hai hộp, từ 0 (không chồng) đến 1 (trùng khít). Dùng để loại hộp **trùng** (hai hộp cùng chỉ một vật): giữ hộp confidence cao hơn.
- **Precision / Recall**: _precision_ = trong các vật mô hình báo, bao nhiêu phần trăm đúng; _recall_ = trong các vật có thật, mô hình tìm ra bao nhiêu phần trăm.
- **mAP50 và mAP50-95**: điểm tổng hợp chất lượng phát hiện. mAP50 coi một hộp là đúng khi IoU với hộp thật ≥ 0,5; mAP50-95 lấy trung bình ở nhiều mức IoU nghiêm hơn (0,5 đến 0,95).

### 3.4 Ba thuật ngữ của bài (đừng nhầm)

- **Nhận dạng đúng vật** (mức mô hình): mô hình tìm đúng hộp và đúng lớp. Đo bằng mAP, precision, recall.
- **Nhận định đúng trạng thái khay** (mức hệ thống): từ các hộp, hệ thống kết luận khay _đủ / thiếu / sai_ có đúng với thực tế không. Đây là chỉ số mà **đề đặt mục tiêu ≥ 90%**.
- **Robot thực hiện đúng lệnh đã nhận**: robot làm đúng điều Python bảo (đúng class, đúng slot). Chỉ số này tách riêng với hai cái trên.

---

## 4. Cấu trúc repo

```
Nhom2_UR3/
├── README.md              (file này)
├── requirements.txt       thư viện Python
├── config.json            IP/cổng, tọa độ 4 ô, ngưỡng, đường dẫn trọng số
├── .gitignore
├── bridge.py              TCP server: nhận GET/DONE/RESET, trả lệnh, ghi log CSV
├── check_tray.py          logic kiểm tra 4 ô và sinh lệnh bổ sung
├── infer.py               chạy YOLO trên một ảnh, trả danh sách hộp
├── train.py               (CHƯA viết) huấn luyện YOLO
├── evaluate.py            (CHƯA viết) đánh giá trên tập test
├── tests/
│   ├── scenarios.py       kịch bản ảnh giả (hộp giả) để thử khi chưa có AI
│   ├── test_check_tray.py 10 test cho logic khay
│   └── fake_robot.py      robot giả (client) để thử bridge không cần URSim
├── ursim/                 .urp, .installation, bảng Waypoint, bảng I/O
├── data/                  ảnh, nhãn, metadata.csv, splits.csv, demo_seq/
├── weights/               best.pt (trọng số YOLO đã huấn luyện)
├── logs/                  log CSV sinh ra mỗi lần chạy bridge
└── docs/                  sơ đồ trạm, ảnh cây chương trình, log đã chọn, báo cáo
```

Ai được sửa gì:

- `ursim/*.urp`, `ursim/*.installation`: **chỉ P1** sửa và commit (file này dễ xung đột khi nhiều người cùng sửa).
- `bridge.py`, `check_tray.py`, `config.json`: sửa khi cần nhưng **báo cả nhóm**, vì ảnh hưởng cả URSim lẫn AI.
- `data/`: P2. `weights/`, `train.py`, `evaluate.py`, `infer.py`: P3.

---

## 5. Phân công

Điền tên/MSV. Có thể đổi vai nhưng mỗi mảng phải có **một người chịu trách nhiệm** và **mỗi người phải giải thích được phần mình** khi vấn đáp.

| Vai                         | Người  | Phần việc                                                                                         | Sản phẩm bàn giao                                                                                 |
| --------------------------- | ------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **P1 – URSim**              | (điền) | TCP, Waypoint, SubProgram, vòng lặp chính, bộ đếm, DO0/DO1/DO2, nhánh lỗi, chạy ca thử trên URSim | `ursim/nhom2_main.urp`, `ursim/nhom2.installation`, bảng Waypoint, bảng I/O, ảnh cây chương trình |
| **P2 – Dữ liệu**            | (điền) | Chụp ảnh, ghi `metadata.csv`, gán nhãn, chia tập, chụp chuỗi ảnh trước–sau                        | `data/` đủ ảnh + nhãn + `splits.csv`, mô tả dữ liệu                                               |
| **P3 – Mô hình & đánh giá** | (điền) | Huấn luyện YOLO, chọn/khóa ngưỡng, đánh giá test, phân tích ca sai, chạy `--mode ai`              | `weights/best.pt`, kết quả train/test, log đánh giá, ảnh sai dự đoán                              |
| **Cả nhóm**                 |        | Ghép, chạy ca thử, quay video, viết báo cáo                                                       | Báo cáo, video                                                                                    |

Chia viết báo cáo: P1 viết bố trí / TCP / Waypoint / cây chương trình / kiểm thử URSim; P2 viết dữ liệu; P3 viết mô hình / đánh giá / sai số; giao thức, thuật toán, kết luận viết chung.

---

## 6. Hiện trạng

Cập nhật bảng này mỗi khi xong việc.

| Hạng mục                                                            | Trạng thái                                                                                                      |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Cấu trúc repo, `.gitignore`, `requirements.txt`                     | Xong                                                                                                            |
| `check_tray.py` + `tests/test_check_tray.py`                        | Xong (10/10 test qua)                                                                                           |
| `bridge.py` (TCP server, GET/DONE/RESET, log CSV, kịch bản ảnh giả) | Xong; chạy đúng với `tests/fake_robot.py` ở các kịch bản `only_B`, `full`, `wrong_slot`, `unchanged_after_done` |
| Nối URSim ↔ bridge: `socket_open`, gửi `GET`, đọc 8 số              | Xong; URSim nhận được `[8, 1, 1, 1, 0, 0, 0, 0.95, 1]`                                                          |
| URSim: TCP `Kep`                                                    | Đã tạo                                                                                                          |
| URSim: Waypoint, SubProgram, vòng lặp chính, bộ đếm                 | **Chưa**                                                                                                        |
| Dữ liệu ảnh, gán nhãn, chia tập                                     | **Chưa**                                                                                                        |
| Huấn luyện YOLO, đánh giá, khóa ngưỡng                              | **Chưa**                                                                                                        |
| Chuỗi ảnh trước–sau, chạy tích hợp `--mode ai`                      | **Chưa**                                                                                                        |
| Báo cáo 12–20 trang, video 5–7 phút                                 | **Chưa**                                                                                                        |

---

## 7. Việc phải hỏi giảng viên

Làm ngay, gộp một tin nhắn:

- Mốc **28/10** là **nghiệm thu cuối** hay **kiểm tra tiến độ**? Cần nộp/trình bày gì ở mốc đó? (Đề ghi 6 tuần cho đề AI nhưng nhóm được chia ngày 15/10.)
- Dùng **ảnh chụp bằng điện thoại và ảnh tĩnh quản lý theo kịch bản** (không webcam/robot thật) có được không? (Đề cho phép, nên xác nhận.)
- Ba lớp A/B/C là vật đơn giản tự chọn (khác màu, khác hình) có được không?

---

## 8. Cài đặt môi trường và Git

### 8.1 Python (mỗi người làm một lần)

Mở thư mục dự án bằng VS Code (**File → Open Folder**), mở Terminal, chạy:

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python tests/test_check_tray.py
```

Lệnh cuối phải in `10/10 OK`. Chọn đúng môi trường trong VS Code: `Ctrl+Shift+P` → _Python: Select Interpreter_ → chọn `.venv`.

Cuối dự án, một người chạy `python -m pip freeze > requirements.txt` để ghi phiên bản đã dùng. **Không** nộp thư mục `.venv`.

### 8.2 Git

```
git clone <link-repo>
cd Nhom2_UR3
git pull                       # LUÔN pull trước khi làm
# ... làm việc ...
git add <tên file>             # tránh "git add ." nếu lỡ có file nặng
git commit -m "P2: them 120 anh khay + metadata"
git push
```

Quy tắc:

- File `.urp` / `.installation` **chỉ P1** sửa và commit.
- Không commit `.venv/`, `__pycache__/`, `runs/` (đã có trong `.gitignore`).
- Ảnh nhỏ (vài chục MB) cho lên repo. Quá nặng thì để Google Drive và ghi link vào `data/README.md` (đề cho phép "cách truy cập đã thống nhất với giảng viên").
- `weights/best.pt` của YOLOv8n nặng khoảng vài MB, commit được.
- Commit nhỏ, thường xuyên, câu commit nói rõ làm gì. Repo để **private**, thêm các bạn làm collaborator.

### 8.3 Chạy thử nhanh (chưa cần AI, chưa cần URSim)

Mở **hai terminal**, cả hai đều đã kích hoạt `.venv`, đều đứng ở thư mục gốc repo:

```
python bridge.py --mode script --scenario only_B          # terminal 1: server
python tests/fake_robot.py                                # terminal 2: robot giả
```

Kết quả đúng: robot giả nhận lần lượt **A→ô 1, A→ô 2, C→ô 4**, rồi `status 3` (khay hoàn tất). Mỗi lần chạy bridge sinh một file `logs/session_*.csv`. Thêm `--dup-get --dup-done` cho `fake_robot.py` để cố tình gửi lặp và xem bridge xử lý.

Các kịch bản có sẵn (`--scenario`):

| Tên                    | Mô tả                                                        | Kết quả mong đợi            |
| ---------------------- | ------------------------------------------------------------ | --------------------------- |
| `only_B`               | Ban đầu chỉ có B ở ô 3, mỗi lần đặt xong ảnh sau có thêm vật | A→1, A→2, C→4, rồi status 3 |
| `full`                 | Khay đủ ngay                                                 | status 3, không cấp thêm    |
| `wrong_slot`           | Đủ 4 vật nhưng sai ô                                         | status 2 (ngoại lệ)         |
| `unchanged_after_done` | Sau DONE, ảnh mới không đổi                                  | A→1, rồi status 2           |
| `occluded`             | Vật ở ô 1 có confidence thấp (bị che)                        | status 2                    |
| `between_slots`        | Vật nằm giữa hai ô                                           | status 2                    |

> Lưu ý: các kịch bản này là **hộp giả** (không có ảnh thật), chỉ để thử logic và giao tiếp trước khi có AI. Khi nghiệm thu phải chạy bằng **ảnh thật + YOLO** (`--mode ai`, mục 11.9).

---

## 9. Giao thức gói tin Python ↔ URSim

### 9.1 Nguyên tắc chung

- Hai bên nói chuyện bằng **dòng chữ ASCII**. **Mỗi gói là một dòng, kết thúc bằng ký tự xuống dòng `\n`.**
- **Python = server** (cổng 5000, chạy trước). **URSim = client**, chủ động nối vào bằng `socket_open(IP, 5000)`.
- **Robot luôn là bên chủ động hỏi**: robot gửi yêu cầu, Python trả lời. Python không tự gửi gì khi robot chưa hỏi.
- Mỗi chu kỳ có một **mã chu kỳ `id`** (số nguyên, robot tăng dần 1, 2, 3, ...; không trùng trong một phiên). Python dùng `id` để nhớ "chu kỳ này đã trả lệnh gì", robot dùng `id` để kiểm tra "gói trả về có đúng chu kỳ của mình không".
- Đề cho phép nhóm tự đặt cú pháp `GET`/`DONE` nhưng phải ghi chính xác và giữ nhất quán hai phía. Dưới đây là cú pháp của nhóm.

### 9.2 Các gói

| Hướng          | Gói (một dòng)                              | Ý nghĩa                                           | Python có trả lời không   |
| -------------- | ------------------------------------------- | ------------------------------------------------- | ------------------------- |
| Robot → Python | `GET,<id>`                                  | "Cho tôi lệnh của chu kỳ `<id>`"                  | **Có**, trả một dòng 8 số |
| Python → Robot | `(id,status,class,x,y,yaw,confidence,slot)` | Lệnh/trạng thái của chu kỳ                        | (đây là câu trả lời)      |
| Robot → Python | `DONE,<id>`                                 | "Tôi đã làm xong chu kỳ `<id>`"                   | **Không** trả lời         |
| Robot → Python | `RESET,<id>`                                | Người vận hành đã kiểm tra, xin xóa lệnh đang chờ | Có, trả `status 0`        |

Ví dụ thật: `GET,17` + xuống dòng. Python trả `(17,1,1,0,0,0,0.93,2)` + xuống dòng. Robot làm xong thì gửi `DONE,17` + xuống dòng.

Gói trả về **bắt buộc** có ngoặc tròn, dấu phẩy, ký tự xuống dòng ở cuối, vì hàm `socket_read_ascii_float` của PolyScope cần đúng định dạng đó.

### 9.3 Gói trả lời gồm 8 trường

`(id, status, class, x, y, yaw, confidence, slot)` — đúng thứ tự này.

| #   | Trường       | Kiểu      | Miền giá trị | Ý nghĩa trong bài này                                                      |
| --- | ------------ | --------- | ------------ | -------------------------------------------------------------------------- |
| 1   | `id`         | số nguyên | ≥ 1          | Mã chu kỳ, **giống hệt** id robot vừa gửi trong `GET`                      |
| 2   | `status`     | số nguyên | 0–4          | Trạng thái chung (bảng 9.4)                                                |
| 3   | `class`      | số nguyên | 0–3          | Loại linh kiện cần lấy: 1=A, 2=B, 3=C; **0 khi không có lệnh**             |
| 4   | `x`          | số thực   | luôn 0       | Tọa độ X trong hệ Base (m). **Bài này không dùng** (dùng Waypoint cố định) |
| 5   | `y`          | số thực   | luôn 0       | Tọa độ Y (m). Không dùng                                                   |
| 6   | `yaw`        | số thực   | luôn 0       | Góc xoay (rad). Không dùng                                                 |
| 7   | `confidence` | số thực   | 0–1          | Độ tin cậy của nhận định (xem 9.6)                                         |
| 8   | `slot`       | số nguyên | 0–4          | Ô đích: 1=A1, 2=A2, 3=B1, 4=C1; **0 khi không có lệnh**                    |

Vì sao `x, y, yaw` vẫn có mặt dù luôn bằng 0? Vì đề dùng **chung một định dạng 8 số** cho cả 12 nhóm; nhóm nào không cần trường nào thì để 0 và bỏ qua phía robot.

### 9.4 Ý nghĩa `status`

| status | Tên                     | Python phát khi nào                                                                                                  | Robot phải làm gì                                                                                                        | Robot có gửi DONE?         |
| ------ | ----------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| **0**  | Chờ / không có mục tiêu | Không có gì để làm lúc này (ví dụ trả lời cho `RESET`)                                                               | Chờ rồi hỏi lại bằng `id` **mới**. Không di chuyển                                                                       | Không                      |
| **1**  | Lệnh hợp lệ             | Có ô trống cần bổ sung và các ô khác đều đúng, ví dụ "lấy A đặt ô 2"                                                 | Kiểm tra lại (conf, class/slot tương thích), rồi gọi `Lay_*` và `Dat_VaoO`, sau đó gửi `DONE`                            | **Có**, sau khi đặt xong   |
| **2**  | Cần kiểm tra lại        | Ảnh có vấn đề: vật sai ô/sai loại, dư vật, vật nằm giữa hai ô, confidence thấp (bị che), ảnh không đổi sau DONE      | **Không di chuyển, không cấp phôi.** Chờ/ngoại lệ, rồi hỏi lại bằng `id` mới; quá số lần thử thì dừng chờ người vận hành | Không                      |
| **3**  | Khay hoàn tất           | Cả 4 ô đều đúng loại, đúng ô, trong ảnh mới                                                                          | Tăng bộ đếm khay hoàn tất **đúng một lần**, kết thúc                                                                     | **Có**, để xác nhận đã đếm |
| **4**  | Lỗi                     | Gói yêu cầu sai cú pháp; lệnh class/slot không tương thích; hoặc robot hỏi `id` mới trong khi lệnh trước chưa `DONE` | Bật DO1, vào nhánh lỗi, không gắp                                                                                        | Không                      |

Quy tắc chốt: **chỉ `status = 1` mới khiến robot di chuyển.** Mọi trạng thái khác thì robot đứng yên.

### 9.5 `class` và `slot` và cặp hợp lệ

| class | Loại | Chỉ được đặt vào slot |
| ----- | ---- | --------------------- |
| 1     | A    | 1 (A1) hoặc 2 (A2)    |
| 2     | B    | 3 (B1)                |
| 3     | C    | 4 (C1)                |

Cặp sai (ví dụ A→ô 3, B→ô 1) **không được chạy**. Python tự kiểm tra trước khi gửi (nếu sai thì gửi `status 4`) và **robot kiểm tra lại một lần nữa** (kiểm tra hai lớp).

Ba vị trí **cấp** phôi (lấy A, lấy B, lấy C) là cố định và được dạy bằng Waypoint; `class` quyết định robot đi tới chỗ cấp nào.

### 9.6 `confidence` là gì

Quy tắc nhóm đã công bố: `confidence` = **giá trị nhỏ nhất** trong các confidence của những vật được hệ thống chấp nhận trong ảnh; nếu ảnh không có vật nào được chấp nhận (khay trống) thì `confidence = 1.0`.
Ý nghĩa: "độ tin cậy của cả bức tranh bằng độ tin cậy của vật kém chắc chắn nhất". Robot **kiểm tra lại ngưỡng** (`conf >= 0.5`) trước khi gắp, đề yêu cầu "kiểm tra lại ngưỡng ở client".

### 9.7 Ví dụ hội thoại thật (trích từ lần chạy thử của nhóm)

**Ca A – `only_B`: ban đầu chỉ có B ở ô 3, ba lần bổ sung rồi hoàn tất**

| Chu kỳ | Robot gửi | Python trả             | Robot làm                         | Robot gửi tiếp |
| ------ | --------- | ---------------------- | --------------------------------- | -------------- |
| 1      | `GET,1`   | `(1,1,1,0,0,0,0.95,1)` | Lấy A, đặt vào ô 1                | `DONE,1`       |
| 2      | `GET,2`   | `(2,1,1,0,0,0,0.95,2)` | Lấy A, đặt vào ô 2                | `DONE,2`       |
| 3      | `GET,3`   | `(3,1,3,0,0,0,0.95,4)` | Lấy C, đặt vào ô 4                | `DONE,3`       |
| 4      | `GET,4`   | `(4,3,0,0,0,0,0.95,0)` | Khay hoàn tất: `n_khay_xong += 1` | `DONE,4`       |

Giữa các chu kỳ, sau mỗi `DONE` Python mới đổi sang ảnh bước kế (ảnh có thêm vật vừa đặt), rồi phân tích lại khi nhận `GET` mới. (Ở chu kỳ 3 `class = 3` là C vì ô 3 đã có B, ô 1 và 2 đã có A, chỉ còn ô 4 trống.)

**Ca B – `wrong_slot`: đủ 4 vật nhưng sai ô**

| Robot gửi | Python trả             | Ý nghĩa                                                                          |
| --------- | ---------------------- | -------------------------------------------------------------------------------- |
| `GET,1`   | `(1,2,0,0,0,0,0.95,0)` | Cần kiểm tra lại: có vật sai loại ở ô. Robot **không di chuyển**, không gửi DONE |
| `GET,2`   | `(2,2,0,0,0,0,0.95,0)` | Vẫn vậy (ảnh chưa đổi), robot dùng id mới; quá 3 lần thì dừng chờ người vận hành |

**Ca C – `unchanged_after_done`: sau DONE ảnh không đổi**

| Robot gửi | Python trả             | Ý nghĩa                                                                |
| --------- | ---------------------- | ---------------------------------------------------------------------- |
| `GET,1`   | `(1,1,1,0,0,0,0.95,1)` | Lấy A, đặt ô 1                                                         |
| `DONE,1`  | (không trả lời)        | Robot báo xong                                                         |
| `GET,2`   | `(2,2,0,0,0,0,0.95,0)` | Ảnh mới **vẫn không thấy A ở ô 1** → không công nhận, báo cần kiểm tra |

Đây là ca đề nhấn mạnh: **không được coi là đủ chỉ vì robot vừa chạy lệnh.**

**Ca D – `full`: khay đủ ngay từ đầu**

| Robot gửi | Python trả             | Ý nghĩa                                                             |
| --------- | ---------------------- | ------------------------------------------------------------------- |
| `GET,1`   | `(1,3,0,0,0,0,0.95,0)` | Khay đủ, **không cấp thêm**. Robot đếm khay một lần và gửi `DONE,1` |

### 9.8 Quy tắc bắt tay (handshake) và lý do

"Bắt tay" là cách hai bên xác nhận qua lại để không bị lặp hoặc sót việc. Mạng có thể chậm, mất gói, gửi lặp, đứt kết nối; nếu không có quy tắc thì robot có thể **gắp hai lần** hoặc **đếm hai lần**.

| Tình huống                                               | Hệ thống xử lý                                                                                                                                              | Vì sao cần                                                               |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Robot gửi **lặp `GET` cùng `id`** (do mạng hoặc gửi lại) | Python **trả y hệt dòng đã trả**, không phân tích lại ảnh                                                                                                   | Nếu phân tích lại có thể ra lệnh khác, robot làm hai việc cho một chu kỳ |
| Robot gửi **lặp `DONE` cùng `id`**                       | Python ghi log `DONE_REPEAT`, **không đổi trạng thái** lần hai, không chuyển ảnh, không đếm                                                                 | Tránh đếm lặp / bỏ qua nhiều ảnh                                         |
| Robot hỏi `id` **mới** khi lệnh trước **chưa DONE**      | Python trả `status 4` (log `REJECT_PENDING`)                                                                                                                | Không tự chạy lại / bỏ qua lệnh chưa rõ đã xong chưa                     |
| **Mất kết nối** giữa chừng                               | Python **giữ nguyên trạng thái phiên**; robot nối lại. Lệnh chưa DONE vẫn bị chặn (status 4) cho tới khi người vận hành xác nhận rồi robot gửi `RESET,<id>` | Không mất dấu lệnh đang dở                                               |
| **Không có phản hồi trong 5 s**                          | Robot coi là lỗi: `ok = False`, bật DO1, **không dùng dữ liệu cũ**                                                                                          | Tránh làm theo lệnh cũ                                                   |
| Gói trả về **sai cú pháp / thiếu số / `id` lệch**        | Robot bỏ qua gói, vào nhánh lỗi                                                                                                                             | Không gắp theo dữ liệu hỏng                                              |
| **Status 0/2/4**                                         | Robot **không gửi DONE**; chờ/chụp lại rồi dùng `id` **mới**                                                                                                | DONE chỉ dành cho việc đã thật sự làm                                    |
| Ảnh **không đổi sau DONE**                               | Python trả `status 2`                                                                                                                                       | Không coi khay đủ chỉ vì robot vừa chạy lệnh                             |

Robot lưu lại id đã hoàn thành để không gắp/đếm lại.

Còn hai trường hợp Python trả `status 4` vì cú pháp: nếu `GET` bị gửi sai (ví dụ `GET,abc`) hoặc gói lạ, Python trả `(0,4,0,0,0,0,0.00,0)`. Vì id là `0` không khớp id robot đang chờ nên robot sẽ bỏ qua (nhờ kiểm tra `rid == cid`).

### 9.9 Python đọc gói thế nào (đã làm trong `bridge.py`)

1. Python lắng nghe cổng 5000, chấp nhận kết nối của URSim.
2. Mỗi lần nhận byte (`recv`), cộng vào **bộ đệm** (`buf`).
3. Chừng nào trong bộ đệm còn ký tự `\n`: tách ra một dòng, xử lý dòng đó (`GET`/`DONE`/`RESET`), phần còn lại giữ lại cho lần sau.
4. Vì vậy dù mạng gửi nửa dòng hay hai dòng dính nhau cũng không sai.
5. Ghi log mỗi sự kiện (xem 9.13).

### 9.10 URSim đọc gói thế nào (phải làm trong chương trình .urp)

Đã kiểm chứng trên PolyScope 3.15.6:

```
okk = socket_open(ip, 5000, "py")                          # mở kết nối, tên socket "py"
socket_send_line(str_cat("GET,", to_str(cid)), "py")       # gửi "GET,<cid>" + xuống dòng
r = socket_read_ascii_float(8, "py", 5)                    # đọc 8 số, timeout 5 giây
```

- Kết quả `r` là **danh sách**: `r[0]` = **số phần tử đọc được**; `r[1]` đến `r[8]` là 8 số theo thứ tự `id, status, class, x, y, yaw, confidence, slot`.
- Ví dụ đã thử: `r = [8, 1, 1, 1, 0, 0, 0, 0.95, 1]` nghĩa là đọc được 8 số: id=1, status=1, class=1 (A), x=y=yaw=0, confidence=0.95, slot=1.
- **Chỉ đọc `r[1]…r[8]` khi `r[0] == 8`.** Nếu `r[0] != 8` (hết thời gian hoặc thiếu số), không dùng gì cả.
- Phải kiểm tra `r[1] == cid` để chắc đây là câu trả lời cho yêu cầu hiện tại.
- Gửi `DONE`: `socket_send_line(str_cat("DONE,", to_str(cid)), "py")`.
- Đóng kết nối: `socket_close("py")`.

> **Quan trọng khi viết trong PolyScope:** mọi biến dùng trong Script (`okk`, `cid`, `r`...) phải được **tạo trước bằng node Assignment** (`okk := False`). Nếu chỉ viết trong Script thì Popup/If **không thấy** biến. Trong Script chỉ gán, **không dùng chữ `global`**. Node Script ở chế độ **Line** (một dòng một node).

### 9.11 Kiểm tra bắt buộc phía robot (checklist)

- [ ] Đã đọc đủ 8 số (`r[0] == 8`), `id` khớp (`rid == cid`).
- [ ] Giá trị hữu hạn, trong miền: `status` 0–4, `class` 0–3, `slot` 0–4.
- [ ] Lệnh chỉ chạy khi `status == 1`, `conf >= 0.5`, và cặp class/slot hợp lệ.
- [ ] Hết thời gian chờ 5 s → lỗi, bật DO1, **không** dùng dữ liệu cũ.
- [ ] Lưu `id` đã hoàn thành, không gắp/đếm lại.
- [ ] Chỉ tăng bộ đếm **sau khi** đặt xong.
- [ ] `status 0/2/4`: không gửi DONE, dùng `id` mới.

### 9.12 Mạng: IP, cổng, máy ảo, firewall

- Python (server) chạy trên **Windows host**; URSim (client) chạy trong **máy ảo VMware**.
- Trong URSim, `socket_open` phải dùng **IP của Windows mà máy ảo thấy**, **không phải 127.0.0.1**.
  - VMware để **NAT**: dùng IP của adapter **VMware Network Adapter VMnet8** (`ipconfig` trên Windows), dạng `192.168.x.1` (nhóm đã thử thành công với `192.168.61.1`).
  - VMware để **Bridged**: dùng IP mạng LAN của Windows.
- IP có thể **khác nhau ở mỗi máy** của nhóm → sửa biến `ip` trong chương trình URSim cho đúng máy đang chạy bridge, ghi lại vào báo cáo chế độ mạng đã dùng.
- Nếu URSim không nối được (`okk = False`): mở **Windows Defender Firewall → Advanced settings → Inbound Rules → New Rule → Port → TCP → 5000 → Allow**.
- Cổng và IP lắng nghe của server nằm trong `config.json` (`server.host = "0.0.0.0"` = lắng nghe mọi card mạng; `server.port = 5000`).
- **Server phải chạy trước**, rồi mới chạy chương trình URSim.

### 9.13 Log CSV

Mỗi lần chạy `bridge.py` tạo `logs/session_<ngày_giờ>.csv`, một dòng cho mỗi sự kiện:

| Cột          | Ý nghĩa                                                        |
| ------------ | -------------------------------------------------------------- |
| `time`       | Thời điểm (có mili giây)                                       |
| `event`      | Loại sự kiện (bảng dưới)                                       |
| `id`         | Mã chu kỳ                                                      |
| `source`     | Nguồn ảnh/khung (tên ảnh hoặc `kịch_bản#step`)                 |
| `prediction` | Trạng thái 4 ô theo AI (`empty/ok/wrong_type/extra/unknown`)   |
| `command`    | Dòng gói tin đã trả cho robot                                  |
| `detail`     | Lý do (ví dụ `slot2_wrong_type`, `placed_slot1_not_confirmed`) |

| `event`                  | Nghĩa                                         |
| ------------------------ | --------------------------------------------- |
| `CONNECT` / `DISCONNECT` | Robot nối vào / ngắt                          |
| `GET`                    | Yêu cầu mới, Python phân tích ảnh và trả lệnh |
| `GET_REPEAT`             | `GET` lặp cùng id, trả lại dòng cũ            |
| `DONE`                   | Robot báo xong lần đầu, đã ghi nhận           |
| `DONE_REPEAT`            | `DONE` lặp, bỏ qua                            |
| `DONE_REJECT`            | `DONE` không khớp lệnh đang chờ               |
| `REJECT_PENDING`         | Từ chối yêu cầu mới vì lệnh trước chưa `DONE` |
| `RESET`                  | Robot xin xóa lệnh đang chờ                   |
| `BAD_PACKET`             | Gói sai cú pháp                               |
| `CONN_ERROR`             | Lỗi kết nối                                   |

Chọn những file log tiêu biểu, copy sang `docs/` (vì `.gitignore` đang bỏ `logs/*.csv`) để làm bằng chứng cho báo cáo.

### 9.14 Thử gói tin: thử số trước, nối AI sau

Đề yêu cầu **thử gói số trước, sau đó mới nối AI**. Số do bridge sinh ở chế độ `--mode script` hoặc bằng `tests/fake_robot.py` chỉ dùng để thử giao tiếp, **không thay phần AI khi nghiệm thu**. Khi nghiệm thu lệnh phải sinh ra từ ảnh thật qua YOLO.

---

## 10. Logic kiểm tra khay và file config.json

### 10.1 Đầu vào của `check_tray.py`

Một danh sách các vật mà AI phát hiện, mỗi vật dạng:

```
{"cls": "A", "box": [x1, y1, x2, y2], "conf": 0.93}
```

(`box` là tọa độ pixel: góc trên trái và góc dưới phải; `conf` là độ tin cậy.)

### 10.2 Các bước xử lý

1. **Lọc theo confidence:**
   - `conf >= conf_min` → **chấp nhận**.
   - `conf_low <= conf < conf_min` → **không chắc chắn**: nếu tâm hộp nằm trong một ô thì ô đó thành `unknown` (không rõ, ví dụ vật bị che).
   - `conf < conf_low` → bỏ qua hoàn toàn.
2. **Loại hộp trùng:** hai hộp chồng lấn nhiều (`IoU ≥ nms_iou`) coi là cùng một vật, giữ hộp confidence cao hơn.
3. **Gán vật vào ô:** lấy **tâm** của mỗi hộp.
   - Tâm nằm trong đúng một ô → vật thuộc ô đó.
   - Tâm nằm **sát ranh giới hai ô** (trong khoảng `boundary_margin_px` pixel) → đánh dấu **nằm giữa hai ô**.
   - Tâm nằm ngoài mọi ô → **vật ngoài ô** (dư).
4. **Trạng thái từng ô:**

| Trạng thái   | Điều kiện                                                      |
| ------------ | -------------------------------------------------------------- |
| `empty`      | Ô không có vật                                                 |
| `ok`         | Đúng một vật, đúng loại mà ô cần (A ở ô 1/2, B ở ô 3, C ở ô 4) |
| `wrong_type` | Đúng một vật nhưng sai loại                                    |
| `extra`      | Hai vật trở lên trong cùng ô                                   |
| `unknown`    | Có vật confidence thấp / bị che trong ô                        |

5. **Kết luận cho cả khay:**
   - Có bất kỳ điều sau → **`status 2`** (ngoại lệ, không cấp phôi): có ô `unknown`/`extra`/`wrong_type`, có vật **nằm giữa hai ô**, có vật **ngoài ô**, có vật confidence thấp, hoặc **ô vừa đặt xong chưa được ảnh mới xác nhận `ok`**.
   - Không có vấn đề và cả 4 ô `ok` → **`status 3`** (khay hoàn tất).
   - Không có vấn đề, còn ô `empty` → lấy ô trống **đầu tiên theo thứ tự A1→A2→B1→C1**, sinh lệnh `status 1` với class tương ứng (ô 1, 2 → A; ô 3 → B; ô 4 → C).
6. **Kiểm tra sau đặt:** sau khi robot `DONE` lệnh `(class, slot)`, ảnh kế tiếp **phải cho thấy ô `slot` ở trạng thái `ok`**, nếu không → `status 2` (đây chính là ca "ảnh không đổi sau DONE / bị che").

Ví dụ: khay chỉ có B ở ô 3.

- Ô 1 `empty`, ô 2 `empty`, ô 3 `ok`, ô 4 `empty`.
- Ô trống đầu tiên là ô 1 → lệnh **A → ô 1**.
- Sau khi đặt, ảnh mới có A ở ô 1 → lệnh tiếp là **A → ô 2**, rồi **C → ô 4**, rồi `status 3`.

### 10.3 Ý nghĩa từng mục trong `config.json`

| Mục                             | Ý nghĩa                                                                                   |
| ------------------------------- | ----------------------------------------------------------------------------------------- |
| `server.host`                   | `0.0.0.0` = lắng nghe trên mọi card mạng                                                  |
| `server.port`                   | Cổng 5000                                                                                 |
| `server.robot_timeout_s`        | 5 s. (Hiện chỉ robot giả dùng; URSim tự đặt timeout trong lệnh `socket_read_ascii_float`) |
| `image.width/height`            | Kích thước ảnh mà bốn ô được vẽ theo (ghi nhắc; code chưa dùng)                           |
| `tray.slots`                    | 4 hình chữ nhật ô `[x1,y1,x2,y2]` **tính theo pixel ảnh**. **Phải đo lại theo ảnh thật**  |
| `tray.names`                    | Tên ô: 1=A1, 2=A2, 3=B1, 4=C1                                                             |
| `tray.expected`                 | Loại cần có ở mỗi ô: 1:A, 2:A, 3:B, 4:C                                                   |
| `tray.allowed`                  | Ô được phép của mỗi loại: A→[1,2], B→[3], C→[4]                                           |
| `tray.order`                    | Thứ tự bổ sung: [1,2,3,4] = A1→A2→B1→C1                                                   |
| `thresholds.conf_low`           | Dưới mức này bỏ qua (0.25)                                                                |
| `thresholds.conf_min`           | Từ mức này mới chấp nhận (0.50). **Chọn bằng tập val rồi khóa**                           |
| `thresholds.nms_iou`            | Ngưỡng coi hai hộp là trùng (0.50)                                                        |
| `thresholds.boundary_margin_px` | Bề rộng vùng sát ranh giới hai ô (15 pixel)                                               |
| `model.weights`                 | Đường dẫn trọng số YOLO (`weights/best.pt`)                                               |
| `model.imgsz`                   | Kích thước ảnh đưa vào mô hình (640)                                                      |
| `log_dir`                       | Thư mục ghi log (`logs`)                                                                  |

> Bốn hình chữ nhật trong `tray.slots` hiện là **số mẫu** cho ảnh 640×480. Khi có ảnh thật, mở một ảnh, đọc tọa độ pixel của bốn ô và điền lại, nếu không mọi vật sẽ bị gán sai ô.

---

## 11. Phần AI: dữ liệu, huấn luyện, đánh giá, tích hợp

Làm theo thứ tự 11.1 → 11.9.

### 11.1 Dựng cảnh chụp (P2, khoảng 1 giờ)

- **Khay**: tờ bìa hoặc hộp giấy, kẻ 4 ô (2×2), ghi A1, A2, B1, C1 (ô 1, 2, 3, 4). Dán cố định xuống bàn.
- **Ba loại linh kiện A, B, C**: chọn vật **cực dễ phân biệt** (khác màu và hình, ví dụ nắp chai đỏ, đồng xu, khối giấy xanh). Vật đơn giản thì ghi hạn chế đại diện của dữ liệu vào báo cáo.
- **Camera**: điện thoại gác cố định (giá, chồng sách), nhìn thẳng xuống khay. **Không đổi góc và độ cao** trong suốt lúc chụp, vì bốn ô trên ảnh là cố định.
- Tắt chế độ tự làm đẹp / HDR / zoom. Khóa lấy nét nếu được. Chụp cùng độ phân giải cho mọi ảnh.

### 11.2 Chụp dữ liệu (cả nhóm, một buổi)

Đề yêu cầu **tối thiểu 300 ảnh khay**. Nên chụp **khoảng 330** để dư. Phân bố đề xuất:

| Tình huống                | Mục tiêu (ảnh) | Ví dụ                                    |
| ------------------------- | -------------- | ---------------------------------------- |
| Đủ bộ (A, A, B, C đúng ô) | 80             | A ở ô 1 và 2, B ở ô 3, C ở ô 4           |
| Thiếu một hoặc nhiều vật  | 90             | chỉ có B; thiếu C; thiếu một trong hai A |
| Sai ô                     | 60             | B ở ô 1; đủ 4 vật nhưng đảo ô            |
| Dư vật                    | 60             | 5 vật; 2 vật trong cùng một ô            |
| Che khuất                 | 40             | tay hoặc giấy che một phần               |

Quy tắc chụp để chia tập đúng:

- Mỗi **bố trí khay** (một cách xếp vật) có một mã `L001`, `L002`, ... Chụp **mỗi bố trí 3 ảnh** (đổi nhẹ ánh sáng/bóng, **không** đổi góc camera). Cần khoảng **110 bố trí khác nhau**.
- Đặt tên ảnh: `L{mã_bố_trí}_{số}.jpg`, ví dụ `L012_1.jpg`, `L012_2.jpg`, `L012_3.jpg`.
- Đa dạng: đổi vị trí vật trong ô, xoay vật, bật/tắt đèn, ánh sáng gần/xa cửa sổ, đổi người chụp. Chia đều giữa ba người để có nhiều phiên chụp.
- **Mọi ảnh cùng một mã bố trí phải nằm cùng một tập** khi chia (11.4).

Ghi **`data/metadata.csv`** ngay khi chụp (không để sau):

```
filename,layout_id,session,photographer,condition,A1,A2,B1,C1,note
L012_1.jpg,L012,S02,Nguoi2,thieu,-,-,B,-,chi co B
L013_1.jpg,L013,S02,Nguoi2,sai_o,B,A,A,C,B o A1
L014_1.jpg,L014,S03,Nguoi3,du_vat,A+A,A,B,C,2 vat o A1
```

- Cột `A1,A2,B1,C1` là **trạng thái thật** của từng ô: `-` (trống), `A`/`B`/`C`, hoặc `A+B` (nhiều vật). Ghi theo **thực tế vật lý** (kể cả khi bị che).
- `condition`: `du`, `thieu`, `sai_o`, `du_vat`, `che`.

### 11.3 Gán nhãn (P2, khoảng nửa ngày)

Công cụ (chọn một): **Roboflow** (web; bản miễn phí thường để dữ liệu công khai, nếu ngại dùng công cụ khác), **CVAT**, hoặc **LabelImg** (chạy trên máy). Mỗi vật vẽ **một hộp** quanh nó và chọn lớp `A`, `B` hoặc `C`.

- **Tên lớp phải đúng `A`, `B`, `C`.** Thứ tự id trong YOLO: `0 = A`, `1 = B`, `2 = C`. (Code `check_tray.py` so sánh theo tên.)
- Vẽ hộp sát vật, kể cả vật ở sai ô và vật dư. Vật bị che một phần: vẽ phần nhìn thấy. Vật bị che hoàn toàn: không vẽ (nhưng `metadata.csv` vẫn ghi trạng thái thật).
- **Xuất định dạng YOLOv8 (YOLO).** Nếu dùng Roboflow, **không** để nó tự chia tập ngẫu nhiên; xuất toàn bộ rồi tự chia (11.4).
- Mẹo tiết kiệm thời gian: gán tay khoảng 50 ảnh, huấn luyện thử (11.5), rồi dùng mô hình đó dự đoán sẵn hộp cho các ảnh còn lại và chỉ sửa lại.
- Kiểm tra lại ngẫu nhiên khoảng 10% ảnh sau khi gán: nhãn sai làm hỏng huấn luyện.

Định dạng nhãn YOLO: mỗi ảnh có một file `.txt` cùng tên, mỗi dòng một vật `class_id cx cy w h` (tâm và kích thước hộp, **chuẩn hóa về 0–1**). Ví dụ `1 0.25 0.75 0.12 0.15` = một vật lớp B, tâm ở 25% chiều rộng, 75% chiều cao.

### 11.4 Chia tập train/val/test theo bố trí (P2)

Quy tắc đề: chia **60/20/20% theo khay/phiên bố trí**; ảnh gần giống và ảnh tăng cường của cùng ảnh gốc ở **cùng tập**; ảnh tăng cường chỉ từ train.

1. Lấy danh sách mã bố trí (`layout_id`) từ `metadata.csv`.
2. Xáo ngẫu nhiên với seed cố định (ví dụ `42`), chia 60/20/20 **theo bố trí**. Nên chia riêng trong từng `condition` rồi gộp lại để cả ba tập đều có đủ các tình huống.
3. Tất cả ảnh của một bố trí đi cùng một tập.
4. Ghi **`data/splits.csv`** (cột `filename,layout_id,split`). Đề yêu cầu nộp danh sách chia tập.
5. Tạo cấu trúc YOLO:

```
data/yolo/
  images/train  images/val  images/test
  labels/train  labels/val  labels/test
```

6. **Tập test phải có ít nhất 60 ảnh** và đủ các tình huống (330 ảnh chia 20% ≈ 66 ảnh).
7. Ghi vào báo cáo: số ảnh, số bố trí, số hộp từng lớp ở mỗi tập.

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

(Chạy lệnh Ultralytics từ **thư mục gốc repo**. Nếu báo không tìm thấy dataset, đổi `path` thành đường dẫn tuyệt đối.)

> Script `split_dataset.py` chưa có, xem mục 18.

### 11.5 Huấn luyện YOLO (P3)

```
python -m pip install ultralytics
yolo detect train data=data/data.yaml model=yolov8n.pt imgsz=640 epochs=60 batch=16 seed=42 name=baseline
```

- `model=yolov8n.pt`: bắt đầu từ mô hình có sẵn (tinh chỉnh). `imgsz=640`: ảnh đưa vào cỡ 640 pixel. `epochs=60`: học 60 lượt qua toàn bộ tập train. `batch=16`: mỗi lần học 16 ảnh.
- **Có thể dùng Google Colab** (thường có GPU T4 miễn phí): tải thư mục `data/` lên (nén zip), `pip install ultralytics`, chạy lệnh trên, rồi tải `runs/detect/baseline/weights/best.pt` về, đặt vào `weights/best.pt` của repo.
- Kết quả nằm trong `runs/detect/baseline/`: có `weights/best.pt` (mô hình tốt nhất trên val), đồ thị loss/mAP, confusion matrix.
- Augmentation mặc định của Ultralytics chỉ áp dụng lúc huấn luyện trên train (đúng yêu cầu), val/test không bị biến đổi.
- Ghi vào báo cáo: kiến trúc (YOLOv8n), trọng số khởi tạo (`yolov8n.pt`, học sẵn trên COCO), kích thước ảnh, epochs, batch, seed, thiết bị, phiên bản `ultralytics`/`torch`, thời gian huấn luyện.
- Nếu kết quả kém: kiểm tra lại nhãn, thêm ảnh ở các tình huống mô hình hay sai, tăng epochs, hoặc đổi `yolov8s.pt`. Mỗi lần thử **chỉ đổi một thứ** và ghi lại.

Chọn mô hình bằng **tập val** (không dùng test). Đã chọn rồi thì **không huấn luyện lại sau khi nhìn kết quả test**.

### 11.6 Chọn và khóa ngưỡng (P3)

Các ngưỡng nằm trong `config.json → thresholds` (mục 10.3).

1. Chạy suy luận trên **tập val** với nhiều giá trị `conf_min` (ví dụ 0.30, 0.35, ..., 0.80).
2. Với mỗi giá trị tính: tỷ lệ nhận định đúng trạng thái khay (đủ/thiếu/sai) và **số khay thiếu/sai bị nhận nhầm là đủ**.
3. Ưu tiên **không để khay thiếu/sai bị nhận là đủ** (lỗi nghiêm trọng nhất của bài), sau đó mới tối đa độ đúng.
4. Chọn ngưỡng, ghi vào `config.json`, **commit**, từ đó **không đổi**.
5. Lập bảng ảnh hưởng của ngưỡng (đưa vào báo cáo).

`boundary_margin_px` và bốn hình chữ nhật ô cũng chọn trên val/quan sát ảnh, không chỉnh theo test.

### 11.7 Đánh giá trên tập test (P3)

Chạy **một lần** sau khi đã khóa mô hình và ngưỡng. Báo cáo:

1. **Chỉ số phát hiện**: mAP50, mAP50-95, precision/recall từng lớp (A, B, C):
   ```
   yolo detect val model=weights/best.pt data=data/data.yaml split=test
   ```
2. **Chỉ số cấp khay** (chỉ số chính của đề): chạy `check_tray` trên từng ảnh test, so với trạng thái thật trong `metadata.csv`.
   - Ánh xạ kết quả hệ thống: `status 3` ↔ "đủ"; `status 1` ↔ "thiếu"; `status 2` ↔ "sai / không rõ".
   - **Độ đúng cấp khay** = số ảnh nhận định đúng / tổng ảnh test. Mục tiêu của đề: **≥ 90% trên ít nhất 60 ảnh test**.
   - **Số khay thiếu/sai bị nhận nhầm là đủ**: báo cáo riêng, cả số tuyệt đối và tỷ lệ.
   - **Tỷ lệ từ chối** (`status 2`): báo cáo riêng; liệt kê ảnh đủ nhưng bị từ chối nhầm.
   - **Confusion matrix** ba trạng thái (đủ / thiếu / sai).
3. **Phân tích ca sai**: lưu ảnh sai vào thư mục (ví dụ `logs/test_errors/`), nêu nguyên nhân (che khuất, bóng, vật gần ranh giới ô, hộp lệch...).
4. **Tách bạch**: độ đúng của **mô hình/AI so với nhãn thật** khác độ đúng của **robot thực hiện lệnh đã nhận**. Báo riêng hai phần.
5. Nếu chưa đạt 90% thì **ghi đúng số đo được** và phân tích nguyên nhân.

> Script `evaluate.py` chưa có, xem mục 18.

### 11.8 Chuỗi ảnh trước–sau (P2 chụp, P3 dùng)

Đề yêu cầu **tối thiểu 10 chuỗi ảnh trước–sau**, quản lý theo kịch bản: **chỉ đổi sang ảnh bước kế sau khi robot gửi `DONE`**. Đây là "cảnh thử được quản lý theo kịch bản": phải nói rõ như vậy trong báo cáo vì URSim không tạo hay thay đổi ảnh sau thao tác gắp.

- Mỗi chuỗi một thư mục: `data/demo_seq/S01/`, `S02/`, ... Ảnh trong chuỗi đặt tên `step0.jpg`, `step1.jpg`, `step2.jpg`, ... (bridge sắp xếp theo tên).
- Ảnh chuỗi **không** nằm trong train/val/test. Chụp riêng bằng cùng camera cố định.
- Chuỗi mẫu `S01` (ca bắt buộc "chỉ có B ở ô 3"):
  - `step0`: chỉ B ở ô 3
  - `step1`: B ở ô 3 + A ở ô 1
  - `step2`: thêm A ở ô 2
  - `step3`: đủ bộ (thêm C ở ô 4)
- Các chuỗi còn lại phủ các ca bổ sung: thiếu A, thiếu C, thiếu hai A, khay đủ ngay (chuỗi một ảnh), sai ô (một ảnh), ảnh không đổi sau DONE (hai ảnh giống nhau), bị che (một ảnh)...
- Ghi `data/demo_seq/README.md`: mỗi chuỗi là ca gì, lệnh dự kiến.

### 11.9 Tích hợp AI vào bridge (P3, sau khi có `best.pt`)

1. Đặt `weights/best.pt`; sửa `config.json → model.weights` nếu đổi tên.
2. **Kiểm tra `tray.slots`** khớp **đúng độ phân giải và góc camera** thật: mở một ảnh, đọc tọa độ pixel bốn ô, điền lại dạng `[x1, y1, x2, y2]`. Đây là việc dễ sai nhất khi chuyển từ hộp giả sang ảnh thật.
3. Thử suy luận một ảnh để chắc `infer.py` chạy (in số vật và thời gian ms).
4. Chạy bridge với một chuỗi ảnh:
   ```
   python bridge.py --mode ai --images data/demo_seq/S01
   ```
   Robot (hoặc `tests/fake_robot.py`) sẽ nhận lệnh theo ảnh thật. Ảnh chỉ chuyển sang `step` kế sau khi nhận `DONE`.
5. Mỗi lần chạy một chuỗi, **khởi động lại bridge** (Ctrl+C rồi chạy lại) để xóa trạng thái phiên.
6. Ghi **thời gian suy luận** (`infer.py` in ra ms) **riêng** với thời gian chu kỳ mô phỏng URSim; đề yêu cầu tách hai số này.
7. Khi nghiệm thu **không dùng gói gõ tay** thay phần AI: video phải cho thấy lệnh sinh ra từ ảnh.

---

## 12. Phần URSim: TCP, Waypoint, SubProgram, vòng lặp chính

Môi trường: PolyScope 3.15.6. Menu cài đặt TCP là **Installation → TCP Configuration** (không phải "General → TCP"). Tên nút/tab có thể hơi khác một chút giữa các bản; chỗ nào lệch thì chụp màn hình hỏi nhau. Phần lớn mục này là hướng dẫn, riêng 12.1 đã chạy được trên URSim của nhóm.

### 12.1 Việc đã kiểm chứng

Chương trình thử nối socket đã chạy đúng:

```
okk := False                                        (Assignment)
Script:  okk = socket_open("192.168.61.1", 5000, "py")
Popup:   okk                                        -> True
cid := 0                                            (Assignment)
r := [0,0,0,0,0,0,0,0,0]                            (Assignment)
cid := cid + 1                                      (Assignment)
Script:  socket_send_line(str_cat("GET,", to_str(cid)), "py")
Script:  r = socket_read_ascii_float(8, "py", 5)
Popup:   r                                          -> [8, 1, 1, 1, 0, 0, 0, 0.95, 1]
Script:  socket_close("py")
```

Đã xác nhận trên bản này: `socket_read_ascii_float` có tham số timeout, và `str_cat`, `to_str`, `socket_send_line` dùng được.

### 12.2 Đặt TCP và lưu Installation (làm TRƯỚC khi dạy Waypoint)

1. **Installation → TCP Configuration**. Bấm **New**.
2. Bấm **Rename**, đặt tên `Kep`.
3. Ô **Z** nhập `100` (mm). **X, Y = 0**; **RX, RY, RZ = 0**.
4. Bấm **Set as default** (dấu tích xanh chuyển sang `Kep`). Payload để nguyên.
5. Menu bên trái chọn **Load/Save** → lưu installation tên `nhom2`. Chuyển file `.installation` vào `ursim/` của repo (nếu không thấy file khi kéo thả, tìm trong thư mục **Programs UR3** hoặc báo cả nhóm).

> Đặt TCP trước khi dạy điểm. Đổi TCP sau sẽ làm các điểm đã dạy bị lệch.

Ghi vào báo cáo: phiên bản URSim, TCP đã đặt (`Kep`, Z = 100 mm), hệ tọa độ dùng (Base), cách chọn vị trí.

### 12.3 Bố trí và dạy Waypoint

Bố trí gợi ý (tự chọn trong vùng với tới của UR3, tầm với khoảng 500 mm):

- Khay 2×2 đặt trước robot, cách gốc khoảng 250–300 mm, các ô cách nhau khoảng 60 mm.
- Ba vị trí cấp A, B, C xếp hàng bên cạnh khay.
- Tư thế đầu kẹp hướng xuống bàn, **giữ nguyên hướng** ở mọi điểm (chỉ tịnh tiến) để tránh lỗi "không với tới".

Dạy một Waypoint:

1. Tab **Program** → chọn vị trí trong cây → tab **Structure** → **Basic → Move** (tạo node `MoveJ` kèm một Waypoint bên trong).
2. Chọn Waypoint, bấm **Set this waypoint**. Giao diện chuyển sang màn hình di chuyển (giống tab **Move**): dùng các nút tịnh tiến/xoay hoặc nhập giá trị khớp để đưa robot tới vị trí cần dạy, rồi bấm **OK**.
3. Đổi tên điểm ở ô tên phía trên.
4. Giảm **Speed** (30–50%) khi thử, quan sát khung 3D.

Cần dạy **8 điểm cố định**, mỗi điểm nằm trong một `MoveJ`:
`Home`, `Cap_A_Approach`, `Cap_B_Approach`, `Cap_C_Approach`, `O1_Approach`, `O2_Approach`, `O3_Approach`, `O4_Approach`. Điểm tiếp cận cao hơn mặt bàn khoảng 100 mm.

Đoạn hạ/nâng dùng `MoveL`. Dùng Waypoint dạng **Relative position** (đổi kiểu trong node Waypoint) với Z = −0,1 m (hạ) và +0,1 m (nâng). Nếu bản của nhóm khác, có thể dùng cặp điểm cố định "tiếp cận" và "chạm". _(Chưa kiểm chứng trên URSim của nhóm: thử rồi ghi lại cách đã dùng.)_

### 12.4 SubProgram

Tạo 4 SubProgram (**Structure → Advanced → SubProgram**, đặt tên rồi sửa cây con):

- `Lay_A`, `Lay_B`, `Lay_C`:
  ```
  MoveJ  Cap_X_Approach
  MoveL  Relative Z = -0.1       (hạ)
  Set DO0 = On                   (đóng kẹp)
  Wait 0.5 s
  MoveL  Relative Z = +0.1       (nâng)
  ```
- `Dat_VaoO` (dùng biến `slot`):
  ```
  If slot == 1: MoveJ O1_Approach ; MoveL Relative Z -0.1 ; Set DO0 = Off ; Wait 0.5 ; MoveL Relative Z +0.1
  ElseIf slot == 2: (tương tự O2)
  ElseIf slot == 3: (tương tự O3)
  ElseIf slot == 4: (tương tự O4)
  ```

Chạy thử **từng SubProgram một mình** (node Call), tốc độ thấp: xem đèn DO0 ở tab **I/O**, kiểm tra hạ thẳng, không báo lỗi với tới. Cách nhanh: Copy/Paste `Lay_A` rồi đổi tên và điểm tiếp cận.

### 12.5 Biến chương trình

Tạo bằng **Assignment** ở đầu chương trình:

| Biến                | Giá trị đầu                     | Ý nghĩa                         |
| ------------------- | ------------------------------- | ------------------------------- |
| `ip`                | `"192.168.61.1"` (sửa theo máy) | IP máy chạy Python              |
| `cid`               | 0                               | mã chu kỳ, tăng mỗi `GET` mới   |
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

### 12.6 Vòng lặp chính

Thiết kế dưới đây là bản nhóm đề xuất (**chưa dựng chạy thử trên URSim**), phần socket đã kiểm chứng ở 12.1. Dựng từng đoạn và thử từng đoạn.

```
Script: okk = socket_open(ip, 5000, "py")      (mở kết nối một lần; kiểm tra okk)
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
     Script: socket_close("py") ; Wait 1 ; Script: okk = socket_open(ip, 5000, "py")   (mở lại, có giới hạn số lần)
  ElseIf st == 1 and conf >= 0.5 and ((cls==1 and (slot==1 or slot==2)) or (cls==2 and slot==3) or (cls==3 and slot==4))
     Set DO1 = Off ; retries := 0
     If cls == 1: Call Lay_A / ElseIf cls == 2: Call Lay_B / ElseIf cls == 3: Call Lay_C
     Call Dat_VaoO
     Script:  socket_send_line(str_cat("DONE,", to_str(cid)), "py")
     n_dat := n_dat + 1                  (chỉ tăng SAU khi đặt xong)
     Set DO2 = On ; Wait 0.2 ; Set DO2 = Off      (xung hoàn tất một lần đặt)
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

Chú ý:

- Biểu thức nhiều điều kiện dùng `and`/`or` và ngoặc trong ô expression của If.
- **Chỉ đọc `r[1]…r[8]` khi `r[0] == 8`**: đã tách thành If lồng nhau ở trên để không lỗi chỉ số.
- **Không dùng DO2 làm bộ đếm khay**: khay hoàn tất do biến `n_khay_xong`, xung DO2 chỉ báo mỗi lần đặt.
- Gặp `status 4` do "lệnh chưa DONE" (sau mất kết nối): người vận hành kiểm tra rồi robot gửi `RESET,<cid>`; bridge trả `status 0` và xóa lệnh đang chờ.
- Chạy chậm khi quan sát, kiểm tra Waypoint trước khi bấm Play. Dùng Popup hoặc Wait trước khi dừng để chụp bộ đếm.
- Lưu chương trình thường xuyên (File → Save), chuyển `.urp` ra thư mục `ursim/` của repo và commit (chỉ P1).

### 12.7 Bảng I/O (nộp kèm)

| Tín hiệu    | Ý nghĩa                                 |
| ----------- | --------------------------------------- |
| DO0         | On = đóng kẹp; Off = mở kẹp             |
| DO1         | Lỗi chương trình / quy trình / kết nối  |
| DO2         | Xung hoàn tất một lần đặt               |
| DO3 trở lên | Chưa dùng (nếu dùng thì lập bảng riêng) |

### 12.8 Bảng Waypoint (điền sau khi dạy)

`Home` | `Cap_A_Approach` | `Cap_B_Approach` | `Cap_C_Approach` | `O1_Approach` | `O2_Approach` | `O3_Approach` | `O4_Approach` — mỗi điểm ghi tọa độ (x, y, z) và kiểu Move (MoveJ/MoveL).

---

## 13. Ghép hệ thống và kiểm thử

**Trước mỗi ca: Ctrl+C rồi chạy lại `bridge.py`** (bridge nhớ lệnh chưa DONE; không khởi động lại thì có thể trả `status 4`).

### 13.1 Giai đoạn 1 – với kịch bản hộp giả (chưa cần model)

| Ca                       | Lệnh bridge                       | Kết quả dự kiến                                |
| ------------------------ | --------------------------------- | ---------------------------------------------- |
| Ban đầu chỉ có B ở ô 3   | `--mode script --scenario only_B` | A→1, A→2, C→4, rồi status 3, `n_khay_xong = 1` |
| Khay đủ ngay từ đầu      | `--scenario full`                 | Không cấp thêm, `n_khay_xong = 1` đúng một lần |
| Đủ số lượng nhưng sai ô  | `--scenario wrong_slot`           | status 2, không gắp, `n_cho` tăng              |
| Ảnh không đổi sau DONE   | `--scenario unchanged_after_done` | A→1 rồi status 2, không coi là đủ              |
| Bị che / confidence thấp | `--scenario occluded`             | status 2                                       |
| Vật nằm giữa hai ô       | `--scenario between_slots`        | status 2                                       |

### 13.2 Giai đoạn 2 – với ảnh thật và model

Chạy lại các ca trên bằng chuỗi ảnh thật: `--mode ai --images data/demo_seq/Sxx`. Video và log phải có đủ: **khay thiếu hai A và một C**, **khay đủ**, **khay sai ô**.

### 13.3 Ít nhất hai ca bất thường (nhóm tự chọn, đề bắt buộc)

Gợi ý:

- **Tắt `bridge.py` giữa chu kỳ** (mất kết nối): robot vào nhánh lỗi, DO1 bật, không dùng dữ liệu cũ; bật lại bridge, xử lý `RESET` rồi tiếp tục an toàn.
- **Sửa IP sai** trong `ip`: `socket_open` thất bại → nhánh lỗi.
- **Gửi lặp `GET`/`DONE`** (`tests/fake_robot.py --dup-get --dup-done`): không đếm lặp.
- **Gói trả sai cú pháp / thiếu trường**: robot không gắp.
- **Ảnh bị che bằng tay** giữa chuỗi.
- **Đổi ánh sáng mạnh** khiến confidence thấp.

### 13.4 Ghi kết quả (quan trọng)

Với **mỗi ca** ghi ba cột **riêng**: **kết quả dự kiến** (viết trước khi chạy), **kết quả quan sát** (sau khi chạy), **đạt / chưa đạt**. Lưu kèm: ảnh cây chương trình, ảnh bộ đếm, file log CSV (copy sang `docs/`).

---

## 14. Bảng ca thử mẫu

Điền vào báo cáo. Với nhóm AI, thêm vào bảng hoặc log CSV: mã ảnh, nhãn thật, confidence, gói tin, trạng thái DONE.

| Ca  | Đầu vào                            | Kết quả dự kiến                                                    | Kết quả quan sát | Đạt |
| --- | ---------------------------------- | ------------------------------------------------------------------ | ---------------- | --- |
| T1  | Ban đầu chỉ có B ở ô 3             | A→1, A→2, C→4, sau mỗi lần có ảnh mới kiểm tra, cuối cùng status 3 |                  |     |
| T2  | Khay đủ ngay từ đầu                | Không phát lệnh bổ sung; đếm khay hoàn tất một lần                 |                  |     |
| T3  | Đủ số lượng nhưng sai ô            | Phát hiện sai, nhánh ngoại lệ, không gắp                           |                  |     |
| T4  | Ảnh không đổi sau DONE hoặc bị che | Không coi đủ chỉ vì lệnh vừa chạy; chờ kiểm tra/ngoại lệ           |                  |     |
| T5  | (ca bất thường 1 của nhóm)         |                                                                    |                  |     |
| T6  | (ca bất thường 2 của nhóm)         |                                                                    |                  |     |

---

## 15. Báo cáo, video, hồ sơ nộp

### 15.1 Yêu cầu của đề cho đề AI

- **Báo cáo 12–20 trang.** Nội dung: đầu bài; bố trí và thông số; bảng I/O/biến; thuật toán; cây chương trình; **dữ liệu, mô hình, giao thức, sai số**; kết quả kiểm thử; nhận xét; kết luận; tài liệu tham khảo.
- **Video 5–7 phút**: hiện **ảnh AI (có hộp), gói tin và chuyển động robot**; có ca bình thường và ít nhất một ca bất thường.
- **Nộp**: `.urp`, `.installation` và tệp liên quan; báo cáo; video; bảng ca thử, đánh giá AI, log CSV, hiệu chuẩn nếu có; mã Python, `requirements.txt`, config mẫu, README, trọng số, danh sách chia tập. **Không** nộp `.venv`. Không chỉ nộp ảnh cây chương trình / video mà thiếu tệp chương trình.
- Ghi nhóm, đề gốc, thành viên, mã sinh viên và **phần việc từng người** trên báo cáo.
- Video yêu cầu của đề cho nhóm này: ít nhất một khay thiếu hai A và một C, một khay đã đủ, một khay sai ô.

### 15.2 Thang điểm đề AI (để biết ưu tiên)

| Nội dung                                       | Điểm |
| ---------------------------------------------- | ---- |
| Dữ liệu, chia tập, gán nhãn, khả năng chạy lại | 2    |
| Huấn luyện AI, đánh giá, phân tích sai số      | 2,5  |
| URSim, Waypoint, If, SubProgram                | 2    |
| TCP, bắt tay, kiểm thử, nhánh lỗi              | 2    |
| Báo cáo, video, giải thích, trình diễn         | 1,5  |

### 15.3 Điều cần ghi rõ trong báo cáo

- Phiên bản phần mềm (URSim 3.15.6.106324, Python, ultralytics, torch).
- **URSim chỉ kiểm chứng lệnh/chuyển động mô phỏng**, không kiểm chứng va chạm hay lực giữ phôi. Camera/ảnh chạy riêng trong Python.
- **Chuỗi ảnh trước–sau là cảnh quản lý theo kịch bản**, không phải ảnh sinh ra từ robot.
- Tách **độ đúng của AI** khỏi **độ đúng robot thực hiện lệnh đã nhận**.
- Báo cáo **số mẫu, số ca sai** (không chỉ phần trăm), tỷ lệ từ chối, và riêng số khay thiếu/sai bị nhận nhầm là đủ.
- Nguồn dữ liệu, cách tự tạo ảnh và giới hạn đại diện (vật đơn giản, một bối cảnh).
- Bộ test **không dùng** để chọn mô hình/ngưỡng.
- Các mục tiêu định lượng của đề (≥ 90% trên ≥ 60 ảnh test...) là **tiêu chí đối chiếu**: báo cáo số đo được thật, kể cả khi chưa đạt.
- Cách xử lý: thiếu phôi, khay sai/không rõ, gói tin sai, quá thời gian, mất kết nối, kèm **điều kiện phục hồi cụ thể**.
- Giải thích phần kiểm chứng bằng mô phỏng và phần cần thiết bị thật.

### 15.4 Checklist nộp

- [ ] `ursim/nhom2_main.urp`, `ursim/nhom2.installation`
- [ ] Bảng Waypoint, bảng I/O, bảng biến, sơ đồ trạm, ảnh cây chương trình
- [ ] `bridge.py`, `check_tray.py`, `infer.py`, `train.py`, `evaluate.py`, `config.json`, `requirements.txt`, `README.md`
- [ ] `weights/best.pt`
- [ ] `data/` (hoặc link Drive đã thống nhất) + `data/metadata.csv` + `data/splits.csv`
- [ ] Log CSV các ca thử (copy vào `docs/`)
- [ ] Bảng ca thử đầy đủ (dự kiến / quan sát / đạt)
- [ ] Báo cáo 12–20 trang
- [ ] Video 5–7 phút (ca bình thường + bất thường, hiện ảnh AI, gói tin, chuyển động)
- [ ] Không có `.venv` trong hồ sơ

---

## 16. Câu hỏi vấn đáp mẫu

Mỗi sinh viên phải giải thích được phần mình. Cả ba người nên trả lời được:

1. **Mô tả một chu kỳ** từ lúc robot hỏi tới lúc báo xong. _(GET → Python phân tích ảnh → trả lệnh 8 số → robot gắp/đặt → DONE → ảnh mới.)_
2. **Vì sao có `status` 0/1/2/3/4**, robot làm gì ở từng trạng thái? _(Mục 9.4: chỉ status 1 mới di chuyển.)_
3. **Vì sao `GET` lặp phải trả cùng lệnh, `DONE` lặp không được đếm lần hai?** _(Tránh gắp/đếm hai lần khi mạng gửi lặp.)_
4. **Vì sao không coi khay đủ chỉ vì robot vừa chạy xong?** _(Phải có ảnh mới AI xác nhận; nếu ô vừa đặt không `ok` thì status 2.)_
5. **Vì sao chia tập theo bố trí khay?** _(Tránh rò rỉ: ảnh gần giống ở train và test làm điểm cao ảo.)_
6. **Ngưỡng confidence chọn bằng tập nào, khóa lúc nào?** _(Chọn bằng val, khóa trước khi chấm test.)_
7. **`TCP` trong URSim là gì, khác "TCP/IP" thế nào?** _(Tool Center Point là điểm đầu kẹp; TCP/IP là giao thức mạng.)_
8. **Khi mất kết nối giữa chừng, hệ thống làm gì?** _(Bridge giữ trạng thái; lệnh chưa DONE bị chặn; robot bật DO1; người vận hành xác nhận rồi RESET.)_
9. **Vì sao dùng MoveJ cho chuyển vùng, MoveL cho hạ/nâng?** _(Hạ/nâng cần đường thẳng, chuyển vùng cần nhanh.)_
10. **Độ đúng của mô hình khác độ đúng của robot thế nào?** _(Mô hình so với nhãn thật; robot là có làm đúng lệnh đã nhận không.)_

---

## 17. Lỗi hay gặp

| Hiện tượng                              | Nguyên nhân thường gặp                                                                 | Cách xử lý                                                                |
| --------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| URSim `socket_open` trả False           | Firewall chặn cổng 5000; sai IP; bridge chưa chạy                                      | Mở inbound rule TCP 5000; `ipconfig` lấy IP VMnet8/LAN; chạy bridge trước |
| Popup không liệt kê biến                | Biến chưa tạo bằng Assignment                                                          | Thêm node Assignment `tên := giá trị` trước                               |
| Bridge in `BAD_PACKET`                  | Robot gửi sai cú pháp (ví dụ `GET,1.0`)                                                | Dùng `to_str` trên biến nguyên `cid`; kiểm tra chuỗi gửi                  |
| Bridge trả `status 4`                   | Còn lệnh chưa DONE từ lần chạy trước                                                   | Ctrl+C rồi chạy lại bridge, hoặc robot gửi `RESET,<cid>` sau xác nhận     |
| Bridge luôn trả `status 2` với ảnh thật | Hình chữ nhật ô trong `config.json` không khớp ảnh thật; ngưỡng cao; vật sát ranh giới | Đo lại tọa độ ô theo ảnh thật; xem `conf_min`, `boundary_margin_px`       |
| Sau DONE lại báo `status 2`             | Ảnh bước kế chưa có vật vừa đặt, hoặc thứ tự ảnh sai                                   | Kiểm tra tên ảnh (`step0, step1, ...`)                                    |
| Robot báo "không với tới"               | Waypoint quá xa/góc quá khó                                                            | Dịch điểm gần gốc robot, giữ hướng đầu kẹp cố định                        |
| MoveL lệch sau khi đổi TCP              | Đổi TCP sau khi dạy điểm                                                               | Đặt TCP trước; dạy lại điểm nếu lỡ đổi                                    |
| `yolo` không nhận lệnh                  | Chưa kích hoạt `.venv` hoặc chưa cài ultralytics                                       | `.venv\Scripts\activate` rồi `pip install ultralytics`                    |
| Kết quả test cao bất thường             | Ảnh cùng bố trí ở cả train và test                                                     | Chia lại theo `layout_id`                                                 |
| Git conflict trên `.urp`                | Hai người cùng sửa                                                                     | Chỉ P1 sửa/commit `.urp`                                                  |
| Nối được nhưng URSim không đọc được số  | Gói trả về thiếu ngoặc/ xuống dòng, hoặc quá 5 s                                       | Xem dòng `command` trong log bridge; kiểm tra timeout                     |

---

## 18. Việc còn thiếu trong code

Những phần sau **chưa có**; ai nhận thì ghi vào bảng phân công:

| Việc                                                                                                                        | Người đề xuất | Ghi chú                                                        |
| --------------------------------------------------------------------------------------------------------------------------- | ------------- | -------------------------------------------------------------- |
| `split_dataset.py`: đọc `metadata.csv`, chia 60/20/20 theo `layout_id`, sinh `splits.csv` và cấu trúc `data/yolo/`          | P2            | Seed cố định, giữ các `condition` ở cả 3 tập                   |
| `train.py`: bọc lệnh huấn luyện YOLO, lưu cấu hình                                                                          | P3            | Có thể chỉ gọi `ultralytics.YOLO(...).train(...)`              |
| `evaluate.py`: chạy test, tính độ đúng cấp khay, số khay thiếu/sai nhận nhầm là đủ, confusion matrix, lưu ảnh sai, xuất CSV | P3            | Dùng `infer.detect` + `check_tray.check_tray` + `metadata.csv` |
| Vẽ hộp/trạng thái ô lên ảnh và hiển thị khi bridge chạy (để quay video "hiện ảnh AI")                                       | P3            | Có thể dùng OpenCV                                             |
| Ghi thời gian suy luận vào log CSV (hiện chỉ in ra console)                                                                 | P3            | Cột riêng, tách với thời gian chu kỳ                           |
| Chương trình URSim hoàn chỉnh (mục 12)                                                                                      | P1            |                                                                |

---

## 19. Thứ tự ưu tiên khi thiếu thời gian

1. **P2 chụp ảnh ngay** (nút thắt: dữ liệu → gán nhãn → huấn luyện). Đừng chờ.
2. **P1 hoàn thành URSim chạy được ca `only_B` với bridge hộp giả**: có bản demo đầu tiên.
3. **P3 viết `split_dataset.py` + huấn luyện baseline** ngay khi có khoảng 50–100 ảnh đã gán nhãn, rồi cải thiện dần.
4. Ghép AI vào bridge (11.9) khi có `best.pt` đầu tiên (chưa cần tốt).
5. Chạy 4 ca bắt buộc + 2 ca bất thường, **ghi bảng ca thử ngay lúc chạy**.
6. Viết báo cáo, quay video. Dành ít nhất 2 ngày cuối, không bỏ.

Nếu phải cắt: giữ **đường chạy thông từ đầu đến cuối** (ảnh → YOLO → check_tray → bridge → URSim → DONE) với dữ liệu ít hơn, và **báo cáo trung thực** giới hạn đã đạt. Mọi mục tiêu định lượng trong đề là tiêu chí đối chiếu, không phải kết quả có sẵn.

---

## 20. Tài liệu tham khảo

[1] Universal Robots – Offline Simulator CB-Series Non Linux URSim 3.15.8.
https://www.universal-robots.com/download/software-cb-series/simulator-non-linux/offline-simulator-cb-series-non-linux-ursim-3158/

[2] Universal Robots – PolyScope Manual 3.13.
https://s3-eu-west-1.amazonaws.com/ur-support-site/77558/Software_Manual_en_US.pdf

[3] Universal Robots – TCP/IP socket communication via URScript (ví dụ CB3 3.1).
https://www.universal-robots.com/articles/ur/interface-communication/tcpip-socket-communication-via-urscript/

[4] Microsoft – Python environments in VS Code.
https://code.visualstudio.com/docs/python/environments

[5] Ultralytics – Detection, Classification và Pose.
https://docs.ultralytics.com/tasks/

_(Nhóm dùng URSim 3.15.6.106324 có sẵn trong máy ảo; tài liệu [1] là bản 3.15.8, ghi rõ sự khác biệt phiên bản trong báo cáo.)_
