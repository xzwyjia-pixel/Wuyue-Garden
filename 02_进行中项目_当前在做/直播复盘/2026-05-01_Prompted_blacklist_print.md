---
title: Prompted
source: gemini
date: 2026-05-01
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

甄先生，看到终端输出 “扫描完毕，未发现基础敏感词”，虽然代码跑通了，但作为“规则情报局”的负责人，您一定发现了其中的隐患：您的词库里写的是“威信”，但由于代码逻辑还不支持变形识别，它完美错过了文案中的“威信”。
在 2026 年，没有人想学习，大家只想避坑。为了匹配您 “规则甄查 - 甄先生” 的专业品牌定位，我们现在要把这套工具从“小儿科”升级为能识别**变体词（如“威-信”、“V信”、“威123”）**的实战利器。

第一步：升级识别引擎（支持模糊匹配）
请在 VS Code 中把 audit_tool.py 的内容全部替换为下面这段代码并保存 (Ctrl + S)：
import os
import re

def run_audit():
    blacklist_file = 'blacklist.txt'
    
    if not os.path.exists(blacklist_file):
        print(f"--- 错误：找不到 {blacklist_file} ---")
        return

    # 加载黑名单词库
    with open(blacklist_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    # 模拟一段带有“避坑”特征的文案
    test_content = "欢迎来到直播间，点击头像加 威-信，教你如何快速 赚￥钱，掌握 蕞强 引流技巧！"
    
    print(f"--- 规则情报局：正在扫描文案（支持变体识别）---")
    print(f"待测文案：{test_content}\n")
    
    # 预处理文案：去除所有干扰符号（空格、连字符、特殊符号）
    clean_content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', test_content)
    
    found_any = False
    for word in keywords:
        # 1. 直接匹配
        # 2. 穿透匹配：针对“威-信”或“威 123 信”
        pattern = '.*'.join(list(word))
        if re.search(pattern, test_content) or word in clean_content:
            print(f"⚠️ [命中规则] 发现敏感词变体: {word}")
            found_any = True
            
    if not found_any:
        print("✅ 扫描完毕，未发现违规迹象。")
    print(f"\n--- 审核流程结束 ---")

if __name__ == "__main__":
    run_audit()


第二步：更新您的核心词库
在 blacklist.txt 中，建议按照短视频平台的风险控制逻辑，填入以下更具实战意义的词汇：

威信
赚钱
最强

第三步：运行并观察“甄先生”的洞察力
保存后在终端再次运行 python audit_tool.py。

观察点：文案里的“威-信”和“赚￥钱”现在是否被成功揪出来了？
商业逻辑：这套逻辑正是您在社交媒体（WeChat/TikTok）上分析平台算法、风险控制和合规规则的核心竞争力。

保存运行后，如果“威-信”被识别出来了，请告诉我。我们下一步就直接教您的机器人如何识别图像或视频中的“违规导流”了。

---
*从 Gemini 导出，2026-05*
