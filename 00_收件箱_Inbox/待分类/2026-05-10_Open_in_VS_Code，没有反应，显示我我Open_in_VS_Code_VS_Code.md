---
title: Open in VS Code，没有反应，显示我我Open in VS Code不存在
source: gemini
date: 2026-05-10
category: Obsidian配置
tags: [gemini, Obsidian配置]
---

## Open in VS Code，没有反应，显示我我Open in VS Code不存在

出现“不存在”或没反应，通常是因为 Windows 还没有把 vscode:// 这个协议和你的 VS Code 软件关联起来，或者 Obsidian 识别到了非法字符。
别担心，我们不需要去翻插件设置。我直接给你一个**“终极修复方案”**，通过两个小步骤彻底解决：

第一步：修复 Windows 的“传送门”协议
如果点击链接没反应，说明 VS Code 在安装时没有注册协议。

按下键盘上的 Win + R，输入 cmd 并回车。
在黑色窗口中输入以下指令（这会让 VS Code 重新向系统“报到”）：
code --install-url-handler

如果提示找不到 code，请手动打开一次 VS Code，按 F1 键，输入 Shell Command: Install 'code' command in PATH 并运行。


第二步：由 Claude 重新生成更兼容的链接
有时候文件夹路径中的空格或中文字符会导致链接断开。我重新为你优化了脚本逻辑，使用了更稳定的格式，并去掉了那些可能干扰显示的图标。
请在 PowerShell 中运行这个修复版脚本：
$apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
$sourceDir = "E:\Mycodeprojects"
$apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"

# 排除隐藏文件夹和缓存，让你的 Obsidian 更干净
$projects = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -notlike ".*" -and $_.Name -notlike "__*" }

$headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }

foreach ($project in $projects) {
    $name = $project.Name
    $path = $project.FullName
    # 将路径转换为标准编码格式，解决“不存在”的问题
    $encodedPath = [uri]::EscapeDataString($path)
    
    $tag = "General"
    if (Test-Path "$path\requirements.txt") { $tag = "AI_Python" }

    $content = @"
# Project: $name
- Type: #$tag
- Folder: $path

## Link to Source
[Open in VS Code](vscode://file/$encodedPath)

## Relations
- Parent: [[Michael_Product_MOC]]
- Category: [[Category_$tag]]
"@

    $targetUrl = "$apiVaultUrl/$name.md"
    Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
    Write-Host "Fixed & Synced: $name" -ForegroundColor Green
}


如何验证是否成功？

重启 Obsidian（确保它加载了新的链接）。
打开 01-Production 或任意一个笔记。
按住 Ctrl 键并点击 「Open in VS Code」链接。
如果弹出询问框：“是否允许此站点打开 vscode 链接？”，请勾选**“始终允许”**并点击确定。


💡 如果还是打不开？
如果上述操作后依然显示“不存在”，那是因为你的 Obsidian 还没安装 "Open in Other Editor" 插件所依赖的底层组件。
终极绝招：
直接在 Obsidian 笔记里输入这段文字测试一下：
[打开我的E盘](file:///E:/Mycodeprojects)
如果这个能打开文件夹，说明 Obsidian 的链接功能是正常的。
你可以试试运行修复脚本，然后告诉我点击 Open in VS Code 时，它弹出了什么错误提示吗？

---
*从 Gemini 导出，2026-05*
