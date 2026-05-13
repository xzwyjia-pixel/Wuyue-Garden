import os
import re

def analyze_rules(folder_path):
    """
    扫描文件夹内的文档，提取关于 '封禁'、'违规'、'限流' 的核心关键词
    """
    findings = []
    keywords = ["封禁", "违规", "限流", "低俗", "虚假", "封号"]
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".md") or file.endswith(".txt"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    for kw in keywords:
                        if kw in content:
                            findings.append(f"发现【{kw}】相关规则: 出现在 {file}")
    return list(set(findings))

if __name__ == "__main__":
    # 模拟扫描你存放文案或调研大纲的目录
    target = r"E:\Mycodeprojects\01-Production"
    print(f"正在分析目录: {target}")
    results = analyze_rules(target)
    for r in results:
        print(r)
