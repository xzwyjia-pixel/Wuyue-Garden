#!/usr/bin/env python3
"""Execute MyCodeProjects restructuring plan."""

import os, datetime, json, shutil, re

BASE = "E:/MyCodeProjects"
OBSIDIAN = "E:/Obsidian"
LOG = []
TS = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")
    LOG.append(f"[{TS}] {msg}")

def save_log():
    with open(f"{BASE}/_claude_log_{TS}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))

# =============== PHASE 1: Restructure MyCodeProjects ===============
log("=== PHASE 1: Restructure MyCodeProjects ===")

# 1a: Rename numbered dirs to Chinese names
renames = {
    "01-Rules_Engine":  "01-规则引擎",
    "02-Audit_Tools":   "02-审计工具",
    "03-Production":    "03-生产素材",
    "04-Case_FanJie":   "04-凡姐案例",
    "05-Case_XiaoTao":  "05-小桃案例",
    "06-Archive":       "06-存档中心",
}

for old, new in renames.items():
    oldp = os.path.join(BASE, old)
    newp = os.path.join(BASE, new)
    if os.path.isdir(oldp) and not os.path.exists(newp):
        os.rename(oldp, newp)
        log(f"RENAME: {old} -> {new}")
    elif os.path.isdir(oldp) and os.path.exists(newp):
        log(f"SKIP: {new} already exists, {old} remains")
    else:
        log(f"SKIP: {old} does not exist")

# 1b: Delete empty 04-Audit_Reports (if still exists)
audit_reports = os.path.join(BASE, "04-Audit_Reports")
if os.path.isdir(audit_reports):
    contents = os.listdir(audit_reports)
    if not contents:
        os.rmdir(audit_reports)
        log(f"DELETE: empty 04-Audit_Reports")
    else:
        log(f"SKIP: 04-Audit_Reports has {len(contents)} items, manual check needed")

# 1c: Handle 05-SubProjects -> move to archive
subproj = os.path.join(BASE, "05-SubProjects")
archive = os.path.join(BASE, "06-存档中心")
if os.path.isdir(subproj):
    items = os.listdir(subproj)
    for item in items:
        src = os.path.join(subproj, item)
        dst = os.path.join(archive, item)
        if os.path.exists(dst):
            dst = os.path.join(archive, f"{item}_moved_{TS}")
        shutil.move(src, dst)
        log(f"MOVE: {src} -> {dst}")
    try:
        os.rmdir(subproj)
        log(f"DELETE: empty 05-SubProjects (moved to archive)")
    except:
        log(f"WARN: could not remove 05-SubProjects")

# 1d: Move root .py/.ps1/.jsonl files into appropriate dirs
# Classify files
tool_dir = os.path.join(BASE, "02-审计工具")
production_dir = os.path.join(BASE, "03-生产素材")
fanjie_dir = os.path.join(BASE, "04-凡姐案例")
xiaotao_dir = os.path.join(BASE, "05-小桃案例")
archive_dir = os.path.join(BASE, "06-存档中心")

# Files to move to 02-审计工具
tool_files = [
    "monitor_engine.py", "monitor_桃.py", "monitor_live.py", "monitor_view.py",
    "start_audit.py", "live_observer.py", "realtime_analyser.py",
    "analyze_cleanup.py", "analyze_e_drive.py", "analyze_report.py", "analyze_stream.py",
    "test_coords.py", "generate_audit_report.py", "generate_ui_overlay.py",
    "find_obsidian_api_key.py", "deep_cleanup.py",
    "cleanup_360.ps1", "run_cleanup_elevated.ps1",
]

# Files to move to 04-凡姐案例 (fanjie-related)
fanjie_files = [
    "live_data_fanjie.jsonl", "triage_log_fanjie.jsonl",
]

# Files to move to 05-小桃案例
xiaotao_files = [
    "live_data.jsonl", "live_data_tao.jsonl", "triage_log.jsonl",
]

# Other root files -> 生产素材 or archive
other_plan = {
    "CLAUDE.md": (production_dir, None),
    "Index.md": (production_dir, None),
    "COO_Rules.md": (production_dir, None),
    "instructions.md": (production_dir, None),
    "E_cleanup_plan.md": (archive_dir, None),
    "E_drive_analysis.md": (archive_dir, None),
    ".mcp.json": (production_dir, None),
}

for fname in tool_files:
    src = os.path.join(BASE, fname)
    dst = os.path.join(tool_dir, fname)
    if os.path.isfile(src):
        if os.path.exists(dst):
            dst = os.path.join(tool_dir, f"{os.path.splitext(fname)[0]}_old_{TS}{os.path.splitext(fname)[1]}")
        shutil.move(src, dst)
        log(f"MOVE: {fname} -> 02-审计工具/")

for fname in fanjie_files:
    src = os.path.join(BASE, fname)
    dst = os.path.join(fanjie_dir, fname)
    if os.path.isfile(src):
        if os.path.exists(dst):
            dst = os.path.join(fanjie_dir, f"{os.path.splitext(fname)[0]}_old_{TS}{os.path.splitext(fname)[1]}")
        shutil.move(src, dst)
        log(f"MOVE: {fname} -> 04-凡姐案例/")

for fname in xiaotao_files:
    src = os.path.join(BASE, fname)
    dst = os.path.join(xiaotao_dir, fname)
    if os.path.isfile(src):
        if os.path.exists(dst):
            dst = os.path.join(xiaotao_dir, f"{os.path.splitext(fname)[0]}_old_{TS}{os.path.splitext(fname)[1]}")
        shutil.move(src, dst)
        log(f"MOVE: {fname} -> 05-小桃案例/")

for fname, (target_dir, subdir) in other_plan.items():
    src = os.path.join(BASE, fname)
    dst_dir = os.path.join(target_dir, subdir) if subdir else target_dir
    dst = os.path.join(dst_dir, fname)
    if os.path.isfile(src):
        os.makedirs(dst_dir, exist_ok=True)
        if os.path.exists(dst):
            dst = os.path.join(dst_dir, f"{os.path.splitext(fname)[0]}_old_{TS}{os.path.splitext(fname)[1]}")
        shutil.move(src, dst)
        log(f"MOVE: {fname} -> {os.path.basename(target_dir)}/")

# 1e: Move logs/ and temp_frames/ to archive
for dirname in ["logs", "temp_frames"]:
    src = os.path.join(BASE, dirname)
    dst = os.path.join(archive_dir, dirname)
    if os.path.isdir(src):
        if os.path.exists(dst):
            dst = os.path.join(archive_dir, f"{dirname}_old_{TS}")
        shutil.move(src, dst)
        log(f"MOVE: {dirname}/ -> 06-存档中心/")

# 1f: Remove __pycache__
pycache = os.path.join(BASE, "__pycache__")
if os.path.isdir(pycache):
    shutil.rmtree(pycache, ignore_errors=True)
    log(f"DELETE: __pycache__/")

log("=== PHASE 1 COMPLETE ===")
log("")

# =============== PHASE 2: Import project files from Obsidian vault ===============
log("=== PHASE 2: Import from Obsidian Vault ===")

# 2a: Move code files from vault 01-Production to 03-生产素材
vault_prod = os.path.join(OBSIDIAN, "01-Production")
if os.path.isdir(vault_prod):
    for root, dirs, files in os.walk(vault_prod):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, vault_prod)
            dst = os.path.join(production_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst):
                bak = dst + f".bak_{TS}"
                os.rename(dst, bak)
                log(f"BACKUP: existing {rel} -> {bak}")
            shutil.move(src, dst)
            log(f"MOVE: vault/01-Production/{rel} -> 03-生产素材/")

    # Remove empty dirs
    for root, dirs, files in os.walk(vault_prod, topdown=False):
        if root == vault_prod:
            continue
        try:
            os.rmdir(root)
        except:
            pass
    try:
        os.rmdir(vault_prod)
        log(f"DELETE: vault/01-Production/ (empty after move)")
    except:
        log(f"WARN: vault/01-Production/ not empty, leaving dir")

# 2b: Move Michael_Product notes to MyCodeProjects as docs
vault_michael = os.path.join(OBSIDIAN, "Michael_Product")
michael_docs_dir = os.path.join(production_dir, "规则甄查系统", "docs", "vault_notes")
if os.path.isdir(vault_michael):
    for root, dirs, files in os.walk(vault_michael):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, vault_michael)
            # Flatten structure, prefix with original dir path for context
            flat_name = rel.replace(os.sep, "__")
            dst = os.path.join(michael_docs_dir, flat_name)
            os.makedirs(michael_docs_dir, exist_ok=True)
            if os.path.exists(dst):
                dst = os.path.join(michael_docs_dir, f"{os.path.splitext(flat_name)[0]}_old_{TS}{os.path.splitext(flat_name)[1]}")
            shutil.move(src, dst)
            log(f"MOVE: vault/Michael_Product/{rel} -> 03-生产素材/docs/vault_notes/")

    for root, dirs, files in os.walk(vault_michael, topdown=False):
        if root == vault_michael:
            continue
        try:
            os.rmdir(root)
        except:
            pass
    try:
        os.rmdir(vault_michael)
        log(f"DELETE: vault/Michael_Product/ (empty after move)")
    except:
        log(f"WARN: vault/Michael_Product/ not empty, leaving dir")

log("=== PHASE 2 COMPLETE ===")
log("")

# =============== PHASE 3: Fix links in MyCodeProjects ===============
log("=== PHASE 3: Fix internal links ===")

# Update .md files referencing old paths
for root, dirs, files in os.walk(BASE):
    if '.git' in root.split(os.sep): continue
    if os.path.basename(root) == '__pycache__': continue
    for f in files:
        if f.endswith('.md'):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                new_content = content
                # Replace old dir names in links
                replacements = {
                    '01-Rules_Engine': '01-规则引擎',
                    '02-Audit_Tools': '02-审计工具',
                    '03-Production': '03-生产素材',
                    '04-Case_FanJie': '04-凡姐案例',
                    '04-Audit_Reports': '04-凡姐案例',
                    '05-Case_XiaoTao': '05-小桃案例',
                    '05-SubProjects': '06-存档中心',
                    '06-Archive': '06-存档中心',
                    'Audit_Assets': '01-规则引擎',
                }
                for old_name, new_name in replacements.items():
                    # Match in links [[...]], markdown links (...), and paths
                    new_content = new_content.replace(old_name, new_name)

                if new_content != content:
                    with open(fp, 'w', encoding='utf-8') as fh:
                        fh.write(new_content)
                    log(f"FIX LINKS: {os.path.relpath(fp, BASE)}")
            except Exception as e:
                log(f"ERROR reading {fp}: {e}")

log("=== PHASE 3 COMPLETE ===")
log("")

save_log()
print(f"\nDONE. Log saved to _claude_log_{TS}.txt")
