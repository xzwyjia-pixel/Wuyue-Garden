---
title: 我现在想用Claude程序，把我的E盘下的Mycodeprojects目录下的所有文件都动态链接到obsidian软件里。并按照项目类型排列
source: gemini
date: 2026-05-10
category: 编程开发
tags: [gemini, 编程开发]
---

## 我现在想用Claude程序，把我的E盘下的Mycodeprojects目录下的所有文件都动态链接到obsidian软件里。并按照项目类型排列

这是一个非常高效的想法！将代码库与 Obsidian 联动，可以极大地提升技术笔记的深度。
不过，这里有一个技术上的小纠正：Obsidian 本身并不支持真正的文件系统“动态链接”（即它不会自动监控外部文件夹的变化并同步显示）。
要实现你的需求，目前最主流且稳定的方案是使用 mklink (符号链接) 或 Obsidian 插件。以下是针对你的目录结构的两种最佳操作路径：

方案一：使用 Windows 符号链接 (最推荐)
这种方法在系统底层创建一个“快捷方式”，让 Obsidian 认为这些代码文件夹就在它的库（Vault）内部。

打开管理员权限的终端：
按下 Win + X，选择“终端管理员”或“命令提示符（管理员）”。
输入 mklink 命令：
假设你的 Obsidian 库路径是 D:\MyNotes，你希望在里面创建一个 CodeProjects 文件夹：
mklink /D "D:\MyNotes\CodeProjects" "E:\Mycodeprojects"


/D 表示创建目录链接。
优点： 性能极高，文件在 E 盘只有一份，但 Obsidian 可以实时读取。


按项目类型排列：
因为符号链接只是镜像了你的文件夹结构，建议你在 E:\Mycodeprojects 下预先分好类（如 /Python, /Web, /C++）。Obsidian 会直接继承这个结构。


方案二：使用 Obsidian 插件 (更智能)
如果你希望在 Obsidian 里更优雅地展示代码（比如带预览、排除 node_modules 等干扰项），推荐配合插件使用。

使用 "Folder Notes" 插件：
可以为每个项目文件夹创建一个说明文档，点击文件夹时直接显示该项目的 README 或开发日志。
使用 "Obsidian Git"：
如果你的代码项目都有 Git 管理，可以在 Obsidian 里快速查看提交记录。
排除干扰文件：
在 Obsidian 设置中，进入 文件与链接 -> 排除文件，添加如下规则：

**/node_modules/**
**/.git/**
**/dist/**
**/target/**
这样可以防止代码库的冗余配置文件污染你的 Obsidian 全文搜索。




方案三：通过 Claude 自动化脚本分类
如果你不想手动整理 E:\Mycodeprojects，可以把文件列表导出来给 Claude，让它写一个 Python 脚本。
脚本逻辑如下：

扫描 E:\Mycodeprojects 下的所有子文件夹。
识别项目特征（如含有 package.json 的归类到 Web，含有 requirements.txt 的归类到 Python）。
在 Obsidian 库内自动创建分类文件夹，并针对每个项目执行 mklink。


⚠️ 注意事项

性能压力： 如果你的代码项目非常多且包含数万个小文件（如前端项目），Obsidian 的索引速度可能会变慢。务必设置“排除文件”。
不要直接编辑： 虽然可以在 Obsidian 里打开代码文件，但它本质是 Markdown 编辑器，不支持代码补全。建议在 Obsidian 里写“思路和文档”，点击路径链接跳转到 VS Code 进行开发。

你想尝试用 Python 脚本来自动化这个分类并建立链接的过程吗？我可以帮你写出代码。

---
*从 Gemini 导出，2026-05*
