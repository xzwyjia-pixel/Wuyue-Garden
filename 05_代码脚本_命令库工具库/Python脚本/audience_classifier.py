"""
audience_classifier.py — 评论区客群分类
读直播评论数据, 按话术分类客群, 输出分类报告 + 话术优化建议
用法: python audience_classifier.py [--target <dir>] [--watch]
"""
import json, re, sys, time
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

if "--target" in sys.argv:
    idx = sys.argv.index("--target")
    TARGET = Path(sys.argv[idx + 1])
else:
    TARGET = Path("E:/MyCodeProjects/04-宝妈直播诊断系统/清晨烟火小厨")
PLATFORMS = [
    {"name": "视频号", "path": TARGET / "live_data_SuSu.jsonl"},
    {"name": "抖音",   "path": TARGET / "live_data_DouYin.jsonl"},
]

# 客群分类定义
# (类别名, 触发关键词列表, 话术建议模板)
SEGMENTS = [
    ("价格敏感型", {
        "多少钱", "价格", "贵", "便宜", "划算", "性价比",
        "什么价", "价位", "值不值", "太贵", "打折", "优惠", "特价",
        "三千", "多少", "送", "点不了",
    }, "强调品质/性价比话术, 对比日常价 vs 直播价, 用'划算'替代'便宜'"),
    ("烹饪方法型", {
        "怎么做", "怎么煮", "怎么弄", "怎么吃", "怎么做",
        "焯水", "炒", "炸", "蒸", "煮", "晒", "煎",
        "扯面", "切", "去苦", "焯", "腌", "洗",
        "教程", "配方", "配料", "做法", "步骤",
    }, "主动展示制作关键步骤, 回应烹饪疑问, '很多人问怎么做, 我教大家一个小窍门'"),
    ("食材讨论型", {
        "苦笋", "熏鹅", "南瓜", "黄鱼", "红糖", "酸菜",
        "笋", "鱼", "鸡", "鸭", "肉", "蛋",
        "梅干菜", "干货", "贝贝", "粉", "面粉",
        "油", "盐", "生抽", "酱油", "醋", "辣椒",
    }, "借机科普食材来源/品质, '这是福建武夷山的特产...', 建立选品专业形象"),
    ("地域相关型", {
        "福建", "浙江", "武夷山", "上饶", "千岛湖",
        "闽北", "闽南", "闽",
        "辣", "北方", "南方", "广东", "四川", "湖南",
        "江西", "云南", "贵州", "东北", "上海",
        "杭州", "温州",
        "浙", "赣", "缅北",
    }, "融入地域共鸣话术, '我们福建老乡都爱这个口味', 武夷山/千岛湖话术"),
    ("家庭生活型", {
        "老婆", "老公", "宝贝", "孩子", "我爸", "我妈",
        "奶奶", "爷爷", "姥姥", "全家", "一家",
        "我家", "你家", "小宝贝", "大宝贝",
        "男人", "女人", "媳妇", "婆婆",
    }, "家常话术拉近距离, '给家人做菜最幸福', 建立温暖家庭品牌"),
    ("互动闲聊型", {
        "来了", "早上好", "下午好", "晚上好", "早早早",
        "刚来", "在的", "在听", "大家好", "主播好",
        "关注了", "来了来了", "拜拜", "下了",
        "对的", "有道理", "是的",
    }, "积极回应亲切互动, 点名感谢, 保持高情绪价值话术"),
    ("粉丝支持型", {
        "好吃", "想要", "下单", "回购", "支持", "买了", "喜欢",
        "不错", "好产品", "已下单", "已买", "好吃吗", "好喝",
        "吃货", "超好吃", "好",
    }, "强化信任背书, '很多老客户回购', 引导晒单互动"),
    ("问题咨询型", {
        "怎么买", "哪里买", "链接", "下单", "怎么下单", "购买",
        "怎么拍", "怎么付", "能发吗", "包邮", "发货",
    }, "简化下单路径指引, 口播清晰操作步骤, 置顶购买链接"),
    ("负面反馈型", {
        "不好", "差评", "不行", "失望", "太难", "上当了", "不值",
        "不好吃", "被骗", "虚假", "退货", "退款",
    }, "私信/1对1解决, 直播间不纠结, 引导客服处理"),
]

# 纯用户名(无消息内容)识别: 如果"xxx:"后无实质内容
def has_message(text):
    """检查是否有实质消息内容, 非仅用户名"""
    # 格式 "用户名: 消息" 或 "用户名：消息"
    m = re.split(r"[:：]\s*", text, maxsplit=1)
    if len(m) == 2 and m[1].strip():
        return True, m[0].strip(), m[1].strip()
    return False, text.strip(), ""


def classify(text):
    """对一条评论消息分类, 返回 (segment, keyword) 或 None"""
    if not text or len(text) < 2:
        return None
    t = text.lower()
    for seg_name, keywords, _ in SEGMENTS:
        for kw in keywords:
            if kw.lower() in t:
                return seg_name, kw
    # 默认: 有消息内容但未匹配任何分类
    return None


def load_data():
    """加载所有评论数据"""
    all_comments = []  # [(platform, time, username, message)]
    for plat in PLATFORMS:
        path = plat["path"]
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except:
                    continue
                ts = entry.get("time", "")
                for text in entry.get("texts", []):
                    has_msg, user, msg = has_message(text)
                    if has_msg:
                        all_comments.append((plat["name"], ts, user, msg))
                    # 也收录纯用户名(表示该用户在直播间)
                    elif user and len(user) >= 2:
                        all_comments.append((plat["name"], ts, user, ""))
    return all_comments


def analyze(comments):
    """执行分类分析"""
    seg_counts = Counter()  # 类别 -> 评论数
    seg_users = defaultdict(set)  # 类别 -> {用户}
    seg_samples = defaultdict(list)  # 类别 -> [示例评论]
    kw_counts = Counter()  # 关键词命中统计
    platform_stats = defaultdict(lambda: defaultdict(int))
    user_total_msgs = Counter()  # 用户 -> 发言总数
    user_msgs = defaultdict(list)  # 用户 -> [消息]

    for plat, ts, user, msg in comments:
        if not msg:
            continue
        user_total_msgs[user] += 1
        user_msgs[user].append((ts, msg, plat))
        platform_stats[plat]["total_msgs"] += 1

        result = classify(msg)
        if result:
            seg, kw = result
            seg_counts[seg] += 1
            seg_users[seg].add(user)
            kw_counts[kw] += 1
            platform_stats[plat][seg] += 1
            if len(seg_samples[seg]) < 5:
                seg_samples[seg].append(f"{user}: {msg}")
        else:
            seg_counts["未分类"] += 1
            seg_users["未分类"].add(user)
            platform_stats[plat]["未分类"] += 1
            if len(seg_samples["未分类"]) < 5:
                seg_samples["未分类"].append(f"{user}: {msg}")

    # 活跃用户 Top10
    top_users = user_total_msgs.most_common(10)

    return {
        "total_comments": sum(1 for _, _, _, msg in comments if msg),
        "total_users": len(set(u for _, _, u, msg in comments if msg)),
        "seg_counts": seg_counts,
        "seg_users": {k: len(v) for k, v in seg_users.items()},
        "seg_samples": dict(seg_samples),
        "kw_counts": kw_counts.most_common(15),
        "platform_stats": dict(platform_stats),
        "top_users": top_users,
        "user_msgs": dict(user_msgs),
    }


def print_report(stats):
    """打印分析报告"""
    total = stats["total_comments"]
    users = stats["total_users"]

    print(f"\n{'='*60}")
    print(f"  客群分类分析报告")
    print(f"  数据: {TARGET.name}  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  {total}条评论  |  {users}位发言用户")
    print(f"{'='*60}")

    # 分类占比
    print(f"\n── 客群构成 ──────────────────────────")
    sorted_segs = sorted(stats["seg_counts"].items(), key=lambda x: -x[1])
    for seg, cnt in sorted_segs:
        pct = cnt / total * 100 if total > 0 else 0
        bar = "#" * int(pct / 3) + "-" * (20 - int(pct / 3))
        print(f"  {seg:<12} {cnt:>4}条 ({pct:5.1f}%) [{bar}]  {stats['seg_users'].get(seg, 0)}人")

    # 平台分布
    print(f"\n── 平台对比 ──────────────────────────")
    for plat, pdata in stats["platform_stats"].items():
        print(f"  [{plat}] 总{pdata['total_msgs']}条")
        for seg in sorted(pdata, key=lambda k: pdata[k], reverse=True):
            if seg != "total_msgs":
                print(f"    {seg}: {pdata[seg]}条")

    # 关键词热点
    print(f"\n── 高频关键词 ────────────────────────")
    for kw, cnt in stats["kw_counts"][:10]:
        bar = "#" * min(cnt, 20)
        print(f"  {kw:<12} {cnt:>3}次 {bar}")

    # 活跃用户
    print(f"\n── 活跃用户 Top10 ────────────────────")
    for i, (user, cnt) in enumerate(stats["top_users"], 1):
        print(f"  {i:>2}. {user:<12} {cnt}条")

    # 各类别话术建议
    print(f"\n── 话术优化建议 ──────────────────────")
    for seg_name, _, suggestion in SEGMENTS:
        cnt = stats["seg_counts"].get(seg_name, 0)
        if cnt > 0:
            print(f"\n  ▶ {seg_name} ({cnt}条)")
            print(f"    {suggestion}")
            samples = stats["seg_samples"].get(seg_name, [])
            if samples:
                print(f"    示例: {samples[0][:50]}")

    # 针对当前占比最大的类别提供专项建议
    if sorted_segs:
        top_seg, top_cnt = sorted_segs[0]
        if top_seg != "未分类":
            pct = top_cnt / total * 100
            print(f"\n  ★ 重点关注: {top_seg} ({pct:.0f}%)")
            # 找对应的话术建议
            for seg_name, _, suggestion in SEGMENTS:
                if seg_name == top_seg:
                    print(f"    → {suggestion}")
                    break

    print(f"\n{'='*60}\n")


def save_report(stats):
    """保存报告到 JSON"""
    out = TARGET / "audience_classification.json"
    report = {
        "generated_at": datetime.now().isoformat(),
        "target": str(TARGET),
        "total_comments": stats["total_comments"],
        "total_users": stats["total_users"],
        "segments": {},
        "top_keywords": [{"keyword": k, "count": c} for k, c in stats["kw_counts"]],
        "top_users": [{"user": u, "count": c} for u, c in stats["top_users"]],
        "suggestions": [],
    }
    for seg_name, cnt in sorted(stats["seg_counts"].items(), key=lambda x: -x[1]):
        user_cnt = stats["seg_users"].get(seg_name, 0)
        pct = cnt / stats["total_comments"] * 100 if stats["total_comments"] > 0 else 0
        suggestion = ""
        for sn, _, sug in SEGMENTS:
            if sn == seg_name:
                suggestion = sug
                break
        report["segments"][seg_name] = {
            "count": cnt,
            "percentage": round(pct, 1),
            "users": user_cnt,
            "suggestion": suggestion,
        }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"[分类] 报告已保存: {out}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if "--watch" in sys.argv:
        POLL = 60
        last_count = 0
        print(f"[分类] 持续监控模式, 每{POLL}s更新")
        while True:
            comments = load_data()
            total = sum(1 for _, _, _, msg in comments if msg)
            if total != last_count:
                stats = analyze(comments)
                if stats["total_comments"] > 0:
                    print(f"[分类] [{datetime.now().strftime('%H:%M:%S')}] {stats['total_comments']}条评论, {stats['total_users']}用户")
                    for seg, cnt in sorted(stats["seg_counts"].items(), key=lambda x: -x[1])[:5]:
                        print(f"  {seg}: {cnt}条")
                save_report(stats)
                last_count = total
            time.sleep(POLL)
    else:
        comments = load_data()
        if not comments:
            print("[分类] 无评论数据, 确保直播监控已运行")
            return
        print(f"[分类] 加载 {len(comments)} 条评论记录")
        stats = analyze(comments)
        print_report(stats)
        save_report(stats)


if __name__ == "__main__":
    main()
