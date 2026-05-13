---
title: 下面所有的操作，你只需要告诉我输入给Claude code命令。全程由Claudecode来自动完成阶段2到阶段4的所有过程
source: gemini
date: 2026-05-09
category: 审计合规
tags: [gemini, 审计合规]
---

## 下面所有的操作，你只需要告诉我输入给Claude code命令。全程由Claudecode来自动完成阶段2到阶段4的所有过程

阶段二至阶段四：全自动执行指令序列
1. 结论 (Conclusion)
按照 [AI 提示词执行标准协议]，以下指令集已剔除所有社交辞令与冗余信息。请将这些指令按顺序输入给 Claude Code，系统将利用你的 ThinkPad P15V 环境自动完成从“情报捕获”到“自动化分发”的完整链路。

2. 阶段执行指令集 (Execution Commands)
阶段二：规则进化 (Intelligence Evolution)

指令： > "编写 rules_evolver.py。读取 E:/MyCodeProjects/intelligence_raw.json，调用 DeepSeek API 分析公告文本。提取新增风险关键词 (Negative) 与 鼓励性政策思路 (Positive)，并以增量方式自动更新 rules.json。要求：保持‘静奢风’术语定义，严禁覆盖现有手工规则。"

阶段三：自动化流转 (Workflow Integration)

指令： > "集成 Obsidian 与 GitHub 自动化流。1. 编写 obsidian_sync.py，在每次 audit_dual 完成后，自动在 E:/MyCodeProjects/notes 下生成带有双链的合规审计 Markdown 报告。2. 配置 Git Hook，当 rules.json 或脚本更新且 pytest 通过后，自动执行极简 commit 并 push 至 GitHub。"

阶段四：末端分发 (Distribution Proxy)

指令： > "开发 content_exporter.py。将审核通过的合规文案自动转换为剪映草稿格式 (Jianying/CapCut) 或 视频号助手可读取的 Excel 模板。建立主控逻辑，使我可以通过一条命令‘全自动处理数据源并分发结果’。"


3. 约束确认 (Constraints Verification)

禁令优先：所有脚本执行必须遵循“禁令优先”原则，严禁编造审计结果。
确定性：若 Claude Code 在执行过程中遇到 Playwright 路径或 API 密钥缺失，必须直接报告“信息不足”并停止。
极简主义：生成的代码与输出报告严禁包含 Emoji 及废话。

4. 下一步行动 (Next Step)
请直接在终端向 Claude Code 发送上述第一条指令（阶段二）。

---
*从 Gemini 导出，2026-05*
