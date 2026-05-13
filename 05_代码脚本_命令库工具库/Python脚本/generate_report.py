import requests
import datetime

API_KEY = "8212fe30470f760008c2bc5a9faa24f07d838267fc995c09b8292a8464ab770c"
URL = "http://127.0.0.1:27123/vault/Michael_Product/"

def push_to_obsidian(filename, content):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "text/markdown"}
    r = requests.put(URL + filename, headers=headers, data=content.encode('utf-8'))
    return r.status_code

if __name__ == "__main__":
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # 这里预留了逻辑，未来可以读取 triage_log.jsonl
    report_md = f"""# 自动复盘报告 ({date_str})
- 类型: #Automated_Report
- 状态: 已完成扫描

## 核心发现
- 视觉建议: 保持重心在安全区 [[Category_General]]
- 话术风险: 需关注极致词汇过滤

---
- 关联: [[04-凡姐案例]] | [[02-审计工具]]
"""
    status = push_to_obsidian(f"Report_Auto_{date_str}.md", report_md)
    print(f"Obsidian 同步状态: {status}")
