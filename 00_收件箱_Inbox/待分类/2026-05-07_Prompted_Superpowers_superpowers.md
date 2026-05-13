---
title: Prompted
source: gemini
date: 2026-05-07
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

从你提供的最后一张截图来看，Superpowers 技能包已经安装在你的系统中了。
目前这些技能显示为 locked by plugin (被插件锁定) 且左侧有 锁头图标，这通常意味着该插件包尚未获得完整的运行授权，或者需要通过特定的指令来激活。
激活 Superpowers 的步骤：


尝试一键激活：
在终端输入并回车：
/plugin add superpowers

或者直接对 Claude 说：

“请激活并开启所有 superpowers 相关的技能。”



手动批量开启：
如果上述命令无效，你可以尝试直接针对某个具体技能进行授权，例如：
/skill enable superpowers:writing-skills



检查配置文件权限：
由于 Superpowers 包含多个子插件（如 brainstorming, systematic-debugging 等），它可能需要再次读取你的 .claude/settings.json。

如果弹出权限请求，请务必选择 Yes, allow reading from .claude/ during this session（类似你之前配置 HUD 时的操作）。



为什么这一步很重要？
一旦这些技能左侧的图标从“锁头”变成 绿色对勾，你就可以：

使用 writing-skills 来润色你的“规则甄查”文案。
使用 systematic-debugging 来优化你的 Python 审计脚本。
配合你刚手搓出来的 skill-creator，实现更高级的自动化。

甄先生，操作完记得输入 /skills 确认一下。如果锁头还在，请告诉我，我们可能需要手动修改一下 settings.json 的插件列表。

---
*从 Gemini 导出，2026-05*
