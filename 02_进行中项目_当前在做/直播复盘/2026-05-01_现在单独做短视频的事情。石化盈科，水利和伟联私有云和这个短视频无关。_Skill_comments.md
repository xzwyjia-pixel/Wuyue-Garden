---
title: 现在单独做短视频的事情。石化盈科，水利和伟联私有云和这个短视频无关。
source: gemini
date: 2026-05-01
category: 文案创意
subcategory: 短视频脚本
old_category: 文案创作
tags: [gemini, 文案创意, 短视频脚本]
---

## 现在单独做短视频的事情。石化盈科，水利和伟联私有云和这个短视频无关。

## 现在单独做短视频的事情。石化盈科，水利和伟联私有云和这个短视频无关。

明白，甄先生。既然现在完全聚焦于短视频创作本身，我们要解决的就是如何利用 Agent 免费、高效地从评论区抓取“AI新规”下的用户痛点，并转化为爆款文案。
要实现这个闭环，我们需要在您现有的 VS Code 环境下构建一个 “评论分析与脚本生成 Agent”。
1. 系统架构：如何建立 Agent 和 Skill
在您的本地系统中，我们将功能拆解为三个 Skill，由一个 Agent 调度：

Skill A: 语义提炼 (The Filter) —— 负责从杂乱的评论中提取疑虑和恐惧。
Skill B: 痛点建模 (The Insight) —— 负责将疑虑归类（如：封号焦虑、技术门槛、合规成本）。
Skill C: 脚本改写 (The Writer) —— 基于您的“避坑”逻辑生成 3 个关键点文案。


2. 核心 Skill 实现代码：insight_agent.py
请在 RulesBureau 文件夹下新建 insight_agent.py。这段代码将作为您的分析 Agent，它不仅会分析内容，还会直接生成文案。
import re

def analyze_comments(file_path):
    # 读取评论数据 (您可以手动将评论复制到 comments.txt)
    with open(file_path, 'r', encoding='utf-8') as f:
        comments = f.readlines()

    # 模拟 AI 新规下的高频痛点特征库
    pain_point_patterns = {
        "封号焦虑": r"(封号|限流|禁言|违规|下架)",
        "合规门槛": r"(标注|实名|备案|新规|要求)",
        "技术恐惧": r"(数字人|真假|AI生成|检测|算法)"
    }

    results = {"封号焦虑": 0, "合规门槛": 0, "技术恐惧": 0}
    
    # 执行痛点抓取 Skill
    for comment in comments:
        for point, pattern in pain_point_patterns.items():
            if re.search(pattern, comment):
                results[point] += 1

    return results

def generate_scripts(top_point):
    # 根据抓取到的第一大痛点，自动生成 3 个关键点文案
    scripts = {
        "封号焦虑": [
            "关键点1：揭秘 2026 AI 强制标注底线，哪些词发了必封号？",
            "关键点2：避坑指南！如何在不影响流量的前提下做好合规标注？",
            "关键点3：如果被限流了，这 3 个动作是唯一的自救机会。"
        ],
        "合规门槛": [
            "关键点1：别再盲目发视频了，AI 新规备案流程详解。",
            "关键点2：什么是‘显著标注’？3 个案例教你过审。",
            "关键点3：普通创作和 AI 创作的界限在哪里？政策专家这样说。"
        ]
    }
    return scripts.get(top_point, ["默认关键点：掌握新规，安全创作"])

if __name__ == "__main__":
    # 假设您已经把评论抓取到了 comments.txt
    file = 'comments.txt'
    try:
        trends = analyze_comments(file)
        top_issue = max(trends, key=trends.get)
        print(f"--- 规则情报局：痛点抓取完成 ---")
        print(f"当前全网最关注疑虑：{top_issue}\n")
        
        print(f"--- 为您生成的 3 个短视频脚本关键点 ---")
        for i, script in enumerate(generate_scripts(top_issue), 1):
            print(f"{i}. {script}")
    except FileNotFoundError:
        print("请先建立 comments.txt 并存入评论内容。")


3. 如何优化您的系统？
您现在的系统已经具备了“识别”能力，但要真正节省人力，需要做以下优化：

输入端自动化（免费方案）：

目前需要您手动将评论复制到 comments.txt。
优化：可以使用浏览器插件（如 Web Scraper 等免费工具）一键导出评论区，直接存入该文件。


建立“变体词库”联动：

将生成的脚本关键点，自动跑一遍您的 audit_tool.py。
作用：在文案写出来的一瞬间，就知道这 3 个关键点里有没有包含可能会被平台二次限流的“变形词”。


Prompt 模板库：

在文件夹里建立 prompts.md。针对不同的平台（抖音、视频号），预设好您的“甄先生”人设指令，让 Agent 产出的语言风格整齐划一。



4. 甄先生的下一步操作

建立 comments.txt：去您关注的 AI 新规视频下方，把那些高赞疑虑评论复制进去（每行一条）。
运行 insight_agent.py：看看它提炼出的第一痛点是否准确。
反馈：如果结果满意，我们可以下一步教 Agent 如何根据这些关键点，自动写出完整的 15 秒口播脚本。

甄先生，您目前手头有已经抓取到的评论样本吗？我们可以先试运行一下。

---
*从 Gemini 导出，2026-05*

---
*Gemini · 文案创意 / 短视频脚本 · 2026-05-01*
