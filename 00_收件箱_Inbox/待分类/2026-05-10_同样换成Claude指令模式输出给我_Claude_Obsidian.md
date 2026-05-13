---
title: 同样换成Claude指令模式输出给我
source: gemini
date: 2026-05-10
category: 编程开发
tags: [gemini, 编程开发]
---

## 同样换成Claude指令模式输出给我

明白了。既然你现在习惯通过 Claude Code 或 命令行模式 来高效管理项目，我为你整理了这套“追加更新”的标准化指令。
以后你只需将具体的内容和路径填入，直接在终端执行即可。
🛠️ 指令模板：追加内容至 Obsidian
你可以直接在终端（Terminal/PowerShell）运行以下 Python 指令。它会自动读取你的 API 并将内容“接”在现有笔记后面。
# 进入你的项目目录（如果你有特定的虚拟环境，请先激活）
# 运行以下指令来追加更新

python -c "
import requests

config = {
    'key': '8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c',
    'url': 'http://127.0.0.1:27123',
    'path': '/vault/Inbox/Claude_Sync.md'
}

update_text = \"\"\"
## 🔄 追加更新：MCP 自动化流配置 (2026-05-10)
- **配置目标**：实现从 Claude 直接控制 Obsidian 笔记。
- **当前状态**：API 连通性测试通过（Status 204），已实现静默写入。
- **后续指令**：使用“存入 Obsidian [路径]”即可触发自动存档。
\"\"\"

headers = {'Authorization': f'Bearer {config[\"key\"]}', 'Content-Type': 'text/markdown'}
res = requests.post(f'{config[\"url\"]}{config[\"path\"]}', data=update_text.encode('utf-8'), headers=headers)

if res.status_code in [200, 204]:
    print('✅ 追加更新成功！已同步至 Obsidian。')
else:
    print(f'❌ 失败: {res.status_code}')
"


📂 进阶：如何让 Claude Code 自动处理
如果你正在使用 Claude Code (命令行交互界面)，你可以直接给它一个“操作指令”，它会自动帮你写代码并执行。
你可以直接对它说：

“帮我把这段对话追加到 Inbox/Claude_Sync.md。使用我之前配置的 API Key 8212...770c，调用端口 27123 的 POST 接口。”


📝 常用 API 指令参考表 (CLI 模式)
如果你想通过 curl（Windows PowerShell 或 CMD）快速操作，可以使用以下简短指令：

读取笔记内容：
curl -H "Authorization: Bearer 你的Key" http://127.0.0.1:27123/vault/Inbox/Claude_Sync.md


完全覆盖笔记：
将 POST 换成 PUT 即可覆盖旧内容。
搜索笔记：
curl -X POST -H "Authorization: Bearer 你的Key" -H "Content-Type: application/json" -d '{"query": "规则甄查"}' http://127.0.0.1:27123/search/



目前追加更新已经完成。接下来，你是想继续完善“规则甄查系统”的架构文档，还是需要我为你整理一份关于短视频算法合规性的调研大纲并存入 Obsidian？

---
*从 Gemini 导出，2026-05*
