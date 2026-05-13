import json
import pandas as pd
import os

def load_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def audit_logic(text, rules):
    risk_found = []
    refined_text = text
    risk_matrix = rules.get("risk_levels", {})
    
    for level, details in risk_matrix.items():
        focus_dict = details.get("focus", {})
        if isinstance(focus_dict, dict):
            for word, advice in focus_dict.items():
                if word in text:
                    risk_found.append(f"[{level}]命中{word}")
                    import re
                    match = re.search(r"“(.+?)”", advice)
                    if match:
                        refined_text = refined_text.replace(word, match.group(1))
    
    return ", ".join(risk_found) if risk_found else "合格", refined_text

def run_batch():
    # 1. 加载规则
    rules = load_rules('rules.json')
    
    # 2. 模拟/读取输入表格
    input_file = 'content.xlsx'
    if not os.path.exists(input_file):
        print(f"未找到 {input_file}，正在为您创建一个演示模板...")
        df_template = pd.DataFrame({
            '原始文案': [
                '这是全网第一的赚钱秘籍，绝对不封号！',
                '追求极致的资产增值方案，核心逻辑如下。',
                '点击领取私信我，最快入账方式。'
            ]
        })
        df_template.to_excel(input_file, index=False)

    # 3. 执行批量审计
    df = pd.read_excel(input_file)
    print(f"正在精密处理 {len(df)} 条文案...")
    
    results = df['原始文案'].apply(lambda x: audit_logic(str(x), rules))
    df['审计结论'], df['甄先生优化建议'] = zip(*results)

    # 4. 导出结果
    output_file = 'Audit_Batch_Report.xlsx'
    df.to_excel(output_file, index=False)
    print(f"--- 批量处理完成 ---")
    print(f"结果已精密存储至: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    run_batch()
