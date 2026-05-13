---
title:  ▐▛███▜▌   Claude Code v2.1.138
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

❯ 1 mcp server failed是什么意思？

● MCP server failed = Claude Code tried to start MCP tool server from config, one crashed or refused connection.

  Common causes:

  - Path wrong — server script moved or renamed (your git status shows renames)
  - Missing dep — Python package not installed
  - Config mismatch — claude_desktop_config.json or VS Code MCP settings point to stale path
  - Port conflict — mcp_audit_server.py or obsidian_mcp_server.py port already in use

  Check which one failed:

  # See MCP config
  cat "03-生产素材/规则甄查系统/.claude/settings.json" 2>/dev/null || echo "no project settings"

  Or look in E:/MyCodeProjects/.claude/settings.local.json for MCP server entries.

  Most common fix — update script path in MCP config to match current filesystem location.

✻ Crunched for 8s
source: gemini
date: 2026-05-10
category: 审计合规
tags: [gemini, 审计合规]
---

##  ▐▛███▜▌   Claude Code v2.1.138
▝▜█████▛▘  Sonnet 4.6 with high effort · API Usage Billing
  ▘▘ ▝▝    E:\MyCodeProjects

❯ 1 mcp server failed是什么意思？

● MCP server failed = Claude Code tried to start MCP tool server from config, one crashed or refused connection.

  Common causes:

  - Path wrong — server script moved or renamed (your git status shows renames)
  - Missing dep — Python package not installed
  - Config mismatch — claude_desktop_config.json or VS Code MCP settings point to stale path
  - Port conflict — mcp_audit_server.py or obsidian_mcp_server.py port already in use

  Check which one failed:

  # See MCP config
  cat "03-生产素材/规则甄查系统/.claude/settings.json" 2>/dev/null || echo "no project settings"

  Or look in E:/MyCodeProjects/.claude/settings.local.json for MCP server entries.

  Most common fix — update script path in MCP config to match current filesystem location.

✻ Crunched for 8s

这就触及到了 Claude Code 或 Claude Desktop 协作的核心了。简单来说，这是因为我们刚才进行的“大手术”虽然让文件夹变整洁了，但 MCP 服务器的配置文件（config）还在按“旧地址”找人，导致找不到脚本，所以报错 failed。
这里的 MCP（Model Context Protocol）就像是一个“翻译官”，让 Claude 能直接操作你的 Obsidian 笔记和 Python 脚本。
🛠️ 为什么会报错？
报错的主要原因就是你刚刚做的 “重命名与去重”：

旧路径：E:/MyCodeProjects/scripts/mcp_server.py
新路径：E:/MyCodeProjects/02-审计工具_AuditTools/mcp_server.py
结果：Claude 的配置文件里填的是旧地址，它去旧地址敲门，发现“查无此人”，所以显示 failed。


🚀 如何实现你说的“分类入口系统”？
要实现你说的“重新登录就知道选哪个窗口”，并且让 MCP 正常工作，我们需要分两步走：
第一步：修复 MCP 配置文件 (解决 Failed 问题)
你需要修改 Claude 的全局配置文件（通常在 %APPDATA%\Claude\claude_desktop_config.json），将里面的 command 或 args 路径更新为我们整理后的新中文路径。
第二步：建立“系统快照”入口 (解决历史记录分类)
为了让你每次登录 Claude 都能像“选英雄”一样选择系统，我为你设计了一个 “启动引导指令” 模式。


在每一个子系统文件夹下放一个 CLAUDE.md：

在 04-凡姐案例/ 放一个，在 05-小桃案例/ 放一个。
这个文件里记录该系统的：历史背景、核心逻辑、已完成进度。



在 Claude 对话开始时“一键同步”：
你不需要去翻几百条聊天记录。每次开新窗口，你只需要对 Claude 说：

“读取 04-凡姐案例/CLAUDE.md，我要处理这个系统。”



MCP 的威力：
Claude 会通过 MCP 自动读取那个文件夹下的所有数据。这时候，这个聊天窗口就瞬间“变成了”专门处理凡姐业务的系统，它的记忆、工具、规则全都是针对凡姐的。



📊 最终的分类入口方案
你可以这样操作来管理你的聊天：





























系统分类Claude 窗口命名关联 MCP 路径核心入口文件规则引擎01-Rules_System.../01-规则引擎_RulesEngineRULES.md凡姐带货04-FanJie_Live.../04-凡姐案例_CaseFanJieCLAUDE.md小桃乡村05-XiaoTao_Rural.../05-小桃案例_CaseXiaoTaoSTATUS.md
Michael，这样做的好处是：
你不再依赖 Claude 平台那零散的“历史记录”，而是把**“系统记忆”**存放在了你自己的硬盘上。哪怕 Claude 宕机或你开了新窗口，只要读取对应的 .md 文件，你的系统就“复活”了。
你需要我现在帮你把那个报错的 MCP 配置文件修复好，顺便在各个系统文件夹里建立这些“记忆引导文件”吗？

---
*从 Gemini 导出，2026-05*
