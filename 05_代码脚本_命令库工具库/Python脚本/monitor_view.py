"""
直播评论区监控 — 30s 截图 OCR → chat_log.json, 每 5min 全景截图
"""

import json
import time
import os
import logging
from datetime import datetime
from pathlib import Path

import pyautogui
import easyocr

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── 配置 ───────────────────────────────────────────────────
CHAT_AREA = (1450, 200, 450, 750)  # (left, top, width, height)
CHAT_INTERVAL = 30                  # 评论区截图间隔(秒)
PANORAMA_INTERVAL = 300            # 全景截图间隔(秒, 5min)
OUTPUT = "chat_log.json"
SCREENSHOT_DIR = "screenshots"


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def load_log(path):
    p = Path(path)
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            log.warning("Log corrupted, start fresh")
    return []


def flush_log(data, path):
    tmp = Path(path).with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def capture_chat(reader) -> dict | None:
    """截图评论区 → OCR → 返回条目."""
    ts = time.time()
    stamp = datetime.fromtimestamp(ts).strftime("%Y%m%d_%H%M%S")
    try:
        img = pyautogui.screenshot(region=CHAT_AREA)
    except Exception:
        log.exception("Screenshot failed")
        return None

    # 临时文件 OCR（easyocr 需要文件路径）
    tmp = f"._chat_{stamp}.png"
    img.save(tmp)
    results = reader.readtext(tmp)
    os.remove(tmp)

    texts = [r[1] for r in results]
    entry = {
        "timestamp": ts,
        "time": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
        "texts": texts,
        "ocr_count": len(texts),
    }
    return entry


def capture_panorama():
    """全景截图 → screenshots/"""
    ensure_dir(SCREENSHOT_DIR)
    ts = time.time()
    stamp = datetime.fromtimestamp(ts).strftime("%Y%m%d_%H%M%S")
    path = f"{SCREENSHOT_DIR}/panorama_{stamp}.png"
    try:
        pyautogui.screenshot().save(path)
        log.info("Panorama saved → %s", path)
    except Exception:
        log.exception("Panorama screenshot failed")


def main():
    ensure_dir(SCREENSHOT_DIR)
    log.info("CHAT_AREA=%s  interval=%ss  panorama=%ss", CHAT_AREA, CHAT_INTERVAL, PANORAMA_INTERVAL)

    reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
    buffer = load_log(OUTPUT)
    last_pano = 0

    while True:
        entry = capture_chat(reader)
        if entry:
            buffer.append(entry)
            flush_log(buffer, OUTPUT)
            log.info("[%s] %d texts  total=%d", entry["time"], entry["ocr_count"], len(buffer))

        # 全景截图
        if time.time() - last_pano >= PANORAMA_INTERVAL:
            capture_panorama()
            last_pano = time.time()

        time.sleep(CHAT_INTERVAL)


if __name__ == "__main__":
    main()
