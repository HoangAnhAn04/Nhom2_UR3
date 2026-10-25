"""Chạy: python tests/test_check_tray.py  (từ thư mục gốc repo)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from check_tray import check_tray, load_config, compatible  # noqa: E402
from tests.scenarios import make_at, build  # noqa: E402

cfg = load_config()
at = make_at(cfg)
full = [at("A", 1), at("A", 2), at("B", 3), at("C", 4)]


def cmd(r):
    return (r["status"], r["cls"], r["slot"])


def test_only_B_sequence():
    sc = build(cfg)["only_B"]
    prev = None
    got = []
    for frame in sc:
        r = check_tray(frame, cfg, prev)
        got.append(cmd(r))
        prev = (r["cls"], r["slot"]) if r["status"] == 1 else None
    assert got == [(1, 1, 1), (1, 1, 2), (1, 3, 4), (3, 0, 0)], got


def test_full_tray():
    assert cmd(check_tray(full, cfg)) == (3, 0, 0)


def test_right_count_wrong_slot():
    r = check_tray([at("A", 1), at("B", 2), at("A", 3), at("C", 4)], cfg)
    assert r["status"] == 2 and "slot2_wrong_type" in r["reason"], r


def test_unchanged_after_done():
    # vừa DONE lệnh A->1 nhưng ảnh mới vẫn chỉ có B ở ô 3
    r = check_tray([at("B", 3)], cfg, prev=(1, 1))
    assert r["status"] == 2 and "placed_slot1_not_confirmed" in r["reason"], r


def test_low_confidence_occluded():
    r = check_tray([at("B", 3), at("A", 1, conf=0.30)], cfg)
    assert r["status"] == 2 and r["states"][1] == "unknown", r


def test_between_slots():
    r = check_tray([at("B", 3), at("A", 1, dx=160)], cfg)
    assert r["status"] == 2 and "between_slots" in r["reason"], r


def test_duplicate_boxes_counted_once():
    a = at("A", 1)
    dup = dict(a, conf=0.80)
    r = check_tray([a, dup, at("A", 2), at("B", 3), at("C", 4)], cfg)
    assert cmd(r) == (3, 0, 0), r


def test_extra_object_in_slot():
    r = check_tray(full + [at("A", 1, dx=-100, dy=-80)], cfg)
    assert r["status"] == 2 and r["states"][1] == "extra", r


def test_object_outside():
    far = {"cls": "A", "box": [1000, 1000, 1060, 1060], "conf": 0.9}
    r = check_tray(full + [far], cfg)
    assert r["status"] == 2 and "object_outside_slots" in r["reason"], r


def test_compatible():
    assert compatible(1, 1, cfg) and compatible(1, 2, cfg)
    assert compatible(2, 3, cfg) and compatible(3, 4, cfg)
    assert not compatible(1, 3, cfg) and not compatible(2, 1, cfg) and not compatible(9, 1, cfg)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"{len(tests)}/{len(tests)} OK")