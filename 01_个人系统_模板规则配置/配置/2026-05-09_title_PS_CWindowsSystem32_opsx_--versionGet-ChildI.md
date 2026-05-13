---
title: PS C:\Windows\System32> opsx --versionGet-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName
opsx: The term 'opsx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> Get-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName

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

PS C:\Windows\System32> get-shit-done-cc --version

   ██████╗ ███████╗██████╗
  ██╔════╝ ██╔════╝██╔══██╗
  ██║  ███╗███████╗██║  ██║
  ██║   ██║╚════██║██║  ██║
  ╚██████╔╝███████║██████╔╝
   ╚═════╝ ╚══════╝╚═════╝

  GSD Code-First v1.3.3
  Code-first development fork of GSD — build first, annotate,
  iterate. For Claude Code, OpenCode, Gemini, Codex, Copilot, Antigravity, Cursor, and Windsurf.

  Which runtime(s) would you like to install for?

  1) Claude Code  (~/.claude)
  2) OpenCode     (~/.config/opencode) - open source, free models
  3) Gemini       (~/.gemini)
  4) Codex        (~/.codex)
  5) Copilot      (~/.copilot)
  6) Antigravity  (~/.gemini/antigravity)
  7) Cursor       (~/.cursor)
  8) Windsurf     (~/.windsurf)
  9) All

  Select multiple: 1,4,6 or 1 4 6

  Choice [1]: 1
  Where would you like to install?

  1) Global (~\.claude) - available in all projects
  2) Local  (./.claude) - this project only

  Choice [1]: 1
  Installing for Claude Code to ~\.claude

  ✓ Installed commands/gsd
  ✓ Installed get-shit-done
  ✓ Installed agents
  ✓ Wrote VERSION (1.3.3)
  ✓ Wrote package.json (CommonJS mode)
  ✓ Installed hooks (bundled)
  ✓ Wrote file manifest (gsd-file-manifest.json)
  ✓ Configured update check hook
  ✓ Configured context window monitor hook
  ✓ Configured prompt injection guard hook

  ⚠ Existing statusline detected

  Your current statusline:
    command: powershell -ExecutionPolicy Bypass -File "C:\Users\think\.claude\plugins\cache\caveman\caveman\ef6050c5e184\hooks\caveman-statusline.ps1"

  GSD includes a statusline showing:
    • Model name
    • Current task (from todo list)
    • Context window usage (color-coded)

  1) Keep existing
  2) Replace with GSD statusline

  Choice [1]: 2

  Also install the GSD SDK?

  The SDK provides a standalone CLI for autonomous execution:
    gsd-sdk init @prd.md    Bootstrap a project from a PRD
    gsd-sdk auto            Run full autonomous lifecycle
    gsd-sdk run "prompt"    Execute a milestone from text

  1) No
  2) Yes (runs: npm install -g @gsd-build/sdk)

  Choice [1]: 2

  Installing GSD SDK...
  npm install -g @gsd-build/sdk@latest

\(node:18208) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

changed 99 packages in 16s

28 packages are looking for funding
  run `npm fund` for details

  ✓ GSD SDK installed (gsd-sdk command available)
  ✓ Configured statusline

  Done! Open a blank directory in Claude Code and run /gsd:new-project.

  Join the community: https://discord.gg/gsd

PS C:\Windows\System32> openspec --version
1.3.1
PS C:\Windows\System32> ecc --help
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## PS C:\Windows\System32> opsx --versionGet-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName
opsx: The term 'opsx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS C:\Windows\System32> Get-ChildItem -Path "E:\ClaudeEnvironment\npm_global" -Filter "*.cmd" -Recurse | Select-Object -Property Name, FullName

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

PS C:\Windows\System32> get-shit-done-cc --version

   ██████╗ ███████╗██████╗
  ██╔════╝ ██╔════╝██╔══██╗
  ██║  ███╗███████╗██║  ██║
  ██║   ██║╚════██║██║  ██║
  ╚██████╔╝███████║██████╔╝
   ╚═════╝ ╚══════╝╚═════╝

  GSD Code-First v1.3.3
  Code-first development fork of GSD — build first, annotate,
  iterate. For Claude Code, OpenCode, Gemini, Codex, Copilot, Antigravity, Cursor, and Windsurf.

  Which runtime(s) would you like to install for?

  1) Claude Code  (~/.claude)
  2) OpenCode     (~/.config/opencode) - open source, free models
  3) Gemini       (~/.gemini)
  4) Codex        (~/.codex)
  5) Copilot      (~/.copilot)
  6) Antigravity  (~/.gemini/antigravity)
  7) Cursor       (~/.cursor)
  8) Windsurf     (~/.windsurf)
  9) All

  Select multiple: 1,4,6 or 1 4 6

  Choice [1]: 1
  Where would you like to install?

  1) Global (~\.claude) - available in all projects
  2) Local  (./.claude) - this project only

  Choice [1]: 1
  Installing for Claude Code to ~\.claude

  ✓ Installed commands/gsd
  ✓ Installed get-shit-done
  ✓ Installed agents
  ✓ Wrote VERSION (1.3.3)
  ✓ Wrote package.json (CommonJS mode)
  ✓ Installed hooks (bundled)
  ✓ Wrote file manifest (gsd-file-manifest.json)
  ✓ Configured update check hook
  ✓ Configured context window monitor hook
  ✓ Configured prompt injection guard hook

  ⚠ Existing statusline detected

  Your current statusline:
    command: powershell -ExecutionPolicy Bypass -File "C:\Users\think\.claude\plugins\cache\caveman\caveman\ef6050c5e184\hooks\caveman-statusline.ps1"

  GSD includes a statusline showing:
    • Model name
    • Current task (from todo list)
    • Context window usage (color-coded)

  1) Keep existing
  2) Replace with GSD statusline

  Choice [1]: 2

  Also install the GSD SDK?

  The SDK provides a standalone CLI for autonomous execution:
    gsd-sdk init @prd.md    Bootstrap a project from a PRD
    gsd-sdk auto            Run full autonomous lifecycle
    gsd-sdk run "prompt"    Execute a milestone from text

  1) No
  2) Yes (runs: npm install -g @gsd-build/sdk)

  Choice [1]: 2

  Installing GSD SDK...
  npm install -g @gsd-build/sdk@latest

\(node:18208) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

changed 99 packages in 16s

28 packages are looking for funding
  run `npm fund` for details

  ✓ GSD SDK installed (gsd-sdk command available)
  ✓ Configured statusline

  Done! Open a blank directory in Claude Code and run /gsd:new-project.

  Join the community: https://discord.gg/gsd

PS C:\Windows\System32> openspec --version
1.3.1
PS C:\Windows\System32> ecc --help

恭喜！看到 openspec 成功返回版本号 1.3.1 以及 GSD SDK 的安装确认，标志着你的 “AI 工业级开发矩阵” 已经正式合体完毕。
作为一名资深的项目管理专家，你现在手中的工具链已经形成了一个闭环。

1. 工具链最终确认清单
你的 E:\ClaudeEnvironment\npm_global 路径已经生效，现在的“大将”调遣命令如下：

ecc: 环境管理。用于配置 MCP、搜索功能和系统级权限。
openspec: 架构设计。用于在写代码前制定 spec.md。
get-shit-done-cc (或 /gsd 指令): 流程控制。负责拆分任务和管理上下文。
gsd-sdk: 自动化执行。用于直接从 PRD 引导整个项目。
spw (Superpowers): 质量保障。通过 TDD 确保每一行代码都经过验证。


2. 第一次实战：如何启动你的项目？
既然你现在拥有了这些工具，建议你立即进入你的 E:\MyCodeProjects，启动 claude。你可以观察一下底部的 Statusline，它现在应该已经由 GSD 接管，显示着模型状态和上下文压力。
你可以按照以下“职业级”流程发起第一个任务：

架构先行：

/openspec:propose "为我的‘语义文件夹图标可视化’项目设计核心逻辑"


流程启动：

/gsd:new-project (这会基于刚才的 spec 开启任务追踪)


代码实现：

让 Claude 根据 GSD 拆分的第一个任务开始写代码，Superpowers 会自动介入确保测试通过。




3. 给你的最后一个“性能补丁”
你刚才在安装过程中看到了 NODE_TLS_REJECT_UNAUTHORIZED = '0' 的警告。这通常是为了绕过网络证书检查，虽然能用，但偶尔会引起某些 npm 包下载不完整。
建议：如果你之后在更新工具（比如 ecc-update）时遇到网络问题，可以尝试临时在 PowerShell 运行：
$env:NODE_TLS_REJECT_UNAUTHORIZED = "1"
来恢复正常安全检查。

总结建议：
你现在不需要再安装任何新东西了。你目前的配置已经非常厚重且专业。接下来的核心是**“让工具互相说话”**。
祝你的“AI 语义文件夹图标可视化”项目顺利启动！如果遇到多个工具（如 GSD 和 Superpowers）在 CLAUDE.md 里打架，随时把那部分代码贴给我，我帮你人工调优它们的权重。

---
*从 Gemini 导出，2026-05*
