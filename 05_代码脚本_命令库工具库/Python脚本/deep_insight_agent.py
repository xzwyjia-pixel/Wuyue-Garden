#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 深度洞察代理（五大工业级思维引擎）
=============================================================
在 LLM 提示词中嵌入五大思维引擎，根据 risk level 自动计算
各模块输出权重，生产有数据、有论据、有层级的合规洞察。

五大引擎：
  1) 第一性原理 (FPS)     — 回归本质，剥离包装看核心矛盾
  2) 演化博弈 (EGT)       — 平台规则是博弈均衡，分析纳什均衡点
  3) FMEA                — 失效模式与影响分析，量化风险优先级
  4) 安全边际 (MOS)       — 在规则边界外保留安全缓冲区
  5) 监管溯源 (RTT)       — 追溯政策源头，还原监管意图

用法：
  python deep_insight_agent.py              # 分析最新哨兵 + 当前规则
  python deep_insight_agent.py --mock       # 模拟数据测试
"""

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

_BASE_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BASE_DIR / "data"
_RULES_PATH = _BASE_DIR / "rules.json"
_API_KEY = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
_API_URL = "https://api.deepseek.com/v1/chat/completions"
_MODEL = "deepseek-chat"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


_MOCK_SENTINEL_TEXT = """
【紧急】抖音 2026年5月 直播话术规避专项治理通告
---------------------------------------------
近期平台监测到大量直播间通过"话术规避"手段绕过风控审核，包括但不限于：
1. 谐音替换：将"赚钱"说成"砖钱"、"Zuan Qian"、"赚米"
2. 拆分重组：将敏感词拆分为单字或倒序表达
3. 语音变调：使用变声器或语速变化绕过语音识别
4. 弹幕诱导：通过弹幕互动引导用户私信交易
5. 画面叠加：在直播画面中叠加文字绕过语音审核

平台即日起启动"净言2026-05"专项行动：
- 引入**AI语义理解引擎**，对直播间语音转文字后进行深层语义分析，
  即使使用谐音/变调也能识别真实意图
- 建立"话术规避行为档案"，首次警告 → 二次断流 → 三次永久封禁
- 连带责任：MCN机构旗下主播累计3次违规，全机构暂停直播权限7天
- 风险兜底：平台对"保健品/金融/医美"三大高风险品类,
  实行直播前内容报备制度

平台重申：
"任何试图通过技术手段规避审核规则的行为，均视为对平台治理秩序的直接挑战，
一经查实将从重处罚。"

[视频号] 2026年5月直播内容合规强化
---------------------------------
更新了直播话术审核标准，重点打击"擦边话术"和"暗示性表述"：
1. 新增"话术合规分"机制，每场直播结束后自动评分
2. 评分低于60分的主播，下播后需完成"合规学习考试"方可再次开播
3. 新增"举报奖励"功能，观众可对违规话术一键举报，查实后奖励流量券
4. 医疗健康类直播实行"双人审核"制度（AI + 人工双重审核）
"""


# ──────────────────────────────────────────────
# 读取当前上下文
# ──────────────────────────────────────────────


def _latest_sentinel_text() -> str:
    """从最新 sentinel JSON 提取分析文本"""
    files = sorted(_DATA_DIR.glob("sentinel_*.json"), reverse=True)
    if not files:
        print("[SENTINEL] 未找到哨兵报告，使用空文本")
        return ""
    data = json.loads(files[0].read_text(encoding="utf-8"))
    parts = []
    for t in data.get("targets", []):
        label = f"[{t['platform_name']}] {t['label']}"
        for a in t.get("articles", []):
            if a.get("title"):
                parts.append(f"{label} > {a['title']}")
        excerpt = t.get("full_text_excerpt", "")
        if excerpt:
            parts.append(f"{label} > {excerpt}")
    return "\n".join(parts)


def _current_rules_summary() -> str:
    """当前规则摘要，含风险等级分布"""
    try:
        rules = json.loads(_RULES_PATH.read_text(encoding="utf-8"))
        v = rules.get("version", "?")
        lines = [f"规则版本: {v}"]
        risk_counts = {}
        for lv in ("HIGH", "MEDIUM", "LOW"):
            focus = rules.get("risk_levels", {}).get(lv, {}).get("focus", {})
            n = len(focus)
            risk_counts[lv] = n
            keys = list(focus.keys())[:8]
            lines.append(f"  {lv}: {n} 条规则 — {', '.join(keys)}")
        inc_count = sum(
            len(rules.get("incentive_points", {}).get(lv, {}).get("indicators", []))
            for lv in ("GREEN_HIGH", "GREEN_MEDIUM", "GREEN_LOW")
        )
        lines.append(f"激励指标: {inc_count} 条")
        return "\n".join(lines) + f"\n风险分布: HIGH={risk_counts.get('HIGH',0)} MEDIUM={risk_counts.get('MEDIUM',0)} LOW={risk_counts.get('LOW',0)}"
    except Exception as e:
        return f"读取规则失败: {e}"


# ──────────────────────────────────────────────
# 五大工业级思维引擎 Prompt
# ──────────────────────────────────────────────

_ENGINE_DESCRIPTIONS = """
## 五大工业级思维引擎

你必须根据【当前规则的风险等级分布】（HIGH/MEDIUM/LOW 数量）和各引擎与规则内容的匹配度，
自动计算每个引擎的**输出权重**（0-100 整数），权重越高表示该引擎在当前分析中应占更大篇幅。

### 引擎 1: 第一性原理 — FPS (First Principle Slicing)
回归规则的本质矛盾，不受既有表述框架影响：
- 平台为什么要有这条规则？核心保护的法益是什么？
- 剥离营销话术包装，底层的"不可做什么"是什么？
- 创作者应建立的最小认知模型
- 典型输出：规则的本质是 X，不是 Y

### 引擎 2: 演化博弈 — EGT (Evolutionary Game Theory)
将平台规则视为多方博弈的纳什均衡：
- 平台、创作者、用户、监管四方的支付矩阵是什么？
- 违规—惩罚的博弈均衡在哪？什么情况下会偏离均衡？
- 平台为什么选择"先松后紧"或"一刀切"的策略？
- 典型输出：当前均衡点在 X，博弈正在向 Y 移动

### 引擎 3: FMEA (Failure Mode and Effects Analysis)
系统化失效模式分析，量化风险优先级：
- 每条规则对应的失效模式是什么？
- 失效的严重度(S)、发生度(O)、检测度(D) 评分（1-10）
- 风险优先级数 RPN = S × O × D
- 典型输出：RPN 排序表，最高风险点 X (RPN=n)

### 引擎 4: 安全边际 — MOS (Margin of Safety)
在规则边界外建立安全缓冲区：
- 规则明文边界在哪？隐形边界在哪？
- 距处罚阈值的安全距离是多少？
- 合规超额储备策略（Safe Zone 计算）
- 典型输出：安全边际建议：至少在 X 之外保留 Y 缓冲区

### 引擎 5: 监管溯源 — RTT (Regulatory Traceability)
从政策源头理解规则演变：
- 当前规则对应哪部上位法/部门规章？
- 监管意图的时间线：原意→解释→执法尺度变化
- 未来 3-6 个月监管趋势预判
- 典型输出：法规溯源链：广告法第 X 条 → 平台细则第 Y 条
"""


def _build_prompt(sentinel_text: str, rules_info: str) -> str:
    return f"""{_ENGINE_DESCRIPTIONS}

## 输入数据

【当前规则】
{rules_info}

【公告文本】
{sentinel_text}

## 分析要求

1. 基于上述规则的风险等级分布和公告内容，为每个引擎分配权重（0-100）。
   - HIGH 风险规则多 → FMEA + EGT 权重提高（需要量化风险、分析博弈）
   - 涉及新规/政策变更 → RTT 权重提高（需要监管溯源）
   - 涉及边界案例/灰色地带 → FPS 权重提高（需要第一性原理）
   - 涉及处罚/封号 → MOS 权重提高（需要安全边际计算）

2. 按权重分配后的优先级顺序输出各引擎的分析内容。

3. 对于每个活跃引擎（权重 > 0），输出该引擎视角下的深度分析。

4. 输出必须包含完整的反直觉边界案例（counter_intuitive），这是内容分发的核心卖点。

## 输出格式（严格 JSON，不要其他文字）

{{
  "thinking_engine_weights": {{
    "FPS": {{"weight": 整数0-100, "rationale": "权重理由"}},
    "EGT": {{"weight": 整数0-100, "rationale": "权重理由"}},
    "FMEA": {{"weight": 整数0-100, "rationale": "权重理由"}},
    "MOS": {{"weight": 整数0-100, "rationale": "权重理由"}},
    "RTT": {{"weight": 整数0-100, "rationale": "权重理由"}}
  }},
  "platform_intent": {{
    "title": "平台意图一句话总结",
    "detail": "基于最高权重引擎视角的详细分析",
    "driving_forces": ["驱动力1", "驱动力2"],
    "lead_engine": "本次分析主导引擎标识"
  }},
  "policy_logic": {{
    "title": "核心逻辑一句话总结",
    "causal_chain": ["因果1（附所属引擎标识: FPS/EGT/FMEA/MOS/RTT）", "因果2", "因果3"],
    "impact_path": "对创作者的实际影响路径"
  }},
  "fmea_table": [
    {{"failure_mode": "失效模式", "severity": 1-10, "occurrence": 1-10, "detection": 1-10, "rpn": 计算结果, "recommendation": "建议"}}
  ],
  "counter_intuitive": [
    {{
      "scenario": "场景描述",
      "common_belief": "常见认知",
      "reality": "真实判定",
      "reason": "基于[引擎标识]的原因解析",
      "action": "应对建议"
    }}
  ]
}}

如果没有公告文本可分析，返回空结构 {{"thinking_engine_weights": {{}}, "platform_intent": {{}}, "policy_logic": {{}}, "fmea_table": [], "counter_intuitive": []}}
"""


# ──────────────────────────────────────────────
# DeepSeek 调用
# ──────────────────────────────────────────────


def _call_deepseek(sentinel_text: str, rules_info: str) -> Optional[dict]:
    try:
        prompt = _build_prompt(sentinel_text, rules_info)
        resp = requests.post(
            _API_URL,
            headers={"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": _MODEL,
                "messages": [
                    {"role": "system", "content": "你是短视频平台合规策略分析师，服务于「规则甄查 · 甄先生」品牌。输出严格 JSON，不包含其他文字。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": 4096,
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)
        return json.loads(match.group()) if match else json.loads(content)
    except Exception as e:
        print(f"[FAIL] DeepSeek: {e}")
        return None


# ──────────────────────────────────────────────
# Logic Adapter — 导入独立模块
# ──────────────────────────────────────────────

try:
    from logic_adapter import load_pains, map_pains_to_engines, best_engine_for_pain
except ImportError:
    # Fallback if logic_adapter.py not available
    def load_pains():
        path = _DATA_DIR / "user_pains.json"
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return sorted(data.get("pains", []), key=lambda p: p.get("score", 0), reverse=True)
        except Exception:
            return []

    def map_pains_to_engines(pains):
        return {}

    def best_engine_for_pain(pain_text):
        return None, 0, []


# ──────────────────────────────────────────────
# 存储
# ──────────────────────────────────────────────


def _save_result(result: dict, mock: bool = False):
    """写 pipeline_state，含思维引擎权重 + 痛点映射"""
    # 计算痛点→引擎映射
    pains = load_pains()
    pain_engine_map = map_pains_to_engines(pains)

    report = {
        "generated_at": datetime.now().isoformat(),
        "mock": mock,
        "pain_engine_map": pain_engine_map,
        "thinking_engine_weights": result.get("thinking_engine_weights", {}),
        "platform_intent": result.get("platform_intent", {}),
        "policy_logic": result.get("policy_logic", {}),
        "fmea_table": result.get("fmea_table", []),
        "counter_intuitive": result.get("counter_intuitive", []),
    }

    state_path = _DATA_DIR / "pipeline_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        state = {}
    state["deep_insight"] = report
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[STATE] pipeline_state.json 已更新")
    return report


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────


def _format_weights(weights: dict) -> str:
    """格式化权重输出"""
    parts = []
    for name, label in [("FPS", "第一性原理"), ("EGT", "演化博弈"), ("FMEA", "FMEA"), ("MOS", "安全边际"), ("RTT", "监管溯源")]:
        w = weights.get(name, {})
        v = w.get("weight", 0)
        r = w.get("rationale", "")[:30]
        parts.append(f"  {label}({v}): {r}")
    return "\n".join(parts)


def _format_fmea(fmea_list: list) -> str:
    """格式化 FMEA 表格输出"""
    if not fmea_list:
        return "  [空]"
    lines = []
    for item in fmea_list[:5]:
        lines.append(f"  {item.get('failure_mode','')[:30]} | S={item.get('severity',0)} O={item.get('occurrence',0)} D={item.get('detection',0)} → RPN={item.get('rpn',0)}")
    return "\n".join(lines)


def analyze(mock: bool = False):
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 深度洞察代理")
    print("  [五大工业级思维引擎]")
    print("=" * 48)

    # 1. 获取文本
    if mock:
        sentinel_text = _MOCK_SENTINEL_TEXT
        print("[MOCK] 使用模拟公告文本")
    else:
        sentinel_text = _latest_sentinel_text()

    if not sentinel_text.strip():
        print("[SKIP] 无可分析文本")
        return

    rules_info = _current_rules_summary()
    print(f"[RULES] {rules_info.split(chr(10))[0]}")
    print(f"[TEXT] {len(sentinel_text)} chars\n")

    # 2. 痛点→引擎映射预览
    pains = load_pains()
    pain_map = map_pains_to_engines(pains)
    print(f"[PAINS] {len(pains)} 条痛点")
    if pain_map:
        print(f"  [ENGINE MAP] {', '.join(f'{k}={v*100:.0f}%' for k,v in pain_map.items())}")

    # 3. DeepSeek 分析
    print("[API] 深度分析中（五大引擎）...")
    result = _call_deepseek(sentinel_text, rules_info)
    if not result:
        print("[FAIL] 分析失败")
        return

    # 4. 输出摘要
    weights = result.get("thinking_engine_weights", {})
    pi = result.get("platform_intent", {})
    pl = result.get("policy_logic", {})
    fmea = result.get("fmea_table", [])
    ci = result.get("counter_intuitive", [])

    print(f"\n{'─' * 48}")
    print(f"  思维引擎权重分布")
    print(f"{'─' * 48}")
    print(_format_weights(weights))

    print(f"\n{'─' * 48}")
    print(f"  维度一 · 平台意图")
    print(f"  [{pi.get('lead_engine', '?')}] {pi.get('title', '—')}")
    for f in pi.get("driving_forces", []):
        print(f"    - {f}")

    print(f"\n  维度二 · 政策逻辑")
    print(f"  {pl.get('title', '—')}")
    for c in pl.get("causal_chain", []):
        print(f"    - {c}")

    print(f"\n  维度三 · FMEA 风险优先级")
    print(_format_fmea(fmea))

    print(f"\n  维度四 · 反直觉教训 ({len(ci)} 条)")
    for item in ci:
        print(f"  [{item.get('scenario', '?')}]")
        print(f"    常识: {item.get('common_belief', '')[:50]}")
        print(f"    真相: {item.get('reality', '')[:50]}")

    # 5. 痛点匹配建议
    if pain_map:
        top_engine = max(pain_map, key=pain_map.get)
        top_pains = pains[:3] if pains else []
        print(f"\n{'─' * 48}")
        print(f"  Logic Adapter · 痛点→引擎匹配")
        print(f"  最佳匹配引擎: {top_engine}")
        if top_pains:
            print(f"  驱动痛点:")
            for p in top_pains:
                print(f"    - [{p.get('score',0)}] {p.get('text','')[:40]}")

    # 6. 存储
    _save_result(result, mock=mock)
    print(f"\n[DONE] 深度洞察已生成")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="深度洞察代理 — 五大工业级思维引擎")
    parser.add_argument("--mock", action="store_true", help="使用模拟数据")
    args = parser.parse_args()
    analyze(mock=args.mock)
