---
title: PowerShell 7.6.1
PS C:\Windows\System32> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Press Ctrl-C again to exit

Resume this session with:
claude --resume 810bc635-5f8e-46cb-8003-79a13ea0cf15
PS C:\Windows\System32> /health
/health: The term '/health' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> /config
/config: The term '/config' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32>
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Press Ctrl-C again to exit

Resume this session with:
claude --resume 810bc635-5f8e-46cb-8003-79a13ea0cf15
PS C:\Windows\System32> /health
/health: The term '/health' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> /config
/config: The term '/config' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32>

看来你刚刚经历了一次典型的“跨次元”误操作。简单来说，你尝试在 Windows PowerShell 的系统命令行里，直接运行原本属于 Claude Code 内部的指令。
这里有两个关键的“知识点”需要纠正：
1. 命令行环境的混淆
当你看到 PS C:\Windows\System32> 时，你处于 Windows 的系统外壳中。

/health 和 /config 是 Claude Code 运行后的内部斜杠命令。
你刚才已经按了 Ctrl-C 退出了 Claude 的交互界面，所以 PowerShell 无法识别这些指令，误以为你要运行某种系统程序。

2. 依然存在的“System32”风险
你依然在 C:\Windows\System32 下操作。这是一个受保护的系统目录，即使你重新进入 Claude，它在尝试读取文件或保存日志时，极大概率会触发 EPERM（权限被拒绝）错误。

建议的操作步骤（手动修复方案）
第一步：离开系统目录（非常重要）
请先切换到一个你存放代码或工具的普通文件夹，例如：
cd D:\MyProjects  # 或者是你习惯的工作目录

第二步：重新启动并进入 Claude 交互模式
在你的工作目录下输入：
claude

只有当你看到那个橙色的像素小人图标和 > 输入提示符时，你才算进入了 Claude Code 的“大脑”。
第三步：在内部运行指令
进入后，再尝试输入指令（注意此时不需要在前面加 claude）：

> /config (查看配置)
> /help (查看可用指令列表)


为什么之前的 nihao 没反应？
从你之前的报错来看，大概率是网络代理没有透传给 PowerShell。如果重新进入后依然卡在 Retrying，请在 启动 claude 之前，先执行以下命令（假设你的代理端口是 7890）：
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"

小贴士： 你现在使用的是 Sonnet 4.6 这种高消耗模式，在网络不通的情况下不断重试会产生无意义的 API 调用等待。建议先把网络和路径调顺了，再让它执行复杂的任务。
要不要试试先切换路径，然后发个指令让它给你写个简单的脚本测试一下连通性？

---
*从 Gemini 导出，2026-05*
