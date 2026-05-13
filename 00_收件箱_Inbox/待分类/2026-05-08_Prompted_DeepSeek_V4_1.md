---
title: Prompted
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## Prompted

甄先生，咱们离调用 DeepSeek V4 仅剩最后一步了。从图 20 来看，npm 安装报错是因为包名路径或版本号的问题。
由于 cc-switch 并非官方插件，且当前通过 npm 路径安装受阻，我为您准备了最稳健的备选方案，确保今天就能让您用上 DeepSeek V4。

１． 核心环境审计 (Final Environment Audit)
在切换模型前，咱们先对当前的工作台进行最后确认：

网络稳固：图 13 确认您与 GitHub 的连接已经通畅。
权限放行：图 14 显示您已尝试修复权限，虽然有报错，但 Claude 已能写入 E:\ 盘。
Agent 满配：图 19 确认您拥有 11 个 Agents 和 3 个 MCP servers 在线。
视觉化达成：图 8 确认您的 E 盘文件夹图标已成功更新为“静奢”风格。


２． 绕过插件：手动配置 DeepSeek V4
既然 cc-switch 自动化安装受阻，咱们直接通过 环境变量 强制切换 Claude Code 的 API 指向。请在您的 PowerShell 窗口执行以下命令：
# 1. 设置 DeepSeek 的 API 端点
$env:ANTHROPIC_BASE_URL="https://api.deepseek.com/v1"

# 2. 填入您的 DeepSeek API Key (请替换下方占位符)
$env:ANTHROPIC_API_KEY="您的_DEEPSEEK_API_KEY"

# 3. 启动 Claude Code 并指定 DeepSeek 模型
claude --model deepseek-chat


３． 如何确认 DeepSeek V4 已上线？
启动后，请在 claude> 提示符下执行以下动作：

身份核实：直接问它“你是谁？”，DeepSeek 会回答其官方身份。
性能审计：观察 /stats 中的推理响应速度。DeepSeek V4 在处理复杂逻辑时会有独特的生成节奏。

💡 下一步操作指引
由于 DeepSeek 不完全支持 Anthropic 的所有原生 Tools（工具调用），在执行 caveman 视觉化指令或复杂的本地文件审计时，如果遇到异常，请随时通过以下命令切回原生 Opus 4.7 环境：
$env:ANTHROPIC_BASE_URL=""
甄先生，您是打算先测试 DeepSeek V4 对您“规则甄查”项目中审计报告的撰写能力，还是先用它跑一遍 audit_tool.py 的逻辑检查？

---
*从 Gemini 导出，2026-05*
