#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 影子改写模拟器
===========================================
rules.json 更新后，用 3 个历史典型案例做影子改写对比。
若新规则导致质量评分大幅下降（>15%），锁定该规则并告警。

用法：
  python simulator_agent.py                          # 对比最新备份 vs 当前规则
  python simulator_agent.py --backup data/rules_backup_xxx.json  # 指定基准
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR / "data"
_RULES_PATH = _BASE_DIR / "rules.json"
_STATE_PATH = _DATA_DIR / "pipeline_state.json"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 质量下降阈值
_FITNESS_DROP_THRESHOLD = 15  # 百分点
_NEW_RISK_THRESHOLD = 2       # 允许新增风险数

_HISTORICAL_CASES = [
    "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！",
    "零成本创业，一学就会的赚钱方法。",
    "点击领取私信我，最快入账方式，绝对赚钱。",
]


# ──────────────────────────────────────────────
# 规则快照切换
# ──────────────────────────────────────────────

def _load_rules() -> dict:
    return json.loads(_RULES_PATH.read_text(encoding="utf-8"))


def _find_latest_backup() -> Optional[Path]:
    files = sorted(_DATA_DIR.glob("rules_backup_*.json"), reverse=True)
    return files[0] if files else None


# ──────────────────────────────────────────────
# 单案例影子审计
# ──────────────────────────────────────────────

def _score_case(text: str, rules: dict) -> dict:
    """用给定规则对文案跑审计，返回评分摘要"""
    # 临时替换 rules.json 并调用 audit_core
    import audit_core
    audit_core._invalidate_cache()

    # 注入规则
    audit_core._RULES_CACHE = rules
    # 但 _invalidate_cache 会置 None，需要重新加载
    audit_core._RULES_CACHE = rules  # 直接塞缓存

    result = audit_core.audit_dual(text)
    risk_count = len(result.get("risk_points", []))
    fitness = result.get("policy_fitness", {})
    total_score = fitness.get("total_score", 0)
    grade = fitness.get("grade", "")
    refined = result.get("refined_content", text)

    return {
        "text": text,
        "risk_count": risk_count,
        "fitness": total_score,
        "grade": grade,
        "refined": refined,
    }


def _assess_quality(new: dict, old: dict) -> dict:
    """对比新旧评分"""
    risk_delta = new["risk_count"] - old["risk_count"]
    fitness_delta = new["fitness"] - old["fitness"]

    degraded = False
    reasons = []

    if risk_delta > _NEW_RISK_THRESHOLD:
        degraded = True
        reasons.append(f"风险数 +{risk_delta}（阈值 {_NEW_RISK_THRESHOLD}）")
    if fitness_delta < -_FITNESS_DROP_THRESHOLD:
        degraded = True
        reasons.append(f"契合度 {fitness_delta:+.1f}（阈值 -{_FITNESS_DROP_THRESHOLD}）")

    return {
        "risk_delta": risk_delta,
        "fitness_delta": round(fitness_delta, 1),
        "degraded": degraded,
        "reasons": reasons,
    }


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def simulate(backup_path: Optional[Path] = None):
    """影子改写对比"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 影子改写模拟")
    print("=" * 48)

    # 1. 加载新旧规则
    if backup_path is None:
        backup_path = _find_latest_backup()
    if backup_path is None or not backup_path.exists():
        print("[SKIP] 无备份规则可做基线对比")
        return

    old_rules = json.loads(backup_path.read_text(encoding="utf-8"))
    new_rules = _load_rules()

    old_v = old_rules.get("version", "?")
    new_v = new_rules.get("version", "?")
    print(f"[RULES] v{old_v} → v{new_v}")
    print(f"[CASES] {len(_HISTORICAL_CASES)} 个影子案例\n")

    # 2. 逐个案例影子审计
    all_ok = True
    locked_rules = []
    results = []

    for text in _HISTORICAL_CASES:
        print(f"{'─' * 48}")
        print(f"  [CASE] {text[:40]}...")
        print(f"{'─' * 48}")

        old_score = _score_case(text, old_rules)
        new_score = _score_case(text, new_rules)

        assess = _assess_quality(new_score, old_score)

        print(f"  OLD: 风险 {old_score['risk_count']} | "
              f"契合度 {old_score['fitness']} | {old_score['grade']}")
        print(f"  NEW: 风险 {new_score['risk_count']} | "
              f"契合度 {new_score['fitness']} | {new_score['grade']}")
        print(f"  OLD: {old_score['refined'][:50]}...")
        print(f"  NEW: {new_score['refined'][:50]}...")

        if assess["degraded"]:
            print(f"  ⚠️ 质量下降:")
            for r in assess["reasons"]:
                print(f"    - {r}")
            all_ok = False
            locked_rules.append({
                "case": text[:40],
                "reasons": assess["reasons"],
                "risk_delta": assess["risk_delta"],
                "fitness_delta": assess["fitness_delta"],
            })
        else:
            print(f"  ✅ 质量正常")

        results.append({
            "case": text[:60],
            "old": old_score,
            "new": new_score,
            "assessment": assess,
        })

    # 3. 结论
    print(f"\n{'=' * 48}")
    print(f"  影子模拟结论")
    print(f"{'=' * 48}")

    if all_ok:
        print(f"  ✅ 所有案例质量正常，新规则安全")
        lock_status = "none"
    else:
        print(f"  ⚠️ {len(locked_rules)} 个案例质量下降")
        print(f"  [LOCK] 建议锁定新规则，回退至 v{old_v}")
        for lr in locked_rules:
            print(f"    - {lr['case']}: {'; '.join(lr['reasons'])}")
        lock_status = "recommended"

    # 4. 写回 pipeline_state
    report = {
        "simulated_at": datetime.now().isoformat(),
        "old_version": old_v,
        "new_version": new_v,
        "cases": len(_HISTORICAL_CASES),
        "degraded_count": len(locked_rules),
        "lock_status": lock_status,
        "details": results,
    }

    if _STATE_PATH.exists():
        state = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    else:
        state = {}
    state["shadow_simulation"] = report
    _STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[STATE] pipeline_state.json 已更新")

    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="影子改写模拟器")
    parser.add_argument("--backup", type=str, default=None, help="基准规则备份路径")
    args = parser.parse_args()
    backup = Path(args.backup) if args.backup else None
    simulate(backup)
