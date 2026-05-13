---
title: 已成功安装

C:\Users\think>$targetPath = "E:\ClaudeEnvironment\npm_global"; $oldPath = [Environment]::GetEnvironmentVariable("Path", "User"); if ($oldPath -notlike "*$targetPath*") { [Environment]::SetEnvironmentVariable("Path", "$oldPath;$targetPath", "User"); Write-Host "✅ 成功！路径已添加到环境变量。" -ForegroundColor Green } else { Write-Host "ℹ️ 路径已经存在，无需重复添加。" -ForegroundColor Cyan }
'$targetPath' 不是内部或外部命令，也不是可运行的程序
或批处理文件。

C:\Users\think>
C:\Users\think>$targetPath = "E:\ClaudeEnvironment\npm_global"; $oldPath = [Environment]::GetEnvironmentVariable("Path", "User"); if ($oldPath -notlike "*$targetPath*") { [Environment]::SetEnvironmentVariable("Path", "$oldPath;$targetPath", "User"); Write-Host "✅ 成功！路径已添加到环境变量。" -ForegroundColor Green } else { Write-Host "ℹ️ 路径已经存在，无需重复添加。" -ForegroundColor Cyan }
'$targetPath' 不是内部或外部命令，也不是可运行的程序
或批处理文件。

C:\Users\think>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## 已成功安装

C:\Users\think>$targetPath = "E:\ClaudeEnvironment\npm_global"; $oldPath = [Environment]::GetEnvironmentVariable("Path", "User"); if ($oldPath -notlike "*$targetPath*") { [Environment]::SetEnvironmentVariable("Path", "$oldPath;$targetPath", "User"); Write-Host "✅ 成功！路径已添加到环境变量。" -ForegroundColor Green } else { Write-Host "ℹ️ 路径已经存在，无需重复添加。" -ForegroundColor Cyan }
'$targetPath' 不是内部或外部命令，也不是可运行的程序
或批处理文件。

C:\Users\think>
C:\Users\think>$targetPath = "E:\ClaudeEnvironment\npm_global"; $oldPath = [Environment]::GetEnvironmentVariable("Path", "User"); if ($oldPath -notlike "*$targetPath*") { [Environment]::SetEnvironmentVariable("Path", "$oldPath;$targetPath", "User"); Write-Host "✅ 成功！路径已添加到环境变量。" -ForegroundColor Green } else { Write-Host "ℹ️ 路径已经存在，无需重复添加。" -ForegroundColor Cyan }
'$targetPath' 不是内部或外部命令，也不是可运行的程序
或批处理文件。

C:\Users\think>

这步报错是因为你无意中在 CMD (命令提示符) 窗口执行了 PowerShell 代码。CMD 认不出 $targetPath 这种变量。
既然你已经装了 PowerShell 7，请确保你打开的是那个黑色底、标题写着 "PowerShell 7" 的窗口。
不过，为了防止再次因窗口类型导致失败，我为你准备了一个 CMD 版本的命令。你可以直接在刚才报错的那个窗口里粘贴运行，效果是一样的：
CMD 版一键修复命令
直接复制下面这行：
setx PATH "%PATH%;E:\ClaudeEnvironment\npm_global"


如果你还是想用 PowerShell 7 执行（推荐）：
请确保你的窗口前缀是 PS 而不是 C:\>，然后执行：
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";E:\ClaudeEnvironment\npm_global", "User")


验证步骤（非常关键）：
执行完上述任一命令后，请必须执行以下动作：

关闭所有已打开的命令行窗口（包括 Claude Code、PowerShell、CMD）。
重新打开一个新的 PowerShell 7 窗口。
输入 gsd --version。

为什么必须重启窗口？
Windows 的环境变量像是一张“通行证”，只有在窗口启动的那一刻才会发放。你在运行中的窗口里改了环境变量，它是感应不到的，必须“重新领证”才能生效。
等你能直接输入 gsd 看到版本号，你的 AI 工业级环境就真的合体完成了！

---
*从 Gemini 导出，2026-05*
