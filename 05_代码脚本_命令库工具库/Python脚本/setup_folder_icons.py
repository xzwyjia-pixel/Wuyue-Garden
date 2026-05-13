#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化文件夹图标设置脚本
功能：下载图标、生成 desktop.ini、执行 attrib 命令激活图标
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
from PIL import Image
from io import BytesIO

# 强制 stdout/stderr 使用 UTF-8，避免 Windows GBK 终端 Emoji 报错
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─── 配置区 ────────────────────────────────────────────────────────────────────

ICONS_DIR = Path("E:/Icons")

# 五个目标文件夹及对应图标配置
FOLDER_CONFIGS = [
    {
        "folder": Path("E:/高考规划分析"),
        "icon_name": "education.ico",
        "keywords": "education/exam",
        "urls": [
            "https://img.icons8.com/color/96/graduation-cap.png",
            "https://img.icons8.com/fluency/96/graduation-cap.png",
            "https://img.icons8.com/color/96/student-center.png",
        ],
    },
    {
        "folder": Path("E:/蒙AE270L"),
        "icon_name": "car.ico",
        "keywords": "car",
        "urls": [
            "https://img.icons8.com/color/96/car.png",
            "https://img.icons8.com/fluency/96/car.png",
            "https://img.icons8.com/color/96/sedan.png",
        ],
    },
    {
        "folder": Path("E:/MyCodeProjects"),
        "icon_name": "coding.ico",
        "keywords": "coding",
        "urls": [
            "https://img.icons8.com/color/96/source-code.png",
            "https://img.icons8.com/fluency/96/source-code.png",
            "https://img.icons8.com/color/96/code.png",
        ],
    },
    {
        "folder": Path("E:/MiniMax Hub Data"),
        "icon_name": "ai.ico",
        "keywords": "artificial intelligence",
        "urls": [
            "https://img.icons8.com/color/96/artificial-intelligence.png",
            "https://img.icons8.com/fluency/96/artificial-intelligence.png",
            "https://img.icons8.com/color/96/robot-2.png",
        ],
    },
    {
        "folder": Path("E:/Obsidian"),
        "icon_name": "notebook.ico",
        "keywords": "notebook",
        "urls": [
            "https://img.icons8.com/color/96/notebook.png",
            "https://img.icons8.com/fluency/96/notebook.png",
            "https://img.icons8.com/color/96/note-pad.png",
        ],
    },
]

# ─── 工具函数 ──────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def print_step(msg: str):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")

def print_ok(msg: str):
    print(f"  ✔  {msg}")

def print_warn(msg: str):
    print(f"  ⚠  {msg}")

def print_err(msg: str):
    print(f"  ✘  {msg}")


# ─── Step 1: 创建 E:/Icons 目录 ────────────────────────────────────────────────

def step_create_icons_dir():
    print_step("Step 1 — 创建 E:/Icons 图标目录")
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    print_ok(f"目录已就绪：{ICONS_DIR}")


# ─── Step 2: 下载 PNG 并转换为 ICO ────────────────────────────────────────────

def download_png_to_ico(urls: list, ico_path: Path, icon_name: str) -> bool:
    """尝试每个 URL，成功下载 PNG 后转换为多尺寸 ICO。"""
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("image"):
                img = Image.open(BytesIO(resp.content)).convert("RGBA")
                # 生成 16/32/48/64/128/256 多尺寸 ICO
                sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
                img_256 = img.resize((256, 256), Image.LANCZOS)
                icons = []
                for s in sizes:
                    icons.append(img_256.resize(s, Image.LANCZOS))
                icons[0].save(
                    ico_path,
                    format="ICO",
                    sizes=sizes,
                    append_images=icons[1:],
                )
                print_ok(f"{icon_name} ← 下载成功 ({url.split('/')[4]})")
                return True
            else:
                print_warn(f"  HTTP {resp.status_code}，尝试下一个 URL …")
        except Exception as e:
            print_warn(f"  请求失败 ({e.__class__.__name__})，尝试下一个 URL …")
    return False


def generate_fallback_ico(ico_path: Path, color: tuple, label: str):
    """网络全部失败时，用 Pillow 绘制带颜色的占位图标。"""
    from PIL import ImageDraw, ImageFont
    sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
    base = Image.new("RGBA", (256, 256), color + (255,))
    draw = ImageDraw.Draw(base)
    # 画圆形背景
    draw.ellipse([8, 8, 248, 248], fill=color+(255,), outline=(255,255,255,200), width=6)
    # 写首字母
    ch = label[0].upper()
    # 尝试用系统字体，失败则用默认字体
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 120)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), ch, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((256-tw)//2, (256-th)//2 - 10), ch, fill=(255,255,255,255), font=font)
    icons = [base.resize(s, Image.LANCZOS) for s in sizes]
    icons[0].save(ico_path, format="ICO", sizes=sizes, append_images=icons[1:])
    print_warn(f"{ico_path.name} ← 网络下载失败，已生成颜色占位图标")


FALLBACK_COLORS = [
    (41, 128, 185),   # 蓝色  education
    (231, 76, 60),    # 红色  car
    (39, 174, 96),    # 绿色  coding
    (142, 68, 173),   # 紫色  AI
    (243, 156, 18),   # 橙色  notebook
]


def step_download_icons():
    print_step("Step 2 — 下载/生成 .ico 图标文件")
    results = []
    for idx, cfg in enumerate(FOLDER_CONFIGS):
        ico_path = ICONS_DIR / cfg["icon_name"]
        success = download_png_to_ico(cfg["urls"], ico_path, cfg["icon_name"])
        if not success:
            generate_fallback_ico(ico_path, FALLBACK_COLORS[idx], cfg["icon_name"])
        results.append((cfg["icon_name"], ico_path, success))
    return results


# ─── Step 3: 生成 desktop.ini ─────────────────────────────────────────────────

DESKTOP_INI_TEMPLATE = """\
[.ShellClassInfo]
IconResource={icon_path},0
IconIndex=0
[ViewState]
Mode=
Vid=
FolderType=Generic
"""

def step_generate_desktop_ini():
    print_step("Step 3 — 生成各文件夹 desktop.ini")
    for cfg in FOLDER_CONFIGS:
        folder: Path = cfg["folder"]
        ico_path = ICONS_DIR / cfg["icon_name"]
        ini_path = folder / "desktop.ini"

        # 确保目标文件夹存在
        folder.mkdir(parents=True, exist_ok=True)

        # 写入 desktop.ini（Windows 路径，反斜杠）
        content = DESKTOP_INI_TEMPLATE.format(
            icon_path=str(ico_path).replace("/", "\\")
        )
        ini_path.write_text(content, encoding="utf-8")
        print_ok(f"{folder.name}/desktop.ini → {ico_path}")


# ─── Step 4: attrib 命令激活图标 ───────────────────────────────────────────────

def run_cmd(cmd: str) -> tuple:
    """运行 shell 命令，返回 (returncode, stdout+stderr)。"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, encoding="gbk", errors="replace"
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def step_apply_attrib():
    print_step("Step 4 — 执行 attrib 命令激活图标显示")
    for cfg in FOLDER_CONFIGS:
        folder: Path = cfg["folder"]
        ini_path = folder / "desktop.ini"
        folder_str = str(folder).replace("/", "\\")
        ini_str = str(ini_path).replace("/", "\\")

        # desktop.ini → 系统+隐藏
        rc1, out1 = run_cmd(f'attrib +s +h "{ini_str}"')
        # 文件夹本身 → 只读（触发 Windows 读取 desktop.ini）
        rc2, out2 = run_cmd(f'attrib +r "{folder_str}"')

        status = "✔" if (rc1 == 0 and rc2 == 0) else "⚠"
        print(f"  {status}  {folder.name}")
        if out1: print(f"       ini: {out1}")
        if out2: print(f"       dir: {out2}")


# ─── Step 5: 汇总报告 ─────────────────────────────────────────────────────────

def step_report(icon_results):
    print_step("✅ 执行完毕 — 汇总报告")
    print(f"\n  图标存储目录：{ICONS_DIR}\n")
    for cfg, (name, path, ok) in zip(FOLDER_CONFIGS, icon_results):
        folder = cfg["folder"]
        status = "网络下载" if ok else "本地生成(占位)"
        print(f"  {'✔' if ok else '~'}  {folder.name}")
        print(f"       图标：{path}  [{status}]")
        print(f"       INI ：{folder / 'desktop.ini'}")
        print()
    print("  💡 提示：若图标未立即刷新，请在资源管理器中按 F5")
    print("          或注销重新登录 Windows 以强制刷新 Shell 缓存。\n")


# ─── 主入口 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🚀 自动化文件夹图标设置脚本 启动")
    print(f"   Python {sys.version.split()[0]}  |  Pillow {Image.__version__}")

    step_create_icons_dir()
    icon_results = step_download_icons()
    step_generate_desktop_ini()
    step_apply_attrib()
    step_report(icon_results)
