# Bảng Waypoint đã tính sẵn (UR3, PolyScope 3.15.6)

Tọa độ được **tính bằng động học UR3 (CB3)** và đã kiểm tra: cả 8 điểm đều **với tới được**, không điểm nào gần suy biến cổ tay,
không đường MoveJ nào giữa các điểm tiếp cận hạ thấp dưới 120 mm. Chưa chạy trên URSim của nhóm: sau khi nhập điểm đầu tiên
phải **đối chiếu bước kiểm tra ở mục 3**.

## 1. Quy ước

- Hệ tọa độ **Base** (trục Z hướng lên, gốc ở đế robot). Mặt bàn đặt ở **Z = 0**.
- **TCP = `Kep`** (Z = 100 mm). Mọi tọa độ TCP dưới đây tính theo TCP này.
- Đầu kẹp **luôn hướng xuống**, giữ nguyên hướng ở mọi điểm: `RX = 3.1416, RY = 0, RZ = 0` (rad, dạng rotation vector).
  Màn hình có thể hiện `-3.1416`: tương đương, không sao.
- Điểm **tiếp cận** ở Z = 120 mm. Điểm **gắp/đặt** ở Z = 20 mm (vật cao khoảng 20 mm). Hạ/nâng = **Relative Z = ∓0,1 m**.

## 2. Bố trí (nhìn từ trên xuống, đơn vị mm; X sang phải, Y lên trên)

```
  Y
 -120        O1(-330)     O2(-270)          khay 2×2, các ô cách nhau 60 mm
 -180        O3(-330)     O4(-270)          O1=A1  O2=A2  O3=B1  O4=C1

 -300   C(-360)    B(-300)    A(-240)       3 vị trí cấp, cách nhau 60 mm
        ───────────────────────────────  X
```

| Điểm | Vai trò | X (mm) | Y (mm) | Z tiếp cận | Z gắp/đặt |
|---|---|---|---|---|---|
| `Cap_A` | cấp linh kiện A | −240 | −300 | 120 | 20 |
| `Cap_B` | cấp linh kiện B | −300 | −300 | 120 | 20 |
| `Cap_C` | cấp linh kiện C | −360 | −300 | 120 | 20 |
| `O1` | ô A1 (slot 1) | −330 | −120 | 120 | 20 |
| `O2` | ô A2 (slot 2) | −270 | −120 | 120 | 20 |
| `O3` | ô B1 (slot 3) | −330 | −180 | 120 | 20 |
| `O4` | ô C1 (slot 4) | −270 | −180 | 120 | 20 |
| `Home` | chờ, trên tâm khay | −300 | −150 | 300 | — |

## 3. Bảng 8 điểm cần dạy (nhập theo GÓC KHỚP)

Chỉ cần dạy **8 điểm cố định** này, mỗi điểm nằm trong một node `MoveJ`. Đoạn hạ/nâng dùng Waypoint **Relative Z = −0,1 / +0,1 m**.

| Waypoint | q1 Base | q2 Shoulder | q3 Elbow | q4 Wrist 1 | q5 Wrist 2 | q6 Wrist 3 | TCP đối chiếu (X, Y, Z mm) |
|---|---|---|---|---|---|---|---|
| `Home` | −133.9 | −98.7 | −56.6 | −114.7 | 90.0 | 136.1 | −300, −150, 300 |
| `Cap_A_Approach` | −111.7 | −110.1 | −91.5 | −68.3 | 90.0 | 158.3 | −240, −300, 120 |
| `Cap_B_Approach` | −119.6 | −119.4 | −77.5 | −73.0 | 90.0 | 150.4 | −300, −300, 120 |
| `Cap_C_Approach` | −126.3 | −130.8 | −58.5 | −80.7 | 90.0 | 143.7 | −360, −300, 120 |
| `O1_Approach` | −141.4 | −102.6 | −101.8 | −65.7 | 90.0 | 128.6 | −330, −120, 120 |
| `O2_Approach` | −133.7 | −89.1 | −116.9 | −64.0 | 90.0 | 136.3 | −270, −120, 120 |
| `O3_Approach` | −134.0 | −108.2 | −94.2 | −67.6 | 90.0 | 136.0 | −330, −180, 120 |
| `O4_Approach` | −126.1 | −96.3 | −109.3 | −64.4 | 90.0 | 143.9 | −270, −180, 120 |

Góc ở đơn vị **độ** (PolyScope hiện độ ở màn hình Move). Làm tròn 0,1° nên TCP thực tế lệch so với bảng **không quá 1 mm**
(ví dụ đọc −239.9 thay vì −240): bình thường.

### Kiểm tra bắt buộc sau khi nhập điểm đầu tiên (`Home`)

Mở tab **Move**, chọn Feature = **Base**, TCP = **Kep**. Ô Tool Position phải hiện xấp xỉ
**X −300, Y −150, Z 300**, hướng `RX ≈ 3.14, RY ≈ 0, RZ ≈ 0`, và đầu kẹp nhìn xuống bàn trong khung 3D.
- **Khớp bảng** → mô hình đúng, nhập tiếp 7 điểm còn lại.
- **Không khớp** (ví dụ X đổi dấu, Z lệch nhiều, kẹp không hướng xuống) → **dừng, chụp màn hình gửi lại**, đừng nhập tiếp.

## 4. Cách nhập một điểm

1. Tab **Program** → chọn vị trí trong cây → **Structure → Basic → Move** (tạo `MoveJ` kèm một Waypoint).
2. Chọn Waypoint → **Set this waypoint**. Màn hình chuyển sang giao diện di chuyển.
3. **Cách A (khuyên dùng): nhập góc khớp.** Chạm vào ô giá trị trong khung Joint Position (hoặc nút Set bên cạnh) để mở bảng nhập số,
   gõ 6 góc ở bảng trên, bấm OK, rồi **nhấn giữ nút Auto** cho robot chạy tới tư thế đó. Nhập khớp luôn ra đúng tư thế, không bị
   chọn nhầm nghiệm "lật khuỷu".
   *(Mô tả theo PolyScope 3.x; nếu bản của mày hiển thị khác, chụp màn hình gửi lại.)*
4. **Cách B (nếu không nhập được khớp): nhập Tool Position** `X, Y, Z, RX, RY, RZ` (Feature Base, TCP Kep). Cách này robot tự chọn
   tư thế khớp nên có thể ra tư thế khác bảng; sau khi tới nơi hãy xem q5 có xấp xỉ 90° không.
5. Bấm **OK** để lưu điểm, đổi tên điểm (ví dụ `Home`, `Cap_A_Approach`).
6. Giảm **Speed** (30–50%) khi thử chạy.

## 5. Hạ/nâng bằng Waypoint Relative

Sau mỗi điểm tiếp cận, thêm node `MoveL` có Waypoint **Relative** với `Z = −0.1 m` (hạ: TCP xuống Z = 20 mm), rồi `Set DO0`, `Wait`,
rồi `MoveL` Relative `Z = +0.1 m` (nâng). Sau khi hạ, ô Tool Position phải đọc **Z ≈ 20 mm**: đó là bước đối chiếu thứ hai.
*(Waypoint Relative chưa kiểm chứng trên bản 3.15.6 của nhóm; nếu không có, báo lại để dùng cặp điểm cố định "tiếp cận" và "chạm".)*

## 6. Đổi bố trí thì làm sao

Sửa phần **CẤU HÌNH BỐ TRÍ** trong `ursim/tinh_waypoint.py` (tâm khay, bước ô, vị trí ba chỗ cấp, độ cao), rồi chạy
`python ursim/tinh_waypoint.py` (cần `pip install numpy scipy`). Script in lại bảng góc khớp và cảnh báo điểm nào không với tới.
Cuối bảng in "độ cao thấp nhất trên đường MoveJ" và "khớp lệch lớn nhất": nên giữ độ cao ≥ 50 mm.

## 7. Giới hạn của bảng này (ghi vào báo cáo)

Đây là kiểm chứng bằng **mô hình động học**, không phải bằng va chạm thật. URSim chỉ cho thấy robot có chạy tới các điểm không;
nó không kiểm chứng va chạm với khay hay vật, và không kiểm chứng lực giữ phôi.