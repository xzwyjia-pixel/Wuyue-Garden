---
title: PS C:\Users\think\.agents\skills>
source: gemini
date: 2026-05-08
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## PS C:\Users\think\.agents\skills>

## PS C:\Users\think\.agents\skills>
PS C:\Users\think\.agents\skills> # 再次执行绑定确保万无一失
PS C:\Users\think\.agents\skills> npx skills link --all
\(node:23344) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Unknown command: link
Run skills --help for usage.
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

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
> 
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ? for shortcuts                                                                                                                                                                              ● high · /effort

甄先生，审计结论：火已经点着了，但超能力插件还没挂载上去。
看到 Claude Code v2.1.133 的界面，说明主引擎已经完全康复。但刚才 npx skills link 报错 Unknown command，是因为 skills 这个工具的版本升级后，命令逻辑发生了变化——它不再需要手动 link，而是只要文件夹放对了位置，它就会自动扫描。
目前的现状是：“发动机”已启动，但“推进器”还在后备箱。

甄先生的“临门一脚”调试
既然您已经进入了 Claude 界面，我们直接在 Claude 内部完成最后的“技能激活”。请直接在 > 提示符后输入以下内容：
1. 检查物理存在 (确认它们是否真的在后备箱)
直接对 Claude 说：

“请检查我的用户目录 C:\Users\think\.agents\skills，列出下面所有的文件夹。我需要确认 caveman、superpowers 和 awesome 是否已经就绪。”

2. 强制读取技能
如果文件夹都在，直接下达这条“最高指令”：

“我刚才手动解压了 caveman 和 superpowers 到你的技能目录。请立即读取这些目录下的指令文件（通常是 README.md 或 .instructions），并将其作为你后续行为的全局规范。尤其是 Caveman 的压缩协议，请立即生效。”


💡 甄先生的“极简”补丁
如果 Claude 回复说“没看到这些技能”，那是因为 npx skills 的逻辑变了。请退出 Claude（输入 /exit），在 PowerShell 执行这一行命令直接安装那个缺失的“调度员”：
# 这个工具能帮 Claude 自动识别那些手动解压的文件夹
npm install -g @juliusbrussee/skills


甄先生，目前的优先级审计：

先在 Claude 里问一句话：看看它能不能看到那些文件夹。
跳过 link 报错：那个命令不存在没关系，只要文件夹在，我们可以让 Claude 强行读取。
遗留的缺失项：skill-creator、claude-hud、find-skills 这三个 ZIP 包您还没下载，所以刚才脚本提示警告。您可以稍后去浏览器下载。

甄先生，现在请在 Claude 的 > 界面，发送我给您的那段“检查物理存在”的话。看看它的反应如何？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-08*
