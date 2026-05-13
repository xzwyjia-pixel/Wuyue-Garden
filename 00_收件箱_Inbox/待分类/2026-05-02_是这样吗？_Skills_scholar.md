---
title: 是这样吗？
source: gemini
date: 2026-05-02
category: 系统运维
tags: [gemini, 系统运维]
---

## 是这样吗？

非常接近了，甄先生！从截图 image_0442b5.png 来看，报错是因为 JSON 格式多了一个结尾括号。
由于您在第 11 行 }, 之后添加了新的技能，原本文件的结构被打乱了。请参照以下代码，把文件里的全部内容替换掉，这样最稳妥：
📝 修正后的完整代码（直接全选替换）
{
  "mcpServers": {
    "tutor-skills": {
      "command": "python",
      "args": [
        "E:\\MCP-Skills\\tutor_server.py"
      ],
      "env": {},
      "disabled": false
    },
    "scholar-skill": {
      "command": "python",
      "args": [
        "C:/AI_Skills/scholar-skill/main.py"
      ],
      "env": {
        "PYTHONPATH": "C:/AI_Skills/scholar-skill"
      },
      "disabled": false
    }
  }
}


🔍 为什么刚才报错？
在 image_0442b5.png 中，错误主要在最后几行：

第 22 行多了一个 }，这导致 JSON 提前结束了。
第 23 行和第 24 行的括号就变成了多余的“孤儿”，导致了右下角显示的 Invalid MCP settings format 错误。

🚀 修改建议：

全选 (Ctrl + A) 您当前编辑器里的所有文字。
删除 (Backspace)。
粘贴 我上面提供的那段完整代码。
保存 (Ctrl + S)。

保存后，右下角的红色报错应该会消失。之后您可以回到 Claude Code 终端输入 /mcp，就能看到这个具备 L1-L3 分级阅读策略 的学术神技已经上线了。既然您之前在配置 VS Code 和 Ollama 环境时非常顺利，这次微调格式对您来说肯定没问题。

---
*从 Gemini 导出，2026-05*
