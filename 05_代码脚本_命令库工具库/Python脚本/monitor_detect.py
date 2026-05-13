"""
monitor_detect.py — 排骨 实时监控
抖音直播间截图OCR, 坐标960,920,480,120
"""
import sys, os

TARGET = "排骨"
OUT_DIR_NAME = "排骨"
FRAME_DIR_NAME = "PaiGu"

_headless = "--headless" in sys.argv
if "--headless" not in sys.argv:
    sys.argv.append("--headless")
if "--auto" not in sys.argv:
    sys.argv.append("--auto")

import monitor_susu_pro as base

BASE = base.BASE
base.OUT_DIR = BASE / "04-宝妈直播诊断系统" / OUT_DIR_NAME
base.FRAME_DIR = BASE / "06-存档中心" / "temp_frames" / FRAME_DIR_NAME
base.OUT_DIR.mkdir(parents=True, exist_ok=True)
base.FRAME_DIR.mkdir(parents=True, exist_ok=True)

base.LIVE_LOG = base.OUT_DIR / f"live_data_{OUT_DIR_NAME}.jsonl"
base.TRIAGE_LOG = base.OUT_DIR / f"triage_log_{OUT_DIR_NAME}.jsonl"

base.KEYWORDS = ["排骨", "乡村", "农村", "好吃", "香", "探店", "打卡",
                 "多少钱", "怎么卖", "味道", "食材", "新鲜", "土",
                 "地道", "农家", "特色", "分量", "实惠", "价格",
                 "检测", "诊断", "分析", "数据", "报告"]
base.FUZZY_CHARS = {"排", "骨", "乡", "农", "吃", "香", "土", "价", "检", "测"}
base.CONVERSION_KW = {"多少钱", "怎么卖", "下单", "价格", "地址"}
base.WCH_KW = set(base.KEYWORDS)

if __name__ == "__main__":
    try:
        m = base.SuSuMonitorPro(auto_mode=True, headless=True)
        m.chat_region = (960, 920, 480, 120)
        m.bg_procs = []
        m.run()
    except KeyboardInterrupt:
        base.console.print("\n[bold red]监控已停止[/]")
    except Exception as e:
        base.console.print(f"\n[bold red]错误: {e}[/]")
        import traceback
        traceback.print_exc()
