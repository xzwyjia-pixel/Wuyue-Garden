import os
import re

# 甄先生，这里需要安装一个轻量级库来处理拼音
# 请在终端输入: pip install pypinyin
from pypinyin import lazy_pinyin

def run_audit():
    blacklist_file = 'blacklist.txt'
    if not os.path.exists(blacklist_file):
        print(f"--- 错误：找不到 {blacklist_file} ---")
        return

    with open(blacklist_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    # 测试文案：包含了“威-信”、“赚￥钱”和同音字“蕞强”
    test_content = "欢迎来到直播间，点击头像加 威-信，教你如何快速 赚￥钱，掌握 蕞强 引流技巧！"
    
    print(f"--- 规则情报局：正在执行【谐音+变体】深度扫描 ---")
    print(f"待测文案：{test_content}\n")
    
    # 预处理：提取文案纯净拼音流
    clean_content = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', test_content)
    content_pinyin = ''.join(lazy_pinyin(clean_content))
    
    found_any = False
    for word in keywords:
        # 1. 逻辑 A：正则穿透（识别 威-信）
        pattern = '.*'.join(list(word))
        
        # 2. 逻辑 B：拼音穿透（识别 蕞强/最强）
        word_pinyin = ''.join(lazy_pinyin(word))
        
        if re.search(pattern, test_content) or word in clean_content or word_pinyin in content_pinyin:
            print(f"⚠️ [高风险] 命中规则变体: {word} (匹配模式: 穿透或谐音)")
            found_any = True
            
    if not found_any:
        print("✅ 扫描完毕，暂未发现违规规避手段。")
    print(f"\n--- 审核流程结束 ---")

if __name__ == "__main__":
    run_audit()