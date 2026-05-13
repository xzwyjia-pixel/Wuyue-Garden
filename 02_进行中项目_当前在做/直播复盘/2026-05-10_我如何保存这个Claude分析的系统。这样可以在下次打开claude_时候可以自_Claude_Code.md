---
title: 我如何保存这个Claude分析的系统。这样可以在下次打开claude 时候可以自动执行
source: gemini
date: 2026-05-10
category: 直播运营
tags: [gemini, 直播运营]
---

## 我如何保存这个Claude分析的系统。这样可以在下次打开claude 时候可以自动执行

要实现“下次打开 Claude 即可自动执行”，核心在于将这套逻辑从**“临时对话指令”固化为“本地工程资产”**。
由于 Claude Code 的运行环境是基于你本地 E:\MyCodeProjects 文件夹的，我们可以通过以下三个步骤把这套“审计系统”变成一个一键启动的工具箱。

1. 固化“系统说明书” (The System Prompt File)
让 Claude 每次打开都能记起它的“身份”和“逻辑”。
操作： 让 Claude 在你的项目根目录下创建一个 .claude_rules 或 README_SYSTEM.md。

给 Claude Code 的指令：
请在 E:\MyCodeProjects 下创建一个 instructions.md。

内容： 详细记录“大山里的小桃”监控系统的核心参数（如模糊匹配阈值 0.5、热区坐标、人设评分加权公式、以及针对“清晨烟火”的对标维度）。
作用： 明确告诉任何后续接入的 AI 助理，这套系统的目标是做“直播间人设审计”。
自启动声明： 写明“下次当我提到‘启动直播审计’时，请自动检查 monitor_桃.py 环境并准备执行”。



2. 封装“一键启动”脚本 (The Launcher)
你不需要记那么多命令，只需要运行一个简单的入口文件。
操作： 让 Claude 写一个 start_audit.py。

给 Claude Code 的指令：
请创建一个 start_audit.py，作为系统的总开关：

功能： 运行后先自动检查依赖环境（EasyOCR, PyAutoGUI），然后自动清理 temp_frames。
自适应： 增加一个 select_target() 函数。启动时询问我：“监控哪个直播间？1. 大山里的小桃 2. 清晨烟火 3. 自定义”。
启动： 根据选择直接调用对应的 .py 脚本。



3. 利用 .clauderc 实现“记忆唤醒”
如果你使用的是 Claude Code 命令行工具，它支持配置文件。
操作： 让 Claude 检查或创建配置文件，使其在加载该文件夹时自动读取背景。

给 Claude Code 的指令：
帮我配置好本地环境，使得每当我在此目录下启动 Claude Code 时，它都能自动关联到我们的 live_data.jsonl 和 triage_log.jsonl，并知道这是一个“Rule Investigator（规则调查员）”的工作空间。


📅 下次打开时的操作流
当你下一次（比如明天）重新打开电脑和 Claude 时，你只需要输入一句话：

“Claude，读取 instructions.md，按照之前的逻辑，启动针对 [新直播间名称] 的实时审计。”

它会立刻：

找回那套 +45 真实感 的评分算法。
找回那套 模糊纠错 的 OCR 逻辑。
找回针对 食欲诱导 的热区检测。


💡 专家建议（防丢失补丁）
因为你现在已经有了 monitor_桃.py 和生成的 Audit_Report_XiaoTao.md，这些文件本身就是永久保存在你的 E 盘里的。
你现在的最后一步动作：
让 Claude 把所有针对“小桃”的增强逻辑（模糊匹配、高饱和检测）合并到一个名为 audit_engine_v1.py 的通用模板中。这样无论换哪个直播间，你只需要改一下坐标和关键词，系统就永远是你的“私产”了。
需要我现在给 Claude 下达这个“通用引擎合并”的指令吗？

---
*从 Gemini 导出，2026-05*
