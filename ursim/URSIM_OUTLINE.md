# Phác chương trình URSim (cho người làm URSim)

> Đây là bản phác, CHƯA chạy thử trên PolyScope 3.15.6. Kiểm tra cú pháp/hàm trong URSim và sửa theo thực tế.

## Biến chương trình (BeforeStart)

```
ip = "192.168.x.1"    # IP máy chạy Python (KHÔNG phải 127.0.0.1)
port = 5000
cid = 0               # mã chu kỳ
last_done = -1
n_khay_xong = 0       # tăng đúng 1 lần mỗi khay (status 3)
n_dat = 0             # số linh kiện đã đặt (tăng SAU khi đặt xong)
n_cho = 0             # số lần chờ/kiểm tra lại (status 0/2)
n_loi = 0             # số lần lỗi
retries = 0
st = 0   cls = 0   slot = 0   conf = 0.0   ok = False
```

Đầu chương trình: `set_digital_out(0,False)`, `(1,False)`, `(2,False)`; MoveJ Home.

## Cây chương trình

```
BeforeStart: khởi tạo biến, đưa DO về Off
Robot Program
  MoveJ Home
  Loop (cho tới khi n_khay_xong >= số khay cần / hoặc Loop True + nút dừng)
    Script: GOI_LENH          # cid += 1, GET, đọc 8 số, kiểm tra -> ok, st, cls, slot, conf
    If ok == False
      DO1 = On (lỗi/mất kết nối); n_loi += 1; Popup/Wait ngắn; xử lý kết nối lại
    ElseIf st == 1 and conf >= 0.5 and (tương thích class/slot)
      DO1 = Off
      If cls == 1: SubProgram Lay_A
      ElseIf cls == 2: SubProgram Lay_B
      ElseIf cls == 3: SubProgram Lay_C
      SubProgram Dat_VaoO     # dùng biến slot (1..4) chọn ô đặt
      Script: gửi "DONE,<cid>"
      n_dat += 1              # chỉ sau khi đặt xong
      DO2 = On, Wait 0.2, DO2 = Off   # xung hoàn tất MỖI LẦN ĐẶT (tách khỏi bộ đếm khay)
    ElseIf st == 3
      Script: gửi "DONE,<cid>"
      n_khay_xong += 1        # đúng một lần
    Else   # st = 0, 2, 4 hoặc lệnh không hợp lệ
      n_cho += 1; Wait 0.5 (không gửi DONE; vòng sau dùng cid mới); giới hạn số lần thử
```

Tương thích class/slot: `(cls==1 and (slot==1 or slot==2)) or (cls==2 and slot==3) or (cls==3 and slot==4)`.

## SubProgram

- `Lay_A`, `Lay_B`, `Lay_C`: MoveJ điểm tiếp cận → MoveL hạ → DO0 = On (đóng kẹp), Wait → MoveL nâng.
- `Dat_VaoO`: If slot == 1..4 → MoveJ/MoveL tới tiếp cận ô → hạ → DO0 = Off (mở kẹp) → nâng.
- Mỗi vị trí cấp (A/B/C) và mỗi ô (1–4) có điểm tiếp cận riêng. Dạy Waypoint trong vùng với tới của UR3.

## Script nối socket (gợi ý, kiểm tra hàm trong URSim)

```
# mở kết nối nếu chưa có
if not socket_open(ip, port, "py"):
  ok = False
else:
  cid = cid + 1
  socket_send_line(str_cat("GET,", to_str(cid)), "py")   # socket_send_line tự thêm \n
  r = socket_read_ascii_float(8, "py", 5)                # tham số timeout 5 s: kiểm tra bản 3.15 có hỗ trợ không
  if r[0] == 8:
    # r[1]=id r[2]=status r[3]=class r[4]=x r[5]=y r[6]=yaw r[7]=confidence r[8]=slot
    if r[1] == cid:
      st = r[2]  cls = r[3]  conf = r[7]  slot = r[8]  ok = True
    else: ok = False      # lệch id -> không dùng dữ liệu cũ
  else:
    ok = False            # hết thời gian / thiếu số
  end
end
# gửi DONE:   socket_send_line(str_cat("DONE,", to_str(cid)), "py")
```

Điểm cần tự kiểm tra trong URSim:

1. `socket_read_ascii_float` có tham số timeout trong 3.15.6 không. Nếu không: dùng vòng đọc có giới hạn
   thời gian, hoặc Thread chỉ đọc socket (theo quy định quyền ghi biến trong đề).
2. `str_cat`, `to_str`, `socket_send_line` có sẵn không. Nếu không, gửi chuỗi đã ghép sẵn + `"\n"` bằng `socket_send_string`.
3. Kiểm tra kết quả `[0] == 8` trước khi đọc `[1]…[8]`; hết thời gian thì không dùng dữ liệu cũ.
4. Sau khi mất kết nối: dùng `socket_close` rồi mở lại; nếu Python báo `status=4` vì lệnh chưa DONE
   thì người vận hành xác nhận rồi gửi `RESET,<cid>`.

## Bảng I/O

| Tín hiệu | Ý nghĩa                            |
| -------- | ---------------------------------- |
| DO0      | On = đóng kẹp, Off = mở kẹp        |
| DO1      | Lỗi chương trình/quy trình/kết nối |
| DO2      | Xung hoàn tất một lần đặt          |

## Bảng Waypoint (điền sau khi dạy)

Home | Cap_A_Approach, Cap_A | Cap_B_Approach, Cap_B | Cap_C_Approach, Cap_C | O1..O4_Approach, O1..O4

## Ca thử cần chạy (kết quả dự kiến vs quan sát, ghi riêng)

1. `only_B` → A→1, A→2, C→4, rồi status 3, `n_khay_xong = 1`
2. `full` → không cấp thêm, `n_khay_xong = 1`
3. `wrong_slot` → status 2, không gắp
4. `unchanged_after_done` / `occluded` → status 2, không coi là đủ
5. Thêm ≥ 2 ca bất thường: tắt bridge giữa chừng (mất kết nối), gói sai, DONE lặp…
