---
title: Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> $apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
PS C:\Users\think> $sourceDir = "E:\Mycodeprojects"
PS C:\Users\think> $apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"
PS C:\Users\think>
PS C:\Users\think> # 排除隐藏文件夹和缓存，让你的 Obsidian 更干净
PS C:\Users\think> $projects = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -notlike ".*" -and $_.Name -notlike "__*" }
PS C:\Users\think>
PS C:\Users\think> $headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }
PS C:\Users\think>
PS C:\Users\think> foreach ($project in $projects) {
>>     $name = $project.Name
>>     $path = $project.FullName
>>     # 将路径转换为标准编码格式，解决“不存在”的问题
>>     $encodedPath = [uri]::EscapeDataString($path)
>>
>>     $tag = "General"
>>     if (Test-Path "$path\requirements.txt") { $tag = "AI_Python" }
>>
>>     $content = @"
>> # Project: $name
>> - Type: #$tag
>> - Folder: $path
>>
>> ## Link to Source
>> [Open in VS Code](vscode://file/$encodedPath)
>>
>> ## Relations
>> - Parent: [[Michael_Product_MOC]]
>> - Category: [[Category_$tag]]
>> "@
>>
>>     $targetUrl = "$apiVaultUrl/$name.md"
>>     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
>>     Write-Host "Fixed & Synced: $name" -ForegroundColor Green
>> }

Fixed & Synced: 01-Production

Fixed & Synced: 02-SubProjects

Fixed & Synced: 03-Archive

Fixed & Synced: Audit_Assets

Fixed & Synced: data

Fixed & Synced: scripts

Fixed & Synced: temp_frames
PS C:\Users\think>
source: gemini
date: 2026-05-10
category: Obsidian配置
tags: [gemini, Obsidian配置]
---

## Windows PowerShell
版权所有（C） Microsoft Corporation。保留所有权利。

安装最新的 PowerShell，了解新功能和改进！https://aka.ms/PSWindows

PS C:\Users\think> $apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
PS C:\Users\think> $sourceDir = "E:\Mycodeprojects"
PS C:\Users\think> $apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"
PS C:\Users\think>
PS C:\Users\think> # 排除隐藏文件夹和缓存，让你的 Obsidian 更干净
PS C:\Users\think> $projects = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -notlike ".*" -and $_.Name -notlike "__*" }
PS C:\Users\think>
PS C:\Users\think> $headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }
PS C:\Users\think>
PS C:\Users\think> foreach ($project in $projects) {
>>     $name = $project.Name
>>     $path = $project.FullName
>>     # 将路径转换为标准编码格式，解决“不存在”的问题
>>     $encodedPath = [uri]::EscapeDataString($path)
>>
>>     $tag = "General"
>>     if (Test-Path "$path\requirements.txt") { $tag = "AI_Python" }
>>
>>     $content = @"
>> # Project: $name
>> - Type: #$tag
>> - Folder: $path
>>
>> ## Link to Source
>> [Open in VS Code](vscode://file/$encodedPath)
>>
>> ## Relations
>> - Parent: [[Michael_Product_MOC]]
>> - Category: [[Category_$tag]]
>> "@
>>
>>     $targetUrl = "$apiVaultUrl/$name.md"
>>     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
>>     Write-Host "Fixed & Synced: $name" -ForegroundColor Green
>> }

Fixed & Synced: 01-Production

Fixed & Synced: 02-SubProjects

Fixed & Synced: 03-Archive

Fixed & Synced: Audit_Assets

Fixed & Synced: data

Fixed & Synced: scripts

Fixed & Synced: temp_frames
PS C:\Users\think>

看来链接依然报错是因为 [uri]::EscapeDataString 在处理 Windows 路径（如 E:\...）时，会将冒号和斜杠也进行转义，导致 vscode:// 协议无法识别路径格式。
我们要把链接做得更“原生”一些。VS Code 协议最稳妥的格式是 vscode://file/E:/path/to/project（使用正斜杠且不转义冒号）。

🛠️ 终极修复方案（针对“链接不存在”报错）
请在 PowerShell 中执行这个最终优化版。这个版本做了三件事：

路径格式化：将所有 \ 统一替换为 /，这是跨软件通信的标准。
纯净链接：不再对冒号进行转义，确保 vscode:// 协议能一眼认出 E 盘。
点击即用：直接生成最符合 Windows 规范的链接。

$apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
$sourceDir = "E:\Mycodeprojects"
$apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"

$projects = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -notlike ".*" -and $_.Name -notlike "__*" }
$headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }

foreach ($project in $projects) {
    $name = $project.Name
    $path = $project.FullName
    # 核心修复：将反斜杠换成正斜杠，且不转义冒号
    $cleanPath = $path.Replace("\", "/")
    
    $tag = "General"
    if (Test-Path "$path\requirements.txt") { $tag = "AI_Python" }

    $content = @"
# Project: $name
- Type: #$tag
- Folder: `$path`

## Link to Source
[🚀 Click to Open in VS Code](vscode://file/$cleanPath)

---
## Relations
- Parent: [[Michael_Product_MOC]]
- Category: [[Category_$tag]]
"@

    $targetUrl = "$apiVaultUrl/$name.md"
    Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
    Write-Host "Success: $name linked." -ForegroundColor Cyan
}


📝 检查与操作指南

执行代码：直接粘贴上述代码到 PowerShell。
回到 Obsidian：打开 01-Production 笔记，你会看到链接变成了 Click to Open in VS Code。
点击测试：

重要提示：在 Obsidian 预览模式下直接点击。如果是在编辑模式，请按住 Ctrl + 点击。


如果弹出警告：Windows 可能会问“你想如何打开此链接？”，选择 Visual Studio Code 并勾选“始终使用此应用”。

为什么这个能成功？
之前失败是因为 E%3A%5C... 这种转义字符让 VS Code 迷路了。现在的链接看起来像 vscode://file/E:/Mycodeprojects/01-Production，这是 VS Code 官方最认可的唤起方式。
请试一下这次的链接，VS Code 应该会乖乖弹出来了！如果成功了，我们就完成了整个自动化闭环。

---
*从 Gemini 导出，2026-05*
