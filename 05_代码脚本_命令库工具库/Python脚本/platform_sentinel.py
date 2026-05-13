# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 平台规则哨兵
=========================================
功能：Playwright 轮询抖音/视频号规则公告页，抓取规则更新与处罚公告
架构：Playwright 全浏览器渲染，适配 SPA 页面
输出：结构化 JSON（规则变更 / 处罚公告 / 政策激励）
缓存：内容哈希去重，仅输出变更
"""

import json
import hashlib
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Windows terminal: force UTF-8 for Chinese output
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright, Page, Browser

# ── 路径配置 ──
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DB = DATA_DIR / "sentinel_cache.db"

# ── 超时配置 ──
NAV_TIMEOUT = 30000  # 页面加载超时 ms
WAIT_TIMEOUT = 10000  # 元素等待超时 ms

# ====================================================================
# 目标平台配置
# ====================================================================
# 每项：url, page_type, label, selector（内容容器 CSS 选择器）
# 若 selector 为空，则提取 <body> 全文（兜底）

TARGETS = [
    # ── 抖音 ──
    {
        "platform": "douyin",
        "name": "抖音",
        "url": "https://www.douyin.com/help",
        "page_type": "help_center",
        "label": "帮助中心 / 规则指引",
        "selector": ".help-content, .article-list, main",
    },
    {
        "platform": "douyin",
        "name": "抖音",
        "url": "https://www.douyin.com/about",
        "page_type": "about",
        "label": "关于抖音 / 平台规范",
        "selector": ".about-content, main",
    },
    # ── 视频号（微信公众平台） ──
    {
        "platform": "wechat_video",
        "name": "视频号",
        "url": "https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_agreement&s=terms",
        "page_type": "terms",
        "label": "微信使用条款 / 视频号规范",
        "selector": ".content, #content, main",
    },
    {
        "platform": "wechat_video",
        "name": "视频号",
        "url": "https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_agreement&s=operator",
        "page_type": "operator",
        "label": "运营规范 / 视频号运营规则",
        "selector": ".content, #content, main",
    },
]


# ====================================================================
# 内容缓存（哈希去重）
# ====================================================================

class SentinelCache:
    """内容哈希缓存，仅记录变更"""

    def __init__(self, db_path: Path = CACHE_DB):
        self.conn = sqlite3.connect(str(db_path))
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                url TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                scanned_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL DEFAULT 'ok'
            )
        """)
        self.conn.commit()

    def has_changed(self, url: str, content: str) -> bool:
        """计算 hash 并与上次快照比较"""
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()
        cur = self.conn.execute(
            "SELECT content_hash FROM snapshots WHERE url = ?", (url,)
        )
        row = cur.fetchone()
        if row and row[0] == h:
            return False  # 内容未变
        # 更新快照
        self.conn.execute(
            "INSERT OR REPLACE INTO snapshots (url, content_hash, scanned_at) VALUES (?, ?, ?)",
            (url, h, datetime.now().isoformat())
        )
        self.conn.commit()
        return True

    def close(self):
        self.conn.close()


# ====================================================================
# 内容提取器
# ====================================================================

def _extract_articles_from_html(page: Page, target: dict) -> list:
    """从已渲染页面提取结构化条目"""
    articles = []

    # 尝试提取文章/条目列表
    article_nodes = page.query_selector_all(
        "article, .article-item, .help-item, .rule-item, "
        "tr, .list-item, .news-item, li"
    )

    for node in article_nodes[:50]:  # 最多 50 条
        title_el = node.query_selector(
            "h1, h2, h3, h4, .title, .article-title, a[href]"
        )
        link_el = node.query_selector("a[href]")
        date_el = node.query_selector(
            "time, .date, .time, .publish-date, .pub-date"
        )
        summary_el = node.query_selector(
            "p, .summary, .desc, .description, .abstract"
        )

        title = title_el.inner_text().strip() if title_el else ""
        link = ""
        if link_el:
            href = link_el.get_attribute("href") or ""
            # 相对路径补全
            if href.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(target["url"])
                link = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif href.startswith("http"):
                link = href
        date = date_el.inner_text().strip() if date_el else ""
        summary = summary_el.inner_text().strip() if summary_el else ""

        if title:
            articles.append({
                "title": title,
                "url": link,
                "date": date,
                "summary": summary[:300] if summary else "",
            })

    return articles


def _extract_full_text(page: Page) -> str:
    """兜底：提取页面全部可见文本"""
    body = page.query_selector("body")
    if not body:
        return ""
    return body.inner_text()[:10000]  # 限制 10K


# ====================================================================
# 主扫描逻辑
# ====================================================================

class PlatformSentinel:
    """平台规则哨兵"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.cache = SentinelCache()
        self.playwright = None
        self.browser: Optional[Browser] = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        return self

    def __exit__(self, *args):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.cache.close()

    def scan_page(self, target: dict) -> dict:
        """扫描单个目标页面，返回结构化结果"""
        url = target["url"]
        selector = target.get("selector", "")
        platform = target["platform"]
        page_type = target["page_type"]

        print(f"  [NET] {target['name']} / {target['label']}")
        print(f"     {url}")

        context = self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
        )
        page = context.new_page()

        try:
            # 导航
            page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
            page.wait_for_timeout(3000)  # 等待 JS 渲染

            # 等待目标内容容器
            if selector:
                try:
                    page.wait_for_selector(selector, timeout=WAIT_TIMEOUT)
                except Exception:
                    pass  # 用兜底提取

            # 提取页面标题
            page_title = page.title()

            # 提取结构化条目
            articles = _extract_articles_from_html(page, target)

            # 兜底全文
            full_text = _extract_full_text(page)

            # 哈希去重
            content_to_hash = json.dumps(articles, ensure_ascii=False) if articles else full_text
            changed = self.cache.has_changed(url, content_to_hash)

            status = "success"
            if not changed and articles:
                status = "no_change"
            elif not articles:
                status = "no_articles_found"

            result = {
                "platform": platform,
                "platform_name": target["name"],
                "page_type": page_type,
                "label": target["label"],
                "url": url,
                "page_title": page_title,
                "status": status,
                "scanned_at": datetime.now().isoformat(),
                "articles": articles,
                "full_text_length": len(full_text),
            }

            # articles 为空但 full_text 有内容时保留全文
            if not articles and full_text:
                result["full_text_excerpt"] = full_text[:2000]

            return result

        except Exception as e:
            print(f"     [FAIL] 扫描失败: {e}")
            return {
                "platform": platform,
                "platform_name": target["name"],
                "page_type": page_type,
                "label": target["label"],
                "url": url,
                "page_title": "",
                "status": "failed",
                "error": str(e),
                "scanned_at": datetime.now().isoformat(),
                "articles": [],
                "full_text_length": 0,
            }

        finally:
            context.close()

    def scan_all(self) -> dict:
        """扫描所有配置的目标页面"""
        results = []
        success = 0
        failed = 0
        changed = 0

        print("=" * 64)
        print("  规则甄查 · 甄先生 v2.0 — 平台规则哨兵")
        print(f"  扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  目标平台: 抖音 + 视频号")
        print(f"  目标页面: {len(TARGETS)} 个")
        print("=" * 64)

        for target in TARGETS:
            print()
            result = self.scan_page(target)
            results.append(result)

            if result["status"] == "failed":
                failed += 1
            else:
                success += 1
                if result["status"] == "no_change":
                    print(f"     [SAME] 内容未变更")

            # 统计新内容
            if result.get("articles"):
                print(f"     [LIST] 条目: {len(result['articles'])} 条")
                changed += 1

        print(f"\n{'=' * 64}")
        print(f"  扫描完成: 成功 {success}, 失败 {failed}, 含新内容 {changed}")
        print(f"{'=' * 64}")

        return {
            "scan_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "scanned_at": datetime.now().isoformat(),
            "engine": "platform_sentinel v2.0",
            "brand": "规则甄查 · 甄先生",
            "summary": {
                "total_targets": len(TARGETS),
                "success": success,
                "failed": failed,
                "with_new_content": changed,
            },
            "targets": results,
        }


# ====================================================================
# 输出 & 报告
# ====================================================================

def _print_report(report: dict):
    """终端摘要输出"""
    print(f"\n[STATS] 摘要")
    print(f"  {'平台':<12} {'页面':<20} {'状态':<12} {'条目':<6}")
    print(f"  {'-'*50}")
    for t in report["targets"]:
        platform_name = t["platform_name"]
        label = t["label"][:18]
        status = t["status"]
        count = len(t.get("articles", []))
        print(f"  {platform_name:<12} {label:<20} {status:<12} {count:<6}")

    # 按平台聚合
    from collections import Counter
    platform_stats = Counter(t["platform"] for t in report["targets"] if t["status"] != "failed")
    article_stats = {}
    for t in report["targets"]:
        p = t["platform"]
        if p not in article_stats:
            article_stats[p] = 0
        article_stats[p] += len(t.get("articles", []))

    print(f"\n[STATS] 平台聚合")
    for p, count in platform_stats.most_common():
        print(f"  {p}: {count} 页面在线, {article_stats.get(p, 0)} 条目")


def save_report(report: dict) -> Path:
    """保存结构化 JSON 报告"""
    timestamp = report["scan_id"]
    filepath = DATA_DIR / f"sentinel_{timestamp}.json"
    filepath.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return filepath


# ====================================================================
# CLI 入口
# ====================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="平台规则哨兵 — 抖音/视频号规则公告监控")
    parser.add_argument("--visible", action="store_true", help="显示浏览器窗口（默认无头）")
    parser.add_argument("--output", "-o", type=str, default="", help="输出路径（默认 data/sentinel_{scan_id}.json）")
    args = parser.parse_args()

    with PlatformSentinel(headless=not args.visible) as sentinel:
        report = sentinel.scan_all()

    # 输出 JSON
    output_path = Path(args.output) if args.output else save_report(report)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n[FILE] JSON 报告: {output_path}")

    _print_report(report)
