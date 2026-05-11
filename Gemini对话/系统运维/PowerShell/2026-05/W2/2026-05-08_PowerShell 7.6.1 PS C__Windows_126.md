---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> # 方案 A：最通用的短别名（最推荐）
>> claude --model claude-3-5-sonnet
>>
>> # 方案 B：如果 A 不行，尝试带版本但不带日期的 ID
>> claude --model claude-3-5-sonnet-v2
>>
>> # 方案 C：如果依然不行，尝试“最新稳定版”指向名
>> claude --model claude-3-5-sonnet-latest
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 3.5 · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> **“我是甄先生。握手成功。                                                                                              **“我是甄先生。握手成功。
                                                                                                                          请执行指令：ls C:\Users\think\.agents\skills                                                                                                                                                                                                   ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 3.5 · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> **“我是甄先生。握手成功。                                                                                            

  请执行指令：ls C:\Users\think\.agents\skills

  如果看到文件夹，请直接读取 C:\Users\think\.agents\skills\caveman\.instructions。

  告诉我你是否已准备好进入‘极简输出’状态。”**                                                                        

● There's an issue with the selected model (claude-3-5-sonnet). It may not exist or you may not have access to it. Run
  /model to pick a different model.

✻ Churned for 2s

> /config

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   Status   Config   Usage   Stats


  ╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
  │ ⌕ Search settings…                                                                                               │
  ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    Auto-compact                               true
    Show tips                                  true
    Reduce motion                              false
    Thinking mode                              true
    Session recap                              true
    Rewind code (checkpoints)                  true
    Verbose output                             false
    Terminal progress bar                      true
    Show turn duration                         true
    Default permission mode                    Default
    Worktree base ref                          fresh
    Respect .gitignore in file picker          true
    Skip the /copy picker                      false
    Auto-update channel                        latest
  ↓ 11 more below

  Type to filter · Enter/↓ to select · ↑ to tabs · Esc to clear

甄先生，这份配置单已经揭示了核心矛盾。您看底部的 “↓ 11 more below”，那里面藏着真正的模型 ID。
由于中转 API 的特殊性，即便界面显示是 Sonnet 3.5，但底层发送给 gptsapi.net 的字符串如果不对，对方就会直接拒收，导致 Claude 陷入“虽然醒了但动弹不得”的状态。
甄先生的“暴力对齐”审计步骤：
1. 挖掘被隐藏的 ID
请在当前 /config 界面，疯狂按向下键（↓），直到看到 primaryModel 或 model 这一项。

重点观察：它后面跟着的字符串到底是 claude-3-5-sonnet 还是带了 -20241022 这种后缀？
动作：如果您发现它显示为某个 ID，请按 Enter，它会进入编辑模式，尝试将其修改为 claude-3-5-sonnet（不带日期）。

2. 物理层面的“降维打击”
如果界面修改不生效，咱们直接去改它的“出厂设置”文件。请在 PowerShell 窗口输入：
# 1. 退出当前的 Claude (Ctrl+C)
# 2. 直接用记事本打开配置文件（这是最精密的操作）
notepad "$env:USERPROFILE\.claude-code-config.json"

在打开的文本里，请执行以下“审计修正”：

找到 "model": "..."。
将其修改为："model": "claude-3-5-sonnet"。
顺便检查是否有 "baseURL": 这一项，确保它精准指向 https://api.gptsapi.net/v1（注意末尾是否有 /v1）。
保存并退出记事本。


3. 甄先生的“阵地转移”
刚才的截图显示您仍在 C:\Windows\System32。在 Windows 的心脏地带操作，权限限制会导致 Claude 无法读取您的 .agents/skills。
启动前请务必先撤退到 E 盘：
cd E:\MyCodeProjects
# 然后再启动
claude


💡 甄先生的精密预判：
只要左下角的 ● There's an issue with the selected model 红色警告消失，变为绿色的模型名称，您的 Caveman 和 Superpowers 就会在您下达 ls 指令的一瞬间被激活。
甄先生，咱们是先通过键盘向下翻页找 ID，还是直接用记事本“手术”？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
