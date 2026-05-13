---
title: Prompted
source: gemini
date: 2026-05-07
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

看来这个指令在当前的 Claude Code 版本中有点“傲娇”。出现 Unknown command: /install-skill 通常是因为该指令是某些插件包自带的，或者在当前的环境变量下没被识别。
别担心，我们换一种“百分之百成功”的办法：
替代安装方法
请直接在对话框里（就像刚才发“你好”那样）对 Claude 说：

“请帮我安装 skill-creator 技能。”

或者输入：

“Install the skill-creator skill.”


为什么这样做有效？
Claude Code 本身具备“自管理”能力。当你通过对话告诉它安装某个 Skill 时，它会自动调用内部的 agent 去 GitHub 或 npm 寻找对应的包并自动完成配置，这比手动输入斜杠指令更智能。
安装成功后的样子：
一旦它操作完成，你可以输入以下指令确认：
/skills

如果在列表中看到了 skill-creator，就说明它已经就位了。
顺便观察一下：
你刚才重启了吗？如果重启成功了，现在的窗口最底部（就在那行长长的白线下面）应该已经出现了一行彩色的状态信息了。如果还是黑漆漆的，试着把窗口再往上拉高一点。

---
*从 Gemini 导出，2026-05*
