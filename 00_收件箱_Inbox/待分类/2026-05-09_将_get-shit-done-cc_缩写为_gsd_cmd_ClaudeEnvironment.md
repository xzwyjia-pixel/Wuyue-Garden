---
title: PS C:\Windows\System32> Get-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName

Name                 FullName
----                 --------
claude-hud.cmd       E:\ClaudeEnvironment\npm_global\claude-hud.cmd
claude.cmd           E:\ClaudeEnvironment\npm_global\claude.cmd
ecc-install.cmd      E:\ClaudeEnvironment\npm_global\ecc-install.cmd
ecc.cmd              E:\ClaudeEnvironment\npm_global\ecc.cmd
get-shit-done-cc.cmd E:\ClaudeEnvironment\npm_global\get-shit-done-cc.cmd
gsd-sdk.cmd          E:\ClaudeEnvironment\npm_global\gsd-sdk.cmd
openspec.cmd         E:\ClaudeEnvironment\npm_global\openspec.cmd
playwright-core.cmd  E:\ClaudeEnvironment\npm_global\playwright-core.cmd
node-which.cmd       E:\ClaudeEnvironment\npm_global\node_modules\@fission-ai\openspec\node_modules\.bin\node-which.cmd
yaml.cmd             E:\ClaudeEnvironment\npm_global\node_modules\@fission-ai\openspec\node_modules\.bin\yaml.cmd
anthropic-ai-sdk.cmd E:\ClaudeEnvironment\npm_global\node_modules\@gsd-build\sdk\node_modules\.bin\anthropic-ai-sdk.cmd
node-which.cmd       E:\ClaudeEnvironment\npm_global\node_modules\@gsd-build\sdk\node_modules\.bin\node-which.cmd

PS C:\Windows\System32>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## PS C:\Windows\System32> Get-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName

Name                 FullName
----                 --------
claude-hud.cmd       E:\ClaudeEnvironment\npm_global\claude-hud.cmd
claude.cmd           E:\ClaudeEnvironment\npm_global\claude.cmd
ecc-install.cmd      E:\ClaudeEnvironment\npm_global\ecc-install.cmd
ecc.cmd              E:\ClaudeEnvironment\npm_global\ecc.cmd
get-shit-done-cc.cmd E:\ClaudeEnvironment\npm_global\get-shit-done-cc.cmd
gsd-sdk.cmd          E:\ClaudeEnvironment\npm_global\gsd-sdk.cmd
openspec.cmd         E:\ClaudeEnvironment\npm_global\openspec.cmd
playwright-core.cmd  E:\ClaudeEnvironment\npm_global\playwright-core.cmd
node-which.cmd       E:\ClaudeEnvironment\npm_global\node_modules\@fission-ai\openspec\node_modules\.bin\node-which.cmd
yaml.cmd             E:\ClaudeEnvironment\npm_global\node_modules\@fission-ai\openspec\node_modules\.bin\yaml.cmd
anthropic-ai-sdk.cmd E:\ClaudeEnvironment\npm_global\node_modules\@gsd-build\sdk\node_modules\.bin\anthropic-ai-sdk.cmd
node-which.cmd       E:\ClaudeEnvironment\npm_global\node_modules\@gsd-build\sdk\node_modules\.bin\node-which.cmd

PS C:\Windows\System32>

真相大白了！从你抓取的文件列表来看，文件确实都在 E:\ClaudeEnvironment\npm_global 目录下，但它们的命令名称（Alias）和你之前尝试输入的略有不同。
由于你安装的是最新版本或特定分支，命令名发生了变化。请看下表对比：
1. 正确的命令映射表
请根据你搜索出来的 Name 列，改用以下命令：






























你想运行的工具你应该输入的命令列表中的证据GSDget-shit-done-ccget-shit-done-cc.cmdOpenSpecopenspecopenspec.cmdGSD SDKgsd-sdkgsd-sdk.cmdECCeccecc.cmd

2. 为什么 gsd 和 opsx 不行？

GSD: 你的版本被命名为了 get-shit-done-cc（CC 代表 Claude Code 专版）。
OpenSpec: 你的版本没有使用简写 opsx，而是全拼 openspec。

3. 立即验证
请在当前的 PowerShell 窗口直接输入以下命令（由于路径已经添加过，现在应该能通了）：
get-shit-done-cc --version
openspec --version
ecc --help


4. 最终优化：如果你觉得命令太长（设置别名）
作为追求“极简精准”和“工业级效率”的专业人士，如果你觉得打 get-shit-done-cc 太麻烦，可以在你的 PowerShell 配置文件里加两个快捷方式（别名）。
执行这两行代码，把它们缩短回你习惯的样子：
# 将 get-shit-done-cc 缩写为 gsd
function gsd { & get-shit-done-cc @args }

# 将 openspec 缩写为 opsx
function opsx { & openspec @args }

5. 关于 Superpowers 的特别说明
由于你已经安装了 Superpowers，现在你的 E:\ClaudeEnvironment\npm_global 下应该还有 spw 或类似的命令（虽然你刚才的列表里没显示，可能是因为安装路径不同）。
现在，你的全套工具已经准备就绪：

用 openspec 定需求。
用 get-shit-done-cc 跑流程。
用 ecc 管理环境。

恭喜！这一波“深蹲”式的环境配置终于结束了，可以开始享受 AI 自动化的乐趣了！

---
*从 Gemini 导出，2026-05*
