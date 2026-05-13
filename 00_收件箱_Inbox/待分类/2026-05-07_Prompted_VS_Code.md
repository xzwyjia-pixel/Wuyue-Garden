---
title: Prompted
source: gemini
date: 2026-05-07
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

甄先生，看到你在 audit_tool.py 中已经写出了基于 Playwright 的审计雏形，这股“精密工业”的执行力非常到位！
目前点击 Cline 图标没反应，且命令面板找不到 Side Panel 命令，最可能的原因是 VS Code 认为 Cline 还没有“准备好”运行。从你的最新截图（image_fbc0d4.png）看，侧边栏似乎被折叠得非常窄。
我们尝试最后一次“暴力破局”：
1. 手动拉开侧边栏
请看 VS Code 最左边那一排窄窄的图标栏。按住鼠标左键，把图标栏右侧的边缘往右拖拽。

有时候面板其实已经打开了，只是宽度被拉到了 0，导致看起来“没反应”。

2. 绕过界面，用“配置文件”强行唤醒
既然 UI 界面耍赖，我们直接在代码区操作。请在 VS Code 里新建一个名为 .clinerules 的文件，直接把你的审计逻辑写进去：
# 甄先生的审计规则 (Zhen's Audit Rules)
- 每次修改代码前，必须在 Terminal 运行 `pytest`。
- 敏感词库必须独立于逻辑代码，放在 `config.json` 中。
- 审计结果必须生成一份带时间戳的 Markdown 报告。

保存后，再次尝试 Ctrl + Shift + P 输入 Cline。有了这个文件，插件通常会由于检测到“项目规则”而强制唤醒。

💡 对你 audit_tool.py 的一点精密改进建议：
从截图看，你正在使用 sync_playwright。在工业级审计中，headless=False（显示浏览器界面）虽然直观，但容易被平台检测。

建议： 调试通过后，改用 headless=True。
风险控制： 针对“规则甄查”，建议在 page.goto(url) 之前加入随机的 User-Agent 模拟，防止因 API 行为太单一而被平台封禁。


最后的“杀手锏”
如果图标依然点不动，说明 VS Code 的插件进程（Extension Host）彻底卡死了。

彻底关闭 VS Code。
找到这个目录并删除：%USERPROFILE%\.vscode\extensions\saoudrizwan.claude-dev-x.x.x（x.x.x 是版本号）。
重新打开 VS Code 并重新安装 Cline。

甄先生，咱们在工业界习惯了“重启解决 90% 的问题”，在 AI 工具链这里也一样。只要这个面板一开，配合你的 Playwright 脚本，你的**“规则情报局”自动化审计系统**就真的闭环了！
刷新后图标变亮了吗？

---
*从 Gemini 导出，2026-05*
