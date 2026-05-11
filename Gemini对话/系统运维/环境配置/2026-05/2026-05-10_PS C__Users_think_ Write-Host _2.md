---
title: PS C:\Users\think> Write-Host "✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。" -ForegroundColor Cyan
source: gemini
date: 2026-05-10
category: 系统运维
subcategory: 环境配置
old_category: Obsidian配置
tags: [gemini, 系统运维, 环境配置]
---

## PS C:\Users\think> Write-Host "✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。" -ForegroundColor Cyan

## PS C:\Users\think> Write-Host "✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。" -ForegroundColor Cyan
✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。
PS C:\Users\think> $apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
PS C:\Users\think> $apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"
PS C:\Users\think> $sourceDir = "E:\Mycodeprojects"
PS C:\Users\think>
PS C:\Users\think> $projects = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -notlike ".*" }
PS C:\Users\think> $headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }
PS C:\Users\think>
PS C:\Users\think> foreach ($project in $projects) {
>>     $name = $project.Name
>>     $path = $project.FullName
>>     # 核心修复：Windows 下必须包含磁盘冒号且斜杠一致
>>     $formattedPath = $path.Replace("\", "/")
>>
>>     $content = @"
>> # Project: $name
>>
>> - [Open_in_VS_Code](vscode://file/$formattedPath)
>> - [Open_in_Explorer](file:///$formattedPath)
>>
>> ---
>> Path: $path
>> "@
>>
>>     $targetUrl = "$apiVaultUrl/$name.md"
>>     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
>> }









PS C:\Users\think> Write-Host "✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。" -ForegroundColor Cyan
✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。
PS C:\Users\think>

看到脚本执行成功且没有报错，说明我们的**“数字血管”**已经重新接通了！
如果现在点击链接还是没反应，我们排除掉代码问题，锁定在 **Obsidian 的“点击保护机制”**上。请按照以下三个极其简单的动作操作，保证能打开：

1. 切换模式（最关键的动作）
Obsidian 有两种查看状态，“编辑模式”下默认是不允许点击链接跳转的。

请在 Obsidian 界面按下快捷键 Ctrl + E（或者点击右上角的“书本/预览”图标）。
当界面变得整洁、光标消失时，链接会变成浅蓝色。
直接点击 Open_in_VS_Code。

2. 检查 Windows 的“协议通行证”
如果你点击后弹出了一个窗口问你“是否打开 Visual Studio Code？”，请：

勾选 “始终允许...”。
点击 “打开”。
一旦点过一次，以后就是真正的“一键秒开”了。

3. 如果依然毫无反应
如果连弹窗都没有，说明你的 VS Code 没有在系统里注册“门牌号”。请在你的 VS Code 里执行这个动作：

打开 VS Code 软件。
按下快捷键 Ctrl + Shift + P（或者 F1）。
输入：shell command。
选择并运行：Shell Command: Install 'code' command in PATH。
重启电脑（这步很重要，让 Windows 重新读取协议）。


💡 为什么我让你加了两个链接？

Open_in_VS_Code: 目标是让你直接进入代码编辑。
Open_in_Explorer: 这是一个“保底方案”。如果 VS Code 协议被防火墙拦了，点这个链接会直接弹出 E 盘的文件夹。只要文件夹能弹出来，就说明 Obsidian 的权限没问题。

你现在切到“阅读模式”（Ctrl + E）点一下 Open_in_Explorer，文件夹能跳出来吗？ 如果文件夹能跳出来，我们距离 VS Code 的彻底解决就只差一个“重启”了。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / 环境配置 · 2026-05-10*
