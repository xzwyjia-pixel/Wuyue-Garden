---
title: Prompted
source: gemini
date: 2026-05-02
category: Claude/MCP
tags: [gemini, Claude/MCP]
---

## Prompted

甄先生，既然 /config 界面里没有直接显示路径，没关系，我们用最直接的方式让它自己去“装修”这个配置文件。
请在您现在的这个界面（如上图所示）按下 Esc 键退出配置菜单，回到可以输入指令的状态。
然后，请直接复制并输入下面这段话给它：

Please add the following MCP servers to my configuration. Create the configuration file if it doesn't exist:
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


为什么要这么做？
您正在使用的这个工具（Claude Code）拥有“自我修改”的能力。与其我们辛苦地在文件夹里找文件，不如直接告诉它“请帮我添加这些技能”。它会自动找到正确的路径，并为您写好配置文件。
输入后，它应该会提示它正在修改文件。等它修改完成后，您再次输入 /mcp 看看，技能是不是已经出现了？

---
*从 Gemini 导出，2026-05*
