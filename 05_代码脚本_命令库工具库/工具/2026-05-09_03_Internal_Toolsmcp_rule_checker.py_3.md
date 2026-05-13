---
title: 在 Obsidian 里安装 Digital Garden 或 Quartz 插件。如何操作？可以用Claude自动执行吗？
执行：强化工具层：把 03_Internal_Tools 里的“规则甄查引擎”封装成一个 MCP Server，让你在任何 Claude 窗口都能随时调用这个审计能力。
source: gemini
date: 2026-05-09
category: 审计合规
tags: [gemini, 审计合规]
---

## 在 Obsidian 里安装 Digital Garden 或 Quartz 插件。如何操作？可以用Claude自动执行吗？
执行：强化工具层：把 03_Internal_Tools 里的“规则甄查引擎”封装成一个 MCP Server，让你在任何 Claude 窗口都能随时调用这个审计能力。

针对你的需求，我分两步执行：第一步是关于 Obsidian 发布的决策判断，第二步是直接交付 MCP Server 的封装脚本。

1. Obsidian 自动化发布：现状与操作
结论： Claude Code 不能直接在你电脑的 Obsidian UI 里点击“安装按钮”，但它可以直接把插件代码和配置文件写入你的文件夹，实现“静默安装”。

Digital Garden: 适合“一键发布”到 Vercel/GitHub，操作最轻。
Quartz: 适合做极度美化的“数字花园”，但它是基于 Node.js 的，配置略重。

我的建议： 先用 Digital Garden。
自动化命令（直接在终端运行）：

"在我的 Obsidian Vault 插件目录 path/to/vault/.obsidian/plugins/ 下创建一个 obsidian-digital-garden 文件夹。下载其最新的 main.js, manifest.json, styles.css 文件。如果无法下载，请直接写一个 Python 脚本帮我从 GitHub Release 抓取并放置到该目录。"


2. 强化工具层：封装“规则甄查”为 MCP Server
你现在的“规则甄查”是一个脚本，通过封装成 MCP (Model Context Protocol)，你可以让 Claude 在任何对话中（不仅仅是在这个项目下）直接调用它。
步骤 A：创建 MCP Server 逻辑文件
在 03_Internal_Tools/ 下新建一个 mcp_rule_checker.py。我为你写好了基于标准 mcp 库的框架：
# 03_Internal_Tools/mcp_rule_checker.py
import sys
from mcp.server.fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("RuleInvestigator")

@mcp.tool()
def audit_content(content: str, platform: str = "douyin"):
    """
    审计短视频内容是否违反平台规则。
    platform: douyin, xiaohongshu, wechat_video
    """
    # 这里直接导入你原有的规则甄查引擎逻辑
    # from engine import check_rules 
    
    # 模拟审计逻辑（请根据你原有的 scripts/ 逻辑替换）
    results = f"正在针对 {platform} 审计内容: {content[:20]}..."
    # 假设你原有的逻辑返回了红绿灯状态
    return {
        "status": "warning",
        "risk_points": ["医疗违禁词", "引流违规"],
        "suggestion": "建议将'最专业'改为'资深'"
    }

if __name__ == "__main__":
    mcp.run()

步骤 B：配置 Claude 客户端
你需要让你的 Claude 客户端（Desktop 或 CLI）认识这个 Server。
操作命令（交给 Claude Code 执行）：

"读取我的 Claude 配置文件（Windows 通常在 %APPDATA%\Claude\claude_desktop_config.json），在 mcpServers 字段下添加一个名为 rule-investigator 的服务。
command: 'python',
args: ['E:/MyCodeProjects/01-Production/规则甄查系统/03_Internal_Tools/mcp_rule_checker.py']"


瑶瑶决策点（为什么这么做）：

产品化第一步：封装成 MCP 后，这不再是一个“文件夹里的脚本”，而是一个**“随身携带的 AI 审计插件”。你在给客户演示时，随手贴一段文案，Claude 就能直接调用这个 Tool 给出审计报告，这种交付感**比跑脚本强 10 倍。
低熵集成：不要去搞复杂的 SaaS 后端，MCP 就是 2026 年最轻量级的“AI 插件”方案。
内容素材：你又多了一个爆款素材——“我如何把我的行业经验（规则甄查）封装成 Claude 都能听懂的 MCP 工具”。

如果你已经安装了 mcp 库，直接运行上述 Python 脚本即可。如果没有，告诉我，我让 Claude Code 帮你配置环境。

---
*从 Gemini 导出，2026-05*
