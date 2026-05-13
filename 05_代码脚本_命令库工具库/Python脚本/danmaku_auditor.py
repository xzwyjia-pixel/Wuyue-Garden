# -*- coding: utf-8 -*-
"""
抖音直播间弹幕敏感词甄查工具
规则引擎：加载 rules.json 敏感词库，逐条检测弹幕文本。
输入：CSV 文件（每行一条弹幕）或 stdin 实时管道
输出：违规弹幕列表 + 风险等级 + 替换建议
"""

import csv
import json
import sys
import os
from datetime import datetime
from typing import Optional

RULES_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "01-Production/规则甄查系统/rules.json",
)


def load_rules(path: str = RULES_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_rules(rules: dict) -> list[dict]:
    """Flatten nested rule structure into flat keyword→rule list."""
    flat = []
    for level, info in rules.get("risk_levels", {}).items():
        for keyword, detail in info.get("focus", {}).items():
            flat.append({
                "keyword": keyword,
                "risk_level": level,
                "category": info.get("category", ""),
                "risk": detail.get("risk", ""),
                "replace": detail.get("replace", ""),
                "policy_ref": detail.get("policy_ref", ""),
            })
    return flat


def audit_danmaku(text: str, rules_flat: list[dict]) -> list[dict]:
    """Check single danmaku against all rules. Return matched violations."""
    results = []
    for rule in rules_flat:
        kw = rule["keyword"]
        if kw and kw.lower() in text.lower():
            results.append({
                "keyword": kw,
                "risk_level": rule["risk_level"],
                "category": rule["category"],
                "risk_desc": rule["risk"],
                "suggestion": rule["replace"],
                "policy_ref": rule["policy_ref"],
            })
    return results


def process_file(filepath: str, rules_flat: list[dict]) -> list[dict]:
    """Process CSV or plain text file. CSV needs 'content' column."""
    records = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # Try CSV first
            sample = f.read(4096)
            f.seek(0)
            if "," in sample or "\t" in sample:
                reader = csv.DictReader(f)
                for row in reader:
                    text = row.get("content") or row.get("text") or row.get("danmaku") or ""
                    if text.strip():
                        records.append(text.strip())
            else:
                # Plain text: one danmaku per line
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(line)
    except FileNotFoundError:
        print(f"[-] File not found: {filepath}")
        return []
    return records


def main():
    import argparse

    parser = argparse.ArgumentParser(description="抖音弹幕敏感词甄查工具")
    parser.add_argument("input", nargs="?", help="输入文件（CSV 或 txt），缺省从 stdin 读取")
    parser.add_argument("--rules", default=RULES_PATH, help="rules.json 路径")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    # Load rules
    try:
        rules = load_rules(args.rules)
    except FileNotFoundError:
        print(f"[-] rules.json not found at: {args.rules}")
        sys.exit(1)

    flat = flatten_rules(rules)
    total_rules = len(flat)
    print(f"[*] 已加载 {total_rules} 条敏感词规则\n", file=sys.stderr)

    # Collect input
    danmaku_list = []
    if args.input:
        danmaku_list = process_file(args.input, flat)
    else:
        # Stdin: one danmaku per line
        for line in sys.stdin:
            line = line.strip()
            if line:
                danmaku_list.append(line)

    if not danmaku_list:
        print("[-] 无输入弹幕", file=sys.stderr)
        sys.exit(0)

    # Audit
    violations = []
    for dm in danmaku_list:
        hits = audit_danmaku(dm, flat)
        if hits:
            violations.append({"danmaku": dm, "hits": hits})

    # Report
    if args.json:
        print(json.dumps({
            "total_scanned": len(danmaku_list),
            "violations_found": len(violations),
            "timestamp": datetime.now().isoformat(),
            "results": violations,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  弹幕敏感词甄查报告")
        print(f"  扫描: {len(danmaku_list)} 条 | 违规: {len(violations)} 条")
        print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        if not violations:
            print("  ✅ 无违规弹幕\n")
            return

        for v in violations:
            print(f"  🚫 弹幕: {v['danmaku']}")
            for h in v["hits"]:
                print(f"     ├─ 命中词: [{h['keyword']}]")
                print(f"     ├─ 风险:    {h['risk_level']} | {h['category']}")
                print(f"     ├─ 说明:    {h['risk_desc']}")
                print(f"     └─ 建议:    {h['suggestion']}")
                print(f"        (参考: {h['policy_ref']})")
            print()


if __name__ == "__main__":
    main()
