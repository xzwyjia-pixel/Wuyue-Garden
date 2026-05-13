---
title: Prompted
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

这个截图显示的是 Claude Code（Anthropic 推出的命令行界面工具）的终端界面。
根据图片内容，这里有几个关键点和操作建议：
1. 当前状态分析

尝试执行未知命令：你输入了 /superpowers，但系统返回 Unknown command。这说明该命令不属于 Claude Code 的标准命令集。
正在进行登录操作：你输入了 /login，系统正在尝试进行身份验证。
浏览器未自动打开：通常 /login 会自动唤起浏览器，但截图中显示它提供了一个长 URL 链接，提示“Browser didn't open? Use the url below...”。

2. 你接下来需要执行的操作
如果你想完成登录并开始使用，请按照以下步骤操作：

复制链接：选中终端中那段以 https://platform.claude.ai/oauth/... 开头的长链接并复制。
手动访问：在你的浏览器（如 Chrome、Edge）中粘贴并打开该链接。
授权登录：在网页端登录你的 Anthropic 账号并点击授权。
输入验证码（如果提示）：网页授权成功后，可能会显示一段验证码（Verification Code）。回到终端，在 Paste code here if prompted > 处粘贴该代码并按回车。

3. 常用命令参考
登录成功后，你可以尝试以下常用命令：

/init：在当前目录下初始化 CLAUDE.md 文件，用于配置项目的特定指令。
/help：查看所有可用的命令列表。
直接输入问题：例如 Explain the code in this directory，它会扫描你的本地文件并给出回答。

如果你是想使用类似于“超级能力”的功能，通常是通过在 .md 文件中定义复杂的 System Prompt 或任务目标来实现的，而不是通过 /superpowers 命令。

---
*从 Gemini 导出，2026-05*
