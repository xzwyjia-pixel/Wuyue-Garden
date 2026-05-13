"""
monitor_multi.py — 多直播间并行监控启动器
每个直播间跑独立进程(monitor_engine.py), 数据隔离
用法:
  python monitor_multi.py                              # 交互选择
  python monitor_multi.py --targets 苏苏,小桃,凡姐       # 指定多个
  python monitor_multi.py --all                        # 全部
  python monitor_multi.py --dashboard                  # 启动所有 + Web面板
"""
import sys, os, time, json, subprocess, signal, re, ast, argparse
from pathlib import Path
from datetime import datetime

BASE = Path("E:/MyCodeProjects")
INSTRUCTIONS = BASE / "审计工具" / "instructions.md"
ENGINE = BASE / "审计工具" / "monitor_engine.py"
DASHBOARD = BASE / "审计工具" / "dashboard_server.py"
PID_FILE = BASE / "06-存档中心" / "logs" / "multi_pids.json"
LOG_DIR = BASE / "06-存档中心" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def parse_profiles():
    """Parse Live_Profiles from instructions.md"""
    if not INSTRUCTIONS.exists():
        print(f"[错误] instructions.md 未找到: {INSTRUCTIONS}")
        return {}
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    m = re.search(r"Live_Profiles\s*=\s*(\{.+?\n\})", text, re.DOTALL)
    if not m:
        print("[错误] instructions.md 中未找到 Live_Profiles")
        return {}
    try:
        profiles = ast.literal_eval(m.group(1))
    except Exception as e:
        print(f"[错误] 解析 Live_Profiles 失败: {e}")
        return {}
    for key, val in profiles.items():
        val["_slug"] = key
    return profiles


def launch_monitor(profile, idx):
    """Launch one monitor engine process"""
    slug = profile.get("_slug", f"target{idx}")
    name = profile.get("display", slug)
    logfile = LOG_DIR / f"monitor_{slug}.log"
    # Build command-line args
    args = []
    for key, val in profile.items():
        if key.startswith("_"):
            continue
        args.append(f"--{key}={val}")
    cmd = [sys.executable, str(ENGINE), f"--target={slug}"] + args
    proc = subprocess.Popen(
        cmd,
        stdout=open(logfile, "a", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
    )
    print(f"  [{idx}] {name} → PID:{proc.id} 日志:{logfile.name}")
    return {"name": name, "slug": slug, "pid": proc.id, "proc": proc}


def show_status(procs):
    """Display running status table"""
    print(f"\n{'='*45}")
    print(f"  多直播间监控状态 ({datetime.now().strftime('%H:%M:%S')})")
    print(f"{'='*45}")
    for p in procs:
        alive = p["proc"].poll() is None
        status = "● 运行中" if alive else "○ 已停止"
        print(f"  [{p['slug']}] {p['name']:<12} PID:{p['pid']:<6} {status}")
    print(f"{'='*45}\n")


def kill_all(procs):
    """Kill all monitor processes"""
    print("\n[停止] 停止所有监控...")
    for p in procs:
        try:
            p["proc"].terminate()
            print(f"  [{p['slug']}] {p['name']} 已停止")
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description="多直播间并行监控")
    parser.add_argument("--targets", help="直播间名称, 逗号分隔")
    parser.add_argument("--all", action="store_true", help="启动全部")
    parser.add_argument("--dashboard", action="store_true", help="同时启动 Web 面板")
    parser.add_argument("--daemon", action="store_true", help="后台运行 (无窗口)")
    args = parser.parse_args()

    profiles = parse_profiles()
    if not profiles:
        return 1

    # Select targets
    if args.all:
        selected = list(profiles.values())
    elif args.targets:
        names = [n.strip() for n in args.targets.split(",")]
        selected = []
        for name in names:
            found = False
            for key, val in profiles.items():
                if name.lower() in key.lower() or name.lower() in val.get("display", "").lower():
                    selected.append(val)
                    found = True
                    break
            if not found:
                print(f"[警告] 未找到 '{name}'")
    else:
        # Interactive
        print("\n选择要监控的直播间 (逗号分隔编号, 如 1,3)")
        items = list(profiles.items())
        for i, (key, val) in enumerate(items, 1):
            print(f"  {i}. {val.get('display', key)}")
        choice = input("  > ").strip()
        indices = [int(x.strip()) for x in choice.split(",") if x.strip().isdigit()]
        selected = [items[i-1][1] for i in indices if 1 <= i <= len(items)]

    if not selected:
        print("[错误] 未选择任何直播间")
        return 1

    # Launch
    print(f"\n启动 {len(selected)} 个监控...")
    procs = []
    for i, profile in enumerate(selected, 1):
        procs.append(launch_monitor(profile, i))

    # Dashboard
    if args.dashboard:
        print("\n启动 Web Dashboard...")
        dash_proc = subprocess.Popen(
            [sys.executable, str(DASHBOARD)],
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print(f"  Dashboard → PID:{dash_proc.id}  http://localhost:5050")
        procs.append({"name": "Dashboard", "slug": "dashboard", "pid": dash_proc.id, "proc": dash_proc})

    show_status(procs)

    if args.daemon:
        print("[后台] 所有监控已在后台运行")
        print(f"[后台] 查看状态: python {__file__} --targets ...")
        procs_data = {p["slug"]: p["pid"] for p in procs}
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PID_FILE, "w") as f:
            json.dump(procs_data, f)
        return 0

    # Wait + keyboard interactive
    print("按 Enter 查看状态 | q + Enter 停止所有")
    try:
        while True:
            line = sys.stdin.readline().strip()
            if line.lower() == "q":
                break
            show_status(procs)
    except (KeyboardInterrupt, EOFError):
        pass

    kill_all(procs)
    print("[完成]")
    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    sys.exit(main())
