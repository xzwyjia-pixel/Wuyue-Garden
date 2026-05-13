---
title: Prompted
source: gemini
date: 2026-05-07
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## Prompted

太棒了！现在你已经成功“进门”了，进入了 Claude Code 的运行环境（看到那个 > 提示符了吗？那就是它在等你下令）。
不过，在执行安装之前，从截图右下角看到一个关键状态：Not logged in · Run /login。
现在的操作步骤
请严格按照以下顺序在当前的 > 提示符后输入：


先登录：
输入并回车：
/login

这会打开浏览器让你授权你的 Anthropic 账号。登录成功后回到这个窗口。


执行安装：
登录完成后，再次在 > 提示符后输入：
/plugin install superpowers@claude-plugins-official




⚠️ 可能遇到的“坑”
如果输入 /plugin 后它还是报错或者提示找不到这个命令，可能是因为 Claude Code 的版本或配置 问题。
由于 Superpowers 本质上是一套 预设指令（Custom Instructions） 和工具集，如果 /plugin 这种自动化安装方式在你的版本里没反应，你还有一个“手动模式”：
手动注入法：

在你的项目根目录下创建一个名为 CLAUDE.md 的文件（正如你截图里的 Tips 建议的那样）。
将 Superpowers 的规则配置直接粘贴进去。

为什么推荐用它？
既然你已经在用 Sonnet 4.6（截图中显示的最新版），配合 Superpowers 的 Agentic Workflow（代理工作流），它会比普通的 Claude 更有“主见”。它不会直接甩给你一堆代码，而是会先问你：“我们要实现什么？测试用例是什么？”
这非常符合你对“精密”和“规则”的追求。登录遇到问题随时告诉我！

---
*从 Gemini 导出，2026-05*
