---
title: Prompted
source: gemini
date: 2026-05-08
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

甄先生，既然您已经充值成功（图 31 确认 100 元到账）且 API Key 显示为启用状态（图 32），但 Claude Code 依然报 403 权限错误，这说明我们正面临一个典型的“API 协议兼容性”阻碍。
在 DeepSeek 这种提供 OpenAI 兼容接口的平台上，并没有类似“勾选框”的显式模型开关。权限是默认全开的。目前的报错通常是因为 Claude Code 发送的某些 Header（报头）或特定的工具调用（Tool Use）协议与 DeepSeek 的 V1 转发层产生了冲突。
为了不让这些技术杂音耽误您的“规则甄查”实战，我为您准备了两套“死磕”方案，咱们直接破局：
方案一：强行通过“备用标识符”重定向（DeepSeek 优先）
有时候 deepseek-chat 这个名字在第三方代理中会被过滤，咱们换一个更底层的路径。请在 PowerShell 中按顺序执行：

彻底清除缓存的环境变量：
Remove-Item Env:ANTHROPIC_BASE_URL; Remove-Item Env:ANTHROPIC_API_KEY
注入新的端点（注意去掉 v1，有时直接使用根路径更稳）：
$env:ANTHROPIC_BASE_URL="https://api.deepseek.com"
$env:ANTHROPIC_API_KEY="sk-c8cf2fa5efc44b29b84f4ef6a7b9706e"
启动！尝试使用这个具体的 V4 推理标识符：
claude --model deepseek-reasoner


方案二：回归“原生 Opus”并行（最稳妥实战方案）
甄先生，您在图 28 中已经回到了 Opus 4.7 状态，但卡在了 403 Request not allowed。这不是 DeepSeek 的问题，而是 Anthropic 官方在检测到频繁切换 API 后触发的安全保护。
操作建议：

在 Claude Code 里输入 /login：这会打开浏览器让你重新授权官方账号。
让 Opus 4.7（1M 窗口）先干活：既然您已经充值了 DeepSeek，我们可以把 DeepSeek 作为“规则提取分析仪”，而用 Opus 4.7 作为“全案总设计师”。


💡 关键审计结论：
从您的截图 31 和 32 来看，您的 DeepSeek 账户没有任何问题。现在的核心问题是 Claude Code 客户端与 DeepSeek 服务器之间的“握手协议”不匹配。
甄先生，为了让实战尽快落地，我建议咱们现在：

执行 /login 恢复 Opus 4.7 的访问（它处理复杂本地文件 audit_tool.py 的能力最强）。
等环境稳定后，我教您如何编写一个简单的 Python 脚本，让您可以直接调用您刚充值的 100 元 DeepSeek 额度，专门处理 E:\RulesBureau 里的海量视频规则。

您看是先通过 /login 把 Claude 唤醒，还是咱们继续尝试在 PowerShell 里调整 DeepSeek 的连接参数？

---
*从 Gemini 导出，2026-05*
