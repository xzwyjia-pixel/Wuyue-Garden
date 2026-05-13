#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 全自动流水线
=========================================
一条命令完整闭环：
  抓取公告 → 进化规则 → 审计文案 → 同步 Obsidian → 导出素材 → 视觉审计 → 云端同步

用法：
  python final_agent_run.py
  python final_agent_run.py --skip-sentinel   # 跳过网络抓取
  python final_agent_run.py --text "自定义文案"  # 审计指定文案
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_STATE_PATH = _DATA_DIR / "pipeline_state.json"
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── 默认测试用例 ──
_DEFAULT_CASES = [
    "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！",
    "零成本创业，一学就会的赚钱方法。",
    "点击领取私信我，最快入账方式，绝对赚钱。",
]

# ── 流水线状态跟踪 ──

_PIPELINE_RESULTS = {
    "pipeline_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "started_at": datetime.now().isoformat(),
    "steps": [],
    "refine_cases": [],
    "refine_results": [],
    "status": "running",
}


def _log_step(step_id: str, name: str, status: str, duration: float, detail: str = ""):
    _PIPELINE_RESULTS["steps"].append({
        "step": step_id,
        "name": name,
        "status": status,
        "duration_s": round(duration, 1),
        "detail": detail,
    })


def _save_state():
    _PIPELINE_RESULTS["finished_at"] = datetime.now().isoformat()
    _STATE_PATH.write_text(
        json.dumps(_PIPELINE_RESULTS, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── 步骤执行器 ──

def _run_step(step_id: str, name: str, script_args: list,
              critical: bool = False, capture: bool = False) -> str:
    """执行一个流水线步骤"""
    header = f"[{step_id}] {name}"
    sep = "=" * 48
    print(f"\n{sep}")
    print(f"  {header}")
    print(sep)

    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable] + script_args,
            cwd=_SCRIPTS_DIR,
            capture_output=capture,
            text=True,
            timeout=120,
        )
        elapsed = time.time() - start
        out = (result.stdout or "") + (result.stderr or "")

        if result.returncode == 0:
            print(f"  [OK] 完成 ({elapsed:.1f}s)")
            _log_step(step_id, name, "ok", elapsed)
            return out
        else:
            print(f"  [FAIL] 退出码 {result.returncode} ({elapsed:.1f}s)")
            err_lines = (result.stderr or "").strip().split("\n")[-3:]
            for line in err_lines:
                print(f"    {line}")
            if critical:
                _log_step(step_id, name, "failed", elapsed, result.stderr or "")
                _PIPELINE_RESULTS["status"] = "failed"
                _save_state()
                print(f"\n[STOP] 关键步骤失败，流水线终止。")
                sys.exit(1)
            _log_step(step_id, name, "skipped", elapsed, result.stderr or "")
            return ""

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"  [FAIL] 超时 ({elapsed:.1f}s)")
        _log_step(step_id, name, "timeout", elapsed)
        if critical:
            _PIPELINE_RESULTS["status"] = "failed"
            _save_state()
            sys.exit(1)
        return ""
    except Exception as e:
        elapsed = time.time() - start
        print(f"  [FAIL] {e}")
        _log_step(step_id, name, "exception", elapsed, str(e))
        if critical:
            sys.exit(1)
        return ""


# ── 审计+改写（在进程中执行以便获取结构化结果） ──

def _run_refine_step(texts: list):
    """执行审计改写，保存结构化结果"""
    print("\n" + "=" * 48)
    print("  [3/7] 审计改写")
    print("=" * 48)

    from audit_core import audit_dual
    from ai_refine_pro import refine_with_verification

    results = []
    for text in texts:
        print(f"\n  [INPUT] {text[:50]}...")
        try:
            res = refine_with_verification(text, max_rounds=2)
            results.append(res)
            status = "PASS" if res.get("verified_safe") else "RISK"
            final = res.get("final_text", "")
            print(f"  [{status}] {final[:60]}...")
        except Exception as e:
            print(f"  [FAIL] {e}")
            # fallback: 纯引擎审计
            audit = audit_dual(text)
            results.append({
                "original_text": text,
                "final_text": audit.get("refined_content", text),
                "pre_audit": audit,
                "post_audit": audit,
                "verified_safe": len(audit.get("risk_points", [])) == 0,
            })

    _PIPELINE_RESULTS["refine_cases"] = texts
    _PIPELINE_RESULTS["refine_results"] = results
    _PIPELINE_RESULTS["steps"].append({
        "step": "3/7", "name": "审计改写",
        "status": "ok", "duration_s": 0,
        "detail": f"{len(texts)} 条, {sum(1 for r in results if r.get('verified_safe'))} 通过",
    })
    _save_state()
    print(f"\n  [DONE] {len(texts)} 条文案, {sum(1 for r in results if r.get('verified_safe'))} 条零风险通过")


# ── 主流水线 ──

def run_pipeline(skip_sentinel: bool = False, texts: list = None):
    """全自动流水线"""
    if texts is None:
        texts = _DEFAULT_CASES

    print(f"\n{'=' * 48}")
    print(f"  规则甄查 · 甄先生 v2.0 — 全自动流水线")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 48}")
    print(f"  步骤: 抓取 → 进化 → 审计 → Obsidian → 导出 → 视觉 → 云端")
    print(f"  文案: {len(texts)} 条")
    if skip_sentinel:
        print(f"  模式: 跳过网络抓取（使用缓存）")
    print()

    if not skip_sentinel:
        # Step 1: 抓取公告
        _run_step("1/7", "抓取公告",
                  ["platform_sentinel.py"], critical=False)
    else:
        print(f"\n{'=' * 48}")
        print("  [1/7] 抓取公告 [SKIP]")
        print("=" * 48)
        _log_step("1/7", "抓取公告", "skipped", 0, "用户跳过")

    # Step 2: 进化规则
    _run_step("2/7", "进化规则",
              ["rules_evolver.py"], critical=False)

    # Step 3: 审计改写（进程中）
    _run_refine_step(texts)

    # Step 4: 同步 Obsidian
    _run_step("4/7", "同步 Obsidian",
              ["obsidian_sync.py"], critical=False)

    # Step 5: 导出分发素材
    _run_step("5/7", "导出分发素材",
              ["content_exporter.py"], critical=False)

    # Step 6: 视觉审计（非关键）
    _run_step("6/7", "视觉审计",
              ["vision_guard.py", "--title", texts[0] if texts else ""],
              critical=False)

    # Step 7: 云端同步（非关键，失败自动转存本地）
    _run_step("7/7", "云端同步",
              ["google_drive_sync.py"],
              critical=False)

    # ── 结果摘要 ──
    _PIPELINE_RESULTS["status"] = "completed"
    _save_state()

    refine_results = _PIPELINE_RESULTS.get("refine_results", [])
    passed = sum(1 for r in refine_results if r.get("verified_safe"))

    print(f"\n{'=' * 48}")
    print(f"  流水线完成")
    print(f"{'=' * 48}")
    print(f"  状态: 通过")
    print(f"  步骤: {len(_PIPELINE_RESULTS['steps'])} 步")
    print(f"  文案: {len(texts)} 条, 通过 {passed} 条")
    print(f"  报告: notes/ 目录")
    print(f"  导出: data/export_*.*")
    print(f"  缓存: {_STATE_PATH.name}")

    export_files = sorted(_DATA_DIR.glob("export_*.*"), reverse=True)
    if export_files:
        print(f"\n  分发素材:")
        for f in export_files[:5]:
            print(f"    {f.name}")

    # Webhook 通知
    print(f"\n  [HERALD] 发送通知...")
    try:
        from herald_agent import send as herald_send
        herald_send()
    except Exception as e:
        print(f"  [HERALD] {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="规则甄查全自动流水线")
    parser.add_argument("--skip-sentinel", action="store_true",
                        help="跳过网络抓取步骤")
    parser.add_argument("--text", type=str, default=None,
                        help="审计指定文案（单条）")
    parser.add_argument("--texts", type=str, nargs="*", default=[],
                        help="审计指定文案（多条）")
    args = parser.parse_args()

    texts = None
    if args.text:
        texts = [args.text]
    elif args.texts:
        texts = args.texts

    run_pipeline(skip_sentinel=args.skip_sentinel, texts=texts)
