import json
import os

def load_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def perform_audit(text, rules):
    results = {"HIGH": [], "MEDIUM": [], "LOW": []}
    risk_matrix = rules.get("risk_levels", {})
    refined_text = text
    
    for level, details in risk_matrix.items():
        focus_dict = details.get("focus", {})
        if isinstance(focus_dict, dict):
            for word, advice in focus_dict.items():
                if word in text:
                    results[level].append({"word": word, "advice": advice})
                    # 简单的重写逻辑：将关键词替换为建议中的核心词
                    # 这里提取建议中引号内的内容
                    import re
                    match = re.search(r"“(.+?)”", advice)
                    if match:
                        refined_text = refined_text.replace(word, match.group(1))
    
    return results, refined_text

def generate_markdown_report(original, refined, results, filename="Audit_Report.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 规则甄查 · 文案审计报告\n\n")
        f.write(f"**品牌调性：** 极简精密 | 静奢风\n\n")
        f.write(f"## 1. 风险诊断看板\n")
        
        has_risk = False
        for level in ["HIGH", "MEDIUM", "LOW"]:
            if results[level]:
                has_risk = True
                f.write(f"### [{level}] 级别风险\n")
                for item in results[level]:
                    f.write(f"- 🚩 **命中词：** {item['word']}\n")
                    f.write(f"  - 💡 **优化建议：** {item['advice']}\n")
        
        if not has_risk:
            f.write("> ✨ 未检测到明显合规风险，文案精密性良好。\n")
            
        f.write(f"\n## 2. 文案精密重构\n")
        f.write(f"| 原始文案 (雷区) | 甄先生优化版 (静奢) |\n")
        f.write(f"| :--- | :--- |\n")
        f.write(f"| {original} | **{refined}** |\n\n")
        f.write(f"---\n*报告生成：规则甄查 - 甄先生 自动化引擎*")
    
    print(f"\n[精密导出] 报告已生成至: {os.path.abspath(filename)}")

if __name__ == "__main__":
    try:
        rules_data = load_rules('rules.json')
        test_content = "这是全网第一的赚钱秘籍，绝对不封号，私信我领链接！"
        
        audit_res, refined_content = perform_audit(test_content, rules_data)
        
        # 输出到控制台
        print("\n--- 正在进行精密审计 ---")
        print(f"原始文案: {test_content}")
        print(f"重构文案: {refined_content}")
        
        # 导出 Markdown 报告
        generate_markdown_report(test_content, refined_content, audit_res)
        
    except Exception as e:
        print(f"运行时错误: {e}")
