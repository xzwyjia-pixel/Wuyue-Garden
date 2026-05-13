---
title: Prompted
source: gemini
date: 2026-05-02
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

太棒了！从你最新的截图来看，tutor_server.py 文件已经成功创建并放到了正确的路径下。
现在我们进入最后的“点火”阶段。请按照以下步骤操作，让 AI 正式获得这个新技能：

第一步：刷新并信任插件配置

回到 VS Code，打开你之前编辑过的 cline_mcp_settings.json。
再次确认文件顶部是否还有 "Restricted Mode"（受限模式）的蓝色横条。如果有，请务必点击 "Manage" -> "Trust"。
按下 Ctrl + S 重新保存一次配置文件。

第二步：重启 MCP 服务端

在 VS Code 侧边栏找到你的 AI 助手插件图标（比如 Cline）。
在插件面板中，找到 MCP Servers 列表。
你应该能看到 tutor-skills。如果它显示为红色或灰色，点击旁边的“刷新”图标或重启按钮。
成功标志：当它变成绿色（Active）时，说明 AI 已经成功连接到了你的 Python 脚本。

第三步：正式测试
现在，你可以在聊天框里直接给 AI 下指令了。建议试试以下几个指令来验证它的功能：

验证工具列表：

“请列出你现在拥有的 tutor-skills 相关的工具。”


模拟初始化（针对你的项目）：

“请调用 tutor_setup 扫描一下我的 E:\MyCodeProjects\RulesBureau 文件夹。”


启动交互测试：

“针对‘短视频风控规则’这个主题，用 tutor_test 对我进行一次提问。”




常见小问题排查
如果 tutor-skills 依然是红色，请在插件的 "Output"（输出）窗口中选择 "MCP Server: tutor-skills" 查看日志。

如果提示 ModuleNotFoundError: No module named 'mcp'：请在终端运行 pip install mcp。
如果提示 python: command not found：请检查你的 Python 是否安装在环境变量中，或者在 json 配置里把 "command": "python" 改为 Python 的绝对路径（例如 "E:\\Users\\think\\AppData\\Local\\Programs\\Python\\Python310\\python.exe"）。

你现在的插件面板里，tutor-skills 变绿了吗？

---
*从 Gemini 导出，2026-05*
