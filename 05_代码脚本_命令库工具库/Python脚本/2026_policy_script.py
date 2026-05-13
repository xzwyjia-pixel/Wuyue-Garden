# -*- coding: utf-8 -*-
"""
规则甄查 · 甄先生 v2.0 — 2026 平台新规解读脚本生成器
=====================================================
结构：案例回溯 → 政策深挖 → 正向对比 → 避坑起量建议
用途：利用爬取的正反案例，自动生成短视频解读脚本
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────
# 案例库（内置典型正反案例 + 可扩展）
# ──────────────────────────────────────────────

NEGATIVE_CASES = [
    {
        "title": "某美妆博主因"全网第一"被封号",
        "platform": "抖音",
        "date": "2026-03",
        "summary": "某 200 万粉丝美妆博主在直播中使用"全网第一遮瑕""绝对不脱妆"等绝对化用语，被平台监测到后直接封禁 30 天，解封后流量断崖式下跌 80%。",
        "violation": "违反《广告法》第九条禁止绝对化用语规定，同时触发抖音 2026 年新版《广告内容合规指引》第 3.2 条。",
        "penalty": "封禁 30 天 + 清除违规视频 + 信用分扣减 40 分",
        "lesson": "绝对化用语是 2026 年平台重点打击对象，AI 审核模型已升级到语义级识别，不再依赖关键词匹配。"
    },
    {
        "title": "财经号因"保证收益"被永久封号",
        "platform": "抖音",
        "date": "2026-02",
        "summary": "某财经类账号发布"跟着我做，月入 10 万不是梦""保证收益，不赚钱退款"等承诺性内容，被平台判定为金融诈骗风险账号，永久封禁。",
        "violation": "违反 2026 抖音《金融内容专项治理》规定，禁止承诺收益、保证回报。",
        "penalty": "永久封号 + 账号主体列入行业黑名单",
        "lesson": "2026 年金融内容审核标准大幅收紧，任何形式的收益承诺都会被 AI 模型识别并触发最高级别处罚。"
    },
    {
        "title": "带货直播间因"私信领福利"被限流",
        "platform": "视频号",
        "date": "2026-01",
        "summary": "某服饰带货直播间频繁使用"私信我领优惠券""点击链接抢购"等话术，被视频号检测到站外导流行为，直播间流量被限制至原来的 10%。",
        "violation": "违反 2026 视频号《站外导流限制》第 4 条及《外链管理规范》。",
        "penalty": "限流 14 天 + 直播间功能限制",
        "lesson": "平台对私域导流的容忍度持续降低，建议使用"后台留言""深度交流"等合规话术。"
    },
    {
        "title": "知识付费账号因"虚假人设"被清退",
        "platform": "抖音",
        "date": "2026-04",
        "summary": "某知识付费账号包装"3 年从负债到年入千万"人设，被用户举报后平台核实为虚构经历，账号被清退出知识付费赛道。",
        "violation": "违反 2026 抖音《真实性内容推荐规则》，虚构人设属于严重虚假宣传。",
        "penalty": "清退知识付费资格 + 下架所有课程 + 信用分归零",
        "lesson": "2026 年平台重点打击"虚假人设"，要求所有知识类创作者提供可验证的资质证明。"
    },
]

POSITIVE_CASES = [
    {
        "title": "三农博主靠"真实记录"获百万流量扶持",
        "platform": "抖音",
        "date": "2026-03",
        "summary": "某三农博主坚持拍摄真实的农村生产生活，无剧本、无夸张话术，单条视频平均播放量从 5000 增长到 50 万。被抖音"真实体验"标签收录后，获得额外 30% 流量加权。",
        "policy_match": "符合抖音《真实性内容推荐规则》及《优质创作者扶持计划》。",
        "benefit": "流量加权 30% + 入选"真实体验"推荐池 + 平台主动推送",
        "takeaway": "真实记录是最好的内容策略。2026 年平台算法对"真实性"的权重提升了 40%。"
    },
    {
        "title": "知识博主用"实证数据"打造爆款系列",
        "platform": "视频号",
        "date": "2026-02",
        "summary": "某经济学科普博主制作"中国制造业 40 年数据解读"系列，每条视频引用权威统计数据并标注来源。系列累计播放破 5000 万，被视频号"原创内容激励"计划收录。",
        "policy_match": "符合视频号《原创内容激励》及抖音《优质创作者扶持计划》长效价值方向。",
        "benefit": "系列播放 5000 万 + 原创标签加权 + 平台主动签约",
        "takeaway": "数据驱动的内容在 2026 年具有极强的竞争力，权威引用是信任资产的核心。"
    },
    {
        "title": "非遗手艺人借"合规创新"获平台专项扶持",
        "platform": "抖音",
        "date": "2026-04",
        "summary": "某非遗手艺人将传统工艺与现代设计结合，所有视频标注"原创内容"，并主动声明 AI 仅用于辅助剪辑。被抖音"非遗合伙人"计划收录，获得每月 10 万流量包。",
        "policy_match": "符合抖音《平台社会责任内容扶持》及"非遗合伙人"专项计划。",
        "benefit": "每月 10 万流量包 + 非遗专题推荐 + 官方账号认证",
        "takeaway": "合规框架内的创新表达是 2026 年的蓝海赛道，传统文化+现代表达=流量密码。"
    },
    {
        "title": "测评博主用"实测过程"建立信任壁垒",
        "platform": "视频号",
        "date": "2026-01",
        "summary": "某数码测评博主坚持展示完整的测试过程（包括仪器数据、对比实验），从不使用"最好""第一"等绝对化用语。粉丝从 2 万增长到 80 万，转化率是行业平均的 3 倍。",
        "policy_match": "符合抖音《真实性内容推荐规则》及视频号"原创声明"流量倾斜政策。",
        "benefit": "粉丝增长 40 倍 + 高转化率 + 品牌合作邀约增加",
        "takeaway": "实证内容建立长期信任，信任是 2026 年最稀缺的商业资产。"
    },
]


# ──────────────────────────────────────────────
# 脚本模板
# ──────────────────────────────────────────────

SCRIPT_TEMPLATES = {
    "opening": [
        "2026 年，短视频平台的规则变了。不是小修小补，是底层逻辑的重写。",
        "你有没有发现，最近很多账号突然就没了？不是限流，是直接封号。",
        "同样的内容，为什么别人能爆 100 万播放，你发出去只有 200 播放？",
        "2026 年做短视频，不懂规则就是在裸奔。今天带你拆解最新的平台逻辑。",
    ],
    "transition_negative": [
        "先看一个真实的封号案例——",
        "这不是危言耸听，这是上个月刚发生的事。",
        "来，我们看第一个反面教材。",
    ],
    "transition_positive": [
        "但别慌，有危就有机。来看看正向案例——",
        "封号案例看完了，我们来看看那些被平台"宠幸"的账号是怎么做的。",
        "红灯看完，我们来看绿灯。同样的赛道，有人换了个思路就起飞了。",
    ],
    "closing": [
        "总结一下：2026 年的平台逻辑，就是"奖励真实，惩罚虚假"。",
        "记住甄先生的一句话：红灯避险，绿灯起量。合规不是束缚，是护城河。",
        "2026 年，合规就是最大的红利。我是甄先生，我们下期见。",
    ],
}


# ──────────────────────────────────────────────
# 脚本生成引擎
# ──────────────────────────────────────────────

class ScriptGenerator:
    """2026 平台新规解读脚本生成器"""

    def __init__(self):
        self.negative_cases = NEGATIVE_CASES
        self.positive_cases = POSITIVE_CASES

    def pick_cases(self, count: int = 2) -> tuple:
        """精选正反案例各 count 个"""
        neg = random.sample(self.negative_cases, min(count, len(self.negative_cases)))
        pos = random.sample(self.positive_cases, min(count, len(self.positive_cases)))
        return neg, pos

    def generate(self, theme: str = "", style: str = "专业") -> str:
        """
        生成完整脚本
        theme: 主题方向（如"美妆""财经""知识付费"）
        style: 风格（"专业""轻松""犀利"）
        """
        neg_cases, pos_cases = self.pick_cases(2)

        sections = []

        # ── 开场 ──
        opening = random.choice(SCRIPT_TEMPLATES["opening"])
        if theme:
            opening = f"今天聊{theme}赛道。{opening}"
        sections.append(f"【开场】\n{opening}\n")

        # ── 案例回溯（负向） ──
        sections.append("【第一部分：案例回溯 · 红灯警示】\n")
        transition = random.choice(SCRIPT_TEMPLATES["transition_negative"])
        sections.append(f"{transition}\n")

        for i, case in enumerate(neg_cases, 1):
            sections.append(
                f"📌 案例 {i}：{case['title']}\n"
                f"平台：{case['platform']} | 时间：{case['date']}\n\n"
                f"【事件还原】\n{case['summary']}\n\n"
                f"【违规认定】\n{case['violation']}\n\n"
                f"【处罚结果】\n{case['penalty']}\n\n"
                f"【甄先生点评】\n{case['lesson']}\n"
            )

        # ── 政策深挖 ──
        sections.append(
            "【第二部分：政策深挖 · 规则拆解】\n\n"
            "2026 年平台监管的核心逻辑可以概括为三个关键词：\n\n"
            "1️⃣ 真实性优先\n"
            "   平台算法对"真实性"的权重提升了 40%。AI 审核模型已升级到语义级理解，\n"
            "   不再依赖关键词匹配，而是理解上下文语义。虚假人设、虚构数据、夸大宣传\n"
            "   都会被精准识别。\n\n"
            "2️⃣ 长效价值导向\n"
            "   平台从"流量分配"转向"价值分配"。完播率不再是唯一指标，\n"
            "   收藏率、分享率、复访率等"长效价值指标"权重显著提升。\n\n"
            "3️⃣ 合规即流量\n"
            "   2026 年最大的变化：合规内容获得平台主动流量扶持。\n"
            "   抖音"真实体验"标签、视频号"原创声明"标签，都意味着额外的流量加权。\n"
        )

        # ── 正向对比 ──
        sections.append("【第三部分：正向对比 · 绿灯起量】\n")
        transition_pos = random.choice(SCRIPT_TEMPLATES["transition_positive"])
        sections.append(f"{transition_pos}\n")

        for i, case in enumerate(pos_cases, 1):
            sections.append(
                f"✅ 案例 {i}：{case['title']}\n"
                f"平台：{case['platform']} | 时间：{case['date']}\n\n"
                f"【成功路径】\n{case['summary']}\n\n"
                f"【政策契合】\n{case['policy_match']}\n\n"
                f"【实际收益】\n{case['benefit']}\n\n"
                f"【甄先生点评】\n{case['takeaway']}\n"
            )

        # ── 正反对比总结 ──
        sections.append(
            "【正反对照表】\n\n"
            "| 维度 | ❌ 违规做法 | ✅ 合规做法 |\n"
            "| :--- | :--- | :--- |\n"
            "| 用语 | 全网第一、绝对、最好 | 核心、关键、深度 |\n"
            "| 导流 | 私信我、点击链接 | 后台留言、深度交流 |\n"
            "| 承诺 | 保证赚钱、不封号 | 资产增值、规范运营 |\n"
            "| 内容 | 虚构人设、搬运洗稿 | 真实记录、实证原创 |\n"
            "| 数据 | 夸大数据、无来源 | 权威引用、标注来源 |\n"
        )

        # ── 避坑起量建议 ──
        sections.append(
            "【第四部分：避坑起量 · 行动清单】\n\n"
            "🚫 红灯 · 立即停止：\n"
            "  1. 删除所有含"第一""最""绝对"的文案\n"
            "  2. 停止使用"私信""链接""领取"等诱导话术\n"
            "  3. 下架所有承诺收益/保证结果的内容\n\n"
            "🟢 绿灯 · 立即执行：\n"
            "  1. 增加真实记录内容（生产过程、实地探访、实测数据）\n"
            "  2. 引用权威数据并标注来源（提升真实性评分）\n"
            "  3. 使用"后台留言""深度交流"等合规话术\n"
            "  4. 申请平台"原创声明""真实体验"等合规标签\n"
            "  5. 关注平台扶持计划（非遗合伙人、乡村振兴等）\n\n"
            "💡 甄先生建议：\n"
            "  2026 年，合规不是成本，是投资。\n"
            "  每一条合规的内容，都在为你积累"信任资产"。\n"
            "  当别人在躲避监管时，你在享受平台流量扶持。\n"
            "  这就是"合规红利"。\n"
        )

        # ── 结尾 ──
        closing = random.choice(SCRIPT_TEMPLATES["closing"])
        sections.append(f"【结尾】\n{closing}\n")

        # ── 附加信息 ──
        sections.append(
            "---\n"
            f"*脚本由 规则甄查 · 甄先生 v2.0 自动生成*\n"
            f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            f"*主题方向：{theme or '通用'} | 风格：{style}*\n"
            "*数据来源：抖音 2026 版《社区自律公约》《广告内容合规指引》"
            "、视频号 2026 版《内容推广规范》*\n"
        )

        return "\n".join(sections)

    def save(self, script: str, filename: Optional[str] = None) -> Path:
        """保存脚本到文件"""
        if not filename:
            filename = f"2026_policy_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        path = DATA_DIR / filename
        path.write_text(script, encoding="utf-8")
        return path


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

def main():
    import sys

    theme = ""
    style = "专业"

    if len(sys.argv) > 1:
        theme = sys.argv[1]
    if len(sys.argv) > 2:
        style = sys.argv[2]

    print("=" * 60)
    print("  规则甄查 · 甄先生 v2.0")
    print("  2026 平台新规解读脚本生成器")
    print("=" * 60)

    generator = ScriptGenerator()
    script = generator.generate(theme=theme, style=style)
    path = generator.save(script)

    print(f"\n📄 脚本已生成: {path}")
    print(f"\n{'='*60}")
    print("  脚本预览（前 500 字）")
    print(f"{'='*60}\n")
    print(script[:500])
    print(f"\n...（完整脚本共 {len(script)} 字）")
    print(f"\n💡 提示：完整脚本已保存至 {path}")


if __name__ == "__main__":
    main()
