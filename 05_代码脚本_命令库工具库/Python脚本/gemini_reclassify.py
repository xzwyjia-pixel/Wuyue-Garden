"""
Gemini 对话重分类脚本 v3 — 8 分类 + 子目录层级 ≤30 条/目录

流程:
  1. 从 organized/ 读取 2245 条导出对话
  2. 新 8 分类 (weighted classifier)
  3. 二级: 话题子分类 (topic-based)
  4. 三级: 若子分类 >30 条, 按月拆分 (YYYY-MM)
  5. 写入 reorganized_v3/ + 同步 Obsidian

用法:
  cd 02-审计工具
  python gemini_reclassify.py           # 执行
  python gemini_reclassify.py --dry-run  # 预览
  python gemini_reclassify.py --stats    # 仅统计
"""

import sys, json, shutil, re, math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
ORGANIZED = SCRIPT_DIR / "gemini_exported" / "organized"
REORGANIZED = SCRIPT_DIR / "gemini_exported" / "reorganized_v3"
OBSIDIAN_VAULT = Path("E:/Obsidian/Gemini对话")

sys.path.insert(0, str(SCRIPT_DIR))
from process_gemini_takeout import classify, CATEGORY_RULES

NEW_CATEGORIES = sorted(set(cat for cat, w, kws in CATEGORY_RULES))
PREFIX_MAP = {
    "审计合规": "[AUD]", "直播运营": "[LIV]", "技术开发": "[DEV]",
    "文案创意": "[CPY]", "品牌设计": "[BRD]", "系统运维": "[OPS]",
    "方案咨询": "[CON]", "数据报表": "[DAT]",
}

DRY_RUN = "--dry-run" in sys.argv
STATS_ONLY = "--stats" in sys.argv
MAX_PER_DIR = 30

# ═══════════════════════════════════════════════════════════
#  二级分类规则 (按 8 个一级分类)
#  空 keyword 列表 = catch-all 兜底 (放在最后)
# ═══════════════════════════════════════════════════════════

SUBCATEGORY_RULES = {
    "审计合规": [
        ("规则甄查",   ["规则甄查", "规则引擎", "红绿灯", "校准", "甄查系统", "违禁词检测系统"]),
        ("违禁词",     ["违禁词", "敏感词", "禁词", "黑名单", "keywords"]),
        ("广告法",     ["广告法", "违规", "处罚", "罚款"]),
        ("平台风控",   ["限流", "封号", "风险", "平台规则", "审核", "平台风控"]),
        ("协议条款",   ["条款", "协议", "声明", "免责", "合同", "规范"]),
        ("通用",       []),
    ],
    "直播运营": [
        ("小桃",       ["小桃"]),
        ("凡姐",       ["凡姐"]),
        ("苏苏",       ["苏苏在浙里", "苏苏", "清晨烟火"]),
        ("通用策略",   []),
    ],
    "技术开发": [
        ("Python",     ["python", "pip", "pandas", "numpy", "def ", "import "]),
        ("脚本工具",   ["脚本", "cli", "命令行", "自动化"]),
        ("前端",       ["javascript", "typescript", "vue", "react", "html", "css", "前端"]),
        ("API集成",    ["api", "mcp", "json-rpc", "接口"]),
        ("Claude/MCP", ["claude", "sonnet", "haiku", "deepseek", "gpts"]),
        ("调试修复",   ["bug", "debug", "修复", "报错", "错误", "问题"]),
        ("通用开发",   []),
    ],
    "文案创意": [
        ("短视频脚本", ["短视频", "脚本", "口播", "拍摄", "视频脚本"]),
        ("Prompt",    ["prompt", "提示词", "prompt提示"]),
        ("标题封面",   ["标题", "封面", "爆款", "选题"]),
        ("故事创作",   ["故事", "创作", "短文", "叙事", "小说"]),
        ("小红书",     ["小红书", "种草"]),
        ("营销文案",   ["营销", "广告语", "slogan", "宣传"]),
        ("改写润色",   ["润色", "改写", "优化", "修改"]),
        ("内容策划",   ["策划", "内容规划", "内容方案"]),
        ("通用文案",   []),
    ],
    "品牌设计": [
        ("LOGO设计",   ["LOGO", "logo", "矢量", "标识", "图标", "寓意"]),
        ("品牌命名",   ["命名", "品牌名", "名字"]),
        ("VI配色",     ["配色", "字体", "排版", "VI", "色彩", "视觉效果"]),
        ("效果图",     ["效果图", "源文件", "定稿"]),
        ("通用设计",   []),
    ],
    "系统运维": [
        ("PowerShell", ["powershell", "pwsh", "ps1"]),
        ("网络代理",   ["代理", "clash", "vpn", "端口", "网络"]),
        ("环境配置",   ["环境变量", "path", "配置", "安装", "profile", "profile"]),
        ("Obsidian",   ["obsidian", "插件", "vault", "反向链接"]),
        ("部署同步",   ["部署", "同步", "备份", "加载", "docker", "ssh"]),
        ("通用运维",   []),
    ],
    "方案咨询": [
        ("教育规划",   ["教育", "学校", "转学", "华德福", "课表", "孩子", "儿子", "闺女", "老大"]),
        ("商业方案",   ["方案", "商业", "项目", "计划", "策划"]),
        ("生活建议",   ["人生", "职场", "建议", "推荐", "选择"]),
        ("决策分析",   ["比较", "哪个好", "怎么选", "利弊", "区别"]),
        ("通用咨询",   []),
    ],
    "数据报表": [
        ("数据分析",   ["pandas", "numpy", "统计", "分析"]),
        ("SQL查询",    ["sql", "数据库", "查询"]),
        ("报表可视化", ["报表", "excel", "图表", "可视化"]),
        ("通用数据",   []),
    ],
}


def subcategorize(main_cat: str, title: str, content: str = "") -> str:
    """Assign subcategory within main category. Catch-all as fallback."""
    rules = SUBCATEGORY_RULES.get(main_cat, [])
    text = (title + " " + content).lower()

    for subcat, keywords in rules:
        if not keywords:
            continue  # skip catch-all, use as fallback
        for kw in keywords:
            if kw.lower() in text:
                return subcat

    # Fallback to catch-all
    for subcat, keywords in rules:
        if not keywords:
            return subcat
    return "通用"


def get_month_key(date_str: str) -> str:
    """Extract YYYY-MM from date string."""
    if not date_str or date_str == "unknown":
        return "unknown-date"
    try:
        return date_str[:7]
    except (IndexError, TypeError):
        return "unknown-date"


def get_week_key(date_str: str) -> str:
    """Extract week number within month (W1-W5)."""
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        week = math.ceil(dt.day / 7)
        return f"W{week}"
    except (ValueError, IndexError, TypeError):
        return "W0"


def parse_md(filepath: Path) -> dict:
    """Parse exported Gemini .md file: extract frontmatter + body."""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not match:
        return {"title": filepath.stem, "content": text, "old_cat": "unknown"}
    front = match.group(1)
    body = match.group(2).strip()
    title = ""
    old_cat = "unknown"
    date = ""
    for line in front.split("\n"):
        if line.startswith("title:"):
            title = line[6:].strip().strip('"')
        elif line.startswith("category:"):
            old_cat = line[9:].strip()
        elif line.startswith("date:"):
            date = line[5:].strip()
    return {
        "title": title or filepath.stem,
        "content": body,
        "old_cat": old_cat,
        "date": date,
        "fname": filepath.name,
    }


def count_files(directory: Path):
    return sum(1 for f in directory.rglob("*.md") if f.is_file() and f.name != "_index.md")


def ensure_unique_path(target_dir: Path, fname: str) -> Path:
    """Avoid filename collisions by appending counter."""
    stem = Path(fname).stem
    ext = Path(fname).suffix
    target = target_dir / fname
    counter = 1
    while target.exists():
        target = target_dir / f"{stem}_{counter}{ext}"
        counter += 1
    return target


def main():
    if not ORGANIZED.exists():
        print(f"[ERROR] 源目录不存在: {ORGANIZED}")
        return

    total = count_files(ORGANIZED)
    print(f"源目录: {ORGANIZED}")
    print(f"总文件: {total}")
    print(f"新分类: {', '.join(NEW_CATEGORIES)}")
    print(f"子目录上限: {MAX_PER_DIR} 条/目录")
    print()

    # ── Phase 1: Classify + Subcategorize ─────────────────
    old_counts = defaultdict(int)
    new_counts = defaultdict(int)
    subcat_counts = defaultdict(int)  # (main_cat, subcat) -> count
    files = []

    for md_file in sorted(ORGANIZED.rglob("*.md")):
        parsed = parse_md(md_file)
        old_counts[parsed["old_cat"]] += 1

        new_cat = classify(title=parsed["title"], content=parsed["content"])
        new_counts[new_cat] += 1

        subcat = subcategorize(new_cat, parsed["title"], parsed["content"])
        subcat_counts[(new_cat, subcat)] += 1

        files.append({
            **parsed,
            "new_cat": new_cat,
            "subcat": subcat,
            "source_path": md_file,
        })

    # ── Phase 2: Determine hierarchy ──────────────────────
    # (main_cat, subcat, month) -> count
    leaf_counts = defaultdict(int)
    file_paths = []  # (file_info, relative_path)

    for f in files:
        main_cat = f["new_cat"]
        subcat = f["subcat"]
        entry_count = subcat_counts[(main_cat, subcat)]

        if entry_count <= MAX_PER_DIR:
            # Flat under subcategory
            rel_dir = f"{main_cat}/{subcat}"
            leaf_counts[(main_cat, subcat)] += 1
        else:
            # Split by month
            month = get_month_key(f["date"])
            rel_dir = f"{main_cat}/{subcat}/{month}"
            leaf_counts[(main_cat, subcat, month)] += 1

        file_paths.append((f, rel_dir))

    # Check if any leaf > MAX_PER_DIR and need week split
    # Re-compute for oversize leaves
    final_paths = []
    oversize_realloc = 0
    for f, rel_dir in file_paths:
        parts = rel_dir.split("/")
        if len(parts) == 3:
            main_cat, subcat, month = parts
            key = (main_cat, subcat, month)
        elif len(parts) == 2:
            main_cat, subcat = parts
            key = (main_cat, subcat)
        else:
            key = rel_dir

        if leaf_counts.get(key, 0) > MAX_PER_DIR:
            # Need week split
            week = get_week_key(f["date"])
            rel_dir = f"{rel_dir}/{week}"
            leaf_counts[(key, week)] = leaf_counts.get((key, week), 0) + 1
            oversize_realloc += 1

        final_paths.append((f, rel_dir))

    if oversize_realloc:
        print(f"  周拆分: {oversize_realloc} 条分配到周级目录")

    # ── Phase 3: Report ───────────────────────────────────
    print(f"{'='*60}")
    print("分类迁移统计")
    print(f"{'='*60}")

    print(f"\n{'旧分类':<16s} → {'新分类':<16s} {'迁移数':>6s}")
    print(f"{'─'*42}")
    cross = defaultdict(lambda: defaultdict(int))
    for f in files:
        cross[f["old_cat"]][f["new_cat"]] += 1
    for old_cat in sorted(cross.keys()):
        for new_cat in sorted(cross[old_cat].keys()):
            if old_cat != new_cat:
                print(f"{old_cat:<16s} → {new_cat:<16s} {cross[old_cat][new_cat]:>6d}")

    print(f"\n{'='*60}")
    print("分布对比")
    print(f"{'='*60}")
    print(f"\n{'分类':<16s} {'旧':>6s} {'新':>6s} {'子分类':>6s}")
    print(f"{'─'*45}")
    for cat in sorted(NEW_CATEGORIES):
        old_n = old_counts.get(cat, 0)
        new_n = new_counts.get(cat, 0)
        sub_n = len({s for (mc, s) in subcat_counts.keys() if mc == cat})
        print(f"{PREFIX_MAP.get(cat,'') + ' ' + cat:<16s} {old_n:>6d} {new_n:>6d} {sub_n:>6d}")
    # Show removed categories
    for cat in sorted(old_counts.keys()):
        if cat not in NEW_CATEGORIES and cat != "unknown":
            print(f"  {cat:<16s} {old_counts[cat]:>6d} {'-':>6s} {'-':>6s}")

    changes = sum(1 for f in files if f["old_cat"] != f["new_cat"])
    print(f"\n分类变更: {changes}/{total} ({changes/total*100:.1f}%)")

    # Subcategory breakdown
    print(f"\n{'='*60}")
    print("子分类明细")
    print(f"{'='*60}")
    for main_cat in NEW_CATEGORIES:
        print(f"\n{main_cat} ({new_counts.get(main_cat, 0)} 条):")
        subs = sorted({s for (mc, s) in subcat_counts.keys() if mc == main_cat})
        for sub in subs:
            cnt = subcat_counts[(main_cat, sub)]
            bar = "█" * min(cnt // 5 + 1, 30)
            print(f"  {sub:<12s} {cnt:>4d}  {bar}")

    if STATS_ONLY:
        return

    # ── Phase 4: Write ────────────────────────────────────
    if not DRY_RUN:
        if REORGANIZED.exists():
            shutil.rmtree(REORGANIZED)

        written = 0
        index_entries = defaultdict(list)  # main_cat -> [(subcat, rel_path, title, date)]

        for f, rel_dir in final_paths:
            target_dir = REORGANIZED / rel_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            target = ensure_unique_path(target_dir, f["fname"])

            content = f"""---
title: {f["title"]}
source: gemini
date: {f.get("date", "unknown")}
category: {f["new_cat"]}
subcategory: {f["subcat"]}
old_category: {f["old_cat"]}
tags: [gemini, {f["new_cat"]}, {f["subcat"]}]
---

## {f["title"]}

{f["content"]}

---
*Gemini · {f["new_cat"]} / {f["subcat"]} · {f.get("date", "")}*
"""
            target.write_text(content, encoding="utf-8")
            written += 1

            # Track for index
            rel_path = str(target.relative_to(REORGANIZED)).replace("\\", "/")
            index_entries[f["new_cat"]].append((f["subcat"], rel_path, f["title"], f.get("date", "")))

        print(f"\n[写入] {written} 条到 {REORGANIZED}")

        # ── Index ──────────────────────────────────────────
        index = f"""# Gemini 对话索引 (分层结构)

重分类: {datetime.now().strftime("%Y-%m-%d %H:%M")}
总对话: {written}
分类: {', '.join(f'{PREFIX_MAP.get(c)} {c}' for c in NEW_CATEGORIES)}
子目录上限: {MAX_PER_DIR} 条/目录

## 目录结构

"""
        for main_cat in NEW_CATEGORIES:
            pfx = PREFIX_MAP.get(main_cat, "")
            count = new_counts.get(main_cat, 0)
            index += f"### {pfx} {main_cat} ({count} 条)\n\n"
            # List subcategories
            subs = sorted({s for (mc, s) in subcat_counts.keys() if mc == main_cat})
            for sub in subs:
                cnt = subcat_counts[(main_cat, sub)]
                if cnt <= MAX_PER_DIR:
                    index += f"- [{sub}]({main_cat}/{sub}/) — {cnt} 条\n"
                else:
                    index += f"- **{sub}** ({cnt} 条, 按月拆分):\n"
                    # List months
                    months = sorted({p.split("/")[2] for _, p, _, _ in index_entries[main_cat]
                                     if p.startswith(f"{main_cat}/{sub}/") and "/" in p[len(f"{main_cat}/{sub}/"):]})
                    for m in months:
                        month_files = [(r, t, d) for s2, r, t, d in index_entries[main_cat]
                                       if r.startswith(f"{main_cat}/{sub}/{m}/") or r.startswith(f"{main_cat}/{sub}/{m}.")]
                        index += f"  - [{m}]({main_cat}/{sub}/{m}/) — {len(month_files)} 条\n"
            index += "\n"

        index += "---\n\n### 最近 20 条\n\n"
        by_date = sorted(final_paths, key=lambda x: x[0].get("date", ""), reverse=True)
        for f, _ in by_date[:20]:
            pfx = PREFIX_MAP.get(f["new_cat"], "")
            # Find the actual relative path
            for _, rp, _, _ in index_entries[f["new_cat"]]:
                if f["fname"] in rp:
                    index += f"- {pfx} [{f['title'][:50]}]({rp}) ({f.get('date', '')[:10]})\n"
                    break

        (REORGANIZED / "_index.md").write_text(index, encoding="utf-8")
        print(f"  索引已写入")

        # ── Sync to Obsidian ──────────────────────────────
        print(f"\n[同步] Obsidian...")
        obs_target = OBSIDIAN_VAULT
        if obs_target.exists():
            shutil.rmtree(obs_target)

        # Walk the hierarchical reorganized tree
        for md_file in REORGANIZED.rglob("*.md"):
            if md_file.name == "_index.md":
                continue
            rel = md_file.relative_to(REORGANIZED)
            target = obs_target / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(md_file.read_text(encoding="utf-8"), encoding="utf-8")

        # Copy index
        src_idx = REORGANIZED / "_index.md"
        if src_idx.exists():
            (obs_target / "_index.md").write_text(
                src_idx.read_text(encoding="utf-8"), encoding="utf-8"
            )

        # Verify
        obs_count = count_files(obs_target)
        print(f"  已同步: {obs_target} ({obs_count} 条)")

        # ── Hierarchy summary ─────────────────────────────
        print(f"\n{'='*60}")
        print("层级结构总览")
        print(f"{'='*60}")
        dir_count = 0
        for main_cat in NEW_CATEGORIES:
            subs = sorted(REORGANIZED.glob(f"{main_cat}/*/"))
            for sub_dir in subs:
                sub_name = sub_dir.name
                months = sorted(sub_dir.glob("*/")) if list(sub_dir.glob("*/")) else []
                if months:
                    for m_dir in months:
                        cnt = count_files(m_dir)
                        dir_count += 1
                        marker = " ⚠" if cnt > MAX_PER_DIR else ""
                        print(f"  {main_cat}/{sub_name}/{m_dir.name}: {cnt}{marker}")
                else:
                    cnt = count_files(sub_dir)
                    dir_count += 1
                    marker = " ⚠" if cnt > MAX_PER_DIR else ""
                    print(f"  {main_cat}/{sub_name}: {cnt}{marker}")

        print(f"\n总目录数: {dir_count}")
        print(f"上限: ≤{MAX_PER_DIR} 条/目录")

        print(f"\n{'='*60}")
        print(f"完成! {written} 条, {dir_count} 个目录")
        print(f"{'='*60}")

    else:
        # Dry run: show hierarchy preview
        print(f"\n[dry-run] 预览层级")
        print(f"{'='*60}")
        for main_cat in NEW_CATEGORIES:
            print(f"\n{main_cat} ({new_counts.get(main_cat, 0)}):")
            subs = sorted({s for (mc, s) in subcat_counts.keys() if mc == main_cat})
            for sub in subs:
                cnt = subcat_counts[(main_cat, sub)]
                if cnt <= MAX_PER_DIR:
                    print(f"  └─ {sub}/ ({cnt})")
                else:
                    print(f"  └─ {sub}/ ({cnt}) — 按月拆分:")
                    # Show estimated month counts
                    month_buckets = defaultdict(int)
                    for f, _ in final_paths:
                        if f["new_cat"] == main_cat and f["subcat"] == sub:
                            month = get_month_key(f["date"])
                            month_buckets[month] += 1
                    for m in sorted(month_buckets.keys()):
                        mc = month_buckets[m]
                        marker = " ⚠" if mc > MAX_PER_DIR else ""
                        print(f"      └─ {m}/ ({mc}){marker}")


if __name__ == "__main__":
    main()
