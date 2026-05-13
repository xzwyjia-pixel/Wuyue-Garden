# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — Obsidian 审计报告同步器
===================================================
读取 data/ 下最新审计产物 → 生成带双链的 Obsidian Markdown 报告
输出：notes/YYYY-MM-DD 规则演变报告.md
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_NOTES_DIR = Path(__file__).resolve().parent.parent.parent / "notes"
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_RULES_PATH = Path(__file__).resolve().parent.parent.parent / "rules.json"
_NOTES_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────

def _find_latest(glob_pattern: str) -> Optional[Path]:
    files = sorted(_DATA_DIR.glob(glob_pattern), reverse=True)
    return files[0] if files else None


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _indicator(value) -> str:
    """Obsidian-compatible status indicator"""
    if value is True or value == "success":
        return "✅"
    if value is False or value == "failed":
        return "❌"
    if value == "no_change":
        return "🔄"
    return "—"


def _get_report_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _get_report_title() -> str:
    return f"规则演变报告 {_get_report_date()}"


# ──────────────────────────────────────────────
# 数据读取
# ──────────────────────────────────────────────

def _collect_data() -> dict:
    """聚合所有可用的审计数据源"""
    data = {
        "date": _get_report_date(),
        "scan": None,
        "rules_current": None,
        "rules_backup": None,
        "has_backup_diff": False,
    }

    # 最新哨兵报告
    sentinel_path = _find_latest("sentinel_*.json")
    if sentinel_path:
        data["scan"] = _load_json(sentinel_path)
        data["scan_filename"] = sentinel_path.name

    # 当前规则
    if _RULES_PATH.exists():
        data["rules_current"] = _load_json(_RULES_PATH)

    # 最新规则备份（用于 diff）
    backup_path = _find_latest("rules_backup_*.json")
    if backup_path:
        data["rules_backup"] = _load_json(backup_path)
        data["backup_filename"] = backup_path.name
        if data["rules_current"]:
            data["has_backup_diff"] = (
                data["rules_backup"].get("version") != data["rules_current"].get("version")
            )

    return data


# ──────────────────────────────────────────────
# 报告构建
# ──────────────────────────────────────────────

def _build_frontmatter(data: dict) -> str:
    tags = ["审计报告", "规则演变"]
    if data.get("scan"):
        tags.append("平台监控")
    if data.get("rules_current"):
        tags.append("规则库")

    return f"""---
tags: [{', '.join(tags)}]
date: {data['date']}
title: {_get_report_title()}
generator: obsidian_sync v2.0
status: 自动生成
---

"""


def _build_conclusion(data: dict) -> str:
    """结论先行 — 核心摘要"""
    lines = [
        "## 核心结论",
        "",
    ]
    scan = data.get("scan")
    rules = data.get("rules_current")
    backup = data.get("rules_backup")
    has_diff = data.get("has_backup_diff")

    # 平台扫描状态
    if scan:
        s = scan["summary"]
        ok = s["success"]
        fail = s["failed"]
        lines.append(f"- **平台扫描**: 成功 {ok} / 失败 {fail}")
        for t in scan.get("targets", []):
            indicator = _indicator(t["status"])
            count = len(t.get("articles", []))
            lines.append(f"  - {indicator} {t['platform_name']} — {t['label']} ({count} 条目)")
    else:
        lines.append("- **平台扫描**: 无数据")

    # 规则演变
    if rules:
        v = rules.get("version", "?")
        if has_diff and backup:
            old_v = backup.get("version", "?")
            lines.append(f"- **规则库**: v{old_v} → v{v}")
        else:
            lines.append(f"- **规则库**: v{v}（无变更）")
        risk_count = sum(
            len(rules.get("risk_levels", {}).get(l, {}).get("focus", {}))
            for l in ("HIGH", "MEDIUM", "LOW")
        )
        lines.append(f"- **风险词**: {risk_count} 个")
    else:
        lines.append("- **规则库**: 未加载")

    lines.append("")
    return "\n".join(lines)


def _build_platform_status(data: dict) -> str:
    scan = data.get("scan")
    if not scan:
        return ""

    lines = [
        "## 平台监控状态",
        "",
        f"扫描时间: {scan.get('scanned_at', '?')[:19]}",
        f"数据来源: ``{data.get('scan_filename', '?')}``",
        "",
        "| 平台 | 页面 | 状态 | 条目 |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for t in scan.get("targets", []):
        lines.append(
            f"| {t['platform_name']} | {t['label']} | {t['status']} | {len(t.get('articles', []))} |"
        )
    lines.append("")
    return "\n".join(lines)


def _build_risk_diff(data: dict) -> str:
    """对比备份与当前规则，列出新增风险词"""
    backup = data.get("rules_backup")
    current = data.get("rules_current")
    if not backup or not current:
        return ""

    lines = [
        "## 风险词变更",
        "",
    ]

    # 收集新旧词
    old_words = set()
    for level in ("HIGH", "MEDIUM", "LOW"):
        for word in backup.get("risk_levels", {}).get(level, {}).get("focus", {}):
            old_words.add(word)

    new_words = set()
    new_details = []
    for level in ("HIGH", "MEDIUM", "LOW"):
        focus = current.get("risk_levels", {}).get(level, {}).get("focus", {})
        for word, info in focus.items():
            if word not in old_words:
                new_words.add(word)
                new_details.append((level, word, info))

    if new_details:
        for level, word, info in new_details:
            lines.append(f"- **[{level}]** `{word}`")
            lines.append(f"  - 风险: {info.get('risk', '?')}")
            lines.append(f"  - 替换: {info.get('replace', '?')}")
        lines.append("")
    else:
        lines.append("无新增风险词。")
        lines.append("")

    return "\n".join(lines)


def _build_incentive_diff(data: dict) -> str:
    """对比备份与当前规则，列出新增激励点"""
    backup = data.get("rules_backup")
    current = data.get("rules_current")
    if not backup or not current:
        return ""

    lines = [
        "## 激励信号变更",
        "",
    ]

    # 收集新旧激励类别
    def _collect_cats(rules, level):
        items = rules.get("incentive_points", {}).get(level, [])
        return {i.get("category", "") for i in items if isinstance(i, dict)}

    new_cats = []
    for level in ("GREEN_HIGH", "GREEN_MEDIUM", "GREEN_LOW"):
        old = _collect_cats(backup, level)
        items = current.get("incentive_points", {}).get(level, [])
        for item in items:
            if isinstance(item, dict) and item.get("category", "") not in old:
                new_cats.append((level, item))

    if new_cats:
        for level, item in new_cats:
            lines.append(f"- **[{level}]** {item.get('category', '?')}")
            lines.append(f"  - {item.get('description', '?')}")
            indicators = item.get("indicators", [])
            if indicators:
                lines.append(f"  - 指标: {' / '.join(indicators[:3])}")
        lines.append("")
    else:
        lines.append("无新增激励信号。")
        lines.append("")

    return "\n".join(lines)


def _build_policy_fitness(data: dict) -> str:
    """当前规则政策契合度维度"""
    rules = data.get("rules_current")
    if not rules:
        return ""

    dims = rules.get("policy_fitness", {}).get("dimensions", [])
    if not dims:
        return ""

    lines = [
        "## 政策契合度维度",
        "",
        "| 维度 | 权重 | 说明 |",
        "| :--- | :--- | :--- |",
    ]
    for d in dims:
        lines.append(f"| {d['name']} | {d['weight']} | {d['description']} |")
    lines.append("")
    return "\n".join(lines)


def _build_action_items(data: dict) -> str:
    lines = [
        "## 行动清单",
        "",
    ]
    scan = data.get("scan")
    rules = data.get("rules_current")
    has_diff = data.get("has_backup_diff")

    if scan and any(t["status"] == "failed" for t in scan.get("targets", [])):
        lines.append("- [ ] 检查扫描失败的平台页面")
    if has_diff:
        lines.append("- [ ] 人工复核新增规则项")
        lines.append("- [ ] 更新规则测试用例")
    if rules:
        lines.append("- [ ] 检查规则覆盖是否完整")
    lines.append("- [ ] 排查新增违规案例")

    lines.append("")
    return "\n".join(lines)


def _build_wikilinks() -> str:
    """Obsidian [[双链]] 关联笔记"""
    return """## 关联笔记

- [[红灯避险]] — 违规风险拦截规则库
- [[绿灯起量]] — 平台激励信号识别库
- [[规则引擎]] — 审计核心引擎
- [[平台哨兵]] — 平台规则监控

---

*报告由 规则甄查 · 甄先生 v2.0 · obsidian_sync 自动生成*
"""


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def build_report() -> str:
    data = _collect_data()

    parts = [
        _build_frontmatter(data),
        _build_conclusion(data),
        _build_platform_status(data),
        _build_risk_diff(data),
        _build_incentive_diff(data),
        _build_policy_fitness(data),
        _build_action_items(data),
        _build_wikilinks(),
    ]

    return "\n".join(parts)


def sync():
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — Obsidian 同步")
    print("=" * 48)

    report = build_report()
    filename = f"{_get_report_date()} 规则演变报告.md"
    filepath = _NOTES_DIR / filename
    filepath.write_text(report, encoding="utf-8")

    print(f"\n[OUTPUT] notes/{filename}")
    print(f"[LINKS]  内置 [[双链]]: 红灯避险, 绿灯起量, 规则引擎, 平台哨兵")
    print("[DONE]\n")

    # 打印前 20 行预览
    for line in report.strip().split("\n")[:20]:
        print(f"  {line}")


if __name__ == "__main__":
    sync()
