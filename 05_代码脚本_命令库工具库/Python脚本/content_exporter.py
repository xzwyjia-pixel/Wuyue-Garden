# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 分发素材导出器
===========================================
输入：审计改写结果 JSON (data/latest_refine_results.json)
输出1：视频号助手 Excel 模板 (data/export_*.xlsx)
输出2：剪映草稿说明文本   (data/export_*.txt)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_STATE_PATH = _DATA_DIR / "pipeline_state.json"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── 视频号助手 Excel 模板样式 ──
_HEADER_FONT = Font(name="微软雅黑", bold=True, size=11, color="FFFFFF")
_HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
_CELL_FONT = Font(name="微软雅黑", size=10)
_WRAP = Alignment(wrap_text=True, vertical="top")
_THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)

_VIDEOHEADER = ["视频文件", "标题", "简介", "话题标签", "风险等级", "备注"]


def _style_sheet(ws, headers: List[str]):
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = _HEADER_FONT
        cell.fill = _HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = _THIN_BORDER


def _style_cell(cell):
    cell.font = _CELL_FONT
    cell.alignment = _WRAP
    cell.border = _THIN_BORDER


# ──────────────────────────────────────────────
# 读取改写结果
# ──────────────────────────────────────────────

def load_refine_results() -> Optional[list]:
    """从 pipeline_state.json 读取最新改写结果"""
    if not _STATE_PATH.exists():
        print(f"[WARN] 未找到 {_STATE_PATH}")
        return None
    state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    return state.get("refine_results")


def load_test_cases_from_state() -> list:
    """读取 pipeline 状态的测试用例"""
    if not _STATE_PATH.exists():
        return []
    state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    return state.get("refine_cases", [])


# ──────────────────────────────────────────────
# 导出 1：视频号助手 Excel
# ──────────────────────────────────────────────

def export_video_account_excel(
    cases: List[str],
    results: List[dict],
    filepath: Optional[Path] = None,
) -> Path:
    """生成视频号助手批量上传 Excel"""
    if filepath is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = _DATA_DIR / f"export_video_{ts}.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "视频号助手导入"
    _style_sheet(ws, _VIDEOHEADER)

    for i, (text, res) in enumerate(zip(cases, results), 2):
        final_text = res.get("final_text", res.get("post_audit", {}).get("refined_content", text))
        verified = res.get("verified_safe", False)
        risk_count = len(res.get("pre_audit", {}).get("risk_points", []))

        row = [
            f"video_{i:03d}.mp4",           # 视频文件（占位）
            final_text[:30] + ("..." if len(final_text) > 30 else ""),  # 标题
            final_text,                       # 简介（完整合规文案）
            "#合规内容 #原创 #知识分享",       # 话题标签
            "通过" if verified else f"{risk_count}项风险",  # 风险等级
            "AI优化" if verified else "需人工复核",        # 备注
        ]
        for col, val in enumerate(row, 1):
            cell = ws.cell(row=i, column=col, value=val)
            _style_cell(cell)

    # 列宽
    widths = [30, 35, 60, 25, 12, 14]
    for col, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    wb.save(str(filepath))
    print(f"[EXCEL] {filepath.name} ({len(cases)} 条)")
    return filepath


# ──────────────────────────────────────────────
# 导出 2：剪映草稿说明文本
# ──────────────────────────────────────────────

def export_jianying_drafts(
    cases: List[str],
    results: List[dict],
    filepath: Optional[Path] = None,
) -> Path:
    """生成适合导入剪映的字幕/口播草稿"""
    if filepath is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = _DATA_DIR / f"export_jianying_{ts}.txt"

    lines = [
        "=" * 48,
        "  规则甄查 · 甄先生 v2.0 — 剪映草稿",
        f"  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 48,
        "",
    ]

    for i, (text, res) in enumerate(zip(cases, results), 1):
        verified = res.get("verified_safe", False)
        final_text = res.get("final_text", res.get("post_audit", {}).get("refined_content", text))
        pre_audit = res.get("pre_audit", {})
        post_audit = res.get("post_audit", {})

        pre_risks = pre_audit.get("risk_points", [])
        post_risks = post_audit.get("risk_points", [])
        pre_fit = pre_audit.get("policy_fitness", {})
        post_fit = post_audit.get("policy_fitness", {})

        lines.append(f"─── 案例 {i} {'✅' if verified else '⚠️'} ───")
        lines.append(f"")
        lines.append(f"[原始文案]")
        lines.append(f"{text}")
        lines.append(f"")
        lines.append(f"[发布文案]")
        lines.append(f"{final_text}")
        lines.append(f"")

        # 逐段分解（按标点分行，适合剪映逐段导入）
        import re
        sentences = re.split(r'[。！？；]', final_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 1:
            lines.append(f"[分段口播 · 可逐段导入剪映字幕]")
            for j, sent in enumerate(sentences, 1):
                lines.append(f"  段{j}: {sent}。")
            lines.append(f"")

        lines.append(f"[审计摘要]")
        lines.append(f"  风险: {len(pre_risks)} → {len(post_risks)}")
        pre_score = pre_fit.get("total_score", "?") if pre_fit else "?"
        post_score = post_fit.get("total_score", "?") if post_fit else "?"
        lines.append(f"  政策契合度: {pre_score} → {post_score}")
        lines.append(f"  状态: {'✅ 零风险通过' if verified else '⚠️ 仍有风险, 建议人工调整'}")
        lines.append(f"")

    lines.append("=" * 48)
    lines.append("  由规则甄查 · 甄先生 v2.0 · content_exporter 生成")
    lines.append("=" * 48)

    text = "\n".join(lines)
    filepath.write_text(text, encoding="utf-8")
    print(f"[JIANYING] {filepath.name} ({len(cases)} 条)")
    return filepath


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

def export_all(cases: list, results: list):
    """导出全部分发素材"""
    excel_path = export_video_account_excel(cases, results)
    jy_path = export_jianying_drafts(cases, results)
    return excel_path, jy_path


if __name__ == "__main__":
    results = load_refine_results()
    if results:
        cases = load_test_cases_from_state()
        if not cases:
            cases = [r.get("original_text", f"案例{i+1}") for i, r in enumerate(results)]
        export_all(cases, results)
    else:
        # 独立模式：从命令行读取文案
        import argparse
        parser = argparse.ArgumentParser(description="导出分发素材")
        parser.add_argument("texts", nargs="*", help="待导出文案")
        args = parser.parse_args()

        if args.texts:
            from audit_core import audit_dual
            cases = args.texts
            results = []
            for text in cases:
                audit = audit_dual(text)
                results.append({
                    "original_text": text,
                    "final_text": audit.get("refined_content", text),
                    "pre_audit": audit,
                    "post_audit": audit,
                    "verified_safe": len(audit.get("risk_points", [])) == 0,
                })
            export_all(cases, results)
        else:
            print("用法: python content_exporter.py <文案1> [文案2 ...]")
            print("      或通过 pipeline_state.json 提供输入")
