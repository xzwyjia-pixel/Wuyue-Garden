---
title: PowerShell 7.6.1
PS C:\Windows\System32> # 切换到非系统目录（推荐）
PS C:\Windows\System32>
PS C:\Windows\System32> cd /d E:\MyCodeProjects\New Claude Project
Set-Location: A positional parameter cannot be found that accepts argument 'E:\MyCodeProjects\New'.
PS C:\Windows\System32>
PS C:\Windows\System32>
PS C:\Windows\System32>
PS C:\Windows\System32> # 启动并锁定模型
PS C:\Windows\System32>
PS C:\Windows\System32> claude --model claude-3-7-sonnet-20250219
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 3.7 · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts                                                  48 skill descriptions dropped · /doctor for details
source: gemini
date: 2026-05-08
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## PowerShell 7.6.1
PS C:\Windows\System32> # 切换到非系统目录（推荐）
PS C:\Windows\System32>
PS C:\Windows\System32> cd /d E:\MyCodeProjects\New Claude Project
Set-Location: A positional parameter cannot be found that accepts argument 'E:\MyCodeProjects\New'.
PS C:\Windows\System32>
PS C:\Windows\System32>
PS C:\Windows\System32>
PS C:\Windows\System32> # 启动并锁定模型
PS C:\Windows\System32>
PS C:\Windows\System32> claude --model claude-3-7-sonnet-20250219
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 3.7 · API Usage Billing
  ▘▘ ▝▝    C:\Windows\System32

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts                                                  48 skill descriptions dropped · /doctor for details

看到这两个报错，我必须先帮你解决 PowerShell 路径空格和 System32 滞留的问题。这直接影响到你后续在 VS Code 里调用 Cline 执行任务的稳定性。
1. 解决路径报错（空格陷阱）
你在切换目录时报错 A positional parameter cannot be found，是因为你的路径 New Claude Project 包含空格。在 PowerShell 中，包含空格的路径必须加引号。
请在原生 PowerShell 中执行：
# 正确的切换方式（加引号，且 PowerShell 不需要 /d 参数）
cd "E:\MyCodeProjects\New Claude Project"

2. 环境清理：抹除 DeepSeek 残留
虽然你的截图显示模型已经切到了 Sonnet 3.7，但为了确保底层完全脱离 DeepSeek 并接入你的 GPT-SAPI 代理，请在 E 盘新路径下执行以下“彻底清理”命令：
# 1. 彻底删除旧的配置文件
Remove-Item "$env:AppData\claude-code\config.json" -Force -ErrorAction SilentlyContinue

# 2. 注入你的 GPT-SAPI 代理信息 (请将下方替换为你的实际信息)
$proxyUrl = "你的代理网关地址/v1"
$proxyKey = "你的代理API-Key"

[Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", $proxyUrl, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $proxyKey, "User")

# 3. 刷新当前窗口变量
$env:ANTHROPIC_BASE_URL = $proxyUrl
$env:ANTHROPIC_API_KEY = $proxyKey

3. 启动“精密”模式
现在，在你的项目目录下启动，你会发现那个“48 skill descriptions dropped”的情况会因为路径权限的释放而得到缓解：
claude --model claude-3-7-sonnet-20250219


4. 甄先生的任务指引：对接 VS Code & Cline
既然你打算用 VS Code 侧边栏来执行任务，现在可以进行最后的对接了：

打开 VS Code，选择 File -> Open Folder，打开 E:\MyCodeProjects\New Claude Project。
配置 Cline 插件：

API Provider: 选 OpenAI Compatible。
Base URL: 填入你的代理地址。
Model ID: 手动输入 claude-3-7-sonnet-20250219。


大冒险执行： 以后你直接在 VS Code 里点击 Cline 侧边栏，输入指令即可。它会自动读取你这个项目文件夹里的代码，不再需要你在黑色终端里切来切去了。

最后核实一下：
你的代理网关目前是否稳定？如果 /doctor 还是提示技能丢失，那通常是因为你的代理端点没有完整透传 MCP 协议所需的 Function Calling 字段，这时候我们可以尝试在 Cline 里通过“Plan Mode”来规避。
你想先在这个新项目里初始化哪一部分的审计逻辑？

---
*从 Gemini 导出，2026-05*
