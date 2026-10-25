"""bridge.py - TCP server (Python) <-> URSim (client).

Chạy từ thư mục gốc repo:
  python bridge.py --mode script --scenario only_B        # ảnh giả theo kịch bản (chưa cần AI)
  python bridge.py --mode ai --images data/demo_seq       # ảnh thật + YOLO (sau khi có model)

Giao thức (mỗi gói kết thúc bằng '\\n'):
  Robot -> Python : GET,<id>      yêu cầu lệnh cho chu kỳ <id>
  Python -> Robot : (id,status,class,x,y,yaw,confidence,slot)
  Robot -> Python : DONE,<id>     đã đặt xong (Python KHÔNG trả lời DONE)
  Robot -> Python : RESET,<id>    xác nhận đặt lại phiên sau khi người vận hành kiểm tra; Python trả status 0
Quy ước status: 0 chờ | 1 lệnh hợp lệ | 2 cần kiểm tra lại | 3 khay hoàn tất | 4 lỗi
Class: A=1, B=2, C=3. x,y,yaw luôn 0 (bài này dùng Waypoint cố định).
"""
import argparse
import csv
import datetime
import glob
import os
import socket
import sys

from check_tray import load_config, analyze, decide, compatible, CODE_CLASS


def fmt(id_, status, cls, conf, slot):
    return f"({id_},{status},{cls},0,0,0,{conf:.2f},{slot})\n"


class Logger:
    def __init__(self, log_dir):
        os.makedirs(log_dir, exist_ok=True)
        name = datetime.datetime.now().strftime("session_%Y%m%d_%H%M%S.csv")
        self.path = os.path.join(log_dir, name)
        self.f = open(self.path, "w", newline="", encoding="utf-8")
        self.w = csv.writer(self.f)
        self.w.writerow(["time", "event", "id", "source", "prediction", "command", "detail"])

    def log(self, event, id_="", source="", prediction="", command="", detail=""):
        t = datetime.datetime.now().isoformat(timespec="milliseconds")
        self.w.writerow([t, event, id_, source, prediction, command, detail])
        self.f.flush()
        print(f"[{t[11:]}] {event:<14} id={id_!s:<4} {command} {detail}")


class FrameSource:
    """Quản lý kịch bản ảnh: chỉ sang khung kế tiếp khi gọi advance() (sau DONE)."""

    def __init__(self, frames):
        self.frames = frames  # list of (label, loader) ; loader() -> list detections
        self.i = 0

    def current(self):
        return self.frames[self.i]

    def advance(self):
        if self.i < len(self.frames) - 1:
            self.i += 1


class Session:
    """Trạng thái giữ nguyên khi robot mất kết nối rồi nối lại."""

    def __init__(self, cfg, source, log):
        self.cfg, self.source, self.log = cfg, source, log
        self.cache = {}          # id -> dòng đã trả (GET lặp trả lại y hệt)
        self.done = set()        # id đã DONE (DONE lặp không cập nhật lần hai)
        self.pending = None      # lệnh status 1/3 đã phát nhưng chưa DONE
        self.last_placed = None  # (cls, slot) vừa DONE, cần ảnh mới xác nhận
        self.trays_done = 0

    # ---- GET ----
    def handle_get(self, id_):
        if id_ in self.cache:
            line = self.cache[id_]
            self.log.log("GET_REPEAT", id_, command=line.strip())
            return line
        if self.pending and self.pending["id"] != id_:
            line = fmt(id_, 4, 0, 0.0, 0)
            self.log.log("REJECT_PENDING", id_, command=line.strip(),
                         detail=f"id {self.pending['id']} chưa DONE; cần RESET có xác nhận")
            return line

        label, loader = self.source.current()
        res = decide(analyze(loader(), self.cfg), self.cfg, self.last_placed)
        status, cls, slot, reason = res["status"], res["cls"], res["slot"], res["reason"]
        if status == 1 and not compatible(cls, slot, self.cfg):
            status, cls, slot, reason = 4, 0, 0, "class_slot_incompatible"
        line = fmt(id_, status, cls, res["conf"], slot)
        self.cache[id_] = line
        if status in (1, 3):
            self.pending = {"id": id_, "status": status, "cls": cls, "slot": slot}
            self.last_placed = None  # ô vừa đặt đã được ảnh mới xác nhận
        self.log.log("GET", id_, source=label, prediction=str(res["states"]),
                     command=line.strip(), detail=reason)
        return line

    # ---- DONE ----
    def handle_done(self, id_):
        if id_ in self.done:
            self.log.log("DONE_REPEAT", id_, detail="bỏ qua, không đổi trạng thái")
            return
        if not self.pending or self.pending["id"] != id_:
            self.log.log("DONE_REJECT", id_, detail="không có lệnh đang chờ với id này")
            return
        p = self.pending
        self.done.add(id_)
        self.pending = None
        if p["status"] == 1:
            self.last_placed = (p["cls"], p["slot"])
            self.log.log("DONE", id_, command=f"class={p['cls']} slot={p['slot']}")
        else:
            self.trays_done += 1
            self.log.log("DONE", id_, detail=f"khay hoàn tất, tổng khay = {self.trays_done}")
        self.source.advance()  # chỉ đổi sang ảnh/bước kế sau DONE

    # ---- RESET ----
    def handle_reset(self, id_):
        self.log.log("RESET", id_, detail=f"xóa pending={self.pending}")
        self.pending = None
        return fmt(id_, 0, 0, 0.0, 0)

    def handle_line(self, text):
        parts = [p.strip() for p in text.split(",")]
        cmd = parts[0].upper()
        try:
            if cmd not in ("GET", "DONE", "RESET") or len(parts) != 2:
                raise ValueError("cú pháp")
            id_ = int(parts[1])
        except ValueError:
            line = fmt(0, 4, 0, 0.0, 0)
            self.log.log("BAD_PACKET", command=line.strip(), detail=repr(text))
            return line if cmd == "GET" or cmd not in ("DONE", "RESET") else None
        if cmd == "GET":
            return self.handle_get(id_)
        if cmd == "DONE":
            self.handle_done(id_)
            return None
        return self.handle_reset(id_)


def serve(cfg, session):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((cfg["server"]["host"], cfg["server"]["port"]))
    srv.listen(1)
    print(f"Server lắng nghe {cfg['server']['host']}:{cfg['server']['port']} | log: {session.log.path}")
    while True:
        conn, addr = srv.accept()
        session.log.log("CONNECT", detail=str(addr))
        buf = b""
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                buf += data
                while b"\n" in buf:  # một recv có thể là nửa dòng hoặc nhiều dòng
                    raw, buf = buf.split(b"\n", 1)
                    reply = session.handle_line(raw.decode("ascii", "replace").strip())
                    if reply:
                        conn.sendall(reply.encode("ascii"))
        except OSError as e:
            session.log.log("CONN_ERROR", detail=str(e))
        finally:
            conn.close()
            session.log.log("DISCONNECT", detail="giữ nguyên trạng thái phiên")


def build_source(args, cfg):
    if args.mode == "script":
        from tests.scenarios import build
        scenarios = build(cfg)
        if args.scenario not in scenarios:
            sys.exit(f"Kịch bản '{args.scenario}' không có. Có: {', '.join(scenarios)}")
        frames = [(f"{args.scenario}#step{i}", (lambda d=d: d))
                  for i, d in enumerate(scenarios[args.scenario])]
    else:
        import infer
        files = sorted(p for ext in ("jpg", "jpeg", "png") for p in glob.glob(os.path.join(args.images, f"*.{ext}")))
        if not files:
            sys.exit(f"Không thấy ảnh trong {args.images}")
        frames = [(os.path.basename(p), (lambda p=p: infer.detect(p, cfg))) for p in files]
    return FrameSource(frames)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    ap.add_argument("--mode", choices=["script", "ai"], default="script")
    ap.add_argument("--scenario", default="only_B")
    ap.add_argument("--images", default="data/demo_seq", help="thư mục ảnh theo thứ tự tên (mode ai)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    session = Session(cfg, build_source(args, cfg), Logger(cfg["log_dir"]))
    try:
        serve(cfg, session)
    except KeyboardInterrupt:
        print("\nDừng server.")


if __name__ == "__main__":
    main()