import os
import sys
import io
import ctypes
from ctypes import wintypes
import configparser
import difflib
import requests
import json
import re

# 强制 stdout 使用 UTF-8，避免 Windows GBK 终端乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ICONS_DIR = "icons"  # 确保这个路径指向您存放图标的文件夹

# ================================================================
#  黑名单：语义模糊 / 无意义的目录名，跳过不处理
# ================================================================
EXCLUDE_PATTERNS = {
    "新建文件夹", "新建文件夹 (2)", "新建文件夹 (3)",
    "new folder", "untitled folder", "temp", "tmp",
    "测试", "test", "临时", "backup", "bak",
    "desktop", "桌面",
}

def is_meaningful_folder(name: str) -> bool:
    """
    判断文件夹名是否有语义价值。
    排除规则：
      1. 在黑名单中（精确匹配，忽略大小写）
      2. 名称为纯数字（如 "123"）
      3. 名称过短（≤1 个字符）
      4. 匹配"新建文件夹*"模式
    """
    name_lower = name.strip().lower()

    # 规则 1：精确黑名单
    if name_lower in {p.lower() for p in EXCLUDE_PATTERNS}:
        return False

    # 规则 2：纯数字
    if name_lower.isdigit():
        return False

    # 规则 3：过短
    if len(name.strip()) <= 1:
        return False

    # 规则 4：以"新建文件夹"开头（含序号变体）
    if re.match(r"^新建文件夹", name.strip()):
        return False

    return True


# ================================================================
#  Ollama 语义提取：输入文件夹名 → 输出 (主题, 图标关键词)
# ================================================================
def extract_topic_with_ollama(folder_name: str, model: str = "qwen2.5:latest") -> dict:
    """
    调用本地 Ollama API，对文件夹名做语义理解。
    返回：{"topic": "合同文档", "icon_keyword": "contract", "confidence": "high"}
    出错时返回 {"topic": folder_name, "icon_keyword": folder_name, "confidence": "low"}
    """
    prompt = f"""你是一个文件管理专家。给定一个文件夹名称，请分析它的语义主题，并推荐一个最合适的英文图标关键词。

文件夹名称：「{folder_name}」

可用的图标关键词（从此表选择最匹配的）：
code / contract / finance / design / document / image / music / database / archive / education / travel / robot / car / note / file / user / lock / share / download / upload / search / save / edit / trash / bell / calendar / play / pause / help / warning

请严格按照以下 JSON 格式返回（不要有任何其他内容）：
{{
  "topic": "中文主题描述（5字以内）",
  "icon_keyword": "英文图标关键词（从上方列表中选取最贴合的）",
  "confidence": "high 或 medium 或 low"
}}"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=30
        )
        if response.status_code == 200:
            raw = response.json().get("response", "")
            # 从返回文本中提取 JSON 块
            json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                return {"topic": folder_name, "icon_keyword": folder_name.lower(), "confidence": "low"}
        else:
            print(f"  ⚠️  Ollama 返回错误状态码：{response.status_code}")
            return {"topic": folder_name, "icon_keyword": folder_name.lower(), "confidence": "low"}
    except requests.exceptions.ConnectionError:
        print("  ❌ 无法连接 Ollama（请确认 ollama serve 正在运行）")
        return {"topic": folder_name, "icon_keyword": folder_name.lower(), "confidence": "low"}
    except Exception as e:
        print(f"  ❌ Ollama 调用异常：{e}")
        return {"topic": folder_name, "icon_keyword": folder_name.lower(), "confidence": "low"}


# ================================================================
#  批量扫描主函数（dry_run=True：仅展示结果，不修改图标）
# ================================================================
def batch_scan_desktop(desktop_path: str = r"E:\Desktop", dry_run: bool = True):
    """
    遍历 desktop_path 下所有一级文件夹，
    对有语义的目录调用 Ollama 提取主题 + 匹配图标，
    打印识别结果列表。

    :param desktop_path: 桌面路径
    :param dry_run:      True=仅预览，False=实际设置图标
    """
    print("=" * 65)
    print(f"  [*]  批量文件夹分析工具")
    print(f"  扫描路径：{desktop_path}")
    print(f"  运行模式：{'[预览] 仅展示识别结果，不修改文件' if dry_run else '[执行] 将实际修改图标'}")
    print("=" * 65)

    if not os.path.isdir(desktop_path):
        print(f"❌ 路径不存在：{desktop_path}")
        return []

    # 获取所有一级文件夹（非文件）
    all_entries = os.listdir(desktop_path)
    folders = [
        e for e in all_entries
        if os.path.isdir(os.path.join(desktop_path, e))
    ]

    print(f"\n共发现 {len(folders)} 个文件夹，正在过滤...\n")

    skipped = []
    to_process = []

    for name in sorted(folders):
        if is_meaningful_folder(name):
            to_process.append(name)
        else:
            skipped.append(name)

    # 打印被跳过的目录
    if skipped:
        print(f"[跳过] 已排除无语义目录：{len(skipped)} 个")
        for s in skipped:
            print(f"   - {s}")
        print()

    if not to_process:
        print("⚠️  没有找到需要处理的有意义文件夹。")
        return []

    print(f"[目标] 待分析文件夹：{len(to_process)} 个\n")
    print("-" * 65)

    results = []

    for idx, name in enumerate(to_process, start=1):
        folder_path = os.path.join(desktop_path, name)
        print(f"[{idx:02d}/{len(to_process):02d}] 正在分析：{name}")

        # 调用 Ollama
        info = extract_topic_with_ollama(name)
        topic       = info.get("topic", name)
        icon_kw     = info.get("icon_keyword", "folder")
        confidence  = info.get("confidence", "low")

        # 在本地图标库中搜索
        icon_path = search_local_icon(icon_kw)
        icon_display = os.path.basename(icon_path) if icon_path else f"❓ 未找到（关键词: {icon_kw}）"

        # 置信度标识
        conf_badge = {"high": "[高]", "medium": "[中]", "low": "[低]"}.get(confidence, "[?]")

        # 终端视觉反馈
        print(f"       文件夹 [{name}]")
        print(f"    -> 识别主题 [{topic}]  {conf_badge}")
        print(f"    -> 匹配图标 [{icon_display}]")
        print()

        results.append({
            "folder_name": name,
            "folder_path": folder_path,
            "topic":       topic,
            "icon_keyword": icon_kw,
            "icon_path":   icon_path,
            "confidence":  confidence,
        })

        # 非 dry_run 模式：实际设置图标
        if not dry_run and icon_path:
            ext = os.path.splitext(icon_path)[1].lower()
            if ext == ".ico":
                result_msg = set_folder_icon(folder_path, icon_path)
                print(f"       {result_msg}\n")
            else:
                print(f"       ⚠️  图标格式为 {ext}，需转换为 .ico 后才能设置。跳过。\n")

    # 打印汇总表格
    print("=" * 65)
    print("  📊  识别结果汇总")
    print("=" * 65)
    print(f"  {'序号':<4} {'文件夹名':<22} {'识别主题':<12} {'匹配图标':<20} 置信度")
    print("-" * 65)
    for i, r in enumerate(results, start=1):
        icon_short = os.path.basename(r["icon_path"]) if r["icon_path"] else "未找到"
        conf_badge = {"high": "[高]", "medium": "[中]", "low": "[低]"}.get(r["confidence"], "[?]")
        print(f"  {i:<4} {r['folder_name']:<22} {r['topic']:<12} {icon_short:<20} {conf_badge}")
    print("=" * 65)

    if dry_run:
        print("\n[OK] 预览完成！以上为识别结果，图标均未修改。")
        print("     确认无误后，将 dry_run=True 改为 dry_run=False 即可执行实际修改。\n")
    else:
        print("\n[OK] 所有支持格式的图标已设置完毕。\n")

    return results


# ----------------------------------------------------------------
#  第 1 级：本地图标库搜索
# ----------------------------------------------------------------
def search_local_icon(keyword: str) -> str | None:
    """
    在 icons/ 目录中按文件名做模糊匹配。
    支持格式：.ico  .png
    返回匹配到的绝对路径，未命中返回 None。
    """
    ICONS_DIR = "icons"  # 确保 ICONS_DIR 是局部变量

    if not os.path.isdir(ICONS_DIR):
        return None

    supported_ext = {".ico", ".png"}
    icon_files = [
        f for f in os.listdir(ICONS_DIR)
        if os.path.splitext(f)[1].lower() in supported_ext
    ]
    if not icon_files:
        return None

    # 提取文件名（去后缀、转小写）作为候选
    bare_names = [os.path.splitext(f)[0].lower() for f in icon_files]
    kw = keyword.lower()

    # ① 精确匹配
    if kw in bare_names:
        idx = bare_names.index(kw)
        return os.path.join(ICONS_DIR, icon_files[idx])

    # ② 子串匹配（keyword 包含于文件名 或 文件名包含于 keyword）
    for i, name in enumerate(bare_names):
        if kw in name or name in kw:
            return os.path.join(ICONS_DIR, icon_files[i])

    # ③ difflib 模糊匹配（相似度阈值 0.6）
    matches = difflib.get_close_matches(kw, bare_names, n=1, cutoff=0.6)
    if matches:
        idx = bare_names.index(matches[0])
        return os.path.join(ICONS_DIR, icon_files[idx])

    # ④ 放弃（Windows 文件夹图标不支持 SVG，跳过远程下载）
    return None


# ----------------------------------------------------------------
#  第 2 级：为文件夹设置自定义图标
# ----------------------------------------------------------------
def set_folder_icon(folder_path: str, icon_path: str) -> str:
    """
    为指定文件夹设置自定义图标，通过写入 desktop.ini 并刷新 Windows Shell 缓存实现。

    :param folder_path: 目标文件夹的路径（绝对或相对路径均可）
    :param icon_path:   图标文件路径，推荐使用 .ico 或 .dll 格式
    :return:            操作结果说明字符串

    支持格式说明
    ─────────────
    ✅ .ico  — 直接支持，Windows 资源管理器原生识别
    ✅ .dll  — 直接支持，需在 IconResource 后追加索引，如 shell32.dll,4
    ⚠️  .svg  — Windows 资源管理器 **不支持** SVG 作为文件夹图标，
                请先使用工具将其转换为 .ico 后再调用此函数。
                推荐工具：https://convertio.co/svg-ico/
                         或本地命令：inkscape input.svg -o output.ico
    """
    # ---------- 参数校验 ----------
    if not os.path.isdir(folder_path):
        return f"❌ 错误：目标文件夹不存在 → {folder_path}"

    if not os.path.isfile(icon_path):
        return f"❌ 错误：图标文件不存在 → {icon_path}"

    ext = os.path.splitext(icon_path)[1].lower()

    # SVG 提前拦截：Windows 不支持 SVG 作文件夹图标
    if ext == ".svg":
        return (
            "⚠️  警告：Windows 资源管理器不支持 .svg 格式的文件夹图标。\n"
            "请先将 SVG 转换为 .ico 文件，再调用此函数。\n"
            "转换工具参考：\n"
            "  • 在线：https://convertio.co/svg-ico/\n"
            "  • 本地：inkscape input.svg -o output.ico\n"
            "  • 本地：magick convert input.svg output.ico  (需 ImageMagick)"
        )

    if ext not in {".ico", ".dll", ".exe"}:
        return f"❌ 错误：不支持的图标格式 '{ext}'，请使用 .ico 或 .dll 文件。"

    # ---------- 路径处理 ----------
    abs_folder = os.path.abspath(folder_path)
    abs_icon   = os.path.abspath(icon_path)
    ini_path   = os.path.join(abs_folder, "desktop.ini")

    # .dll/.exe 可带资源索引（默认 0），.ico 固定用 0
    icon_resource = f"{abs_icon},0"

    # ---------- 写入 desktop.ini ----------
    # 若已存在，先解除只读/系统/隐藏属性，确保可写
    if os.path.exists(ini_path):
        ctypes.windll.kernel32.SetFileAttributesW(ini_path, 128)  # 128 = FILE_ATTRIBUTE_NORMAL

    ini_lines = [
        "[.ShellClassInfo]",
        f"IconResource={icon_resource}",
        "[ViewState]",
        "Mode=",
        "Vid=",
        "FolderType=Generic",
    ]

    try:
        # Windows 资源管理器读取 desktop.ini 默认期望 UTF-16 LE 或 ANSI（GBK）编码
        with open(ini_path, "w", encoding="gbk") as f:
            f.write("\n".join(ini_lines) + "\n")
    except Exception as e:
        return f"❌ 写入 desktop.ini 失败：{e}"

    # ---------- 设置文件属性 ----------
    # desktop.ini 需标记为「隐藏 + 系统」才会被 Explorer 读取
    # 2 = FILE_ATTRIBUTE_HIDDEN，4 = FILE_ATTRIBUTE_SYSTEM
    ctypes.windll.kernel32.SetFileAttributesW(ini_path, 2 | 4)

    # 文件夹本身需标记为「只读」，这是 Explorer 检查 desktop.ini 的触发条件
    # 1 = FILE_ATTRIBUTE_READONLY
    ctypes.windll.kernel32.SetFileAttributesW(abs_folder, 1)

    # ---------- 刷新 Windows Shell 图标缓存 ----------
    # SHCNE_ASSOCCHANGED (0x08000000)：通知 Shell 文件关联/外观已改变
    # SHCNF_IDLIST      (0x0000)    ：参数为 NULL（全局刷新）
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

    return (
        f"✅ 成功！文件夹图标已设置。\n"
        f"   文件夹 : {abs_folder}\n"
        f"   图标   : {abs_icon}\n"
        f"   如图标未立即刷新，可尝试：\n"
        f"     1. 按 F5 刷新资源管理器\n"
        f"     2. 注销并重新登录 Windows"
    )


# ================================================================
#  主入口
# ================================================================
if __name__ == "__main__":
    # ── 预览模式（dry_run=True）：扫描并展示识别结果，不修改任何文件 ──
    batch_scan_desktop(
        desktop_path=r"E:\Desktop",
        dry_run=True           # ⬅ 改为 False 即可执行真实图标替换
    )
