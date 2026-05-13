"""
live_link_manager.py — 直播间链接自动检测+监控管理器
自动校验链接有效性, 自动打开直播间, 替代纯桌面OCR依赖
"""
import sys, os, json, time, re, subprocess
from pathlib import Path
from datetime import datetime
from threading import Thread
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

BASE = Path("E:/MyCodeProjects")
CONFIG_FILE = Path(__file__).parent / "live_links.json"
LOG_FILE = Path(__file__).parent / "live_links.log"
POLL_INTERVAL = 300  # 5min link check

# 默认直播间链接 (抖音)
DEFAULT_LINKS = {
    "排骨": {"url": "https://live.douyin.com/29140092590", "platform": "抖音", "auto_open": True},
    "排骨走遍乡村": {"url": "https://live.douyin.com/977116080057", "platform": "抖音", "auto_open": True},
    "苏苏在浙里": {"url": "", "platform": "视频号", "auto_open": False},
    "直播复盘系统": {"url": "https://live.douyin.com/977116080057", "platform": "抖音", "auto_open": True},
    "丹家小厨": {"url": "", "platform": "抖音", "auto_open": False},
    "大山里的小桃": {"url": "", "platform": "抖音", "auto_open": False},
    "清晨烟火小厨": {"url": "", "platform": "抖音", "auto_open": False},
    "顺子在杭州": {"url": "", "platform": "抖音", "auto_open": False},
    "凡姐走乡村": {"url": "", "platform": "抖音", "auto_open": False},
    "乡村小罗（苗族）": {"url": "", "platform": "抖音", "auto_open": False},
}


def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_links():
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            # Merge with defaults (keep existing, add new)
            for k, v in DEFAULT_LINKS.items():
                if k not in data:
                    data[k] = v
            return data
        except:
            pass
    return dict(DEFAULT_LINKS)


def save_links(data):
    CONFIG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def validate_url(url):
    """Validate URL basic format"""
    if not url or not url.strip():
        return False, "无链接"
    url = url.strip()
    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        return False, "链接格式无效"
    if "douyin.com" not in url and "live." not in url:
        return False, f"非抖音直播链接: {url[:40]}"
    return True, "格式有效"


def check_link_accessible(url):
    """Check if link is accessible via HTTP HEAD"""
    if not url:
        return False, "无链接"
    if not HAS_REQUESTS:
        return None, "未安装requests库"
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code < 500:
            return True, f"HTTP {r.status_code}"
        else:
            return False, f"HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        return False, "超时"
    except requests.exceptions.ConnectionError:
        return False, "连接失败"
    except Exception as e:
        return False, str(e)[:30]


def open_in_browser(url):
    """Open URL in default browser"""
    if not url:
        return False
    try:
        subprocess.run(["cmd", "/c", "start", url], shell=True, timeout=5)
        return True
    except:
        return False


def auto_open_live(profiles_data):
    """Auto-open live rooms that have auto_open=True"""
    opened = []
    for name, info in profiles_data.items():
        url = info.get("url", "")
        auto = info.get("auto_open", True)
        if url and auto:
            valid, msg = validate_url(url)
            if valid:
                open_in_browser(url)
                opened.append(name)
                log(f"[open] 打开直播间: {name} -> {url}")
                time.sleep(1)
    return opened


def status():
    data = load_links()
    print("\n=== 直播间链接状态 ===\n")
    for name, info in data.items():
        url = info.get("url", "")
        valid, vmsg = validate_url(url)
        icon = "[link]" if valid else "[x]"
        platform = info.get("platform", "?")
        auto = "自动" if info.get("auto_open") else "手动"
        print(f"  {icon} {name} ({platform}/{auto})")
        if url:
            print(f"      {url}")
        print(f"      {vmsg}")


def set_url(name, url):
    data = load_links()
    if name not in data and name not in DEFAULT_LINKS:
        # Check display names
        found = None
        for k in data:
            if name.lower() in k.lower() or k.lower() in name.lower():
                found = k
                break
        if not found:
            print(f"[X] 未知直播间: {name}")
            return
        name = found
    data[name]["url"] = url
    save_links(data)
    print(f"[OK] {name} 链接已更新")


def check_all():
    data = load_links()
    issues = []
    for name, info in data.items():
        url = info.get("url", "")
        if not url:
            issues.append(f"  [X] {name}: 未配置链接")
            continue
        valid, vmsg = validate_url(url)
        if not valid:
            issues.append(f"  [X] {name}: {vmsg}")
            continue
        accessible, amsg = check_link_accessible(url)
        if accessible is False:
            issues.append(f"  [!] {name}: {amsg}")
    return issues


def run_watchdog():
    """Background checker"""
    log("live_link_manager 启动")
    while True:
        try:
            issues = check_all()
            if issues:
                for i in issues:
                    log(i)
            else:
                log("[OK] 所有链接正常")
        except Exception as e:
            log(f"检查异常: {e}")
        time.sleep(POLL_INTERVAL)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="直播间链接管理器")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["status", "set", "open", "check", "watch"])
    parser.add_argument("name", nargs="?", default=None, help="直播间名称")
    parser.add_argument("url", nargs="?", default=None, help="直播间链接")
    args = parser.parse_args()

    if args.action == "status":
        status()

    elif args.action == "set":
        if not args.name or not args.url:
            print("用法: live_link_manager.py set <名称> <链接>")
            return
        set_url(args.name, args.url)

    elif args.action == "open":
        data = load_links()
        if args.name:
            info = data.get(args.name)
            if info and info.get("url"):
                open_in_browser(info["url"])
                print(f"[OK] 已打开 {args.name}")
            else:
                print(f"[X] {args.name} 未配置链接")
        else:
            opened = auto_open_live(data)
            if opened:
                print(f"[OK] 已打开 {len(opened)} 个直播间: {', '.join(opened)}")
            else:
                print("无自动打开的直播间")

    elif args.action == "check":
        issues = check_all()
        if issues:
            print("链接问题:")
            for i in issues:
                print(i)
        else:
            print("[OK] 所有链接正常")

    elif args.action == "watch":
        print("live_link_manager 守护运行中 (Ctrl+C 停止)")
        try:
            run_watchdog()
        except KeyboardInterrupt:
            print("\n已停止")


if __name__ == "__main__":
    main()
