---
title: Prompted
source: gemini
date: 2026-05-07
category: 文案创意
old_category: 系统运维
tags: [gemini, 文案创意]
---

## Prompted

## Prompted

看来您已经尝试运行命令了，但目前遇到了两个小卡点。别担心，按照下面的步骤操作就能搞定：
1. 解决“Not logged in”报错
从截图看，Claude Code 提示 "Not logged in · Please run /login"。这是因为所有的插件（包括 HUD）都需要在登录状态下才能获取额度和费用信息。

操作方法： 在终端直接输入并回车：
/login


后续： 它会弹出一个网页或验证码，按提示完成 Anthropic 账号登录即可。


2. 正确启用指令
您刚才输入的命令里似乎多了一些横线和重复内容。登录成功后，请确保输入以下标准格式：
/statusline claude-hud


3. 排查：如果还是没反应？
如果在登录后输入指令依然无效，可能是因为 claude-hud 这个包本身还没安装到您的全局环境中。
您可以先按 Ctrl+C 退出当前的 Claude 界面，在普通的 Windows 终端（Command Prompt 或 PowerShell）里运行：
npm install -g claude-hud

安装完成后，再次输入 claude 进入程序，然后运行 /statusline claude-hud。

💡 提示
如果您看到底部的红字变成了绿色的费用和百分比进度条，那就说明大功告成了！
登录过程中如果遇到网络问题（比如网页打不开），记得检查一下您的网络环境是否顺畅。

---
*从 Gemini 导出，2026-05*

---
*从 Gemini 导出 · 分类: 文案创意 · 2026-05*
