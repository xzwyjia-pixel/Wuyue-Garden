---
title: Prompted
source: gemini
date: 2026-05-02
category: 系统运维
tags: [gemini, 系统运维]
---

## Prompted

这一步走得非常漂亮！从 image_045cfb.png 可以看到，你已经成功退出了 AI 对话模式，并在系统环境下完成了 qwen2.5-coder 模型的下载。
现在“大脑”已经就绪，我们可以进行最后的连接与测试了。

第一步：正式启动 AI 助手
既然模型已经 success 下载完成，请在当前的 PowerShell 窗口输入以下命令来启动它：
ollama launch claude --model qwen2.5-coder

这次应该能直接进入 Claude 的交互界面，而不再提示 no matches。

第二步：手把手安装 Scholar-Skill
为了让你在 VS Code 里能用上 scholar-skill（即 image_054a58.png 中提到的学术解构系统），我们需要完成最后的“管道连接”：


确定路径：假设你的技能文件夹在 C:\AI_Skills\scholar-skill。


配置 Cline：

打开 VS Code，找到 Cline 插件的 Settings。
点击 MCP Config，在打开的 JSON 文件中加入以下配置：

{
  "mcpServers": {
    "scholar-skill": {
      "command": "python",
      "args": ["C:/AI_Skills/scholar-skill/main.py"],
      "env": {
        "PYTHONPATH": "C:/AI_Skills/scholar-skill"
      }
    }
  }
}

(注意：JSON 中的路径请统一使用正斜杠 /)


安装运行环境：
在 PowerShell 中切换到该目录并安装依赖：


    cd C:\AI_Skills\scholar-skill
    pip install -r requirements.txt
    ```

---

### 第三步：开始你的第一次“学术解构”

一切就绪后，回到 VS Code 的 Cline 对话框。你可以像“甄先生”一样开始工作了。

**试试输入：**
> “请启动 scholar-skill，针对‘仿生机器人关节控制算法’进行 L1-L3 级深度阅读，并生成一份结构化反思报告。”

### 🛠️ 故障排查建议
*   **IndentationError**：如果你之后在修改 Python 代码时遇到缩进错误（如你在尝试运行检测程序时遇到的情况），请确保使用 VS Code 的“自动格式化”功能。
*   **Ollama 连接**：如果运行过程中提示无法连接，请确认你的系统托盘里 Ollama 的图标是亮着的。

**恭喜你！到这一步，你已经亲手搭建起了一套完整的本地 AI 科研辅助环境。**

---
*从 Gemini 导出，2026-05*
