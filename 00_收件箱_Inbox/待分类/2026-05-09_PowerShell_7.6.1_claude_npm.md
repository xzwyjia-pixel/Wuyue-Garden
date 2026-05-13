---
title: PowerShell 7.6.1
PS C:\Windows\System32> npm install -g @anthropic-ai/claude-code --force
npm warn using --force Recommended protections disabled.
\(node:14536) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

changed 2 packages in 4s
PS C:\Windows\System32> cd E:\MyCodeProjects
PS E:\MyCodeProjects> .\start-claude-direct.ps1
>>> 正在尝试直连 DeepSeek 官网 - 高性能模式
'"C:\Users\think\AppData\Roaming\npm\\node_modules\@anthropic-ai\claude-code\bin\claude.exe"' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
PS E:\MyCodeProjects>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> npm install -g @anthropic-ai/claude-code --force
npm warn using --force Recommended protections disabled.
\(node:14536) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

changed 2 packages in 4s
PS C:\Windows\System32> cd E:\MyCodeProjects
PS E:\MyCodeProjects> .\start-claude-direct.ps1
>>> 正在尝试直连 DeepSeek 官网 - 高性能模式
'"C:\Users\think\AppData\Roaming\npm\\node_modules\@anthropic-ai\claude-code\bin\claude.exe"' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
PS E:\MyCodeProjects>

看来即便重新安装了程序，那个顽固的“双斜杠路径”依然像幽灵一样存在于你的 npm 缓存中。这通常是因为 npm 在你的 ThinkPad P15V 上生成的 claude.cmd 脚本内部路径依然是错误的。
作为项目管理专家，我们不再纠结于修复这个受损的“路标”，而是直接换一条“高速公路”。
终极解决方案：绕过受损的 cmd 脚本
既然直接调用 claude 会触发错误的路径，我们直接在你的 start-claude-direct.ps1 脚本中指定正确的、干净的路径。
请按照以下步骤调整你的脚本：


修改 start-claude-direct.ps1：
将最后一行（原来的 cmd.exe /c "claude"）替换为：
& "C:\Users\think\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"

注：请注意这里我用的是单斜杠。


如果依然报错，请尝试这个“纯净模式”调用：
npx @anthropic-ai/claude-code


优势：npx 会绕过你本地损坏的全局 cmd 链接，直接运行包内的可执行文件。这是打通 DeepSeek 直连模式 最稳妥的办法。




为什么这对你的任务至关重要？

资产保护：这种修改方式完全不会触及你 E:\MyCodeProjects 下的 “规则甄查”系统资料。
成本控制：一旦这个脚本跑通，你就能彻底摆脱不稳定的中转通道，直接利用 DeepSeek 的低成本优势。
环境兼容：你使用的是 PowerShell 7.6.1，这个版本的 & 符号（调用操作符）在处理带有 @ 的复杂路径时比 cmd /c 更加精准。

验证步骤：
修改完脚本后，请在 E:\MyCodeProjects 再次运行：
.\start-claude-direct.ps1

如果这次能够看到启动界面，说明我们成功绕开了 npm 的配置故障。你的 MCP 审计服务器 就可以正式在高性能模式下开始工作了。
如果修改为 npx 方案后依然报错，请告诉我，那可能意味着我们需要手动清理一下你 AppData 里的 npm 缓存。

---
*从 Gemini 导出，2026-05*
