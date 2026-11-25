# Hướng Dẫn Chạy Tích Hợp VS Code (`bridge.py`) và URSim (`nhom2_main.urp`)

## 1. Kiểm tra IP và cấu hình URSim (VMware)

1. Trên Windows, mở PowerShell và chạy lệnh `ipconfig` để lấy địa chỉ **IPv4 Address** của card mạng ảo **VMware Network Adapter VMnet8** (ví dụ: `192.168.61.1`).
2. Khởi động **URSim UR3**, vào **File → Load Program** và mở đúng file `nhom2_main.urp` (bản đầy đủ có vòng lặp `Loop chay == True` và 4 chương trình con `Lay_A`, `Lay_B`, `Lay_C`, `Dat_VaoO`).
3. Tại dòng gán biến `ip` ở đầu chương trình URSim, sửa giá trị cho khớp với địa chỉ IP `VMnet8` vừa lấy ở bước 1.

---

## 2. Kích hoạt môi trường ảo trên VS Code

Mở thư mục dự án bằng **VS Code**, nhấn `` Ctrl + ` `` mở Terminal (PowerShell) và kích hoạt `.venv`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
```

---

## 3. Chạy đồng bộ Server Python và Robot URSim

> **Nguyên tắc bắt buộc:** Luôn khởi động Server Python trên VS Code **trước**, sau đó mới bấm **Play** trên URSim.

1. **Khởi động Server cho kịch bản cần chạy (ví dụ `S01`):**
   ```powershell
   python -X utf8 bridge.py --mode ai --images data/demo_seq/S01
   ```
   Chờ Terminal báo đang lắng nghe kết nối tại `0.0.0.0:5000`.

2. **Chạy trên URSim:**
   * Bấm nút **Play** trên thanh điều khiển dưới cùng của PolyScope.
   * Nếu xuất hiện popup xác nhận **RESET** (đưa robot về vị trí khởi tạo `Home`), bấm **Continue** để chương trình bắt đầu chạy.
   * Khi hoàn tất chuỗi, đọc kết quả bộ đếm trên popup (`n_dat`, `n_khay_xong`, `n_cho`, `n_loi`) và kiểm tra trạng thái ngõ ra số (`DO1`) tại tab **I/O** nếu là ca báo lỗi.

3. **Chuyển sang kịch bản tiếp theo (`S02` → `S13`):**
   * Nhấn `Ctrl + C` tại Terminal VS Code để tắt server cũ.
   * Chạy lại lệnh với thư mục kịch bản mới (ví dụ `data/demo_seq/S02`) rồi bấm **Play** trên URSim.

---

## 4. Dọn tiến trình kẹt cổng 5000 & Lưu log tiêu biểu

* **Giải phóng riêng cổng `5000`** (nếu server cũ chưa tắt hẳn khiến URSim nhận nhầm kết quả cũ; lệnh này chỉ tắt đúng tiến trình đang chiếm cổng `5000`, không làm ảnh hưởng các tiến trình Python khác đang chạy trên máy):
  ```powershell
  Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```

* **Mở cổng TCP `5000` trên Windows Firewall** (chạy 1 lần với quyền Administrator nếu URSim không kết nối được):
  ```powershell
  New-NetFirewallRule -DisplayName "URSim Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
  ```

* **Lưu trữ file log tiêu biểu vào `docs/`:**
  Thư mục `logs/` mặc định bị `.gitignore` bỏ qua các file `*.csv`. Sau khi chạy nghiệm thu xong, cần copy các file `logs/session_*.csv` tiêu biểu (và ảnh chụp màn hình popup / tab I/O) sang thư mục `docs/logs/` để đẩy lên GitHub làm minh chứng.