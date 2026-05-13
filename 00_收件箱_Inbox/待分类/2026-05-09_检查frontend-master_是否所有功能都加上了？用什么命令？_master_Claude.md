---
title: 检查frontend-master 是否所有功能都加上了？用什么命令？
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## 检查frontend-master 是否所有功能都加上了？用什么命令？

在 Claude Code 界面下，你可以直接使用内置指令来检查当前加载的所有工具及其详细功能。
请在 Claude Code 的输入框（即 > 符号后面）执行以下操作：
1. 查看工具列表（快速检查）
输入并回车：
/tools

这个命令会列出所有当前可用的 MCP 工具。请在列表中找到 frontend-master，看它下方列出了几个功能项。

2. 查看详细功能描述（确认是否为 4 个）
如果你想确认具体是哪 4 个功能，可以直接问 Claude：

“详细列出 frontend-master 技能的所有工具函数，并确认总数。”

正常情况下，frontend-master 应该包含类似以下的功能（具体名称可能随版本变化）：

视觉/样式分析 (Visual Analysis)
UI 代码生成 (UI Generation)
响应式修复 (Responsive Fix)
设计系统对齐 (Design System Alignment)


3. 如果发现还是只有 1 个功能，请执行此命令修复
如果 /tools 显示功能不全，通常是因为 dist 目录下的编译文件未更新。请在 PowerShell（不是 Claude Code 内部）执行：
# 进入技能目录
cd E:\ClaudeEnvironment\frontend-master

# 强制重新编译
npm run build

# 检查 package.json 确认入口
cat package.json | Select-String "main", "bin"

4. 验证翻译和 Markdown 技能
同理，执行 /tools 后，你应该能在列表中看到：

google-translate 或 translation
markdown-to-html

如果列表中完全没有这些名字：
说明 claude_desktop_config.json 里的路径写错了，或者你刚才的安装命令因为 404 根本没成功。你可以直接把 E:\ClaudeEnvironment 目录下的文件夹列表发给我，我帮你写出正确的配置文件内容。

---
*从 Gemini 导出，2026-05*
