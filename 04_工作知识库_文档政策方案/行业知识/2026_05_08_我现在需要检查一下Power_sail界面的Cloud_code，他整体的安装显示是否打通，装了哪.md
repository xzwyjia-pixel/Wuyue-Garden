---
title: 我现在需要检查一下Power sail界面的Cloud code，他整体的安装显示是否打通，装了哪些插件，装了哪些skills有没有装agent，我现在需要对我昨天到现在的所有的操作做一个详细的梳理。 请告诉我用什么命令。 如何检测？ 我需要重新处理一下这个。 整体环境。
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## 我现在需要检查一下Power sail界面的Cloud code，他整体的安装显示是否打通，装了哪些插件，装了哪些skills有没有装agent，我现在需要对我昨天到现在的所有的操作做一个详细的梳理。 请告诉我用什么命令。 如何检测？ 我需要重新处理一下这个。 整体环境。

理解您的意图。既然您在使用 Claude Code 并希望梳理从昨天到现在的环境搭建进度，我们需要针对它的多层架构（CLI 核心、MCP 服务器、Plugins、Skills）逐一排查。
由于截图中显示了频繁的 504 Gateway Time-out（网关超时），这通常意味着本地 CLI 与 Cloudflare 节点之间的连接不畅。这种情况下，我们需要先确认本地服务是否已经就绪。
以下是在 PowerShell 界面中进行“深度体检”和“历史梳理”的具体命令：

1. 核心状态自检 (Check the Foundation)
首先要查看 Claude Code 识别到的环境全貌：


查看当前已安装的组件：
/stats


目的： 这是一个总览命令。它会列出当前的 plugins, skills, agents, 以及 MCP servers 的数量。如果这里的数字全是 0，说明之前的安装因网络超时并未真正生效。



查看插件详细列表：
/reload-plugins


目的： 如您截图中执行的那样，它不仅会重载，还会详细列出目前活跃的组件。请重点检查 "0 agents" 和 "0 plugin MCP servers" 这两行。如果显示为 0，说明 caveman 等插件虽然添加了，但并未成功挂载。




2. 梳理历史操作 (Audit the Session)
要回顾从昨天到现在的操作轨迹，可以使用这个“回溯”命令：

查看操作历史：
/history


目的： 它会列出您在当前会话或最近会话中输入的所有命令。通过这个列表，您可以确认哪些 plugininstall 命令成功了，哪些因为 504 失败了。




3. MCP 服务与 Agent 检测 (Advanced Audit)
如果您在折腾 "规则甄查" 项目，MCP 服务器是核心。

检查 MCP 链接状态：
/mcp-status


目的： 确认您的本地模型（如 Ollama）或自定义的 Python 审计工具是否已经作为 MCP 服务器挂载。




4. 针对截图中的 Error 504 进行修复
从您的截图中看，caveman 插件处于一个尴尬的状态：已添加（Added），但无法执行命令（Unknown command）。这正是因为网络超时导致下载不完整。
建议的重新处理步骤：


彻底清除缓存（针对连接问题）：
/compact


这会清理上下文，减少同步压力。



强制重新安装（建议在网络较好或挂代理时操作）：
/plugin remove caveman
/plugin add JuliusBrussee/caveman
/plugin install caveman@caveman



检查本地 Python 环境：
因为您的“视觉化”和“规则侦查”依赖 Python，请在终端输入：
python --version
pip list


确认 requests 和 Pillow（用于处理图标）是否在列表中。




梳理建议清单 (Audit Checklist)
请执行完上述命令后，对照以下清单告诉我：

/stats 命令返回的 Agents 和 MCP servers 数量各是多少？
/history 中是否显示有成功的 "Successfully installed" 记录，还是大部分都是 "API Error 504"？
您的 E 盘视觉化 脚本是否已经作为一个本地技能（Skill）被 Claude Code 识别？

如果您想让我帮您写一个一键体检脚本（输出一个完整的环境报告），请告诉我，我会为您编写一个 .ps1 文件。

---
*从 Gemini 导出，2026-05*
