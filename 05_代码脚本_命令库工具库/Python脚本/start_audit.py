"""
start_audit.py — 多目标动态审计引擎启动器
读取 Live_Profiles → 交互/命令行选目标 → 注入引擎 → 启动
"""

import sys, json, subprocess, time, ast, re
from pathlib import Path

BASE = Path("E:/MyCodeProjects")
INSTRUCTIONS = Path(__file__).parent / "instructions.md"

# ── 解析 Live_Profiles ──────────────────────────────────

def parse_profiles() -> dict:
    """从 instructions.md 提取 Live_Profiles dict."""
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    # 找 Live_Profiles = { ... } 代码块
    m = re.search(r"Live_Profiles\s*=\s*(\{.+?\n\})", text, re.DOTALL)
    if not m:
        print("[错误] instructions.md 中未找到 Live_Profiles")
        sys.exit(1)
    try:
        profiles = ast.literal_eval(m.group(1))
    except Exception as e:
        print(f"[错误] 解析 Live_Profiles 失败: {e}")
        sys.exit(1)
    # 注入 _slug
    for key, val in profiles.items():
        val["_slug"] = key
    return profiles


PROFILES = parse_profiles()


# ── 交互选择 ────────────────────────────────────────────

def select_target():
    print("\n" + "=" * 45)
    print("  监控哪个直播间?")
    print("=" * 45)
    items = list(PROFILES.items())
    for i, (key, val) in enumerate(items, 1):
        print(f"  {i}. {val['display']} ({val.get('style', '?')})")
    print(f"  {len(items)+1}. 自定义(新直播间)")
    print()
    choice = input("  输入编号: ").strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx][1]
        elif idx == len(items):
            return custom_target()
        else:
            print("无效")
            return select_target()
    except ValueError:
        print("无效")
        return select_target()


def custom_target():
    name = input("  直播间名称: ").strip()
    print(f"  [采样] 将运行 1 分钟采样模式自动分析 {name}")
    profile = {
        "_slug": name.replace(" ", "_"),
        "_alias": name.replace(" ", "_"),
        "display": name,
        "style": "自定义",
        "chat_region": (1700, 700, 400, 500),
        "food_zone": {"y_start": 0.66, "y_end": 1.0, "x_start": 0.2, "x_end": 0.8},
        "keywords": [],
        "fuzzy_chars": [],
        "fuzzy_targets": [],
        "benchmark": {},
        "notes": f"自动采样: {time.strftime('%Y-%m-%d')}",
    }
    return profile


# ── 依赖检查 ────────────────────────────────────────────

def check_deps():
    deps = {"easyocr": "easyocr", "cv2": "opencv-python", "pyautogui": "pyautogui", "pygetwindow": "pygetwindow"}
    missing = [pkg for mod, pkg in deps.items() if _import_fails(mod)]
    if not missing:
        print("[依赖] 全部通过")
        return True
    print(f"[依赖] 缺失: {', '.join(missing)}")
    if input(" 自动安装? (y/n): ").strip().lower() == "y":
        for pkg in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
        print("[依赖] 安装完成")
        return True
    return False


def _import_fails(mod):
    try:
        __import__(mod)
        return False
    except ImportError:
        return True


# ── 清理 ────────────────────────────────────────────────

def clean_frames(profile):
    alias = profile.get("_alias", profile["_slug"])
    d = BASE / "06-存档中心" / "temp_frames" / alias
    if d.exists():
        count = sum(1 for f in d.iterdir() if f.suffix in (".png", ".jpg"))
        for f in d.iterdir():
            f.unlink()
        print(f"[清理] 删 {count} 张旧截图")
    else:
        d.mkdir(parents=True)
        print(f"[清理] 创建 {d}")


# ── 保存新 Profile ─────────────────────────────────────

def save_profile(profile, metrics: dict):
    """采样后将新 profile 写入 instructions.md."""
    slug = profile["_slug"]
    # 更新视觉参数
    if metrics:
        profile["brightness_target"] = round(metrics.get("brightness", 0))
        profile["warm_ratio_target"] = round(metrics.get("warm_ratio", 0), 2)
        profile["benchmark"]["brightness"] = round(metrics.get("brightness", 0) * 1.1)
        profile["benchmark"]["contrast"] = round(metrics.get("contrast", 0))
        profile["benchmark"]["warm_ratio"] = round(metrics.get("warm_ratio", 0) * 1.5, 2)
        profile["benchmark"]["detail"] = round(metrics.get("detail", 0))
        profile["benchmark"]["color_entropy"] = round(metrics.get("color_entropy", 0), 1)

    # 以 JSON 格式追加
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    new_entry = f'\n    "{slug}": {json.dumps(profile, ensure_ascii=False, indent=4)},\n'
    # 在 "}" 前插入
    text = text.rstrip()
    if text.endswith("}"):
        text = text[:-1] + new_entry + "}"
    INSTRUCTIONS.write_text(text, encoding="utf-8")
    print(f"[保存] {slug} profile 已写入 instructions.md")


# ── 运行引擎 ────────────────────────────────────────────

def run_engine(profile):
    from monitor_engine import LiveMonitorEngine

    clean_frames(profile)
    name = profile["display"]

    # 采样模式: 新直播间 / --sample 标志
    if profile.get("style") == "自定义" or "--sample" in sys.argv:
        print(f"\n[采样] 开始 1 分钟采样 ({name})...")
        engine = LiveMonitorEngine(profile)
        metrics = engine.sample()
        if metrics:
            save_profile(profile, metrics)
            print(f"[采样] 完成, 视觉向量已保存")
            # 用更新后的 profile 重启
            profile["benchmark"]["brightness"] = round(metrics.get("brightness", 0) * 1.1)
            profile["brightness_target"] = round(metrics.get("brightness", 0))
        else:
            print("[采样] 失败, 使用默认参数")

    print(f"\n[启动] {name} -> monitor_engine.py")
    print("  Ctrl+C 停止\n")
    time.sleep(1)

    engine = LiveMonitorEngine(profile)
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\n[停止] 用户中断")


# ── 主入口 ──────────────────────────────────────────────

def main():
    print("\n" + "=" * 45)
    print("  Rule Investigator v2.0")
    print("  多目标动态审计引擎")
    print("=" * 45)

    if not check_deps():
        sys.exit(1)

    # 命令行参数: --target <名称>
    target_name = None
    if "--target" in sys.argv:
        idx = sys.argv.index("--target")
        if idx + 1 < len(sys.argv):
            target_name = sys.argv[idx + 1]

    profile = None
    if target_name:
        # 模糊匹配
        for key, val in PROFILES.items():
            if target_name.lower() in key.lower() or target_name.lower() in val["display"].lower():
                profile = val
                break
        if not profile:
            print(f"[目标] 未找到 '{target_name}', 进入采样模式")
            profile = {
                "_slug": target_name.replace(" ", "_"),
                "_alias": target_name.replace(" ", "_"),
                "display": target_name,
                "style": "自定义",
                "chat_region": (1700, 700, 400, 500),
                "food_zone": {"y_start": 0.66, "y_end": 1.0, "x_start": 0.2, "x_end": 0.8},
                "keywords": [],
                "fuzzy_chars": [],
                "fuzzy_targets": [],
                "benchmark": {},
                "notes": f"CLI创建: {time.strftime('%Y-%m-%d')}",
            }
    else:
        profile = select_target()

    run_engine(profile)


if __name__ == "__main__":
    main()
