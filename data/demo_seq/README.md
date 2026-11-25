# Bộ Kịch Bản Kiểm Thử Chuỗi Ảnh (`data/demo_seq/S01` – `S13`)

Bộ dữ liệu gồm **13 kịch bản** (trong đó **10 chuỗi nhiều bước** trước–sau và **3 ca biên 1 bước**), kích thước ảnh chuẩn hóa `640×480`, thứ tự ưu tiên cấp bù `A1 → A2 → B1 → C1`.

| Chuỗi | Ca kiểm thử | Số bước | Lệnh / Trạng thái mong đợi từng bước (`status, cls, slot`) | Bộ đếm & ngõ ra mong đợi trên URSim |
| :--- | :--- | :---: | :--- | :--- |
| **S01** | Thiếu 2 A và 1 C (chỉ có B1) | 4 | `step00`: `status=1, cls=1, slot=1` (A→A1)<br>`step01`: `status=1, cls=1, slot=2` (A→A2)<br>`step02`: `status=1, cls=3, slot=4` (C→C1)<br>`step03`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=3`, `n_khay_xong=1`, `n_cho=0` |
| **S02** | Thiếu 1 A ở ô A1 | 2 | `step00`: `status=1, cls=1, slot=1` (A→A1)<br>`step01`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=1`, `n_khay_xong=1`, `n_cho=0` |
| **S03** | Thiếu B ở ô B1 | 2 | `step00`: `status=1, cls=2, slot=3` (B→B1)<br>`step01`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=1`, `n_khay_xong=1`, `n_cho=0` |
| **S04** | Thiếu C ở ô C1 | 2 | `step00`: `status=1, cls=3, slot=4` (C→C1)<br>`step01`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=1`, `n_khay_xong=1`, `n_cho=0` |
| **S05** | Thiếu cả 2 A (chỉ có B1, C1) | 3 | `step00`: `status=1, cls=1, slot=1` (A→A1)<br>`step01`: `status=1, cls=1, slot=2` (A→A2)<br>`step02`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=2`, `n_khay_xong=1`, `n_cho=0` |
| **S06** | Khay trống hoàn toàn (4 ô trống) | 5 | `step00`: `status=1, cls=1, slot=1` (A→A1)<br>`step01`: `status=1, cls=1, slot=2` (A→A2)<br>`step02`: `status=1, cls=2, slot=3` (B→B1)<br>`step03`: `status=1, cls=3, slot=4` (C→C1)<br>`step04`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=4`, `n_khay_xong=1`, `n_cho=0` |
| **S07** | Khay đủ bộ ngay từ đầu | 1 | `step00`: `status=3, cls=0, slot=0` (Đủ bộ ngay) | `n_dat=0`, `n_khay_xong=1`, `n_cho=0` |
| **S08** | Đặt nhầm ô (sai loại linh kiện) | 1 | `step00` (retry 3 lần): `status=2, 2, 2` (`wrong_type`) | `n_dat=0`, `n_khay_xong=0`, `n_cho=3`, popup `"Can nguoi van hanh kiem tra"`, `DO1` bật |
| **S09** | Ảnh không đổi sau khi robot báo `DONE` | 2 | `step00`: `status=1, cls=1, slot=1` (A→A1)<br>`step01` (retry 3 lần): `status=2, 2, 2` (`not_confirmed`) | `n_dat=1`, `n_khay_xong=0`, `n_cho=3`, popup `"Can nguoi van hanh kiem tra"`, `DO1` bật |
| **S10** | Bị che khuất vật ở ô A1 (`conf < 0.5`) | 1 | `step00` (retry 3 lần): `status=2, 2, 2` (`low_confidence` / `empty`) | `n_dat=0`, `n_khay_xong=0`, `n_cho=3`, popup `"Can nguoi van hanh kiem tra"`, `DO1` bật |
| **S11** | Thiếu A1 và C1 (chỉ có A2, B1) | 3 | `step00`: `status=1, cls=1, slot=1` (A→A1)<br>`step01`: `status=1, cls=3, slot=4` (C→C1)<br>`step02`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=2`, `n_khay_xong=1`, `n_cho=0` |
| **S12** | Thiếu B1 và C1 (chỉ có A1, A2) | 3 | `step00`: `status=1, cls=2, slot=3` (B→B1)<br>`step01`: `status=1, cls=3, slot=4` (C→C1)<br>`step02`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=2`, `n_khay_xong=1`, `n_cho=0` |
| **S13** | Thiếu A2 và B1 (chỉ có A1, C1) | 3 | `step00`: `status=1, cls=1, slot=2` (A→A2)<br>`step01`: `status=1, cls=2, slot=3` (B→B1)<br>`step02`: `status=3, cls=0, slot=0` (Đủ bộ) | `n_dat=2`, `n_khay_xong=1`, `n_cho=0` |