"""
ai_bridge/orchestrator.py — 并行分析 / 交叉辩论 / 深度推演 / 自动汇总结论
"""
import json, time, yaml
from datetime import datetime
from pathlib import Path
from typing import Callable

from .client import call_all, call_model, AIResponse, load_config

CONFIG_PATH = Path(__file__).parent / "config.yaml"


class AIOrchestrator:
    """AI分析编排器"""

    def __init__(self):
        self.config = load_config()
        self.history = []

    # ── 阶段1: 并行分析 ──
    def parallel_analyze(self, topic: str, context: str = "", models: list = None) -> dict:
        """所有AI并行分析同一问题"""
        system_prompt = f"""你是一位专业的直播运营分析师。请对以下问题进行深度分析。
分析要求：结构化输出(问题分析→根因→数据支撑→改进建议→预期效果)。
结论必须基于数据、可落地执行。"""

        prompt = f"""## 分析主题
{topic}

## 背景上下文
{context if context else '无额外上下文'}

## 分析要求
1. 识别核心问题（最多3个）
2. 分析根本原因
3. 提供数据支撑
4. 给出可执行改进建议
5. 预估改进后的效果
"""
        results = call_all(prompt, system_prompt, models)
        self.history.append({
            "phase": "parallel_analyze",
            "topic": topic,
            "timestamp": time.time(),
            "results": {k: v.to_dict() for k, v in results.items()},
        })
        return results

    # ── 阶段2: 交叉辩论 ──
    def cross_debate(self, topic: str, round_count: int = 2) -> list:
        """AI之间交叉辩论，互相质疑和补充"""
        rounds = []
        viewpoints = {}

        for round_i in range(round_count):
            round_num = round_i + 1
            debate_prompt = f"""## 辩论主题
{topic}

## 辩论规则
这是第{round_num}轮辩论。请对以下观点进行分析：
- 如果这是你的第一轮发言：请提出你的核心分析观点
- 如果这是回应轮：请回看其他人的观点，指出1-2个漏洞或补充点

其他AI的观点摘要:
{json.dumps(viewpoints, ensure_ascii=False, indent=2) if viewpoints else '暂无其他观点'}

请输出：你的观点、对他人观点的评价、补充建议。"""
            results = call_all(debate_prompt)
            viewpoints = {k: v.content for k, v in results.items() if v.success}
            rounds.append({
                "round": round_num,
                "results": {k: v.to_dict() for k, v in results.items()},
            })

        self.history.append({
            "phase": "cross_debate",
            "topic": topic,
            "rounds": rounds,
        })
        return rounds

    # ── 阶段3: 深度推演 ──
    def deep_reasoning(self, topic: str, scenario: str = "") -> dict:
        """推演不同执行策略的预期结果"""
        system_prompt = """你是一位推演专家。请模拟不同策略执行后的结果。
使用决策树或情景分析法，输出每种策略的: 预期效果/风险/概率/关键指标变化。"""

        prompt = f"""## 推演主题
{topic}

## 策略描述
{scenario if scenario else '执行改进方案中的各项建议'}

## 推演要求
1. 输出3种可能情景（乐观/中性/悲观）
2. 每种情景的概率、关键指标变化、所需条件
3. 推荐策略及理由
4. 风险点和应对预案
"""
        results = call_all(prompt, system_prompt)
        self.history.append({
            "phase": "deep_reasoning",
            "topic": topic,
            "results": {k: v.to_dict() for k, v in results.items()},
        })
        return results

    # ── 阶段4: 自动汇总结论 ──
    def synthesize(self, analysis_results: dict, topic: str) -> str:
        """汇总所有AI的分析结论，生成最终报告"""
        summaries = []
        for model_key, response in analysis_results.items():
            if isinstance(response, AIResponse) and response.success:
                summaries.append(f"## {model_key} ({response.model})\n{response.content}")
            elif isinstance(response, dict) and response.get("success"):
                summaries.append(f"## {model_key}\n{response.get('content', '')}")

        consensus_prompt = f"""## 汇总任务
以下是多个AI对同一主题的分析结果。请汇总：

## 分析主题
{topic}

## 各AI分析结果
{chr(10).join(summaries)}

## 汇总要求
1. 找出各AI的一致结论（共识点）
2. 标记分歧点（不同AI的不同观点）
3. 给出推荐结论
4. 格式：Markdown结构化报告
"""
        result = call_model("claude", consensus_prompt,
                            "你是一位总结专家。将多AI分析汇结构化成一份完整报告。")
        final_report = result.content if result.success else "汇总失败"

        self.history.append({
            "phase": "synthesize",
            "topic": topic,
            "final_report": final_report,
        })
        return final_report

    # ── 全流程一键执行 ──
    def full_pipeline(self, topic: str, context: str = "") -> dict:
        """一键执行：分析→辩论→推演→汇总"""
        output = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "phases": {},
        }

        # Phase 1: 并行分析
        print(f"[1/4] 并行分析: {topic}")
        phase1 = self.parallel_analyze(topic, context)
        output["phases"]["parallel_analyze"] = {k: v.to_dict() for k, v in phase1.items()}

        # Phase 2: 交叉辩论
        print(f"[2/4] 交叉辩论: 2轮")
        phase2 = self.cross_debate(topic)
        output["phases"]["cross_debate"] = phase2

        # Phase 3: 深度推演
        print(f"[3/4] 深度推演")
        phase3 = self.deep_reasoning(topic)
        output["phases"]["deep_reasoning"] = {k: v.to_dict() for k, v in phase3.items()}

        # Phase 4: 汇总
        print(f"[4/4] 自动汇总结论")
        output["final_report"] = self.synthesize(phase1, topic)

        return output

    def save_report(self, output: dict, output_path: Path = None):
        """保存报告到文件"""
        if output_path is None:
            output_path = Path("E:/MyCodeProjects/AI研讨报告")
            output_path.mkdir(parents=True, exist_ok=True)

        topic_slug = output["topic"][:30].replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{topic_slug}_{timestamp}"

        # Markdown
        md_path = output_path / f"{fname}.md"
        md_content = self._to_markdown(output)
        md_path.write_text(md_content, encoding="utf-8")

        # JSON (原始数据)
        json_path = output_path / f"{fname}.json"
        json_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

        return {"md": str(md_path), "json": str(json_path)}

    def _to_markdown(self, output: dict) -> str:
        lines = [
            "---",
            f"created: {output['timestamp']}",
            "tags: [AI研讨, 多模型分析, 自动生成]",
            "---",
            "",
            f"# {output['topic']}",
            "",
            "## 最终结论",
            output.get("final_report", "无"),
            "",
            "## 各模型原始分析",
        ]
        for model_key, result in output.get("phases", {}).get("parallel_analyze", {}).items():
            lines.append(f"\n### {model_key}")
            lines.append(f"- 耗时: {result.get('elapsed', 0)}s")
            lines.append(f"- 成功: {result.get('success', False)}")
            if result.get("error"):
                lines.append(f"- 错误: {result['error']}")
            if result.get("content"):
                lines.append(result["content"])

        lines.append("\n## 辩论记录")
        for round_data in output.get("phases", {}).get("cross_debate", []):
            lines.append(f"\n### 第{round_data['round']}轮")
            for model_key, result in round_data.get("results", {}).items():
                lines.append(f"\n**{model_key}**:")
                if result.get("content"):
                    lines.append(result["content"])

        lines.append("\n## 推演结果")
        for model_key, result in output.get("phases", {}).get("deep_reasoning", {}).items():
            lines.append(f"\n### {model_key}")
            if result.get("content"):
                lines.append(result["content"])

        return "\n".join(lines)
