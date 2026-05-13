---
title: Prompted
source: gemini
date: 2026-04-30
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

从最新的图片来看，您依然面临 Error: timed out waiting for server to start 的报错。这意味着虽然 Ollama 已经安装，但其后台引擎并未成功运行。
为了实现您 100% 免费开发 “规则甄查” Agent 的目标，我们需要彻底解决这个连接问题。

1. 核心排查：强制启动 Ollama 后台
请按照以下步骤操作，这是解决此报错最直接的方法：

手动启动服务模式：
在当前的 PowerShell 窗口中，输入并运行：
ollama serve
观察反馈：

如果没有任何报错，且窗口没有返回新的输入行，说明后台服务已启动。请保持这个窗口开启，不要关闭它。
如果报错“Address already in use”，说明服务其实在运行，只是卡住了。请打开任务管理器，找到所有名为 ollama 的进程并“结束任务”，然后再次尝试 ollama serve。


验证状态：
打开另一个新的 PowerShell 窗口，再次输入：
ollama list


2. 为什么这一步对您的“规则甄查”项目很重要？
您之前已经成功安装了 mcp 相关的 Python 依赖包，具备了开发 Skill 的技术基础。

本地化的优势：通过 Ollama 运行本地模型（如 Llama 3 或 Qwen），您可以让 Agent 扫描您收集的平台风险控制规则（Rules Detection），而无需将这些敏感的业务逻辑上传到云端。
成本控制：一旦 ollama list 正常工作，您在 Cline 插件中选择本地模型，整个开发和调试过程将不再消耗任何 API 费用。


3. 给“甄先生”的下一步行动指南
在解决了 Ollama 启动问题后，您的第一步开发任务应该是：

建立本地知识库：创建一个名为 rules.txt 的文件，输入一些您研究过的平台违规词或算法风险点。
配置 Cline 调用本地模型：

在 Cline (image_f11b84.png) 的设置中，将 Provider 切换为 Ollama。
确保 Base URL 指向 http://localhost:11434。


编写 Skill (MCP Server)：
让 Cline 帮您写一个简单的 Python 脚本，功能是：“读取 rules.txt 并比对输入的文案草稿”。

建议： 如果 ollama serve 依然无法启动，请尝试重启电脑。作为拥有丰富工业自动化经验的专业人士，您应该了解有时系统层面的进程冲突只能通过冷启动来解决。重启后，请先观察系统托盘是否有小羊驼图标，再尝试命令。

---
*从 Gemini 导出，2026-04*
