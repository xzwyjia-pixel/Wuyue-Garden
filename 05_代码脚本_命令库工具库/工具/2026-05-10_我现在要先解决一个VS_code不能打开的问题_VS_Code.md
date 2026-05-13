---
title: 我现在要先解决一个VS code不能打开的问题
source: gemini
date: 2026-05-10
category: Obsidian配置
tags: [gemini, Obsidian配置]
---

## 我现在要先解决一个VS code不能打开的问题

既然 vscode:// 协议已经能在浏览器地址栏唤起弹窗，说明系统层面的“大门”已经打开了，但在 Obsidian 内部点击依然没反应，这通常是由于 Obsidian 的内部链接解析滞后 或 安全沙箱限制 导致的。
我们现在用两个最直接的操作彻底解决它：
1. 强制刷新 Obsidian 的“外部链接”缓存
有时候 Obsidian 在编辑模式下会对新生成的 API 链接有“保护机制”。

操作：按下 Ctrl + R (重新加载) 或者完全关闭 Obsidian 再重新打开。
验证：打开 Audit_Assets 笔记，按住 Ctrl 键再点击 那个蓝色的链接。


2. 在脚本中加入“备用物理路径”（Plan B）
如果协议跳转在某些情况下不稳定，我们在笔记里多加一个资源管理器直接打开的链接。这样万一 VS Code 没弹出来，你点一下就能直接打开 E 盘文件夹，右键“用 VS Code 打开”即可。
请在 PowerShell 运行这个“双重保障版”同步代码：
$apiKey = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
$sourceDir = "E:\Mycodeprojects"
$apiVaultUrl = "http://127.0.0.1:27123/vault/Michael_Product"

$projects = Get-ChildItem $sourceDir -Directory | Where-Object { $_.Name -notlike ".*" -and $_.Name -notlike "__*" }
$headers = @{ "Authorization" = "Bearer $apiKey"; "Content-Type" = "text/markdown" }

foreach ($project in $projects) {
    $name = $project.Name
    $path = $project.FullName
    $urlPath = $path.Replace("\", "/")
    
    $content = @"
# Project: $name
- Folder: `$path`

## 🚀 快捷执行
- [在 VS Code 中打开](vscode://file/$urlPath)
- [在资源管理器中打开](file:///$urlPath)

---
- [[Michael_Product_MOC]]
"@

    $targetUrl = "$apiVaultUrl/$name.md"
    Invoke-RestMethod -Method Put -Uri $targetUrl -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($content))
}
Write-Host "✅ 双重链接已部署，请回到 Obsidian 测试。" -ForegroundColor Cyan


3. 如果点击依然“无感”，请检查这个设置：
如果点击 file:/// 能打开文件夹，但 vscode:// 还是不行，请检查：

VS Code 是否正在运行？ 有时候 VS Code 在后台卡死会导致协议失效，请尝试关闭所有 VS Code 窗口再试。
Obsidian 插件干扰：请尝试暂时禁用你之前截图里的 Open vault in VS Code 插件。有时候同类插件会争夺 Ctrl+点击 的控制权。

你现在运行完这个脚本后，点一下那个新增的“在资源管理器中打开”，文件夹能弹出来吗？ 如果文件夹能出，说明路径没问题，我们只需要最后微调一下 VS Code 的唤醒参数。

---
*从 Gemini 导出，2026-05*
