"""
monitor_susu_pro.py — 苏苏在浙里 实时监控增强版
功能:
- mss 高速截图 (≈50ms vs pyautogui 300ms)
- 评论区自动定位校准
- Rich 实时仪表盘
- 热键控制 (C=扫描区域, R=校准, Q=退出)
- 后台音频采集 + STT 转写 (自动拉起)
- 开机自启动注册 (--install)
"""
import sys, os, time, json, difflib, re, threading, tempfile, subprocess
from datetime import datetime
from pathlib import Path
from collections import deque, Counter

import cv2, numpy as np, mss, mss.tools, easyocr
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console
from rich.text import Text
from rich import box

_headless = "--headless" in sys.argv
if _headless:
    console = Console(file=sys.stderr, quiet=True, force_terminal=False)
    console.clear = lambda: None
else:
    console = Console()
if _headless:
    console.clear = lambda: None

# ── 路��� ──
BASE = Path("E:/MyCodeProjects")
OUT_DIR = BASE / "04-宝妈直播诊断系统" / "苏苏在浙里"
FRAME_DIR = BASE / "06-存档中心" / "temp_frames" / "SuSu"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FRAME_DIR.mkdir(parents=True, exist_ok=True)

LIVE_LOG = OUT_DIR / "live_data_susu.jsonl"
TRIAGE_LOG = OUT_DIR / "triage_log_susu.jsonl"

# ── 配置 ──
OCR_INTERVAL = 10
PANORAMA_INTERVAL = 120
CHAT_CANDIDATES = [
    (1550, 500, 450, 600),
    (1600, 400, 400, 700),
    (1400, 600, 500, 500),
    (0, 700, 1920, 400),
    (0, 300, 1920, 800),
]

KEYWORDS = ["苏苏", "江南", "农村", "家乡", "好吃", "香", "怎么做",
            "菜", "炒", "煮", "蒸", "妈妈", "小时候", "回忆",
            "想吃", "流口水", "关注", "点赞", "分享", "回购",
            "食材", "新鲜", "土", "农家", "绿色", "多少", "下单",
            "姐", "海燕"]

FUZZY_CHARS = {"苏", "江", "菜", "吃", "香", "妈", "土", "农", "鲜", "姐"}
CONVERSION_KW = {"下单", "回购", "多少", "怎么买", "链接", "关注"}
WCH_KW = {"苏苏", "江南", "农村", "家乡", "好吃", "香", "妈妈",
          "小时候", "回忆", "想吃", "流口水", "关注", "点赞",
          "食材", "土", "农家", "绿色", "新鲜", "姐"}

UI_NOISE = {"发四", "嫩瞎", "Ux", "2026", "士袄"}


class FastCapture:
    """基于 mss 的高速截图引擎"""
    def __init__(self):
        self.sct = mss.MSS()
        self.reader = easyocr.Reader(["ch_sim", "en"], gpu=False)

    def capture_region(self, region):
        return self.sct.grab({"left": region[0], "top": region[1],
                              "width": region[2], "height": region[3]})

    def capture_full(self):
        return self.sct.grab(self.sct.monitors[1])

    def save_png(self, sct_img, path):
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=path)

    def save_jpeg(self, sct_img, path, quality=85):
        arr = np.array(sct_img)
        bgr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        cv2.imwrite(path, bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])

    def ocr_region(self, region, tag=""):
        try:
            img = self.capture_region(region)
        except:
            return []
        arr = np.array(img)
        gray = cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        tmp = os.path.join(tempfile.gettempdir(), f"_ocr_{tag}_{int(time.time())}.png")
        cv2.imwrite(tmp, enhanced)
        if not os.path.isfile(tmp):
            return []
        results = self.reader.readtext(tmp)
        try: os.remove(tmp)
        except: pass
        return [r[1] for r in results]

    def triage(self, frame_bgr, prev_gray=None):
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

        # 冻帧检测: 与前一帧对比
        freeze_detected = False
        freeze_score = 0.0
        if prev_gray is not None and prev_gray.shape == gray.shape:
            diff = cv2.absdiff(prev_gray, gray).mean()
            freeze_score = float(diff)
            freeze_detected = diff < 3.0  # 几乎无变化

        pz = gray[int(h*0.30):int(h*0.55), int(w*0.30):int(w*0.70)]
        product_detail = float(cv2.Laplacian(pz, cv2.CV_64F).std()) if pz.size > 0 else 0.0

        fz = hsv[int(h*0.55):int(h*1.0), int(w*0.20):int(w*0.80)]
        sat_mean = float(cv2.mean(fz)[1]) if fz.size > 0 else 0.0

        sat_ok = 40 <= sat_mean <= 70
        warm_ok = 0.13 <= warm_ratio <= 0.27
        score_a = sum([10 if brightness > 60 else 0, 15 if contrast > 35 else 0,
                       15 if warm_ok else 0, 10 if green_ratio < 0.40 else 0,
                       15 if detail > 30 else 0, 10 if color_entropy > 4.5 else 0,
                       15 if sat_ok else 0, 10 if product_detail > 25 else 0])
        score_s = sum([10 if contrast <= 35 else 0, 10 if not warm_ok else 0,
                       15 if green_ratio > 0.40 else 0, 10 if detail <= 30 else 0,
                       10 if color_entropy <= 4.5 else 0, 10 if product_detail <= 25 else 0])

        # ── 场景分类 ──
        scene_scores = {
            "kitchen":   (brightness / 120 * 30 + warm_ratio / 0.5 * 25 + detail / 100 * 25 + sat_mean / 60 * 20) * (0 if freeze_detected else 1),
            "dining":    (warm_ratio / 0.5 * 30 + sat_mean / 60 * 30 + brightness / 120 * 20 + detail / 100 * 20) * (0 if freeze_detected else 1),
            "outdoor":   (green_ratio / 0.8 * 35 + brightness / 120 * 25 + color_entropy / 6 * 25 + detail / 100 * 15) * (0 if freeze_detected else 1),
            "product":   (product_detail / 100 * 35 + brightness / 120 * 25 + sat_mean / 60 * 25 + contrast / 100 * 15) * (0 if freeze_detected else 1),
            "freeze":    100 if freeze_detected else max(0, 100 - brightness * 5),
            "general":   20,
        }
        scene = max(scene_scores, key=scene_scores.get)

        # ── 食物视觉质量细化评分 ──
        # 色彩丰富度: H通道熵
        food_color_rich = color_entropy
        # 暖色食物区域: 橙色红色饱和度强度
        food_warm_mask = cv2.inRange(hsv, (0, 50, 50), (25, 255, 255))
        food_warm_sat = float(cv2.mean(hsv[:,:,1], mask=food_warm_mask)[0]) if cv2.countNonZero(food_warm_mask) > 100 else 0.0
        # 绿色蔬菜区域
        food_green_mask = cv2.inRange(hsv, (35, 50, 50), (85, 255, 255))
        food_green_sat = float(cv2.mean(hsv[:,:,1], mask=food_green_mask)[0]) if cv2.countNonZero(food_green_mask) > 100 else 0.0
        # 整体视觉质量分
        food_quality = min(100, (
            min(sat_mean / 60 * 30, 30) +          # 食物饱和度30%
            min(food_color_rich / 6 * 20, 20) +     # 色彩丰富度20%
            min(warm_ratio / 0.3 * 25, 25) +        # 暖色氛围25%
            min(detail / 80 * 25, 25)               # 细节纹理25%
        ))

        return {
            "score_authentic": score_a, "score_staged": score_s, "diff": score_a - score_s,
            "brightness": round(brightness, 1), "contrast": round(contrast, 1),
            "warm_ratio": round(warm_ratio, 3), "green_ratio": round(green_ratio, 3),
            "detail": round(detail, 1), "color_entropy": round(color_entropy, 2),
            "food_saturation": round(sat_mean, 1), "product_detail": round(product_detail, 1),
            # 新增字段
            "scene": scene,
            "freeze_detected": freeze_detected,
            "freeze_score": round(freeze_score, 2),
            "food_quality": round(food_quality, 1),
            "food_warm_sat": round(food_warm_sat, 1),
            "food_green_sat": round(food_green_sat, 1),
        }


# ── 校准函数 ──

def calibrate_chat_region(capture, rounds=30):
    console.print("[bold yellow] 评论区校准模式[/]")
    console.print("请在直播间评论发消息 (如 '今天做什么菜')")
    console.print("等待文字出现后自动定位...")
    baselines = {}
    for i, region in enumerate(CHAT_CANDIDATES):
        texts = capture.ocr_region(region, f"cal{i}")
        baselines[i] = set(texts)
    for attempt in range(rounds):
        time.sleep(2)
        for i, region in enumerate(CHAT_CANDIDATES):
            texts = capture.ocr_region(region, f"cal{i}")
            new_texts = set(texts) - baselines[i]
            real = {t for t in new_texts if not any(f in t for f in UI_NOISE)}
            if real:
                console.print(f"[green] 候选区 {i+1}: {real}[/]")
                console.print(f"   区域: {region}")
                return region
        if attempt % 5 == 0:
            console.print(f"  等待... ({attempt*2}s)")
    console.print("[yellow] 未检测到, 用默认区域[/]")
    return CHAT_CANDIDATES[0]


def quick_scan(capture):
    console.print("[bold]快速扫描全屏文字分布...[/]")
    sct = capture.sct
    monitor = sct.monitors[1]
    sw, sh = monitor["width"], monitor["height"]
    best_region, best_count = None, 0
    scans = [
        ("右侧中部", sw-500, 200, 500, sh-400),
        ("右侧全部", sw-500, 0, 500, sh),
        ("底部通栏", 0, sh-400, sw, 400),
        ("底部右半", sw//2, sh-400, sw//2, 400),
    ]
    for name, x, y, w, h in scans:
        texts = capture.ocr_region((x, y, w, h), "scan")
        real = [t for t in texts if not any(f in t for f in UI_NOISE)]
        console.print(f"  {name}: {len(texts)}段({len(real)}非UI)")
        if len(real) > best_count:
            best_count = len(real)
            best_region = (x, y, w, h)
    return best_region


class SuSuMonitorPro:
    def __init__(self, auto_mode=False, headless=False):
        self.capture = FastCapture()
        self.chat_region = (1700, 650, 450, 550)
        self.running = True
        self.auto_mode = auto_mode
        self.headless = headless
        self.keyword_counter = Counter()
        self.chat_history = deque(maxlen=50)
        self.latest_texts = []
        self.last_activity = 0
        self.session_start = time.time()
        self.ocr_count = 0
        self.conversion_count = 0
        self.triage_history = deque(maxlen=20)
        self.last_pano = 0
        self.conversion_active = False
        self.prev_frame = None
        self.quiet_cycles = 0
        self.stream_ended = False
        self.last_keyword_time = time.time()
        self.ocr_interval = OCR_INTERVAL
        self.bg_procs = []
        self.audio_target = ""

    def check_keywords(self, texts):
        full = "".join(texts)
        hits = [kw for kw in KEYWORDS if kw in full]
        fuzzy = [c for c in FUZZY_CHARS if c in full and c not in hits]
        all_hits = hits + fuzzy
        conv = [h for h in all_hits if h in CONVERSION_KW]
        wch = [kw for kw in WCH_KW if kw in full]
        return all_hits, conv, wch

    def append_jsonl(self, path, entry):
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False,
                               default=lambda x: float(x) if hasattr(x, 'item') else x) + "\n")

    def cleanup_old_data(self):
        """启动时清理过期数据: 旧帧/旧音频/JSONL 截断"""
        now = time.time()
        # 清理 7 天前全景截图
        kept_frames = 0
        del_frames = 0
        for f in sorted(FRAME_DIR.glob("pano_*.*")):
            age_days = (now - f.stat().st_mtime) / 86400
            if age_days > 7:
                f.unlink(missing_ok=True)
                del_frames += 1
            else:
                kept_frames += 1
        if del_frames:
            console.print(f"[dim]  清理全景截图: {del_frames} 过期, {kept_frames} 保留[/]")

        # 清理旧音频, 保留最多 50 个
        audio_dir = OUT_DIR / "audio"
        if audio_dir.exists():
            wavs = sorted(audio_dir.glob("*.wav"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in wavs[50:]:
                f.unlink(missing_ok=True)
            if len(wavs) > 50:
                console.print(f"[dim]  清理旧音频: {len(wavs)-50} 删除[/]")

        # JSONL 截断: 保留最后 2000 行
        for log_path in [LIVE_LOG, TRIAGE_LOG]:
            if log_path.exists():
                lines = log_path.read_text(encoding="utf-8").strip().split("\n")
                if len(lines) > 2000:
                    log_path.write_text("\n".join(lines[-2000:]) + "\n", encoding="utf-8")
                    console.print(f"[dim]  {log_path.name} 截断: {len(lines)}→2000[/]")

    def send_notification(self, title, message):
        """Windows 桌面通知 (PowerShell toast)"""
        try:
            safe_title = title.replace('"', "'")
            safe_msg = message.replace('"', "'")
            ps = f'''
$null = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$textNodes = $template.GetElementsByTagName("text")
$textNodes.Item(0).AppendChild($template.CreateTextNode("{safe_title}"))
$textNodes.Item(1).AppendChild($template.CreateTextNode("{safe_msg}"))
$toast = [Windows.UI.Notifications.ToastNotification]::new($template)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier().Show($toast)
'''
            subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, timeout=10)
        except Exception:
            pass  # 通知失败不影响主流程

    def build_display(self):
        now = time.time()
        elapsed = int(now - self.session_start)
        h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60

        info = Table.grid(padding=(0, 1))
        info.add_column(); info.add_column()
        info.add_row(" 时间", f"{h:02d}:{m:02d}:{s:02d}")
        info.add_row(" OCR", f"{self.ocr_count} 次")
        info.add_row(" 最新文字", f"{len(self.latest_texts)} 段")
        info.add_row(" 关键词命中", f"{sum(self.keyword_counter.values())} 次")
        info.add_row(" 转化意向", f"{self.conversion_count} 次")

        chat_text = Text()
        if self.latest_texts:
            for t in self.latest_texts[:10]:
                if any(kw in t for kw in KEYWORDS) or any(c in t for c in FUZZY_CHARS):
                    chat_text.append(f"  {t}\n", style="bold green")
                elif not any(f in t for f in UI_NOISE):
                    chat_text.append(f"  {t}\n", style="yellow")
                else:
                    pass  # skip UI noise
        else:
            chat_text.append("  等待评论区数据...\n", style="dim")
        if self.chat_history:
            chat_text.append(f"\n  [最近{len(self.chat_history)}条]", style="italic")

        kw_text = Text()
        if self.keyword_counter:
            for kw, cnt in self.keyword_counter.most_common(12):
                kw_text.append(f"  {kw}: {cnt}\n")
        else:
            kw_text.append("  暂无命中\n", style="dim")

        triage_text = Text()
        if self.triage_history:
            t = self.triage_history[-1]
            triage_text.append(f"  真实感: {t['score_authentic']}  |  道具感: {t['score_staged']}  |  diff: {t['diff']:+d}\n")
            triage_text.append(f"  亮度: {t['brightness']}  |  暖色: {t['warm_ratio']:.0%}  |  细节: {t['detail']}\n")
            triage_text.append(f"  食物饱和度: {t['food_saturation']}  |  色彩熵: {t['color_entropy']}\n")
        else:
            triage_text.append("  等待全景...\n", style="dim")

        layout = Layout()
        layout.split_column(
            Layout(Panel(info, title=" 苏苏在浙里 实时监控", border_style="cyan", box=box.ROUNDED)),
            Layout(Layout.split_row(
                Layout(Panel(chat_text, title=" 最新评论区", border_style="green")),
                Layout(Panel(kw_text, title=" 关键词排行", border_style="yellow")),
            )),
            Layout(Panel(triage_text, title=" 画面分析", border_style="magenta")),
        )
        return layout

    def on_keyboard(self):
        try:
            from pynput import keyboard
            def on_press(key):
                try: k = key.char.lower()
                except: return
                if k == 'c':
                    console.print("\n[扫描] 快速扫描评论区...")
                    region = quick_scan(self.capture)
                    if region:
                        self.chat_region = region
                        console.print(f"[green] 区域已更新: {region}[/]")
                elif k == 'r':
                    console.print("\n[校准] 等待测试消息...")
                    region = calibrate_chat_region(self.capture)
                    if region:
                        self.chat_region = region
                        console.print(f"[green] 已校准: {region}[/]")
                elif k == 'q':
                    self.running = False
                    console.print("\n[停止]")
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
        except ImportError:
            pass

    def run_startup_test(self):
        """系统自检: OCR + 音频 + 画面, 启动后立即执行"""
        console.print("\n[bold yellow]═══ 系统自检 ═══[/]")
        results = []

        # ── 1. OCR 评论区测试 ──
        console.print("\n[1/3] 评论区 OCR 测试...", end=" ")
        try:
            texts = self.capture.ocr_region(self.chat_region, "test_boot")
            real = [t for t in texts if not any(f in t for f in UI_NOISE)]
            if real:
                hits, conv, _ = self.check_keywords(real)
                sample = " | ".join(real[:3])
                results.append(("评论区OCR", "PASS", f"{len(real)}段文字, {len(hits)}关键词"))
                console.print(f"[green]通过[/]  {len(real)}段文字")
                console.print(f"  └─ 样本: {sample[:80]}")
                if hits:
                    console.print(f"  └─ 关键词: {', '.join(hits)}")
            else:
                results.append(("评论区OCR", "WARN", f"{len(texts)}段(纯UI噪声)"))
                console.print(f"[yellow]警告[/] {len(texts)}段文字, 均为UI元素")
                console.print("  └─ 按 C 扫描 或 R 校准评论区位置")
        except Exception as e:
            results.append(("评论区OCR", "FAIL", str(e)))
            console.print(f"[red]失败: {e}[/]")

        # ── 2. 音频设备测试 ──
        console.print("\n[2/3] 音频设备测试...", end=" ")
        try:
            import pyaudiowpatch as pyaudio
            p = pyaudio.PyAudio()
            loopback = p.get_default_wasapi_loopback()
            dev_name = loopback['name']
            dev_rate = int(loopback['defaultSampleRate'])
            dev_ch = loopback['maxInputChannels']
            console.print(f"[green]通过[/]  {dev_name}")
            console.print(f"  └─ {dev_rate}Hz / {dev_ch}ch")

            # 小段实测: 录制3s验证
            console.print("  └─ 录制3s测试...", end=" ")
            stream = p.open(
                format=pyaudio.paInt16, channels=dev_ch, rate=dev_rate,
                input=True, input_device_index=loopback['index'],
                frames_per_buffer=1024,
            )
            frames = []
            for _ in range(int(dev_rate / 1024 * 3)):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream(); stream.close()
            raw = np.frombuffer(b''.join(frames), dtype=np.int16)
            rms = np.sqrt(np.mean(raw.astype(np.float64)**2)) / 32768.0
            console.print(f"RMS={rms:.4f}  {'[green]有声音[/]' if rms > 0.003 else '[yellow]环境安静[/]'}")
            p.terminate()
            results.append(("音频设备", "PASS", f"{dev_name} RMS={rms:.4f}"))
        except ImportError:
            console.print("[yellow]跳过[/]  pyaudiowpatch 未安装")
            results.append(("音频设备", "SKIP", "pyaudiowpatch 未安装"))
        except Exception as e:
            console.print(f"[red]失败: {e}[/]")
            results.append(("音频设备", "FAIL", str(e)))

        # ── 3. 全屏画面测试 ──
        console.print("\n[3/3] 画面采集测试...", end=" ")
        try:
            sct_img = self.capture.capture_full()
            bgr = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = str(FRAME_DIR / f"pano_boottest_{stamp}.jpg")
            self.capture.save_jpeg(sct_img, path)
            t = self.capture.triage(bgr)
            console.print(f"[green]通过[/]  {bgr.shape[1]}x{bgr.shape[0]}")
            console.print(f"  └─ 亮度:{t['brightness']} 暖色:{t['warm_ratio']:.0%} 细节:{t['detail']}")
            console.print(f"  └─ 食物sat:{t['food_saturation']} 真实感:{t['score_authentic']}/{t['score_staged']}")
            self.triage_history.append(t)
            self.prev_frame = bgr
            self.last_pano = time.time()
            results.append(("画面采集", "PASS", f"{bgr.shape[1]}x{bgr.shape[0]} 亮度={t['brightness']}"))
        except Exception as e:
            console.print(f"[red]失败: {e}[/]")
            results.append(("画面采集", "FAIL", str(e)))

        # ── 汇总表 ──
        table = Table(title="启动自检结果", box=box.ROUNDED)
        table.add_column("项目"); table.add_column("状态"); table.add_column("详情")
        for name, status, detail in results:
            style = {"PASS": "green", "WARN": "yellow", "FAIL": "red", "SKIP": "dim"}.get(status, "")
            table.add_row(name, f"[{style}]{status}[/]", detail)
        console.print("\n"); console.print(table)
        console.print("[bold yellow]══════════════[/]\n")

    def run(self):
        console.clear()
        console.print("[bold cyan] 苏苏在浙里 . 实时监控增强版 [/]")
        console.print()
        console.print("  热键: [bold]C[/] 扫描  [bold]R[/] 校准  [bold]Q[/] 退出")
        console.print()

        # 系统自检 + 数据清理
        self.run_startup_test()
        self.cleanup_old_data()

        if not self.auto_mode:
            try:
                has_tty = sys.stdin.isatty()
            except:
                has_tty = False
            if has_tty:
                ans = input("  校准评论区? (y/n, 默认y): ").strip().lower()
                if ans != 'n':
                    region = calibrate_chat_region(self.capture)
                    if region:
                        self.chat_region = region
                        console.print(f"[green]  区域: {self.chat_region}[/]")

        console.print(f"\n[bold]区域: {self.chat_region}  OCR: {OCR_INTERVAL}s(自适应)  全景: {PANORAMA_INTERVAL}s[/]")
        console.print("[dim]3秒后启动...[/]")
        time.sleep(3)

        threading.Thread(target=self.on_keyboard, daemon=True).start()

        # 后台进程看门狗
        if self.bg_procs:
            def watchdog():
                bg_target = self.audio_target
                bg_list = self.bg_procs
                while self.running:
                    time.sleep(30)
                    for i, p in enumerate(bg_list):
                        if p.poll() is not None:
                            name = ["音频", "STT"][i] if i < 2 else f"进程{i}"
                            script = ["audio_capture.py", "whisper_stt.py"][i] if i < 2 else ""
                            log_tag = ["audio", "stt"][i] if i < 2 else "bg"
                            console.print(f"[red]  {name} 已停止, 重启...[/]")
                            try:
                                new_p = spawn_background(name, script, f'--target "{bg_target}"', log_tag)
                                bg_list[i] = new_p
                                console.print(f"[green]  {name} 已重启 PID:{new_p.pid}[/]")
                            except Exception as e:
                                console.print(f"[red]  重启 {name} 失败: {e}[/]")
            threading.Thread(target=watchdog, daemon=True).start()

        if self.headless:
            self._run_headless()
        else:
            with Live(self.build_display(), refresh_per_second=2, screen=False) as live:
                self._run_loop(live)

    def _run_headless(self):
        """Headless monitoring loop — no rich.live, all data writing."""
        while self.running:
            self._do_ocr_cycle()
            self._check_panorama()
            time.sleep(self.ocr_interval)

    def _do_ocr_cycle(self):
        """Single OCR capture + keyword check + log write."""
        now = time.time()
        self.ocr_count += 1
        texts = self.capture.ocr_region(self.chat_region, "susu")
        hits, conv_hits, wch_hits = self.check_keywords(texts)
        real_texts = [t for t in texts if not any(f in t for f in UI_NOISE)]

        entry = {
            "timestamp": now, "time": datetime.fromtimestamp(now).strftime("%H:%M:%S"),
            "texts": texts, "real_texts": real_texts,
            "text_count": len(texts),
            "keyword_hits": hits, "conversion_hits": conv_hits, "wch_hits": wch_hits,
        }
        self.append_jsonl(LIVE_LOG, entry)

        if hits:
            self.keyword_counter.update(hits)
            self.last_activity = now
            self.last_keyword_time = now
            self.chat_history.append((entry["time"], hits))
        if conv_hits:
            self.conversion_count += 1
            self.conversion_active = True
            kw_list = ", ".join(conv_hits[:3])
            threading.Thread(
                target=self.send_notification,
                args=(" 转化意向", f"检测到: {kw_list}"),
                daemon=True,
            ).start()

        self.latest_texts = real_texts if real_texts else texts

        # 自适应 OCR 频率
        idle = time.time() - self.last_activity
        if idle < 30:
            self.ocr_interval = 5
        elif idle < 120:
            self.ocr_interval = 10
        else:
            self.ocr_interval = 20

    def _check_panorama(self):
        """Periodic panorama capture + triage."""
        now = time.time()
        if now - self.last_pano < PANORAMA_INTERVAL:
            return
        try:
            sct_img = self.capture.capture_full()
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = str(FRAME_DIR / f"pano_{stamp}.jpg")
            self.capture.save_jpeg(sct_img, path)

            bgr = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
            bright = float(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).mean())
            if bright < 255:
                prev_gray = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY) if self.prev_frame is not None else None
                t = self.capture.triage(bgr, prev_gray=prev_gray)
                t["timestamp"] = now
                t["image"] = path
                self.triage_history.append(t)
                self.append_jsonl(TRIAGE_LOG, t)
                if self.prev_frame is not None:
                    d = cv2.absdiff(cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY),
                                    cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)).mean()
                    self.quiet_cycles = 0 if d > 5 else self.quiet_cycles + 1
                    if self.quiet_cycles >= 5 and not self.stream_ended:
                        idle = (time.time() - self.last_keyword_time) / 60
                        if idle > 8:
                            self.stream_ended = True
                            console.print("\n[bold yellow]检测到下播, 生成复盘报告...[/]")
                            try:
                                rp = self.generate_post_report()
                                console.print(f"[green]报告已保存: {rp}[/]")
                            except Exception as e:
                                console.print(f"[red]报告生成失败: {e}[/]")
                self.prev_frame = bgr
        except Exception as e:
            console.print(f"[red]全景失败: {e}[/]")
        self.last_pano = now

    def _run_loop(self, live):
        """Main loop with live display."""
        while self.running:
            self._do_ocr_cycle()
            self._check_panorama()
            live.update(self.build_display())
            time.sleep(self.ocr_interval)

    def generate_post_report(self):
        """下播后自动生成复盘报告"""
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = OUT_DIR / f"auto复盘_{stamp}.md"

        live_data = tail_jsonl(LIVE_LOG)
        triage_data = tail_jsonl(TRIAGE_LOG)
        stt_data = tail_jsonl(STT_LOG)

        # Time range
        all_ts = []
        for e in live_data + triage_data:
            if e.get("timestamp"):
                all_ts.append(e["timestamp"])
        start_ts = min(all_ts) if all_ts else time.time()
        end_ts = max(all_ts) if all_ts else time.time()
        dur = int(end_ts - start_ts)

        # Aggregate
        all_kw = Counter()
        conv_total = 0
        for entry in live_data:
            for h in entry.get("keyword_hits", []):
                all_kw[h] += 1
            if entry.get("conversion_hits"):
                conv_total += 1

        # Triage averages
        tri_avgs = {}
        if triage_data:
            for key in ("brightness", "food_saturation", "score_authentic", "detail", "warm_ratio"):
                vals = [t.get(key, 0) for t in triage_data if t.get(key)]
                tri_avgs[key] = round(sum(vals) / len(vals), 1) if vals else 0

        # STT summary
        stt_texts = [s.get("text", "") for s in stt_data if s.get("text")]

        # Build report
        report = []
        report.append(f"# 苏苏在浙里 · 自动复盘报告")
        report.append(f"")
        report.append(f"**直播日期:** {datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d')}")
        report.append(f"**时段:** {datetime.fromtimestamp(start_ts).strftime('%H:%M')} → {datetime.fromtimestamp(end_ts).strftime('%H:%M')}")
        report.append(f"**直播时长:** {dur//60}分{dur%60}秒")
        report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"")
        report.append(f"## 互动数据")
        report.append(f"")
        report.append(f"- **OCR 扫描:** {len(live_data)} 次")
        report.append(f"- **关键词命中:** {sum(all_kw.values())} 次")
        report.append(f"- **转化意向:** {conv_total} 次")
        report.append(f"- **STT 语音转写:** {len(stt_data)} 条")
        report.append(f"")
        report.append(f"### 热门关键词 TOP 10")
        report.append(f"")
        report.append(f"| 关键词 | 次数 |")
        report.append(f"|--------|------|")
        for kw, cnt in all_kw.most_common(10):
            bar = "█" * min(cnt, 20)
            report.append(f"| {kw} | {cnt} {bar} |")
        report.append(f"")

        if tri_avgs:
            report.append(f"## 画面质量分析")
            report.append(f"")
            report.append(f"| 指标 | 平均值 |")
            report.append(f"|------|--------|")
            labels = {"brightness": "亮度", "food_saturation": "食物饱和度", "score_authentic": "真实感评分", "detail": "画面细节", "warm_ratio": "暖色比"}
            for key, label in labels.items():
                if key in tri_avgs:
                    val = tri_avgs[key]
                    if key == "warm_ratio":
                        val = f"{float(val)*100:.1f}%"
                    report.append(f"| {label} | {val} |")
            report.append(f"")

        if stt_texts:
            report.append(f"## 语音识别精选 (最后 20 条)")
            report.append(f"")
            for s in stt_data[-20:]:
                txt = s.get("text", "")[:60]
                t = s.get("time", "")
                if txt.strip():
                    report.append(f"- [{t}] {txt}")
            report.append(f"")

        report.append(f"---")
        report.append(f"*由 苏苏在浙里 监控系统自动生成*")

        out = "\n".join(report)
        report_path.write_text(out, encoding="utf-8")
        return report_path


def tail_jsonl(path, max_lines=500):
    """Read last N lines of a JSONL file"""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        results = []
        for line in lines[-max_lines:]:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except:
                    pass
        return results
    except:
        return []


# ── 后台进程管理 ──

def spawn_background(name, script, args, log_tag):
    """启动后台 Python 进程 (隐藏窗口)"""
    ps_cmd = (
        f'powershell -NoProfile -WindowStyle Hidden -Command "'
        f'cd \\"E:\\MyCodeProjects\\审计工具\\"; '
        f'python {script} {args} 2>&1 | '
        f'ForEach-Object {{ \\"$($(Get-Date -Format HH:mm:ss)) [{log_tag}] $_\\" }} '
        f'>> \\"E:\\MyCodeProjects\\06-存档中心\\logs\\{log_tag}.log\\"'
        f'"'
    )
    proc = subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command",
         f'cd "E:\\MyCodeProjects\\审计工具"; python {script} {args}'],
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc


def install_autostart():
    """注册开机自启动 (计划任务)"""
    script = Path(__file__).resolve()
    ps_code = f'''
    $action = New-ScheduledTaskAction -Execute "python" -Argument "\\"{script}\\""
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName "SuSuLiveMonitor" -Action $action -Trigger $trigger -Principal $principal -Force
    '''
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_code],
                            capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        console.print("[green]开机自启动已注册 (计划任务: SuSuLiveMonitor)[/]")
        return True
    # 备用: Startup 文件夹
    shortcut = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "SuSuLiveMonitor.bat"
    shortcut.write_text(f'@echo off\npython "{script}" --auto\n', encoding="utf-8")
    console.print(f"[green]开机自启动已注册 (Startup: {shortcut})[/]")
    return True


def uninstall_autostart():
    """移除开机自启动"""
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    'Unregister-ScheduledTask -TaskName "SuSuLiveMonitor" -Confirm:$false -ErrorAction SilentlyContinue'],
                   capture_output=True, timeout=15)
    shortcut = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "SuSuLiveMonitor.bat"
    shortcut.unlink(missing_ok=True)
    console.print("[yellow]开机自启动已移除[/]")


if __name__ == "__main__":
    # ── 参数处理 ──
    if "--install" in sys.argv:
        install_autostart()
        sys.exit(0)
    if "--uninstall" in sys.argv:
        uninstall_autostart()
        sys.exit(0)
    if "--status" in sys.argv:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             'Get-ScheduledTask -TaskName "SuSuLiveMonitor" -ErrorAction SilentlyContinue | Select-Object State'],
            capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and "Ready" in result.stdout:
            console.print("[green]开机自启动: 已注册 (计划任务)[/]")
        else:
            console.print("[yellow]开机自启动: 未注册 (python --install 注册)[/]")
        sys.exit(0)

    auto = "--auto" in sys.argv

    # ── 拉起后台音频 + STT (除非 --no-bg) ──
    bg_procs = []
    if "--no-bg" not in sys.argv:
        console.print("[dim]拉起后台音频采集 + STT 转写...[/]")
        target = "E:\\MyCodeProjects\\04-宝妈直播诊断系统\\苏苏在浙里"
        bg_procs.append(spawn_background("音频", "audio_capture.py", f'--target "{target}"', "audio"))
        bg_procs.append(spawn_background("STT", "whisper_stt.py", f'--target "{target}"', "stt"))
        console.print(f"[dim]  后台进程已启动 ({len(bg_procs)}个)[/]")

    # ── 拉起 Web Dashboard (--dashboard) ──
    if "--dashboard" in sys.argv:
        console.print("[dim]启动 Web Dashboard (端口 5050)...[/]")
        try:
            from dashboard_server import run_dashboard
            t = threading.Thread(target=run_dashboard, kwargs={"open_browser": False}, daemon=True)
            t.start()
            console.print("[dim]  Web 面板: http://localhost:5050 [/]")
            console.print("[dim]  手机访问: http://<本机IP>:5050 [/]")
        except Exception as e:
            console.print(f"[red]  Dashboard 启动失败: {e}[/]")

    headless = "--headless" in sys.argv
    try:
        m = SuSuMonitorPro(auto_mode=auto, headless=headless)
        m.bg_procs = bg_procs
        m.audio_target = target if "--no-bg" not in sys.argv else ""
        m.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]监控已停止[/]")
    except Exception as e:
        console.print(f"\n[bold red]错误: {e}[/]")
        import traceback
        traceback.print_exc()
    finally:
        # 清理后台进程
        for p in bg_procs:
            try: p.terminate()
            except: pass
