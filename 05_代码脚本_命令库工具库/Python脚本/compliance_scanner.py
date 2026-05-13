import os

# 深度细化的话术库
FORBIDDEN_RULES = {
    "虚假夸大": ["最", "第一", "绝对", "万能", "100%", "唯一"],
    "诱导互动": ["点点关注", "扣个1", "评论区刷起", "关注我领"],
    "医疗助农风险": ["根治", "疗效", "预防", "抗癌", "救救农民"] 
}

def deep_scan(target_dir):
    print(f"--- 深度话术扫描启动 ---")
    for file in os.listdir(target_dir):
        if file.endswith((".md", ".txt")):
            with open(os.path.join(target_dir, file), 'r', encoding='utf-8') as f:
                content = f.read()
                for cat, words in FORBIDDEN_RULES.items():
                    for word in words:
                        if word in content:
                            print(f"🚩 [话术风险] {file} 命中 '{cat}': {word}")

if __name__ == "__main__":
    deep_scan(r"E:\Mycodeprojects\01-Production")
