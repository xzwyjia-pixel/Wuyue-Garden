---
title: 我希望把这个任务在Claude里面的superpowers来完成
source: gemini
date: 2026-05-08
category: 编程开发
tags: [gemini, 编程开发]
---

## 我希望把这个任务在Claude里面的superpowers来完成

既然你决定调用 Claude 的 "Superpowers"（也就是深度推理、多文件处理和全自动代码构建能力），那我们就不能把它当成简单的聊天框，而是要把它当作一个资深系统架构师+全栈工程师。
要在 Claude 中完美实现这个任务，建议你开启一个全新的 Project（项目），并按照以下“超级指令”序列进行操作：

第一步：构建项目上下文 (System Instructions)
在 Claude 项目的 Custom Instructions 或初始对话中，输入这段高度结构化的背景，这能激活它对 Windows 底层 API 的认知：

Role: Windows System Level Developer & NLP Expert
Task: 开发“基于语义分析的 Windows 文件夹图标动态映射与注入工具”
Tech Stack: Python, Watchdog, Win32 API, Local LLM/NLP (scikit-learn), PyQt6.
Constraint: 必须严格遵守 Windows desktop.ini 写入规范，确保 .ico 路径处理支持相对路径，且必须包含 Shell 刷新逻辑防止图标显示延迟。


第二步：分阶段“全自动”执行方案
不要让它一次性吐出几千行代码，按以下 superpower 指令分块推进：
1. 核心注入引擎（底层突破）
Prompt:

“请生成核心模块 injector.py。

实现文件夹属性修改逻辑（attrib +s +r）。
生成 desktop.ini，配置 IconResource 和 InfoTip。
使用 ctypes 调用 SHChangeNotify 强制系统刷新缓存。
编写一个测试函数，将 C:\Test 文件夹图标改为 D:\icons\code.ico。”


2. 语义分析与特征提取（大脑构建）
Prompt:

“现在开发 analyzer.py。

设计一个多重扫描逻辑：优先根据文件夹名关键词匹配，其次根据内部文件后缀占比（如 .py > 30% 为代码项目）。
集成一个简单的 NLP 分类器：如果文件夹名是中文，使用关键词权重算法识别意图（例如‘照片’、‘旅游’归类为 Image 标签）。
预留 API 接口，以便后续接入 Ollama 或本地 Transformer 模型进行深度语义理解。”


3. 实时监控服务（自动化感知）
Prompt:

“开发 monitor.py。

使用 watchdog 库实现后台常驻。
当有新文件夹创建、更名或内部文件大量增加时，延迟 3 秒触发 analyzer.py。
必须包含防抖逻辑（Debounce），避免频繁读写磁盘。”



第三步：利用 Claude 的 Artifacts 进行调试
如果你使用的是 Claude 3.5 Sonnet，它会开启 Artifacts 窗口展示 UI 预览或完整的代码架构图。

UI 协同： 让它生成 PyQt6 的界面代码。你可以对它说：“在 Artifacts 中展示这个软件的设置界面，我需要能看到监控文件夹列表和图标映射表。”
逻辑纠错： 如果注入后图标没变，直接截图目录属性发给它，利用它的视觉能力分析 desktop.ini 是否编码错误（通常需要 UTF-16 LE 编码）。


第四步：极客进阶（这才是真正的 Superpower）
如果你想让软件更聪明，给 Claude 下达这个指令：

“请为我设计一个**‘反馈闭环’**。如果用户手动更改了某个被我软件修改过的图标，程序应通过 Windows 事件日志捕获这一行为，并更新语义分析的权重模型，实现‘学习’用户的分类偏好。”


⚠️ 避坑检查点 (Claude 可能会遗漏的细节)
在生成过程中，你要通过追问确保它处理了以下问题：

权限问题：修改系统盘（C盘）文件夹通常需要管理员权限，让 Claude 生成一个 uac_elevator.py 脚本。
性能消耗：如果扫描几万个小文件会卡顿，要求它实现异步扫描（asyncio）。
图标来源：让 Claude 帮你写一个简单的爬虫脚本，自动从特定的开源图标库下载符合语义标签的 .ico 文件。

你现在准备好在 Claude 开启这个 Project 了吗？建议从“核心注入引擎”开始第一步。

---
*从 Gemini 导出，2026-05*
