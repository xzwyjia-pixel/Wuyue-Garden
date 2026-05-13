---
title: 对市面上所有的agent和skill做一下详细梳理和对比
source: gemini
date: 2026-05-01
category: 编程开发
tags: [gemini, 编程开发]
---

## 对市面上所有的agent和skill做一下详细梳理和对比

在 2026 年的 AI 生态中，**Agent（智能体）**与 **Skill（技能）**的关系已经从早期的“模糊替代”演变为类似“员工”与“职业证书/SOP”的清晰协作关系。
以下是对市面上主流 Agent 平台与 Skill 标准的详细梳理与对比。

一、 核心概念：Agent vs. Skill






























维度Agent (智能体)Skill (技能)本质定义具有规划、记忆和工具使用能力的执行主体。封装好的能力包（包含指令、工具调用逻辑、领域知识）。类比职场中的“数字员工”。员工脑中的“技能插件”或手里的“SOP 手册”。标准协议厂商私有协议为主（如 OpenAI, Microsoft）。行业开放标准（如 Anthropic 引领的 SKILL.md）。复用性跨平台迁移难度大，通常绑定特定大模型。高复用性，可跨 Agent 挂载（如 MCP 协议支持）。

二、 2026 主流 Agent 平台梳理
目前市面上的 Agent 主要分为通用入口型、企业工作流型和自主行动型三大阵营。
1. 通用入口型 (B2C)

OpenAI GPTs / Operators:

特点： 依托 ChatGPT 的巨大流量，生态最丰富。2026 年的“Operator”已经具备浏览器自动化控制能力。
优势： 使用门槛极低，多模态能力最强。


Claude Computer Use (Anthropic):

特点： 强调“像素级”屏幕操控，能像人一样操作复杂的桌面软件。
优势： 逻辑严密，安全性（Constitutional AI）高。



2. 企业工作流型 (B2B)

Microsoft Copilot Studio:

特点： 深度集成 Office 365 和 Azure 数据。
优势： 权限管理极其严格，适合处理企业内部报表、审批流等敏感任务。


Coze (字节跳动) / Dify:

特点： 典型的 Low-code/No-code 平台，将 Agent 的创建流程拆解为节点（Nodes）。
优势： 国内生态适配极好（微信、飞书），灵活度极高。



3. 自主行动型 (Autonomous Agents)

AutoGPT / BabyAGI (进阶版):

特点： 能够自我反思、拆解长期目标，无需人工干预即可完成长链条任务。
劣势： 容易陷入“逻辑循环”，目前多用于研究和复杂的代码开发场景。




三、 Agent Skill 的行业标准与分类
2026 年，Skill 已经不再是简单的 Prompt，而是标准化的能力单元。
1. 核心标准：SKILL.md & MCP

MCP (Model Context Protocol): 由 Anthropic 推动，解决了 Agent 如何统一调用外部工具（如 Google Drive, GitHub, SQL）的协议问题。
SKILL.md: 技能的“说明书”，包含：

Metadata: 技能名称、版本、适用场景。
Execution Logic: 具体的脚本、模板或 API 调用逻辑。
Knowledge Base: 技能所需的特定领域静态资料。



2. 常见 Skill 类型对比






























Skill 类型典型代表核心价值连接类 (Connectors)SQL 查询、Gmail 发送、Jira 联动打通 Agent 与现有软件系统的“手脚”。流程类 (Workflows)合同审核流程、PPT 自动生成将复杂的业务 SOP 脚本化，确保执行不走样。专业知识类 (Domain)某行业合规准则、特定公司品牌手册为 Agent 提供“专家大脑”，减少幻觉。自动化类 (Browser)网页抢票、跨网站信息抓取在没有 API 的环境下，通过模拟点击完成任务。

四、 总结：如何选择？

如果您是开发者： 建议优先拥抱 MCP 协议 和 Dify。通过封装标准化的 Skill，可以让您的代码逻辑在多个 Agent 平台上运行，避免被单一厂商锁死。
如果您是企业管理/业务： 关注 Microsoft Copilot 或 Coze。重点不在于 Agent 强不强，而在于它能否合规地调用你现有的业务数据。
未来的趋势： “Agent 平台化，Skill 中立化”。未来你可能拥有一个固定的 Agent 助手，但你会通过订阅不同的“专业 Skill”来让它不断进化，就像在手机上下载 App 一样。


洞察： 2026 年的竞争核心已从“谁的模型更聪明”转向“谁的 Skill 库更精准”。对于您正在做的“规则情报局”项目，将复杂的算法规则封装成合规类 Skill，或许是极具商业价值的路径。

---
*从 Gemini 导出，2026-05*
