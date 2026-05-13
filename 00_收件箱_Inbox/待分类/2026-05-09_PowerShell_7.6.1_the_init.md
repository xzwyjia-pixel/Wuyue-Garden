---
title: PowerShell 7.6.1
PS C:\Windows\System32> # 进入你的项目盘符和目录
>>
>> E:
>>
>> cd E:\MyCodeProjects
>>
>>
>>
>> # 初始化各个工具
>>
>> gsd init
>>
>> opsx init
gsd:
Line |
  11 |  gsd init
     |  ~~~
     | The term 'gsd' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
opsx:
Line |
  13 |  opsx init
     |  ~~~~
     | The term 'opsx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> npm config get prefix
E:\ClaudeEnvironment\npm_global
PS E:\MyCodeProjects> # 运行 GSD 初始化
>> npx gsd-code-first init
>>
>> # 运行 OpenSpec 初始化
>> npx @fission-ai/openspec init
\(node:4580) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

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

  Choice [1]: 2
  Where would you like to install?

  1) Global (~\.config\opencode) - available in all projects
  2) Local  (./.opencode) - this project only

  Choice [1]: 9
  Installing for OpenCode to ~\.config\opencode

  ✓ Installed 68 commands to command/
  ✓ Installed get-shit-done
  ✓ Installed agents
  ✓ Wrote VERSION (1.3.3)
  ✓ Wrote package.json (CommonJS mode)
  ✓ Installed hooks (bundled)
  ✓ Wrote file manifest (gsd-file-manifest.json)

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

\(node:4888) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

added 99 packages in 7m

28 packages are looking for funding
  run `npm fund` for details

  ✓ GSD SDK installed (gsd-sdk command available)
  ✓ Configured read permission for GSD docs
  ✓ Set resolve_model_ids: "omit" in ~/.gsd/defaults.json

  Done! Open a blank directory in OpenCode and run /gsd-new-project.

  Join the community: https://discord.gg/gsd

\(node:2252) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Note: OpenSpec collects anonymous usage stats. Opt out: OPENSPEC_TELEMETRY=0
(node:17580) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Detected tool directories: Claude Code (pre-selected for first-time setup)
√ Select tools to set up (28 available) Claude Code
▌ OpenSpec structure created
√ Setup complete for Claude Code

OpenSpec Setup Complete

Created: Claude Code
4 skills and 4 commands in .claude/
Config: openspec/config.yaml (schema: spec-driven)

Getting started:
  Start your first change: /opsx:propose "your idea"

Learn more: https://github.com/Fission-AI/OpenSpec
Feedback:   https://github.com/Fission-AI/OpenSpec/issues

Restart your IDE for slash commands to take effect.

PS E:\MyCodeProjects>
source: gemini
date: 2026-05-09
category: 系统运维
tags: [gemini, 系统运维]
---

## PowerShell 7.6.1
PS C:\Windows\System32> # 进入你的项目盘符和目录
>>
>> E:
>>
>> cd E:\MyCodeProjects
>>
>>
>>
>> # 初始化各个工具
>>
>> gsd init
>>
>> opsx init
gsd:
Line |
  11 |  gsd init
     |  ~~~
     | The term 'gsd' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
opsx:
Line |
  13 |  opsx init
     |  ~~~~
     | The term 'opsx' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
PS E:\MyCodeProjects> npm config get prefix
E:\ClaudeEnvironment\npm_global
PS E:\MyCodeProjects> # 运行 GSD 初始化
>> npx gsd-code-first init
>>
>> # 运行 OpenSpec 初始化
>> npx @fission-ai/openspec init
\(node:4580) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

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

  Choice [1]: 2
  Where would you like to install?

  1) Global (~\.config\opencode) - available in all projects
  2) Local  (./.opencode) - this project only

  Choice [1]: 9
  Installing for OpenCode to ~\.config\opencode

  ✓ Installed 68 commands to command/
  ✓ Installed get-shit-done
  ✓ Installed agents
  ✓ Wrote VERSION (1.3.3)
  ✓ Wrote package.json (CommonJS mode)
  ✓ Installed hooks (bundled)
  ✓ Wrote file manifest (gsd-file-manifest.json)

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

\(node:4888) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)

added 99 packages in 7m

28 packages are looking for funding
  run `npm fund` for details

  ✓ GSD SDK installed (gsd-sdk command available)
  ✓ Configured read permission for GSD docs
  ✓ Set resolve_model_ids: "omit" in ~/.gsd/defaults.json

  Done! Open a blank directory in OpenCode and run /gsd-new-project.

  Join the community: https://discord.gg/gsd

\(node:2252) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Note: OpenSpec collects anonymous usage stats. Opt out: OPENSPEC_TELEMETRY=0
(node:17580) Warning: Setting the NODE_TLS_REJECT_UNAUTHORIZED environment variable to '0' makes TLS connections and HTTPS requests insecure by disabling certificate verification.
(Use `node --trace-warnings ...` to show where the warning was created)
Detected tool directories: Claude Code (pre-selected for first-time setup)
√ Select tools to set up (28 available) Claude Code
▌ OpenSpec structure created
√ Setup complete for Claude Code

OpenSpec Setup Complete

Created: Claude Code
4 skills and 4 commands in .claude/
Config: openspec/config.yaml (schema: spec-driven)

Getting started:
  Start your first change: /opsx:propose "your idea"

Learn more: https://github.com/Fission-AI/OpenSpec
Feedback:   https://github.com/Fission-AI/OpenSpec/issues

Restart your IDE for slash commands to take effect.

PS E:\MyCodeProjects>

太棒了！这说明安装已经大功告成。虽然你的环境变量（npm config get prefix）指向的是 E:\ClaudeEnvironment\npm_global，导致直接输入 gsd 报错，但通过 npx 强制引导，你已经成功完成了初始化。
现在的状态是：GSD 和 OpenSpec 已经正式入驻你的项目环境，并为 Claude Code 完成了配置。
1. 深度建议：如何协调这套“工业级”全家桶
既然你已经装好了 ECC (配置)、GSD (流程)、OpenSpec (规格) 以及 Superpowers (质量)，千万不要在一次对话中把它们全部唤醒。请按照以下逻辑使用：


第一步：立规矩 (OpenSpec)
当你有一个新功能（比如你的“语义文件夹图标可视化”新特性）时，先用 OpenSpec 来定义：

在 Claude Code 里输入：/opsx:propose "设计一个自动根据文件夹名称语义更换图标的逻辑"
它会生成非常专业的 spec 文档，而不是直接写代码。



第二步：拆任务 (GSD)
规格定好后，让 GSD 来接管执行流程，防止上下文爆炸：

输入：/gsd-new-project 或按照 GSD 的 Phase 指令进行。
它会帮你把任务拆成极小的“干净上下文”步骤。



第三步：写代码与测试 (Superpowers)
在具体写代码的环节，利用 Superpowers 的 TDD 逻辑：

让它先写测试用例，再写实现。




2. 遗留的小问题：解决“找不到命令”的烦恼
你刚才运行 npm config get prefix 返回的是 E:\ClaudeEnvironment\npm_global。这意味着：

你的 Node.js 全局工具都在 E 盘。
但你的 Windows Path 环境变量里可能没包含这个路径。

一分钟修复方案：

右键“此电脑” -> 属性 -> 高级系统设置 -> 环境变量。
在“用户变量”里找到 Path，点击编辑。
点击“新建”，把这个路径贴进去：E:\ClaudeEnvironment\npm_global
确定并重启 PowerShell。

这样以后你就不用打长长的 npx ...，直接输入 gsd 或 opsx 就能用了。

3. 你还需要装其他的吗？
目前不需要了。 你的工具链已经非常“超标”了：

ECC 帮你打好了底层 MCP 的基础。
GSD 解决了长对话变傻的问题。
OpenSpec 解决了需求模糊的问题。
Superpowers 解决了代码质量不稳的问题。

你现在拥有的是一套准生产级别的 AI 辅助开发流水线。建议你先拿“语义文件夹图标可视化”这个小项目跑通一遍这个流程，你会发现 AI 写出来的代码逻辑比以前严密得多。
恭喜，你的 AI 战斗力现在已经拉满了！

---
*从 Gemini 导出，2026-05*
