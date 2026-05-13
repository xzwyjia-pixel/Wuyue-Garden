"""
直播监控核心 — 评论区 OCR + 全景截图 + 画面变化检测
"""

import json
import time
import os
import logging
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import easyocr

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  修改位置 ↓↓↓  调整评论区截图区域 (left, top, width, height)
CHAT_AREA = (1450, 200, 450, 750)
#  修改位置 ↑↑↑
# ═══════════════════════════════════════════════════════════

CHAT_INTERVAL = 20          # 评论区截图间隔(秒)
PANORAMA_INTERVAL = 120     # 全景截图间隔(秒, 2分钟)
CHANGE_TIMEOUT = 60         # 无变化告警阈值(秒)
CHANGE_THRESHOLD = 5.0      # 画面差异阈值(像素均值, 越低越敏感)

OUTPUT = "chat_log.json"
SCREENSHOT_DIR = "screenshots"


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_log(path):
    p = Path(path)
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            log.warning("Log corrupted, start fresh")
    return []


def flush_log(data, path):
    tmp = Path(path).with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def capture_chat_img() -> np.ndarray | None:
    """截取评论区, 返回 numpy array."""
    try:
        img = pyautogui.screenshot(region=CHAT_AREA)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception:
        log.exception("Chat screenshot failed")
        return None


def save_chat_snapshot(img_bgr: np.ndarray) -> str:
    """保存评论区临时图片供 OCR, 返回路径."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"._chat_{stamp}.png"
    cv2.imwrite(path, img_bgr)
    return path


def ocr_image(reader, img_bgr: np.ndarray) -> list[str]:
    """OCR 识别, 返回文字列表."""
    path = save_chat_snapshot(img_bgr)
    results = reader.readtext(path)
    os.remove(path)
    return [r[1] for r in results]


def detect_change(prev: np.ndarray | None, curr: np.ndarray) -> float:
    """计算两帧差异均值. 返回 0~255, 越大变化越多."""
    if prev is None:
        return 999.0
    diff = cv2.absdiff(prev, curr)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    return float(gray.mean())


def capture_panorama():
    """全景截图."""
    ensure_dir(SCREENSHOT_DIR)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/panorama_{stamp}.png"
    try:
        pyautogui.screenshot().save(path)
        log.info("全景截图 → %s", path)
    except Exception:
        log.exception("全景截图失败")


def main():
    ensure_dir(SCREENSHOT_DIR)
    log.info("CHAT_AREA=%s  评论区=%ss  全景=%ss  变化阈值=%s",
             CHAT_AREA, CHAT_INTERVAL, PANORAMA_INTERVAL, CHANGE_THRESHOLD)

    reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
    buffer = load_log(OUTPUT)

    prev_frame: np.ndarray | None = None
    quiet_cycles = 0
    quiet_limit = CHANGE_TIMEOUT // CHAT_INTERVAL  # 60/20=3
    last_pano = 0

    while True:
        now = time.time()

        # ── 评论区截图 + OCR ──
        frame = capture_chat_img()
        if frame is not None:
            texts = ocr_image(reader, frame)
            entry = {
                "timestamp": now,
                "time": datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
                "texts": texts,
                "ocr_count": len(texts),
            }
            buffer.append(entry)
            flush_log(buffer, OUTPUT)
            log.info("[%s] %d段文字  总记录=%d", entry["time"], len(texts), len(buffer))

            # ── 画面变化检测 ──
            diff = detect_change(prev_frame, frame)
            prev_frame = frame

            if diff < CHANGE_THRESHOLD:
                quiet_cycles += 1
                if quiet_cycles >= quiet_limit:
                    log.warning("⚠️  画面静止 %ds, 可能断流!  diff=%.2f",
                                quiet_cycles * CHAT_INTERVAL, diff)
            else:
                quiet_cycles = 0  # 有变化, 重置

        # ── 全景截图 ──
        if now - last_pano >= PANORAMA_INTERVAL:
            capture_panorama()
            last_pano = now

        time.sleep(CHAT_INTERVAL)


if __name__ == "__main__":
    main()
