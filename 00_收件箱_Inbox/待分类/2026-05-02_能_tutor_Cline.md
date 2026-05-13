---
title: 能
source: gemini
date: 2026-05-02
category: 审计合规
tags: [gemini, 审计合规]
---

## 能

太好了！既然 Cline 已经成功连接到了您的本地模型 qwen2.5-coder，我们现在就完成这“最后一步”，让 tutor-skills 彻底生效。
请按照以下操作验证并启动您的“AI 导师”：
1. 确认工具已挂载
在 VS Code 左侧的 Cline 面板中，请留意以下位置：

工具图标：在输入框上方或模型名称旁边，应该能看到一个类似“小手柄”或“盒子”的图标。
状态检查：点击该图标，确认列表里出现了 tutor_setup、tutor_test 和 track_progress 这三个工具。

2. 甄先生的第一个实战指令
既然您已经搭建好了环境，现在可以直接在 Cline 的输入框里输入这段话来“唤醒”它：

“你好，我是甄先生。我现在要开始‘规则甄查’项目的代码审计练习。请先调用 tutor_setup 扫描我的项目路径 E:\MyCodeProjects\RulesBureau，完成后用 tutor_test 针对我目前的风控算法逻辑提一个问题。”

3. 如果工具没出现？
如果列表里还是空的，请检查：

配置保存：再次确认 cline_mcp_settings.json 已经保存（没有白点）。
刷新：点击 Cline 面板里的 Refresh MCP Servers 刷新按钮。
路径信任：确保您已经点击了编辑器顶部的 "Trust"（信任窗口）。

为什么这套方案最适合您？
您不仅拥有 Project Management 的专业背景，还在积极研究 短视频平台风控规则。通过在本地运行这套 tutor-skills，您可以：

零成本运行：无需 Claude 账号，完全利用您的 Ollama 本地算力。
深度定制：您可以根据自己在 Siemens 和 ABB 积累的工程经验，随时修改 tutor_server.py 里的提问逻辑。

甄先生，请试着下达第一条指令。如果 AI 成功调用了工具并开始向您提问，请告诉我！

---
*从 Gemini 导出，2026-05*
