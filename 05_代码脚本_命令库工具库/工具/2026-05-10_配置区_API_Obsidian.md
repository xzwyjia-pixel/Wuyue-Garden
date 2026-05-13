---
title: 我的目标是用Costco的生成文件存放在一盘下的Michael的product文件夹下，当不需要生成文件的时候，或者说我本地操作的时候，我就会用obcd软件打开一盘下的Michael的product文件夹下的文件。 我希望达到的目标是软件。 可以运用他的。 本身的能力。 清晰的显示出来Michael的product文件夹下的所有文件之间的相互联系。 按照这个目标， 帮我生成高的扣的指令。 同时我在Microsoft Microsoft的随时调用。 同时。 在生成文件的时候，希望三者能够形成。 实实的连动如果实现不了连动的话，那么可以通过命令或者说通过其他方式直接调用。
source: gemini
date: 2026-05-10
category: Obsidian配置
tags: [gemini, Obsidian配置]
---

## 我的目标是用Costco的生成文件存放在一盘下的Michael的product文件夹下，当不需要生成文件的时候，或者说我本地操作的时候，我就会用obcd软件打开一盘下的Michael的product文件夹下的文件。 我希望达到的目标是软件。 可以运用他的。 本身的能力。 清晰的显示出来Michael的product文件夹下的所有文件之间的相互联系。 按照这个目标， 帮我生成高的扣的指令。 同时我在Microsoft Microsoft的随时调用。 同时。 在生成文件的时候，希望三者能够形成。 实实的连动如果实现不了连动的话，那么可以通过命令或者说通过其他方式直接调用。

鉴于你目前的配置（已启用 Obsidian Local REST API），我们可以通过一个 Python 自动化桥梁 来实现这个复杂的联动需求。
你的核心诉求是：代码资产（E 盘）、AI 逻辑（Claude） 与 知识大脑（Obsidian） 之间的实时或指令级触发联动。

核心实现逻辑
由于 Obsidian 无法直接“通过感知文件变化”来自动生成复杂的双链关系，我们需要利用 Python + Local REST API。

扫描器：读取 E:\Mycodeprojects 及其子目录。
分类器：根据后缀（.py, .js, .cpp）或配置文件（requirements.txt, package.json）自动识别项目类型。
连接器：

在 Obsidian 中为每个项目生成一个 MOC (Map of Content) 笔记。
使用 [[双链]] 将同类型的项目、共用的库或相互引用的模块关联起来。
利用你配置好的 API，直接将这些结构推送到你的 Obsidian 库。




Python 联动脚本
请将以下代码保存为 sync_to_obsidian.py。我已经根据你之前的配置信息（API Key 和地址）进行了预设：
import os
import requests

# --- 配置区 ---
OBSIDIAN_API_KEY = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
API_URL = "http://127.0.0.1:27123"
SOURCE_DIR = r"E:\Mycodeprojects"
# 你希望在 Obsidian 中存放这些索引的文件夹
TARGET_FOLDER = "Project_Nexus" 

headers = {
    "Authorization": f"Bearer {OBSIDIAN_API_KEY}",
    "Content-Type": "text/markdown"
}

def get_project_type(path):
    """简单识别项目类型"""
    files = os.listdir(path)
    if 'package.json' in files: return "Web_Frontend"
    if 'requirements.txt' in files or any(f.endswith('.py') for f in files): return "Python_AI"
    if 'CMakeLists.txt' in files: return "CPP_Industrial"
    return "General_Tech"

def sync_projects():
    project_map = {}
    
    # 1. 扫描并分类
    for item in os.listdir(SOURCE_DIR):
        full_path = os.path.join(SOURCE_DIR, item)
        if os.path.isdir(full_path):
            p_type = get_project_type(full_path)
            project_map.setdefault(p_type, []).append((item, full_path))

    # 2. 生成/更新 Obsidian 笔记
    for p_type, projects in project_map.items():
        content = f"# 项目分类: {p_type}\n\n## 关联项目列表\n"
        for name, path in projects:
            # 创建指向本地文件的链接 (Obsidian 支持 file:// 协议)
            file_link = f"file:///{path.replace('\\', '/')}"
            content += f"- [[{name}]] (路径: [{name}]({file_link}))\n"
        
        # 调用 API 写入 Obsidian
        file_path = f"{TARGET_FOLDER}/Type_{p_type}.md"
        url = f"{API_URL}/active-handle/{file_path}" # 这里可根据需要改为 put 接口
        try:
            requests.put(f"{API_URL}/vault/{file_path}", headers=headers, data=content.encode('utf-8'))
            print(f"已同步分类: {p_type}")
        except Exception as e:
            print(f"同步失败: {e}")

if __name__ == "__main__":
    sync_projects()


如何实现“实时联动”与“随时调用”
1. 在 Claude 中随时调用
当你与 Claude 交流新代码或新项目时，你可以直接下令：

“把这个项目存入 Obsidian，并更新 Project_Nexus 的关联图谱。”

我会调用上述脚本逻辑，通过 API 实时在你 E 盘创建文件，并同步在 Obsidian 中更新对应的 Markdown 索引和双链。
2. 实现真正的“相互联系”可视化

Graph View (关系图谱)：在 Obsidian 中打开“关系图谱”。由于脚本生成了 [[项目名]] 形式的双链，你会看到所有属于 Python_AI 的项目都围绕着一个中心节点，形成清晰的星状或网状结构。
Canvas (画布)：你可以手动将脚本生成的笔记拖入 Obsidian Canvas，直观地连线表示项目间的逻辑依赖。

3. 跨软件调用的“捷径”
为了满足你“不生成文件时本地操作”的需求：

在 Obsidian 中打开 VS Code：安装插件 Open in VS Code。这样你在 Obsidian 里看到项目联系后，一键点击就能跳回 E 盘对应的代码位置。
Windows 计划任务：你可以将上面的 Python 脚本设为“每小时运行一次”，或者“文件夹变动时运行”，从而实现无感的实时联动。

你需要我现在针对某个具体的项目类型（比如你的 Rule Investigator 审计工具）生成第一份关联结构吗？

---
*从 Gemini 导出，2026-05*
