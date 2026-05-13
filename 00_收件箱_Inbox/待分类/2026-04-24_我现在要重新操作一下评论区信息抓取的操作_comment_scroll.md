---
title: 我现在要重新操作一下评论区信息抓取的操作
source: gemini
date: 2026-04-24
category: 文案创作
tags: [gemini, 文案创作]
---

## 我现在要重新操作一下评论区信息抓取的操作

针对“评论区抓取”这一高阶需求，它比抓取标题要复杂得多，因为视频号的评论区是**“动态懒加载”**的（即你需要一边向下滚动，它才会一边加载出新评论）。
请按照以下“情报局标准工作流”重新操作，这次我们直接精准打击：
第一步：设置“滚动加载”规则（关键）
抓评论不能只选 Text 类型，必须让机器人学会“自动滚动”。

进入你的 Sitemap rules_intelligence 面板。
在 Selectors 列表里，点击 Add new selector。
ID: 命名为 comment_scroll。
Type: 重点！下拉选择 Element scroll downstream（意为：向下滚动并抓取元素）。
Selector: 点击 Select，去网页上点击评论区外层那个包裹着所有评论的容器框（通常是一整块大的空白区域）。点击后显示 Done selecting!。
Save Selector: 保存。

第二步：定义具体的“评论内容”
现在我们要告诉机器人，在那块滚动的区域里，到底要抓什么：

在刚才建好的 comment_scroll 这一行，点击它的 ID 进入其内部（这是“父级”）。
在里面再次点击 Add new selector。
ID: 命名为 comment_text。
Type: 选择 Text。
Selector: 点击 Select，去框选其中一条评论的文字内容。
Multiple: 一定要勾选这个选项（因为评论是一堆，不是一个）。
Save Selector: 保存。


第三步：为什么这次能成功？

逻辑闭环： 我们定义了一个父级规则（comment_scroll），它的任务就是“不断滚轮下滑”；我们定义了一个子级规则（comment_text），它的任务就是“只要看到文字就抓下来”。
自动配合： 当你点击 Scrape 时，机器人会一边滚轮触动网页加载，一边把加载出来的评论全部收进 Excel。


💡 甄先生（Mr. Zhen）的防封号提示：
视频号的评论区如果有反爬机制（例如加载过快会弹验证），请务必在 Scrape 时的配置里做如下调整：

Page load delay: 建议设为 3000 或 5000（3-5秒），让加载更从容。
Request interval: 同样设为 3000。

现在请操作：
你先按照上述步骤，把那个 Element scroll downstream 规则建好。如果中途页面弹出了“登录”提示，请立刻用你刚才准备好的方式扫码，确保这个滚动动作是在“登录后”的后台页面执行的。
操作完成后，点击 Data preview，看看能不能看到刚才滚动抓取出来的几条评论？ 如果看到了，这套评论采集引擎就彻底建成了！

---
*从 Gemini 导出，2026-04*
