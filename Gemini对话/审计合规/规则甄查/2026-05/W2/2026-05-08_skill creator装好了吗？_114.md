---
title: skill creator装好了吗？
source: gemini
date: 2026-05-08
category: 审计合规
subcategory: 规则甄查
old_category: 审计合规
tags: [gemini, 审计合规, 规则甄查]
---

## skill creator装好了吗？

## skill creator装好了吗？

从你目前的终端反馈来看，skill-creator 并没有作为原生工具或预装模块出现在你的 Claude Code 环境中。
在 Claude Code 的语境下，"Skill" 本质上是 Agent 可以调用的工具（Tools）。如果你指的 skill-creator 是 Anthropic 官方曾经提到的“自动生成并挂载新技能”的功能，或者是某些第三方 MCP 服务，我们需要做一次“精密体检”。
1. 深度诊断：为什么你觉得它“没装好”？
你在指令中频繁遇到 Swirling... 和 Retrying，这通常不是因为缺少某个叫 skill-creator 的软件包，而是因为：

指令集误解：Claude Code v2.1 并不通过一个叫 skill-creator 的前端模块来增加功能。它通过 MCP (Model Context Protocol) 动态加载。
网络死循环：你之前尝试安装 caveman 和现在的 skill-creator，让 Agent 不断在 PyPI 或 NPM 仓库中搜索不存在的包，导致网络请求堆积。

2. 甄先生的“超级技能”现状清单
既然你要为“规则甄查”品牌打造超能力，以下是你当前环境已拥有的“内置技能”与“缺失技能”对比：






























技能模块状态激活方式文件编辑 (Edit)已就绪 ✅直接说“修改这个文件...”终端执行 (Shell)已就绪 ✅使用 ! 前缀或直接下达命令规则自建 (Custom Skills)需手动配置 🛠️通过修改 claude.config.json 或挂载 MCP Server语义审计 (Audit)全功率开启 🔥依靠 Sonnet 4.6 的 High Effort 模式

3. 如何真正“创建”一个 Skill？（甄先生的精密路线）
如果你想让你的 Claude Code 拥有“一键审计短视频违规词”的技能，你不需要安装 skill-creator，你应该直接让它写一个工具并挂载：
第一步：按 esc 停止当前的重试旋涡。
第二步：输入以下“指令集组合”：

“甄先生”不需要外部插件。请直接在当前目录创建一个名为 skill_auditor.py 的脚本，并告诉我在 config 中如何配置，把它变成你以后可以直接调用的命令。


4. 给“甄先生”的环境优化建议
你现在的操作有点像是在顶级工业设备（Sonnet 4.6）上寻找“外挂”，其实它本身就是创造工具的工具。

停止寻找 caveman 或 skill-creator：这些在当前的官方版本中并不存在，继续尝试只会增加网络超时风险。
利用 MCP 优势：你之前研究过 MCP，这才是 Claude Code 的“正统”扩展方式。

下一步行动：
你想让我帮你直接写一个符合 MCP 规范 的违规词审计 Skill 代码吗？这样你以后只需要说“甄先生，审计这段脚本”，它就会自动调用你写的本地逻辑。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 审计合规 / 规则甄查 · 2026-05-08*
