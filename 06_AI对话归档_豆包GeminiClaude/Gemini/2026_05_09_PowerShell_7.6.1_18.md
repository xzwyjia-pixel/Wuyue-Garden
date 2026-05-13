---
title: PowerShell 7.6.1
PS C:\Windows\System32> # 将原来的末行改为：
>> cmd.exe /c "claude"
'"C:\Users\think\AppData\Roaming\npm\\node_modules\@anthropic-ai\claude-code\bin\claude.exe"' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
PS C:\Windows\System32>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> # 将原来的末行改为：
>> cmd.exe /c "claude"
'"C:\Users\think\AppData\Roaming\npm\\node_modules\@anthropic-ai\claude-code\bin\claude.exe"' 不是内部或外部命令，也不是可运行的程序
或批处理文件。
PS C:\Windows\System32>

从报错信息来看，即便你使用了 cmd.exe /c "claude"，系统仍然顽固地试图去调用那个带有双斜杠和长路径的 .exe 文件，并且依然报错。这说明你的 npm 配置或系统 PATH 变量中，claude 这个指令被硬编码指向了一个错误的绝对路径。
既然你使用的是 ThinkPad P15V 且安装了 PowerShell 7.6.1，我们可以通过更底层的逻辑来“疏通”这个调用路径。
处方 1：手动修正 npm 的“软链接”脚本
报错的原因通常是 C:\Users\think\AppData\Roaming\npm\claude.cmd 这个文件内部的路径写错了（多了一个斜杠或引号不对）。

请在资源管理器中打开路径：C:\Users\think\AppData\Roaming\npm\。
找到名为 claude.cmd 的文件，右键点击“编辑”。
检查里面的路径，确保它是：

"%~dp0\node_modules\@anthropic-ai\claude-code\bin\claude.exe"
注意：确保 npm 后面没有多余的 \\。



处方 2：在脚本中使用“全量转义”启动（最稳妥）
如果修改 npm 配置文件比较麻烦，我们直接在你的 start-claude-direct.ps1 脚本中使用 PowerShell 的“停止解析”符号 --%，强行让系统执行最原始的命令：
请将脚本最后一行修改为：
& "C:\Users\think\AppData\Roaming\npm\claude.cmd"

或者，如果 claude 已经在你的环境变量里，直接使用：
cmd.exe /c --% claude

处方 3：重新链接（一劳永逸）
如果你希望以后所有新任务都不再出现这个路径错误，建议在 管理员模式 的 PowerShell 中执行一次重新安装，这会修复损坏的二进制链接：
npm install -g @anthropic-ai/claude-code --force


核心建议：
由于你现在正处于 “规则甄查”系统 和 MCP 审计服务器 的关键开发期，不建议在路径问题上耗费太多精力。

临时方案：先用 & "C:\Users\think\AppData\Roaming\npm\claude.cmd" 顶替，确保能立刻进入 DeepSeek 直连模式。
后续计划：等今天任务告一段落，再通过 npm install -g ... --force 彻底清理环境。

修改后，直接在 E:\MyCodeProjects> 再次运行 .\start-claude-direct.ps1 试试，看看那行恼人的“不是内部或外部命令”是否消失了？

---
*从 Gemini 导出，2026-05*
