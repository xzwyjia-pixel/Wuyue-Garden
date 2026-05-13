# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 发布反馈监听器
===========================================
读取 data/feedback_*.xlsx → 分析各策略互动率 → 检测劣化 → 追加 Prompt 约束到 ai_refine_pro.py

检测到某类合规文案互动率大幅下降（默认 30%）时:
  1. 定位劣化模式（哪类替换词/哪种策略）
  2. 调用 DeepSeek 生成精准优化规则
  3. 自动追加到 ai_refine_pro.py 的改写原则列表
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import requests
import openpyxl

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_REFINE_PATH = Path(__file__).resolve().parent.parent.parent / "content_pipeline" / "ai_refine_pro.py"

_API_KEY = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
_API_URL = "https://api.deepseek.com/v1/chat/completions"
_MODEL = "deepseek-chat"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 互动率下降阈值
_DROP_THRESHOLD = 0.30

# 反馈 Excel 列名
_COLUMNS = [
    "case_id", "original_text", "refined_text", "strategy",
    "plays", "likes", "comments", "shares", "engagement_rate",
    "baseline_engagement",
]


# ──────────────────────────────────────────────
# 查找反馈文件
# ──────────────────────────────────────────────

def _find_feedback(max_files: int = 5) -> List[Path]:
    files = sorted(_DATA_DIR.glob("feedback_*.xlsx"), reverse=True)[:max_files]
    if not files:
        print("[FAIL] data/ 下无 feedback_*.xlsx")
        print("[HINT] 使用 --seed 生成示例数据")
    return files


# ──────────────────────────────────────────────
# 读取与解析反馈数据
# ──────────────────────────────────────────────

def _load_feedback(path: Path) -> list:
    """加载反馈 Excel，返回行字典列表"""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        print(f"[WARN] {path.name} 为空")
        return []

    header = [str(c).strip() if c else "" for c in rows[0]]
    data = []
    for row in rows[1:]:
        if not any(row):
            continue
        record = dict(zip(header, row))
        # 类型转换
        for num_col in ("plays", "likes", "comments", "shares", "engagement_rate", "baseline_engagement"):
            if num_col in record:
                try:
                    record[num_col] = float(record[num_col])
                except (ValueError, TypeError):
                    record[num_col] = 0.0
        data.append(record)
    wb.close()

    if data:
        print(f"[LOAD] {path.name} ({len(data)} 条)")
    return data


# ──────────────────────────────────────────────
# 策略表现分析
# ──────────────────────────────────────────────

def _analyze(data: list) -> dict:
    """按策略分组分析互动率变化"""
    from collections import defaultdict

    groups = defaultdict(list)
    for r in data:
        strategy = str(r.get("strategy", "unknown"))
        groups[strategy].append(r)

    analysis = {}
    for strategy, items in groups.items():
        engagements = [r.get("engagement_rate", 0) or 0 for r in items]
        baselines = [r.get("baseline_engagement", 0) or 0 for r in items]
        avg_eng = sum(engagements) / len(engagements) if engagements else 0
        avg_base = sum(baselines) / len(baselines) if baselines else 0

        drop = 0
        if avg_base > 0:
            drop = (avg_base - avg_eng) / avg_base

        analysis[strategy] = {
            "count": len(items),
            "avg_engagement": round(avg_eng, 4),
            "avg_baseline": round(avg_base, 4),
            "drop_pct": round(drop, 4),
            "degraded": drop >= _DROP_THRESHOLD,
            "records": items,
        }

    return analysis


def _find_degraded_patterns(analysis: dict, data: list) -> list:
    """
    定位具体劣化模式:
    - 哪些策略劣化
    - 哪些记录互动率最低
    """
    findings = []

    for strategy, info in analysis.items():
        if not info["degraded"]:
            continue

        sorted_records = sorted(info["records"], key=lambda r: r.get("engagement_rate", 0) or 0)
        worst = sorted_records[:3]

        for rec in worst:
            findings.append({
                "strategy": strategy,
                "original": rec.get("original_text", ""),
                "refined": rec.get("refined_text", ""),
                "engagement": rec.get("engagement_rate", 0),
                "baseline": rec.get("baseline_engagement", 0),
                "drop": info["drop_pct"],
            })

    return findings


# ──────────────────────────────────────────────
# DeepSeek: 生成优化规则
# ──────────────────────────────────────────────

_OPT_PROMPT = """你是一位短视频文案策略分析师。分析以下改写导致的互动率劣化案例，生成一条精炼的改写约束规则。

劣化策略: {strategy}
劣化幅度: {drop_pct}%
案例:
  原文: {original}
  改写后: {refined}
  原互动率: {baseline}
  现互动率: {current}

要求:
- 生成一条可操作的改写约束，追加到改写原则列表中
- 保持「静奢风」调性：克制、精密、不损失表达效果
- 定位具体问题（如某类替换过于生硬、情绪流失、信息密度下降）
- 格式: "编号. 规则描述"
- 仅输出规则文本，不要解释，不要多余格式"""


def _gen_optimization_rule(findings: list) -> Optional[str]:
    """调用 DeepSeek 生成优化规则"""
    if not findings:
        return None

    # 取最差的案例
    worst = max(findings, key=lambda f: f["drop"])

    prompt = _OPT_PROMPT.format(
        strategy=worst["strategy"],
        drop_pct=round(worst["drop"] * 100, 1),
        original=worst["original"][:100],
        refined=worst["refined"][:100],
        baseline=worst["baseline"],
        current=worst["engagement"],
    )

    try:
        resp = requests.post(
            _API_URL,
            headers={"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": "你输出中文文案优化规则。仅输出规则文本。不要解释。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 256,
            },
            timeout=30,
        )
        resp.raise_for_status()
        rule_text = resp.json()["choices"][0]["message"]["content"].strip()
        # 清理引号
        rule_text = rule_text.strip("\"'")
        print(f"[AI-RULE] {rule_text[:80]}...")
        return rule_text
    except Exception as e:
        print(f"[FAIL] DeepSeek 规则生成失败: {e}")
        return None


def _gen_fallback_rule(findings: list) -> str:
    """AI 不可用时的规则兜底"""
    worst = max(findings, key=lambda f: f["drop"])
    return (
        f"5. 互动率保护：改写时保留文案的情绪价值和信息密度，"
        f"避免过度替换导致表达生硬（参考: {worst['strategy']} 策略互动率下降 {round(worst['drop']*100,1)}%）"
    )


# ──────────────────────────────────────────────
# 追加到 ai_refine_pro.py
# ──────────────────────────────────────────────

def _append_rule(rule_text: str) -> bool:
    """将规则追加到 _REFINE_SYSTEM_PROMPT 的改写原则列表末尾"""
    if not rule_text:
        return False

    # 标准化 rule_text: 去掉编号，生成新的编号
    rule_text = re.sub(r"^\d+\.\s*", "", rule_text).strip()

    source = _REFINE_PATH.read_text(encoding="utf-8")

    # 找到改写原则最后一条插入点：line with "4. 合规优先"
    marker = "4. 合规优先：任何时候安全合规大于表达效果"
    if marker not in source:
        print(f"[FAIL] 未找到规则锚点行")
        return False

    new_rule_line = f"\n5. {rule_text}"
    modified = source.replace(marker, marker + new_rule_line)

    # 备份
    backup = _DATA_DIR / f"ai_refine_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    backup.write_text(source, encoding="utf-8")
    print(f"[BACKUP] {backup.name}")

    # 写入
    _REFINE_PATH.write_text(modified, encoding="utf-8")
    print(f"[MODIFY] ai_refine_pro.py — 追加原则5")
    return True


# ──────────────────────────────────────────────
# 种子数据生成
# ──────────────────────────────────────────────

def seed_sample_data():
    """生成模拟反馈数据供测试"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _DATA_DIR / f"feedback_seed_{ts}.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "发布反馈"
    ws.append(_COLUMNS)

    samples = [
        # (case_id, original, refined, strategy, plays, likes, comments, shares, baseline)
        ("A001", "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！",
         "业内深耕，追求极致。长期合规运营，确定性资产增值逻辑。后台留言获取详情页入口。",
         "standard", 5200, 89, 12, 5, 0.035),
        ("A002", "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！",
         "本内容为业内深耕的深度分析，致力于资产增值逻辑的长期合规运营。欢迎后台留言获取详情。",
         "aggressive", 4800, 42, 8, 3, 0.035),
        ("B001", "零成本创业，一学就会的赚钱方法。",
         "零成本起步，一学即会的资产增值逻辑。",
         "standard", 8300, 215, 34, 28, 0.028),
        ("B002", "零成本创业，一学就会的赚钱方法。",
         "零成本起步新路径，掌握资产增值的核心逻辑。原创内容，仅供参考。",
         "aggressive", 7900, 98, 15, 11, 0.028),
        ("C001", "点击领取私信我，最快入账方式，绝对赚钱。",
         "后台留言获取深度交流，核心入账路径，确定性资产增值。",
         "standard", 3500, 155, 22, 18, 0.048),
        ("C002", "点击领取私信我，最快入账方式，绝对赚钱。",
         "欢迎后台交流，获取核心入账路径与资产增值方案。本内容仅供学习参考。",
         "aggressive", 3100, 62, 9, 6, 0.048),
        # 高互动率对照
        ("D001", "今天教大家一个实用小技巧，学会能省不少钱。",
         "今天分享一个实用小技巧，掌握后可以优化日常开支。",
         "standard", 12000, 580, 92, 45, 0.052),
        ("D002", "今天教大家一个实用小技巧，学会能省不少钱。",
         "今天分享一个实用技巧，帮助你优化日常开支结构。原创经验，亲测有效。",
         "aggressive", 11500, 510, 78, 40, 0.052),
    ]

    for s in samples:
        case_id, orig, refined, strategy, plays, likes, comments, shares, baseline = s
        engagement = (likes + comments + shares) / plays if plays > 0 else 0
        ws.append([case_id, orig, refined, strategy, plays, likes, comments, shares,
                   round(engagement, 4), baseline])

    # 样式
    from openpyxl.styles import Font, PatternFill
    for col in range(1, len(_COLUMNS) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")

    wb.save(str(path))
    print(f"[SEED] {path.name} ({len(samples)} 条)")
    return path


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def listen(feedback_paths: Optional[List[Path]] = None):
    """监听反馈 → 分析 → 优化"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 发布反馈监听器")
    print("=" * 48)

    # 1. 加载反馈
    if not feedback_paths:
        feedback_paths = _find_feedback()
    if not feedback_paths:
        return

    all_data = []
    for fp in feedback_paths:
        all_data.extend(_load_feedback(fp))

    if not all_data:
        print("[FAIL] 无有效反馈数据")
        return

    print(f"[DATA] 共 {len(all_data)} 条记录")

    # 2. 分组分析
    analysis = _analyze(all_data)
    print(f"\n[ANALYSIS] 策略表现:")
    for strategy, info in analysis.items():
        status = "⚠️ 劣化" if info["degraded"] else "✅ 正常"
        print(f"  {strategy:<12} 互动率 {info['avg_engagement']:.4f}  "
              f"(基线 {info['avg_baseline']:.4f}, 变化 {info['drop_pct']*100:+.1f}%)  {status}")

    # 3. 检测劣化
    degraded = [s for s, i in analysis.items() if i["degraded"]]
    if not degraded:
        print(f"\n[PASS] 无策略互动率显著劣化（阈值: {_DROP_THRESHOLD*100:.0f}%）")
        return

    print(f"\n[DEGRADE] {len(degraded)} 个策略互动率下降")
    findings = _find_degraded_patterns(analysis, all_data)

    # 4. 生成优化规则
    print(f"\n[OPT] 生成优化规则...")
    rule = _gen_optimization_rule(findings)
    if not rule:
        print(f"[FALLBACK] 使用规则兜底")
        rule = _gen_fallback_rule(findings)

    print(f"[RULE] {rule}")

    # 5. 追加到 ai_refine_pro.py
    success = _append_rule(rule)
    if success:
        print(f"\n[DONE] Prompt 已追加，下次 AI 改写将应用新约束。")

    # 6. 报告
    print(f"\n{'─' * 48}")
    print("  FEEDBACK REPORT")
    print(f"{'─' * 48}")
    for f in findings[:5]:
        print(f"  {f['strategy']:<12} 互动率 {f['engagement']:.4f} (基线 {f['baseline']:.4f})")
        print(f"  ├ 原文: {f['original'][:40]}...")
        print(f"  └ 改写: {f['refined'][:40]}...")
        print()
    print(f"[DONE] 反馈监听完成")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="发布反馈监听器 — 分析互动率并优化改写策略")
    parser.add_argument("--seed", action="store_true", help="生成示例反馈数据")
    parser.add_argument("--threshold", type=float, default=_DROP_THRESHOLD,
                        help=f"互动率下降阈值（默认 {_DROP_THRESHOLD}）")
    args = parser.parse_args()

    if args.seed:
        seed_sample_data()
    else:
        # 若有新种子数据，优先使用
        feedback_files = _find_feedback()
        if not feedback_files:
            print("[HINT] 先运行 --seed 生成示例数据")
        else:
            listen(feedback_files)
