"""
live_dashboard.py — 实时监控仪表盘 (sidecar, 不中断主进程)
读取 jsonl 数据流, 展示实时状态
运行方式: python live_dashboard.py --target <dir>
"""
import json, time, os, sys, argparse
from pathlib import Path
from datetime import datetime
from collections import deque

REFRESH_SECONDS = 5
MAX_LINES = 200  # per source

class LiveDashboard:
    def __init__(self, base_dir):
        self.base = Path(base_dir)
        self.sources = {
            "stt": self.base / "stt.jsonl",
            "ocr_su": self.base / "live_data_SuSu.jsonl",
            "ocr_dy": self.base / "live_data_DouYin.jsonl",
            "triage_su": self.base / "triage_log_SuSu.jsonl",
            "triage_dy": self.base / "triage_log_DouYin.jsonl",
        }
        self.positions = {k: 0 for k in self.sources}
        self.buffers = {k: deque(maxlen=MAX_LINES) for k in self.sources}
        self.rates = {k: deque(maxlen=12) for k in self.sources}  # last 12 samples = 60s

        # 智能告警关键词
        self.question_kw = ["怎么做", "多少钱", "怎么买", "哪里买", "链接", "好吃吗", "什么价格"]
        self.praise_kw = ["好吃", "想要", "下单", "回购", "关注", "点赞", "分享"]
        self.negative_kw = ["太贵", "不好", "差评", "退了", "失望", "不行"]

    def poll(self):
        """读新行, 更新缓冲, 返回本次新增数"""
        added = {}
        now = time.time()
        for key, path in self.sources.items():
            if not path.is_file():
                added[key] = 0
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    f.seek(self.positions[key])
                    new_lines = f.readlines()
                    self.positions[key] = f.tell()
                for line in new_lines:
                    line = line.strip()
                    if line:
                        try:
                            self.buffers[key].append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                added[key] = len(new_lines)
                self.rates[key].append((now, len(new_lines)))
            except Exception:
                added[key] = 0
        return added

    def calc_rate(self, key):
        """计算每分钟新增条目数"""
        rates = self.rates.get(key, [])
        if len(rates) < 2:
            return 0
        recent = [r for r in rates if r[0] > time.time() - 65]
        if len(recent) < 2:
            return 0
        total = sum(r[1] for r in recent)
        span = min(recent[-1][0] - recent[0][0], 60)
        if span < 1:
            return total
        return int(total / span * 60)

    def render(self):
        """清屏刷新仪表盘"""
        os.system('cls' if os.name == 'nt' else 'clear')
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"═" * 60)
        print(f"  清晨烟火小厨 · 实时监控仪表盘    {now_str}")
        print(f"═" * 60)

        # 数据速率
        print(f"\n── 数据流 ──────────────────────────────")
        labels = {
            "stt": "STT语音",
            "ocr_su": "OCR视频号",
            "ocr_dy": "OCR抖音",
            "triage_su": "Triage视频号",
            "triage_dy": "Triage抖音",
        }
        for key, label in labels.items():
            buf = self.buffers[key]
            rate = self.calc_rate(key)
            print(f"  {label}: {len(buf)}条  {rate}条/分")

        # 最新 STT
        stt_buf = self.buffers["stt"]
        if stt_buf:
            last = stt_buf[-1]
            text = last.get("text", "")[:120]
            t = last.get("time", "")
            speakers = last.get("speakers", [])
            spk = f" [{','.join(speakers)}]" if speakers else ""
            print(f"\n── 语音识别 ───────────────────────────")
            print(f"  [{t}]{spk} {text}")

        # 最新 OCR
        for key, label in [("ocr_su", "视频号评论"), ("ocr_dy", "抖音评论")]:
            buf = self.buffers[key]
            if buf:
                # 最近 3 条
                recent = list(buf)[-3:]
                texts = []
                for r in recent:
                    for t in r.get("texts", [])[:2]:
                        if t not in texts:
                            texts.append(t)
                if texts:
                    print(f"\n── {label} ─────────────────────────")
                    for t in texts[-5:]:
                        print(f"  · {t[:60]}")

        # 最新 Triage
        for key, label in [("triage_su", "视频号"), ("triage_dy", "抖音")]:
            buf = self.buffers[key]
            if buf:
                last = buf[-1]
                print(f"\n── 视觉分析 {label} ───────────────────")
                print(f"  亮度:{last.get('brightness', '?'):>5}  "
                      f"暖色:{last.get('warm_ratio', 0)*100:.0f}%  "
                      f"食Sat:{last.get('food_saturation', '?'):>5}  "
                      f"真实:{last.get('score_authentic', '?')}/85  "
                      f"人脸:{last.get('face',{}).get('count', 0)}")
                zb = last.get("zone_brightness", {})
                if zb:
                    print(f"  左/中/右亮度: {zb.get('left','?'):.0f}/{zb.get('center','?'):.0f}/{zb.get('right','?'):.0f}  "
                          f"差:{zb.get('left_right_diff',0):+.0f}")

        # 智能告警
        print(f"\n── 智能告警 ───────────────────────────")
        alerts = []
        # 扫描 OCR 中关键词
        for key, label in [("ocr_su", "视频号"), ("ocr_dy", "抖音")]:
            buf = self.buffers[key]
            seen_texts = set()
            for r in list(buf)[-50:]:  # 最近 50 条
                for t in r.get("texts", []):
                    if t in seen_texts:
                        continue
                    seen_texts.add(t)
                    for kw in self.question_kw:
                        if kw in t:
                            alerts.append(f"[{label}] 提问: \"{t[:50]}\"")
                            break
                    for kw in self.praise_kw:
                        if kw in t:
                            if kw in t:
                                pass  # 记录但暂不告警

        # STT 告警
        for r in list(stt_buf)[-30:]:
            text = r.get("text", "")
            t = r.get("time", "")
            if "苏苏" in text and ("做" in text or "菜" in text):
                alerts.append(f"[语音] 烹饪内容: \"{text[:60]}\"")

        if alerts:
            for a in alerts[-8:]:
                print(f"  ! {a}")
        else:
            print(f"  无告警 (正常)")

        # 进度条
        stt_len = len(stt_buf)
        if stt_len > 0:
            progress = min(stt_len / 500 * 100, 100)
            bar = "#" * int(progress / 5) + "-" * (20 - int(progress / 5))
            print(f"\n  数据积累: [{bar}] {stt_len}条STT")

        print(f"\n{'='*60}")
        print(f"  刷新: 每{REFRESH_SECONDS}s  |  Ctrl+C 停止")

    def run(self):
        print(f"[仪表盘] 监控 {self.base}/")
        print(f"[仪表盘] 首次加载...")
        self.poll()  # initial load
        time.sleep(1)
        while True:
            self.poll()
            self.render()
            time.sleep(REFRESH_SECONDS)


def main():
    parser = argparse.ArgumentParser(description="实时监控仪表盘")
    parser.add_argument("--target", default="", help="数据目录")
    args = parser.parse_args()
    base = args.target if args.target else "E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨"
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    dashboard = LiveDashboard(base)
    try:
        dashboard.run()
    except KeyboardInterrupt:
        print("\n[仪表盘] 停止")


if __name__ == "__main__":
    main()
