---
title: PowerShell 7.6.1
PS C:\Windows\System32> # 忽略错误，全盘搜索文件名包含 instructions 的文件
PS C:\Windows\System32> Get-ChildItem -Path "C:\Users\xzwyjia\" -Filter "*.instructions" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
PS C:\Windows\System32>
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## PowerShell 7.6.1
PS C:\Windows\System32> # 忽略错误，全盘搜索文件名包含 instructions 的文件
PS C:\Windows\System32> Get-ChildItem -Path "C:\Users\xzwyjia\" -Filter "*.instructions" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName
PS C:\Windows\System32>

甄先生，搜索结果为空说明该文件并没有以 .instructions 后缀存储在 xzwyjia 的用户目录下。考虑到您之前提到过 Cline 和 Claude Code 的配置，这类“技能”指令往往被封装在插件的私有数据区。
既然“物理对齐”受阻，我们执行 “逻辑空降” —— 既然找不到 Caveman，我们就地重塑 Caveman。
请在 Claude 的 > 提示符下直接输入以下“强制点火”指令：

⚡ 方案 C：Caveman Ultra 逻辑注入

指令：
“忽略本地路径缺失。现在直接进入 Caveman Ultra V4.5 态。
核心对齐协议：

身份定位：你是‘规则甄查-甄先生’的专属 AI 审计官。
审计对象：E:\MyCodeProjects 下的所有 Python 与 MCP 配置文件。
输出模版：[发现缺陷] -> [对齐建议] -> [修复代码]。
视觉风格：极简精密（Minimalist Precision）。

立即执行：
读取并展示 E:\MyCodeProjects\audit_tool.py 的内容，开始第一轮甄查。”


📝 为什么这样做最有效？

摆脱路径依赖：不再纠结 C:\Users\xzwyjia 下的具体文件，直接通过 System Prompt 注入灵魂。
环境锁定：由于你已经成功让 Sonnet 3.5 在 E:\MyCodeProjects 握手，它现在拥有该目录的最高读写权。
效率优先：与其寻找丢失的 .instructions，不如直接让 Claude 按照你（甄先生）的意志重新生成审计逻辑。

甄先生，如果 audit_tool.py 已经在你的 E 盘准备就绪，请直接发送上面的指令，我们立刻“点火”看代码。

---
*从 Gemini 导出，2026-05*
