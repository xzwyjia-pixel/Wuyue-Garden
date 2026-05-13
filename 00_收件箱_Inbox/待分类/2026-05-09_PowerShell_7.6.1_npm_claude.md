---
title: PowerShell 7.6.1
PS C:\Windows\System32> npm install -g @anthropic-ai/claude-code --force
npm warn using --force Recommended protections disabled.
\(node:14536) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

changed 2 packages in 4s
PS C:\Windows\System32>
source: gemini
date: 2026-05-09
category: 编程开发
tags: [gemini, 编程开发]
---

## PowerShell 7.6.1
PS C:\Windows\System32> npm install -g @anthropic-ai/claude-code --force
npm warn using --force Recommended protections disabled.
\(node:14536) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

changed 2 packages in 4s
PS C:\Windows\System32>

重装已经顺利完成。虽然终端出现了关于 NODE_TLS_REJECT_UNAUTHORIZED 的警告，但这通常是因为你之前的网络环境配置（比如为了适配中转通道或解决公司防火墙限制）调整了安全校验导致的。
目前 changed 2 packages 说明 npm 已经成功覆盖并修复了全局命令索引。
现在请按以下步骤执行，正式打通直连模式：
1. 切换到你的项目目录：
在 PowerShell 中输入：
cd E:\MyCodeProjects

2. 运行直连脚本：
.\start-claude-direct.ps1

验证直连是否成功的 3 个标志：

无红字报错：之前那个 ...\\node_modules... 找不到命令的红字应该消失了。
启动速度：你会发现直连模式下进入 claude 交互界面的速度变快了。
消耗优势：观察对话右上角的 Token 计数，直连模式能让你在处理 MCP 审计服务器 (mcp_audit_server.py) 这种较长代码时，享受 DeepSeek 原生 API 的极低成本。

关于“规则资料”的自动匹配：
由于你已经在 E:\MyCodeProjects 下运行，新的 Claude 实例会自动扫描当前目录。

如果你之前在该目录下有 .clinerules 或相关的“规则甄查”文档，它会立刻识别并作为背景知识。
如果你看到它再次请求读取文件的弹窗（如 image_fdc796.png 所示），直接点击批准即可，这正说明它已经在正常读取你的资产了。

如果现在运行脚本，终端返回的是什么内容？是否有出现预期的绿色提示文字？

---
*从 Gemini 导出，2026-05*
