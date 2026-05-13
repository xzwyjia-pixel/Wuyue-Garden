#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 竞品评论区心声监听器
================================================
职能：
  - 读取 config.yaml 的 trend.keywords + competitor.accounts
  - 抓取大博主评论区高频问题 / 痛点
  - 聚类去重 → 输出 data/user_pains.json

用法：
  python vocal_listener.py                          # 正常抓取
  python vocal_listener.py --seed                   # 仅用种子数据（无网络）
  python vocal_listener.py --force                  # 强制覆盖已有 user_pains.json
"""

import json
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

# 仅在非 seed 模式导入
try:
    import yaml
    import requests
    from bs4 import BeautifulSoup
    _HAS_SCRAPE = True
except ImportError:
    _HAS_SCRAPE = False

_BASE_DIR = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _BASE_DIR / "config.yaml"
_DATA_DIR = _BASE_DIR / "data"
_PAINS_PATH = _DATA_DIR / "user_pains.json"

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ── 配置加载 ──

def _load_config() -> dict:
    if not _CONFIG_PATH.exists():
        print(f"[FAIL] {_CONFIG_PATH} 不存在")
        return {}
    return yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))


# ── 评论区抓取（模拟/真实） ──

_QUESTION_PATTERNS = re.compile(
    r"(怎么|如何|能不能|有没有|是否|该不该|可以.*吗|需要.*吗|为什么|多久|多少|哪些|什么)",
)

_QUESTION_PHRASES = [
    "有没有适合新手的推荐？",
    "看完了还是不知道怎么开始",
    "能不能推荐一些入门级的书单",
    "你是怎么坚持下来的？",
    "有没有不需要太多本钱的项目推荐？",
    "会不会被割韭菜？怎么分辨靠谱项目？",
    "怎么判断一个理财产品靠不靠谱？",
    "怎么才能记得住这么多知识点？",
    "为什么我照着做效果不明显？",
    "这些方法真的有用吗？实测过没有？",
    "你用了多久才形成这个体系的？",
    "看完收藏等于学会吗？",
    "有没有交流群可以一起学习？",
    "失败了你怎么办？有退路吗？",
    "现在行情不好，适合创业吗？",
    "怎么找到第一批客户？",
    "你是怎么平衡主业和副业的？",
    "做了多久才开始盈利的？",
    "如果第一年没盈利还要坚持吗？",
    "基金亏了快20%要不要割肉？",
    "黄金现在还能买吗？",
    "通货膨胀这么高，存钱是不是反而亏了？",
    "可转债打新现在还值得参与吗？",
    "怎么防止被银行理财经理忽悠？",
    "哪个AI工具最好用？免费的有推荐吗？",
    "提示词怎么写才能出高质量结果？",
    "AI画画能商用吗？版权怎么算？",
    "现在学AI还来得及吗？门槛高不高？",
    "怎么用AI提升工作效率？有具体案例吗？",
    "AI生成的代码安全吗？能用在生产环境？",
    "会不会用AI的人替代不会用的人？",
    "有没有适合懒人的定投方案？",
    "月薪5000真的有必要理财吗？",
    "银行存款和理财哪个更划算？",
    "有房贷还要不要投资？",
    "年轻人应该先攒钱还是先投资自己？",
    "理财会不会越理越少？",
    "启动资金最少需要多少？",
    "这个模式在小城市能跑通吗？",
    "投入产出比大概多少？",
    "需要注册公司吗？前期要办哪些手续？",
    "这些技巧适合零基础吗？",
    "能不能出一期慢节奏的教学视频？",
    "内容太干，能不能多加点实操案例？",
    "团队一开始几个人比较合适？",
    "有没有更简单的方法？",
    "资产配置的比例多久调整一次？",
]


def _mock_fetch_comments(keywords: list, max_per: int) -> list:
    """模拟抓取评论区（无网络时使用）"""
    print("  [MOCK] 使用种子数据模拟评论区")
    domain_keywords = {
        "知识分享": ["有没有", "怎么", "能不能", "推荐", "适合", "效果", "开始", "坚持"],
        "职场": ["怎么", "能不能", "适合", "坚持", "多久", "开始"],
        "创业": ["有没有", "怎么", "能不能", "推荐", "靠谱", "适合", "开始", "坚持"],
        "理财": ["怎么", "能不能", "推荐", "适合", "亏", "买", "值得", "多少"],
        "AI": ["推荐", "怎么", "能用吗", "门槛", "安全", "替代"],
        "科技": ["推荐", "怎么", "能不能", "买", "有用吗", "值得"],
    }
    results = []
    for kw in keywords:
        dkws = domain_keywords.get(kw, ["怎么", "推荐"])
        for q in _QUESTION_PHRASES:
            if any(d in q for d in dkws):
                score = max_per - len(results) % max_per  # 递减权重
                results.append({
                    "text": q,
                    "source": kw,
                    "score": score,
                    "keywords": [d for d in dkws if d in q],
                })
            if len(results) >= max_per * len(keywords):
                break
    return results


def _real_fetch_comments(keywords: list, max_per: int,
                         competitor_accounts: list) -> list:
    """真实抓取：用搜索引擎模拟 + 抽取问句"""
    print(f"  [SCRAPE] 关键词: {keywords}, 竞对账号: {len(competitor_accounts)}")
    results = []
    seen = set()

    for kw in keywords:
        print(f"  [FETCH] 搜索 \"{kw} 评论 疑问\"...")
        try:
            url = f"https://www.douyin.com/search/{kw}"
            resp = requests.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                },
                timeout=15,
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            texts = set()
            for tag in soup.find_all(["span", "p", "div"]):
                t = tag.get_text(strip=True)
                if len(t) > 4 and len(t) < 120:
                    texts.add(t)

            for t in texts:
                if t in seen:
                    continue
                if _QUESTION_PATTERNS.search(t):
                    seen.add(t)
                    results.append({
                        "text": t,
                        "source": kw,
                        "score": 1,
                        "keywords": list(set(_QUESTION_PATTERNS.findall(t))),
                    })
            print(f"    → 提取 {len(results)} 条问题")
        except Exception as e:
            print(f"    [WARN] 抓取失败: {e}")

    return results[:max_per * len(keywords)]


# ── 聚类与去重 ──

def _deduplicate(pains: list) -> list:
    """语义去重：相同关键词簇只保留高分为"""
    clusters: dict = {}
    for p in pains:
        key = tuple(sorted(p.get("keywords", [])))
        if key not in clusters or p.get("score", 0) > clusters[key].get("score", 0):
            clusters[key] = p
    return sorted(clusters.values(), key=lambda x: x.get("score", 0), reverse=True)


def _normalize_scores(pains: list) -> list:
    """分数归一化到 0-5"""
    if not pains:
        return pains
    scores = [p.get("score", 0) for p in pains]
    max_s = max(scores) or 1
    for p in pains:
        p["score"] = round(p["score"] / max_s * 5, 1)
    return pains


# ── 主流程 ──

def listen(force: bool = False, seed_only: bool = False):
    """监听竞品评论区 → user_pains.json"""
    print("=" * 48)
    print("  规则甄查 · 甄先生 v2.0 — 评论区心声监听")
    print("=" * 48)

    # 1. 检查是否已有数据
    if _PAINS_PATH.exists() and not force:
        existing = json.loads(_PAINS_PATH.read_text(encoding="utf-8"))
        print(f"[EXIST] {len(existing.get('pains', []))} 条痛点 (上次: {existing.get('extracted_at', '?')})")
        print("[SKIP] 使用 --force 覆盖")
        return existing

    # 2. 加载配置
    cfg = _load_config()
    if not cfg:
        return

    keywords = cfg.get("trend", {}).get("keywords", [])
    max_per = cfg.get("trend", {}).get("max_per_keyword", 5)
    competitor_accounts = cfg.get("competitor", {}).get("accounts", [])
    print(f"[CFG] 关键词: {keywords}, 每关键词: {max_per}")
    print(f"[CFG] 竞对账号: {len(competitor_accounts)} 个")

    # 3. 抓取 / 种子
    if seed_only or not _HAS_SCRAPE:
        pains = _mock_fetch_comments(keywords, max_per)
    else:
        pains = _real_fetch_comments(keywords, max_per, competitor_accounts)
        if not pains:
            print("  [FALLBACK] 真实抓取为空，转种子数据")
            pains = _mock_fetch_comments(keywords, max_per)

    # 4. 去重 + 归一
    pains = _deduplicate(pains)
    pains = _normalize_scores(pains)

    # 5. 按分数降序
    pains.sort(key=lambda x: x.get("score", 0), reverse=True)

    output = {
        "extracted_at": datetime.now().isoformat(),
        "total_comments_scraped": len(pains),
        "total_pains": len(pains),
        "pains": pains,
    }

    # 6. 写入
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _PAINS_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SAVE] {_PAINS_PATH}")
    print(f"[DONE] {len(pains)} 条用户痛点")

    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="评论区心声监听器 — 提取用户高频痛点")
    parser.add_argument("--seed", action="store_true", help="仅用种子数据")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有数据")
    args = parser.parse_args()
    listen(force=args.force, seed_only=args.seed)
