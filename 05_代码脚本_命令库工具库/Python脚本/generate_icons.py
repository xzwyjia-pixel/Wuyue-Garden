"""
generate_icons.py
=================
极简工业风图标生成器

功能：
  1. 调用 Recraft.ai 或 Stability AI 的 API 生成图标图片
  2. 自动用 Pillow 将图片转为 256x256 的 .ico 格式
  3. 存入 icons/ 文件夹，命名为 <keyword>.ico

用法：
  1. 在下方 CONFIG 区填入 API Key
  2. 修改 KEYWORDS 列表
  3. 运行：python generate_icons.py

依赖：
  pip install requests pillow
"""

import os
import sys
import io as _io

# 强制 UTF-8 输出，避免 Windows GBK 终端乱码
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests
from PIL import Image
import base64
import time

# ================================================================
#  CONFIG — 填入你的 API Key（两者填一个即可）
# ================================================================
RECRAFT_API_KEY    = "YOUR_RECRAFT_API_KEY"       # https://www.recraft.ai/
STABILITY_API_KEY  = "YOUR_STABILITY_API_KEY"     # https://platform.stability.ai/

# 优先使用哪个后端："recraft" 或 "stability"（会自动跳过未填写的）
PREFERRED_BACKEND  = "recraft"

# 图标输出目录
ICONS_DIR = "icons"

# 需要生成的图标关键词列表（可按需修改）
KEYWORDS = [
    "contract",    # 合同
    "travel",      # 旅行 / 游学
    "finance",     # 财务
    "code",        # 代码
    "music",       # 音乐
    "design",      # 设计
    "archive",     # 归档
    "photo",       # 照片
    "document",    # 文档
    "database",    # 数据
]

# Prompt 模板（{keyword} 会被替换）
PROMPT_TEMPLATE = (
    "A minimalist, precise, frosted glass folder icon for {keyword}, "
    "high-end industrial design, neutral grey and silver tones, "
    "isolated on white background, flat vector style."
)


# ================================================================
#  后端 1：Recraft.ai
#  文档：https://www.recraft.ai/docs
# ================================================================
def generate_with_recraft(keyword: str, prompt: str) -> bytes | None:
    """
    调用 Recraft.ai API 生成图片，返回 PNG 字节流；失败返回 None。
    Recraft 有专属 icon style，效果优于通用模型。
    """
    if not RECRAFT_API_KEY or RECRAFT_API_KEY == "YOUR_RECRAFT_API_KEY":
        print("  [跳过] Recraft API Key 未设置")
        return None

    url = "https://external.recraft.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {RECRAFT_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "n": 1,
        "style": "icon",            # Recraft 专属图标风格
        "size": "1024x1024",
        "response_format": "b64_json",
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            b64 = data["data"][0]["b64_json"]
            return base64.b64decode(b64)
        else:
            print(f"  [Recraft] 错误 {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  [Recraft] 异常: {e}")
        return None


# ================================================================
#  后端 2：Stability AI (SDXL)
#  文档：https://platform.stability.ai/docs/api-reference
# ================================================================
def generate_with_stability(keyword: str, prompt: str) -> bytes | None:
    """
    调用 Stability AI SDXL API 生成图片，返回 PNG 字节流；失败返回 None。
    """
    if not STABILITY_API_KEY or STABILITY_API_KEY == "YOUR_STABILITY_API_KEY":
        print("  [跳过] Stability AI API Key 未设置")
        return None

    url = (
        "https://api.stability.ai/v1/generation/"
        "stable-diffusion-xl-1024-v1-0/text-to-image"
    )
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "text_prompts": [
            {"text": prompt, "weight": 1.0},
            # 负向提示词：排除低质量、写实风格
            {"text": "photorealistic, blurry, noisy, complex background, 3D render", "weight": -1.0},
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
        "style_preset": "digital-art",
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            b64 = data["artifacts"][0]["base64"]
            return base64.b64decode(b64)
        else:
            print(f"  [Stability] 错误 {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  [Stability] 异常: {e}")
        return None


# ================================================================
#  图片 -> 256x256 .ico  (Pillow)
# ================================================================
def png_bytes_to_ico(png_bytes: bytes, output_path: str) -> bool:
    """
    将 PNG 字节流缩放至 256x256，保存为 .ico 文件。
    返回 True 表示成功。
    """
    try:
        img = Image.open(_io.BytesIO(png_bytes)).convert("RGBA")
        img = img.resize((256, 256), Image.LANCZOS)

        # ICO 格式支持多尺寸，这里同时嵌入 256 / 128 / 64 / 48 / 32 / 16
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        frames = []
        for s in sizes:
            frame = img.resize(s, Image.LANCZOS)
            frames.append(frame)

        frames[0].save(
            output_path,
            format="ICO",
            sizes=[(f.width, f.height) for f in frames],
            append_images=frames[1:],
        )
        return True
    except Exception as e:
        print(f"  [Pillow] 转换失败: {e}")
        return False


# ================================================================
#  主流程：批量生成图标
# ================================================================
def generate_icons(keywords: list[str], backend: str = PREFERRED_BACKEND):
    """
    对 keywords 列表中的每个关键词：
      1. 构造 Prompt
      2. 调用指定 API 后端生成图片
      3. 转换为 .ico 并保存到 ICONS_DIR
    """
    os.makedirs(ICONS_DIR, exist_ok=True)

    print("=" * 60)
    print("  极简工业风图标生成器")
    print(f"  后端: {backend.upper()}  |  输出目录: {ICONS_DIR}/")
    print(f"  待生成: {len(keywords)} 个关键词")
    print("=" * 60)

    success_list = []
    fail_list    = []

    for idx, kw in enumerate(keywords, start=1):
        ico_path = os.path.join(ICONS_DIR, f"{kw}.ico")

        # 若已存在则跳过（避免重复消耗 API 额度）
        if os.path.exists(ico_path):
            print(f"[{idx:02d}/{len(keywords):02d}] 已存在，跳过: {ico_path}")
            success_list.append(kw)
            continue

        prompt = PROMPT_TEMPLATE.format(keyword=kw)
        print(f"[{idx:02d}/{len(keywords):02d}] 生成中: {kw}")
        print(f"  Prompt: {prompt[:80]}...")

        # 选择后端
        png_bytes = None
        if backend == "recraft":
            png_bytes = generate_with_recraft(kw, prompt)
            if png_bytes is None:
                print("  Recraft 失败，尝试 Stability AI 备用...")
                png_bytes = generate_with_stability(kw, prompt)
        else:
            png_bytes = generate_with_stability(kw, prompt)
            if png_bytes is None:
                print("  Stability 失败，尝试 Recraft 备用...")
                png_bytes = generate_with_recraft(kw, prompt)

        if png_bytes is None:
            print(f"  [FAIL] 两个后端均失败，跳过: {kw}\n")
            fail_list.append(kw)
            continue

        # 转 .ico
        if png_bytes_to_ico(png_bytes, ico_path):
            file_kb = os.path.getsize(ico_path) / 1024
            print(f"  [OK] 已保存: {ico_path}  ({file_kb:.1f} KB)\n")
            success_list.append(kw)
        else:
            fail_list.append(kw)

        # 避免 API 限速（每次请求间隔 1 秒）
        time.sleep(1)

    # 汇总
    print("=" * 60)
    print(f"  完成！成功 {len(success_list)} 个 / 失败 {len(fail_list)} 个")
    if fail_list:
        print(f"  失败列表: {fail_list}")
    print("=" * 60)

    return success_list, fail_list


# ================================================================
#  命令行入口
# ================================================================
if __name__ == "__main__":
    # -------- 使用前请先填写上方 CONFIG 区的 API Key --------
    #
    # 快速测试（只生成 2 个）：
    # generate_icons(["contract", "travel"])
    #
    # 全量生成：
    generate_icons(KEYWORDS, backend=PREFERRED_BACKEND)
