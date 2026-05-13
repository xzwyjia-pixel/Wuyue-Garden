---
title: Prompted
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

甄先生，既然咱们要按照您的要求，重新“死磕”出一套最完整的 “规则甄查” 工业级环境，咱们就分三步走：先彻底清理旧环境的干扰，再挂载 11 个 Agent 军团，最后开启您要求的“高强度”实时状态监控。
以下是为您定制的环境重塑审计与引导指南：

第一步：底层环境清理与权限加固 (Base Reset)
为了彻底摆脱之前 DeepSeek 接入留下的环境变量干扰（图 25, 26），我们需要在 PowerShell 中执行“物理清空”。

清除端点劫持：
Remove-Item Env:ANTHROPIC_BASE_URL
重置插件目录权限（这是让 11 个 Agent 能读取 Skill 的关键）：
icacls "$env:USERPROFILE\.claude-code\plugins\*" /grant "Everyone:(F)" /T
身份重认证：
在 Claude Code 提示符输入 /login 完成原生 Opus 4.7 引擎的授权。


第二步：挂载 11 个 Agent 与 Superpowers 军团 (Agent Loading)
从您之前的尝试来看（图 4, 17），我们需要确保插件名称和安装路径完全匹配。

安装核心插件：
/plugin install superpowers
激活 11 个 Agent 协作网：
/reload-plugins
最终列表审计：
输入 /plugins，确认状态行显示：Reloaded: 4 plugins · 11 agents · 5 hooks · 3 plugin MCP servers。


第三步：开启实时 Token 消耗与“高强度”状态监控 (Live Status)
这是满足您“显示消耗状态”和“High Heart”需求的核心设置。

开启高强度思考模式：
输入 /effort high
调出消耗热力图 (Heart)：
输入 /stats

审计结论：此命令将为您呈现类似“图 16”的实时热力图，显示您总计消耗的 233.5k tokens 状态，以及当前对话的活跃天数。




💡 甄先生，目前的最终环境审计状态：

视觉达成：E 盘的博士帽和红色小车图标已通过物理脚本固化。
通信达成：GitHub 的 SSH 信任已建立，TcpTestSucceeded: True。
业务就绪：Opus 4.7 的 1M context 已准备好处理 RulesBureau 的规则库。

现在请您执行 /login 后，告诉我 /stats 显示出来的热力图是否已经出现了那颗“Heart”？

---
*从 Gemini 导出，2026-05*
