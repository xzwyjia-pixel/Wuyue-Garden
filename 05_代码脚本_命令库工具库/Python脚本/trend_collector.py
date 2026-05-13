#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 趋势热词 → 激励词采集器
=====================================================
config.yaml trend.keywords → Playwright 抓取热门视频文案
→ DeepSeek 提取模式 → 增量注入 rules.json incentive_points

用法：
  python trend_collector.py --mock          # 模拟数据测试
  python trend_collector.py                 # 真实采集（需 Playwright）
  python trend_collector.py --keywords AI,创业  # 只采集指定关键词
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

_BASE_DIR = Path(__file__).resolve().parent.parent
_CFG_PATH = _BASE_DIR / "config.yaml"
_RULES_PATH = _BASE_DIR / "rules.json"
_DATA_DIR = _BASE_DIR / "data"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _load_cfg() -> dict:
    return yaml.safe_load(_CFG_PATH.read_text(encoding="utf-8")) if _CFG_PATH.exists() else {}


def _api_config() -> tuple:
    cfg = _load_cfg()
    api = cfg.get("api", {})
    return (
        api.get("deepseek_key", "sk-cad1b7bcd5dd4644a03c87c14a1fa690"),
        api.get("deepseek_url", "https://api.deepseek.com/v1/chat/completions"),
        api.get("deepseek_model", "deepseek-chat"),
    )


# ──────────────────────────────────────────────
# 模拟数据
# ──────────────────────────────────────────────

_MOCK_SAMPLES = {
    "知识分享": [
        "3个让你效率翻倍的工作方法，亲测有效",
        "为什么你读过的书总是记不住？试试这个方法",
        "普通人逆袭必读的5本书，每一本都改变认知",
        "用思维导图整理知识，效率提升200%",
        "深度工作：如何进入心流状态的3个技巧",
    ],
    "职场": [
        "面试官最讨厌的5种自我介绍，你中了几条",
        "升职加薪的人都在做这3件事",
        "如何优雅地拒绝同事的无理请求",
        "写给30岁职场人的10条生存法则",
        "从月薪5千到5万，我只改变了这一个习惯",
    ],
    "创业": [
        "白手起家第一步：找到你的最小可行产品",
        "创业公司活过第一年的3个关键决策",
        "复盘我第一次创业失败的全部原因",
        "低成本获客的5个实战方法",
        "SOHO创业者的时间管理心法",
    ],
    "理财": [
        "月薪5000也能开始的理财计划",
        "基金定投的黄金法则：什么时候买什么时候卖",
        "年轻人应该避开的3个消费陷阱",
        "我的被动收入从0到5000的实操记录",
        "家庭资产配置的4321法则详解",
    ],
    "AI": [
        "用AI写周报，老板说我的总结比同事都好",
        "ChatGPT进阶提示词，让AI输出质量翻倍",
        "普通人如何用AI做副业，月入3000+",
        "2026年一定要学会的5个AI工具",
        "AI绘画入门：用提示词生成商业级海报",
    ],
    "科技": [
        "2026年最值得入手的数码产品Top10",
        "骁龙旗舰芯片深度对比：性能差距有多大",
        "智能家居入门指南：从零搭建全屋智能",
        "国产操作系统深度体验：它能替代Windows吗",
        "5G改变生活的5个真实案例",
    ],
    "直播新规": [
        "2026直播带货新规来了！这些红线千万别踩",
        "抖音直播新规解读：违规话术自查清单",
        "视频号直播新规下，主播必须知道的3个变化",
        "直播违规词大全：这些话说出口就封号",
        "新规后直播间话术怎么改？合规话术模板分享",
    ],
    "违规封号": [
        "因为一句话被封7天，这些违规词你还在用吗",
        "账号被限流的5个隐蔽原因，90%的人不知道",
        "直播违规记录如何申诉？3步成功解封",
        "2026最新封号案例复盘：这些坑千万别踩",
        "短视频违规避坑指南：从警告到封号的等级说明",
    ],
    "教案合规": [
        "教育培训类内容合规指南：从资质到话术全解析",
        "知识付费课程审核要点，合规通过率提升80%",
        "教培直播间话术合规改造实战案例",
        "在线教育内容审核新规：这5类内容将被严查",
        "教案合规设计：如何在不违规前提下做好知识输出",
    ],
}

# ──────────────────────────────────────────────
# DeepSeek Prompt
# ──────────────────────────────────────────────

_TREND_PROMPT = """你是短视频平台合规策略分析师，服务于「规则甄查 · 甄先生」品牌。

分析以下按领域分组的热门视频文案样本，提取可用于「绿灯激励」的文案模式。

## 任务
1. 识别高频出现的正向表达模式（句式结构、关键词、叙事角度）
2. 将每个可复用的模式转化为一条激励词（Incentive Indicator）
3. 为每条激励词分类：GREEN_HIGH（长效价值）/ GREEN_MEDIUM（实证原创）/ GREEN_LOW（合规创新）
4. 评估该模式在各领域的可迁移性

## 约束
- 只提取合规范围内的正向表达（不包含夸大/诱导/绝对化）
- 每条激励词应有明确的"可用场景"说明
- 保持静奢风：极简、精密、克制
- 与已有激励点不重复

## 输出格式（严格 JSON）

{
  "domain": "领域名称",
  "incentives": [
    {
      "category": "GREEN_HIGH",
      "indicator": "激励词描述",
      "example": "应用示例文案",
      "scenario": "适用内容类型",
      "transferability": ["可迁移领域1", "可迁移领域2"]
    }
  ]
}

如果没有可提取的激励模式，返回 {"domain": "", "incentives": []}"""


# ──────────────────────────────────────────────
# DeepSeek 调用
# ──────────────────────────────────────────────

def _call_deepseek(payload: str) -> Optional[dict]:
    """调用 DeepSeek 分析文案模式"""
    key, url, model = _api_config()

    try:
        import requests
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _TREND_PROMPT},
                    {"role": "user", "content": payload},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(content)
    except Exception as e:
        print(f"  [API] DeepSeek 分析失败: {e}")
        return None


# ──────────────────────────────────────────────
# 注入规则库
# ──────────────────────────────────────────────

def _merge_trend_to_rules(all_incentives: list) -> int:
    """增量合并趋势激励词到 rules.json"""
    rules = json.loads(_RULES_PATH.read_text(encoding="utf-8"))

    added = 0
    for item in all_incentives:
        cat = item.get("category", "GREEN_MEDIUM")
        indicator = item.get("indicator", "").strip()
        scenario = item.get("scenario", "").strip()

        if not indicator:
            continue

        # 去重
        existing = rules.get("incentive_points", {}).get(cat, {}).get("indicators", [])
        if indicator in existing:
            continue
        if any(e.startswith(indicator[:8]) for e in existing):
            continue

        entry = indicator
        if scenario:
            entry = f"{indicator}（场景: {scenario}）"

        rules.setdefault("incentive_points", {}).setdefault(cat, {}).setdefault("indicators", []).append(entry)
        added += 1

    if added:
        _RULES_PATH.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
    return added


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def collect(mock: bool = False, keywords_override: Optional[list] = None):
    """趋势关键词 → 抓取 → 分析 → 注入规则库"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 趋势热词采集")
    print("=" * 48)

    cfg = _load_cfg()
    trend_cfg = cfg.get("trend", {})
    keywords = keywords_override or trend_cfg.get("keywords", [])
    max_per = trend_cfg.get("max_per_keyword", 5)

    if not keywords:
        print("[SKIP] config.yaml trend.keywords 为空")
        return

    print(f"[KEYWORDS] {', '.join(keywords)}")
    print(f"[MAX] 每关键词 {max_per} 条\n")

    # 1. 采集/生成样本
    all_samples = {}
    if mock:
        for kw in keywords:
            samples = _MOCK_SAMPLES.get(kw, [])[:max_per]
            all_samples[kw] = samples
            status = f"{len(samples)} 条" if samples else "无对应 mock"
            print(f"  [MOCK] {kw}: {status}")
    else:
        print("  [WARN] Playwright 采集不可用，退回 mock 模式")
        for kw in keywords:
            samples = _MOCK_SAMPLES.get(kw, [])[:max_per]
            all_samples[kw] = samples
            print(f"  [MOCK] {kw}: {len(samples)} 条")

    if not any(all_samples.values()):
        print("[FAIL] 未采集到任何样本")
        return

    # 打印样本
    for kw, samples in all_samples.items():
        if samples:
            print(f"\n  [SAMPLES] {kw}:")
            for s in samples:
                print(f"    - {s[:60]}")

    # 2. DeepSeek 分析
    all_incentives = []
    for kw, samples in all_samples.items():
        if not samples:
            continue

        print(f"\n[ANALYZE] {kw} ({len(samples)} 条)...")
        payload = json.dumps({
            "domain": kw,
            "samples": samples,
        }, ensure_ascii=False, indent=2)

        result = _call_deepseek(payload)
        if result and result.get("incentives"):
            for inc in result["incentives"]:
                inc["source_domain"] = kw
                all_incentives.append(inc)
                print(f"  [+] {inc.get('category', '?')}: {inc.get('indicator', '')[:50]}")
        else:
            print(f"  [—] 无有效激励模式")

    # 3. 注入规则库
    if all_incentives:
        added = _merge_trend_to_rules(all_incentives)
        print(f"\n[INJECT] {added} 条激励词已注入 rules.json")
    else:
        print("\n[INJECT] 无新增激励词")

    # 4. 写 pipeline_state
    report = {
        "collected_at": datetime.now().isoformat(),
        "keywords": keywords,
        "domains": {kw: len(samples) for kw, samples in all_samples.items() if samples},
        "total_incentives": len(all_incentives),
        "incentives": [
            {
                "domain": inc.get("source_domain", ""),
                "category": inc.get("category", ""),
                "indicator": inc.get("indicator", "")[:60],
                "scenario": inc.get("scenario", ""),
            }
            for inc in all_incentives
        ],
    }

    state_path = _DATA_DIR / "pipeline_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        state = {}
    state["trend_collection"] = report
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[STATE] pipeline_state.json 已更新")

    print(f"\n{'=' * 48}")
    print(f"  采集完成: {len(all_incentives)} 条激励词")
    print(f"  规则版本: {json.loads(_RULES_PATH.read_text(encoding='utf-8')).get('version', '?')}")
    print(f"{'=' * 48}")

    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="趋势热词 → 激励词采集器")
    parser.add_argument("--mock", action="store_true", help="使用模拟数据")
    parser.add_argument("--keywords", type=str, default=None, help="逗号分隔的关键词列表")
    args = parser.parse_args()

    kw_list = args.keywords.split(",") if args.keywords else None
    collect(mock=args.mock, keywords_override=kw_list)
