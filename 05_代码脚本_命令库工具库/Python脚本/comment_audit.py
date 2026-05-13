#!/usr/bin/env python3
"""comment_audit.py

自动化抓取抖音热门博主评论区，并生成 CSV 数据与 Markdown 简报。

使用说明:
    python comment_audit.py --url <抖音视频或评论页URL> --output-dir ./output

依赖:
    pip install playwright
    playwright install
"""

import argparse
import csv
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from playwright.sync_api import Page, sync_playwright

DEFAULT_TRAFFIC_KEYWORDS = [
    "僵尸粉",
    "涨粉",
    "涨粉神器",
    "吸粉",
    "一键关注",
    "刷量",
    "代运营",
    "刷粉",
    "封号",
    "黑粉",
    "涨粉群",
    "流量加持",
]

DEFAULT_COMPLIANCE_KEYWORDS = [
    "违规",
    "违法",
    "涉黄",
    "涉政",
    "涉赌",
    "涉毒",
    "诈骗",
    "虚假宣传",
    "诱导关注",
    "诱导点赞",
    "诱导转发",
    "宣传外挂",
    "宣传脚本",
    "账号买卖",
    "售卖",
    "违规引流",
]

SCROLL_PAUSE = 1.8
COMMENT_SELECTOR_CANDIDATES = [
    'div[data-e2e="comment-item"]',
    'div[data-testid="comment-item"]',
    'div.comment-item',
    'div[class*="comment"]',
]


def build_keyword_map(custom_keywords_file: Optional[str] = None) -> Dict[str, List[str]]:
    keywords = {
        "traffic_anomaly": DEFAULT_TRAFFIC_KEYWORDS.copy(),
        "compliance_risk": DEFAULT_COMPLIANCE_KEYWORDS.copy(),
    }

    if custom_keywords_file:
        path = Path(custom_keywords_file)
        if path.exists():
            with path.open("r", encoding="utf-8") as fp:
                for line in fp:
                    text = line.strip()
                    if not text or text.startswith("#"):
                        continue
                    if text.startswith("traffic:"):
                        keywords["traffic_anomaly"].append(text.split(":", 1)[1].strip())
                    elif text.startswith("risk:"):
                        keywords["compliance_risk"].append(text.split(":", 1)[1].strip())
                    else:
                        keywords["compliance_risk"].append(text)
        else:
            print(f"警告：自定义关键词文件不存在: {custom_keywords_file}")
    return keywords


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def find_comment_elements(page: Page) -> List[str]:
    for selector in COMMENT_SELECTOR_CANDIDATES:
        elements = page.query_selector_all(selector)
        if elements:
            return selector
    raise RuntimeError("未找到评论节点，请检查页面结构或选择器。")


def parse_comment_element(element) -> Dict[str, str]:
    try:
        text = element.inner_text().strip()
    except Exception:
        text = ""

    username = ""
    timestamp = ""
    like_count = ""
    content = text

    if "\n" in text:
        parts = [line.strip() for line in text.split("\n") if line.strip()]
        if len(parts) >= 2:
            username = parts[0]
            content = parts[1]
            if len(parts) >= 3:
                timestamp = parts[-1]
                like_count = parts[-2] if len(parts) >= 4 else ""

    return {
        "username": username,
        "content": normalize_text(content),
        "timestamp": timestamp,
        "like_count": like_count,
    }


def scan_comment_for_keywords(comment_text: str, keyword_map: Dict[str, List[str]]) -> Dict[str, List[str]]:
    matches = {"traffic_anomaly": [], "compliance_risk": []}
    normalized = comment_text.lower()
    for category, terms in keyword_map.items():
        for term in terms:
            if term and term.lower() in normalized:
                if term not in matches[category]:
                    matches[category].append(term)
    return matches


def classify_risk(matches: Dict[str, List[str]]) -> str:
    if matches["compliance_risk"] and matches["traffic_anomaly"]:
        return "高风险"
    if matches["compliance_risk"]:
        return "合规风险"
    if matches["traffic_anomaly"]:
        return "流量异常"
    return "普通"


def scroll_to_load_comments(page: Page, max_comments: int = 120) -> None:
    previous_height = 0
    retry = 0

    while True:
        page.mouse.wheel(0, 1200)
        time.sleep(SCROLL_PAUSE)

        current_height = page.evaluate("document.documentElement.scrollHeight")
        if current_height == previous_height:
            retry += 1
            if retry >= 3:
                break
        else:
            retry = 0
            previous_height = current_height

        comment_count = len(page.query_selector_all(COMMENT_SELECTOR_CANDIDATES[0])) if page.query_selector_all(COMMENT_SELECTOR_CANDIDATES[0]) else 0
        if comment_count >= max_comments:
            break


def extract_comments(page: Page, max_comments: int = 120) -> List[Dict[str, str]]:
    selector = find_comment_elements(page)
    elements = page.query_selector_all(selector)
    comments = []
    seen = set()

    for element in elements:
        raw = parse_comment_element(element)
        if not raw["content"]:
            continue
        unique = (raw["username"], raw["content"])
        if unique in seen:
            continue
        seen.add(unique)
        comments.append(raw)
        if len(comments) >= max_comments:
            break

    return comments


def generate_csv(comments: List[Dict[str, str]], output_path: Path) -> None:
    fieldnames = ["username", "content", "timestamp", "like_count", "matched_traffic_terms", "matched_risk_terms", "risk_level"]
    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for comment in comments:
            writer.writerow({
                "username": comment.get("username", ""),
                "content": comment.get("content", ""),
                "timestamp": comment.get("timestamp", ""),
                "like_count": comment.get("like_count", ""),
                "matched_traffic_terms": ",".join(comment.get("matched_traffic_terms", [])),
                "matched_risk_terms": ",".join(comment.get("matched_risk_terms", [])),
                "risk_level": comment.get("risk_level", "普通"),
            })


def generate_markdown_report(comments: List[Dict[str, str]], target_url: str, keyword_map: Dict[str, List[str]], output_path: Path) -> None:
    total = len(comments)
    traffic_count = sum(1 for c in comments if c.get("matched_traffic_terms"))
    risk_count = sum(1 for c in comments if c.get("matched_risk_terms"))
    high_risk_count = sum(1 for c in comments if c.get("risk_level") == "高风险")

    traffic_counter = Counter(term for c in comments for term in c.get("matched_traffic_terms", []))
    risk_counter = Counter(term for c in comments for term in c.get("matched_risk_terms", []))

    top_traffic = traffic_counter.most_common(10)
    top_risk = risk_counter.most_common(10)
    suspicious_comments = [c for c in comments if c.get("risk_level") != "普通"][:8]

    lines = [
        f"# 抖音评论区风险审计报告",
        "",
        f"- 监测目标：{target_url}",
        f"- 抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 抓取评论数量：{total}",
        f"- 流量异常评论数量：{traffic_count}",
        f"- 合规风险评论数量：{risk_count}",
        f"- 高风险评论数量：{high_risk_count}",
        "",
        "## 关键词汇统计",
        "",
        "### 流量异常关键词 Top 10",
        "",
    ]

    if top_traffic:
        lines.extend([f"- `{term}`：{count}" for term, count in top_traffic])
    else:
        lines.append("- 无匹配到流量异常关键词。")

    lines.extend(["", "### 合规风险关键词 Top 10", ""])
    if top_risk:
        lines.extend([f"- `{term}`：{count}" for term, count in top_risk])
    else:
        lines.append("- 无匹配到合规风险关键词。")

    lines.extend(["", "## 重点可疑评论示例", ""])
    if suspicious_comments:
        for comment in suspicious_comments:
            lines.append(f"- 用户：{comment.get('username', '')}")
            lines.append(f"  - 时间：{comment.get('timestamp', '')}")
            lines.append(f"  - 内容：{comment.get('content', '')}")
            lines.append(f"  - 风险等级：{comment.get('risk_level')}" )
            lines.append(f"  - 流量异常关键词：{', '.join(comment.get('matched_traffic_terms', [])) or '无'}")
            lines.append(f"  - 合规风险关键词：{', '.join(comment.get('matched_risk_terms', [])) or '无'}")
            lines.append("")
    else:
        lines.append("- 未检测到可疑评论。")

    lines.append("\n## 备注")
    lines.append("- 本脚本基于页面评论结构抓取，若抖音页面样式发生变化，选择器需更新。")
    lines.append("- 建议定期补充和校对关键词库，以保持对新型风险词的覆盖。\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_audit(url: str, output_dir: str, keywords_file: Optional[str], max_comments: int, headless: bool) -> None:
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    keyword_map = build_keyword_map(keywords_file)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(locale="zh-CN", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(url, timeout=60000)
        time.sleep(3)

        try:
            page.click('text=评论', timeout=5000)
            time.sleep(2)
        except Exception:
            pass

        scroll_to_load_comments(page, max_comments=max_comments)
        comments = extract_comments(page, max_comments=max_comments)

        for comment in comments:
            matches = scan_comment_for_keywords(comment["content"], keyword_map)
            comment["matched_traffic_terms"] = matches["traffic_anomaly"]
            comment["matched_risk_terms"] = matches["compliance_risk"]
            comment["risk_level"] = classify_risk(matches)

        csv_path = output_dir_path / f"comment_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        md_path = output_dir_path / f"comment_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        generate_csv(comments, csv_path)
        generate_markdown_report(comments, url, keyword_map, md_path)

        print(f"CSV 数据已生成：{csv_path}")
        print(f"Markdown 简报已生成：{md_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="抖音热门博主评论区自动化审计脚本")
    parser.add_argument("--url", required=True, help="抖音视频或评论区页面 URL")
    parser.add_argument("--output-dir", default="./output", help="输出目录")
    parser.add_argument("--keywords-file", default=None, help="可选自定义关键词文件，支持 traffic:xxx 和 risk:xxx 语法")
    parser.add_argument("--max-comments", type=int, default=120, help="最多抓取评论数量")
    parser.add_argument("--headless", action="store_true", help="以无头模式运行浏览器")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run_audit(args.url, args.output_dir, args.keywords_file, args.max_comments, args.headless)
        return 0
    except Exception as exc:
        print(f"抓取失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
