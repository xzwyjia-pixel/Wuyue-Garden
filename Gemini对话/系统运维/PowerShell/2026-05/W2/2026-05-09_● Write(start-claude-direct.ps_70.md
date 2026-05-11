---
title: ● Write(start-claude-direct.ps1)
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## ● Write(start-claude-direct.ps1)

## ● Write(start-claude-direct.ps1)
  ⎿  Added 1 line, removed 1 line
       8
       9  Write-Host ">>> 正在尝试直连 DeepSeek 官网 - 高性能模式" -ForegroundColor Green
      10
      11 -claude
      11 +cmd.exe /c "claude"

● Task 2.1 完成。

  两个脚本末行均改为 cmd.exe /c "claude"，所有变量保留原值不变。下次双击或 PowerShell 运行，走 cmd 解析 npm 路径，规避
  PowerShell 的 PATH 兼容问题。

✻ Worked for 2m 38s

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Press Ctrl-C again to exit

Resume this session with:
claude --resume 9ed76546-d968-4812-b12a-6c3f6786fa33
PS E:\MyCodeProjects> .\start-claude-direct.ps1
>>> 正在尝试直连 DeepSeek 官网 - 高性能模式
'"C:\Users\think\AppData\Roaming\npm\\node_modules\@anthropic-ai\claude-code\bin\claude.exe"' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
PS E:\MyCodeProjects>

看来在切换到直连模式时，系统报了一个典型的路径解析错误。报错信息显示：'"C:\Users\think\AppData\Roaming\npm\\node_modules\@anthropic-ai\claude-code\bin\claude.exe"' 无法被识别。
这通常是由于 cmd.exe /c 在处理带有空格或特殊字符（如 @ 符号）的复杂长路径时，对双引号的嵌套解析出现了偏差。由于你的用户名文件夹包含在 C:\Users\think\ 下，且路径中存在双斜杠 \\ 和 @ 符号，CMD 没能正确“吃掉”这段路径。
处方建议：针对性调整脚本
既然你使用的是 ThinkPad P15V 这种专业开发设备，我们用更稳健的“绝对路径转义”方式来修复 start-claude-direct.ps1。
请尝试将脚本末行修改为以下两种方案之一：
方案 A：简化引用（推荐）
直接调用 claude 命令，让系统通过 PATH 自动寻找，而不是写死那个复杂的长路径：
# 将原来的末行改为：
cmd.exe /c "claude"


理由：既然你已经通过 npm 全局安装了 Claude Code，claude 本身就是一个可执行的入口，不需要手动指向 node_modules 内部的具体 .exe。

方案 B：修复双引号嵌套
如果你必须指向那个具体的 .exe 文件，请确保双引号的使用符合 CMD 的规范：
# 使用这种嵌套方式：
cmd.exe /c `""C:\Users\think\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"`"


验证步骤

修改脚本：建议先试 方案 A，因为它最符合你追求的“极简精准”审美。
清理进程：建议先关闭当前的 VS Code 终端。
重新运行：在 E:\MyCodeProjects 目录下再次执行 .\start-claude-direct.ps1。

一旦成功，你会直接进入 DeepSeek 直连环境。这对于你后续频繁调试 MCP 审计服务器 来说，能省下大量的中转 Token 消耗。
如果运行后依然提示找不到命令，请在终端输入 npm list -g --depth=0 确认一下 Claude Code 是否确实安装在当前用户的 npm 路径下。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
