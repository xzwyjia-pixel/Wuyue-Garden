---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-10
category: 系统运维
subcategory: PowerShell
old_category: 编程开发
tags: [gemini, 系统运维, PowerShell]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> # 1. 设置配置信息
>> $apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
>> $sourceDir = "E:\Mycodeprojects"
>> $apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"
>>
>> # 2. 扫描文件夹并推送
>> if (Test-Path $sourceDir) {
>>     $projects = Get-ChildItem $sourceDir -Directory
>>     $headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }
>>
>>     foreach ($project in $projects) {
>>         $name = $project.Name
>>         $path = $project.FullName
>>         $linuxPath = $path.Replace('\', '/')
>>
>>         # 自动贴标签
>>         $tag = "General"
>>         if (Test-Path "$path\package.json") { $tag = "Web_Project" }
>>         if (Test-Path "$path\requirements.txt") { $tag = "AI_Python" }
>>
>>         # 生成 Markdown 内容
>>         $content = @"
>> # Project: $name
>> - Type: #$tag
>> - Path: $path
>>
>> ## Actions
>> - [Open in VS Code](vscode://file/$linuxPath)
>> - [Open in Explorer](file:///$linuxPath)
>>
>> ## Links
>> - Category: [[Category_$tag]]
>> "@
>>
>>         # 推送到 Obsidian (Michael_Product 文件夹)
>>         $targetUrl = "$apiVaultUrl/$name.md"
>>         Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
>>         Write-Host "Synced: $name" -ForegroundColor Green
>>     }
>>     Write-Host "All Done! Check Michael_Product folder in Obsidian." -ForegroundColor Cyan
>> } else {
>>     Write-Host "Error: E:\Mycodeprojects not found!" -ForegroundColor Red
>> }

Synced: __pycache__

Synced: .claude

Synced: .githooks

Synced: .obsidian

Synced: .vs

Synced: 01-Production

Synced: 02-SubProjects

Synced: 03-Archive

Synced: Audit_Assets

Synced: data

Synced: scripts

Synced: temp_frames
All Done! Check Michael_Product folder in Obsidian.
PS C:\Windows\System32>

太棒了！看到 PowerShell 输出了一连串的 Synced，说明我们的**“数字血管”**已经彻底打通了。
现在，你已经成功将 E 盘的项目结构实时映射到了 Obsidian 中。

🚀 现在的成果检查
请切换到 Obsidian 软件，你会看到以下变化：

Michael_Product 文件夹：侧边栏出现了这个新文件夹，里面包含了你刚才同步的所有子项目（如 01-Production, Audit_Assets 等）。
可视化连接：

点击左侧工具栏的 关系图谱 (Graph View)。
你会发现这些笔记已经自动连接到了 [[Category_General]] 或 [[Category_AI_Python]]。
进阶操作：在图谱设置的 Groups 里添加查询 path: Michael_Product，给它们设置一个醒目的颜色（比如亮蓝色），你会看到你的代码版图非常清晰。


一键回传 VS Code：

打开任意一个生成的笔记（例如 Audit_Assets.md）。
点击 Open in VS Code 链接。
VS Code 会立即弹出并直接定位到 E 盘的对应目录。




🛠️ 以后如何“零人工”维持联动？
既然你希望减少操作，我们现在确定一下未来的 “Michael 工作流”：
方案一：随用随点（手动触发）
如果你在 E 盘新建了项目，只需要再次把刚才那段代码粘贴进 PowerShell 运行一次即可（或者我们可以把代码存为一个 .ps1 文件放在桌面，改完代码双击一下）。
方案二：Claude 自动同步（AI 触发）
以后当你在 Claude 界面里让我写代码时，直接告诉我：

“把刚才这段代码保存到 E 盘，并同步到 Obsidian。”

我会通过 API 同时执行两个操作：

文件落地：把 .py 或 .js 文件写入 E 盘。
同步索引：更新 Obsidian 里的项目卡片和联系网。


💡 一个优化建议
我注意到你的同步列表里有 .obsidian, .vs, __pycache__ 这种隐藏或缓存文件夹。如果你觉得它们在 Obsidian 里很碍眼，我们可以修改脚本逻辑，自动跳过以“.”开头的文件夹。
你现在的 Obsidian 关系图谱看起来符合你的预期吗？ 或者需要我帮你把那些“垃圾文件夹”从 Obsidian 中清理掉？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-10*
