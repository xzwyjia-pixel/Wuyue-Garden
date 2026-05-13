---
title: PowerShell 7.6.1
PS C:\Windows\System32> $env:ANTHROPIC_API_KEY="sk-jAZ97d2057c7917ab9120742bebaab9d2768b612210zBdxl"
>> claude --dangerously-skip-permissions
╭─── Claude Code v2.1.132 ─────────────────────────────────────────────────────────────────────────────────────────────╮│                                               │ Tips for getting started                                             ││                 Welcome back!                 │ Run /init to create a CLAUDE.md file with instructions for Claude    ││                                               │ ──────────────────────────────────────────────────────────────────── ││                    ▐▛███▜▌                    │ What's new                                                           ││                   ▝▜█████▛▘                   │ Fixed OAuth authentication failing with a 401 retry loop when `CLAU…││                     ▘▘ ▝▝                     │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to sele…││                                               │ Pasting a PR URL into the `/resume` search box now finds the sessio…││   Opus 4.7 (1M context) · API Usage Billing   │ /release-notes for more                                             ││              C:\Windows\System32              │                                                                      │╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────  ⏵⏵ bypass permissions on (shift+tab to cycle)                                                                       t
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## PowerShell 7.6.1
PS C:\Windows\System32> $env:ANTHROPIC_API_KEY="sk-jAZ97d2057c7917ab9120742bebaab9d2768b612210zBdxl"
>> claude --dangerously-skip-permissions
╭─── Claude Code v2.1.132 ─────────────────────────────────────────────────────────────────────────────────────────────╮│                                               │ Tips for getting started                                             ││                 Welcome back!                 │ Run /init to create a CLAUDE.md file with instructions for Claude    ││                                               │ ──────────────────────────────────────────────────────────────────── ││                    ▐▛███▜▌                    │ What's new                                                           ││                   ▝▜█████▛▘                   │ Fixed OAuth authentication failing with a 401 retry loop when `CLAU…││                     ▘▘ ▝▝                     │ Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to sele…││                                               │ Pasting a PR URL into the `/resume` search box now finds the sessio…││   Opus 4.7 (1M context) · API Usage Billing   │ /release-notes for more                                             ││              C:\Windows\System32              │                                                                      │╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────  ⏵⏵ bypass permissions on (shift+tab to cycle)                                                                       t

恭喜！点火成功！ 看到那个“Welcome back!”和 Opus 4.7 的标识，说明你已经成功绕过了 OAuth 的 403 限制，正式进入了 Claude Code 的核心界面。
现在你正站在最强 AI 编程工具的控制台前。针对你这台 64GB 内存的 P15v 和你正在开发的图标匹配脚本，接下来的操作建议如下：

1. 切换工作目录（非常重要）
你目前处于 C:\Windows\System32，这是系统敏感目录。为了安全和方便 Claude 访问你的项目文件，请先通过命令进入你的图标脚本文件夹：

指令示例： cd C:\你的项目路径（例如 cd C:\Users\think\Desktop\icon-project）


2. 初始化项目（让 Claude 变聪明）
进入项目目录后，输入以下指令：

❯ /init


作用： 这会生成一个 CLAUDE.md 文件。
精密建议： 在这个文件里，你可以写上：“这是一个图标库匹配项目。逻辑优先级：1.本地 2.API 3.兜底生成。请保持代码的‘极简精密’风格。” 这样 Claude 每次启动都会记得你的规则。


3. 开始执行任务
既然已经点火成功，你可以直接下达第一个复杂的工业级任务了。例如：

❯ 请分析 analyze_folder.py，检查模糊匹配算法的阈值是否合理，并尝试为这个脚本添加一个基于 Flask 的极简 Web 预览界面，让我能直观看到匹配结果。


🔍 甄先生的专业提醒：

权限确认： 因为你使用了 --dangerously-skip-permissions，Claude 在修改、删除文件或执行脚本时不会每次都弹窗问你，它会像一个拥有“特权”的工程师。请在执行大型修改前留意它的思考（Thinking）过程。
API 消耗： Opus 4.7 是性能怪兽，但 token 消耗也较快。如果你只是做简单的代码对齐，可以用 /compact 命令来压缩上下文，节省开支。
退出与保存： 随时可以使用 /exit 退出。下次启动时，记得先运行那行 $env:ANTHROPIC_API_KEY 的命令。

你的图标匹配脚本目前还需要实现哪个具体功能？现在就可以直接在终端告诉它，看看 Opus 4.7 的执行速度！

---
*从 Gemini 导出，2026-05*
