"""imgio.py - Đọc ảnh theo đúng MỘT quy ước hướng, dùng chung cho mọi script."""
import cv2

_ROT = {"ccw": cv2.ROTATE_90_COUNTERCLOCKWISE, "cw": cv2.ROTATE_90_CLOCKWISE}


def read_oriented(path, cfg, flags=cv2.IMREAD_COLOR):
    img = cv2.imread(path, flags)
    if img is None:
        return None
    h, w = img.shape[:2]
    mode = cfg["image"].get("rotate_portrait")
    if h > w and mode in _ROT:
        img = cv2.rotate(img, _ROT[mode])
    return img
