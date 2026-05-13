---
title: >> claude --model deepseek-chat
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  deepseek-chat with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> /status                                                                                                               
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   Status   Config   Usage   Stats

  Version:             2.1.133
  Session name:        /rename to add a name
  Session ID:          1e2a10e9-1238-4f25-8c9a-f9cec5e3a7bd
  cwd:                 C:\Windows\System32
  Auth token:          none                                                                                         …
  API key:             ANTHROPIC_API_KEY                                                                            …
  Anthropic base URL:  https://api.deepseek.com/v1

  Model:               deepseek-chat
  MCP servers:         3 failed · /mcp                                                                             …
  Setting sources:     User settings, Project local settings
  Esc to cancel
source: gemini
date: 2026-05-08
category: 编程开发
tags: [gemini, 编程开发]
---

## >> claude --model deepseek-chat
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  deepseek-chat with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

> /status                                                                                                               
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────   Status   Config   Usage   Stats

  Version:             2.1.133
  Session name:        /rename to add a name
  Session ID:          1e2a10e9-1238-4f25-8c9a-f9cec5e3a7bd
  cwd:                 C:\Windows\System32
  Auth token:          none                                                                                         …
  API key:             ANTHROPIC_API_KEY                                                                            …
  Anthropic base URL:  https://api.deepseek.com/v1

  Model:               deepseek-chat
  MCP servers:         3 failed · /mcp                                                                             …
  Setting sources:     User settings, Project local settings
  Esc to cancel

从你提供的终端状态输出来看，这套“混血”环境配置非常有意思，但也存在几个明显的风险点和待优化项。
你目前正在使用 Claude Code 作为命令行界面（CLI），但底层逻辑切换到了 DeepSeek 的 API，并且运行在 Windows 系统目录下。
以下是针对当前环境的详细核实与建议：
1. 核心风险：工作目录 (cwd) 权限

当前路径： C:\Windows\System32
警示： 这是系统核心目录。在这种路径下运行 AI 自动编程工具（如 Claude Code）非常危险。AI 可能会尝试创建临时文件、修改脚本或索引目录，这可能触发系统权限错误（EPERM）或意外损坏系统文件。
建议： 立即切换到你的项目目录，例如 D:\Projects\RulesInvestigation。

2. 模型适配：DeepSeek 替代 Claude

配置核实： 你通过 --model deepseek-chat 并修改 base URL 成功实现了用 DeepSeek 引擎驱动 Claude Code。
性能表现：

优势： deepseek-chat (V3/R1) 的性价比极高，且在中文逻辑理解上表现优异。
潜在问题： Claude Code 的某些高级功能（如特定的提示词优化和多模态工具调用）是针对 Anthropic 的原生模型优化的。在使用 DeepSeek 时，可能会出现工具调用（Tool Use）不稳定或格式解析错误。


核实： 如果发现 /mcp 无法正常唤起，可能需要检查 DeepSeek 的 API 是否完整支持 Function Calling。

3. MCP Server 故障排查

状态显示： 3 failed
原因分析：

协议不匹配： 某些为 Claude 原生设计的 MCP Server 可能无法完美适配 DeepSeek 的流式输出。
Windows 路径问题： 在 Windows 环境下，claude_desktop_config.json 中的命令（如 npx 或 python）如果没有加入系统环境变量，或者路径含有空格，会导致加载失败。


核实建议： 输入 /mcp 查看具体是哪三个服务器报错。通常需要确保 node 和 python 环境在当前终端可用。

4. 身份与令牌 (Auth Token)

状态： Auth token: none
说明： 因为你使用的是 DeepSeek 的 API Key 模式，所以 Anthropic 的官方身份认证显示为 none 是正常的，但这意味着你无法使用 Claude 的官方云端同步功能。


下一步操作建议：

迁移目录： cd /d D:\你的开发路径。
修复 MCP： 运行 /mcp，重点检查 audit_tool.py 相关的本地服务器是否在列表中。
压力测试： 尝试运行一个简单的规则审计指令，观察 DeepSeek 在“high effort”模式下对代码上下文的理解是否准确。

如果你需要调整具体的 claude_desktop_config.json 来修复那 3 个失败的服务器，可以把配置发给我帮你看看。目前这个“Claude 外壳 + DeepSeek 核心”的配置，在处理大规模工业自动化逻辑时，确实能节省不少成本。

---
*从 Gemini 导出，2026-05*
