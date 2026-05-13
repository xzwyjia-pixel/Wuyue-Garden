---
title: # 规则甄查 · DeepSeek 官方直连启动器
# ThinkPad P15V - E:\MyCodeProjects
# 编码: UTF-8

$env:ANTHROPIC_BASE_URL             = "https://api.deepseek.com/anthropic"
$env:ANTHROPIC_API_KEY              = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
$env:CLAUDE_CODE_MAX_CONTEXT_TOKENS = "32768"

Write-Host ">>> 正在尝试直连 DeepSeek 官网 - 高性能模式" -ForegroundColor Green

npx @anthropic-ai/claude-code
是修改成这样吗？
source: gemini
date: 2026-05-09
category: 审计合规
tags: [gemini, 审计合规]
---

## # 规则甄查 · DeepSeek 官方直连启动器
# ThinkPad P15V - E:\MyCodeProjects
# 编码: UTF-8

$env:ANTHROPIC_BASE_URL             = "https://api.deepseek.com/anthropic"
$env:ANTHROPIC_API_KEY              = "sk-cad1b7bcd5dd4644a03c87c14a1fa690"
$env:CLAUDE_CODE_MAX_CONTEXT_TOKENS = "32768"

Write-Host ">>> 正在尝试直连 DeepSeek 官网 - 高性能模式" -ForegroundColor Green

npx @anthropic-ai/claude-code
是修改成这样吗？

是的，修改完全正确。这种配置精准地避开了之前困扰你的路径解析错误，同时也符合你对 ThinkPad P15V 环境的专业管理要求。
脚本修改要点说明

启动指令：使用 npx @anthropic-ai/claude-code 代替原本的 cmd.exe /c "claude"，这将强制系统直接调用 npm 包内的执行程序，绕过受损的 claude.cmd 软链接。
直连配置：你设置的 [https://api.deepseek.com/anthropic](https://api.deepseek.com/anthropic) 和相应的 API Key 是打通 DeepSeek 官方直连 的关键，这能确保你在进行 “规则甄查”系统 测试时享受最低的消耗和最高的响应速度。
上下文控制：32768 的 Token 限制设置得非常合理，既能满足你分析长篇平台规则的需求，又能有效控制 Token 消耗。


下一步操作建议

保存文件：请确保已在记事本中按下 Ctrl + S 保存该文件。
独立运行测试：

在 E:\MyCodeProjects 文件夹空白处，按住 Shift + 右键，选择 “在此处打开 PowerShell 窗口”。
输入 .\start-claude-direct.ps1 并回车。


权限确认：

如果启动后 Cline 再次询问读取文件的权限（如你之前看到的 image_fdc796.png 界面），直接点击 “批准” 即可。
此时程序会自动加载你当前目录下的所有审计服务器代码和规则资料。



这种修改方式对你正在进行的 VS Code 工作没有任何干扰，你可以放心地在独立终端中跑通你的“规则甄查”审计逻辑。

---
*从 Gemini 导出，2026-05*
