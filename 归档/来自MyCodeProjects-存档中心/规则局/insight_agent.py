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