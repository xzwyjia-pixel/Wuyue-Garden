---
title: 
PS C:\Users\think> Write-Host "✅ 双重链接已部署，请回到 Obsidian 测试。" -ForegroundColor Cyan
✅ 双重链接已部署，请回到 Obsidian 测试。
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
Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

PS C:\Users\think> Write-Host "✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。" -ForegroundColor Cyan
✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。
PS C:\Users\think>
source: gemini
date: 2026-05-10
category: Obsidian配置
tags: [gemini, Obsidian配置]
---

## 
PS C:\Users\think> Write-Host "✅ 双重链接已部署，请回到 Obsidian 测试。" -ForegroundColor Cyan
✅ 双重链接已部署，请回到 Obsidian 测试。
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
Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

Invoke-RestMethod : 无法连接到远程服务器
所在位置 行:18 字符: 5
+     Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers - ...
+     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (:) [Invoke-RestMethod], WebException
    + FullyQualifiedErrorId : System.Net.WebException,Microsoft.PowerShell.Commands.InvokeRestMethodCommand

PS C:\Users\think> Write-Host "✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。" -ForegroundColor Cyan
✅ 补丁已部署。请检查 Obsidian 中的 Open_in_VS_Code 链接。
PS C:\Users\think>

出现“无法连接到远程服务器”的错误，是因为刚才你为了解决 VS Code 无法打开的问题，可能无意中关闭了 Obsidian 或者 Local REST API 服务中断了。
当 Obsidian 没运行，或者它的 API 服务没启动时，PowerShell 脚本就找不到 127.0.0.1:27123 这个“门”，所以会报错。
🛠️ 恢复连接的 3 个简单步骤：


确认 Obsidian 正在运行：
请确保你的 Obsidian 窗口是打开的，并且处于你当前的库（Vault）中。


检查插件状态（参考你刚才上传的图片 image_07e9f8.png）：

进入 Obsidian 设置 -> Community Plugins -> Local REST API。
确保 Enable Non-encrypted (HTTP) Server 这个开关是 紫色（开启） 的。
如果开关是开着的，试着关掉再重新打开一次，这相当于重启了 API 端口。



重新执行脚本：
保持 Obsidian 开启，回到 PowerShell 再次粘贴运行刚才的脚本。



💡 为什么文件夹和 VS Code 之前点不动？
从你之前的截图看，有一个细节：你的链接显示为 Open_in_VS_Code 后面带有一个**“外部链接图标”（右上角的小箭头）。这说明 Obsidian 已经识别了链接，但点击没反应通常是因为“点击姿势”不对**：

如果你在编辑模式（能看到光标在跳动）：必须 按住 Ctrl 键再点链接 才能跳转。
如果你在阅读模式（看不到光标，像看网页一样）：直接点击即可。你可以按 Ctrl + E 快速切换模式。

请先重新启动 Obsidian 的 API 服务，然后再跑一次脚本。只要脚本不再报“无法连接”，我们就成功把正确的“双重链接”写进去了！

---
*从 Gemini 导出，2026-05*
