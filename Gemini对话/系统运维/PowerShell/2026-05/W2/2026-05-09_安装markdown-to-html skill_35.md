---
title: 安装markdown-to-html skill
source: gemini
date: 2026-05-09
category: 系统运维
subcategory: PowerShell
old_category: 编程开发
tags: [gemini, 系统运维, PowerShell]
---

## 安装markdown-to-html skill

## 安装markdown-to-html skill

在你的环境中安装 markdown-to-html 技能，同样属于 MCP (Model Context Protocol) 技能扩展的范畴。
由于你之前的 npm install 报错 404，这再次确认了这些技能（包括 baoyu-skills 和 frontend-master）通常不是通过 npm 公共库发布的，而是通过本地源码路径或 GitHub 仓库地址直接挂载到你的 AI 配置文件中的。

1. 安装 markdown-to-html 技能
请根据你目前使用的工具环境选择对应的操作：
方案 A：通过 cc-switch (如果你已成功安装该切换器)
cc-switch 应该是一个专门管理 MCP 技能的工具，你可以尝试执行：
cc-switch add markdown-to-html

方案 B：手动配置 claude_desktop_config.json
这是最稳妥的办法。你需要将该技能手动加入到 Claude 的配置文件中：

打开配置文件（路径一般为：%APPDATA%\Claude\claude_desktop_config.json）。
在 "mcpServers" 下添加以下内容：

"markdown-to-html": {
  "command": "node",
  "args": [
    "E:/ClaudeEnvironment/markdown-to-html/dist/index.js" 
  ]
}

(注：请务必将路径替换为你本地 markdown-to-html 源码的实际存放路径。)

2. 补全技能：为什么 frontend-master 只显示 1 个功能？
针对你之前提到的“4 个功能只安装了 1 个”的问题，这通常是因为 TypeScript 没有编译 或 环境变量未生效。
彻底修复步骤：


进入目录并强制编译：
cd E:\ClaudeEnvironment\frontend-master
npm install
npm run build  # 这一步至关重要，它会将 TS 源码转化为包含所有 4 个功能的 JS 文件



清理进程：
在 PowerShell 中执行以下命令（由于你之前遇到权限问题，请以管理员身份运行）：


    # 强制结束可能占用技能文件的 node 进程
    taskkill /F /IM node.exe
    ```

3.  **验证配置文件：**
    确保 `claude_desktop_config.json` 中指向的是编译后的 `dist/index.js`（或 `build/index.js`），而不是 `src` 目录下的文件。

---

## 3. 常见故障排查清单

*   **路径问题：** 在 Windows 的 JSON 配置文件中，路径建议使用正斜杠 `/` (例如 `E:/Tools/...`) 或双反斜杠 `\\`，否则容易导致读取失败。
*   **依赖缺失：** 如果 `npm install` 报错，请检查你是否开启了代理。鉴于你之前有 `NODE_TLS_REJECT_UNAUTHORIZED='0'` 的警告，建议先配置好 npm 的镜像源：
    ```powershell
    npm config set registry https://registry.npmmirror.com
    ```
*   **验证安装：** 重启 Claude 后，在对话框输入 `What tools do you have?`。如果配置正确，它会列出 `frontend-master` 的全部 4 个 Tool 和新装的 `markdown-to-html`。

如果你在 `E:\ClaudeEnvironment` 目录下没找到对应的源码文件夹，说明你需要先从代码仓库 `git clone` 它们。需要我提供对应的 GitHub 仓库地址吗？

---
*从 Gemini 导出，2026-05*

---
*Gemini · 系统运维 / PowerShell · 2026-05-09*
