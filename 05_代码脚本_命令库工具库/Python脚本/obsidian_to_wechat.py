"""
obsidian_to_wechat.py — Obsidian MD 导出到微信联系人
用法:
  python obsidian_to_wechat.py <md文件路径> --contact <联系人名>
  python obsidian_to_wechat.py <md文件路径> --contact <联系人名> --preview  (仅预览, 不发送)

依赖:
  pip install uiautomation
  微信 PC 版需已登录
"""
import sys, re, time, argparse
from pathlib import Path

try:
    import uiautomation as auto
except ImportError:
    print("请先安装: pip install uiautomation")
    sys.exit(1)

# ====== Markdown 处理 ======

def strip_frontmatter(text):
    """移除 YAML frontmatter (--- ... ---)"""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text

def md_to_wechat_text(md_text):
    """Markdown → 微信友好纯文本"""
    text = strip_frontmatter(md_text)
    lines = text.split("\n")
    out = []
    in_code = False

    for line in lines:
        # 跳过代码块
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        # 跳过 frontmatter 残余
        if line.strip() == "---":
            continue

        # 标题: # xxx → 加粗换行
        if line.startswith("# "):
            out.append(f"\n{line[2:].strip()}\n{'-'*20}")
        elif line.startswith("## "):
            out.append(f"\n{line[3:].strip()}\n{'-'*15}")
        elif line.startswith("### "):
            out.append(f"\n{line[4:].strip()}")
        elif line.startswith("#### "):
            out.append(f"\n{line[5:].strip()}")
        # 列表
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            out.append(f"• {line.strip()[2:]}")
        # 数字列表
        elif re.match(r"^\d+[.)]\s", line.strip()):
            out.append(f"  {line.strip()}")
        # 表格分隔行 (|---|) 跳过
        elif re.match(r"^[\s\|:\-]+$", line) and "|" in line and "-" in line:
            continue
        # 表格行
        elif line.strip().startswith("|"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                out.append(" | ".join(cells))
        # 空行
        elif not line.strip():
            out.append("")
        # 普通文字: 移除行内 Markdown 标记
        else:
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            clean = re.sub(r"\*(.+?)\*", r"\1", clean)
            clean = re.sub(r"`(.+?)`", r"\1", clean)
            clean = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", clean)
            out.append(clean)

    return "\n".join(out).strip()


# ====== WeChat 自动化 ======

WECHAT_WINDOW_NAMES = ["微信", "WeChat"]

def find_wechat_window():
    """查找微信主窗口"""
    for name in WECHAT_WINDOW_NAMES:
        win = auto.WindowControl(searchDepth=1, Name=name)
        if win.Exists(maxSearchSeconds=2):
            return win
    return None

def send_to_wechat(contact_name, message):
    """通过 UI 自动化向微信联系人发送消息"""
    win = find_wechat_window()
    if not win:
        print("错误: 微信未运行或未登录。请打开微信后再试。")
        return False

    # 激活微信窗口
    win.SetActive()
    win.SetTopmost(True)
    time.sleep(1)

    # 找搜索框: 通常在顶部
    search = win.EditControl(searchDepth=5)
    if not search.Exists(maxSearchSeconds=3):
        # 尝试 Ctrl+F 打开搜索
        win.SendKeys("{Ctrl}F", waitTime=1)
        time.sleep(0.5)
        search = win.EditControl(searchDepth=5)

    if not search.Exists(maxSearchSeconds=2):
        print("错误: 找不到微信搜索框")
        return False

    # 搜索联系人
    search.Click()
    time.sleep(0.3)
    search.SendKeys(contact_name, waitTime=0.5)
    time.sleep(1.5)

    # 选中搜索结果 (第一个联系人)
    try:
        list_item = win.ListItemControl(searchDepth=8)
        if list_item.Exists(maxSearchSeconds=2):
            list_item.Click()
            time.sleep(1)
        else:
            print(f"错误: 找不到联系人 '{contact_name}'")
            # 清空搜索
            search.SendKeys("{Escape}", waitTime=0.3)
            return False
    except Exception as e:
        print(f"错误: 选择联系人失败 - {e}")
        return False

    # 获取聊天输入框
    try:
        msg_edit = win.EditControl(searchDepth=8)
        if not msg_edit.Exists(maxSearchSeconds=3):
            # 可能是RichEditControl
            msg_edit = win.RichEditControl(searchDepth=8)
    except Exception:
        msg_edit = None

    if not msg_edit or not msg_edit.Exists(maxSearchSeconds=2):
        print("错误: 找不到聊天输入框")
        return False

    # 分块发送 (微信单条消息不宜过长)
    msg_edit.Click()
    time.sleep(0.3)

    CHUNK_MAX = 2000
    if len(message) <= CHUNK_MAX:
        msg_edit.SendKeys(message, waitTime=0.5)
        time.sleep(0.3)
        msg_edit.SendKeys("{Enter}", waitTime=0.5)
        print(f"已发送: {len(message)} 字符")
    else:
        chunks = split_chunks(message, CHUNK_MAX)
        for i, chunk in enumerate(chunks):
            msg_edit.SendKeys(chunk, waitTime=0.5)
            time.sleep(0.2)
            msg_edit.SendKeys("{Enter}", waitTime=1)
            print(f"已发送第 {i+1}/{len(chunks)} 段 ({len(chunk)} 字符)")
            time.sleep(0.5)

    # 返回聊天列表 (按 Escape)
    time.sleep(0.5)
    win.SendKeys("{Escape}", waitTime=0.3)
    return True


def split_chunks(text, max_size):
    """按段落切分长文本"""
    paragraphs = text.split("\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 1 > max_size and current:
            chunks.append(current.strip())
            current = p + "\n"
        else:
            current += p + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


# ====== CLI ======

def main():
    parser = argparse.ArgumentParser(description="Obsidian MD → 微信联系人")
    parser.add_argument("md_path", help="Obsidian MD 文件路径")
    parser.add_argument("--contact", "-c", default="文件传输助手",
                       help="微信联系人名称 (默认: 文件传输助手)")
    parser.add_argument("--preview", "-p", action="store_true",
                       help="仅预览转换结果, 不发送")
    args = parser.parse_args()

    md_path = Path(args.md_path)
    if not md_path.is_file():
        print(f"错误: 文件不存在 - {md_path}")
        sys.exit(1)

    md_raw = md_path.read_text(encoding="utf-8")
    wechat_text = md_to_wechat_text(md_raw)

    if not wechat_text.strip():
        print("错误: 转换后内容为空")
        sys.exit(1)

    # 附加文件信息头
    output = f"[来自 Obsidian] {md_path.name}\n{'-'*30}\n\n{wechat_text}"

    print(f"═══ 预览 (共 {len(output)} 字符) ═══")
    print(output[:500])
    if len(output) > 500:
        print(f"\n... (剩余 {len(output)-500} 字符)")
    print(f"\n═══ 发送目标: {args.contact} ═══")

    if args.preview:
        print("预览模式, 不发送")
        return

    confirm = input(f"\n确认发送到 [{args.contact}]? (y/n): ")
    if confirm.lower() not in ("y", "yes"):
        print("已取消")
        return

    print(f"正在发送到 [{args.contact}]...")
    print("提示: 自动化操作期间请勿移动鼠标或键盘")
    time.sleep(2)

    success = send_to_wechat(args.contact, output)
    if success:
        print(f"完成: {md_path.name} → {args.contact}")
    else:
        print("发送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
