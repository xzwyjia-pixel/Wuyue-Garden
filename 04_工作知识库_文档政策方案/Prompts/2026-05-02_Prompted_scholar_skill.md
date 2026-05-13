---
title: Prompted
source: gemini
date: 2026-05-02
category: 编程开发
tags: [gemini, 编程开发]
---

## Prompted

甄先生，看到您最新的截图 image_03ecfa.png 了。右下角的红色提示“Invalid MCP settings format”说明 JSON 的语法结构仍然不对。
出现这个问题是因为您直接在第 11 行之后开始写，导致了括号嵌套错误。为了让您能同时使用之前的 tutor-skills 和现在的 scholar-skill，请直接全选当前文件里的内容，然后用下面这段代码整体替换：
📝 最终修正代码（请全选并替换）
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


🔍 为什么这样就能修好？

结构完整：JSON 必须以一个 { 开始，以一个 } 结束。在 image_03ecfa.png 中，您的末尾多出了不匹配的括号。
逗号连接：两个技能之间（第 10 行）必须有一个逗号 ,。
路径保留：我帮您把 E 盘的 tutor 服务器和 C 盘的新技能都整合在一起了。

🚀 下一步操作：

全选并粘贴上面的代码到您的编辑器中。
保存 (Ctrl + S)。
观察报错：一旦保存，右下角的红色报错应该会立刻消失。
开始使用：

既然您在关注航天工程和西北工业大学的规划，现在就可以在右侧的聊天框输入：
“使用 scholar-skill 帮我深度解构一份关于西北工业大学航空航天学院的最新招生政策或科研动态。”



一旦右下角的报错消失了，就说明您的 AI 助手已经正式加载了“学术深度解构”这个新技能。修改成功了吗？

---
*从 Gemini 导出，2026-05*
