"""
Obsidian 全局重构脚本 — Karpathy 演化逻辑
=============================================
将库中所有笔记按 Raw/Concept/Wiki/Contrast/Inbox 分类迁移.

物理移动: GET(读) + PUT(写新路径) + DELETE(删旧路径)
(Obsidian REST API 的 PATCH 仅用于笔记内编辑, 不支持移动)

流程:
  1. Dry Run 模式: 扫描 → 分类 → 显示重构清单
  2. 输入 CONFIRM 后执行真实移动
  3. 可选: 修复内部 wikilink 引用

用法:
  python obsidian_vault_restructure.py     # 交互式 (Dry Run → CONFIRM → 执行)
  python obsidian_vault_restructure.py --dry-run  # 仅显示预览, 不执行
  python obsidian_vault_restructure.py --execute   # 跳过确认直接执行 (危险!)
  python obsidian_vault_restructure.py --fix-links # 仅修复 wikilink (执行后运行)
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VAULT_DIR = SCRIPT_DIR.parent  # E:/Obsidian/
CONFIG_FILE = SCRIPT_DIR / "config.json"

# ── 目标目录结构 ──────────────────────────────────────────────────
TARGET_DIRS = {
    "inbox": "00_Inbox",        # 无法判定
    "raw": "01_Raw",            # 原始剪藏/碎片
    "concept": "02_Concept",    # 单一概念/术语
    "wiki": "03_Wiki",          # 结构化长文/百科
    "contrast": "04_Contrast",  # A vs B 对比
}

# ── 保护路径 (绝对不触碰) ─────────────────────────────────────────
PROTECTED_PREFIXES = [
    ".obsidian",
    ".smart-env",
    "scripts",
    "wiki",          # 已是正确结构
]


class VaultRestructurer:
    """主重构引擎"""

    def __init__(self, config):
        self.config = config
        self.base_url = config["obsidian_api"]["base_url"]
        self.api_key = config["obsidian_api"]["api_key"]
        self.plan = []   # [(old_path, new_path, classification)]
        self.move_log = []
        self.api_count = 0

    # ── REST API ──────────────────────────────────────────────────

    def _api(self, method, path, data=None):
        """统一的 API 请求."""
        segments = path.strip("/").split("/")
        encoded = "/".join(urllib.parse.quote(s, safe="") for s in segments)
        url = f"{self.base_url}/vault/{encoded}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if data is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
        body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data else None
        req = urllib.request.Request(url, headers=headers, method=method, data=body)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                self.api_count += 1
                return raw if resp.status < 300 else None
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            if e.code != 404:  # 404 is expected for some checks
                print(f"  [API {e.code}] {method} {url}")
                if detail and len(detail) < 200:
                    print(f"    {detail}")
            return None
        except urllib.error.URLError as e:
            print(f"  [API ERROR] Obsidian running? {e.reason}")
            return None

    def get_content(self, path):
        """GET 读取笔记内容."""
        return self._api("GET", path)

    def create_file(self, path, content):
        """PUT 创建新文件."""
        return self._api("PUT", path, {"content": content})

    def delete_file(self, path):
        """DELETE 删除文件."""
        return self._api("DELETE", path)

    def api_alive(self):
        """检查 API 是否可达. 用根端点."""
        url = f"{self.base_url}/"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False

    # ── 文件遍历 ──────────────────────────────────────────────────

    def scan_vault(self, include_protected=False):
        """遍历库中所有 .md 文件. 返回 [(rel_path, abs_path)]."""
        files = []
        for root, dirs, fnames in os.walk(VAULT_DIR):
            # 跳过保护目录
            rel = Path(root).relative_to(VAULT_DIR).as_posix()
            if not include_protected:
                skip = False
                for p in PROTECTED_PREFIXES:
                    if rel == p or rel.startswith(p + "/"):
                        skip = True
                        break
                if skip:
                    dirs[:] = []  # 不进入子目录
                    continue

            for fname in fnames:
                if not fname.endswith(".md"):
                    continue
                full = os.path.join(root, fname)
                rel_path = os.path.relpath(full, VAULT_DIR).replace("\\", "/")
                files.append((rel_path, full))
        return sorted(files, key=lambda x: x[0])

    # ── 内容读取 ──────────────────────────────────────────────────

    def read_local(self, abs_path):
        """本地读文件 (快速, 无需 API)."""
        try:
            with open(abs_path, encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    # ── 内容分类器 ────────────────────────────────────────────────

    def classify(self, rel_path, content):
        """
        路由分类.
        返回: (target_type, new_path_suffix, reason)
          target_type: inbox|raw|concept|wiki|contrast
          new_path_suffix: 相对于目标目录的路径 (含 .md 或目录)
          reason: 分类理由
        """
        fname = os.path.basename(rel_path)
        stem = fname.replace(".md", "")
        ext = ".md"

        # ── 批量路由: 整个目录迁移, 保留子路径 ──
        BULK_ROUTES = {
            "Gemini对话/":    ("raw",  "Gemini对话"),   # 保持子结构
            "Google活动记录/":("raw",  "Google活动记录"),
            "Day Planners/":  ("inbox", "Day_Planners"),
            "工作资料库/":    ("wiki",  ""),             # 直接放 wiki 根目录
            "AI/":            ("raw",  "AI"),
            "Inbox/":         ("raw",  ""),             # 直接放 raw 根目录
        }
        for prefix, (rtype, subdir) in BULK_ROUTES.items():
            if rel_path.startswith(prefix):
                if subdir:
                    # 保留子路径: Gemini对话/品牌设计/.../file.md
                    subpath = rel_path[len(prefix):]  # 去掉前缀
                    suffix = f"{subdir}/{subpath}"
                else:
                    suffix = rel_path[len(prefix):]  # 保持原路径
                return (rtype, suffix, f"批量路由: {prefix}")

        # ── 根目录文件: 内容判定 ──
        # YAML frontmatter 检查
        fm_type = self._check_frontmatter_type(content)
        if fm_type:
            return (fm_type, f"{stem}{ext}", f"Frontmatter: {stem}")

        # 文件名含 vs / vs  → contrast
        if re.search(r'[_\s]vs[_\.\s]', stem, re.IGNORECASE):
            return ("contrast", f"{stem}{ext}", "文件名含 vs")

        # 内容含明确对比结构
        if re.search(r'(对比|区别|差异|优缺点|vs\.?\s)', content[:2000], re.IGNORECASE):
            lines = content.strip().split("\n")
            if len(lines) >= 10 and len(content) >= 500:
                return ("contrast", f"{stem}{ext}", "内容含对比关键词")

        # 短内容 + 定义式 → concept
        lines = content.strip().split("\n")
        char_count = len(content)
        if char_count < 300 and len(lines) <= 15:
            if not self._looks_like_raw(content):
                return ("concept", self._core_name(content, stem), "短内容判定概念")
            return ("raw", f"{stem}{ext}", "短内容似碎片")

        # 长内容, 结构化 → wiki
        if char_count >= 800:
            headings = re.findall(r'^#{1,3}\s+', content, re.MULTILINE)
            if len(headings) >= 3:
                return ("wiki", f"{stem}{ext}", "多级标题结构")
            if char_count >= 2000:
                return ("wiki", f"{stem}{ext}", "超长内容")
            return ("wiki", f"{stem}{ext}", f"长内容 {char_count} 字符")

        return ("inbox", f"{stem}{ext}", "无法判定, 归入 Inbox")

    def _check_frontmatter_type(self, content):
        """从 frontmatter 标签推断类型."""
        fm = self._parse_frontmatter(content)
        if not fm:
            return None
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if any("raw" in t for t in tags):
            return "raw"
        if any("concept" in t or "术语" in t or "定义" in t for t in tags):
            return "concept"
        if any("wiki" in t or "百科" in t or "参考" in t for t in tags):
            return "wiki"
        if any("contrast" in t or "对比" in t or "差异" in t for t in tags):
            return "contrast"
        return None

    def _looks_like_raw(self, content):
        """判断是否像原始碎片内容."""
        lines = content.strip().split("\n")
        # 只有 1-3 行且无标题 → 碎片
        if len(lines) <= 3 and not re.search(r'^#', content, re.MULTILINE):
            return True
        # 含 URL 链接但无自己内容
        urls = re.findall(r'https?://\S+', content)
        own_words = len(re.findall(r'[一-鿿\w]{2,}', content))
        if len(urls) >= 2 and own_words < 10:
            return True
        # 全是 bullet points → 可能还是 raw
        bullet_ratio = len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE)) / max(len(lines), 1)
        if bullet_ratio > 0.6 and len(content) < 500:
            return True
        return False

    def _parse_frontmatter(self, content):
        """解析 YAML frontmatter 为 dict (简化版)."""
        m = re.match(r'^---\s*\n(.*?)\n(?:---|\.\.\.)', content, re.DOTALL)
        if not m:
            return None
        fm = {}
        for line in m.group(1).split("\n"):
            kv = re.match(r'^(\w+):\s*(.*)', line.strip())
            if kv:
                key, val = kv.group(1), kv.group(2).strip()
                # 数组: [a, b, c]
                if val.startswith("[") and val.endswith("]"):
                    val = [v.strip().strip("\"'") for v in val[1:-1].split(",")]
                # 引号
                elif (val.startswith('"') and val.endswith('"')) or \
                     (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                fm[key] = val
        return fm

    def _core_name(self, content, fallback):
        """从内容提取核心概念名. 用于非批量文件."""
        h1 = re.findall(r'^#\s+(.+)', content, re.MULTILINE)
        if h1:
            name = h1[0].strip()
            name = re.sub(r'[\[\]{}()\'\"<>:|*?\\/\n\r\t]', '', name)
            name = re.sub(r'\s+', '_', name)
            return name[:80].rstrip("_") if name else fallback
        return fallback

    def resolve_target(self, target_type, path_suffix):
        """
        解析目标路径. 处理重名版本化.
        path_suffix 含 .md 或子路径.
        返回: (target_rel_path, versioned)
        """
        target_dir = TARGET_DIRS[target_type]
        rel = f"{target_dir}/{path_suffix}"
        # 确保目标子目录存在
        target_abs = os.path.join(VAULT_DIR, rel)
        os.makedirs(os.path.dirname(target_abs), exist_ok=True)
        # 重名版本化
        base, ext = os.path.splitext(path_suffix) if rel.endswith(".md") else (path_suffix, "")
        count = 1
        while os.path.exists(target_abs):
            new_base = f"{base} ({count})"
            rel = f"{target_dir}/{new_base}{ext}"
            target_abs = os.path.join(VAULT_DIR, rel)
            count += 1
        return rel, count > 1

    # ── Plan 构建 ──────────────────────────────────────────────────

    def build_plan(self, progress_callback=None):
        """扫描所有文件, 构建重构计划."""
        files = self.scan_vault()
        plan = []
        skipped = []
        total = len(files)

        for i, (rel_path, abs_path) in enumerate(files):
            if progress_callback:
                progress_callback(i + 1, total, rel_path)

            content = self.read_local(abs_path)
            if not content:
                skipped.append((rel_path, "empty"))
                continue

            target_type, path_suffix, reason = self.classify(rel_path, content)
            if not target_type:
                skipped.append((rel_path, "no_classification"))
                continue

            try:
                target_rel, versioned = self.resolve_target(target_type, path_suffix)
            except KeyError:
                skipped.append((rel_path, f"unknown_type:{target_type}"))
                continue

            if rel_path == target_rel:
                skipped.append((rel_path, "already_correct"))
                continue

            plan.append({
                "old_rel": rel_path,
                "new_rel": target_rel,
                "old_abs": abs_path,
                "type": target_type,
                "reason": reason,
                "versioned": versioned,
                "content": content,
            })

        self.plan = plan
        return plan, skipped

    # ── 执行 ──────────────────────────────────────────────────────

    def execute_plan(self, plan, progress_callback=None):
        """执行移动: PUT → DELETE 两步."""
        total = len(plan)
        results = {"moved": 0, "failed": 0, "errors": []}

        for i, item in enumerate(plan):
            if progress_callback:
                progress_callback(i + 1, total, item["new_rel"])

            # 1. PUT 创建新路径
            created = self.create_file(item["new_rel"], item["content"])
            if created is None:
                results["failed"] += 1
                results["errors"].append((item["old_rel"], "PUT failed"))
                continue

            # 2. DELETE 删除旧路径
            deleted = self.delete_file(item["old_rel"])
            if deleted is None:
                # 写成功但删失败 → 有副本但旧文件残留
                results["failed"] += 1
                results["errors"].append((item["old_rel"], "DELETE failed (file may have copy at new location)"))
                continue

            results["moved"] += 1
            self.move_log.append((item["old_rel"], item["new_rel"]))

        return results

    # ── Wikilink 修复 ─────────────────────────────────────────────

    def fix_wikilinks(self, plan, progress_callback=None):
        """
        修复库中所有笔记的 wikilink 引用.
        扫描全部文件, 将 [[旧路径]] → [[新路径]].
        """
        # 构建映射: old_stem → new_rel (移除了 .md)
        link_map = {}
        for item in plan:
            old_stem = Path(item["old_rel"]).stem
            new_stem = Path(item["new_rel"]).stem
            if old_stem != new_stem:
                link_map[old_stem] = item["new_rel"].replace(".md", "")

        if not link_map:
            print("  No wikilinks to fix (filenames unchanged).")
            return {"fixed": 0, "files_changed": 0}

        # 遍历所有 .md 文件
        all_files = self.scan_vault(include_protected=False)
        changed_files = 0
        total_fixes = 0

        for rel_path, abs_path in all_files:
            content = self.read_local(abs_path)
            if not content:
                continue

            new_content = content
            for old_stem, new_wikilink in link_map.items():
                # [[old_stem]] → [[new_wikilink]]
                pattern = re.compile(r'\[\[(' + re.escape(old_stem) + r')(\|[^\]]+)?\]\]')
                replacement = lambda m: f'[[{new_wikilink}{m.group(1) or ""}]]'
                new_content, count = pattern.subn(replacement, new_content)
                if count > 0:
                    total_fixes += count

            if new_content != content:
                # 通过 API 更新
                result = self._api("PUT", rel_path, {"content": new_content})
                if result is not None:
                    changed_files += 1

        return {"fixed": total_fixes, "files_changed": changed_files}


# ── 打印辅助 ──────────────────────────────────────────────────────

def print_summary(plan, skipped):
    """打印重构清单预览."""
    # 分组统计
    type_counts = {}
    for item in plan:
        t = item["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    target_names = {
        "inbox": "00_Inbox",
        "raw": "01_Raw",
        "concept": "02_Concept",
        "wiki": "03_Wiki",
        "contrast": "04_Contrast",
    }

    print("\n" + "=" * 70)
    print("  Obsidian Vault 重构清单预览")
    print("=" * 70)

    print(f"\n  总计扫描文件: {len(plan) + len(skipped)}")
    print(f"  待移动: {len(plan)}")
    print(f"  跳过: {len(skipped)}\n")

    print("  ┌──────────────────────┬──────────┐")
    print("  │ 目标目录             │ 文件数   │")
    print("  ├──────────────────────┼──────────┤")
    for t, name in target_names.items():
        count = type_counts.get(t, 0)
        print(f"  │ {name:<20} │ {count:<8} │")
    print("  └──────────────────────┴──────────┘")

    # 跳过原因
    skip_reasons = {}
    for _, reason in skipped:
        skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
    if skip_reasons:
        print(f"\n  跳过原因:")
        for reason, count in sorted(skip_reasons.items()):
            print(f"    - {reason}: {count}")

    # 详细清单 (最多显示 50 条)
    print(f"\n  ── 移动清单 ({min(len(plan), 50)}/{len(plan)} 条) ──\n")
    for i, item in enumerate(plan):
        if i >= 50:
            print(f"  ... 还有 {len(plan) - 50} 条未显示")
            break
        tag = {
            "inbox": "[I]",
            "raw": "[R]",
            "concept": "[C]",
            "wiki": "[W]",
            "contrast": "[X]",
        }.get(item["type"], "[?]")
        ver = " (v)" if item["versioned"] else "   "
        print(f"  {tag}{ver} {item['old_rel']}")
        print(f"      → {item['new_rel']}")
        print(f"      ({item['reason']})")
        print()

    print(f"  {len(plan)} files to relocate.")

    # 警告
    if type_counts.get("inbox", 0) > 0:
        print("\n  ⚠ 部分文件归入 00_Inbox. 请人工判定后手动移到正确目录.")
    print()


# ── 主函数 ────────────────────────────────────────────────────────

def main():
    # 加载配置
    if not CONFIG_FILE.exists():
        print(f"[ERROR] config.json not found at {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    # 是否允许覆盖验证
    force_execute = "--execute" in sys.argv
    dry_run_only = "--dry-run" in sys.argv
    fix_links_only = "--fix-links" in sys.argv

    # 检测 Obsidian 是否运行 (用根端点, 不依赖特定文件)
    engine = VaultRestructurer(config)
    alive = engine.api_alive()
    if not alive:
        print("\n[ERROR] Obsidian REST API 不可达. 请确认:")
        print("  1. Obsidian 已打开")
        print("  2. Local REST API 插件已启用")
        print(f"  3. {CONFIG_FILE} 中的 API 密钥正确")
        if not force_execute:
            sys.exit(1)

    if fix_links_only:
        print("\n[FIX-LINKS] 正在扫描并修复 wikilink 引用...\n")
        # Need a plan - reuse from tracker if available
        # For now, scan and build plan
        plan, skipped = engine.build_plan()
        result = engine.fix_wikilinks(plan)
        print(f"\n  Wikilink 修复完成: {result['fixed']} 处链接更新, "
              f"{result['files_changed']} 个文件修改")
        return

    # ── Phase 1: 扫描 + 分类 ──
    print("\n[PHASE 1] 扫描库并分类笔记...")
    print(f"  VAULT: {VAULT_DIR}")

    def show_progress(current, total, path):
        if current % 50 == 0 or current == total:
            print(f"  [{current}/{total}] {path}", flush=True)

    plan, skipped = engine.build_plan(progress_callback=show_progress)
    print(f"\n  扫描完成. API calls: {engine.api_count}")

    # ── 显示预览 ──
    print_summary(plan, skipped)

    # ── Phase 2: Dry Run ──
    if dry_run_only:
        print("[DRY-RUN] 预览模式. 未执行任何移动.\n"
              "运行 python obsidian_vault_restructure.py 进入交互模式.")
        return

    # ── Phase 3: 确认 ──
    if not force_execute:
        confirm = input("\n输入 CONFIRM 开始执行移动 (输入任意内容取消): ").strip()
        if confirm != "CONFIRM":
            print("[CANCELLED] 未执行任何移动.")
            return

    # ── Phase 4: 执行 ──
    print(f"\n[PHASE 2] 执行 {len(plan)} 次移动...")
    results = engine.execute_plan(plan, progress_callback=show_progress)
    print(f"\n  移动完成.")
    print(f"  ✓ 成功: {results['moved']}")
    print(f"  ✗ 失败: {results['failed']}")

    if results["errors"]:
        print(f"\n  错误详情:")
        for old, err in results["errors"][:20]:
            print(f"    - {old}: {err}")
        if len(results["errors"]) > 20:
            print(f"    ... (还有 {len(results['errors']) - 20} 条)")

    # ── Phase 5: Wikilink 修复 (可选) ──
    if results["moved"] > 0:
        print(f"\n[PHASE 3] 建议运行 wikilink 引用修复:")
        print(f"  python obsidian_vault_restructure.py --fix-links")

    print(f"\n  ✓ 总计 API 调用: {engine.api_count}")
    print(f"  ✓ Git 提交建议: git -C \"{VAULT_DIR}\" add -A && git commit -m \"restructure: Karpathy routing\"")


if __name__ == "__main__":
    main()
