"""
auto_confirm.py — 自动确认弹窗
检测 "Do you want to proceed?" / "1. Yes" 弹窗, 自动确认
静默后台运行, 指纹去重
"""
import sys, os, time, json, logging, hashlib
from datetime import datetime
from pathlib import Path
from threading import Thread, Event

import pygetwindow as gw
import pyautogui

LOG_FILE = Path(__file__).parent / "auto_confirm.log"
STATE_FILE = Path(__file__).parent / "auto_confirm_state.json"
POLL_INTERVAL = 1.0
SEEN_TIMEOUT = 300  # forget fingerprint after 5 min

# 匹配模式: title 或 部分文本
MATCH_PATTERNS = [
    "proceed",
    "Do you want",
    "1. Yes",
    "安全警告",
    "防火墙",
    "Windows 安全",
    "确认",
    "提示",
]
# 按钮操作: 默认 Enter (选 Yes/确定)
ACTION = "enter"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger("auto_confirm")


def window_fingerprint(win):
    """生成窗口指纹用于去重"""
    raw = f"{win.title}|{win.left}|{win.top}|{win.width}|{win.height}"
    return hashlib.md5(raw.encode()).hexdigest()


def try_get_text(hwnd):
    """通过 ctypes 尝试读取窗口文本内容"""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buf = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buf, length)
    return buf.value


def find_matching_windows():
    """找到匹配的弹窗"""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    results = []
    seen_hwnds = set()

    def enum_callback(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = try_get_text(hwnd)
        if not title:
            return True
        text_lower = title.lower()
        for pat in MATCH_PATTERNS:
            if pat.lower() in text_lower:
                rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                results.append({
                    "hwnd": hwnd,
                    "title": title,
                    "left": rect.left,
                    "top": rect.top,
                    "width": rect.right - rect.left,
                    "height": rect.bottom - rect.top,
                })
                break
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                     ctypes.wintypes.HWND,
                                     ctypes.wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return results


def get_dialog_items(hwnd):
    """获取对话框中的子窗口 (按钮等)"""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    items = []

    def enum_child(child_hwnd, lparam):
        text = try_get_text(child_hwnd)
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(child_hwnd, ctypes.byref(rect))
        items.append({
            "hwnd": child_hwnd,
            "text": text,
            "left": rect.left,
            "top": rect.top,
            "width": rect.right - rect.left,
            "height": rect.bottom - rect.top,
        })
        return True

    CHILDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                       ctypes.wintypes.HWND,
                                       ctypes.wintypes.LPARAM)
    user32.EnumChildWindows(hwnd, CHILDENUMPROC(enum_child), 0)
    return items


def confirm_dialog(win_info):
    """执行确认操作"""
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    # 1. 激活窗口
    user32.SetForegroundWindow(win_info["hwnd"])
    user32.BringWindowToTop(win_info["hwnd"])
    time.sleep(0.3)

    # 2. 找子按钮
    children = get_dialog_items(win_info["hwnd"])
    yes_btn = None
    for c in children:
        txt = (c.get("text") or "").lower()
        if any(k in txt for k in ["yes", "确定", "是", "确认", "allow", "允许",
                                   "proceed", "继续", "运行", "run"]):
            yes_btn = c
            break

    if yes_btn:
        # 点击按钮中心
        cx = yes_btn["left"] + yes_btn["width"] // 2
        cy = yes_btn["top"] + yes_btn["height"] // 2
        pyautogui.click(cx, cy)
        log.info(f"Clicked Yes button '{yes_btn['text']}' at ({cx},{cy})")
    else:
        # 没找到按钮 → 发 Enter
        pyautogui.press("enter")
        log.info("No Yes button found, sent Enter")

    return True


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {"seen": {}, "count": 0}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def cleanup_state(state):
    now = time.time()
    state["seen"] = {fp: ts for fp, ts in state["seen"].items()
                     if now - ts < SEEN_TIMEOUT}


def run_loop(stop_event):
    log.info("auto_confirm 启动")
    state = load_state()

    while not stop_event.is_set():
        try:
            windows = find_matching_windows()
            for w in windows:
                fp = window_fingerprint(w)
                # pygetwindow 检测 title 辅助
                try:
                    pgw = gw.getWindowsWithTitle(w["title"])
                    if pgw:
                        w["_pygw"] = pgw[0]
                except:
                    pass

                now = time.time()
                # 去重: 指纹窗口
                if fp in state["seen"] and now - state["seen"][fp] < SEEN_TIMEOUT:
                    continue

                log.info(f"检测到弹窗: {w['title']} ({w['width']}x{w['height']})")
                if confirm_dialog(w):
                    state["seen"][fp] = now
                    state["count"] = state.get("count", 0) + 1
                    cleanup_state(state)
                    save_state(state)
                    log.info(f"已确认 (总计 {state['count']})")
        except Exception as e:
            log.error(f"轮询错误: {e}")

        stop_event.wait(POLL_INTERVAL)

    log.info("auto_confirm 停止")


def start(stop_event=None):
    """启动后台线程"""
    e = stop_event or Event()
    t = Thread(target=run_loop, args=(e,), daemon=True)
    t.start()
    return e, t


def main():
    import argparse
    parser = argparse.ArgumentParser(description="自动确认弹窗")
    parser.add_argument("action", nargs="?", default="run",
                        choices=["run", "status", "list", "reset"],
                        help="操作")
    args = parser.parse_args()

    if args.action == "list":
        state = load_state()
        print(f"已确认: {state.get('count', 0)} 次")
        for fp, ts in state.get("seen", {}).items():
            dt = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            print(f"  {dt} | {fp[:12]}")
        return

    if args.action == "reset":
        save_state({"seen": {}, "count": 0})
        print("状态已重置")
        return

    if args.action == "status":
        # 检查是否有同名进程
        import subprocess
        r = subprocess.run(
            'wmic process where "name=\'python.exe\'" get commandline /FORMAT:CSV',
            shell=True, capture_output=True, text=True, timeout=10
        )
        running = "auto_confirm" in r.stdout.lower()
        print(f"auto_confirm: {'运行中' if running else '未运行'}")
        state = load_state()
        print(f"已确认历史: {state.get('count', 0)} 次")
        return

    # run — 前台持续运行
    print("auto_confirm 运行中 (Ctrl+C 停止)")
    stop_event = Event()
    try:
        run_loop(stop_event)
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
