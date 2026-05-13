"""
enable_obsidian_plugin.py — UI自动化: 在Obsidian中启用Claudian插件
"""
import sys, time

try:
    import uiautomation as auto
except ImportError:
    print("请先运行: pip install uiautomation")
    sys.exit(1)

def find_obsidian():
    names = ["Obsidian", "知识库", "笔记"]
    for n in names:
        w = auto.WindowControl(searchDepth=1, Name=n)
        if w.Exists(maxSearchSeconds=1):
            return w
    return None

def main():
    print("查找 Obsidian 窗口...")
    win = find_obsidian()
    if not win:
        print("未找到 Obsidian 窗口, 请确认已打开")
        return

    win.SetActive()
    win.SetTopmost(True)
    time.sleep(1)

    print("打开设置 (Ctrl+,)...")
    win.SendKeys("{Ctrl}", waitTime=0.2)
    win.SendKeys(",", waitTime=0.5)
    time.sleep(1.5)

    # 获取设置窗口
    settings = auto.WindowControl(searchDepth=1, Name="设置")
    if not settings.Exists(maxSearchSeconds=3):
        settings = auto.WindowControl(searchDepth=1, Name="Settings")
    if not settings.Exists(maxSearchSeconds=2):
        # 可能已经开了
        settings = win
    else:
        settings.SetActive()
    time.sleep(1)

    # 侧边栏搜索: 找"社区插件"
    print("搜索: 社区插件...")
    search = settings.EditControl(searchDepth=5)
    if search.Exists(maxSearchSeconds=2):
        search.Click()
        time.sleep(0.2)
        search.SendKeys("社区插件", waitTime=0.5)
        time.sleep(1)
    elif search.Exists(maxSearchSeconds=2):
        search.Click()
        search.SendKeys("community plugins", waitTime=0.5)
        time.sleep(1)

    # 尝试点击搜索结果中的"社区插件"
    try:
        for ctrl in settings.GetChildren():
            if ctrl.Name and "社区插件" in ctrl.Name:
                ctrl.Click()
                time.sleep(1)
                break
    except:
        pass

    # 向下滚动找 Claudian
    print("查找 Claudian 开关...")
    # 通过搜索框找
    search2 = settings.EditControl(searchDepth=5)
    if search2.Exists(maxSearchSeconds=1):
        search2.Click()
        time.sleep(0.2)
        search2.SendKeys("{Ctrl}a", waitTime=0.3)
        search2.SendKeys("{Delete}", waitTime=0.2)
        search2.SendKeys("claudian", waitTime=0.5)
        time.sleep(1)

    # 尝试直接点击 toggle
    found = False
    try:
        # 搜索所有切换开关
        toggles = settings.Controls()
        for t in toggles:
            try:
                if t.Name and "Claudian" in t.Name:
                    t.Click()
                    found = True
                    print(f"找到并点击: {t.Name}")
                    break
            except:
                continue
    except:
        pass

    if not found:
        # 尝试通过 ControlType 找
        for depth in range(1, 10):
            try:
                pane = settings.PaneControl(searchDepth=depth)
                kids = pane.GetChildren() if pane.Exists(maxSearchSeconds=0.5) else []
                for k in kids:
                    if k.Name and "Claudian" in k.Name:
                        k.Click()
                        found = True
                        print(f"点击: {k.Name}")
                        break
            except:
                continue
            if found:
                break

    if not found:
        print("未自动找到开关, 已在插件列表中, 请手动开启")
        print("路径: Obsidian → 设置 → 社区插件 → Claudian → 开启")
    else:
        print("Claudian 已启用!")
        time.sleep(1)

    # 关闭设置
    settings.SendKeys("{Escape}", waitTime=0.5)
    time.sleep(0.5)

    print("\n完成。左侧边栏应出现机器人图标, 点击即可使用 Claude Code")

if __name__ == "__main__":
    main()
