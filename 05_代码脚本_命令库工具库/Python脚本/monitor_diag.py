"""
monitor_diag.py — 直播复盘系统 实时监控
用于抖音技术复盘/诊断类直播
"""
import sys, os

TARGET = "直播复盘系统"
OUT_DIR_NAME = "直播复盘系统"
FRAME_DIR_NAME = "DiagSystem"

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

base.KEYWORDS = ["诊断", "复盘", "数据", "分析", "报告", "评分", "指标",
                 "直播间", "监控", "优化", "建议", "趋势", "对比",
                 "算法", "流量", "转化", "合规", "风险", "如何"]
base.FUZZY_CHARS = {"诊", "复", "数", "报", "分", "监", "优"}
base.CONVERSION_KW = {"数据", "报告", "分析", "建议"}
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
