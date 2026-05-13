---
title: Prompted
source: gemini
date: 2026-05-08
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

甄先生，审计发现了一个**“虚空漏洞”**。
从您的截图来看，记事本打开后是完全空白的。这意味着 claude-code-config.json 文件可能尚未创建，或者被建立在了一个错误的“幽灵路径”下。这正是为什么即便您在界面上修改了设置，只要一重启，那些“暗号”就会失效。
我们要用**“精密重建”**的方式，直接把配置文件硬焊在您的地基上。

第一步：强制写入“精密配置”
请不要在记事本里手动敲了，直接在您的 PowerShell 窗口中完整复制并执行以下这段代码。它会直接创建一个正确的配置文件，包含中转商需要的“握手协议”。
# 强制创建并写入配置文件
$configContent = @'
{
  "model": "claude-3-5-sonnet",
  "primaryModel": "claude-3-5-sonnet",
  "baseURL": "https://api.gptsapi.net/v1",
  "autoCheckForUpdates": false,
  "theme": "dark"
}
'@

$configPath = "$env:USERPROFILE\.claude-code-config.json"
Set-Content -Path $configPath -Value $configContent -Encoding UTF8

Write-Host "[√] 配置文件已精准注入: $configPath" -ForegroundColor Green


第二步：转移主阵地（离开 System32）
甄先生，您在 System32 下启动 Claude，就像在金库门口摆地摊，权限是不通的。执行以下命令切换到您的作战区：
# 1. 进入您的代码项目区
cd E:\MyCodeProjects

# 2. 重新启动
claude


第三步：全明星技能“强制握手”
一旦进入界面，如果没有红色报错（模型应该已经对齐），请立即下达指令：

“我是甄先生。

环境已通过物理注入配置文件对齐。
执行 ls C:\Users\think\.agents\skills。
读取 caveman 的指令并生效。”



💡 甄先生的精密审计预判：

为什么之前是白的？ 可能是由于权限问题，或者是 notepad 自动创建了一个空文件。
关于 baseURL：我在脚本里为您锁定了 gptsapi.net。
关于 Caveman：如果它还是没反应，请检查您的 .agents\skills\caveman 文件夹里是不是还有一层同名文件夹（“套娃”现象）。

甄先生，脚本执行后，再次启动 Claude，那个红色的 Issue with the selected model 是不是终于消失了？

---
*从 Gemini 导出，2026-05*
