---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> npm install -g @claudecode/everything-claude-code && \
所在位置 行:1 字符: 51
+ npm install -g @claudecode/everything-claude-code && \
+                                                   ~~
标记“&&”不是此版本中的有效语句分隔符。
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : InvalidEndOfLine

PS C:\Users\think> npx gsd-ai@latest init && \
所在位置 行:1 字符: 24
+ npx gsd-ai@latest init && \
+                        ~~
标记“&&”不是此版本中的有效语句分隔符。
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : InvalidEndOfLine

PS C:\Users\think> npx hermes-code@latest setup && \
所在位置 行:1 字符: 30
+ npx hermes-code@latest setup && \
+                              ~~
标记“&&”不是此版本中的有效语句分隔符。
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : InvalidEndOfLine

PS C:\Users\think> npx openspec@latest init
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> npm install -g @claudecode/everything-claude-code && \
所在位置 行:1 字符: 51
+ npm install -g @claudecode/everything-claude-code && \
+                                                   ~~
标记“&&”不是此版本中的有效语句分隔符。
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : InvalidEndOfLine

PS C:\Users\think> npx gsd-ai@latest init && \
所在位置 行:1 字符: 24
+ npx gsd-ai@latest init && \
+                        ~~
标记“&&”不是此版本中的有效语句分隔符。
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : InvalidEndOfLine

PS C:\Users\think> npx hermes-code@latest setup && \
所在位置 行:1 字符: 30
+ npx hermes-code@latest setup && \
+                              ~~
标记“&&”不是此版本中的有效语句分隔符。
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : InvalidEndOfLine

PS C:\Users\think> npx openspec@latest init

这是因为你使用的是 Windows 默认的 PowerShell（旧版本 5.1），它不识别 Linux 风格的 &&（连接符）和 \（换行符）。
在旧版 PowerShell 中，分号 ; 才是正确的命令分隔符。
为了让你一次性成功，请直接复制下面这段专门为 Windows PowerShell 调整过的命令：
npm install -g @claudecode/everything-claude-code; npx gsd-ai@latest init; npx hermes-code@latest setup; npx openspec@latest init

为什么之前的会报错？

&&：在旧版 PowerShell 中代表“无效字符”。它只在最新的 PowerShell 7 或 CMD 中有效。
\：在 Linux 里是换行，但在 PowerShell 里它被理解为文件路径的斜杠，导致命令断开了。

执行建议：

逐个确认：因为 npx 命令在第一次运行时会询问 Need to install the following packages: ... (y)，请在看到提示时输入 y 并按回车。
管理员权限：确保你的 PowerShell 窗口标题显示有“管理员”，否则安装全局包（-g）可能会失败。

如果安装后提示“找不到命令”：
请关闭当前的 PowerShell 窗口，重新打开一个新的。这是为了让系统刷新环境变量，识别刚刚安装到 C 盘的 ecc、gsd 等工具。

---
*从 Gemini 导出，2026-05*
