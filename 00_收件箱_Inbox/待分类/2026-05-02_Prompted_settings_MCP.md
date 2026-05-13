---
title: Prompted
source: gemini
date: 2026-05-02
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## Prompted

从 image_04c658.png 可以看到，虽然你已经在 cline_mcp_settings.json 中写好了配置，但当前的 Agent Customizations 窗口显示 "No MCP servers configured"。
这通常是因为配置文件的存放位置或者加载状态不对。咱们临门一脚，按以下步骤排查：
1. 检查文件的“保存”状态
观察 image_04c658.png 背景中的 cline_mcp_settings.json 标签页。如果文件名旁边有一个小白圆点，说明文件还没保存。

操作：按下 Ctrl + S 确保文件已保存到硬盘。

2. 核心问题：配置文件路径是否正确？
截图显示你的文件路径是：
C:\Users\think\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
关键点：你目前使用的 AI 助手可能不是 Cline，而是另一个支持 MCP 的插件（例如 Roo Code 或其他自定义 Agent 窗口）。不同的插件读取的配置文件路径是不同的。

如果是 Roo Code：它的配置文件通常在 ...\roovet.roo-code\settings\roo_mcp_settings.json。
如果是 VS Code 原生支持：它可能在寻找 .../User/globalStorage/mcp-servers.json。

3. 强制刷新加载
在 image_04c658.png 的窗口中：

点击右上角的 "+" (Add) 按钮试试，看它是否允许你手动指定刚才创建的 tutor_server.py。
或者重启 VS Code。很多时候，MCP 配置文件只有在插件初始化时才会被读取。

4. 检查日志（排查语法错误）
如果 JSON 里多了一个逗号或者少了一个括号，插件会直接忽略整个文件。

操作：在 VS Code 底部面板点击 Output，在下拉框里找 "Cline" 或 "MCP" 开头的通道，看有没有类似 Failed to parse MCP settings 的报错。


建议尝试
既然你已经成功创建了 E:\MCP-Skills\tutor_server.py，如果上述自动加载一直不成功，最暴力的解决办法是：

点击 image_04c658.png 窗口右侧的 "Browse Marketplace" 旁边的 "+" 号。
看看是否可以直接通过界面填写：

Name: tutor-skills
Command: python
Args: E:\MCP-Skills\tutor_server.py



甄先生，一旦这个列表里出现了 tutor-skills，你的 AI 导师就正式“入职”了。你现在重启一下 VS Code 看看列表更新了吗？

---
*从 Gemini 导出，2026-05*
