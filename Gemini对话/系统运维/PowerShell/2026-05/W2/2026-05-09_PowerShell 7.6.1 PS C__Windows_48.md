---
title: PowerShell 7.6.1
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 系统运维
tags: [gemini, 系统运维, PowerShell]
---

## PowerShell 7.6.1

## PowerShell 7.6.1
PS C:\Windows\System32> gsd --version
gsd: The term 'gsd' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.

[General Feedback]
  The most similar commands are:
    > gsv, gsn

PS C:\Windows\System32> opsx --version

看来环境变量的“最后一公里”还没完全通。这通常是因为 npm 在非默认路径（你的 E:\ClaudeEnvironment\npm_global）安装时，生成的执行文件可能藏在子文件夹里。
我们用一招“降维打击”的方法，直接定位文件并强行打通。
1. 终极定位：看看文件到底在哪
请在 PowerShell 7 中输入这条命令，它会帮你搜遍那个文件夹：
Get-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName

观察输出结果：

如果你看到了 gsd.cmd 和 opsx.cmd，请看它们所在的 FullName（路径）。
很有可能它们在 E:\ClaudeEnvironment\npm_global 的某个子文件夹里（比如 node_modules\.bin）。

2. 精准修复：手动将确切路径加入环境变量
根据你之前的 npm config 设置，最有可能的“真身”路径是：
E:\ClaudeEnvironment\npm_global 或者 E:\ClaudeEnvironment\npm_global\bin。
请在 PowerShell 中执行这个增强版修复脚本：
$globalPath = "E:\ClaudeEnvironment\npm_global"
# 自动探测 bin 目录
$binPath = if (Test-Path "$globalPath\bin") { "$globalPath\bin" } else { $globalPath }

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$binPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", "User")
    Write-Host "✅ 已添加确切路径: $binPath" -ForegroundColor Green
} else {
    Write-Host "ℹ️ 路径已在记录中，尝试强制刷新当前会话..." -ForegroundColor Cyan
}

# 强制让当前窗口也认领这个路径
$env:Path += ";$binPath"

3. 如果还是报错，直接用这个“必杀技”
如果上面的环境变量死活不生效，说明 Windows 的注册表刷新有延迟。不需要再折腾系统了，直接在你的项目目录里用 npx 即可，这和直接运行命令的效果是 100% 一样的：

想用 GSD？输入：npx gsd-code-first
想用 OpenSpec？输入：npx @fission-ai/openspec (简写为 npx opsx)


💡 给你的特别建议
作为一名处理复杂项目的专业人士，如果这套工具在全局环境下总是反复出现路径问题，我建议你采用 “项目内局部安装” 的策略：

在你的项目目录 E:\MyCodeProjects 下运行：
npm install gsd-code-first @fission-ai/openspec --save-dev
这样在 Claude Code 里，它会自动识别项目内的 node_modules，兼容性是最好的，也不会被 Windows 的环境变量坑到。

试试看运行 npx gsd-code-first --version，只要这一行通了，你的开发之旅就可以正式开启了！

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
