"""
monitor_paigu.py — 排骨走遍乡村 实时监控
修改自 monitor_susu_pro.py, 目标为抖音乡村探店
"""
import sys, os

# ── 覆盖路径指向排骨 ──
TARGET = "排骨走遍乡村"
OUT_DIR_NAME = "排骨走遍乡村"
FRAME_DIR_NAME = "PaiGu"

# 在导入前注入 sys.argv 识别 headless
_headless = "--headless" in sys.argv
if "--headless" not in sys.argv:
    sys.argv.append("--headless")
if "--auto" not in sys.argv:
    sys.argv.append("--auto")

# ── 动态修改 monitor_susu_pro 的模块级常量 ──
import monitor_susu_pro as base

BASE = base.BASE
base.OUT_DIR = BASE / "04-宝妈直播诊断系统" / OUT_DIR_NAME
base.FRAME_DIR = BASE / "06-存档中心" / "temp_frames" / FRAME_DIR_NAME
base.OUT_DIR.mkdir(parents=True, exist_ok=True)
base.FRAME_DIR.mkdir(parents=True, exist_ok=True)

base.LIVE_LOG = base.OUT_DIR / f"live_data_{OUT_DIR_NAME}.jsonl"
base.TRIAGE_LOG = base.OUT_DIR / f"triage_log_{OUT_DIR_NAME}.jsonl"

# 覆盖关键词为排骨专用
base.KEYWORDS = ["排骨", "乡村", "农村", "好吃", "香", "探店", "打卡",
                 "多少钱", "怎么卖", "味道", "食材", "新鲜", "土",
                 "地道", "农家", "特色", "分量", "实惠", "价格"]
base.FUZZY_CHARS = {"排", "骨", "乡", "农", "吃", "香", "土", "价"}
base.CONVERSION_KW = {"多少钱", "怎么卖", "下单", "分量", "价格", "地址"}
base.WCH_KW = set(base.KEYWORDS)

if __name__ == "__main__":
    try:
        m = base.SuSuMonitorPro(auto_mode=True, headless=True)
        m.chat_region = (1500, 400, 450, 700)
        # 无音频/STT 子进程 (抖音直播)
        m.bg_procs = []
        m.run()
    except KeyboardInterrupt:
        base.console.print("\n[bold red]监控已停止[/]")
    except Exception as e:
        base.console.print(f"\n[bold red]错误: {e}[/]")
        import traceback
        traceback.print_exc()
