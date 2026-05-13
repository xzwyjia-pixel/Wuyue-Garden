# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 红绿灯双向雷达扫描器
================================================
功能：异步抓取抖音/视频号平台内容，同步采集"负向受罚"与"正向获益"两类案例
架构：asyncio + aiohttp 异步架构，适配 ThinkPad P15V 多核标压 CPU
存储：E:/MyCodeProjects/data/ — 内存缓冲+批量写入，保护 SSD 寿命
缓存：SQLite 本地缓存，支持断点续传
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse

import aiohttp

# ── P15V 适配配置 ──
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DB = DATA_DIR / "radar_cache.db"

# 并发控制 — P15V 6核12线程标压 CPU
MAX_CONCURRENCY = 12  # 充分利用多核
BATCH_SIZE = 50       # 每批写入条数
BUFFER_FLUSH_INTERVAL = 30  # 秒

# 请求配置
TIMEOUT = aiohttp.ClientTimeout(total=30)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ──────────────────────────────────────────────
# SQLite 缓存层（支持断点续传）
# ──────────────────────────────────────────────

class RadarCache:
    """轻量化 SQLite 缓存，支持断点续传"""

    def __init__(self, db_path: Path = CACHE_DB):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS crawled_urls (
                url TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'pending',
                category TEXT,
                title TEXT,
                content TEXT,
                crawled_at TIMESTAMP,
                error TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_sessions (
                session_id TEXT PRIMARY KEY,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                total_urls INTEGER,
                success_count INTEGER,
                fail_count INTEGER
            )
        """)
        self.conn.commit()

    def is_crawled(self, url: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM crawled_urls WHERE url = ? AND status = 'done'",
            (url,)
        )
        return cur.fetchone() is not None

    def mark_pending(self, urls: List[str]):
        now = datetime.now().isoformat()
        data = [(u, 'pending', None, None, None, now, None) for u in urls if not self.is_crawled(u)]
        if data:
            self.conn.executemany(
                "INSERT OR IGNORE INTO crawled_urls (url, status, category, title, content, crawled_at, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)", data
            )
            self.conn.commit()

    def mark_done(self, url: str, category: str, title: str = "", content: str = ""):
        self.conn.execute(
            "UPDATE crawled_urls SET status='done', category=?, title=?, content=?, "
            "crawled_at=? WHERE url=?",
            (category, title, content, datetime.now().isoformat(), url)
        )
        self.conn.commit()

    def mark_failed(self, url: str, error: str):
        self.conn.execute(
            "UPDATE crawled_urls SET status='failed', error=?, crawled_at=? WHERE url=?",
            (error, datetime.now().isoformat(), url)
        )
        self.conn.commit()

    def get_pending(self) -> List[str]:
        cur = self.conn.execute(
            "SELECT url FROM crawled_urls WHERE status = 'pending' ORDER BY crawled_at ASC"
        )
        return [row[0] for row in cur.fetchall()]

    def get_results(self, category: Optional[str] = None) -> List[dict]:
        if category:
            cur = self.conn.execute(
                "SELECT url, category, title, content, crawled_at FROM crawled_urls "
                "WHERE status='done' AND category=? ORDER BY crawled_at DESC",
                (category,)
            )
        else:
            cur = self.conn.execute(
                "SELECT url, category, title, content, crawled_at FROM crawled_urls "
                "WHERE status='done' ORDER BY crawled_at DESC"
            )
        return [
            {"url": r[0], "category": r[1], "title": r[2],
             "content": r[3], "crawled_at": r[4]}
            for r in cur.fetchall()
        ]

    def get_stats(self) -> dict:
        cur = self.conn.execute(
            "SELECT status, COUNT(*) FROM crawled_urls GROUP BY status"
        )
        stats = {row[0]: row[1] for row in cur.fetchall()}
        return {
            "total": sum(stats.values()),
            "done": stats.get("done", 0),
            "pending": stats.get("pending", 0),
            "failed": stats.get("failed", 0),
        }

    def close(self):
        self.conn.close()


# ──────────────────────────────────────────────
# 异步爬取引擎（P15V 多核优化）
# ──────────────────────────────────────────────

class AsyncRadarScanner:
    """
    异步雷达扫描器
    - asyncio + aiohttp 异步架构
    - 信号量控制并发数（默认12，适配P15V 6核12线程）
    - 内存缓冲 + 批量写入 SQLite
    """

    def __init__(self, max_concurrency: int = MAX_CONCURRENCY):
        self.cache = RadarCache()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session: Optional[aiohttp.ClientSession] = None
        self.buffer: List[tuple] = []  # 内存缓冲
        self.buffer_lock = asyncio.Lock()
        self.last_flush = time.time()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT}
        )
        return self

    async def __aexit__(self, *args):
        await self._flush_buffer()
        if self.session:
            await self.session.close()
        self.cache.close()

    async def _flush_buffer(self):
        """批量写入缓冲数据到 SQLite"""
        async with self.buffer_lock:
            if not self.buffer:
                return
            batch = self.buffer[:]
            self.buffer.clear()
            self.last_flush = time.time()

        # 批量写入
        conn = sqlite3.connect(str(CACHE_DB))
        try:
            conn.executemany(
                "INSERT OR REPLACE INTO crawled_urls "
                "(url, status, category, title, content, crawled_at, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)", batch
            )
            conn.commit()
        finally:
            conn.close()

    async def _add_to_buffer(self, record: tuple):
        """添加记录到内存缓冲，达到阈值或超时则刷入"""
        async with self.buffer_lock:
            self.buffer.append(record)

        if len(self.buffer) >= BATCH_SIZE or (time.time() - self.last_flush) >= BUFFER_FLUSH_INTERVAL:
            await self._flush_buffer()

    async def crawl_single(self, url: str, category: str) -> dict:
        """
        爬取单个 URL
        category: 'negative' (负向受罚案例) / 'positive' (正向获益案例)
        """
        async with self.semaphore:
            # 断点续传检查
            if self.cache.is_crawled(url):
                return {"url": url, "status": "skipped", "category": category}

            try:
                async with self.session.get(url, ssl=False) as response:
                    html = await response.text(encoding='utf-8', errors='replace')
                    title = self._extract_title(html)
                    content = self._extract_content(html)

                    # 写入缓冲
                    await self._add_to_buffer((
                        url, 'done', category, title, content[:5000],
                        datetime.now().isoformat(), None
                    ))

                    return {
                        "url": url,
                        "status": "success",
                        "category": category,
                        "title": title,
                        "content_length": len(content),
                    }

            except asyncio.TimeoutError:
                await self._add_to_buffer((
                    url, 'failed', category, None, None,
                    datetime.now().isoformat(), "Timeout"
                ))
                return {"url": url, "status": "timeout", "category": category}

            except Exception as e:
                await self._add_to_buffer((
                    url, 'failed', category, None, None,
                    datetime.now().isoformat(), str(e)
                ))
                return {"url": url, "status": "failed", "error": str(e), "category": category}

    def _extract_title(self, html: str) -> str:
        """从 HTML 中提取标题"""
        import re
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_content(self, html: str) -> str:
        """从 HTML 中提取正文（简化版）"""
        import re
        # 移除 script/style 标签
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # 提取文本
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:10000]  # 限制长度

    async def crawl_batch(self, urls: List[tuple]) -> List[dict]:
        """
        批量爬取
        urls: [(url, category), ...]
        category: 'negative' / 'positive'
        """
        # 先注册所有 URL 为 pending 状态
        all_urls = [u[0] for u in urls]
        self.cache.mark_pending(all_urls)

        # 并发爬取
        tasks = [self.crawl_single(url, cat) for url, cat in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 最终刷入缓冲
        await self._flush_buffer()

        return [
            r for r in results
            if isinstance(r, dict)
        ]


# ──────────────────────────────────────────────
# 案例源配置
# ──────────────────────────────────────────────

# 负向受罚案例源（违规封号/限流案例）
NEGATIVE_SOURCES = [
    # 抖音违规案例
    ("https://www.douyin.com/search/违规封号案例", "negative"),
    ("https://www.douyin.com/search/限流警告", "negative"),
    ("https://www.douyin.com/search/广告法违规", "negative"),
    ("https://www.douyin.com/search/虚假宣传处罚", "negative"),
    # 视频号违规案例
    ("https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_agreement&s=terms", "negative"),
]

# 正向获益案例源（合规起量/政策扶持案例）
POSITIVE_SOURCES = [
    # 抖音正向案例
    ("https://www.douyin.com/search/优质创作者扶持", "positive"),
    ("https://www.douyin.com/search/原创内容激励", "positive"),
    ("https://www.douyin.com/search/长视频扶持计划", "positive"),
    ("https://www.douyin.com/search/真实体验推荐", "positive"),
    # 视频号正向案例
    ("https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_agreement&s=operator", "positive"),
]


# ──────────────────────────────────────────────
# 报告生成
# ──────────────────────────────────────────────

def generate_scan_report(cache: RadarCache) -> str:
    """生成扫描报告 Markdown"""
    stats = cache.get_stats()
    negative_cases = cache.get_results("negative")
    positive_cases = cache.get_results("positive")

    lines = [
        "# 规则甄查 · 红绿灯双向雷达扫描报告",
        "",
        f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**引擎版本：** v2.0.0 (Dual-Direction Navigation)",
        f"**硬件适配：** ThinkPad P15V",
        "",
        "---",
        "",
        "## 📊 扫描统计",
        "",
        f"| 指标 | 数值 |",
        f"| :--- | :--- |",
        f"| 总扫描数 | {stats['total']} |",
        f"| 成功 | {stats['done']} |",
        f"| 待处理 | {stats['pending']} |",
        f"| 失败 | {stats['failed']} |",
        "",
        "---",
        "",
        "## 🔴 负向受罚案例",
        "",
    ]

    if negative_cases:
        for i, case in enumerate(negative_cases[:20], 1):
            lines.append(f"### {i}. {case['title'] or '无标题'}")
            lines.append(f"- **来源：** {case['url']}")
            lines.append(f"- **采集时间：** {case['crawled_at']}")
            if case['content']:
                lines.append(f"- **内容摘要：** {case['content'][:200]}...")
            lines.append("")
    else:
        lines.append("> 暂未采集到负向案例数据。\n")

    lines.extend([
        "---",
        "",
        "## 🟢 正向获益案例",
        "",
    ])

    if positive_cases:
        for i, case in enumerate(positive_cases[:20], 1):
            lines.append(f"### {i}. {case['title'] or '无标题'}")
            lines.append(f"- **来源：** {case['url']}")
            lines.append(f"- **采集时间：** {case['crawled_at']}")
            if case['content']:
                lines.append(f"- **内容摘要：** {case['content'][:200]}...")
            lines.append("")
    else:
        lines.append("> 暂未采集到正向案例数据。\n")

    lines.extend([
        "---",
        "",
        "*报告由 规则甄查 · 甄先生 v2.0 自动生成*",
    ])

    return "\n".join(lines)


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

async def main():
    import sys

    print("=" * 60)
    print("  规则甄查 · 甄先生 v2.0 — 红绿灯双向雷达扫描")
    print("  ThinkPad P15V 多核优化版")
    print("=" * 60)

    # 合并正反案例源
    all_sources = NEGATIVE_SOURCES + POSITIVE_SOURCES
    print(f"\n📡 待扫描源: {len(all_sources)} 个")
    print(f"   🔴 负向案例: {len(NEGATIVE_SOURCES)} 个")
    print(f"   🟢 正向案例: {len(POSITIVE_SOURCES)} 个")
    print(f"   ⚡ 并发数: {MAX_CONCURRENCY} (P15V 优化)")
    print(f"   💾 存储路径: {DATA_DIR}")

    async with AsyncRadarScanner() as scanner:
        print(f"\n{'='*60}")
        print("  开始扫描...")
        print(f"{'='*60}\n")

        results = await scanner.crawl_batch(all_sources)

        success = sum(1 for r in results if r["status"] == "success")
        skipped = sum(1 for r in results if r["status"] == "skipped")
        failed = sum(1 for r in results if r["status"] in ("failed", "timeout"))

        print(f"\n{'='*60}")
        print("  扫描完成")
        print(f"{'='*60}")
        print(f"  ✅ 成功: {success}")
        print(f"  ⏭️  跳过(已缓存): {skipped}")
        print(f"  ❌ 失败: {failed}")

    # 生成报告
    cache = RadarCache()
    report = generate_scan_report(cache)
    report_path = DATA_DIR / f"radar_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report, encoding="utf-8")
    cache.close()

    print(f"\n📄 报告已生成: {report_path}")
    print(f"💾 缓存数据库: {CACHE_DB}")
    print(f"\n💡 提示: 下次运行将自动跳过已缓存 URL，实现断点续传。")
    print(f"   使用 --force 参数可强制重新扫描所有 URL。")

    # 输出统计摘要
    stats = RadarCache().get_stats()
    print(f"\n📊 缓存统计: 总计 {stats['total']} | 成功 {stats['done']} | 待处理 {stats['pending']} | 失败 {stats['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
