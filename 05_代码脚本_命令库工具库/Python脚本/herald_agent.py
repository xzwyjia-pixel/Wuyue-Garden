#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 传令官 · Webhook 推送
=================================================
final_agent_run.py 完成/崩溃时推送极简报告到指定机器人。

支持：
  - 企业微信机器人
  - Slack Webhook
  - Discord Webhook
  - 通用 JSON POST

用法：
  python herald_agent.py                              # 从 pipeline_state 推送
  python herald_agent.py --status failed --msg "崩溃"  # 手动推送
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_STATE_PATH = _DATA_DIR / "pipeline_state.json"
_CFG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _load_config() -> dict:
    try:
        import yaml
        return yaml.safe_load(_CFG_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _read_state() -> dict:
    if not _STATE_PATH.exists():
        return {}
    return json.loads(_STATE_PATH.read_text(encoding="utf-8"))


# ──────────────────────────────────────────────
# 报告组装
# ──────────────────────────────────────────────

def build_report(state: dict, override_status: str = "",
                  override_msg: str = "") -> dict:
    """从 pipeline_state 组装报告数据"""
    steps = state.get("steps", [])
    refine_results = state.get("refine_results", [])
    vision = state.get("vision_audit", {})
    gdrive = state.get("gdrive_sync", {})

    status = override_status or state.get("status", "unknown")
    passed = sum(1 for r in refine_results if r.get("verified_safe"))
    total_cases = len(refine_results)

    # 规则数量
    rules_path = Path(_DATA_DIR).parent / "rules.json"
    rule_count = 0
    try:
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
        for lv in ("HIGH", "MEDIUM", "LOW"):
            rule_count += len(rules.get("risk_levels", {}).get(lv, {}).get("focus", {}))
    except Exception:
        pass

    # 耗时
    duration = 0
    for s in steps:
        duration += s.get("duration_s", 0)

    return {
        "status": status,
        "msg": override_msg or "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration_s": round(duration, 1),
        "steps": len(steps),
        "cases": total_cases,
        "passed": passed,
        "rule_count": rule_count,
        "vision_findings": vision.get("total_findings", 0),
        "gdrive_status": gdrive.get("status", "none"),
        "gdrive_files": gdrive.get("files_uploaded", 0),
    }


# ──────────────────────────────────────────────
# Webhook 格式化
# ──────────────────────────────────────────────

def _fmt_wechat_work(r: dict) -> dict:
    status_emoji = "✅" if r["status"] == "completed" else "❌"
    lines = [
        f"{status_emoji} 规则甄查 · 流水线 {r['status']}",
        f"> 时间: {r['timestamp']}",
        f"> 耗时: {r['duration_s']}s | 步骤: {r['steps']}",
        f"> 文案: {r['passed']}/{r['cases']} 通过",
        f"> 规则: {r['rule_count']} 条",
        f"> 视觉: {r['vision_findings']} 项 | 云端: {r['gdrive_files']} 文件",
    ]
    if r["msg"]:
        lines.append(f"> 备注: {r['msg']}")
    return {"msgtype": "markdown", "markdown": {"content": "\n".join(lines)}}


def _fmt_slack(r: dict) -> dict:
    status_color = "#2eb886" if r["status"] == "completed" else "#e01e5a"
    fields = [
        {"title": "耗时", "value": f"{r['duration_s']}s", "short": True},
        {"title": "步骤", "value": str(r["steps"]), "short": True},
        {"title": "文案通过", "value": f"{r['passed']}/{r['cases']}", "short": True},
        {"title": "规则", "value": str(r["rule_count"]), "short": True},
        {"title": "视觉发现", "value": str(r["vision_findings"]), "short": True},
        {"title": "云端文件", "value": str(r["gdrive_files"]), "short": True},
    ]
    return {
        "attachments": [{
            "color": status_color,
            "title": f"流水线 {r['status']}",
            "fields": fields,
            "footer": r["timestamp"],
        }]
    }


def _fmt_discord(r: dict) -> dict:
    status_color = 0x2eb886 if r["status"] == "completed" else 0xe01e5a
    return {
        "embeds": [{
            "title": f"流水线 {r['status']}",
            "color": status_color,
            "fields": [
                {"name": "耗时", "value": f"{r['duration_s']}s", "inline": True},
                {"name": "步骤", "value": str(r["steps"]), "inline": True},
                {"name": "文案通过", "value": f"{r['passed']}/{r['cases']}", "inline": True},
                {"name": "规则", "value": str(r["rule_count"]), "inline": True},
                {"name": "视觉", "value": str(r["vision_findings"]), "inline": True},
                {"name": "云端", "value": f"{r['gdrive_files']} 文件", "inline": True},
            ],
            "footer": {"text": r["timestamp"]},
        }]
    }


def _fmt_generic(r: dict) -> dict:
    return {
        "source": "规则甄查",
        "status": r["status"],
        "timestamp": r["timestamp"],
        "duration_seconds": r["duration_s"],
        "steps": r["steps"],
        "cases_passed": f"{r['passed']}/{r['cases']}",
        "rule_count": r["rule_count"],
        "vision_findings": r["vision_findings"],
        "gdrive_files": r["gdrive_files"],
    }


_FORMATTERS = {
    "wechat_work": _fmt_wechat_work,
    "slack": _fmt_slack,
    "discord": _fmt_discord,
    "generic": _fmt_generic,
}


# ──────────────────────────────────────────────
# 推送
# ──────────────────────────────────────────────

def push_report(report: dict, webhook_url: str, webhook_type: str = "generic"):
    """推送报告到指定 webhook"""
    fmt = _FORMATTERS.get(webhook_type, _fmt_generic)
    payload = fmt(report)

    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code in (200, 204):
            print(f"[WEBHOOK] {webhook_type} → OK")
            return True
        else:
            print(f"[WEBHOOK] {webhook_type} → HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"[WEBHOOK] {webhook_type} → FAIL: {e}")
        return False


# ──────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────

def send(override_status: str = "", override_msg: str = ""):
    """读取 config + state → 推送"""
    cfg = _load_config()
    wh = cfg.get("webhook", {})
    if not wh.get("enabled") or not wh.get("url"):
        print("[HERALD] webhook 未启用（config.yaml 中配置）")
        return

    state = _read_state()
    report = build_report(state, override_status, override_msg)

    print(f"[HERALD] 推送 → {wh['type']} ({wh['url'][:40]}...)")
    print(f"  状态: {report['status']} | 文案: {report['passed']}/{report['cases']} | "
          f"规则: {report['rule_count']}")

    push_report(report, wh["url"], wh["type"])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Webhook 推送传令官")
    parser.add_argument("--status", default="", help="覆盖状态")
    parser.add_argument("--msg", default="", help="附加消息")
    args = parser.parse_args()
    send(args.status, args.msg)
