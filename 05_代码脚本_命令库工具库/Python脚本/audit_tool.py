import os
import re
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def local_scan(text):
    rules = {"威信": "威-信|微-x", "赚钱": "赚￥钱|赚.钱", "最强": "蕞强|最.强"}
    hits = []
    for word, pattern in rules.items():
        if re.search(pattern, text):
            hits.append(word)
    return hits

def deepseek_audit(text):
    print("\n📡 正在连接 DeepSeek 进行 AI 深度建模审计...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位短视频风控专家。请分析文案中的隐性违规，并给出‘静奢’风格的优化建议。"},
                {"role": "user", "content": f"请审计：{text}"}
            ],
            stream=False
        )
        return response.choices[0].message.content, response.usage
    except Exception as e:
        return f"❌ 审计失败: {str(e)}", None

if __name__ == "__main__":
    content_to_test = "欢迎来到直播间，点击头像加 威-信，教你如何快速 赚￥钱，掌握 蕞强 引流技巧！"
    print(f"\n--- 规则甄查 - 甄先生专用版 ---")
    
    # 1. 本地扫描
    hits = local_scan(content_to_test)
    for h in hits: print(f"⚠️ [本地风险] 命中关键词: {h}")
    
    # 2. AI 审计
    report, usage = deepseek_audit(content_to_test)
    print(f"\n--- AI 深度审计报告 ---\n{report}")
    
    if usage:
        print(f"\n--- 💡 消耗统计: 输入 {usage.prompt_tokens} | 输出 {usage.completion_tokens} | 总计 {usage.total_tokens} Tokens ---")
