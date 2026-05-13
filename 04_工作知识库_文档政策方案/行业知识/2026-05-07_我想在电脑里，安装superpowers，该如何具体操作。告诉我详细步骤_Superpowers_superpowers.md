---
title: 我想在电脑里，安装superpowers，该如何具体操作。告诉我详细步骤
source: gemini
date: 2026-05-07
category: 编程开发
tags: [gemini, 编程开发]
---

## 我想在电脑里，安装superpowers，该如何具体操作。告诉我详细步骤

安装 Superpowers（一个开源的、支持协作的 HTML5 游戏引擎）主要有两种方式：一种是直接下载编译好的安装包（适合大多数用户），另一种是从 GitHub 源码手动构建（适合开发者或需要自定义插件的用户）。
以下是详细的安装步骤：
方法一：下载预编译安装包（最简单）
这是官方推荐给普通用户的方法，不需要配置复杂的编程环境。

访问官方下载页面：
前往 Superpowers 的 itch.io 页面。
点击下载：
点击“Download Now”。由于它是开源免费软件，你可以选择捐赠，也可以点击“No thanks, just take me to the downloads”直接进入下载列表。
选择系统版本：
根据你的电脑系统选择对应的压缩包：

Windows: 下载 superpowers-X.X.X-win.zip。
macOS / Linux: 下载对应的 .zip 或 .tar.gz 文件。


解压并运行：

将下载的压缩包解压到你电脑的一个文件夹中（建议不要放在系统盘）。
双击运行 Superpowers.exe（Windows）或执行文件。


启动服务：
打开软件后，它会提示你启动服务器。Superpowers 是基于服务器架构的，即使你在本地单机使用，也需要先运行它自带的本地服务器。


方法二：从源码手动安装（高级版）
如果你需要最新的功能或进行插件开发，可以使用这种方式。
前提条件：
你需要先安装好 Node.js（建议 LTS 版本）和 Git。
操作步骤：

克隆核心仓库：
打开终端或命令行（CMD/PowerShell），输入：
git clone https://github.com/superpowers/superpowers-core superpowers/core
cd superpowers/core


克隆游戏系统：
Superpowers 需要特定的游戏系统（如 TypeScript 系统）才能工作：
git clone --recursive https://github.com/superpowers/superpowers-game systems/game


安装依赖并编译：
在 superpowers/core 目录下执行：
npm install
npm run build


启动服务器：
编译完成后，运行：
node server start


访问编辑器：
打开浏览器，输入 http://localhost:4237/ 即可进入 Superpowers 仪表盘。


安装后的建议

创建账号：第一次进入时，你需要创建一个本地管理员账号。这只是为了保护你的项目，不需要联网。
资源包（Asset Packs）：Superpowers 官方提供了一套非常丰富的免费资源包（Sprites, 3D Models, Sounds），建议在官网上顺便下载，可以极大地提高开发效率。
关于 2026 年的现状：虽然 Sparklin Labs 已经停止了官方的大规模更新，但由于其完全开源且基于 Web 技术（TypeScript/Three.js），它在轻量化协作开发和教学中依然非常实用。

特别提醒：如果你是在安装某个特定的 AI 工具插件（如某些 AI Agent 的 "Superpowers" 插件），请告知我具体的软件名称（如 OpenCode 或 Claude Code），安装步骤会完全不同。

---
*从 Gemini 导出，2026-05*
