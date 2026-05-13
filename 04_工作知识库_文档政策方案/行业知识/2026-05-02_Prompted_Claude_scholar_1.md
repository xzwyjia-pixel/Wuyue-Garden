---
title: Prompted
source: gemini
date: 2026-05-02
category: 文案创意
old_category: 系统运维
tags: [gemini, 文案创意]
---

## Prompted

## Prompted

甄先生，看来这款 Claude Code 终端在处理 %APPDATA% 这种系统环境变量时存在理解偏差，它刚才写入的内容变成了 "new_server_url"，这显然不对。
既然“软”的不行，我们来“硬”的。请您按照以下步骤手动创建配置文件，这是最稳妥的办法：
第一步：手动打开目标文件夹

按下键盘上的 Win + R 键。
在弹出的运行框里直接粘贴下面这段路径：
C:\Users\think\AppData\Roaming
点击确定。
在打开的窗口里，看看有没有一个叫 Claude 的文件夹？

如果没有：请右键 -> 新建 -> 文件夹，命名为 Claude。
如果有：直接双击进去。




第二步：创建配置文件

在 Claude 文件夹内，右键 -> 新建 -> 文本文档。
将文件名完整修改为：config.json（注意要删掉最后的 .txt 后缀）。
如果系统提示“改变文件扩展名可能导致文件不可用”，点击 “是”。


第三步：写入正确代码

双击打开这个 config.json（用记事本打开即可）。
把下面这段精准的代码粘贴进去并保存：

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


第四步：最后一次“点火”测试

回到那个黑色终端窗口，输入 /exit 退出。
重新启动：ollama launch claude --model qwen2.5-coder。
输入：/mcp。

只要文件夹和文件在正确的位置，它这次绝对无法“拒绝”加载。
一旦成功，咱们就立刻开始分析您儿子 2028 年的高考目标——西工大航天学院。如果您在新建文件夹或修改后缀名时卡住了，随时拍个照给我看。

---
*从 Gemini 导出，2026-05*

---
*从 Gemini 导出 · 分类: 文案创意 · 2026-05*
