"""print_guide.py - Tạo data/shoot_guide.txt: hướng dẫn chụp theo đúng thứ tự bấm máy.
Chạy sau make_plan.py:  python print_guide.py
"""
import csv
import re

PLAN, ORDER, OUT = "data/shoot_plan.csv", "data/shoot_order.csv", "data/shoot_guide.txt"
HINT_TEXT = {
    "giua_o": "đặt vật ở giữa ô",
    "lech_len": "đặt vật lệch về phía trên trong ô",
    "lech_xuong": "đặt vật lệch về phía dưới trong ô",
    "lech_trai": "đặt vật lệch sang trái trong ô",
    "lech_phai": "đặt vật lệch sang phải trong ô",
    "xoay_45": "xoay vật khoảng 45 độ",
    "xoay_90": "xoay vật khoảng 90 độ",
}


def explain(tok):
    if tok.startswith("dat_"):
        return HINT_TEXT.get(tok[4:], tok)
    m = re.match(r"^che_(A1|A2|B1|C1)_(\d+)$", tok)
    if m:
        return f"che khoảng {m.group(2)}% vật ở ô {m.group(1)} bằng mảnh giấy hoặc tay (vật che nằm trong khung hình)"
    m = re.match(r"^([ABC])_giua_(A1|A2|B1|C1)-(A1|A2|B1|C1)$", tok)
    if m:
        return (f"vật {m.group(1)} nằm vắt ngang đường kẻ giữa {m.group(2)} và {m.group(3)}, "
                "tâm vật sát đường kẻ")
    m = re.match(r"^([ABC])_ngoai_khay$", tok)
    if m:
        return f"vật {m.group(1)} đặt ngoài tờ giấy khay, cách mép giấy một đoạn (vẫn trong khung hình)"
    return tok


def cell_text(v):
    return "trống" if v == "-" else v


def main():
    with open(PLAN, encoding="utf-8-sig") as f:
        plan = {r["filename"]: r for r in csv.DictReader(f)}
    with open(ORDER, encoding="utf-8-sig") as f:
        order = list(csv.DictReader(f))

    lines = [
        "HƯỚNG DẪN CHỤP (theo đúng thứ tự bấm máy, không bỏ, không đổi thứ tự)",
        "Quy ước: 'trống' = ô không có vật; 'A+A' = hai vật A trong cùng một ô; "
        "'B+A' = vật B và vật A trong cùng một ô.",
        "Mỗi bố trí chụp 3 ảnh liên tiếp: đổi nhẹ ánh sáng/bóng đổ, KHÔNG chạm điện thoại, "
        "KHÔNG đổi vị trí vật giữa 3 ảnh.",
        "",
    ]
    i, n_layout = 0, 0
    while i < len(order):
        row = order[i]
        if row["kind"] == "ref":
            lines.append(f"#{int(row['order']):03d}  {row['filename']}  >>> KHAY TRỐNG: "
                         "lấy hết vật ra khỏi khay, chụp 1 ảnh")
            lines.append("")
            i += 1
            continue
        p = plan[row["filename"]]
        j = i
        while (j < len(order) and order[j]["kind"] == "photo"
               and plan[order[j]["filename"]]["layout_id"] == p["layout_id"]):
            j += 1
        first, last = int(order[i]["order"]), int(order[j - 1]["order"])
        lines.append(f"#{first:03d}-#{last:03d}  {p['layout_id']}  [{p['condition']}]")
        lines.append("    A1: {} | A2: {} | B1: {} | C1: {}".format(
            *(cell_text(p[c]) for c in ("A1", "A2", "B1", "C1"))))
        empty = all(p[c] == "-" for c in ("A1", "A2", "B1", "C1"))
        if empty:
            lines.append("    - KHAY TRỐNG HOÀN TOÀN: không đặt vật nào, chụp 3 ảnh khay trống")
        for tok in p["note"].split(";"):
            if tok and not (empty and tok.startswith("dat_")):
                lines.append(f"    - {explain(tok)}")
        lines.append("")
        n_layout += 1
        i = j

    with open(OUT, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))
    print(f"Đã ghi {OUT}: {n_layout} bố trí, {len(order)} lần bấm máy")


if __name__ == "__main__":
    main()
