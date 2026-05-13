---
title: Prompted
source: gemini
date: 2026-05-02
category: 文案创作
tags: [gemini, 文案创作]
---

## Prompted

看到您的截图 image_044e57.png 了，您已经成功打开了 Claude Code 的内部配置菜单。
目前显示的是基础 UI/交互设置。要让 scholar-skill 生效，我们需要跳出这个图形化菜单，直接去修改 MCP 配置文件。因为 scholar-skill 具备 L1-L3 分级阅读策略、2.5 小时长异步任务以及自动生成结构化笔记等核心科研功能，必须通过 MCP 协议挂载。

🛠️ 关键步骤：修改 MCP 配置文件
在 Windows 环境下，Claude Code 默认读取的 MCP 配置文件路径通常与 Cline 不同。
第一步：定位文件
请在您的文件夹浏览器地址栏直接输入并跳转：
%APPDATA%\Claude
在该目录下，您会看到一个 config.json 或 mcp_settings.json 文件。
第二步：添加 Scholar-Skill 配置
用记事本或 VS Code 打开该文件，在 mcpServers 部分加入以下内容：
{
  "mcpServers": {
    "scholar-skill": {
      "command": "python",
      "args": [
        "C:/AI_Skills/scholar-skill/main.py" 
      ],
      "env": {
        "PYTHONPATH": "C:/AI_Skills/scholar-skill"
      }
    }
  }
}

注：请确保 args 和 PYTHONPATH 的路径指向您电脑上 scholar-skill 文件夹的实际位置。
第三步：重启 Claude Code

在 image_044e57.png 显示的窗口中按 Esc 退出菜单。
输入 /exit 退出程序。
重新运行：ollama launch claude --model qwen2.5-coder。
再次输入 /mcp，此时您应该能看到 scholar-skill 出现在已加载的工具列表中。


🚀 开启学术研究解构
一旦安装成功，您可以直接发挥其科研专长。考虑到您对 航天工程 的关注（为您儿子规划高考目标），您可以尝试以下指令：

“使用 scholar-skill 的 L3 级深度解构策略，分析本地（或指定 URL）的航天动力学论文，并为我生成一份包含反思报告的结构化笔记。”

⚠️ 注意事项

Token 消耗：该 Skill 标注为“高 Token 消耗”，在执行 L3 级长任务时请保持网络稳定。
异步机制：它支持长达 2.5 小时 的异步任务，如果您分析的是极长篇幅的文献，只需下达指令后等待即可。

如果您在修改 JSON 文件时遇到格式错误，可以把文件内容贴出来，我帮您检查。

---
*从 Gemini 导出，2026-05*
