import os
import json
import re

# === 核心配置 ===
PROJECT_ROOT = r"E:\MyCodeProjects"
OBSIDIAN_ROOT = r"E:\Obsidian"  # 请根据实际路径微调
CLAUDE_CONFIG = os.path.expandvars(r"%APPDATA%\Claude\claude_desktop_config.json")

# 系统映射表 (匹配实际目录名)
SYSTEM_MAP = {
    "01-规则引擎": "核心规则与算法逻辑",
    "02-审计工具": "自动化脚本与MCP服务",
    "04-凡姐案例": "凡姐直播间审计专题",
    "05-小桃案例": "小桃乡村电商专题"
}

def run_maintenance():
    print("[START] 开始全自动化维护任务...")

    # 1. 修复 MCP 配置文件
    if os.path.exists(CLAUDE_CONFIG):
        with open(CLAUDE_CONFIG, 'r', encoding='utf-8') as f:
            config = json.load(f)

        config_str = json.dumps(config, ensure_ascii=False)
        # 自动纠正由于目录重整导致的路径错误
        config_str = config_str.replace("01-Production/", "03-生产素材/")
        config_str = config_str.replace("Audit_Assets/", "01-规则引擎/")

        with open(CLAUDE_CONFIG, 'w', encoding='utf-8') as f:
            f.write(config_str)
        print("[OK] MCP 配置文件路径已修复。")
    else:
        print("[WARN] Claude Desktop 配置文件不存在，跳过。")

    # 2. 生成/更新 CLAUDE.md 记忆锚点
    for folder, desc in SYSTEM_MAP.items():
        path = os.path.join(PROJECT_ROOT, folder)
        if os.path.exists(path):
            content = f"# {folder} 系统入口\n\n## 📋 系统描述\n{desc}\n\n" \
                      f"## 🤖 指令规约\n- 启动前读取本目录下最新 .jsonl 审计数据。\n" \
                      f"- 强制遵循 01 目录下的合规标准。\n\n" \
                      f"## 🔗 历史会话\n- [进入该系统历史 Chat](https://claude.ai/chat/)"

            with open(os.path.join(path, "CLAUDE.md"), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] 已更新记忆锚点: {folder}/CLAUDE.md")
        else:
            print(f"[WARN] 目录不存在，跳过: {folder}")

    # 3. 冗余清理 (自检程序)
    trash_folders = ['__pycache__', '.pytest_cache']
    for root, dirs, files in os.walk(PROJECT_ROOT):
        for d in dirs:
            if d in trash_folders:
                full_path = os.path.join(root, d)
                print(f"[SCAN] 发现冗余: {full_path}")
                # os.removedirs(full_path) # 谨慎操作，默认仅打印

    print("\n[DONE] 维护完成！请重启 Claude Desktop 以激活新配置。")

if __name__ == "__main__":
    run_maintenance()
