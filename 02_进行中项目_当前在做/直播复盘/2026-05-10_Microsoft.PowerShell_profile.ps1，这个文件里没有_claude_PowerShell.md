---
title: Microsoft.PowerShell_profile.ps1，这个文件里没有内容
source: gemini
date: 2026-05-10
category: 系统运维
tags: [gemini, 系统运维]
---

## Microsoft.PowerShell_profile.ps1，这个文件里没有内容

这是完全正常的。Microsoft.PowerShell_profile.ps1 默认情况下就是一个不存在或空白的文件，它就像一张白纸，等着你把“开机指令”写上去。
既然文件是空的，我们直接把刚才的配置“全量植入”即可。
🛠️ 操作步骤


直接编辑：
在 PowerShell 中运行（如果刚才没关就直接在那写）：
notepad $PROFILE



复制并粘贴以下内容：
（我根据你的描述，为你精准定制了这两个入口）


# ==========================================
# Claude 生产力环境配置 (Michael's Workstation)
# ==========================================

# 1. DeepSeek 直连入口
function claude-ds {
    $env:CLAUDE_API_KEY = "这里填你的DeepSeek-Claude-Key"
    $env:CLAUDE_BASE_URL = "这里填DeepSeek的API地址" # 通常是 https://api.deepseek.com/v1
    Write-Host "🚀 已切换至 DeepSeek 直连环境" -ForegroundColor Cyan
    claude
}

# 2. GPTSAPI 中转入口
function claude-gpt {
    $env:CLAUDE_API_KEY = "这里填你的GPTSAPI-Key"
    $env:CLAUDE_BASE_URL = "这里填GPTSAPI的中转地址"
    Write-Host "🌐 已切换至 GPTSAPI 中转环境" -ForegroundColor Yellow
    claude
}

# 默认加载路径 (进入你重构后的项目根目录)
cd E:\Mycodeprojects



保存并退出记事本。


强制刷新环境（这一步至关重要）：
在 PowerShell 中输入：
. $PROFILE




💡 现在的终极工作流
现在你每次打开电脑，想开始工作时，只需要：

想用 DeepSeek？ 输入 claude-ds
想用中转 API？ 输入 claude-gpt

它会自动帮你完成：1. 切换 API 秘钥 -> 2. 切换服务器地址 -> 3. 自动进入 E:\Mycodeprojects 目录 -> 4. 启动 Claude 命令行。

⚠️ 一个可能的“安全报错”拦截
如果你运行 . $PROFILE 时报错说 “在此系统上禁止运行脚本”，请执行下面这行命令解锁权限：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

（选 [Y] 是）
🔍 现状确认
Michael，现在你的“拨号系统”已经植入到 PowerShell 的灵魂里了。
既然登录已经自动化，刚才那个因为找不到 instructions.md 而报错的 start_audit.py，我已经为你修复了路径。你要不要尝试输入 python 02-审计工具\start_audit.py 看看现在是否能正常拉起凡姐直播间的审计界面？

---
*从 Gemini 导出，2026-05*
