---
title: Prompted
source: gemini
date: 2026-05-01
category: 审计合规
tags: [gemini, 审计合规]
---

## Prompted

甄先生，看到 image_b760a1.png 终端里那行清爽的 Hello, world!，恭喜您！这标志着您的 “规则情报局” 物理环境已经彻底打通。虽然由于本地模型规模较小，我们绕过了一些自动化的坑，但现在的状态是最踏实的。
1. 甄先生，让我们注入“灵魂代码”
既然 Python 已经可以成功打印输出，我们现在把刚才那个简单的 print 换成真正的规则识别引擎。
请将 audit_tool.py 中的内容全部替换为以下代码并保存（Ctrl + S）：
import os

def run_audit():
    blacklist_file = 'blacklist.txt'
    
    # 检查黑名单是否存在
    if not os.path.exists(blacklist_file):
        print(f"--- 错误：找不到 {blacklist_file} ---")
        return

    # 加载黑名单词库
    with open(blacklist_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    # 模拟一段需要审核的直播间文案
    # 您之后可以把这里改成从文本文件读取
    test_content = "欢迎来到直播间，点击头像加威信，教你如何快速赚钱，掌握最强引流技巧！"
    
    print(f"--- 规则情报局：正在扫描文案 ---")
    print(f"待测文案：{test_content}\n")
    
    found_any = False
    for word in keywords:
        if word in test_content:
            print(f"⚠️ [命中规则] 发现敏感词: {word}")
            found_any = True
            
    if not found_any:
        print("✅ 扫描完毕，未发现基础敏感词。")
    print(f"\n--- 审核流程结束 ---")

if __name__ == "__main__":
    run_audit()


2. 下一步动作

保存代码：按下 Ctrl + S（确保 audit_tool.py 标签上的白点消失）。
更新词库：点击 blacklist.txt 标签页，填入您关心的词，例如：威信、赚钱、最强，然后也按下 Ctrl + S。
运行程序：在终端输入 python audit_tool.py 并回车。

3. 为什么这一步对您很重要？
作为 “规则甄查 - 甄先生” 品牌的掌舵人，您在 2026 年的核心使命是帮大家在短视频平台“避坑”。这段代码虽然简单，但它建立了最基础的“合规检测”模型。
等您运行成功后，我们下一回合就进入**“变体识别”**——针对那些故意绕过算法的词（比如把“威信”写成“威-信”或“V心”）编写高级侦测逻辑。
保存并运行后，看到那些“⚠️ [命中规则]”的提示了吗？

---
*从 Gemini 导出，2026-05*
