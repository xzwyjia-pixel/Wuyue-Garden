---
title: 使用本地模型 (Local LLM)：
source: gemini
date: 2026-04-30
category: 技术开发
subcategory: Python
old_category: 系统运维
tags: [gemini, 技术开发, Python]
---

## 使用本地模型 (Local LLM)：

## 使用本地模型 (Local LLM)：

安装 Ollama。
在 VS Code 中使用支持本地模型的开源插件（如 Cline 或 Continue）。
这些插件同样支持 MCP 协议。这样你编写的“违规词检测 Skill”可以对接本地运行的免费模型（如 Llama 3 或 DeepSeek），实现真正的 100% 免费。

告诉我上述操作的详细步骤

通过使用 Ollama 结合 VS Code 插件（如 Cline 或 Continue），你可以完全脱离云端 API 费用，在本地构建并运行你的 “规则甄查” Agent。
以下是实现 100% 免费本地 AI 编码与技能 (Skill) 调用环境的详细步骤：
1. 安装与配置 Ollama (本地 LLM 引擎)
Ollama 是在本地运行 Llama 3 或 DeepSeek 等开源模型的后端服务。

安装：前往 Ollama 官网 下载并安装 Windows 版。
下载模型：在终端 (PowerShell) 中运行以下命令下载支持“工具调用”(Tool Use) 的模型（这是 Agent 使用 Skill 的前提）：
# 推荐用于逻辑推理和工具调用 (需要约 8GB 显存/内存)
ollama pull llama3.1:8b 
# 推荐用于代码辅助 (轻量且快)
ollama pull qwen2.5-coder:7b


验证运行：运行 ollama list 确认模型已在本地。


2. 在 VS Code 中配置插件
你可以从以下两个主流插件中择一使用：
方案 A：使用 Cline (原 Claude Dev)
Cline 对 MCP (Skill) 的支持非常直观，且能够自动执行终端命令。

安装：在 VS Code 扩展市场搜索并安装 Cline。
配置 API：

点击侧边栏 Cline 图标，进入 Settings。
将 API Provider 设置为 Ollama。
在 Model 下拉框选择刚才下载的模型（如 llama3.1:8b）。
确保 Ollama Base URL 填入 http://localhost:11434。



方案 B：使用 Continue
Continue 更加侧重于代码补全和深度自定义配置。

安装：在 VS Code 扩展市场安装 Continue。
配置模型：点击侧边栏 Continue 图标，点击底部的齿轮图标进入 config.json，添加 Ollama 配置：
{
  "models": [{
    "title": "Ollama Llama3.1",
    "provider": "ollama",
    "model": "llama3.1:8b"
  }]
}





---

### 3. 对接你的“违规词检测 Skill” (MCP Server)
无论你选择哪个插件，它们都支持 **MCP (Model Context Protocol)** 协议来调用你编写的 Python 脚本。

*   **Cline 配置方法**：
    *   在 Cline 的设置页面找到 **MCP Servers** 部分。
    *   点击添加新服务器，填入你的 Python 脚本运行信息：
        *   **Command**: `python`
        *   **Args**: `["C:/路径/到/你的/violation_check.py"]`
*   **Continue 配置方法**：
    *   在 `config.json` 中添加 `mcpServers` 字段：
    ```json
    "mcpServers": [
      {
        "name": "violation-checker",
        "command": "python",
        "args": ["C:/路径/到/你的/violation_check.py"]
      }
    ]
    ```

---

### 4. 验证与使用
1.  **启动 Agent**：在 Cline 或 Continue 的对话框中。
2.  **下达指令**：你可以直接对它说：“请检查我这段关于‘规则情报局’的文案是否有敏感词。”
3.  **免费执行**：
    *   插件会将指令发送给本地的 **Ollama**。
    *   模型判断需要调用“违规词检测”工具。
    *   插件自动运行你的 **Python 脚本** 并返回结果。
    *   **全程不联网、不扣费、隐私安全**。

**关键提醒**：Agent 模式（即调用工具）对模型的推理能力要求较高，建议电脑至少有 **16GB 内存**，并优先使用 **8B** 及以上参数规模的模型（如 `llama3.1:8b` 或 `deepseek-v3` 的本地版本）以获得稳定的工具调用效果。

---
*从 Gemini 导出，2026-04*

---
*Gemini · 技术开发 / Python · 2026-04-30*
