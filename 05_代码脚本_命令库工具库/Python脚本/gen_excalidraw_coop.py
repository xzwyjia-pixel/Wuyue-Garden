#!/usr/bin/env python3
"""生成苏苏共创方案 Excalidraw 图，推送 Obsidian"""

import json, time, math, random

OBSIDIAN_API = "http://127.0.0.1:27123"
API_KEY = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
BASE_PATH = "知识库/宝妈直播诊断/"

# ── helpers ─────────────────────────────────────────────
_ele_id = [0]
def eid():
    _ele_id[0] += 1
    return f"ele_{_ele_id[0]:04d}"

_ver = [1]
seed_ctr = [random.randint(100000, 999999)]

def text_elem(text, x, y, w=200, h=28, **kw):
    sid = seed_ctr[0]; seed_ctr[0] += 1
    v = _ver[0]; _ver[0] += 1
    return {
        "id": eid(), "type": "text",
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0,
        "strokeColor": kw.get("color", "#1e1e1e"),
        "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100,
        "groupIds": [], "roundness": None,
        "seed": sid, "version": v, "versionNonce": sid,
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
        "text": text,
        "fontSize": kw.get("fontSize", 20),
        "fontFamily": kw.get("fontFamily", 1),
        "textAlign": "left", "verticalAlign": "top",
        "baseline": h - 4,
        "containerId": None, "originalText": text,
        "autoResize": True,
        "lineHeight": 1.25
    }

def rect_elem(x, y, w, h, **kw):
    sid = seed_ctr[0]; seed_ctr[0] += 1
    v = _ver[0]; _ver[0] += 1
    fill = kw.get("fillStyle", "solid")
    return {
        "id": eid(), "type": "rectangle",
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0,
        "strokeColor": kw.get("stroke", "#1971c2"),
        "backgroundColor": kw.get("bg", "#e7f5ff"),
        "fillStyle": fill, "strokeWidth": kw.get("strokeWidth", 2),
        "strokeStyle": "solid",
        "roughness": kw.get("roughness", 1),
        "opacity": 100,
        "groupIds": [], "roundness": {"type": 3},
        "seed": sid, "version": v, "versionNonce": sid,
        "isDeleted": False,
        "boundElements": [],
        "updated": int(time.time() * 1000),
        "link": None, "locked": False
    }

def arrow_elem(x1, y1, x2, y2, **kw):
    sid = seed_ctr[0]; seed_ctr[0] += 1
    v = _ver[0]; _ver[0] += 1
    return {
        "id": eid(), "type": "arrow",
        "x": x1, "y": y1,
        "width": x2 - x1, "height": y2 - y1,
        "angle": 0,
        "strokeColor": kw.get("stroke", "#1971c2"),
        "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": kw.get("strokeWidth", 2),
        "strokeStyle": "solid",
        "roughness": 1, "opacity": 100,
        "groupIds": [], "roundness": {"type": 2},
        "seed": sid, "version": v, "versionNonce": sid,
        "isDeleted": False,
        "boundElements": None,
        "updated": int(time.time() * 1000),
        "link": None, "locked": False,
        "points": [[0, 0], [x2 - x1, y2 - y1]],
        "lastCommittedPoint": None,
        "startBinding": None, "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "elbowed": False
    }

def make_scene(elements, title=""):
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": None,
            "viewBackgroundColor": "#ffffff",
            "zenModeEnabled": False,
            "zenMode": False,
            "viewModeEnabled": False,
            "pasteDialog": {"shown": False, "data": None},
            "theme": "light",
            "currentChartType": None
        },
        "files": {}
    }

def excalidraw_md(scene_json):
    text_elems = []
    for el in scene_json.get("elements", []):
        if el.get("type") == "text":
            text_elems.append(el["text"])
    text_block = "\n".join(f"- {t}" for t in text_elems)
    return f"""---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠ Switch to EXCALIDRAW VIEW for the most accurate rendering.==
%%
# Text Elements
{text_block}

# Drawing
```json
{json.dumps(scene_json, ensure_ascii=False, indent=2)}
```
%%"""
# ── 1. 三人共创角色架构图 ───────────────────────────

def diagram_roles():
    els = []
    # Title
    els.append(text_elem("🎯 三人共创角色架构图", 60, 40, fontSize=28, color="#e64980"))

    # 苏苏 box
    els.append(rect_elem(80, 120, 220, 140, bg="#fff3e0", stroke="#e65100", strokeWidth=3))
    els.append(text_elem("👩‍🍳 苏苏 (主厨+主讲)", 90, 130, fontSize=18, color="#e65100"))
    els.append(text_elem("• 灶台做菜 & 讲解\n• 出锅展示菜品\n• 核心内容输出者", 95, 165, fontSize=14, color="#424242"))

    # 苏苏 → 海燕 arrow
    els.append(arrow_elem(300, 170, 370, 170, stroke="#e65100"))
    els.append(text_elem("互动职责移交", 310, 150, fontSize=13, color="#e65100"))

    # 海燕 box
    els.append(rect_elem(380, 100, 220, 150, bg="#e3f2fd", stroke="#1565c0", strokeWidth=3))
    els.append(text_elem("🎤 海燕 (互动官)", 390, 110, fontSize=18, color="#1565c0"))
    els.append(text_elem("• 评论区互动 & 念评论\n• 每5分钟引导关注\n• 烹饪过程翻译解说\n• 持手机拍近景展示", 395, 145, fontSize=14, color="#424242"))

    # 苏苏 → 姐 arrow
    els.append(arrow_elem(300, 310, 370, 310, stroke="#e65100"))
    els.append(text_elem("品鉴职责移交", 310, 290, fontSize=13, color="#e65100"))

    # 姐 box
    els.append(rect_elem(380, 270, 220, 130, bg="#e8f5e9", stroke="#2e7d32", strokeWidth=3))
    els.append(text_elem("🍽️ 姐 (品鉴官)", 390, 280, fontSize=18, color="#2e7d32"))
    els.append(text_elem("• 每道菜出锅试吃评价\n• 观众视角提问\n• 制造家常话题", 395, 315, fontSize=14, color="#424242"))

    # Bottom legend
    bx = 80
    els.append(rect_elem(bx, 480, 700, 100, bg="#f5f5f5", stroke="#9e9e9e", strokeWidth=1))
    els.append(text_elem("💡 核心逻辑：不是增加工作量，而是重新分配", bx+15, 490, fontSize=16, color="#333"))
    els.append(text_elem("苏苏省下'看镜头'精力做好菜 → 海燕接管互动引导 → 姐制造品鉴话题", bx+15, 520, fontSize=14, color="#555"))
    els.append(text_elem("每个人做自己最擅长的事。调整前后：互动率 8/100 → 目标 60/100", bx+15, 545, fontSize=14, color="#c62828"))

    return make_scene(els)


# ── 2. 抖音共创引流流程图 ───────────────────────────

def diagram_flow():
    els = []
    els.append(text_elem("📲 抖音共创引流流程", 60, 40, fontSize=28, color="#e64980"))

    # Three account boxes (left)
    accounts = [
        ("👩‍🍳 苏苏在浙里", "主账号 · 直播发起", 80, 120, "#fff3e0", "#e65100"),
        ("🥬 海燕在浙里", "帮厨号 · 互动引流", 80, 270, "#e3f2fd", "#1565c0"),
        ("👭 姐的江南厨房", "姐妹号 · 氛围引流", 80, 420, "#e8f5e9", "#2e7d32"),
    ]
    for name, desc, x, y, bg, stroke in accounts:
        els.append(rect_elem(x, y, 200, 90, bg=bg, stroke=stroke, strokeWidth=2))
        els.append(text_elem(name, x+10, y+10, fontSize=17, color=stroke))
        els.append(text_elem(desc, x+10, y+45, fontSize=13, color="#555"))

    # Center arrow
    els.append(arrow_elem(280, 170, 350, 200, stroke="#e65100", strokeWidth=3))
    els.append(arrow_elem(280, 315, 350, 250, stroke="#1565c0", strokeWidth=3))
    els.append(arrow_elem(280, 465, 350, 300, stroke="#2e7d32", strokeWidth=3))

    # Center label
    els.append(text_elem("⬇ 共创视频发布 ⬇", 290, 340, fontSize=14, color="#555"))

    # Funnel / target
    els.append(rect_elem(380, 140, 280, 350, bg="#fce4ec", stroke="#c62828", strokeWidth=3, fillStyle="solid"))
    els.append(text_elem("🎯 苏苏直播间", 440, 160, fontSize=22, color="#c62828"))
    els.append(text_elem("三号粉丝汇聚一处", 430, 200, fontSize=14, color="#555"))
    els.append(text_elem("", 0, 0))

    # Benefits
    els.append(rect_elem(380, 240, 260, 40, bg="#fff", stroke="#c62828"))
    els.append(text_elem("✅ 苏苏粉丝看到", 390, 250, fontSize=13, color="#333"))
    els.append(rect_elem(380, 290, 260, 40, bg="#fff", stroke="#1565c0"))
    els.append(text_elem("✅ 海燕粉丝看到", 390, 300, fontSize=13, color="#333"))
    els.append(rect_elem(380, 340, 260, 40, bg="#fff", stroke="#2e7d32"))
    els.append(text_elem("✅ 姐的粉丝看到", 390, 350, fontSize=13, color="#333"))
    els.append(text_elem("一条视频 = 三号曝光", 400, 400, fontSize=16, color="#c62828"))

    # Right side — operation flow
    rx = 710
    els.append(rect_elem(rx, 120, 240, 380, bg="#f3e5f5", stroke="#7b1fa2", strokeWidth=1))
    els.append(text_elem("📋 操作流程", rx+15, 135, fontSize=18, color="#7b1fa2"))
    steps = [
        "① 苏苏号拍摄上传视频",
        "② 发布页点'添加共创'",
        "③ 添加海燕号 + 姐号",
        "④ 三号审核通过",
        "⑤ 视频同步展示三主页",
        "⑥ 评论区置顶直播入口",
        "",
        "🔥 抖加放大规则：",
        "点赞>500 或 播放>1w",
        "→ 投直播间人气",
        "→ 浙江+美食+25-45岁",
        "→ 每条100元/天×3天",
    ]
    for i, s in enumerate(steps):
        els.append(text_elem(s, rx+15, 170 + i*22, fontSize=12, color="#424242"))

    return make_scene(els)


# ── 3. 共创视频内容日历 ───────────────────────────

def diagram_calendar():
    els = []
    els.append(text_elem("📅 共创视频发布日历", 60, 40, fontSize=28, color="#e64980"))

    days = [
        ("Day 1", "注册改号", "海燕号/姐号改好\n各发2条热身视频", "#fff3e0", "#e65100"),
        ("Day 2", "预告视频 🎬", "三人同框直播预告\n晚7点发布", "#e3f2fd", "#1565c0"),
        ("Day 3", "备菜花絮", "海燕偷师苏苏做菜\n晚7点发布", "#e8f5e9", "#2e7d32"),
        ("Day 4", "直播日 🎯", "姐妹猜菜单(早9点)\n下午3点直播", "#fce4ec", "#c62828"),
        ("Day 5", "切片1", "海燕号发高光切片\n+共创苏苏，晚7点", "#f3e5f5", "#7b1fa2"),
        ("Day 6", "复盘选投", "复盘前几条数据\n选好的投抖加", "#e0f7fa", "#00838f"),
        ("Day 7", "切片2", "姐号发直播切片\n+共创苏苏，晚7点", "#fff8e1", "#f57f17"),
    ]

    start_x = 60
    start_y = 110
    box_w = 160
    box_h = 120
    gap = 15

    for i, (day, title, desc, bg, stroke) in enumerate(days):
        x = start_x + i * (box_w + gap)
        y = start_y

        els.append(rect_elem(x, y, box_w, box_h, bg=bg, stroke=stroke, strokeWidth=2))
        els.append(text_elem(f"{day}: {title}", x+8, y+8, fontSize=16, color=stroke))
        for j, line in enumerate(desc.split("\n")):
            els.append(text_elem(line, x+10, y+42 + j*20, fontSize=12, color="#424242"))

        # Arrow between days
        if i < len(days) - 1:
            ax = x + box_w
            ay = y + box_h // 2
            els.append(arrow_elem(ax, ay, ax + gap, ay, stroke="#bdbdbd", strokeWidth=1))

    # Bottom summary
    els.append(rect_elem(60, start_y + box_h + 40, 1200, 80, bg="#f5f5f5", stroke="#9e9e9e", strokeWidth=1))
    els.append(text_elem("💡 核心策略", 75, start_y + box_h + 50, fontSize=16, color="#333"))
    els.append(text_elem("三条账号各展人设 → 苏苏主厨 + 海燕帮厨 + 姐的姐妹情 → 通过共创视频把三波粉丝汇聚到苏苏直播间", 75, start_y + box_h + 75, fontSize=14, color="#555"))
    els.append(text_elem("视频号替代方案：海燕/姐转发苏苏视频到朋友圈+微信群（视频号权重极高），或 @苏苏在浙里", 75, start_y + box_h + 95, fontSize=13, color="#9e9e9e"))

    return make_scene(els)


# ── upload ───────────────────────────────────────────

import urllib.request, urllib.parse

def upload_to_obsidian(filename, md_content):
    path = urllib.parse.quote(f"{BASE_PATH}{filename}")
    url = f"{OBSIDIAN_API}/vault/{path}"
    data = json.dumps({"content": md_content}).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        method="PUT"
    )
    try:
        resp = urllib.request.urlopen(req)
        print(f"  ✅ {filename} — HTTP {resp.status}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ❌ {filename} — HTTP {e.code}: {e.read().decode()}")
        return False


# ── main ─────────────────────────────────────────────

if __name__ == "__main__":
    files = [
        ("共创_角色架构图.excalidraw.md", diagram_roles()),
        ("共创_引流流程图.excalidraw.md", diagram_flow()),
        ("共创_视频日历.excalidraw.md", diagram_calendar()),
    ]

    print("Generating Excalidraw files for Obsidian...")
    for name, scene in files:
        md = excalidraw_md(scene)
        # Also save locally for inspection
        local_path = f"E:\\MyCodeProjects\\{name}"
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  [OK] Saved local: {local_path}")
        upload_to_obsidian(name, md)

    print("\nDone! Open Obsidian -> Excalidraw view to see diagrams.")
