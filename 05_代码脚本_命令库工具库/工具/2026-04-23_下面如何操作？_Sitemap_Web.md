---
title: 下面如何操作？
source: gemini
date: 2026-04-23
category: 数据分析
tags: [gemini, 数据分析]
---

## 下面如何操作？

老甄，看你这张截图，开发者工具已经呼出来了，但你现在处于 “Elements（元素）” 标签页，这是看网页代码的地方，不是用来采集的。
咱们现在的目标是找到 Web Scraper 的操作界面。按以下步骤操作：
1. 找到插件入口
在面板顶部的那一排标签（Elements, Console, Sources...），最右边有一个 >> 双箭头符号。点击它，在弹出的下拉菜单里选择 Web Scraper。

如果下拉菜单里也没有，说明插件没安装成功或者没开启，去扩展程序页面重新刷新一下。

2. 建立采集地图（Create Sitemap）
进入 Web Scraper 界面后，你会看到几个主菜单。点击 Create new sitemap -> Create Sitemap。

Sitemap Name: 随便起个名，比如 shipinhao_caiji。
Start URL: 把你想要抓取的那个视频的网页版地址粘贴进去。

3. 设置最关键的“滚动选择器”
这是最核心的一步，因为视频号评论是向下滚动加载的。点击 Add new selector：

ID: 起名 comment_list。
Type: 选 Element scroll down（这是精华，它能自动帮你滚屏）。
Selector: 点击旁边的 Select 按钮，然后在网页上把评论区的那个大框点亮，点红。
Delay: 设置为 2000（给网页 2 秒加载时间，防止太快被封 IP）。

4. 抓取评论文字
在刚才建立的 comment_list 里面，再点 Add new selector：

ID: 起名 content。
Type: 选 Text。
Selector: 点击 Select，在网页上点选两条评论的文字，直到所有评论都变红，点 Done selecting。

5. 开始暴力采集
点击顶部菜单的 Sitemap (shipinhao_caiji) -> Scrape -> Start scraping。

这时候会弹出一个新窗口，你会看到它自己在疯狂往下滚。这时候千万别关掉它。


事后调查员的温馨提示：
老甄，你现在就是在给你的“规则情报局”搜集第一手证据。
等它滚完停下来，点击 Export data as CSV，你就能拿到那份沉甸甸的 Excel 原始数据了。这时候，你再把那些抱怨“封号、限流、AI”的内容一筛选，你的**“必死指令”视频脚本**就自动生成了。
现在的面板里看到 Web Scraper 了吗？看到的话，先去建立那个 Sitemap。

---
*从 Gemini 导出，2026-04*
