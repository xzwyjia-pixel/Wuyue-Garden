#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 中心调度器
========================================
职能：
  - 加载 config.yaml 为全局配置
  - 提供统一 CLI 入口（子命令模式）
  - Windows 计划任务注册/卸载/查询
  - 每日凌晨全流程触发

用法：
  python orchestrator.py full          # 执行全流程
  python orchestrator.py schedule      # 注册 Windows 计划任务
  python orchestrator.py unschedule    # 卸载计划任务
  python orchestrator.py status        # 查询计划任务状态
  python orchestrator.py config        # 查看/校验当前配置
  python orchestrator.py web           # 生成 status.html（Obsidian 控制台）
  python orchestrator.py accounts      # 查看/初始化矩阵账号分发目录
"""

import json
import subprocess
import sys
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

# ── 路径 ──
_BASE_DIR = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _BASE_DIR / "config.yaml"
_DATA_DIR = _BASE_DIR / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── 全局缓存 ──
_CFG: Dict[str, Any] = {}


def load_config() -> Dict[str, Any]:
    """加载 config.yaml（带缓存）"""
    global _CFG
    if _CFG:
        return _CFG
    if _CONFIG_PATH.exists():
        _CFG = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
    else:
        print(f"[WARN] {_CONFIG_PATH} 不存在，使用默认配置")
        _CFG = _default_config()
        save_config()
    return _CFG


def save_config():
    """写回 config.yaml"""
    _CONFIG_PATH.write_text(
        yaml.dump(_CFG, allow_unicode=True, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def _default_config() -> Dict[str, Any]:
    return {
        "api": {
            "deepseek_key": "sk-cad1b7bcd5dd4644a03c87c14a1fa690",
            "deepseek_url": "https://api.deepseek.com/v1/chat/completions",
            "deepseek_model": "deepseek-chat",
        },
        "paths": {
            "data_dir": str(_DATA_DIR),
            "notes_dir": str(_BASE_DIR / "notes"),
            "rules_path": str(_BASE_DIR / "rules.json"),
            "refine_path": str(_BASE_DIR / "ai_refine_pro.py"),
            "sentinel_cache": str(_DATA_DIR / "sentinel_cache.db"),
            "pipeline_state": str(_DATA_DIR / "pipeline_state.json"),
            "pending_sync": str(_DATA_DIR / "pending_sync"),
        },
        "thresholds": {
            "engagement_drop": 0.30,
            "refine_max_rounds": 3,
            "sentinel_timeout_ms": 30000,
        },
        "vision": {
            "frame_interval": 30,
            "qr_detect": True,
            "text_detect": True,
            "logo_detect": True,
            "cover_title_check": True,
        },
        "scheduler": {
            "daily_time": "02:00",
            "task_name": "规则甄查每日全流程",
        },
        "google_drive": {
            "credentials_path": str(_DATA_DIR / "gdrive_credentials.json"),
            "token_path": str(_DATA_DIR / "gdrive_token.json"),
            "root_folder": "Sentinel_Audit",
        },
        "webhook": {
            "enabled": False,
            "type": "generic",
            "url": "",
            "title": "规则甄查 · 流水线报告",
        },
        "feedback_collector": {
            "enabled": False,
            "login_url": "",
            "username": "",
            "password": "",
            "data_url": "",
        },
        "accounts": [
            {"id": "main", "label": "主账号", "strategy": "standard", "export_subdir": "main", "enabled": True},
            {"id": "sub_01", "label": "子账号A", "strategy": "aggressive", "export_subdir": "sub_01", "enabled": False},
        ],
        "trend": {
            "keywords": ["知识分享", "职场", "创业", "理财", "AI", "科技"],
            "max_per_keyword": 5,
            "enabled": False,
        },
    }


# ── 子命令：全流程 ──

def cmd_full():
    """全流程：sentinel → evolver → refine → obsidian → export → vision → gdrive"""
    scripts = [
        ("platform_sentinel", ["platform_sentinel.py"], False),
        ("rules_evolver", ["rules_evolver.py"], False),
        ("final_agent_run", ["final_agent_run.py", "--skip-sentinel"], True),
    ]

    print("=" * 52)
    print(f"  规则甄查 · 全流程  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 52)

    for name, args, critical in scripts:
        print(f"\n--- [{name}] ---")
        cfg = load_config()
        result = subprocess.run(
            [sys.executable] + args,
            cwd=_BASE_DIR,
            capture_output=False,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"[FAIL] {name}")
            if critical:
                print("[STOP] 关键步骤失败，流水线终止")
                sys.exit(1)
        else:
            print(f"[OK] {name}")

    print("\n[DONE] 全流程完成")


# ── 子命令：计划任务 ──

def _powershell(cmd: str) -> str:
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        capture_output=True, text=True, timeout=30,
    )
    return result.stdout.strip()


def cmd_schedule():
    cfg = load_config()
    task_name = cfg["scheduler"]["task_name"]
    daily_time = cfg["scheduler"]["daily_time"]
    python_path = sys.executable
    script_path = _BASE_DIR / "orchestrator.py"

    ps_script = f'''
$action = New-ScheduledTaskAction -Execute "{python_path}" -Argument "`"{script_path}`" full"
$trigger = New-ScheduledTaskTrigger -Daily -At "{daily_time}"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -Force
'''
    out = _powershell(ps_script)
    print(f"[SCHEDULE] 任务 '{task_name}' @ {daily_time}")
    print(f"  {out}" if out else "  OK")
    # 验证
    cmd_status()


def cmd_unschedule():
    cfg = load_config()
    task_name = cfg["scheduler"]["task_name"]
    out = _powershell(f'Unregister-ScheduledTask -TaskName "{task_name}" -Confirm:$false')
    print(f"[UNSCHEDULE] 任务 '{task_name}' 已删除")
    if out:
        print(f"  {out}")


def cmd_status():
    cfg = load_config()
    task_name = cfg["scheduler"]["task_name"]
    out = _powershell(f'Get-ScheduledTask -TaskName "{task_name}" | Format-List TaskName,State,Triggers')
    if "TaskName" in out:
        print(f"[STATUS] 计划任务状态:")
        for line in out.split("\n"):
            line = line.strip()
            if line:
                print(f"  {line}")
    else:
        print(f"[STATUS] 任务 '{task_name}' 未注册")


# ── 子命令：配置查看 ──

def cmd_config():
    cfg = load_config()
    print("=" * 52)
    print("  规则甄查 · 中心配置")
    print("=" * 52)
    for section, values in cfg.items():
        print(f"\n[{section}]")
        for k, v in values.items():
            val = str(v)
            if "key" in k.lower() and v:
                val = v[:8] + "..." + v[-4:] if len(v) > 16 else "****"
            print(f"  {k}: {val}")
    print(f"\n文件: {_CONFIG_PATH}")


# ── 子命令：账号管理 ──

def cmd_accounts():
    """显示多账号配置并创建分发目录"""
    cfg = load_config()
    accounts = cfg.get("accounts", [])

    if not accounts:
        print("[ACCOUNTS] 无账号配置")
        return

    print("=" * 52)
    print("  规则甄查 · 矩阵账号")
    print("=" * 52)

    for acct in accounts:
        aid = acct.get("id", "?")
        label = acct.get("label", "?")
        strategy = acct.get("strategy", "standard")
        enabled = acct.get("enabled", False)
        subdir = acct.get("export_subdir", aid)

        status = "✅ 启用" if enabled else "⏸️ 停用"
        export_path = _DATA_DIR / "export" / subdir

        print(f"\n  [{aid}] {label}  {status}")
        print(f"  策略: {strategy}")
        print(f"  导出: {export_path}")

        # 创建分发目录
        if enabled:
            export_path.mkdir(parents=True, exist_ok=True)
            print(f"  [MKDIR] 分发目录已就绪")

    print(f"\n共 {len(accounts)} 个账号")
    print("[HINT] 编辑 config.yaml 的 accounts 段新增/修改账号")


# ── 子命令：Web 控制台 ──

def _build_timeline() -> str:
    """从备份文件构建规则进化时间线 HTML"""
    entries = []

    # 当前规则
    try:
        rules = json.loads((_BASE_DIR / "rules.json").read_text(encoding="utf-8"))
        v = rules.get("version", "?")
        ts = rules.get("trend_collected_at") or rules.get("cleaned_at", "")
        label = "current" if not ts else ""
        if ts:
            d = ts[:10] if "T" in ts else ts
            entries.append((v, d, "当前版本", True))
        else:
            entries.append((v, "", "当前版本", True))
    except Exception:
        pass

    # 备份文件
    for f in sorted(_DATA_DIR.glob("rules_backup_*.json"), reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            v = data.get("version", "?")
            ts = data.get("cleaned_at", "")
            d = ts[:10] if ts else f.stem.split("_")[-1][:8]
            label = f.stem
            entries.append((v, d, label, False))
        except Exception:
            continue

    entries.sort(key=lambda x: x[0])  # 按版本升序

    if not entries:
        return "<p>暂无版本记录</p>"

    lines = ""
    for v, d, label, is_current in entries:
        cls = "current" if is_current else ""
        dot_color = "#e94560" if is_current else "#4fc3f7"
        lines += (
            f'<div class="tl-item {cls}">'
            f'<div class="tl-dot" style="background:{dot_color}"></div>'
            f'<div class="tl-content">'
            f'<span class="tl-version">v{v}</span> '
            f'<span class="tl-date">{d}</span>'
            f'<span class="tl-label">{" · " + label if not is_current else ""}</span>'
            f'</div></div>'
        )
    return lines


def _build_word_cloud() -> str:
    """从 trend_collection 数据生成词云 HTML"""
    state_path = _DATA_DIR / "pipeline_state.json"
    trend = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        trend = state.get("trend_collection", {})

    incentives = trend.get("incentives", [])
    if not incentives:
        return '<p style="color:#666;font-size:0.85em;">暂无趋势数据 · 运行 trend_collector.py 采集</p>'

    # 按 domain 分组计数
    domain_counts = Counter()
    cat_colors = {"GREEN_HIGH": "#2eb886", "GREEN_MEDIUM": "#4fc3f7", "GREEN_LOW": "#ffa726"}
    for inc in incentives:
        domain_counts[inc.get("domain", "?")] += 1

    max_count = max(domain_counts.values()) if domain_counts else 1
    min_size = 12
    max_size = 36

    tags = ""
    for domain, count in domain_counts.most_common():
        # 取该 domain 的主色
        domain_incentives = [i for i in incentives if i.get("domain") == domain]
        cat = domain_incentives[0].get("category", "GREEN_MEDIUM") if domain_incentives else "GREEN_MEDIUM"
        color = cat_colors.get(cat, "#4fc3f7")

        size = min_size + (count / max_count) * (max_size - min_size)
        tags += (
            f'<span class="cloud-word" style="font-size:{size:.0f}px;'
            f'color:{color};opacity:{0.5 + 0.5 * count / max_count:.2f};">'
            f'{domain}</span> '
        )

    return tags if tags else '<p style="color:#666;">暂无</p>'


def _build_golden_quote(state: dict) -> str:
    """从 deep_insight 提取今日金句"""
    di = state.get("deep_insight", {})
    pi = di.get("platform_intent", {})
    ci = di.get("counter_intuitive", [])

    quotes = []

    title = pi.get("title", "")
    if title:
        # 浓缩金句
        short = title.replace("平台意图：", "").replace("核心逻辑：", "")
        quotes.append(("平台意图", short))

    detail = pi.get("detail", "")
    if len(detail) > 20:
        # 取第一句或最有金句感的片段
        for sentence in detail.replace("。", "。\n").split("\n"):
            s = sentence.strip()
            if len(s) > 10 and len(s) < 100 and any(kw in s for kw in ["核心", "本质", "关键", "不是", "而是", "最终"]):
                quotes.append(("甄先生·洞察", s))
                break

    if ci:
        ci_item = ci[0]
        quotes.append(("反直觉·警示", f"{ci_item.get('scenario', '')} — {ci_item.get('action', '')}"))

    if not quotes:
        return '<p style="color:#666;font-size:0.85em;">暂无金句 · 运行全流程后生成</p>'

    cards = ""
    for i, (tag, text) in enumerate(quotes[:3]):
        border_colors = ["#e94560", "#2eb886", "#4fc3f7"]
        cards += (
            f'<div class="quote-card" style="border-left:3px solid {border_colors[i % 3]};">'
            f'<span class="quote-tag">{tag}</span>'
            f'<p class="quote-text">{text}</p>'
            f'</div>'
        )
    return cards


def _build_posting_directions(state: dict) -> str:
    """从 trend_collection + user_pains 提取建议发帖方向"""
    trend = state.get("trend_collection", {})
    domains = trend.get("domains", {})
    incentives = trend.get("incentives", [])
    di = state.get("deep_insight", {})
    ci = di.get("counter_intuitive", [])

    pain_path = _DATA_DIR / "user_pains.json"
    pains = []
    if pain_path.exists():
        pains = json.loads(pain_path.read_text(encoding="utf-8")).get("pains", [])

    if not domains and not pains:
        return '<p style="color:#666;font-size:0.85em;">暂无数据 · 运行 trend_collector.py + vocal_listener.py 后更新</p>'

    lines = ""

    # 按领域 + 痛点密度排序
    domain_pain_count = {}
    source_weights = Counter()
    for p in pains:
        src = p.get("source", "其他")
        source_weights[src] += p.get("score", 1)
        domain_pain_count.setdefault(src, []).append(p.get("text", ""))

    sorted_domains = sorted(
        domains.items(),
        key=lambda x: source_weights.get(x[0], 0) + x[1],
        reverse=True,
    )

    for domain, count in sorted_domains[:5]:
        pain_texts = domain_pain_count.get(domain, [])[:2]
        pain_hint = ""
        if pain_texts:
            pain_hint = (
                f'<span class="direction-pain">'
                f'用户高频问: {" | ".join(pain_texts)}'
                f'</span>'
            )
        # 匹配该 domain 的激励点
        domain_inc = [i for i in incentives if i.get("domain") == domain]
        inc_hint = ""
        if domain_inc:
            scenarios = set(i.get("scenario", "") for i in domain_inc[:2])
            inc_hint = (
                f'<span class="direction-inc">'
                f'推荐形式: {" | ".join(s for s in scenarios if s)}'
                f'</span>'
            )

        source_score = source_weights.get(domain, 0)
        urgency = "high" if source_score >= 5 else ("med" if source_score >= 2 else "low")
        lines += (
            f'<div class="direction-item urgency-{urgency}">'
            f'<strong>{domain}</strong> '
            f'<span class="direction-meta">热度 {count} · 痛点密度 {source_score:.0f}</span>'
            f'{pain_hint}'
            f'{inc_hint}'
            f'</div>'
        )

    if ci:
        lines += (
            f'<div class="direction-item urgency-high">'
            f'<strong>⚠️ 边界预警</strong>'
            f'<span class="direction-meta">基于反直觉案例</span>'
            f'<span class="direction-pain">{ci[0].get("scenario", "")}</span>'
            f'<span class="direction-inc">建议: {ci[0].get("action", "")}</span>'
            f'</div>'
        )

    return lines


def cmd_web():
    """生成 status.html 到 notes/ 供 Obsidian 预览"""
    _NOTES_DIR = _BASE_DIR / "notes"
    _NOTES_DIR.mkdir(parents=True, exist_ok=True)

    state_path = _DATA_DIR / "pipeline_state.json"
    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    steps = state.get("steps", [])
    refine_results = state.get("refine_results", [])
    vision = state.get("vision_audit", {})
    gdrive = state.get("gdrive_sync", {})
    passed = sum(1 for r in refine_results if r.get("verified_safe"))
    total_cases = len(refine_results)
    status = state.get("status", "none")
    duration = sum(s.get("duration_s", 0) for s in steps)

    # 步骤 HTML
    step_rows = ""
    for s in steps:
        ok = s["status"] == "ok"
        color = "#2eb886" if ok else "#e01e5a"
        icon = "●" if ok else "○"
        step_rows += (
            f"<tr><td>{s['step']}</td>"
            f"<td>{s['name']}</td>"
            f"<td style='color:{color}'>{icon} {s['status']}</td>"
            f"<td>{s['duration_s']}s</td></tr>"
        )

    # 视觉发现
    vision_lines = ""
    for sev in ("HIGH", "MEDIUM", "LOW"):
        c = vision.get("severity_summary", {}).get(sev, 0)
        if c:
            vision_lines += f"<li>{sev}: {c}</li>"

    # 规则统计
    rule_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    try:
        rules = json.loads((_BASE_DIR / "rules.json").read_text(encoding="utf-8"))
        for lv in ("HIGH", "MEDIUM", "LOW"):
            rule_counts[lv] = len(rules.get("risk_levels", {}).get(lv, {}).get("focus", {}))
    except Exception:
        pass

    # 时间线 + 词云
    timeline_html = _build_timeline()
    wordcloud_html = _build_word_cloud()

    # 今日金句 + 建议发帖方向
    golden_quote_html = _build_golden_quote(state)
    posting_directions_html = _build_posting_directions(state)

    # 激励点统计
    inc_counts = {"GREEN_HIGH": 0, "GREEN_MEDIUM": 0, "GREEN_LOW": 0}
    try:
        ips = rules.get("incentive_points", {})
        for k in inc_counts:
            inc_counts[k] = len(ips.get(k, {}).get("indicators", []))
    except Exception:
        pass

    # 待发布文案
    distill = state.get("matrix_distill", {})
    distill_files = distill.get("files", {})
    publish_flag = distill.get("publish_flag", False)
    distill_time = distill.get("distilled_at", "")[:16] if distill.get("distilled_at") else ""
    distill_summary = distill.get("summary", {})
    pending_count = 3 if distill_files else 0

    publish_html = ""
    if distill_files:
        for platform, fpath in distill_files.items():
            fname = Path(fpath).name
            platform_label = {"douyin": "抖音 · 规则情报局", "shipinhao": "视频号 · 规则甄查", "gongzhonghao": "公众号 · 规则甄查"}
            label = platform_label.get(platform, platform)
            try:
                content = Path(fpath).read_text(encoding="utf-8")
            except Exception:
                content = "文件不可读"
            # escape for JS string
            escaped = content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
            publish_html += f"""
<div class="publish-card">
  <strong>{label}</strong>
  <span class="meta">{fname} | {distill_time}</span>
  <div class="copy-area" id="copy-area-{platform}">{content}</div>
  <button class="copy-btn" onclick="copyContent('{platform}')">复制到 Obsidian</button>
</div>"""
    else:
        publish_html = "<p style='color:#666;font-size:0.85em;'>暂无待发布文案 · 运行 matrix_distiller.py 生成</p>"

    # 最近报告链接
    report_links = ""
    for f in sorted(_NOTES_DIR.glob("*规则演变报告*.md"), reverse=True)[:5]:
        name = f.stem
        report_links += f"<li><a href='{f.name}'>{name}</a></li>"

    # 导出文件
    export_links = ""
    for f in sorted(_DATA_DIR.glob("export_*.*"), reverse=True)[:5]:
        rel = f"../data/{f.name}"
        export_links += f"<li><a href='{rel}'>{f.name}</a></li>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>规则甄查 · 系统状态</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,'微软雅黑',sans-serif; background:#1a1a2e; color:#e0e0e0; padding:24px; }}
  h1 {{ font-size:1.5em; color:#e94560; margin-bottom:4px; }}
  .sub {{ color:#888; font-size:0.85em; margin-bottom:24px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:12px; margin-bottom:24px; }}
  .card {{ background:#16213e; border-radius:8px; padding:16px; }}
  .card .num {{ font-size:1.8em; font-weight:700; }}
  .card .label {{ font-size:0.8em; color:#888; margin-top:4px; }}
  table {{ width:100%; border-collapse:collapse; margin-bottom:24px; }}
  th,td {{ padding:8px 12px; text-align:left; border-bottom:1px solid #333; font-size:0.9em; }}
  th {{ color:#e94560; font-weight:600; }}
  a {{ color:#4fc3f7; text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  .ok {{ color:#2eb886; }}
  .fail {{ color:#e01e5a; }}
  ul {{ list-style:none; }}
  li {{ padding:4px 0; font-size:0.9em; }}
  .section {{ margin-bottom:24px; }}
  .section h2 {{ color:#e94560; font-size:1.1em; margin-bottom:8px; border-bottom:1px solid #333; padding-bottom:4px; }}
  /* 时间线 */
  .timeline {{ position:relative; padding-left:24px; border-left:2px solid #333; }}
  .tl-item {{ position:relative; padding:8px 0 8px 16px; }}
  .tl-dot {{ position:absolute; left:-7px; top:12px; width:10px; height:10px; border-radius:50%; }}
  .tl-item.current .tl-dot {{ box-shadow:0 0 8px #e94560; }}
  .tl-version {{ font-weight:700; color:#e94560; }}
  .tl-date {{ color:#888; font-size:0.85em; margin-left:8px; }}
  .tl-label {{ color:#666; font-size:0.8em; }}
  /* 词云 */
  .wordcloud {{ line-height:2.2; padding:8px 0; }}
  .cloud-word {{ display:inline-block; padding:4px 6px; cursor:default; transition:transform 0.2s; }}
  .cloud-word:hover {{ transform:scale(1.15); }}
  /* 待发布文案 */
  .copy-area {{ background:#0d1b2a; border:1px solid #333; border-radius:6px; padding:12px; font-family:'Consolas','Courier New',monospace; font-size:0.85em; white-space:pre-wrap; word-break:break-all; max-height:400px; overflow-y:auto; margin-bottom:8px; }}
  .copy-btn {{ background:#e94560; color:#fff; border:none; border-radius:4px; padding:6px 16px; cursor:pointer; font-size:0.85em; }}
  .copy-btn:hover {{ background:#c0392b; }}
  .copy-btn.ok {{ background:#2eb886; }}
  .publish-card {{ background:#16213e; border-left:3px solid #e94560; padding:12px; margin-bottom:8px; border-radius:0 6px 6px 0; }}
  .publish-card .meta {{ color:#888; font-size:0.8em; }}
  /* 今日金句 */
  .quote-card {{ background:#16213e; padding:14px 16px; margin-bottom:10px; border-radius:0 8px 8px 0; }}
  .quote-tag {{ display:inline-block; font-size:0.7em; color:#888; letter-spacing:1px; margin-bottom:6px; }}
  .quote-text {{ margin:0; font-size:0.95em; line-height:1.6; color:#e0e0e0; }}
  /* 建议发帖方向 */
  .direction-item {{ background:#16213e; padding:12px; margin-bottom:8px; border-radius:8px; }}
  .direction-item.urgency-high {{ border-left:3px solid #e94560; }}
  .direction-item.urgency-med {{ border-left:3px solid #ffa726; }}
  .direction-item.urgency-low {{ border-left:3px solid #4fc3f7; }}
  .direction-meta {{ font-size:0.75em; color:#888; margin-left:8px; }}
  .direction-pain {{ display:block; font-size:0.8em; color:#ffa726; margin-top:4px; }}
  .direction-inc {{ display:block; font-size:0.8em; color:#2eb886; margin-top:2px; }}
</style></head><body>
<h1>⚡ 规则甄查 · 甄先生 v2.0</h1>
<p class="sub">流水线状态 · {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

<div class="grid">
  <div class="card"><div class="num {'ok' if status=='completed' else 'fail'}">{status}</div><div class="label">流水线状态</div></div>
  <div class="card"><div class="num">{total_cases}</div><div class="label">处理文案</div></div>
  <div class="card"><div class="num">{passed}</div><div class="label">零风险通过</div></div>
  <div class="card"><div class="num">{rule_counts['HIGH']}</div><div class="label">高风险词</div></div>
  <div class="card"><div class="num">{duration}s</div><div class="label">总耗时</div></div>
  <div class="card"><div class="num">{vision.get('total_findings',0)}</div><div class="label">视觉发现</div></div>
  <div class="card"><div class="num">{pending_count}</div><div class="label">待发布文案</div></div>
</div>

<div class="section">
<h2>步骤明细</h2>
<table><tr><th>步骤</th><th>名称</th><th>状态</th><th>耗时</th></tr>{step_rows}</table>
</div>

<div class="section">
<h2>规则库</h2>
<table><tr><th>等级</th><th>数量</th></tr>
<tr><td>HIGH · 封号风险</td><td>{rule_counts['HIGH']}</td></tr>
<tr><td>MEDIUM · 限流风险</td><td>{rule_counts['MEDIUM']}</td></tr>
<tr><td>LOW · 优化建议</td><td>{rule_counts['LOW']}</td></tr>
</table>
</div>

<div class="section">
<h2>规则进化路径</h2>
<div class="timeline">{timeline_html}</div>
</div>

<div class="section">
<h2>近 7 日趋势词云</h2>
<div class="wordcloud">{wordcloud_html}</div>
</div>

<div class="section">
<h2>激励点总览</h2>
<table><tr><th>等级</th><th>数量</th></tr>
<tr><td>GREEN_HIGH · 长效价值</td><td>{inc_counts['GREEN_HIGH']}</td></tr>
<tr><td>GREEN_MEDIUM · 实证原创</td><td>{inc_counts['GREEN_MEDIUM']}</td></tr>
<tr><td>GREEN_LOW · 合规创新</td><td>{inc_counts['GREEN_LOW']}</td></tr>
</table>
</div>

<div class="section">
<h2>今日金句</h2>
{golden_quote_html}
</div>

<div class="section">
<h2>建议发帖方向</h2>
{posting_directions_html}
</div>

<div class="section">
<h2>视觉审计</h2>
<ul>{"".join(vision_lines) if vision_lines else "<li>暂无数据</li>"}</ul>
<p style="font-size:0.85em;color:#888;margin-top:4px;">帧数: {vision.get('frames_analyzed',0)} | 类型: {', '.join(f'{k}:{v}' for k,v in vision.get('type_summary',{}).items()) if vision.get('type_summary') else '—'}</p>
</div>

<div class="section">
<h2>云端同步</h2>
<p>状态: {gdrive.get('status','none')} | 文件: {gdrive.get('files_uploaded',0)}/{gdrive.get('files_total',0)}</p>
</div>

<div class="section">
<h2>最近报告</h2>
<ul>{report_links if report_links else '<li>暂无</li>'}</ul>
</div>

<div class="section">
<h2>导出素材</h2>
<ul>{export_links if export_links else '<li>暂无</li>'}</ul>
</div>

<div class="section">
<h2>待发布文案 ({pending_count})</h2>
{publish_html}
</div>

<p class="sub" style="margin-top:32px;">由 orchestrator.py web 命令自动生成 · 刷新页面更新</p>
<script>
function copyContent(id) {{
  var area = document.getElementById('copy-area-' + id);
  if (!area) return;
  var text = area.textContent || area.innerText;
  navigator.clipboard.writeText(text).then(function() {{
    var btn = document.querySelector('button[onclick="copyContent(\'' + id + '\')"]');
    if (btn) {{ btn.textContent = '已复制 ✓'; btn.classList.add('ok'); }}
  }}).catch(function() {{
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    var btn = document.querySelector('button[onclick="copyContent(\'' + id + '\')"]');
    if (btn) {{ btn.textContent = '已复制 ✓'; btn.classList.add('ok'); }}
  }});
}}
</script>
</body></html>"""

    path = _NOTES_DIR / "status.html"
    path.write_text(html, encoding="utf-8")
    print(f"[WEB] {path}")
    print(f"[DONE] 在 Obsidian 中预览: notes/status.html")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    commands = {
        "full": cmd_full,
        "schedule": cmd_schedule,
        "unschedule": cmd_unschedule,
        "status": cmd_status,
        "config": cmd_config,
        "web": cmd_web,
        "accounts": cmd_accounts,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"[FAIL] 未知命令: {command}")
        print("可用命令: full, schedule, unschedule, status, config")
        sys.exit(1)


if __name__ == "__main__":
    main()
