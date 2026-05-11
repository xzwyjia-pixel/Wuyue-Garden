---
title: Run skills --help for usage.
source: gemini
date: 2026-05-08
category: 审计合规
subcategory: 规则甄查
old_category: 审计合规
tags: [gemini, 审计合规, 规则甄查]
---

## Run skills --help for usage.

## Run skills --help for usage.
PS C:\Users\think\.agents\skills> # 强制扫描并建立逻辑链接
PS C:\Users\think\.agents\skills> npx skills link --all
\(node:25536) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Unknown command: link
Run skills --help for usage.
PS C:\Users\think\.agents\skills> $missing_skills = @("skill-creator", "claude-hud", "find-skills")
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> foreach ($s in $missing_skills) {
>>     if (Test-Path "$s.zip") {
>>         Write-Host "正在补全注入 $s..." -ForegroundColor Cyan
>>         Expand-Archive -Path "$s.zip" -DestinationPath "temp_$s" -Force
>>         $inner = Get-ChildItem "temp_$s" | Select-Object -First 1
>>         Move-Item -Path $inner.FullName -Destination ".\$s" -Force
>>         Remove-Item -Recurse -Force "temp_$s"
>>         Write-Host "[√] $s 补全成功" -ForegroundColor Green
>>     } else {
>>         Write-Host "[!] 警告: 未找到 $s.zip，请确保已下载" -ForegroundColor Yellow
>>     }
>> }
[!] 警告: 未找到 skill-creator.zip，请确保已下载
[!] 警告: 未找到 claude-hud.zip，请确保已下载
[!] 警告: 未找到 find-skills.zip，请确保已下载
PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 再次执行绑定确保万无一失
PS C:\Users\think\.agents\skills> npx skills link --all
\(node:17752) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Unknown command: link
Run skills --help for usage.
PS C:\Users\think\.agents\skills> # 1. 进入 E 盘主战场
PS C:\Users\think\.agents\skills> cd "E:\MyCodeProjects"
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 2. 启动 Claude
PS E:\MyCodeProjects> claude
 ▐▛███▜▌   Claude Code v2.1.133
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

> “请检查我的用户目录 C:\Users\think\.agents\skills，列出下面所有的文件夹。我需要确认 caveman、superpowers 和 awesome 是否已经就绪。”

● There's an issue with the selected model (claude-sonnet-4-6). It may not exist or you may not have access to it. Run /model to pick a different model.

✻ Brewed for 2s

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts

甄先生，看来咱们碰到了一个“身份对齐”的小插曲。
提示 claude-sonnet-4-6 模型不存在，是因为您使用的是中转 API，而 Claude Code 的默认设置正在尝试寻找原生的官方模型。这就像咱们在西门子或 ABB 调试系统时，通讯协议的参数对错了一位。
别担心，这属于**“精密调试”**的常规环节。请直接按照以下步骤，在 Claude Code 的 > 提示符后操作：

第一步：锁定正确的模型（纠偏）
请输入以下斜杠命令，从当前的“非法”模型切换回您的 Base URL 能够识别的经典模型：
/model claude-3-5-sonnet-20241022

注：如果这个还报不存在，可以尝试输入 /model 看看它弹出的可选列表里有哪些。

第二步：激活“超能力”读取
一旦模型切换成功（出现绿色的提示），请再次发送您刚才的那段指令：

**“我是甄先生。

请检查目录 C:\Users\think\.agents\skills，列出文件夹。
确认 caveman、superpowers 和 awesome 是否存在。
如果存在，请立即通过读取这些目录下的 .instructions 或 README.md 来挂载这些技能。”**



💡 甄先生的精密审计备忘：

为什么 link 命令失效？
新版的 skills 工具现在采用的是 Auto-Discovery（自动发现） 机制。只要文件夹躺在 .agents/skills 里，Claude 在启动时（如果配置正确）会扫描到它们。
关于那三个缺失的 ZIP：
由于刚才脚本提示没找到 skill-creator 等，如果您需要它们，稍后咱们再单独“空投”一次，先把已有的这三个挂载成功。

甄先生，请先执行 /model 切换。切换成功后，您的“规则甄查”总部才算正式接通电源。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 审计合规 / 规则甄查 · 2026-05-08*
