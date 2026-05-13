"""
monitor_dual.py — 双平台直播监控 v2.1
视频号(左下) + 抖音(右侧)
启动自动校准评论区坐标 → OCR+Triage → 输出 jsonl
"""
import sys, os, time, json, threading
from pathlib import Path
from datetime import datetime
import mss, mss.tools
import cv2, numpy as np
import tempfile
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# === CONFIG ===
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(HAAR_PATH)

MONITOR_INTERVAL = 30       # OCR间隔(秒)
TRIAGE_INTERVAL = 300       # 视觉评分间隔(秒)

# 默认区域 (基于 1920x1080, 视频号左下, 抖音右侧)
# auto_calibrate() 会在启动时亮度扫描修正
DEFAULT_REGIONS = {
    "susu": {
        "chat_region": (640, 500, 310, 500),
        "video_region": (0, 478, 640, 600),
        "scan_area": (0, 400, 960, 680),     # brightness scan area
        "chat_x_range": (500, 950),           # where chat panel likely starts
    },
    "douyin": {
        "chat_region": (1500, 50, 400, 980),
        "video_region": (960, 0, 540, 1030),
        "scan_area": (960, 0, 960, 1080),
        "chat_x_range": (1300, 1880),
    }
}

def build_platforms(base_dir):
    b = Path(base_dir)
    return {
        "susu": {
            "name": "清晨烟火小厨",
            "alias": "SuSu",
            "data_dir": b,
            "frame_dir": Path("E:/MyCodeProjects/06-存档中心/temp_frames/SuSu"),
            "chat_region": DEFAULT_REGIONS["susu"]["chat_region"],
            "video_region": DEFAULT_REGIONS["susu"]["video_region"],
            "scan_area": DEFAULT_REGIONS["susu"]["scan_area"],
            "chat_x_range": DEFAULT_REGIONS["susu"]["chat_x_range"],
            "keywords": ["苏苏", "丝瓜", "菜", "好吃", "香", "怎么做", "关注", "点赞", "清晨", "烟火"],
            "fuzzy_chars": ["苏", "菜", "吃", "香"],
        },
        "douyin": {
            "name": "抖音直播间",
            "alias": "DouYin",
            "data_dir": b,
            "frame_dir": Path("E:/MyCodeProjects/06-存档中心/temp_frames/DouYin"),
            "chat_region": DEFAULT_REGIONS["douyin"]["chat_region"],
            "video_region": DEFAULT_REGIONS["douyin"]["video_region"],
            "scan_area": DEFAULT_REGIONS["douyin"]["scan_area"],
            "chat_x_range": DEFAULT_REGIONS["douyin"]["chat_x_range"],
            "keywords": ["好吃", "回购", "下单", "关注", "分享", "清晨", "烟火"],
            "fuzzy_chars": ["吃", "香"],
        }
    }

# === AUTO CALIBRATION ===
def auto_calibrate(sct, plat):
    """亮度扫描自动检测评论区坐标, 更新 plat dict"""
    scan_x, scan_y, scan_w, scan_h = plat["scan_area"]
    frame = np.array(sct.grab(sct.monitors[1]))
    bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    h, w = bgr.shape[:2]

    # clip scan area to screen
    scan_x = max(0, min(scan_x, w - 10))
    scan_y = max(0, min(scan_y, h - 10))
    scan_w = min(scan_w, w - scan_x)
    scan_h = min(scan_h, h - scan_y)

    roi = bgr[scan_y:scan_y+scan_h, scan_x:scan_x+scan_w]
    col_avg = roi.mean(axis=0).mean(axis=1)  # brightness per column in scan area

    x_min, x_max = plat["chat_x_range"]
    rel_min = max(0, x_min - scan_x)
    rel_max = min(len(col_avg), x_max - scan_x)

    # Find sharpest brightness drop in chat range -> chat panel left edge
    if rel_max > rel_min + 5:
        segment = col_avg[rel_min:rel_max]
        diffs = np.diff(segment)
        # negative diffs = brightness drops (dark panel border)
        drop_idx = np.argmin(diffs)
        chat_left = scan_x + rel_min + int(drop_idx)
        # chat panel width ~300-450px
        chat_right = min(chat_left + 450, w - 20)
        chat_w = chat_right - chat_left
        chat_h = scan_h - 60
        chat_y = scan_y + 30

        plat["chat_region"] = (chat_left, chat_y, chat_w, chat_h)
        # video region = everything left of chat panel in this area
        video_x = scan_x
        video_y = scan_y
        video_w = chat_left - scan_x
        video_h = scan_h
        if video_w > 100 and video_h > 100:
            plat["video_region"] = (video_x, video_y, video_w, video_h)

        print(f"  [校准] chat_region={plat['chat_region']}  video_region={plat['video_region']}")
    else:
        print(f"  [校准] 亮度扫描无结果, 用默认坐标")

# === FILTER ===
UI_NOISE = {"发四", "嫩瞎", "Ux", "士袄", "孑鸡", "聊-聊", "禁止",
             "充值", "直播推荐", "关注", "分享", "点赞",
             "与大家互动一下", "规行为请及时投诉", "进入直播间"}
TIME_PATTERN = set("0123456789:-. ")

def is_noise(text):
    if len(text) < 2:
        return True
    if text in UI_NOISE:
        return True
    time_chars = sum(1 for c in text if c in TIME_PATTERN)
    if time_chars > len(text) * 0.4 and any(c.isdigit() for c in text):
        return True
    return False

# === OCR ===
_reader = None
def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    return _reader

def ocr_region(img_bgr, region):
    x, y, w, h = region
    roi = img_bgr[y:y+h, x:x+w]
    if roi.size == 0 or roi.shape[0] < 10 or roi.shape[1] < 10:
        return []
    tmp = os.path.join(tempfile.gettempdir(), f'_ocr_{int(time.time()*1000)}.png')
    cv2.imwrite(tmp, roi)
    try:
        reader = get_reader()
        results = reader.readtext(tmp)
        texts = [t for _, t, c in results if c > 0.3 and not is_noise(t)]
        return texts
    finally:
        try: os.unlink(tmp)
        except: pass

# === TRIAGE ===
def triage_frame(img_rgb):
    gray = np.mean(img_rgb, axis=2)
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    h_chan, s_chan, v_chan = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]

    brightness = float(np.mean(v_chan))
    contrast = float(np.std(gray))
    warm = float(((h_chan < 25) | (h_chan > 160)).mean())
    green = float(((h_chan > 35) & (h_chan < 85)).mean())
    detail = float(cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F).std())

    hist = cv2.calcHist([h_chan.astype(np.uint8)], [0], None, [180], [0, 180])
    hist_norm = hist / hist.sum()
    entropy = float(-np.sum(hist_norm * np.log2(hist_norm + 1e-10)))

    hf, wf = img_rgb.shape[:2]
    food = hsv[int(hf*0.70):int(hf*0.95), int(wf*0.20):int(wf*0.80)]
    food_sat = float(food[:,:,1].mean()) if food.size > 0 else 0

    left = v_chan[:, :wf//3]
    center = v_chan[:, wf//3:2*wf//3]
    right = v_chan[:, 2*wf//3:]
    left_b = float(left.mean())
    center_b = float(center.mean())
    right_b = float(right.mean())

    faces = face_cascade.detectMultiScale(
        gray.astype(np.uint8), scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    face_brightness = []
    for (fx, fy, fw, fh) in faces:
        face_roi = v_chan[fy:fy+fh, fx:fx+fw]
        face_brightness.append(float(face_roi.mean()))
    avg_face_b = float(np.mean(face_brightness)) if face_brightness else 0

    score_a = 0
    if brightness > 60: score_a += 10
    if contrast > 35: score_a += 15
    if warm > 0.15: score_a += 15
    elif warm > 0.10: score_a += 8
    if green < 0.40: score_a += 10
    if detail > 30: score_a += 15
    if entropy > 4.5: score_a += 10
    elif entropy > 3.0: score_a += 5
    if food_sat > 50: score_a += 15
    elif food_sat > 30: score_a += 8
    elif food_sat > 20: score_a += 3
    score_a = min(score_a, 85)

    score_s = 0
    if contrast <= 35: score_s += 10
    if warm <= 0.15: score_s += 10
    if green > 0.40: score_s += 15
    if detail <= 30: score_s += 10
    if entropy <= 4.5: score_s += 10
    score_s = min(score_s, 100)

    return {
        "brightness": round(brightness, 1),
        "contrast": round(contrast, 1),
        "warm_ratio": round(warm, 3),
        "green_ratio": round(green, 3),
        "detail": round(detail, 1),
        "color_entropy": round(entropy, 2),
        "food_saturation": round(food_sat, 1),
        "zone_brightness": {
            "left": round(left_b, 1),
            "center": round(center_b, 1),
            "right": round(right_b, 1),
            "left_right_diff": round(right_b - left_b, 1),
        },
        "face": {
            "count": len(faces),
            "avg_brightness": round(avg_face_b, 1),
        },
        "score_authentic": score_a,
        "score_staged": score_s,
        "diff": score_a - score_s,
    }

# === MONITOR THREAD ===
class PlatformMonitor:
    def __init__(self, plat):
        self.cfg = plat
        self.data_dir = plat["data_dir"]
        self.frame_dir = plat["frame_dir"]
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.frame_dir.mkdir(parents=True, exist_ok=True)

        safe = plat["alias"]
        self.ocr_log = self.data_dir / f"live_data_{safe}.jsonl"
        self.triage_log = self.data_dir / f"triage_log_{safe}.jsonl"
        self.status_log = self.data_dir / f"monitor_{safe}.log"

        self.last_triage = 0
        self.row_count = 0
        self.alert_brightness = None
        self.prev_food_sat = 0

    def log(self, msg):
        line = f"[{time.strftime('%H:%M:%S')}] [{self.cfg['alias']}] {msg}"
        print(line)
        with open(self.status_log, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def check_alerts(self, triage):
        alerts = []
        b = triage["brightness"]
        if self.alert_brightness is not None:
            diff = abs(b - self.alert_brightness)
            if diff > 50:
                alerts.append(f"亮度异常变化: {self.alert_brightness:.0f}->{b:.0f}")
        self.alert_brightness = b

        if triage["warm_ratio"] < 0.05:
            alerts.append("暖色不足(<5%) - 建议灶火入镜")
        if triage["food_saturation"] < 25:
            alerts.append(f"食物饱和度偏低({triage['food_saturation']:.0f}) - 建议近拍")
        curr_fs = triage["food_saturation"]
        if self.prev_food_sat > 0 and curr_fs > self.prev_food_sat * 1.5 and curr_fs > 30:
            alerts.append(f"食物展示检出! 饱和度{self.prev_food_sat:.0f}->{curr_fs:.0f} - 建议保持近拍")
        self.prev_food_sat = curr_fs

        zb = triage.get("zone_brightness", {})
        if zb.get("left_right_diff", 0) > 30:
            alerts.append(f"左右亮度差({zb['left_right_diff']:.0f}) - 建议调整机位或补充左侧光")
        return alerts

    def step(self, sct):
        now = time.time()
        monitor = sct.monitors[1]

        frame = np.array(sct.grab(monitor))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # --- OCR Chat ---
        texts = ocr_region(bgr, self.cfg["chat_region"])
        keyword_hits = []
        for t in texts:
            for kw in self.cfg["keywords"]:
                if kw in t:
                    keyword_hits.append(kw)
            for ch in self.cfg["fuzzy_chars"]:
                if ch in t:
                    keyword_hits.append(f"{ch}(含字)")

        ocr_record = {
            "timestamp": now,
            "time": datetime.now().strftime("%H:%M:%S"),
            "texts": texts,
            "text_count": len(texts),
            "keyword_hits": keyword_hits,
        }
        with open(self.ocr_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(ocr_record, ensure_ascii=False) + "\n")
        self.row_count += 1

        if texts:
            self.log(f"OCR: {texts[:3]}")

        # --- Triage ---
        alerts = []
        if now - self.last_triage > TRIAGE_INTERVAL:
            self.last_triage = now

            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pano_path = self.frame_dir / f"pano_{stamp}.png"
            self.frame_dir.mkdir(parents=True, exist_ok=True)
            saved = cv2.imwrite(str(pano_path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
            if not saved:
                self.log(f"WARN: 全景截图保存失败: {pano_path}")
            else:
                self.log(f"全景截图: {pano_path.name}")

            vx, vy, vw, vh = self.cfg["video_region"]
            video_rgb = rgb[vy:vy+vh, vx:vx+vw]
            triage = triage_frame(video_rgb)
            triage["timestamp"] = now
            triage["image"] = str(pano_path)

            with open(self.triage_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(triage, ensure_ascii=False) + "\n")

            alerts = self.check_alerts(triage)
            b = triage["brightness"]
            w = triage["warm_ratio"] * 100
            f_sat = triage["food_saturation"]
            fc = triage["face"]["count"]
            zb = triage["zone_brightness"]
            self.log(f"TRIAGE: b{b:.0f} w{w:.0f}% food{f_sat:.0f} faces{fc} zoneL{zb['left']:.0f}/C{zb['center']:.0f}/R{zb['right']:.0f} auth{triage['score_authentic']}/85")
            if alerts:
                for a in alerts:
                    self.log(f"ALERT: {a}")

        return alerts


# === MAIN ===
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="", help="data dir")
    parser.add_argument("--calibrate", action="store_true", help="run calibration")
    parser.add_argument("--auto", action="store_true", help="auto mode")
    args = parser.parse_args()

    base_dir = args.target if args.target else Path("E:/MyCodeProjects/05-参考案例/农村小琪")
    PLATFORMS = build_platforms(base_dir)

    print("=" * 44)
    print("  双平台直播监控引擎 v2.1")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  target: {base_dir}")
    print("=" * 44)

    with mss.MSS() as sct:
        # --- 自动校准 (优先级高) ---
        print("\n[校准] 亮度扫描检测评论区坐标...")
        for key, plat in PLATFORMS.items():
            auto_calibrate(sct, plat)

        # --- 交互式校准 (--calibrate 时) ---
        if args.calibrate and not args.auto:
            for key, plat in PLATFORMS.items():
                print(f"\n=== 交互校准: {plat['name']} ===")
                print("在直播间评论区发一条测试消息, 10s后扫描...")
                time.sleep(10)
                from easyocr import Reader
                all_boxes = []
                for attempt in range(8):
                    frame = np.array(sct.grab(sct.monitors[1]))
                    bgr2 = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    tmp = os.path.join(tempfile.gettempdir(), f'_cal_{int(time.time())}.png')
                    cv2.imwrite(tmp, bgr2)
                    reader = Reader(['ch_sim', 'en'], gpu=False)
                    results = reader.readtext(tmp)
                    os.unlink(tmp)
                    for box, text, conf in results:
                        if conf > 0.5 and len(text) >= 2:
                            x1, y1 = int(box[0][0]), int(box[0][1])
                            x2, y2 = int(box[2][0]), int(box[2][1])
                            all_boxes.append((x1, y1, x2, y2, text, conf))
                            print(f"  text: '{text}' @ ({x1},{y1})-({x2},{y2}) conf:{conf:.2f}")
                    time.sleep(2)
                if all_boxes:
                    last = all_boxes[-1]
                    margin = 20
                    cx = max(0, last[0] - margin)
                    cy = max(0, last[1] - margin)
                    cw = last[2] - last[0] + margin * 2
                    ch = last[3] - last[1] + margin * 2
                    print(f"  >> chat_region: ({cx}, {cy}, {cw}, {ch})")
                    plat["chat_region"] = (cx, cy, cw, ch)

        # --- Start monitoring ---
        monitors = []
        for key, plat in PLATFORMS.items():
            m = PlatformMonitor(plat)
            monitors.append(m)
            m.log(f"monitor start | chat={plat['chat_region']} video={plat['video_region']}")

        # --- 首次立即执行一次 Triage (即时反馈) ---
        print("\n[监控] 首次视觉分析...")
        step_start = time.time()
        for m in monitors:
            m.last_triage = 0  # 确保首次立即触发
            # 强制首次 step 执行 triage
            m.step(sct)
        print(f"[监控] 首次分析完成 ({time.time()-step_start:.1f}s)")
        print(f"[监控] OCR 每 {MONITOR_INTERVAL}s | Triage 每 {TRIAGE_INTERVAL}s | Ctrl+C 停止")
        print("---")

        try:
            while True:
                all_alerts = []
                for m in monitors:
                    alerts = m.step(sct)
                    all_alerts.extend(alerts)
                time.sleep(MONITOR_INTERVAL)
        except KeyboardInterrupt:
            print("\n[监控] 停止")

if __name__ == "__main__":
    main()
