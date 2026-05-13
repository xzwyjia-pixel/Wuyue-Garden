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
PS C:\Windows\System32> cd D:\MyProjects  # 或者是你习惯的工作目录
Set-Location: Cannot find path 'D:\MyProjects' because it does not exist.
PS C:\Windows\System32> cd E:\MyCodeProjects
PS E:\MyCodeProjects> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> > /config
  ⎿  Retrying in 37s · attempt 7/10

✢ Crafting… (36s)
  ⎿  Tip: Use /btw to ask a quick side question without interrupting Claude's current work


  > /config
  > /help
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> Press up to edit queued messages
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt
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
PS C:\Windows\System32> cd D:\MyProjects  # 或者是你习惯的工作目录
Set-Location: Cannot find path 'D:\MyProjects' because it does not exist.
PS C:\Windows\System32> cd E:\MyCodeProjects
PS E:\MyCodeProjects> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> > /config
  ⎿  Retrying in 37s · attempt 7/10

✢ Crafting… (36s)
  ⎿  Tip: Use /btw to ask a quick side question without interrupting Claude's current work


  > /config
  > /help
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> Press up to edit queued messages
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  esc to interrupt

终于看到你把阵地转移到了 E:\MyCodeProjects，这是一个非常关键的进步！至少现在 Agent 不会被系统权限锁死“手脚”了。
不过，从当前的截图来看，你的 Claude Code 依然处于“严重心律不齐”的状态。
核心病灶：网络隧道未打通
截图显示 Retrying in 37s · attempt 7/10，这意味着即使你切换了路径，Claude Code 的“大脑”还是无法连接到 Anthropic 的服务器。
为什么会出现这种情况？
即使你的电脑可以上网页，PowerShell 终端通常是不自动走代理的。Claude Code 作为一个命令行工具，它在伸手向服务器要配置（/config）和帮助（/help）时，被挡在了墙内。

紧急修复方案（三步走）
第一步：强制止损
按下 esc 或者连续按两次 Ctrl-C 退出当前的 Claude 会话。不要让它继续尝试第 8 次、第 9 次重试，这只会白白浪费你的等待时间。
第二步：在 PowerShell 中注入“燃料” (代理)
在你启动 claude 之前，必须在当前的 PowerShell 窗口里手动声明代理地址。请根据你实际使用的代理软件（如 Clash, V2Ray, Clash Verge 等）修改下面的端口号（通常是 7890 或 1080）：
# 这里的 7890 请替换为你代理软件的实际端口
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"

第三步：验证并重启
输入完上面的命令后，你可以先输入 curl.exe -I https://www.google.com 测试一下。如果能返回一串 HTTP 信息而不是报错，说明路通了。
此时再重新启动：
claude


深度检测报告

Agent 搭配情况： 你启用了 Sonnet 4.6 with high effort。这是一个极其强大的配置，适合处理复杂的架构设计和代码审计（比如你之前研究的 MCP 规则审计）。但在网络不通时，这个模式会显得非常迟钝。
Skill 状态： 由于网络重试，你的指令 /config 和 /help 被塞在了队列里（Queued messages）。
建议： * 一旦网络通了，先运行一次 /compact 清理一下混乱的上下文。

如果网络依然不稳定，建议暂时关闭 high effort 模式，先用标准模式把环境调通。



你可以尝试先配置代理，然后输入 /health 看看？如果看到绿色的 Checkmark，说明你的 Agent 才真正“活”过来了。

---
*从 Gemini 导出，2026-05*
