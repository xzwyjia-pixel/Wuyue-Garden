---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 审计合规
tags: [gemini, 系统运维, PowerShell]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> claude --new-session
error: unknown option '--new-session'
PS C:\Windows\System32> cd E:\MyCodeProjects
PS E:\MyCodeProjects> claude --compact
error: unknown option '--compact'
PS E:\MyCodeProjects> claude config set skillListingBudgetFraction 0.05
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> config
  ⎿  Retrying in 18s · attempt 6/10

· Finagling… (20s)


  > “甄先生”要求：直接读取 @audit_tool.py，并在这个目录下帮我创建一个核心配置文件
    rules.json，定义三个风险等级：高风险（封号）、中风险（限流）、低风险（建议修改）。”
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> Press up to edit queued messages
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt

由于我们正在处理的是 v2.1.133 版本，这个版本在处理 config set 时如果直接在 PowerShell 里输入带空格的命令，有时会误触发交互模式，导致它再次陷入 Finagling...（钻研/调校）的重试泥潭。
你的指令已经排队（Queued）了，但现在 Agent 显然被“规则读取”和“配置写入”卡在了同步阶段。
1. 深度诊断：为什么还在 Retrying？

指令排队冲突：你刚才连续输入了 config set 和一段长指令。由于之前的 1% 限制还在生效，Claude 在尝试读取 @audit_tool.py 时，因为“不记得”如何使用高阶读取技能（Skill dropped），导致逻辑死锁。
路径权限：虽然在 E 盘，但如果 audit_tool.py 文件很大，Agent 会在 Finagling 阶段尝试建立索引，这非常消耗网络稳定性。


2. “甄先生”的精密复位方案（手动强制干预）
既然自动修改配置卡住了，我们直接用 PowerShell 原生力量 帮它把路铺平。请按以下步骤操作：
第一步：彻底杀掉卡死的进程
按 Ctrl + C 退出，然后在 PS 里执行：
stop-process -name "claude*" -Force

第二步：直接修改配置文件 (跳过 AI)
Claude Code 的配置文件通常位于：
%USERPROFILE%\.claude\settings.json（或者类似路径）。
与其让卡住的 AI 去改，不如你直接在 PowerShell 里用这一行强制覆盖配置：
# 如果路径正确，这一行能直接解决“超能力掉落”问题
claude config set skillListingBudgetFraction 0.05

如果执行完这行，它没有进入交互模式而是直接回到了 PS 提示符，说明设置成功了。
第三步：分步执行“甄先生”的指令
重新输入 claude 进入后，不要一次性给长指令。先做最简单的验证：

进入后检查：> /skills (看右下角是否还有 dropped 提示)。
如果没有提示了，输入：> !cat audit_tool.py (先用 shell 模式确保它能读到文件)。


3. “规则甄查”核心架构：rules.json 预览
一旦环境恢复，我会让 Claude 帮你生成如下精密结构的配置文件：
{
  "brand": "Rules Investigation - Mr. Zhen",
  "version": "1.0.0",
  "risk_levels": {
    "HIGH": {"action": "封号", "color": "RED", "weight": 1.0},
    "MEDIUM": {"action": "限流", "color": "ORANGE", "weight": 0.6},
    "LOW": {"action": "建议修改", "color": "YELLOW", "weight": 0.2}
  },
  "patterns": [
    {"text": "最*", "level": "HIGH", "reason": "违反广告法绝对化用语"}
  ]
}


💡 甄先生的特别提醒：
现在的 Finagling... 状态说明 Agent 正在尝试“钻营”一个它目前权限（Context 限制）够不着的逻辑。
请先退出，执行 stop-process。 我们先确保 skillListingBudgetFraction 真的变成了 0.05，否则你的 Superpowers 永远处于“断连”状态。
执行完 stop-process 后，请告诉我你再次输入 claude 时，右下角那行 5 skill descriptions dropped 是否消失了？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
