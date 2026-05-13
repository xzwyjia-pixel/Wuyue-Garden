---
title: C:\Users\think>defuddle --version
0.18.1

C:\Users\think>
source: gemini
date: 2026-05-02
category: 编程开发
tags: [gemini, 编程开发]
---

## C:\Users\think>defuddle --version
0.18.1

C:\Users\think>

抱歉，我之前对 Defuddle 的功能理解有误，误导了你将其作为 JavaScript 代码解密工具。
Defuddle 实际上是由 Obsidian 的 CEO (Steph Ango) 开发的一个网页内容提取工具。它的作用是把网页（URL）或 HTML 文件中多余的广告、导航栏去掉，提取出干净的正文并转换成 Markdown 格式。
1. 为什么会报错？
报错 unknown command 'main.js' 是因为 Defuddle 的命令行格式要求先输入一个具体的指令（子命令），比如 parse。

它的正确用法： 应该是 defuddle parse <网页链接或文件>。
适用场景： 如果你是在研究短视频平台规则时，想把某个长篇累牍的规则网页一键转成干净的 Markdown 笔记，它非常有效。


2. 如果你的目的是“解密/查看插件源码”
如果你是想把 Obsidian 插件中那些混淆过（看不懂）的 main.js 还原成人类可读的代码，你应该使用的正确工具是 webcrack 或 js-beautify。
推荐方案：使用 webcrack
它是目前处理 Webpack 混淆代码最强大的工具之一。

安装：
在终端输入：
npm install -g webcrack


使用：
切换到插件所在的文件夹，运行：

    webcrack main.js -o ./output
    ```
    这会把 `main.js` 解码并整理到 `output` 文件夹中，代码逻辑会变得非常清晰。

---

### 3. 如何修正你现在的操作？
既然你已经进入了 `C:\Users\think` 路径，且 Defuddle 已经装好了，你可以先试试它的**真实功能**（比如抓取你的研究资料）：

*   **把一个规则网页转成 Markdown：**
    ```cmd
    defuddle parse https://example.com/rules --md -o rules.md
    ```

**总结：**
*   **Defuddle**：用于**网页转 Markdown**（对你的“规则甄查”项目收集素材很有用）。
*   **Webcrack**：用于**还原/解密插件代码**（对你分析插件原理有用）。

非常抱歉之前的口误！你现在是想继续研究如何反混淆插件代码，还是想试试用 Defuddle 抓取一些短视频平台的规则网页？

---
*从 Gemini 导出，2026-05*
