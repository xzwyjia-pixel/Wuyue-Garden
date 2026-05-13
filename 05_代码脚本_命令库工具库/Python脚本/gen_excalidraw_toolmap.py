#!/usr/bin/env python3
"""生成 Claude 工具全家桶全景导航 Excalidraw 图"""

import json, time, random

# ── helpers ──
_ele_id = [0]; _seed_ctr = [random.randint(100000, 999999)]
def eid(): _ele_id[0] += 1; return f"e{_ele_id[0]:04d}"
def seed(): _seed_ctr[0] += 1; return _seed_ctr[0]

FONT_TITLE = 24; FONT_H = 18; FONT_M = 14; FONT_S = 12; FONT_XS = 11

def text(txt, x, y, w=200, h=28, **kw):
    s = seed()
    return {
        "id": eid(), "type": "text", "x": x, "y": y,
        "width": w, "height": h, "angle": 0,
        "strokeColor": kw.get("color", "#1e1e1e"),
        "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": 1, "strokeStyle": "solid", "roughness": 1,
        "opacity": kw.get("opacity", 100), "groupIds": [],
        "roundness": None, "seed": s, "version": 1, "versionNonce": s,
        "isDeleted": False, "boundElements": None,
        "updated": int(time.time()*1000), "link": None, "locked": False,
        "text": txt, "fontSize": kw.get("fs", FONT_M),
        "fontFamily": kw.get("ff", 2),
        "textAlign": kw.get("align", "left"),
        "verticalAlign": kw.get("valign", "top"),
        "baseline": h-4, "containerId": None, "originalText": txt,
        "autoResize": True, "lineHeight": 1.25
    }

def rect(x, y, w, h, **kw):
    s = seed()
    return {
        "id": eid(), "type": "rectangle", "x": x, "y": y,
        "width": w, "height": h, "angle": 0,
        "strokeColor": kw.get("stroke", "#1971c2"),
        "backgroundColor": kw.get("bg", "#e7f5ff"),
        "fillStyle": kw.get("fill", "solid"),
        "strokeWidth": kw.get("sw", 2), "strokeStyle": "solid",
        "roughness": kw.get("rough", 1), "opacity": 100,
        "groupIds": [], "roundness": {"type": 3},
        "seed": s, "version": 1, "versionNonce": s,
        "isDeleted": False, "boundElements": [],
        "updated": int(time.time()*1000), "link": None, "locked": False
    }

def arrow(x1, y1, x2, y2, **kw):
    s = seed()
    return {
        "id": eid(), "type": "arrow", "x": x1, "y": y1,
        "width": x2-x1, "height": y2-y1, "angle": 0,
        "strokeColor": kw.get("stroke", "#1971c2"),
        "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": kw.get("sw", 2), "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [],
        "roundness": {"type": 2},
        "seed": s, "version": 1, "versionNonce": s,
        "isDeleted": False, "boundElements": None,
        "updated": int(time.time()*1000), "link": None, "locked": False,
        "points": [[0,0],[x2-x1,y2-y1]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": kw.get("endArrow", "arrow"),
        "elbowed": False
    }

def make_scene(els):
    return {
        "type": "excalidraw", "version": 2,
        "source": "https://excalidraw.com",
        "elements": els,
        "appState": {
            "gridSize": None, "viewBackgroundColor": "#f8f9fa",
            "zenModeEnabled": False, "viewModeEnabled": False,
            "pasteDialog": {"shown": False, "data": None},
            "theme": "light", "currentChartType": None
        }, "files": {}
    }


# ── Layout constants ──
CX = 60               # canvas left margin
CW = 2280             # canvas content width (2400-60-60)
GAP = 40              # gap between columns
COL = (CW - GAP*2)//3 # 733 px per column
C1X = CX; C2X = CX + COL + GAP; C3X = C2X + COL + GAP

# Colors per zone
CAVE_S, CAVE_BG = "#1971c2", "#e7f5ff"     # blue
SUPER_S, SUPER_BG = "#2f9e44", "#ebfbee"   # green
BAOYU_S, BAOYU_BG = "#9c36b5", "#f8f0fc"  # purple
GSD_S, GSD_BG = "#e8590c", "#fff4e6"       # orange
TOOL_S, TOOL_BG = "#c92a2a", "#fff5f5"     # red
NEUTRAL_S, NEUTRAL_BG = "#495057", "#f1f3f5"

# ── Build elements ──
els = []

# ════════════════════════════════════════════
# TITLE + LEGEND
# ════════════════════════════════════════════

els.append(text("🤖 Claude 工具全家桶 · 全景导航图", CX, 25, fs=32, color="#1c1c1c"))
els.append(text("一份地图看懂所有 tool/agent/skill 的定位、关系、优劣", CX, 65, fs=14, color="#868e96"))

# Legend bar
leg_y = 100
els.append(rect(CX, leg_y, CW, 36, stroke="#adb5bd", bg="#ffffff", sw=1, rough=0))
legend_items = [
    (C1X+20, "🗣️ Caveman 沟通压缩"), (C1X+COL//2, "⚡ Superpowers 方法论"),
    (C2X+20, "🎨 Baoyu 内容创作"), (C2X+COL//2, "🏗️ GSD 项目骨架"),
    (C3X+20, "🛠️ 专项工具"), (C3X+COL//2, "💡 比喻说明")
]
for lx, lt in legend_items:
    els.append(text(lt, lx, leg_y+5, fs=13, color="#495057"))


# ════════════════════════════════════════════
# ROW 1: CAVEMAN | SUPERPOWERS | BAOYU
# ════════════════════════════════════════════
R1Y = 165; R1H = 560
# Container backgrounds
els.append(rect(C1X, R1Y, COL, R1H, stroke=CAVE_S, bg=CAVE_BG, sw=2))
els.append(rect(C2X, R1Y, COL, R1H, stroke=SUPER_S, bg=SUPER_BG, sw=2))
els.append(rect(C3X, R1Y, COL, R1H, stroke=BAOYU_S, bg=BAOYU_BG, sw=2))

INNER = 12  # inner padding

# ── CAVEMAN ZONE ──
cx, cy = C1X + INNER, R1Y + INNER
els.append(text("🗣️ Caveman", cx, cy, fs=FONT_TITLE, color=CAVE_S))
els.append(text("沟通压缩模式", cx, cy+28, fs=FONT_H, color=CAVE_S))
els.append(text("💡 比喻：短信 vs 书信 — 砍掉废话，保留干货", cx, cy+55, fs=FONT_S, color="#495057"))
els.append(text("每句话都像电报：省 token ~70%，长对话持久", cx, cy+75, fs=FONT_S, color="#495057"))

# Intensity cards
card_w = (COL - INNER*2 - 8) // 3 - 8
card_y = cy + 100
intensities = [
    ("lite", "轻度压缩", CAVE_S, "#d0ebff"),
    ("full", "标准压缩 🏆", CAVE_S, "#a5d8ff"),
    ("ultra", "极限压缩", CAVE_S, "#74c0fc"),
]
for i, (name, desc, sc, bg) in enumerate(intensities):
    ix = cx + i * (card_w + 8)
    els.append(rect(ix, card_y, card_w, 50, stroke=sc, bg=bg, sw=1))
    els.append(text(name, ix+6, card_y+5, fs=FONT_M, color=sc))
    els.append(text(desc, ix+6, card_y+27, fs=FONT_XS, color="#495057"))

# Sub-agents
sub_y = card_y + 65
els.append(text("子 Agent (cavecrew)：", cx, sub_y, fs=FONT_S, color=CAVE_S, ff=3))
agent_info = [
    ("🔍 investigator", "只读探索 · 定位代码位置", CX+INNER),
    ("🔧 builder", "精准 1-2 文件编辑", C2X+INNER),
    ("👁️ reviewer", "压缩版 code review", C3X+INNER),
]
# Adjust because sub-agents span differently - let me put them inline
agent_y = sub_y + 22
for i, (name, desc, ax) in enumerate(agent_info):
    a_w = COL - INNER*2
    ay = agent_y + i * 42
    els.append(rect(ax, ay, a_w, 36, stroke=CAVE_S, bg="#ffffff", sw=1))
    els.append(text(f"{name}  —  {desc}", ax+8, ay+8, fs=FONT_XS, color="#495057"))

# Utility commands
util_y = agent_y + 135
els.append(text("实用指令：/caveman-stats(查省量) /caveman-help(速查) /caveman:compress(压缩记忆文件)", cx, util_y, fs=FONT_XS, color="#868e96"))

# Pros/Cons
pc_y = util_y + 25
pad = 8
pc_w = COL - INNER*2 - pad*2
els.append(rect(cx+pad, pc_y, pc_w, 50, stroke="#2b8a3e", bg="#ebfbee", sw=1))
els.append(text(f"✅ token节省~75% · 对话存活更久 · 聚焦核心", cx+pad+6, pc_y+6, fs=FONT_XS, color="#2b8a3e"))
els.append(rect(cx+pad, pc_y+54, pc_w, 36, stroke="#c92a2a", bg="#fff5f5", sw=1))
els.append(text(f"❌ 太生硬 · 不适合对外沟通 · 安全警告需切回正常", cx+pad+6, pc_y+60, fs=FONT_XS, color="#c92a2a"))


# ── SUPERPOWERS ZONE ──
cx, cy = C2X + INNER, R1Y + INNER
els.append(text("⚡ Superpowers", cx, cy, fs=FONT_TITLE, color=SUPER_S))
els.append(text("工作方法论", cx, cy+28, fs=FONT_H, color=SUPER_S))
els.append(text("💡 比喻：老师傅操作手册 — 什么时候做什么事", cx, cy+55, fs=FONT_S, color="#495057"))

# Method cards - 2x3 grid
sp_card_w = (COL - INNER*2 - 8) // 2 - 4
sp_card_h = 80
sp_gap = 10
sp_start_y = cy + 100
methods = [
    ("💡 brainstorming", "创意需求探索\n明确用户意图与范围", SUPER_S, "#d3f9d8"),
    ("📐 writing-plans", "多步骤任务计划\n执行前先设计路径", SUPER_S, "#d3f9d8"),
    ("🔴 tdd", "测试驱动开发\n先写测试再编码", SUPER_S, "#b2f2bb"),
    ("🔍 systematic-debugging", "科学排查bug\n假设置→验证→修复", SUPER_S, "#b2f2bb"),
    ("✅ verification-before-completion", "完成前必须验证\n杜绝拍胸脯保证", SUPER_S, "#8ce99a"),
    ("👥 dispatching-parallel-agents", "并行任务分发\n独立工作同时推进", SUPER_S, "#d3f9d8"),
]
for i, (name, desc, sc, bg) in enumerate(methods):
    col_idx = i % 2
    row_idx = i // 2
    mx = cx + col_idx * (sp_card_w + sp_gap)
    my = sp_start_y + row_idx * (sp_card_h + sp_gap)
    els.append(rect(mx, my, sp_card_w, sp_card_h, stroke=sc, bg=bg, sw=1))
    els.append(text(name, mx+6, my+5, fs=FONT_S, color=sc))
    els.append(text(desc, mx+6, my+30, fs=FONT_XS, color="#495057"))

# Extra methods row
extras = ["git-worktrees(隔离)", "code-review(审查)", "executing-plans(执行)"]
extra_y = sp_start_y + 3*(sp_card_h+sp_gap) + 5
els.append(text("其他：", cx, extra_y, fs=FONT_XS, color=SUPER_S))
for i, ex in enumerate(extras):
    exx = cx + (i * 155)
    els.append(text(ex, exx, extra_y+16, fs=FONT_XS, color="#495057"))

# Pros/Cons
pc_y2 = extra_y + 42
els.append(rect(cx+pad, pc_y2, pc_w, 50, stroke="#2b8a3e", bg="#ebfbee", sw=1))
els.append(text(f"✅ 流程严谨 · 避免冲动编码 · 质量门禁", cx+pad+6, pc_y2+6, fs=FONT_XS, color="#2b8a3e"))
els.append(rect(cx+pad, pc_y2+54, pc_w, 36, stroke="#c92a2a", bg="#fff5f5", sw=1))
els.append(text(f"❌ 小改动也走全套流程 · 有时overkill", cx+pad+6, pc_y2+60, fs=FONT_XS, color="#c92a2a"))


# ── BAOYU ZONE ──
cx, cy = C3X + INNER, R1Y + INNER
els.append(text("🎨 Baoyu 宝榆", cx, cy, fs=FONT_TITLE, color=BAOYU_S))
els.append(text("内容创作套件", cx, cy+28, fs=FONT_H, color=BAOYU_S))
els.append(text("💡 比喻：全能内容工作室 — 拍照/写稿/发朋友圈", cx, cy+55, fs=FONT_S, color="#495057"))

# Group cards by function
groups = [
    ("🖼️ 图片", BAOYU_S, "#e5dbff",
     ["imagine (AI生图)", "cover-image (封面)", "image-cards (小红书)", "slide-deck (PPT)", "infographic (信息图)"]),
    ("📝 文本", BAOYU_S, "#d0bfff",
     ["translate (翻译精翻)", "edit-article (编辑)", "format-markdown (排版)", "markdown-to-html (转HTML)"]),
    ("📤 发布", BAOYU_S, "#b197fc",
     ["post-to-wechat (公众号)", "post-to-weibo (微博)", "post-to-x (Twitter)"]),
    ("🔧 工具", BAOYU_S, "#9775fa",
     ["url-to-markdown (网页剪藏)", "youtube-transcript (字幕)", "diagram (画架构图)"]),
]
group_h = 40
group_y_start = cy + 85
for gi, (gname, sc, bg, items) in enumerate(groups):
    gy = group_y_start + gi * (group_h + 2)
    els.append(rect(cx, gy, COL - INNER*2, 36 + len(items)*18, stroke=sc, bg=bg, sw=1))
    els.append(text(gname, cx+8, gy+6, fs=FONT_M, color="#1c1c1c"))
    for j, item in enumerate(items):
        els.append(text(f"  · {item}", cx+8, gy+28 + j*18, fs=FONT_XS, color="#495057"))

# Pros/Cons
pc_y3 = group_y_start + 4*(group_h+2) + 10
els.append(rect(cx+pad, pc_y3, pc_w, 50, stroke="#2b8a3e", bg="#ebfbee", sw=1))
els.append(text(f"✅ 全链路覆盖 · 从零到发布一站搞定 · 品牌统一", cx+pad+6, pc_y3+6, fs=FONT_XS, color="#2b8a3e"))
els.append(rect(cx+pad, pc_y3+54, pc_w, 36, stroke="#c92a2a", bg="#fff5f5", sw=1))
els.append(text(f"❌ 依赖外部API · 效果取决于prompt质量", cx+pad+6, pc_y3+60, fs=FONT_XS, color="#c92a2a"))


# ════════════════════════════════════════════
# ROW 2: GSD — full width
# ════════════════════════════════════════════
R2Y = 760; R2H = 580
els.append(rect(CX, R2Y, CW, R2H, stroke=GSD_S, bg=GSD_BG, sw=3))
cx, cy = CX + INNER, R2Y + INNER
els.append(text("🏗️ GSD 项目管理系统  (核心枢纽)", cx, cy, fs=FONT_TITLE+2, color=GSD_S))
els.append(text("💡 比喻：建筑公司工程管理系统 — 从打地基到竣工验收", cx, cy+32, fs=FONT_S, color="#495057"))
els.append(text("纵向：全生命周期管理 · 横向：可并行也可串行 · 贯穿：Superpowers提供方法 + Baoyu提供内容", cx, cy+52, fs=FONT_S, color="#6c757d"))

# 4 phase groups: 规划 → 执行 → 质量 → 管理
phases = [
    ("📋 规划", "#e8590c", "#ffd8a8",
     ["discuss-phase", "plan-phase", "research-phase", "brainstorm"]),
    ("⚙️ 执行", "#d9480f", "#ffc078",
     ["execute-phase", "fast", "quick", "iterate"]),
    ("✅ 质量", "#c92a2a", "#ffa8a8",
     ["review-code", "verify-work", "audit-milestone", "validate-phase"]),
    ("📊 管控", "#4263eb", "#bac8ff",
     ["manager", "progress", "health", "stats"]),
]

phase_w = (CW - INNER*2 - 24) // 4  # 4 columns with 8px gap
phase_h = 260
phase_y = cy + 80
arrow_y = phase_y + phase_h // 2

for i, (pname, sc, bg, items) in enumerate(phases):
    px = cx + i * (phase_w + 8)
    els.append(rect(px, phase_y, phase_w, phase_h, stroke=sc, bg=bg, sw=2))
    els.append(text(pname, px+10, phase_y+8, fs=FONT_H, color=sc))
    for j, item in enumerate(items):
        iy = phase_y + 38 + j * 24
        els.append(rect(px+8, iy, phase_w-16, 20, stroke=sc, bg="#ffffff", sw=1))
        els.append(text(item, px+12, iy+2, fs=FONT_XS, color="#1c1c1c", ff=3))

    # Arrow between phases
    if i < len(phases) - 1:
        ax = px + phase_w
        els.append(arrow(ax, arrow_y, ax + 8, arrow_y, stroke=GSD_S, sw=2))

# Arrow labels
els.append(text("→ 顺序迭代", C2X, phase_y-8, fs=FONT_XS, color=GSD_S))
els.append(text("π 可并行", C2X+100, phase_y-8, fs=FONT_XS, color=GSD_S))

# Quick action cards
q_y = phase_y + phase_h + 15
els.append(text("快捷操作：", cx, q_y, fs=FONT_M, color=GSD_S))
quick_actions = ["/gsd:next", "/gsd:fast", "/gsd:quick", "/gsd:progress", "/gsd:help", "/gsd:stats"]
for i, qa in enumerate(quick_actions):
    qx = cx + 100 + i * 170
    els.append(rect(qx, q_y-2, 155, 22, stroke="#adb5bd", bg="#ffffff", sw=1))
    els.append(text(qa, qx+6, q_y+1, fs=FONT_XS, color=GSD_S, ff=3))

# Pros/Cons
pc_y4 = q_y + 40
p_w = 500
els.append(rect(cx, pc_y4, p_w, 60, stroke="#2b8a3e", bg="#ebfbee", sw=1))
els.append(text(f"✅ 全流程覆盖 · 可追溯 · 大项目救星 · 状态不丢失", cx+8, pc_y4+6, fs=FONT_XS, color="#2b8a3e"))
els.append(rect(cx+p_w+10, pc_y4, p_w, 60, stroke="#c92a2a", bg="#fff5f5", sw=1))
els.append(text(f"❌ 小项目太重 · 学习成本高 · 指令太多要记", cx+p_w+18, pc_y4+6, fs=FONT_XS, color="#c92a2a"))


# ════════════════════════════════════════════
# ROW 3: 专项工具
# ════════════════════════════════════════════
R3Y = 1375; R3H = 280
els.append(rect(CX, R3Y, CW, R3H, stroke=TOOL_S, bg=TOOL_BG, sw=2))
cx, cy = CX + INNER, R3Y + INNER
els.append(text("🛠️ 专项工具  (瑞士军刀)", cx, cy, fs=FONT_TITLE, color=TOOL_S))
els.append(text("💡 比喻：瑞士军刀 — 每个工具解决一个特定问题", cx, cy+30, fs=FONT_S, color="#495057"))

specialized = [
    ("review", "PR 代码审查", TOOL_S, "#ffd8d8"),
    ("triage", "问题分类/转派", TOOL_S, "#ffc9c9"),
    ("simplify", "代码简化优化", TOOL_S, "#ffb3b3"),
    ("diagnose", "bug 诊断排查", TOOL_S, "#ffa8a8"),
    ("init", "初始化 CLAUDE.md", TOOL_S, "#ff8787"),
    ("claude-api", "API 开发助手", TOOL_S, "#ff6b6b"),
    ("update-config", "Settings 配置", TOOL_S, "#ffa8a8"),
    ("security-review", "安全审查", TOOL_S, "#ff8787"),
    ("improve-arch", "架构改进", TOOL_S, "#ff6b6b"),
    ("frontend-design", "UI 界面设计", TOOL_S, "#ffc9c9"),
]

tool_w = (CW - INNER*2 - 90) // 10  # 10 tools per row
tool_gap = 10
tool_y = cy + 60
for i, (tname, tdesc, sc, bg) in enumerate(specialized):
    tx = cx + i * (tool_w + tool_gap)
    els.append(rect(tx, tool_y, tool_w, 55, stroke=sc, bg=bg, sw=1))
    els.append(text(tname, tx+4, tool_y+4, fs=FONT_S, color=sc, ff=3))
    els.append(text(tdesc, tx+4, tool_y+26, fs=10, color="#495057"))

# Pros/Cons
pc_y5 = tool_y + 70
els.append(rect(cx, pc_y5, p_w, 36, stroke="#2b8a3e", bg="#ebfbee", sw=1))
els.append(text(f"✅ 即插即用 · 精准解决特定问题", cx+8, pc_y5+8, fs=FONT_XS, color="#2b8a3e"))
els.append(rect(cx+p_w+10, pc_y5, p_w, 36, stroke="#c92a2a", bg="#fff5f5", sw=1))
els.append(text(f"❌ 功能边界有限 · 复杂场景需组合使用", cx+p_w+18, pc_y5+8, fs=FONT_XS, color="#c92a2a"))


# ════════════════════════════════════════════
# CROSS-ZONE RELATIONSHIP ARROWS
# ════════════════════════════════════════════

# Superpowers → GSD (methodology flows into GSD)
# From bottom of Superpowers zone to top-right of GSD
sp_bottom = R1Y + R1H
gsd_top = R2Y
els.append(arrow(C2X + COL//2, sp_bottom, C2X + COL//2, gsd_top,
                 stroke=SUPER_S, sw=2))
els.append(text("方法论输入\n提供流程规范", C2X + COL//2 + 10, (sp_bottom + gsd_top)//2 - 18,
                 fs=10, color=SUPER_S))

# GSD → Baoyu (GSD calls Baoyu for content)
# From bottom-right of GSD to Baoyu
gsd_bottom = R2Y + R2H
baoyu_bottom = R1Y + R1H
els.append(arrow(C3X + COL//2, baoyu_bottom, C3X + COL//2, gsd_top,
                 stroke=BAOYU_S, sw=2, endArrow="arrow"))
els.append(text("内容输出\n被GSD流程调用", C3X + COL//2 + 10, (baoyu_bottom + gsd_top)//2 - 18,
                 fs=10, color=BAOYU_S))

# Caveman → All (label on the side)
els.append(text("← 🗣️ Caveman 贯穿所有对话 →", CX + CW//2 - 150, R3Y + R3H + 20,
                 fs=FONT_S, color=CAVE_S))

# GSD → 专项工具
els.append(arrow(CX + CW//2, gsd_bottom, CX + CW//2, R3Y,
                 stroke=GSD_S, sw=2))
els.append(text("流程中按需调用专项工具", CX + CW//2 + 10, (gsd_bottom + R3Y)//2 - 10,
                 fs=10, color=GSD_S))

# Legend for relationships
legend_y = R3Y + R3H + 60
els.append(rect(CX, legend_y, CW, 50, stroke="#adb5bd", bg="#ffffff", sw=1))
rels = [
    ("🏗️ GSD = 主骨架 (中心枢纽)", CAVE_S),
    ("⚡ Superpowers → 提供方法论给 GSD", SUPER_S),
    ("🎨 Baoyu → 内容创作供 GSD 调用", BAOYU_S),
    ("🗣️ Caveman → 沟通模式贯穿所有会话", TOOL_S),
]
for i, (rt, rc) in enumerate(rels):
    rx = CX + 20 + i * (CW // 4)
    els.append(text(rt, rx, legend_y+8, fs=FONT_S, color=rc))
    els.append(text("↕ 双向影响" if i < 3 else "↕ 无处不在", rx, legend_y+28, fs=FONT_XS, color="#868e96"))


# ── Write file ──
OUTPUT = "E:\\MyCodeProjects\\Claude工具全景导航图.excalidraw"
scene = make_scene(els)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(scene, f, ensure_ascii=False, indent=2)

print(f"[OK] Generated: {OUTPUT}")
print(f"     Elements: {len(els)}")
