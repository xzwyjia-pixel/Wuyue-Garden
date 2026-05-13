"""
manage_monitors.py — 多直播间监控管理器
查看/启动/停止/切换监控目标
"""
import sys, os, time, json, signal, subprocess, re, ast
from pathlib import Path

BASE = Path("E:/MyCodeProjects")
INSTRUCTIONS = Path(__file__).parent / "instructions.md"

PID_FILE = Path("monitors.pid")
MONITOR_DIR = Path("E:/MyCodeProjects/审计工具")


def parse_profiles():
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    m = re.search(r"Live_Profiles\s*=\s*(\{.+?\n\})", text, re.DOTALL)
    if not m:
        print("× instructions.md 中未找到 Live_Profiles")
        return {}
    try:
        profiles = ast.literal_eval(m.group(1))
        for k, v in profiles.items():
            v["_slug"] = k
        return profiles
    except Exception as e:
        print(f"× 解析失败: {e}")
        return {}


def find_python_processes():
    """Find running python processes with their command lines"""
    import subprocess
    result = subprocess.run(
        'wmic process where "name=\'python.exe\'" get processid,commandline /FORMAT:CSV',
        shell=True, capture_output=True, text=True, timeout=10
    )
    procs = {}
    for line in result.stdout.strip().split('\n'):
        if 'python' not in line.lower():
            continue
        # CSV: Node,CommandLine,ProcessId
        # CommandLine may contain commas, so split from right: PID after last comma
        idx = line.rfind(',')
        if idx < 0:
            continue
        pid = line[idx+1:].strip('" \r')
        rest = line[:idx]
        idx2 = rest.find(',')
        if idx2 < 0:
            continue
        cmd = rest[idx2+1:].strip('" ')
        procs[pid] = cmd
    return procs


def get_dashboard_pid():
    import subprocess
    result = subprocess.run(
        'wmic process where "name=\'python.exe\'" get processid,commandline /FORMAT:CSV',
        shell=True, capture_output=True, text=True, timeout=10
    )
    for line in result.stdout.strip().split('\n'):
        if 'dashboard' in line.lower():
            parts = line.split(',')
            if len(parts) >= 3:
                return parts[2].strip('" ')
    return None


def kill_process(pid):
    try:
        os.kill(int(pid), signal.SIGTERM)
        time.sleep(1)
        subprocess.run(f"taskkill /F /PID {pid} 2>nul", shell=True)
        return True
    except:
        return False


def status():
    print("\n=== 监控状态 ===\n")

    # Dashboard
    dp = get_dashboard_pid()
    if dp:
        print(f"  Dashboard: 运行中 (PID {dp}) → http://localhost:5050")
    else:
        print("  Dashboard: 未运行")

    # Monitors
    procs = find_python_processes()
    monitor_procs = {p: c for p, c in procs.items()
                     if 'monitor_' in c.lower() or 'start_audit' in c.lower()}
    if monitor_procs:
        print(f"\n  运行中的监控 ({len(monitor_procs)}):")
        for pid, cmd in monitor_procs.items():
            script = cmd.split('\\')[-1] if '\\' in cmd else cmd
            print(f"    PID {pid}: {script}")
    else:
        print("\n  监控: 无")

    # Profiles available
    profiles = parse_profiles()
    print(f"\n  可用目标 ({len(profiles)}):")
    for slug, p in profiles.items():
        status_icon = "●" if any(p['display'] in c for c in procs.values()) else "○"
        print(f"    {status_icon} {p['display']} ({p.get('style','?')})")

    # Auto-confirm
    has_ac = any("auto_confirm" in c.lower() for c in procs.values())
    print(f"\n  auto_confirm: {'运行中' if has_ac else '未运行'}")
    if has_ac:
        ac_state = MONITOR_DIR / "auto_confirm_state.json"
        if ac_state.exists():
            try:
                conf_state = json.loads(ac_state.read_text(encoding="utf-8"))
                print(f"    已确认: {conf_state.get('count', 0)} 次")
            except:
                pass

    # Data stats
    print("\n  数据量:")
    for slug, p in profiles.items():
        data_path = BASE / "04-宝妈直播诊断系统" / slug
        if data_path.exists():
            jsonl_files = list(data_path.glob("*.jsonl"))
            total_lines = 0
            for f in jsonl_files:
                try:
                    total_lines += len(f.read_text(encoding='utf-8', errors='ignore').split('\n'))
                except:
                    pass
            if total_lines > 0:
                print(f"    {p['display']}: {total_lines} 行数据")


def start_monitor(profile_slug):
    """Start monitor for a given profile"""
    profiles = parse_profiles()
    if profile_slug not in profiles:
        print(f"× 未知目标: {profile_slug}")
        return

    p = profiles[profile_slug]
    script_map = {
        "直播复盘系统": "monitor_diag.py",
        "排骨": "monitor_detect.py",
        "排骨走遍乡村": "monitor_paigu.py",
        "苏苏在浙里": "monitor_susu_pro.py",
        "小桃": "monitor_桃.py",
    }

    script = script_map.get(p["display"])
    if not script:
        # Try generic start
        script = "start_audit.py"
        cmd = f'start /B "" python "{MONITOR_DIR / script}" --target "{p["_slug"]}"'
    else:
        cmd = f'start /B "" python "{MONITOR_DIR / script}"'

    print(f"\n  启动监控: {p['display']}")
    print(f"  命令: python {script}")
    os.system(cmd)
    time.sleep(2)
    print(f"  已启动, 使用 status 查看")


def stop_monitor(pid=None):
    if pid:
        if kill_process(pid):
            print(f"  已停止 PID {pid}")
        else:
            print(f"  PID {pid} 停止失败")
    else:
        # Stop all monitors
        procs = find_python_processes()
        if not procs:
            print("  无运行中的监控")
            return
        for pid, cmd in procs.items():
            kill_process(pid)
            print(f"  已停止 PID {pid}")
        print("  所有监控已停止")


def restart_dashboard():
    dp = get_dashboard_pid()
    if dp:
        print(f"  停止旧 Dashboard (PID {dp})...")
        kill_process(dp)
        time.sleep(2)
    cmd = f'start /B "" python "{MONITOR_DIR / "dashboard_server.py"}" --port 5050'
    print("  启动 Dashboard...")
    os.system(cmd)
    time.sleep(2)
    print("  Dashboard 已启动 → http://localhost:5050")


def start_autoconfirm():
    print("  启动 auto_confirm 弹窗自动确认...")
    subprocess.Popen(
        f'start /B "" python "{MONITOR_DIR / "auto_confirm.py"}" run',
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    print("  auto_confirm 已启动 (后台静默运行)")


def stop_autoconfirm():
    import subprocess
    result = subprocess.run(
        'wmic process where "name=\'python.exe\'" get processid,commandline /FORMAT:CSV',
        shell=True, capture_output=True, text=True, timeout=10
    )
    found = False
    for line in result.stdout.strip().split('\n'):
        if 'auto_confirm' in line.lower():
            parts = line.split(',')
            if len(parts) >= 2:
                pid = parts[-1].strip('" ')
                if kill_process(pid):
                    print(f"  auto_confirm 已停止 (PID {pid})")
                    found = True
    if not found:
        print("  auto_confirm 未运行")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="多直播间监控管理器")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "start", "stop", "restart", "switch", "autoconfirm"],
                        help="操作: status/start/stop/restart/switch/autoconfirm")
    parser.add_argument("target", nargs="?", default=None,
                        help="目标直播间名称")

    args = parser.parse_args()

    if args.action == "status":
        status()

    elif args.action == "start":
        if not args.target:
            # Interactive selection
            profiles = parse_profiles()
            print("\n=== 选择启动目标 ===")
            items = list(profiles.items())
            for i, (key, val) in enumerate(items, 1):
                print(f"  {i}. {val['display']}")
            try:
                idx = int(input("  编号: ").strip()) - 1
                if 0 <= idx < len(items):
                    start_monitor(items[idx][0])
                else:
                    print("无效")
            except:
                print("无效")
        else:
            start_monitor(args.target)

    elif args.action == "stop":
        procs = find_python_processes()
        monitor_procs = {p: c for p, c in procs.items()
                         if 'monitor_' in c.lower() or 'start_audit' in c.lower()}
        if not monitor_procs:
            print("无运行中的监控")
            return
        print("\n运行中的监控:")
        items = list(monitor_procs.items())
        for i, (pid, cmd) in enumerate(items, 1):
            print(f"  {i}. PID {pid}: {cmd.split(chr(92))[-1] if chr(92) in cmd else cmd}")
        print(f"  {len(items)+1}. 全部停止")
        try:
            choice = int(input("  编号: ").strip())
            if 1 <= choice <= len(items):
                stop_monitor(items[choice-1][0])
            elif choice == len(items) + 1:
                stop_monitor()
        except:
            stop_monitor()

    elif args.action == "restart":
        if args.target == "dashboard":
            restart_dashboard()
        else:
            print("用法: manage_monitors.py restart dashboard")

    elif args.action == "switch":
        profiles = parse_profiles()
        print("\n=== 切换目标 ===")
        items = list(profiles.items())
        for i, (key, val) in enumerate(items, 1):
            print(f"  {i}. {val['display']}")
        try:
            idx = int(input("  编号: ").strip()) - 1
            if 0 <= idx < len(items):
                # Stop all, start new
                stop_monitor()
                time.sleep(1)
                start_monitor(items[idx][0])
            else:
                print("无效")
        except:
            print("无效")

    elif args.action == "autoconfirm":
        procs = find_python_processes()
        has_ac = any("auto_confirm" in c.lower() for c in procs.values())
        if has_ac:
            print("\n  auto_confirm 正在运行")
            choice = input("  停止? (y/N): ").strip().lower()
            if choice == "y":
                stop_autoconfirm()
        else:
            print("\n  auto_confirm 未运行")
            choice = input("  启动? (Y/n): ").strip().lower()
            if choice != "n":
                start_autoconfirm()

    elif args.action == "links":
        import live_link_manager as llm
        sub = args.target or "status"
        if sub == "status":
            llm.status()
        elif sub == "open":
            llm.auto_open_live(llm.load_links())
        elif sub == "check":
            issues = llm.check_all()
            for i in issues:
                print(i)
        elif sub == "watch":
            print("启动链接守护...")
            from threading import Thread
            t = Thread(target=llm.run_watchdog, daemon=True)
            t.start()


if __name__ == "__main__":
    main()
