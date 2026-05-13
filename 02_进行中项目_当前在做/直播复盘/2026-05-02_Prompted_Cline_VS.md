---
title: Prompted
source: gemini
date: 2026-05-02
category: 文案创意
old_category: 编程开发
tags: [gemini, 文案创意]
---

## Prompted

## Prompted

从这张截图可以看到，你已经成功进入了 VS Code 的 MCP 全局设置界面。
在 cline_mcp_settings.json 文件中，你已经完成了代码编写，文件也已经确认存在于 E:\MCP-Skills\tutor_server.py。
最后的关键操作：
要让 tutor-skills 真正“活”起来，请按以下步骤操作：


保存配置文件：
确保你后台那个 cline_mcp_settings.json 文件已经保存（按下 Ctrl + S）。


信任当前窗口：
观察 VS Code 最底部状态栏左侧，如果还有一个蓝色的 "Restricted Mode"（受限模式）图标，请点击它并选择 "Trust"。不信任该窗口，VS Code 是不会允许插件调用本地 Python 脚本的。


刷新 Cline 插件：

关闭当前的 Settings 窗口。
在 VS Code 最左侧活动栏点击 Cline 图标（那个小机器人头像）。
在 Cline 面板的右上方，点击那个 “小齿轮” 进入插件内部设置，或者点击 "MCP Servers" 旁边的 刷新（圆圈箭头） 按钮。



如何确认已经成功？
当你在 Cline 的聊天框输入任务时，观察输入框上方或工具列表。如果出现了 tutor-skills 相关的工具图标（或者状态灯变绿），说明已经成功挂载。

给“甄先生”的第一个任务建议：
既然环境已经搭好了，你可以直接在左侧 Cline 聊天框里输入这段指令来试运行：

“你好，我是甄先生。请调用 tutor_setup 工具，扫描我的项目路径 E:\MyCodeProjects\RulesBureau。初始化完成后，请针对‘短视频风控审计逻辑’给我出三道测试题。”

如果插件报错或者没有出现工具：
请检查 VS Code 底部 "Output"（输出）通道，在下拉菜单中选择 "Cline MCP: tutor-skills"，把里面的报错日志发给我，我来帮你排查。

---
*从 Gemini 导出，2026-05*

---
*从 Gemini 导出 · 分类: 文案创意 · 2026-05*
