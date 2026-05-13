"""
monitor_engine.py — 可配置直播监控引擎
通过 profile dict 注入参数, 不依赖硬编码
"""
import json, time, os, difflib, logging, ctypes, warnings, tempfile
from datetime import datetime
from pathlib import Path
from ctypes import wintypes

import cv2, numpy as np, pyautogui, pygetwindow as gw, easyocr

warnings.filterwarnings("ignore")

# 强制使用脚本所在目录为根, 避免 CWD 漂移
_BASE = Path(__file__).parent.resolve()
_ROOT = _BASE.parent  # MyCodeProjects root

# ── 日志系统: 文件全量, 控制台仅 WARNING+ ──────────────────
LOGDIR = _ROOT / "06-存档中心" / "logs"
LOGDIR.mkdir(parents=True, exist_ok=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

_fh = logging.FileHandler(str(LOGDIR / "audit.log"), encoding="utf-8")
_fh.setLevel(logging.INFO)
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
root_logger.addHandler(_fh)

_ch = logging.StreamHandler()
_ch.setLevel(logging.WARNING)
_ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
root_logger.addHandler(_ch)

log = logging.getLogger(__name__)


class LiveMonitorEngine:
    def __init__(self, profile: dict):
        self.profile = profile
        name = profile.get("display", "unknown")
        slug = profile.get("_slug", name.replace(" ", "_"))
        alias = profile.get("_alias", slug)

        # 从 profile 读取参数
        self.chat_region = profile.get("chat_region", (1700, 700, 400, 500))
        self.chat_interval = profile.get("chat_interval", 30)
        self.pano_interval = profile.get("pano_interval", 300)
        self.keywords = profile.get("keywords", [])
        self.conversion_keywords = set(profile.get("conversion_keywords", []))
        self.dy_keywords = set(profile.get("dy_keywords", []))
        self.wch_keywords = set(profile.get("wch_keywords", []))
        # Safe zones (product showcase center at y~42.5%, x~50%)
        self.dy_safe = (0.15, 0.75, 0.05, 0.75)
        self.wch_safe = (0.10, 0.80, 0.05, 0.80)
        # Dual-platform common denominator targets
        self.dual_sat_target = 55
        self.dual_sat_tol = 10
        self.dual_warm_target = 0.18
        self.dual_warm_tol = 0.05
        self.fuzzy_chars = set(profile.get("fuzzy_chars", []))
        self.fuzzy_targets = [(t[0], set(t[1])) for t in profile.get("fuzzy_targets", [])]
        fz = profile.get("food_zone", {"y_start": 0.66, "y_end": 1.0, "x_start": 0.2, "x_end": 0.8})
        self.food_zone = (fz["y_start"], fz["y_end"], fz["x_start"], fz["x_end"])
        self.benchmark = profile.get("benchmark", {})

        # ASCII-safe 输出路径（基于项目根，适配整理后目录结构）
        _CASE_ROOTS = {
            "fanjie": _ROOT / "04-凡姐案例",
            "xiaotao": _ROOT / "05-小桃案例",
            "susu": _ROOT / "04-宝妈直播诊断系统" / "苏苏在浙里",
        }
        case_root = _CASE_ROOTS.get(alias.lower(), _BASE)
        self.frame_dir = _ROOT / "06-存档中心" / "temp_frames" / alias
        self.live_log = str(case_root / f"live_data_{alias.lower()}.jsonl")
        self.triage_log = str(case_root / f"triage_log_{alias.lower()}.jsonl")
        self.asset_dir = _BASE / "case_assets" / alias

        self.frame_dir.mkdir(parents=True, exist_ok=True)
        self.asset_dir.mkdir(parents=True, exist_ok=True)

        self.reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
        self.buffer = []
        self.prev_frame = None
        self.quiet_cycles = 0
        self.quiet_limit = 3
        self.last_pano = 0
        self.triage_counter = 0
        self.conversion_active = False   # flag for HIGH_CONVERSION capture
        self.sat_history = []            # visual fatigue tracking
        self.fatigue_warned = False

    # ── 工具函数 ──

    def _ocr_region(self, region, tag=""):
        try:
            img = pyautogui.screenshot(region=region)
        except Exception:
            log.exception("截图失败 %s", tag)
            return []
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img_cv)
        safe = "".join(c for c in tag if ord(c) < 128) or "ocr"
        tmp = os.path.join(tempfile.gettempdir(), f"_ocr_{safe}_{int(time.time())}.png")
        cv2.imwrite(tmp, enhanced)
        if not os.path.isfile(tmp):
            log.warning("OCR temp file not written: %s", tmp)
            return []
        results = self.reader.readtext(tmp)
        time.sleep(0.1)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return [r[1] for r in results]

    def _append_jsonl(self, path, entry):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False,
                               default=lambda x: float(x) if hasattr(x, 'item') else x) + "\n")

    def _check_keywords(self, texts):
        full = "".join(texts)
        hits = [kw for kw in self.keywords if kw in full]
        fuzzy = [c for c in self.fuzzy_chars if c in full and c not in hits]
        for target, core_chars in self.fuzzy_targets:
            if any(c in full for c in core_chars):
                for word in full.split():
                    if difflib.SequenceMatcher(None, target, word).ratio() >= 0.7:
                        fuzzy.append(f"{target}(模糊)")
                        break
                else:
                    fuzzy.append(f"{target}(含字)")
        all_hits = hits + fuzzy
        conversion_hits = [h for h in all_hits if any(c in h for c in self.conversion_keywords)]
        dy_hits = [kw for kw in self.dy_keywords if kw in full]
        wch_hits = [kw for kw in self.wch_keywords if kw in full]
        return all_hits, conversion_hits, dy_hits, wch_hits

    @staticmethod
    def _count_emojis(text):
        count = 0
        for ch in text:
            cp = ord(ch)
            if 0x1F300 <= cp <= 0x1F9FF or 0x2600 <= cp <= 0x27BF:
                count += 1
        return count

    @staticmethod
    def _check_ui_occlusion(frame_bgr):
        h, w = frame_bgr.shape[:2]
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        M = cv2.moments(np.abs(lap))
        if M["m00"] < 1:
            return None
        cy_rel = (M["m01"] / M["m00"]) / h
        cx_rel = (M["m10"] / M["m00"]) / w
        in_dy = (cy_rel >= 0.70) or (cx_rel >= 0.80)
        in_wch = (cy_rel >= 0.60 and cx_rel >= 0.60)
        return {"cx_rel": round(cx_rel, 3), "cy_rel": round(cy_rel, 3),
                "in_dy_mask": in_dy, "in_wch_mask": in_wch, "occluded": in_dy or in_wch}

    @staticmethod
    def _find_and_pin():
        candidates = [w for w in gw.getAllWindows() if w.width > 200
                      and any(kw in w.title.lower() for kw in ["微信", "chrome", "edge", "直播"])]
        if not candidates:
            return None
        win = max(candidates, key=lambda x: x.width * x.height)
        if win.isMinimized:
            win.restore()
            time.sleep(0.5)
        try:
            ctypes.windll.user32.SetWindowPos(wintypes.HWND(win._hWnd), -1, 0, 0, 0, 0, 0x0003)
        except Exception:
            pass
        return (win.left, win.top, win.width, win.height)

    # ── Triage ──

    def triage(self, frame_bgr):
        h, w = frame_bgr.shape[:2]
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        brightness = float(gray.mean())
        contrast = float(gray.std())
        warm_mask = cv2.inRange(hsv, (0, 30, 30), (25, 255, 255))
        warm_ratio = float(cv2.countNonZero(warm_mask)) / (h * w)
        green_mask = cv2.inRange(hsv, (35, 30, 30), (85, 255, 255))
        green_ratio = float(cv2.countNonZero(green_mask)) / (h * w)
        detail = float(cv2.Laplacian(gray, cv2.CV_64F).std())
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180]).flatten()
        h_hist = h_hist / h_hist.sum() if h_hist.sum() > 0 else h_hist
        color_entropy = float(-np.sum(h_hist * np.log(h_hist + 1e-10)))

        # Product zone: upper-center (handheld product close-up area)
        pz = gray[int(h*0.30):int(h*0.55), int(w*0.30):int(w*0.70)]
        if pz.size > 0:
            clahe_pz = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            pz_enhanced = clahe_pz.apply(pz)
            product_detail = float(cv2.Laplacian(pz_enhanced, cv2.CV_64F).std())
        else:
            product_detail = 0.0

        ys, ye, xs, xe = self.food_zone
        fz = hsv[int(h*ys):int(h*ye), int(w*xs):int(w*xe)]
        if fz.size > 0:
            sat_mean = float(cv2.mean(fz)[1])
            red = cv2.inRange(fz, (0, 100, 30), (10, 255, 255))
            red2 = cv2.inRange(fz, (170, 100, 30), (180, 255, 255))
            red_ratio = float(cv2.countNonZero(red) + cv2.countNonZero(red2)) / fz.size
            gsat = cv2.inRange(fz, (35, 100, 30), (85, 255, 255))
            green_ratio_sat = float(cv2.countNonZero(gsat)) / fz.size
        else:
            sat_mean = red_ratio = green_ratio_sat = 0.0

        st, stol = self.dual_sat_target, self.dual_sat_tol
        wt, wtol = self.dual_warm_target, self.dual_warm_tol
        sat_ok = (st - stol) <= sat_mean <= (st + stol)
        warm_ok = (wt - wtol) <= warm_ratio <= (wt + wtol)
        score_a = sum([
            10 if brightness > 60 else 0,
            15 if contrast > 35 else 0,
            15 if warm_ok else 0,
            10 if green_ratio < 0.40 else 0,
            15 if detail > 30 else 0,
            10 if color_entropy > 4.5 else 0,
            15 if sat_ok else 0,
            10 if product_detail > 25 else 0,
        ])
        score_s = sum([
            10 if contrast <= 35 else 0,
            10 if not warm_ok else 0,
            15 if green_ratio > 0.40 else 0,
            10 if detail <= 30 else 0,
            10 if color_entropy <= 4.5 else 0,
            10 if product_detail <= 25 else 0,
        ])
        diff = score_a - score_s
        food_appeal = ""
        if sat_mean > 50 and (red_ratio > 0.05 or green_ratio_sat > 0.08):
            food_appeal = "食欲诱导力强, 具备高转化潜质"

        return {
            "score_authentic": score_a, "score_staged": score_s, "diff": diff,
            "brightness": round(brightness, 1), "contrast": round(contrast, 1),
            "warm_ratio": round(warm_ratio, 3), "green_ratio": round(green_ratio, 3),
            "detail": round(detail, 1), "color_entropy": round(color_entropy, 2),
            "food_saturation": round(sat_mean, 1), "food_appeal": food_appeal,
            "product_detail": round(product_detail, 1),
        }

    # ── 采样模式 ──

    def sample(self, rounds=6):
        """采样模式: 快速截 rounds 次(默认6次=1min), 返回平均视觉指标."""
        log.info("[采样] 开始 %d 轮快速采样...", rounds)
        metrics = []
        for i in range(rounds):
            time.sleep(10)
            try:
                img = pyautogui.screenshot()
                bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                metrics.append(self.triage(bgr))
                log.info("[采样] %d/%d  亮度=%.0f  对比=%.0f", i+1, rounds, metrics[-1]["brightness"], metrics[-1]["contrast"])
            except Exception as e:
                log.warning("[采样] 第%d轮失败: %s", i+1, e)
        if not metrics:
            return {}
        avg = {k: sum(m[k] for m in metrics) / len(metrics) for k in ["brightness", "contrast", "warm_ratio", "detail", "color_entropy"]}
        log.info("[采样] 完成  平均亮度=%.0f  暖色=%.1f%%", avg["brightness"], avg["warm_ratio"] * 100)
        return avg

    # ── 主循环 ──

    def run(self):
        name = self.profile.get("display", "unknown")
        alias = self.profile.get("_alias", name)
        log.info("== [%s] 监控启动  区域=%s  间隔=%ds ==", name, self.chat_region, self.chat_interval)
        self._find_and_pin()
        print(f"[启动] {name} (alias={alias})  区域={self.chat_region}  间隔={self.chat_interval}s")
        # One-time dual-platform position check
        pz_y, pz_x = 0.425, 0.50  # product zone center (relative)
        dy_ys, dy_ye, dy_xs, dy_xe = self.dy_safe
        wch_ys, wch_ye, wch_xs, wch_xe = self.wch_safe
        if not (dy_xs <= pz_x <= dy_xe and dy_ys <= pz_y <= dy_ye):
            print(f"  [UI预警] 产品位置在抖音可能被遮挡! (center={pz_y:.0%},{pz_x:.0%})")
        if not (wch_xs <= pz_x <= wch_xe and wch_ys <= pz_y <= wch_ye):
            print(f"  [UI预警] 产品位置在视频号可能被遮挡! (center={pz_y:.0%},{pz_x:.0%})")

        while True:
            now = time.time()
            self.triage_counter += 1

            # OCR
            texts = self._ocr_region(self.chat_region, alias[:8])
            hits, conversion_hits, dy_hits, wch_hits = self._check_keywords(texts)
            full_text = "".join(texts)
            emoji_count = self._count_emojis(full_text)
            entry = {"timestamp": now, "time": datetime.fromtimestamp(now).strftime("%H:%M:%S"),
                     "texts": texts, "text_count": len(texts), "emoji_count": emoji_count,
                     "keyword_hits": hits, "conversion_hits": conversion_hits,
                     "dy_hits": dy_hits, "wch_hits": wch_hits}
            self._append_jsonl(self.live_log, entry)

            if conversion_hits:
                self.conversion_active = True
                print(f"\n  >>> [{entry['time']}] {name} [转化意向命中]: {' '.join(conversion_hits)} <<<")
            elif hits:
                print(f"[{entry['time']}] {name} 命中: {' '.join(hits)}")

            # 0命中重校准
            if len(texts) > 5 and len(hits) == 0:
                self._find_and_pin()

            # 全景 + Triage
            if now - self.last_pano >= self.pano_interval:
                try:
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    full = pyautogui.screenshot()
                    path = str(self.frame_dir / f"pano_{stamp}.png")
                    full.save(path)
                    bgr = cv2.cvtColor(np.array(full), cv2.COLOR_RGB2BGR)
                    bright = float(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).mean())
                    if bright < 255:
                        triage = self.triage(bgr)
                        triage["timestamp"] = now
                        triage["image"] = path
                        self._append_jsonl(self.triage_log, triage)
                        self._print_triage(triage)

                        # Visual fatigue: track sat fluctuation over last 3 cycles
                        sat = triage.get("food_saturation", 0)
                        self.sat_history.append(sat)
                        if len(self.sat_history) >= 3:
                            recent = self.sat_history[-3:]
                            sat_range = max(recent) - min(recent)
                            sat_mean_val = sum(recent) / 3
                            if sat_mean_val > 0 and (sat_range / sat_mean_val) < 0.05:
                                if not self.fatigue_warned:
                                    print(f"  [警告] 画面视觉疲劳, 建议增加手部互动或改变景别 (sat波动={sat_range:.1f})")
                                    log.warning("视觉疲劳 sat波动<5%%: %s", recent)
                                    self.fatigue_warned = True
                            else:
                                self.fatigue_warned = False

                        # UI occlusion check when product is being shown
                        pd = triage.get("product_detail", 0)
                        if pd > 80:
                            occ = self._check_ui_occlusion(bgr)
                            if occ and occ["occluded"]:
                                tags = [k for k, v in [("DY", occ["in_dy_mask"]), ("WCH", occ["in_wch_mask"])] if v]
                                print(f"\n  !!! [UI 遮挡预警] 产品正被{'/'.join(tags)}组件覆盖, 请提醒主播上移手部 (重心={occ['cy_rel']:.0%},{occ['cx_rel']:.0%}) !!!")
                                log.warning("UI遮挡 product_detail=%.1f pos=(%.0f%%,%.0f%%) masks=%s", pd, occ["cy_rel"]*100, occ["cx_rel"]*100, "/".join(tags))

                        # CONVERSION_MOMENT: high product detail + recent conversion activity
                        if pd > 85 and self.conversion_active:
                            conv_path = str(self.asset_dir / f"CONVERSION_MOMENT_{stamp}.jpg")
                            full.save(conv_path)
                            print(f"  [转化时刻捕获] pd={pd} -> {conv_path}")
                            log.info("转化时刻资产保存: %s (pd=%.1f)", conv_path, pd)
                            self.conversion_active = False
                    elif bright >= 255:
                        log.warning("纯白跳过 (bright=%.0f)", bright)

                    diff = self._frame_diff(self.prev_frame, bgr)
                    self.prev_frame = bgr
                    if diff < 5:
                        self.quiet_cycles += 1
                        if self.quiet_cycles >= self.quiet_limit:
                            log.warning("画面静止, 可能断流")
                    else:
                        self.quiet_cycles = 0
                except Exception:
                    log.exception("全景失败")
                self.last_pano = now

            time.sleep(self.chat_interval)

    @staticmethod
    def _frame_diff(prev, curr):
        if prev is None:
            return 999.0
        return float(cv2.cvtColor(cv2.absdiff(prev, curr), cv2.COLOR_BGR2GRAY).mean())

    @staticmethod
    def _print_triage(t):
        print(f"\n 真实感={t['score_authentic']} 道具感={t['score_staged']} diff={t['diff']:+d}")
        print(f" 亮度={t['brightness']} 对比={t['contrast']} 暖色={t['warm_ratio']:.0%}")
        print(f" 细节={t['detail']} 产品细节={t.get('product_detail','?')} 色彩熵={t['color_entropy']} sat={t['food_saturation']}")
        if t.get("food_appeal"):
            print(f" {t['food_appeal']}")
