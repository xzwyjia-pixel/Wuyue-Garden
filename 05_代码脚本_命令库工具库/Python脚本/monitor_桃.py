"""
monitor_桃.py — 大山里的小桃直播间监控
截图评论区 → 关键词识别 → 全景 → 视觉人设比对
"""

import json
import time
import os
import difflib
import logging
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import easyocr
import ctypes
from ctypes import wintypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

_SCRIPT_DIR = Path(__file__).parent.resolve()

# ═══════════════════════════════════════════════════════════
# 坐标配置
CHAT_REGION = (1700, 700, 400, 500)   # 评论区 (left, top, width, height)
PANORAMA_DIR = str(_SCRIPT_DIR.parent / "06-存档中心" / "temp_frames")
CHAT_INTERVAL = 30                    # 评论区 OCR 间隔(秒)
PANORAMA_INTERVAL = 300               # 全景截图间隔(秒, 5min)
KEYWORDS = ["火", "灶", "想吃", "辛苦", "多少钱", "快递", "回购", "下单", "小桃", "怎么卖", "真香",
            "好吃", "咸了", "油少", "妈妈", "年轻", "韭菜", "放点水", "回购"]
TRIGGER_WORDS = KEYWORDS
JSONL_PATH = "live_data_tao.jsonl"
# ═══════════════════════════════════════════════════════════


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


# ── 窗口定位 ──────────────────────────────────────────────

def find_right_browser():
    """扫右侧浏览器/微信窗口, 返回窗口区域."""
    candidates = []
    for w in gw.getAllWindows():
        if w.width < 200 or w.height < 200:
            continue
        # 优先标题含"微信"或"Chrome"或"Edge"的窗口
        title_lower = w.title.lower()
        for kw in ["微信", "chrome", "edge", "firefox", "browser", "直播"]:
            if kw in title_lower:
                candidates.append(w)
                break
    if candidates:
        win = max(candidates, key=lambda x: x.width * x.height)
        if win.isMinimized:
            win.restore()
            time.sleep(0.5)
        log.info("检测到浏览器窗口: %s  (%d×%d)", win.title, win.width, win.height)
        return (win.left, win.top, win.width, win.height)
    log.warning("未发现浏览器窗口, 使用默认坐标")
    return None


# ── 窗口置顶 ──────────────────────────────────────────────

def pin_window(hwnd: int):
    """通过 Windows SetWindowPos 将窗口置顶."""
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    ctypes.windll.user32.SetWindowPos(
        wintypes.HWND(hwnd), HWND_TOPMOST,
        0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
    )


def find_and_pin():
    """找直播间窗口并置顶, 返回区域."""
    box = find_right_browser()
    if box:
        # 找匹配的 pygetwindow 对象
        l, t, w, h = box
        for win in gw.getAllWindows():
            if (win.left, win.top, win.width, win.height) == (l, t, w, h):
                try:
                    pin_window(win._hWnd)
                    log.info("窗口已置顶: %s", win.title)
                except Exception:
                    log.exception("置顶失败")
                break
    return box


# ── OCR + 存储 ────────────────────────────────────────────

def ocr_region(reader, region, tag=""):
    """截图区域 → CLAHE 增强对比度 → OCR → 文字列表."""
    try:
        img = pyautogui.screenshot(region=region)
    except Exception:
        log.exception("截图失败 %s", tag)
        return []
    # CLAHE 自适应对比度增强 (低对比度评论区文字提升明显)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_cv)
    tmp = f"._ocr_{tag}_{int(time.time())}.png"
    cv2.imwrite(tmp, enhanced)
    results = reader.readtext(tmp)
    os.remove(tmp)
    return [r[1] for r in results]


def append_jsonl(path, entry):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False,
                          default=lambda x: float(x) if hasattr(x, 'item') else x) + "\n")


# ── 关键词检测 (含模糊 + 纠错匹配) ─────────────────────────

FUZZY_CHARS = {"桃", "灶", "火", "姐", "香"}  # 单字模糊命中
# OCR 易错词模糊映射: (目标词, {核心纠错字集})
FUZZY_TARGETS = [
    ("小桃", {"桃", "挑", "眺", "逃", "跳"}),
    ("好吃", {"好", "吃"}),
]


def fuzzy_match(text: str) -> list[str]:
    """对 OCR 文本做模糊纠错匹配, 返回命中的目标词."""
    hits = []
    for target, core_chars in FUZZY_TARGETS:
        # 核心字命中
        if any(c in text for c in core_chars):
            # 用 difflib 确认相似度 > 70%
            for word in text.split():
                ratio = difflib.SequenceMatcher(None, target, word).ratio()
                if ratio >= 0.7:
                    hits.append(f"{target}(模糊:{word})")
                    break
            else:
                # 即使没分词匹配, 含核心字也算软命中
                hits.append(f"{target}(含字)")
    return hits


def check_keywords(texts, keywords):
    """返回命中的关键词 + 模糊单字 + 纠错匹配."""
    full = "".join(texts)
    hits = [kw for kw in keywords if kw in full]
    fuzzy = [c for c in FUZZY_CHARS if c in full and c not in hits]
    fuzzy += fuzzy_match(full)
    return hits + fuzzy


# ── 人设 Triage 视觉比对 ──────────────────────────────────

KITCHEN_AUTHENTICITY_PARAMS = {
    "brightness_low": 40,      # 过低→昏暗
    "brightness_high": 200,    # 过高→过曝
    "contrast_min": 35,        # 对比度下限
    "warmth_min": 20,          # 暖色占比下限(红色/橙色区域)
    "green_max": 0.4,          # 绿色占比上限(田野/植被)
    "detail_min": 30,          # 细节丰富度(边缘检测均值)
    "clutter_max": 0.3,        # 杂乱度上限(颜色种类熵)
}


def triage_visual_style(frame_bgr: np.ndarray) -> dict:
    """
    视觉人设比对。
    判断画面风格接近"大山里的小桃"还是"清晨烟火小厨"。
    返回评分 + 推测 + 改善建议。
    """
    h, w = frame_bgr.shape[:2]
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    # ── 基础指标 ──
    brightness = float(gray.mean())
    contrast = float(gray.std())

    # 暖色占比 (H: 0-25 红/橙区)
    warm_mask = cv2.inRange(hsv, (0, 30, 30), (25, 255, 255))
    warm_ratio = float(cv2.countNonZero(warm_mask)) / (h * w)

    # 绿色占比 (H: 35-85 绿区)
    green_mask = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))
    green_ratio = float(cv2.countNonZero(green_mask)) / (h * w)

    # 边缘细节 (拉普拉斯)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    detail = float(laplacian.std())

    # 颜色丰富度 (HSV 直方图熵)
    h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180]).flatten()
    h_hist = h_hist / h_hist.sum() if h_hist.sum() > 0 else h_hist
    color_entropy = float(-np.sum(h_hist * np.log(h_hist + 1e-10)))

    # ── "一桌菜" 视觉热区: 画面中心下半部 ──
    # 取画面下方 1/3 区域、中心 60% 宽度
    crop_top = int(h * 0.66)
    crop_bot = h
    crop_left = int(w * 0.2)
    crop_right = int(w * 0.8)
    food_zone = hsv[crop_top:crop_bot, crop_left:crop_right]
    if food_zone.size > 0:
        # 饱和度均值 (S 通道)
        sat_mean = float(cv2.mean(food_zone)[1])
        # 红色高饱和像素 (H:0-10, 170-180 红区 + S>100)
        red_mask = cv2.inRange(food_zone, (0, 100, 30), (10, 255, 255))
        red2_mask = cv2.inRange(food_zone, (170, 100, 30), (180, 255, 255))
        red_sat_ratio = float(cv2.countNonZero(red_mask) + cv2.countNonZero(red2_mask)) / food_zone.size
        # 绿色高饱和像素 (H:35-85, S>100)
        green_sat_mask = cv2.inRange(food_zone, (35, 100, 30), (85, 255, 255))
        green_sat_ratio = float(cv2.countNonZero(green_sat_mask)) / food_zone.size
    else:
        sat_mean = 0.0
        red_sat_ratio = 0.0
        green_sat_ratio = 0.0

    # ── 风格推测 ──
    score_authentic = 0
    score_staged = 0
    clues = []

    # 灶台真实感线索: 暖色居中 + 细节丰富 + 绿色低
    if brightness > 60:
        score_authentic += 10
    if contrast > 35:
        score_authentic += 15
    else:
        score_staged += 10
        clues.append("对比度偏低, 可能道具布景缺少材质质感")

    if warm_ratio > 0.15:
        score_authentic += 15
        clues.append("暖色充足, 疑似真实灶台火光/油烟灯光")
    else:
        score_staged += 10
        clues.append("暖色不足, 缺少厨房烟火气的暖色调")

    if green_ratio > KITCHEN_AUTHENTICITY_PARAMS["green_max"]:
        score_staged += 15
        clues.append(f"绿色占比{green_ratio:.1%}, 野外/植被背景, 非厨房场景")
    else:
        score_authentic += 10
        clues.append("绿色占比低, 符合室内厨房场景")

    if detail > KITCHEN_AUTHENTICITY_PARAMS["detail_min"]:
        score_authentic += 15
        clues.append("纹理细节丰富, 真实灶台应有材质颗粒感")
    else:
        score_staged += 10
        clues.append("纹理平淡, 可能存在道具感或磨皮滤镜")

    if color_entropy > 4.5:
        score_authentic += 10
        clues.append("颜色层次丰富, 食材/厨具自然色彩分布")
    else:
        score_staged += 10
        clues.append("色调单一, 可能统一滤镜或单调布景")

    # ── "一桌菜" 食欲诱导力 ──
    food_appeal = ""
    if sat_mean > 50:
        score_authentic += 15
        if red_sat_ratio > 0.05 or green_sat_ratio > 0.08:
            food_appeal = "食欲诱导力强，具备高转化潜质"
            clues.append(f"食物区饱和度{sat_mean:.0f}, 红椒/绿菜高饱和 → {food_appeal}")

    # ── 总判断 ──
    diff = score_authentic - score_staged
    if diff >= 20:
        verdict = "倾向真实厨房场景"
        suggestion = "保持现状, 真实感是高转化武器"
    elif diff >= -10:
        verdict = "半真半道具, 观众可能察觉"
        suggestion = "增加真实食材/厨具的特写, 去掉抛光滤镜, 让灶台油光自然"
    else:
        verdict = "道具感偏重, 缺乏烟火气"
        suggestion = "参考清晨烟火小厨: 用真实切菜/下锅画面替代摆拍, 暖色补光打亮食物"

    return {
        "score_authentic": score_authentic,
        "score_staged": score_staged,
        "diff": diff,
        "verdict": verdict,
        "suggestion": suggestion,
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "warm_ratio": round(warm_ratio, 3),
        "green_ratio": round(green_ratio, 3),
        "detail": round(detail, 1),
        "color_entropy": round(color_entropy, 2),
        "food_saturation": round(sat_mean, 1),
        "food_appeal": food_appeal,
        "clues": clues,
    }


def print_triage_report(t: dict):
    sep = "─" * 50
    print(f"\n{' 视觉人设 Triage 报告 ':=^50}")
    print(f"  真实感评分: {t['score_authentic']}  vs  道具感评分: {t['score_staged']}")
    print(f"  偏差值:     {t['diff']:+d}")
    print(f"  判断:       {t['verdict']}")
    print(sep)
    print(f"  亮度 {t['brightness']}  对比度 {t['contrast']}  暖色 {t['warm_ratio']:.0%}")
    print(f"  绿色 {t['green_ratio']:.0%}  细节 {t['detail']}  色彩熵 {t['color_entropy']}")
    if t.get('food_appeal'):
        print(f"  食欲诱导:  {t['food_appeal']}")
    if t['clues']:
        for c in t['clues']:
            print(f"  · {c}")
    print(sep)
    print(f"  💡 {t['suggestion']}")
    print("=" * 50)


# ── 诊断图 ────────────────────────────────────────────────

def save_debug_crop(full_bgr: np.ndarray, chat_region: tuple):
    """在全景图上标注评论区 + 食物热区, 保存 debug_crop.jpg."""
    vis = full_bgr.copy()
    h, w = vis.shape[:2]

    # 评论区矩形 (屏幕坐标 → 图像坐标)
    cx, cy, cw, ch = chat_region
    cv2.rectangle(vis, (cx, cy), (cx + cw, cy + ch), (0, 255, 0), 3)
    cv2.putText(vis, "CHAT", (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    # 食物热区 (画面中心下半部)
    f_left = int(w * 0.2)
    f_right = int(w * 0.8)
    f_top = int(h * 0.66)
    f_bot = h
    cv2.rectangle(vis, (f_left, f_top), (f_right, f_bot), (0, 0, 255), 3)
    cv2.putText(vis, "FOOD", (f_left, f_top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    cv2.imwrite("debug_crop.jpg", vis)


# ── 变化检测 ──────────────────────────────────────────────

def frame_diff(prev, curr) -> float:
    if prev is None:
        return 999.0
    diff = cv2.absdiff(prev, curr)
    return float(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY).mean())


# ── 主循环 ────────────────────────────────────────────────

def main():
    ensure_dir(PANORAMA_DIR)
    reader = easyocr.Reader(["ch_sim", "en"], gpu=False)

    # 探测右侧浏览器并置顶
    win_box = find_and_pin()

    chat_region = CHAT_REGION
    if win_box:
        # 如果找到了窗口, 用窗口右下方作为评论区
        l, t, w, h = win_box
        chat_region = (l + int(w * 0.65), t + int(h * 0.6), int(w * 0.32), int(h * 0.35))
        log.info("自适应评论区: %s", chat_region)

    log.info("== 监控启动  区域=%s  间隔=%ss  全景=%ss ==", chat_region, CHAT_INTERVAL, PANORAMA_INTERVAL)

    buffer = []
    prev_frame = None
    quiet_cycles = 0
    quiet_limit = 3
    last_pano = 0
    triage_interval = 5       # 每 N 轮做一次视觉比对
    triage_counter = 0
    repin_cycle = 10    # 每 N 轮重新置顶一次, 防用户拖拽

    while True:
        now = time.time()

        # 定期重新置顶
        triage_counter += 1
        if triage_counter % repin_cycle == 0:
            find_and_pin()

        # ── 评论区 OCR ──
        texts = ocr_region(reader, chat_region, "tao")
        hits = check_keywords(texts, TRIGGER_WORDS)
        entry = {
            "timestamp": now,
            "time": datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
            "texts": texts,
            "text_count": len(texts),
            "keyword_hits": hits,
        }
        append_jsonl(JSONL_PATH, entry)
        buffer.append(entry)

        # 打印关键词命中
        if hits:
            print(f"[{entry['time']}] 🎯 命中: {' '.join(hits)}")
        log.info("[OCR] %d 段文字  命中=%s", len(texts), hits)

        # ── 全景 + 视觉 Triage ──
        if now - last_pano >= PANORAMA_INTERVAL:
            try:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                full = pyautogui.screenshot()
                full_path = f"{PANORAMA_DIR}/tao_pano_{stamp}.png"
                full.save(full_path)
                log.info("全景 → %s", full_path)

                # 用全景做视觉人设比对
                full_bgr = cv2.cvtColor(np.array(full), cv2.COLOR_RGB2BGR)
                triage = triage_visual_style(full_bgr)
                # 存报告
                triage["timestamp"] = now
                triage["image"] = full_path
                append_jsonl("triage_log.jsonl", triage)
                print_triage_report(triage)

                # 变化检测
                diff = frame_diff(prev_frame, full_bgr)
                prev_frame = full_bgr
                if diff < 5.0:
                    quiet_cycles += 1
                    if quiet_cycles >= quiet_limit:
                        log.warning("⚠️ 画面静止, 可能断流")
                else:
                    quiet_cycles = 0

            except Exception:
                log.exception("全景/比对失败")
            last_pano = now

        # ── 定期 Triage (每 5 轮) ──
        if triage_counter % triage_interval == 0 and buffer:
            print(f"\n  [轮询 Triage] 已采集 {len(buffer)} 条数据")

        time.sleep(CHAT_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("监控已停止")
