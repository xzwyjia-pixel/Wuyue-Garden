---
title: playwright-cli skill,安装一下这个
source: gemini
date: 2026-05-04
category: 编程开发
tags: [gemini, 编程开发]
---

## playwright-cli skill,安装一下这个

在 Python 或 Node.js 环境中安装 Playwright 的命令行工具，主要分为核心包安装与浏览器二进制文件下载两个步骤。
1. Node.js 环境（推荐）
如果你在 VS Code 或终端中使用，这是最常用的方式：

安装核心工具：
npm install -g playwright


安装浏览器内核（Chromium, Firefox, WebKit）：
npx playwright install



2. Python 环境
如果你是在配置 MCP 脚本或自动化审计工具：

安装 Python 库：

    pip install playwright
    ```
*   **初始化浏览器：**
    ```bash
    playwright install
    ```

---

### 3. 常用命令行（CLI）功能
安装完成后，你可以直接使用以下命令进行快速操作：

*   **录制脚本（自动生成代码）：**
    ```bash
    npx playwright codegen https://example.com
    ```
    *这会打开一个浏览器窗口，你在页面上的点击会自动转化为 Python 或 JS 代码。*

*   **打开交互式解释器（REPL）：**
    ```bash
    npx playwright cr  # 打开 Chromium 交互模式
    ```

*   **截图保存：**
    ```bash
    npx playwright screenshot --device="iPhone 13" https://baidu.com baidu.png
    

常见问题排查

权限问题：如果 Linux 环境下提示缺少系统依赖，请执行 npx playwright install-deps。
路径问题：确保 Python 环境已激活（虚拟环境），否则 playwright 命令可能无法识别。

---
*从 Gemini 导出，2026-05*
