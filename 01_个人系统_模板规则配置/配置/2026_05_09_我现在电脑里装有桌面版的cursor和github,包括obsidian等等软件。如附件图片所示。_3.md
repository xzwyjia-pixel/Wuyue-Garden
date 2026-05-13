---
title: 我现在电脑里装有桌面版的cursor和github,包括obsidian等等软件。如附件图片所示。我如何把DeepSeek直连模式下的Claude code与他们形成无缝连接。
source: gemini
date: 2026-05-09
category: Obsidian配置
tags: [gemini, Obsidian配置]
---

## 我现在电脑里装有桌面版的cursor和github,包括obsidian等等软件。如附件图片所示。我如何把DeepSeek直连模式下的Claude code与他们形成无缝连接。

要将处于 DeepSeek 直连模式 的 Claude Code 与你电脑上的 Cursor、GitHub 以及 Obsidian 形成无缝连接，核心逻辑是利用 E:\MyCodeProjects 作为所有工具共享的“神经中枢”。
由于你已经通过 /init 建立了项目规范，现在的环境已经非常适合进行多端联动。以下是具体的操作方案：
1. 与 Cursor 的深度联动：双脑协同
你现在的 ThinkPad P15V 已经同时拥有了 Cursor（图形化 AI 编辑器）和 Claude Code（终端命令行 AI）。

共享上下文：在 Cursor 中打开 E:\MyCodeProjects 目录。
分工合作：

Cursor 用于大面积的代码编写、UI 设计和实时视觉预览。
Claude Code (直连模式) 用于执行复杂的 MCP 审计逻辑 (mcp_audit_server.py) 和处理耗费 Token 的长文档规则分析。


同步感知：由于两者操作的是同一套物理文件，你在 Claude Code 中运行 /init 生成的 CLAUDE.md，会被 Cursor 的索引功能直接读取，让 Cursor 也瞬间理解你的项目架构。


2. 与 Obsidian 的联动：打造“规则甄查”知识库
你的 Obsidian 笔记可以成为你“规则甄查”品牌的策略大脑。

建立软链接：将你的 Obsidian 仓库（Vault）中的某个文件夹通过 Windows 软链接（mklink）指向 E:\MyCodeProjects\docs。
自动化文档：

你在 Claude Code 中生成的审计报告（如 Audit_Report_HHMMSS.json 或 Markdown 报告）可以直接保存到该目录下。
这样你无需移动文件，就可以在 Obsidian 中利用其强大的双链功能对不同平台的合规策略进行复盘。




3. 与 GitHub 的联动：版本管理与自动化
你在任务栏中已经安装了 GitHub 相关工具，这可以确保你的“规则甄查”系统资产安全。

资产保护：在 E:\MyCodeProjects 目录下运行 git init。
终端提效：在 Claude Code 直连模式下，你可以直接通过自然语言命令 AI 提交代码，例如：

> "请帮我把刚才优化的规则矩阵 (rules.json) 提交到 GitHub，并写一段关于 v2.0 双向导航逻辑的提交信息。"




4. 关键配置：打通 MCP 通道
要让这些软件真正“无缝”，你需要发挥你已经配好的 MCP 审计服务器 的威力：

跨软件调用：你可以将 mcp_audit_server.py 的路径配置到你的 Claude Desktop 或其他支持 MCP 的软件设置中。
直连优势：无论你从哪个软件调用这个 MCP 工具，它底层都会走你刚刚配好的 DeepSeek 直连链路，既省钱又快速。


建议的操作步骤：

在 Cursor 中打开项目：确保右下角的索引已完成，它会自动发现你的 CLAUDE.md。
设置自动化命令：在 Claude Code 终端中尝试让它读取你 Obsidian 里的规则草稿，并将其转化为 rules.json 中的结构化数据。
消除 Warning 隐患：为了让跨软件通信更安全，建议在你的直连脚本中尝试将安全校验恢复（设置为 1），确保各软件间的 HTTPS 请求不报红字。

你目前在 ThinkPad P15V 上的这套组合方案，已经具备了极强的生产力。你现在想先尝试让 Claude Code 帮你在 Obsidian 里生成一份最新的审计报告模版吗？

---
*从 Gemini 导出，2026-05*
