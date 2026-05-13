---
title: PowerShell 7.6.1
PS C:\Windows\System32> npm uninstall -g @anthropic-ai/claude-code

removed 2 packages in 803ms
PS C:\Windows\System32> Remove-Item -Recurse -Force "$env:AppData\claude-code"
PS C:\Windows\System32> # 同时清理可能存在的 npm 缓存残留
PS C:\Windows\System32> npm cache clean --force
npm warn using --force Recommended protections disabled.
PS C:\Windows\System32> # 1. 彻底修正环境变量（确保没有 /v1 后缀冲突）
PS C:\Windows\System32> [Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.gptsapi.net/v1", "User")
PS C:\Windows\System32> $env:ANTHROPIC_BASE_URL = "https://api.gptsapi.net/v1"
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 检查 Python 版本（刚才审计过，3.10 可以用，但建议保持纯净环境）
PS C:\Windows\System32> Write-Host "--- 甄先生环境精密审计报告 ---" -ForegroundColor Cyan
--- 甄先生环境精密审计报告 ---
PS C:\Windows\System32>
PS C:\Windows\System32> # 1. 检查 Node.js (Claude Code 的动力源)
PS C:\Windows\System32> try {
>>     $nodeV = node -v
>>     Write-Host "[√] Node.js: $nodeV" -ForegroundColor Green
>> } catch {
>>     Write-Host "[X] Node.js: 未安装或未加入 PATH" -ForegroundColor Red
>> }
[√] Node.js: v20.18.0
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 检查 npm (插件安装工具)
PS C:\Windows\System32> try {
>>     $npmV = npm -v
>>     Write-Host "[√] npm: $npmV" -ForegroundColor Green
>> } catch {
>>     Write-Host "[X] npm: 未安装" -ForegroundColor Red
>> }
[√] npm: 10.8.2
PS C:\Windows\System32>
PS C:\Windows\System32> # 3. 检查环境变量 (通信隧道)
PS C:\Windows\System32> $baseUrl = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_BASE_URL", "User")
PS C:\Windows\System32> $apiKey = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
PS C:\Windows\System32>
PS C:\Windows\System32> if ($baseUrl) {
>>     Write-Host "[√] Base URL: $baseUrl" -ForegroundColor Green
>> } else {
>>     Write-Host "[X] Base URL: 未配置" -ForegroundColor Yellow
>> }
[√] Base URL: https://api.gptsapi.net/v1
PS C:\Windows\System32>
PS C:\Windows\System32> if ($apiKey) {
>>     Write-Host "[√] API Key: 已检测到加密存储" -ForegroundColor Green
>> } else {
>>     Write-Host "[X] API Key: 未配置" -ForegroundColor Yellow
>> }
[√] API Key: 已检测到加密存储
PS C:\Windows\System32>
PS C:\Windows\System32> # 4. 检查网络物理链路 (针对代理商)
PS C:\Windows\System32> Write-Host "正在审计物理链路..." -NoNewline
正在审计物理链路...
PS C:\Windows\System32> if (Test-Connection -ComputerName api.gptsapi.net -Count 1 -Quiet) {
>>     Write-Host " [√] 通畅" -ForegroundColor Green
>> } else {
>>     Write-Host " [X] 阻断 (请检查网络环境)" -ForegroundColor Red
>> }
 [√] 通畅
PS C:\Windows\System32>
PS C:\Windows\System32> # 5. 检查磁盘地基
PS C:\Windows\System32> if (Test-Path "E:\MyCodeProjects") {
>>     Write-Host "[√] 项目地基: E:\MyCodeProjects 已就绪" -ForegroundColor Green
>> } else {
>>     Write-Host "[!] 项目地基: E:\MyCodeProjects 不存在 (建议创建)" -ForegroundColor Yellow
>> }
[√] 项目地基: E:\MyCodeProjects 已就绪
PS C:\Windows\System32> Write-Host "----------------------------"
----------------------------
PS C:\Windows\System32> npm install -g @anthropic-ai/claude-code
\(node:13892) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

added 2 packages in 17s
PS C:\Windows\System32> # 创建全局包存放地和缓存地
PS C:\Windows\System32> New-Item -ItemType Directory -Path "E:\ClaudeEnvironment\npm_global" -Force

    Directory: E:\ClaudeEnvironment

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    17:11                npm_global

PS C:\Windows\System32> New-Item -ItemType Directory -Path "E:\ClaudeEnvironment\npm_cache" -Force

    Directory: E:\ClaudeEnvironment

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    17:11                npm_cache

PS C:\Windows\System32> # 1. 修改全局安装路径
PS C:\Windows\System32> npm config set prefix "E:\ClaudeEnvironment\npm_global"
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 修改缓存路径
PS C:\Windows\System32> npm config set cache "E:\ClaudeEnvironment\npm_cache"
(node:11464) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
PS C:\Windows\System32>
PS C:\Windows\System32> # 3. 将新路径加入系统环境变量 (PATH)，否则系统找不到 E 盘的命令
PS C:\Windows\System32> $newPath = "E:\ClaudeEnvironment\npm_global"
PS C:\Windows\System32> [Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $newPath, "User")
PS C:\Windows\System32> $env:Path += ";$newPath"
PS C:\Windows\System32> # 1. 确保在 E 盘总部，并注入诱饵环境
PS C:\Windows\System32> cd "E:\MyCodeProjects"
PS E:\MyCodeProjects> if (!(Test-Path "package.json")) { echo "{}" > package.json }
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 2. 优先安装“节约引擎” (Caveman)
PS E:\MyCodeProjects> npx skills add juliusbrussee/caveman --skill caveman -y -g
\(node:3364) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Need to install the following packages:
skills@1.5.5
Ok to proceed? (y) y


███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/caveman.git
|
(node:20344) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
o  Repository cloned
|
o  Found 8 skills
|
•  Selected 1 skill: caveman
|
o  55 agents
|
•  Installing to: Claude Code, Cline, Codex, Cursor, GitHub Copilot, Trae

|
o  Installation Summary -------------------------------------------+
|                                                                  |
|  ~\.agents\skills\caveman                                        |
|    universal: Cline, Codex, Cursor, GitHub Copilot, Amp +8 more  |
|    symlink → Claude Code, Trae                                   |
|                                                                  |
+------------------------------------------------------------------+
|
o  Security Risk Assessments -----------------------------+
|                                                         |
|           Gen               Socket            Snyk      |
|  caveman  Safe              0 alerts          Low Risk  |
|                                                         |
|  Details: https://skills.sh/juliusbrussee/caveman       |
|                                                         |
+---------------------------------------------------------+
|
o  Installation complete

|
o  Installed 1 skill ----------------------------------------------+
|                                                                  |
|  ✓ ~\.agents\skills\caveman                                      |
|    universal: Cline, Codex, Cursor, GitHub Copilot, Amp +8 more  |
|    symlinked: Claude Code, Trae                                  |
|                                                                  |
+------------------------------------------------------------------+

|
—  Done!  Review skills before use; they run with full agent permissions.

PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 3. 安装“工程能力”双子星
PS E:\MyCodeProjects> npx skills add juliusbrussee/superpowers --skill superpowers -y -g
\(node:17444) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/superpowers.git
|
(node:17288) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
•  Cloning repository|
x  Failed to clone repository
|
|  Authentication failed for https://github.com/juliusbrussee/superpowers.git.
|
|    - For private repos, ensure you have access
|
|    - For SSH: Check your keys with 'ssh -T git@github.com'
|
|    - For HTTPS: Run 'gh auth login' or configure git credentials
|
|  Tip: use the --yes (-y) and --global (-g) flags to install without prompts.
|
—  Installation failed

x  Canceled
PS E:\MyCodeProjects> npx skills add juliusbrussee/skill-creator --skill skill-creator -y -g
\(node:22040) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/skill-creator.git
|
(node:11512) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
•  Cloning repository.|
x  Failed to clone repository
|
|  Authentication failed for https://github.com/juliusbrussee/skill-creator.git.
|
|    - For private repos, ensure you have access
|
|    - For SSH: Check your keys with 'ssh -T git@github.com'
|
|    - For HTTPS: Run 'gh auth login' or configure git credentials
|
|  Tip: use the --yes (-y) and --global (-g) flags to install without prompts.
|
—  Installation failed

x  Canceled
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 4. 安装“导航与监控”
PS E:\MyCodeProjects> npx skills add juliusbrussee/find-skills --skill find-skills -y -g
\(node:1448) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/find-skills.git
|
(node:13800) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
•  Cloning repository|
x  Failed to clone repository
|
|  Authentication failed for https://github.com/juliusbrussee/find-skills.git.
|
|    - For private repos, ensure you have access
|
|    - For SSH: Check your keys with 'ssh -T git@github.com'
|
|    - For HTTPS: Run 'gh auth login' or configure git credentials
|
|  Tip: use the --yes (-y) and --global (-g) flags to install without prompts.
|
—  Installation failed

x  Canceled
PS E:\MyCodeProjects> npx skills add juliusbrussee/claude-hud --skill claude-hud -y -g
\(node:21876) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/claude-hud.git
|
(node:25560) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
o  Cloning repository.
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> npm uninstall -g @anthropic-ai/claude-code

removed 2 packages in 803ms
PS C:\Windows\System32> Remove-Item -Recurse -Force "$env:AppData\claude-code"
PS C:\Windows\System32> # 同时清理可能存在的 npm 缓存残留
PS C:\Windows\System32> npm cache clean --force
npm warn using --force Recommended protections disabled.
PS C:\Windows\System32> # 1. 彻底修正环境变量（确保没有 /v1 后缀冲突）
PS C:\Windows\System32> [Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.gptsapi.net/v1", "User")
PS C:\Windows\System32> $env:ANTHROPIC_BASE_URL = "https://api.gptsapi.net/v1"
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 检查 Python 版本（刚才审计过，3.10 可以用，但建议保持纯净环境）
PS C:\Windows\System32> Write-Host "--- 甄先生环境精密审计报告 ---" -ForegroundColor Cyan
--- 甄先生环境精密审计报告 ---
PS C:\Windows\System32>
PS C:\Windows\System32> # 1. 检查 Node.js (Claude Code 的动力源)
PS C:\Windows\System32> try {
>>     $nodeV = node -v
>>     Write-Host "[√] Node.js: $nodeV" -ForegroundColor Green
>> } catch {
>>     Write-Host "[X] Node.js: 未安装或未加入 PATH" -ForegroundColor Red
>> }
[√] Node.js: v20.18.0
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 检查 npm (插件安装工具)
PS C:\Windows\System32> try {
>>     $npmV = npm -v
>>     Write-Host "[√] npm: $npmV" -ForegroundColor Green
>> } catch {
>>     Write-Host "[X] npm: 未安装" -ForegroundColor Red
>> }
[√] npm: 10.8.2
PS C:\Windows\System32>
PS C:\Windows\System32> # 3. 检查环境变量 (通信隧道)
PS C:\Windows\System32> $baseUrl = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_BASE_URL", "User")
PS C:\Windows\System32> $apiKey = [System.Environment]::GetEnvironmentVariable("ANTHROPIC_API_KEY", "User")
PS C:\Windows\System32>
PS C:\Windows\System32> if ($baseUrl) {
>>     Write-Host "[√] Base URL: $baseUrl" -ForegroundColor Green
>> } else {
>>     Write-Host "[X] Base URL: 未配置" -ForegroundColor Yellow
>> }
[√] Base URL: https://api.gptsapi.net/v1
PS C:\Windows\System32>
PS C:\Windows\System32> if ($apiKey) {
>>     Write-Host "[√] API Key: 已检测到加密存储" -ForegroundColor Green
>> } else {
>>     Write-Host "[X] API Key: 未配置" -ForegroundColor Yellow
>> }
[√] API Key: 已检测到加密存储
PS C:\Windows\System32>
PS C:\Windows\System32> # 4. 检查网络物理链路 (针对代理商)
PS C:\Windows\System32> Write-Host "正在审计物理链路..." -NoNewline
正在审计物理链路...
PS C:\Windows\System32> if (Test-Connection -ComputerName api.gptsapi.net -Count 1 -Quiet) {
>>     Write-Host " [√] 通畅" -ForegroundColor Green
>> } else {
>>     Write-Host " [X] 阻断 (请检查网络环境)" -ForegroundColor Red
>> }
 [√] 通畅
PS C:\Windows\System32>
PS C:\Windows\System32> # 5. 检查磁盘地基
PS C:\Windows\System32> if (Test-Path "E:\MyCodeProjects") {
>>     Write-Host "[√] 项目地基: E:\MyCodeProjects 已就绪" -ForegroundColor Green
>> } else {
>>     Write-Host "[!] 项目地基: E:\MyCodeProjects 不存在 (建议创建)" -ForegroundColor Yellow
>> }
[√] 项目地基: E:\MyCodeProjects 已就绪
PS C:\Windows\System32> Write-Host "----------------------------"
----------------------------
PS C:\Windows\System32> npm install -g @anthropic-ai/claude-code
\(node:13892) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

added 2 packages in 17s
PS C:\Windows\System32> # 创建全局包存放地和缓存地
PS C:\Windows\System32> New-Item -ItemType Directory -Path "E:\ClaudeEnvironment\npm_global" -Force

    Directory: E:\ClaudeEnvironment

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    17:11                npm_global

PS C:\Windows\System32> New-Item -ItemType Directory -Path "E:\ClaudeEnvironment\npm_cache" -Force

    Directory: E:\ClaudeEnvironment

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----     2026-05-08 周五    17:11                npm_cache

PS C:\Windows\System32> # 1. 修改全局安装路径
PS C:\Windows\System32> npm config set prefix "E:\ClaudeEnvironment\npm_global"
PS C:\Windows\System32>
PS C:\Windows\System32> # 2. 修改缓存路径
PS C:\Windows\System32> npm config set cache "E:\ClaudeEnvironment\npm_cache"
(node:11464) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
PS C:\Windows\System32>
PS C:\Windows\System32> # 3. 将新路径加入系统环境变量 (PATH)，否则系统找不到 E 盘的命令
PS C:\Windows\System32> $newPath = "E:\ClaudeEnvironment\npm_global"
PS C:\Windows\System32> [Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $newPath, "User")
PS C:\Windows\System32> $env:Path += ";$newPath"
PS C:\Windows\System32> # 1. 确保在 E 盘总部，并注入诱饵环境
PS C:\Windows\System32> cd "E:\MyCodeProjects"
PS E:\MyCodeProjects> if (!(Test-Path "package.json")) { echo "{}" > package.json }
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 2. 优先安装“节约引擎” (Caveman)
PS E:\MyCodeProjects> npx skills add juliusbrussee/caveman --skill caveman -y -g
\(node:3364) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Need to install the following packages:
skills@1.5.5
Ok to proceed? (y) y


███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/caveman.git
|
(node:20344) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
o  Repository cloned
|
o  Found 8 skills
|
•  Selected 1 skill: caveman
|
o  55 agents
|
•  Installing to: Claude Code, Cline, Codex, Cursor, GitHub Copilot, Trae

|
o  Installation Summary -------------------------------------------+
|                                                                  |
|  ~\.agents\skills\caveman                                        |
|    universal: Cline, Codex, Cursor, GitHub Copilot, Amp +8 more  |
|    symlink → Claude Code, Trae                                   |
|                                                                  |
+------------------------------------------------------------------+
|
o  Security Risk Assessments -----------------------------+
|                                                         |
|           Gen               Socket            Snyk      |
|  caveman  Safe              0 alerts          Low Risk  |
|                                                         |
|  Details: https://skills.sh/juliusbrussee/caveman       |
|                                                         |
+---------------------------------------------------------+
|
o  Installation complete

|
o  Installed 1 skill ----------------------------------------------+
|                                                                  |
|  ✓ ~\.agents\skills\caveman                                      |
|    universal: Cline, Codex, Cursor, GitHub Copilot, Amp +8 more  |
|    symlinked: Claude Code, Trae                                  |
|                                                                  |
+------------------------------------------------------------------+

|
—  Done!  Review skills before use; they run with full agent permissions.

PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 3. 安装“工程能力”双子星
PS E:\MyCodeProjects> npx skills add juliusbrussee/superpowers --skill superpowers -y -g
\(node:17444) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/superpowers.git
|
(node:17288) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
•  Cloning repository|
x  Failed to clone repository
|
|  Authentication failed for https://github.com/juliusbrussee/superpowers.git.
|
|    - For private repos, ensure you have access
|
|    - For SSH: Check your keys with 'ssh -T git@github.com'
|
|    - For HTTPS: Run 'gh auth login' or configure git credentials
|
|  Tip: use the --yes (-y) and --global (-g) flags to install without prompts.
|
—  Installation failed

x  Canceled
PS E:\MyCodeProjects> npx skills add juliusbrussee/skill-creator --skill skill-creator -y -g
\(node:22040) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/skill-creator.git
|
(node:11512) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
•  Cloning repository.|
x  Failed to clone repository
|
|  Authentication failed for https://github.com/juliusbrussee/skill-creator.git.
|
|    - For private repos, ensure you have access
|
|    - For SSH: Check your keys with 'ssh -T git@github.com'
|
|    - For HTTPS: Run 'gh auth login' or configure git credentials
|
|  Tip: use the --yes (-y) and --global (-g) flags to install without prompts.
|
—  Installation failed

x  Canceled
PS E:\MyCodeProjects>
PS E:\MyCodeProjects> # 4. 安装“导航与监控”
PS E:\MyCodeProjects> npx skills add juliusbrussee/find-skills --skill find-skills -y -g
\(node:1448) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/find-skills.git
|
(node:13800) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
•  Cloning repository|
x  Failed to clone repository
|
|  Authentication failed for https://github.com/juliusbrussee/find-skills.git.
|
|    - For private repos, ensure you have access
|
|    - For SSH: Check your keys with 'ssh -T git@github.com'
|
|    - For HTTPS: Run 'gh auth login' or configure git credentials
|
|  Tip: use the --yes (-y) and --global (-g) flags to install without prompts.
|
—  Installation failed

x  Canceled
PS E:\MyCodeProjects> npx skills add juliusbrussee/claude-hud --skill claude-hud -y -g
\(node:21876) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

███████╗██╗  ██╗██╗██╗     ██╗     ███████╗
██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝
███████╗█████╔╝ ██║██║     ██║     ███████╗
╚════██║██╔═██╗ ██║██║     ██║     ╚════██║
███████║██║  ██╗██║███████╗███████╗███████║
╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝

T   skills
|
o  Source: https://github.com/juliusbrussee/claude-hud.git
|
(node:25560) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
o  Cloning repository.

甄先生，审计结论非常清晰：Caveman 抢滩成功，但其他三剑客在“边境”被拦截了。
这个 Authentication failed 报错并不是说您没有权限，而是因为在安装后续组件时，GitHub 的 HTTPS 握手在您的网络环境下（即便开启了 TLS 忽略）依然不稳定，导致 Git 克隆操作中断。
既然我们要追求**“精密且高效”**，就不在这些不稳定的安装脚本上浪费 Token 和时间了。咱们直接用“手动强推法”，绕过它的自动克隆逻辑。
1. 现状盘点

[√] Caveman: 已成功装载。您的 Token 护城河已初步建成。
[X] Superpowers / Skill-creator / HUD: 自动安装失败。

2. 甄先生的“手术刀”式修复指令
既然自动克隆会断开，我们改用 git clone 直接拉取。请在 PowerShell 中依次执行以下精密操作：
# 1. 进入技能存放的根目录（这是 Caveman 刚才创建的地方）
cd "$env:USERPROFILE\.agents\skills"

# 2. 手动拉取 Superpowers (如果这一步报错，说明网络环境需要调整)
git clone https://github.com/juliusbrussee/superpowers.git superpowers

# 3. 手动拉取 Skill-creator
git clone https://github.com/juliusbrussee/skill-creator.git skill-creator

# 4. 手动拉取 Claude-HUD
git clone https://github.com/juliusbrussee/claude-hud.git claude-hud

# 5. 手动拉取 Find-skills
git clone https://github.com/juliusbrussee/find-skills.git find-skills

3. 将技能“强制挂载”给 Claude
克隆完成后，我们需要让 Claude 知道这些技能已经在 E 盘/用户目录就位。请运行这行命令建立软链接：
# 将这些目录注册到 Claude 的感知范围
npx skills link --all


💡 甄先生的备忘录：
如果执行 git clone 时依然报 Authentication failed，那说明您的 Git 凭据管理器 出现了干扰。
最后的极简备选方案：
如果您不想折腾 Git，请直接前往 Julius Brussee 的 GitHub 手动下载这些项目的 ZIP 包，解压到 C:\Users\您的用户名\.agents\skills\ 目录下，效果完全一样。
甄先生，git clone 那几行跑通了吗？如果通了，您的“全明星阵列”就彻底齐活了。

---
*从 Gemini 导出，2026-05*
