"""
直播观察者 — 自动定位微信窗口 + 评论区监控 + 冲突预警 + 视觉审计
"""

import json
import time
import os
import logging
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import easyocr

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
#  配置
CHAT_INTERVAL = 20          # 评论区截图间隔(秒)
PANORAMA_INTERVAL = 120     # 全景截图间隔(秒)
CONFLICT_WINDOW = 180       # 冲突检测滑动窗口(秒, 3min)
CHANGE_TIMEOUT = 60         # 画面静止告警阈值(秒)
CHANGE_THRESHOLD = 5.0      # 画面差异阈值

_SCRIPT_DIR = Path(__file__).parent.resolve()
CONFLICT_KEYWORDS = ["哈哈", "互动", "吵架", "有趣"]
CHAT_LOG = str(_SCRIPT_DIR.parent / "05-小桃案例" / "live_data.jsonl")
FRAME_DIR = str(_SCRIPT_DIR.parent / "06-存档中心" / "temp_frames")

#  直播画面区域相对比例 (基于微信窗口内部)
#  左: 直播画面 ≈ 70% 宽度
#  右: 评论区 ≈ 30% 宽度
LIVE_RATIO = (0.0, 0.0, 0.68, 1.0)   # (left, top, width, height) 相对窗口
CHAT_RATIO = (0.68, 0.0, 0.32, 1.0)
# ═══════════════════════════════════════════════════════════


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


# ── 窗口定位 ──────────────────────────────────────────────

def find_wechat_window():
    """查找标题含 '微信' 的窗口, 返回 (left, top, width, height)."""
    wins = [w for w in gw.getAllWindows() if "微信" in w.title and w.width > 100]
    if not wins:
        log.warning("未找到微信窗口")
        return None
    # 取最大窗口
    win = max(wins, key=lambda w: w.width * w.height)
    if win.isMinimized:
        win.restore()
        time.sleep(0.5)
    win.activate()
    time.sleep(0.3)
    box = (win.left, win.top, win.width, win.height)
    log.info("微信窗口: title=%s  rect=%s", win.title, box)
    return box


def region_from_ratio(win_box, ratio):
    """根据窗口坐标 + 比例计算子区域."""
    l, t, w, h = win_box
    rl, rt, rw, rh = ratio
    return (l + int(w * rl), t + int(h * rt), int(w * rw), int(h * rh))


# ── OCR + 存储 ────────────────────────────────────────────

def ocr_region(reader, region, tag=""):
    """截取区域 → OCR → 返回文字列表."""
    try:
        img = pyautogui.screenshot(region=region)
    except Exception:
        log.exception("截图失败 %s", tag)
        return []
    tmp = f"._ocr_{tag}.png"
    img.save(tmp)
    results = reader.readtext(tmp)
    os.remove(tmp)
    return [r[1] for r in results]


def append_jsonl(path, entry):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── 冲突感强度检测 ────────────────────────────────────────

def check_conflict_intensity(now):
    """读最近 CONFLICT_WINDOW 秒的 jsonl, 统计冲突关键词频次."""
    if not Path(CHAT_LOG).exists():
        return 0, {}

    cutoff = now - CONFLICT_WINDOW
    counts = {kw: 0 for kw in CONFLICT_KEYWORDS}
    total = 0

    try:
        with open(CHAT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("timestamp", 0) < cutoff:
                    continue
                texts = "".join(entry.get("texts", []))
                for kw in CONFLICT_KEYWORDS:
                    c = texts.count(kw)
                    if c:
                        counts[kw] += c
                        total += c
    except OSError:
        pass

    return total, dict(sorted(counts.items(), key=lambda x: -x[1]))


# ── 视觉审计评分 ──────────────────────────────────────────

def audit_visual_style(frame_bgr: np.ndarray) -> dict:
    """分析亮度、对比度、绿色占比. 返回评分."""
    h, w = frame_bgr.shape[:2]
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    brightness = float(gray.mean())
    contrast = float(gray.std())

    # 绿色像素占比 (HSV: H ~35~85)
    green_mask = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))
    green_ratio = float(cv2.countNonZero(green_mask)) / (h * w)

    # 灰度直方图平坦度 (越集中说明色调单一)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist = hist / hist.sum() if hist.sum() > 0 else hist
    hist_entropy = -np.sum(hist * np.log(hist + 1e-10))

    issues = []
    if brightness < 60:
        issues.append("画面过暗")
    elif brightness > 200:
        issues.append("画面过曝")
    if contrast < 30:
        issues.append("对比度偏低, 画面发灰")
    if green_ratio > 0.5:
        issues.append("绿色占比过高, 植被背景过重")

    score = 100
    if brightness < 60 or brightness > 200:
        score -= 20
    if contrast < 30:
        score -= 15
    if green_ratio > 0.5:
        score -= 10
    if hist_entropy < 4.0:
        score -= 10  # 色调单一

    return {
        "score": max(0, score),
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "green_ratio": round(green_ratio, 3),
        "issues": issues,
    }


def print_visual_advice(result: dict):
    """根据审计结果打印优化建议."""
    if result["score"] >= 80:
        return
    issues = result["issues"]
    brightness = result["brightness"]
    contrast = result["contrast"]
    green = result["green_ratio"]

    if not issues and result["score"] >= 70:
        return

    if brightness < 60:
        print(f"\n🔴 [视觉优化] 画面亮度 {brightness}, 建议增加暖色补光")
    if contrast < 30:
        print(f"\n🔴 [视觉优化] 对比度 {contrast}, 画面发灰, 建议调整精致姐站位, 增加布景层次")
    if green > 0.5:
        print(f"\n🔴 [视觉优化] 绿色占比 {green:.1%}, 背景植被过重, 建议调整机位")
    if brightness < 60 and contrast < 30:
        print(f"\n🔴 [视觉优化] 画面色调偏冷, 建议增加暖色补光, 调整精致姐站位")


# ── 变化检测 ──────────────────────────────────────────────

def frame_diff(prev, curr) -> float:
    if prev is None:
        return 999.0
    diff = cv2.absdiff(prev, curr)
    return float(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY).mean())


# ── 主循环 ────────────────────────────────────────────────

def main():
    ensure_dir(FRAME_DIR)
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False)

    # 等待窗口出现
    win_box = None
    while win_box is None:
        win_box = find_wechat_window()
        if win_box is None:
            log.info("等待微信窗口... (5s 后重试)")
            time.sleep(5)

    chat_region = region_from_ratio(win_box, CHAT_RATIO)
    live_region = region_from_ratio(win_box, LIVE_RATIO)
    log.info("评论区区域: %s  直播画面区域: %s", chat_region, live_region)

    prev_frame = None
    quiet_cycles = 0
    quiet_limit = CHANGE_TIMEOUT // CHAT_INTERVAL
    last_pano = 0

    # 冲突检测历史 (记录上次总量, 判断趋势)
    prev_conflict_total = 0
    prev_conflict_time = 0

    while True:
        now = time.time()

        # ── 评论区 OCR ──
        texts = ocr_region(reader, chat_region, "chat")
        entry = {
            "timestamp": now,
            "time": datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
            "texts": texts,
            "ocr_count": len(texts),
        }
        append_jsonl(CHAT_LOG, entry)
        log.info("[chat] %d 段文字", len(texts))

        # ── 直播画面截图 + 视觉审计 + 变化检测 ──
        try:
            live_img = pyautogui.screenshot(region=live_region)
            live_bgr = cv2.cvtColor(np.array(live_img), cv2.COLOR_RGB2BGR)
        except Exception:
            log.exception("直播画面截图失败")
            live_bgr = None

        if live_bgr is not None:
            # 视觉审计
            va = audit_visual_style(live_bgr)
            print_visual_advice(va)

            # 变化检测
            diff = frame_diff(prev_frame, live_bgr)
            prev_frame = live_bgr
            if diff < CHANGE_THRESHOLD:
                quiet_cycles += 1
                if quiet_cycles >= quiet_limit:
                    log.warning("⚠️  画面静止 %ds, 可能断流!", quiet_cycles * CHAT_INTERVAL)
            else:
                quiet_cycles = 0

        # ── 冲突预警 ──
        total, kw_counts = check_conflict_intensity(now)
        if prev_conflict_time > 0 and (now - prev_conflict_time) >= CONFLICT_WINDOW / 2:
            if total < prev_conflict_total * 0.5 and prev_conflict_total > 5:
                print('\n⚠️ [警告] 直播间气氛变淡, 建议触发"海燕"人设冲突')
        prev_conflict_total = total
        prev_conflict_time = now

        # ── 全景截图 ──
        if now - last_pano >= PANORAMA_INTERVAL:
            try:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pyautogui.screenshot().save(f"{FRAME_DIR}/panorama_{stamp}.png")
                log.info("全景截图已保存")
            except Exception:
                log.exception("全景截图失败")
            last_pano = now

        time.sleep(CHAT_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("观察者已停止")
