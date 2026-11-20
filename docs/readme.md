## Chạy đồng bộ Server Python (VS Code) và Robot URSim

> **Nguyên tắc bắt buộc:** Luôn khởi động Server Python trên VS Code **trước**, sau đó mới bấm **Play** trên URSim.

### Bước 1: Chạy Server cho kịch bản `S01` tại Terminal VS Code
```powershell
python -X utf8 bridge.py --mode ai --images data/demo_seq/S01
```
Chờ Terminal hiển thị thông báo server đang lắng nghe tại `0.0.0.0:5000`.

### Bước 2: Bấm Play trên URSim
* Nhấn nút **Play** trên giao diện PolyScope của URSim.
* Robot tự động gắp và đặt linh kiện theo thứ tự ưu tiên `A1 → A2 → B1 → C1` dựa trên gói tin phản hồi từ AI.
* Khi kết thúc chuỗi, màn hình URSim hiện popup tổng kết bộ đếm (`n_dat`, `n_khay_xong`, `n_cho`, `n_loi`) và lịch sử gói tin được lưu tự động thành file `.csv` trong thư mục `logs/`.

### Bước 3: Chuyển sang kịch bản tiếp theo (`S02` → `S10`)
1. Tại Terminal VS Code, nhấn `Ctrl + C` để dừng server của kịch bản vừa chạy.
2. Chạy lại lệnh với thư mục kịch bản mới (ví dụ `S02`):
   ```powershell
   python -X utf8 bridge.py --mode ai --images data/demo_seq/S02
   ```
3. Quay lại URSim và bấm **Play** để chạy chu kỳ tiếp theo.

---

##  Xử lý nhanh lỗi kết nối thường gặp

* **Dọn tiến trình Python chạy ngầm (khi đổi kịch bản nhưng URSim vẫn trả về kết quả cũ do kẹt cổng `5000`):**
  ```powershell
  Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
  ```

* **Mở cổng TCP `5000` trên Windows Firewall (chạy 1 lần với quyền Administrator nếu URSim báo `okk = False` hoặc `[0, nan, ...]`):**
  ```powershell
  New-NetFirewallRule -DisplayName "URSim Port 5000" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
  ```