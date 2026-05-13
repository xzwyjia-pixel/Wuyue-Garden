---
title: 我这边的token一直就没有消耗
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## 我这边的token一直就没有消耗

看到你的仪表盘截图，谜底终于揭开了：你的 Token 确实没有消耗，因为你的 Claude Code 压根没有连上这个 API 后台。
这解释了为什么你一直看到 401 Authentication Fails。这是一个典型的**“配置错位”**问题，对于追求“精密”的甄先生来说，我们需要做一次“物理层”的对齐。

1. 深度诊断：为什么 Token 没消耗？

Endpoint 没对齐：截图显示你使用的是 api.gptsapi.net（一个第三方 API 中转站），但 Claude Code 默认会去连接 Anthropic 的官方服务器 (api.anthropic.com)。
认证逻辑断层：即使你在控制台看到有 $4.90 的余额，由于 Claude Code 找不到这个非官方的“Base URL”，它拿着你的 Key 去敲官方的门，自然会被报 401（非法访问）。


2. 甄先生的“极简精密”修复方案
要让 Claude Code 识别你的中转 API，你需要强制修改它的 API 地址。请在 PowerShell 中执行以下两步：
第一步：设置自定义 API 节点（关键）
Claude Code 支持通过环境变量或配置来更改 Base URL。请在你的 PowerShell 里输入：
# 将 Claude Code 的连接点指向你的中转站
$env:ANTHROPIC_BASE_URL="https://api.gptsapi.net/v1"

第二步：重新登录并检查
# 重新输入你的那个结尾为 706e 的 Key
claude config set apiKey YOUR_FULL_KEY_HERE


3. 环境体检报告（修复后预期）

























维度现状修正后API 地址默认官方 (api.anthropic.com)自定义 (api.gptsapi.net)Token 消耗0 (因为连不上)开始正常计费401 报错持续弹出消失，进入精密处理状态

4. 甄先生的“实战逻辑”重启
一旦上面的环境变量设置成功，你再次进入 claude 之后，执行那个久违的指令：

“甄先生”要求： 既然 API 链路已打通，请立即读取 @audit_tool.py，生成我们的 rules.json。 我们要看到真正的 Token 在跑，看到真正的规则在落地。


💡 甄先生的特别提示：
由于你使用的是第三方中转 API，有些高级插件（如 superpowers）可能会因为中转站不支持某些特定 Header 而报错。建议： 如果还是报错，就先用最基础的模式生成文件，不要强行挂载复杂的子代理插件。
要不要先试着在 PS 里把 $env:ANTHROPIC_BASE_URL 改过来？这是让你的 $4.90 余额发挥作用的唯一办法。

---
*从 Gemini 导出，2026-05*
