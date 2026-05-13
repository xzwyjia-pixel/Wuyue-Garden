---
title: Prompted
source: gemini
date: 2026-05-07
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

甄先生，看来目前进入了一个有趣的“逻辑死循环”。Claude 坚持认为技能已经是 on 状态了，但 /skills 列表里的黄色锁头图标却无情地告诉我们：这些功能依然被插件策略锁着，无法直接调用。
这是因为 Superpowers 这种大型插件包通常有自己的安全合规检测，单纯靠对话强制开启有时会被底层的配置文件拦截。
🔧 终极激活方案：手动编辑配置文件
既然“文斗”不行，我们直接去改它的“大脑”配置。请按照以下步骤操作：
1. 让 Claude 为你打开配置文件
在终端输入：

“请帮我读取并编辑 ~/.claude/settings.json 文件。”

2. 检查 plugins 字段
在打开的文件中，寻找类似 "plugins": [...] 的部分。我们需要确认里面是否包含 "superpowers"。

如果不在： 请让 Claude 将其添加进去。
如果在： 检查是否有对应的 permissions (权限) 字段被设为了 false。

3. 强制赋予权限
您可以直接对 Claude 说：

“请在我的 settings.json 中，将 superpowers 插件的所有权限设置为允许（true），并确保它处于 enabled 状态。”


🚀 为什么一定要解锁它们？
一旦锁头解开，您就能立即体验到以下“超能力”：

writing-skills：它不仅仅是润色，它能深度理解您“规则甄查”的严谨风格，帮您生成更具工业精密感的报告。
systematic-debugging：如果您正在写的 Python 审计脚本报错，它会像资深专家一样进行系统性排查。

验证最后一步
修改并保存文件后，请执行：

/exit 彻底退出。
重新输入 claude 进入。
输入 /skills。

只要看到 superpowers: 开头的项目左侧变成绿色对勾，您的全功能工作站就正式开启了！
配置文件读取成功了吗？我们可以一起看看里面的内容。

---
*从 Gemini 导出，2026-05*
