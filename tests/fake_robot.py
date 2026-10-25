"""fake_robot.py - Robot giả (client TCP) mô phỏng logic URSim để test bridge.py.

  Terminal 1: python bridge.py --mode script --scenario only_B
  Terminal 2: python tests/fake_robot.py --host 127.0.0.1 [--dup-get] [--dup-done]
"""
import argparse
import math
import os
import socket
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from check_tray import load_config, compatible, CODE_CLASS  # noqa: E402


def recv_line(sock, buf):
    while b"\n" not in buf[0]:
        data = sock.recv(4096)
        if not data:
            raise ConnectionError("server đóng kết nối")
        buf[0] += data
    line, buf[0] = buf[0].split(b"\n", 1)
    return line.decode().strip()


def parse(line):
    """Giống kiểm tra trong URSim: đủ 8 số hữu hạn, có ngoặc tròn."""
    if not (line.startswith("(") and line.endswith(")")):
        return None
    try:
        vals = [float(x) for x in line[1:-1].split(",")]
    except ValueError:
        return None
    if len(vals) != 8 or not all(math.isfinite(v) for v in vals):
        return None
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--max-ids", type=int, default=20)
    ap.add_argument("--max-retries", type=int, default=3)
    ap.add_argument("--dup-get", action="store_true", help="gửi GET lặp cùng id, phải nhận cùng lệnh")
    ap.add_argument("--dup-done", action="store_true", help="gửi DONE hai lần")
    args = ap.parse_args()
    cfg = load_config()
    port = args.port or cfg["server"]["port"]
    conf_min = cfg["thresholds"]["conf_min"]

    s = socket.create_connection((args.host, port), timeout=cfg["server"]["robot_timeout_s"])
    buf = [b""]
    send = lambda text: s.sendall((text + "\n").encode())

    placed, retries, trays = [], 0, 0
    for id_ in range(1, args.max_ids + 1):
        send(f"GET,{id_}")
        line = recv_line(s, buf)
        if args.dup_get:
            send(f"GET,{id_}")
            line2 = recv_line(s, buf)
            assert line == line2, f"GET lặp trả khác: {line} vs {line2}"
        vals = parse(line)
        print(f"[robot] id={id_} nhận {line}")
        if vals is None or int(vals[0]) != id_:
            print("[robot] gói sai -> nhánh lỗi, DO1 bật")
            break
        status, cls, conf, slot = int(vals[1]), int(vals[2]), vals[6], int(vals[7])
        if status == 1:
            if conf < conf_min or not compatible(cls, slot, cfg):
                print("[robot] lệnh bị từ chối ở client")
                break
            time.sleep(0.1)  # giả lập gắp/đặt
            send(f"DONE,{id_}")
            if args.dup_done:
                send(f"DONE,{id_}")
            placed.append((CODE_CLASS[cls], slot))
            print(f"[robot] đã đặt {CODE_CLASS[cls]} -> ô {slot}, gửi DONE,{id_}")
        elif status == 3:
            send(f"DONE,{id_}")
            trays += 1
            print("[robot] khay hoàn tất, n_khay_xong +1")
            break
        else:
            retries += 1
            print(f"[robot] status {status}: chờ/ngoại lệ, không DONE (lần {retries})")
            if retries >= args.max_retries:
                print("[robot] quá số lần thử -> dừng chờ xác nhận người vận hành")
                break
            time.sleep(0.2)
    time.sleep(0.3)
    print(f"\nTổng kết: lệnh đã thực hiện = {placed}, khay hoàn tất = {trays}")
    s.close()


if __name__ == "__main__":
    main()