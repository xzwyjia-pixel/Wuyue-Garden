---
title: #F3F3F3
source: gemini
date: 2026-05-02
category: 系统运维
tags: [gemini, 系统运维]
---

## #F3F3F3

根据您目前的环境配置进度，这一步是实现 scholar-skill（学术研究深度解构系统）闭环的关键。由于您已经成功在 PowerShell 中完成了模型的拉取，接下来的重点在于将这个“大脑”与您在 VS Code 中使用的 Cline (或 Claude Dev) 插件进行物理连接。
以下是实现 image_054a58.png 中功能的最终配置指南：

第一步：启动本地 AI 核心
在您的 PowerShell 窗口中，执行以下命令以确保 AI 助手能够调用您刚刚拉取的模型：
ollama launch claude --model qwen2.5-coder


第二步：配置 Cline 以挂载 Scholar-Skill
您需要修改 Cline 的 MCP 配置文件。根据之前的检测，该文件通常位于您的用户数据目录下。

打开设置：在 VS Code 的 Cline 插件面板中，点击齿轮图标（Settings），然后选择 MCP Config。
添加 Skill 定义：在 cline_mcp_settings.json 的 mcpServers 部分添加以下代码块（注意： 请将路径替换为您存放 scholar-skill 源码的实际位置）：

{
  "mcpServers": {
    "scholar-skill": {
      "command": "python",
      "args": [
        "C:/Users/think/Documents/scholar-skill/main.py"
      ],
      "env": {
        "PYTHONPATH": "C:/Users/think/Documents/scholar-skill"
      }
    }
  }
}


第三步：安装 Skill 运行依赖
该系统包含 L1-L3 分级阅读策略和 2.5 小时长异步任务，这需要特定的 Python 库支持。

打开一个新的 PowerShell 窗口（确保不是在 AI 聊天模式下）。
进入技能文件夹并安装依赖：
cd C:\Users\think\Documents\scholar-skill
pip install -r requirements.txt




第四步：功能验证与使用
完成上述步骤并保存 JSON 文件后，Cline 会自动重新加载。您可以直接在聊天框中下达指令，触发 image_054a58.png 中提到的核心功能：

L1-L3 级阅读：“请使用 scholar-skill 对这篇关于‘低空经济’的论文进行 L3 级深度解构。”
生成反思报告：“分析完成后，请自动生成一份结构化笔记和反思报告。”
确认防呆机制：当执行长达 2.5 小时的异步任务时，请留意 VS Code 弹出的操作确认提示。


💡 针对“甄先生”的特别建议

模型选择：考虑到您正在为儿子规划 2028 年的高考及西北工业大学航天专业，建议您使用该 Skill 重点分析相关的航天前沿论文。
Token 监控：该 Skill 标记为“科研专用（高 Token 消耗）”。虽然您目前使用本地 Ollama 免费运行，但如果未来切换到联网的 Claude 3.5 模型，请务必关注您的 API 消耗情况。

---
*从 Gemini 导出，2026-05*
