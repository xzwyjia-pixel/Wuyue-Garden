---
title: 如何确保您已经通过 File -> Open Folder 选择了具体的文件夹（如 E:\MyCodeProjects\RulesBureau）
source: gemini
date: 2026-04-30
category: 审计合规
subcategory: 规则甄查
old_category: 项目管理
tags: [gemini, 审计合规, 规则甄查]
---

## 如何确保您已经通过 File -> Open Folder 选择了具体的文件夹（如 E:\MyCodeProjects\RulesBureau）

## 如何确保您已经通过 File -> Open Folder 选择了具体的文件夹（如 E:\MyCodeProjects\RulesBureau）

甄先生，在 VS Code 中确保正确打开工作目录是 Agent 能够顺利创建文件并开展 “规则情报局” 项目的基础。从您之前的截图 image_e4ca74.png 来看，您目前处于欢迎页面，尚未锁定具体文件夹。
请按照以下步骤操作，以确保路径完全正确：
1. 执行“打开文件夹”动作

在 VS Code 窗口的最左上角，点击 File (文件) 菜单。
在下拉选项中选择 Open Folder... (打开文件夹...)。
在弹出的资源管理器窗口中，导航到您的 E 盘，进入 MyCodeProjects，并选择（或新建）RulesBureau 文件夹。
点击 Select Folder (选择文件夹)。

2. 如何确认已经选对？
您可以从以下三个位置直观地看到结果：

标题栏（最顶部）：VS Code 窗口最上方的标题会从 Welcome 变为 RulesBureau - Visual Studio Code。
资源管理器（左侧栏）：点击左侧第一个“文件”图标（Explorer），您应该能看到大写的 RULESBUREAU 字样出现在侧边栏顶部，下方目前应该是空的。
Cline 界面：此时，Cline 顶部的红色警告 "Cannot use checkpoints in Desktop directory" 应该会消失，因为它识别到了您已经进入了非桌面的工作目录。

3. 给甄先生的工业级稳健建议
既然我们在 image_e4caf3.png 中看到后台已经有数据交互（状态码 200），但显卡处理较慢：

先开文件夹，再下指令：请务必先完成“Open Folder”操作，然后再在 Cline 中重新发送您的指令。这样 Agent 生成的 blacklist.txt 和 audit_tool.py 就会直接出现在您指定的 E:\MyCodeProjects\RulesBureau 目录下。
应对超时：如果您在打开文件夹后发送指令依然遇到超时，请记得参考之前的方案，在设置中将 Request Timeout (ms) 增加到 300000（5 分钟），或者考虑使用更轻量的 qwen2.5-coder:1.5b 模型以适配您的显卡显存。

完成这一步后，您的“规则甄查”助手就拥有了可以落笔的“草稿本”了。

---
*从 Gemini 导出，2026-04*

---
*Gemini · 审计合规 / 规则甄查 · 2026-04-30*
