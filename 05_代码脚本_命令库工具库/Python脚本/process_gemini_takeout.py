"""
Gemini Takeout (My Activity JSON) → 分类整理 → Obsidian 同步
用法:
  python process_gemini_takeout.py <takeout.zip>
"""
import json, os, re, shutil, zipfile, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from html.parser import HTMLParser

sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

OBSIDIAN_VAULT = Path("E:/Obsidian")
OUTPUT_DIR = Path("E:/MyCodeProjects/02-审计工具/gemini_exported")


class HTMLStripper(HTMLParser):
    """Strip HTML tags, keep text."""
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        self.text.append(data)
    def get_text(self):
        return "".join(self.text)


def strip_html(html: str) -> str:
    s = HTMLStripper()
    s.feed(html)
    return s.get_text().strip()


# ── 8 分类 (2026-05-10 重构: 按内容领域而非工具划分) ─────
# Weighted scoring: higher weight = stronger signal
# Title matches get 3x multiplier vs content matches
CATEGORY_RULES = [
    ("审计合规", 20, ["规则甄查", "违禁词", "广告法", "红绿灯导航", "品牌安全"]),
    ("审计合规", 10, ["审计", "合规", "封号", "限流", "风险控制"]),
    ("审计合规", 5, ["违规", "检测", "敏感词", "禁词", "黑名单", "平台规则"]),
    ("审计合规", 3, ["政策", "审核", "条款", "免责声明"]),
    ("审计合规", 2, ["声明", "协议", "规范", "合规检查"]),

    ("直播运营", 20, ["小桃", "凡姐", "苏苏在浙里", "清晨烟火小厨"]),
    ("直播运营", 10, ["直播", "带货", "ROI", "GPM", "橱窗"]),
    ("直播运营", 5, ["直播间", "粉丝分析", "复盘", "诊断", "话术"]),
    ("直播运营", 3, ["流量", "转化", "千川", "投流", "排品", "挂车"]),
    ("直播运营", 2, ["停留", "互动率", "点击率", "人设", "开播"]),

    ("技术开发", 20, ["python", "javascript", "typescript", "def ", "import "]),
    ("技术开发", 10, ["代码", "编程", "生成代码", "cli"]),
    ("技术开发", 5, ["api", "npm", "pip", "git", "docker", "debug"]),
    ("技术开发", 3, ["claude", "mcp", "json-rpc", "sonnet", "haiku"]),
    ("技术开发", 2, ["函数", "算法", "实现", "修复", "重构"]),

    ("文案创意", 20, ["文案", "短视频脚本", "提示词", "prompt"]),
    ("文案创意", 10, ["标题", "口播", "爆款", "选题", "内容策划"]),
    ("文案创意", 5, ["润色", "改写", "灵感", "故事", "创意"]),
    ("文案创意", 3, ["写作", "文章", "小红书", "内容创作"]),
    ("文案创意", 2, ["封面", "视频脚本", "拍摄"]),

    ("品牌设计", 20, ["LOGO", "logo", "矢量图", "VI设计", "品牌设计"]),
    ("品牌设计", 10, ["配色", "字体", "排版", "品牌命名"]),
    ("品牌设计", 5, ["源文件", "寓意", "效果图", "标识"]),
    ("品牌设计", 3, ["定稿", "色彩", "图标", "图形"]),
    ("品牌设计", 2, ["方案A", "方案B", "视觉效果"]),

    ("系统运维", 20, ["PowerShell", "Clash", "代理端口"]),
    ("系统运维", 10, ["环境变量", "配置文件", "安装"]),
    ("系统运维", 5, ["部署", "网络", "备份", "同步", "加载"]),
    ("系统运维", 3, ["docker", "ssh", "ssl", "证书", "端口"]),
    ("系统运维", 2, ["obsidian", "插件", "终端", "shell", "profile"]),

    ("方案咨询", 10, ["教育", "学校", "转学", "华德福", "课表"]),
    ("方案咨询", 5, ["利弊", "建议", "推荐", "规划"]),
    ("方案咨询", 3, ["比较", "哪个好", "怎么选", "区别"]),
    ("方案咨询", 2, ["方案", "分析"]),
    ("方案咨询", 1, ["人生", "职场", "发展", "能力", "学习"]),

    ("数据报表", 10, ["SQL", "数据库", "查询", "报表"]),
    ("数据报表", 5, ["Excel", "pandas", "numpy", "csv", "统计"]),
    ("数据报表", 3, ["清洗", "可视化", "指标", "趋势"]),
    ("数据报表", 2, ["数据", "图表", "汇总"]),
]

# Default fallback when no keywords match
DEFAULT_CATEGORY = "方案咨询"


def classify(title: str = "", content: str = "") -> str:
    """
    Weighted scoring classifier.
    Title matches get 3x multiplier vs content matches.
    If no keywords match, returns DEFAULT_CATEGORY.
    """
    from collections import defaultdict
    scores = defaultdict(int)
    full_text = (title + " " + content).lower()

    for cat, weight, keywords in CATEGORY_RULES:
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in title.lower():
                scores[cat] += weight * 3
            elif kw_lower in full_text:
                scores[cat] += weight

    if not scores:
        return DEFAULT_CATEGORY
    return max(scores, key=scores.get)


def sanitize_filename(s: str, max_len: int = 30) -> str:
    # Strip ANSI escapes first
    s = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', s)
    s = re.sub(r'[\\/*?:"<>|]', "_", s)
    s = re.sub(r'\s+', " ", s).strip().strip("._-")
    return s[:max_len] or "untitled"


def process_zip(zip_path: str):
    print(f"[1/3] 读取 {zip_path}...")
    z = zipfile.ZipFile(zip_path, "r")

    # 找 My Activity JSON
    json_path = None
    for f in z.namelist():
        if f.endswith(".json") and "Gemini" in f and "Activity" not in f:
            json_path = f
            break
    if not json_path:
        # Try alternate naming
        for f in z.namelist():
            if f.endswith(".json") and "Gemini" in f:
                json_path = f
                break

    if not json_path:
        print("  未找到 Gemini JSON 文件")
        z.close()
        return

    print(f"  发现: {json_path}")
    raw_data = json.loads(z.read(json_path))
    z.close()

    if not isinstance(raw_data, list):
        print("  JSON 格式非列表，尝试提取")
        raw_data = raw_data.get("activity", raw_data.get("items", []))

    total = len(raw_data)
    print(f"  共 {total} 条活动记录")

    # 解码并分类
    conversations = []
    for item in raw_data:
        title = item.get("title", "").strip()
        # 去掉 "Prompted " 前缀
        if title.startswith("Prompted "):
            title = title[9:]
        elif title == "Used Gemini Apps":
            continue  # 纯使用记录，无对话内容
        elif title.startswith("Created Gemini Canvas"):
            continue  # Canvas 创建记录

        html_items = item.get("safeHtmlItem", [])
        content = ""
        for h in html_items:
            raw_html = h.get("html", "") if isinstance(h, dict) else ""
            content += strip_html(raw_html) + "\n"

        if not content.strip():
            continue

        ts = item.get("time", "")
        date_prefix = ts[:10] if ts else ""

        conversations.append({
            "title": title or "(无标题)",
            "date": date_prefix,
            "timestamp": ts,
            "content": content.strip()[:5000],
            "header": item.get("header", ""),
        })

    print(f"[2/3] 有效对话: {len(conversations)} 条，开始分类...")

    # 分类
    by_cat = defaultdict(list)
    for conv in conversations:
        cat = classify(title=conv["title"], content=conv["content"])
        by_cat[cat].append(conv)

    for cat, convs in sorted(by_cat.items()):
        print(f"   [{cat}] {len(convs)} 条")

    # 写文件
    out_root = OUTPUT_DIR / "organized"
    if out_root.exists():
        shutil.rmtree(out_root)

    total_files = 0
    for cat, convs in by_cat.items():
        cat_dir = out_root / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        convs.sort(key=lambda c: c["timestamp"], reverse=True)
        for i, conv in enumerate(convs, 1):
            safe = sanitize_filename(conv["title"]) or f"conv_{i}"
            date = conv["date"]
            fname = f"{date}_{safe}_{i}.md" if date else f"{safe}_{i}.md"

            content = f"""---
title: {conv["title"]}
source: gemini
date: {conv["date"] or "unknown"}
category: {cat}
tags: [gemini, {cat}]
---

## {conv["title"]}

{conv["content"]}

---
*从 Gemini 导出，{conv["date"][:7] if conv["date"] else ""}*
"""
            (cat_dir / fname).write_text(content, encoding="utf-8")
            total_files += 1

    # 写索引
    index = f"""# Gemini 对话索引

导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}
总对话数: {total_files}

## 分类分布

"""
    for cat in sorted(by_cat.keys()):
        index += f"- **{cat}**: {len(by_cat[cat])} 条\n"

    index += "\n## 最近 20 条\n\n"
    all_sorted = sorted(conversations, key=lambda c: c["timestamp"], reverse=True)
    for conv in all_sorted[:20]:
        cat = classify(title=conv["title"], content=conv["content"])
        index += f"- [{conv['title'][:50]}]({cat}/{sanitize_filename(conv['title'])}.md)  ({conv['date']})\n"

    (OUTPUT_DIR / "_index.md").write_text(index, encoding="utf-8")

    print(f"\n[3/3] 同步到 Obsidian...")
    # 清空目标
    obs_target = OBSIDIAN_VAULT / "Gemini对话"
    if obs_target.exists():
        shutil.rmtree(obs_target)

    # 按分类写入
    for cat_dir in out_root.iterdir():
        if cat_dir.is_dir():
            for f in cat_dir.glob("*.md"):
                target = obs_target / cat_dir.name / f.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")

    # 复制索引
    (obs_target / "_index.md").write_text(index, encoding="utf-8")

    print(f"   保存至 Obsidian: {obs_target}")
    print(f"\n{'='*50}")
    print(f"完成! {total_files} 条对话已同步到 Obsidian")
    print(f"分类: {', '.join(sorted(by_cat.keys()))}")
    print(f"{'='*50}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python process_gemini_takeout.py <takeout.zip>")
        sys.exit(1)
    z = sys.argv[1]
    if not os.path.exists(z):
        print(f"文件不存在: {z}")
        sys.exit(1)
    process_zip(z)
