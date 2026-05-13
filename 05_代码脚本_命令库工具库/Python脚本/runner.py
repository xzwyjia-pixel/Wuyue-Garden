"""
ai_bridge/runner.py — AI专家研讨集群 主入口
支持: 一键分析 / 启动飞书Bot / Obsidian同步 / 自检
"""
import sys, json, time, yaml
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def cmd_setup():
    """初始化配置"""
    cfg_path = CONFIG_PATH
    if cfg_path.exists():
        print(f"[!] 配置文件已存在: {cfg_path}")
        overwrite = input("  覆盖? (y/N): ").strip().lower()
        if overwrite != "y":
            print("[*] 保留现有配置")
            return

    config = {
        "models": {
            "gpt": {"api_key": "", "model": "gpt-4o"},
            "gemini": {"api_key": "", "model": "gemini-2.0-flash"},
            "claude": {"api_key": "", "model": "claude-3-5-sonnet-20241022"},
            "doubao": {"api_key": "", "model": "doubao-pro-32k"},
            "tongyi": {"api_key": "", "model": "qwen-max"},
            "wenxin": {"api_key": "", "secret_key": "", "model": "ernie-4.0-8k"},
            "dpc": {"api_key": "", "model": "deepseek-chat"},
        },
        "feishu": {"app_id": "", "app_secret": "", "webhook_port": 8080, "group_chat_id": ""},
        "obsidian": {"api_url": "http://localhost:27123", "api_key": "", "vault_path": "E:/MyCodeProjects"},
        "parallel": {"max_workers": 4, "debate_rounds": 2, "consensus_threshold": 0.7},
    }

    cfg_path.write_text(
        yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print(f"[OK] 配置文件已创建: {cfg_path}")
    print("    请编辑该文件，填入各平台API密钥")


def cmd_analyze():
    """执行一键分析"""
    from .orchestrator import AIOrchestrator
    from .obsidian_sync import ObsidianSync

    topic = input("  分析主题: ").strip()
    if not topic:
        print("[X] 主题不能为空")
        return

    context = input("  上下文(可选): ").strip()

    print(f"\n[*] 开始全流程分析: {topic}")
    orchestrator = AIOrchestrator()
    output = orchestrator.full_pipeline(topic, context)

    # 保存
    obsidian = ObsidianSync()
    result = obsidian.save_all(
        title=topic,
        md_content=output.get("final_report", ""),
        json_data=output,
        tags=["AI研讨", "多模型分析", "自动生成"],
    )

    print(f"\n[OK] 分析完成!")
    for fmt, path in result.items():
        print(f"  {fmt}: {path}")


def cmd_bot():
    """启动飞书Webhook Bot"""
    from ..feishu_bot.server import start_server, FeishuWebhookHandler
    from .orchestrator import AIOrchestrator
    from .obsidian_sync import ObsidianSync
    from ..feishu_bot.client import FeishuClient
    import yaml

    # 加载配置
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    fc = cfg.get("feishu", {})
    port = fc.get("webhook_port", 8080)
    group_id = fc.get("group_chat_id", "")

    orchestrator = AIOrchestrator()
    obsidian = ObsidianSync()
    feishu = FeishuClient()

    def on_message(text: str, sender: str, chat_id: str) -> str:
        """处理飞书消息"""
        text = text.strip()

        # 命令路由
        if text.startswith("/analyze") or text.startswith("/分析"):
            topic = text.replace("/analyze", "").replace("/分析", "").strip()
            if not topic:
                return "用法: /分析 <主题>"

            # 异步分析同步返回
            output = orchestrator.full_pipeline(topic)
            report = output.get("final_report", "分析无结果")

            # 保存到Obsidian
            obsidian.save_markdown(topic, report, ["AI研讨", "飞书请求"])

            # 推送到飞书群
            try:
                cid = group_id or chat_id
                feishu.send_text(cid, f"✅ 分析完成: {topic}\n\n{report[:2000]}")
            except Exception as e:
                pass

            return f"分析完成，报告已保存"

        elif text.startswith("/status") or text.startswith("/状态"):
            return "AI专家集群运行中 | 可用模型: " + ", ".join(cfg.get("models", {}).keys())

        elif text.startswith("/help") or text.startswith("/帮助"):
            return """可用命令:
/分析 <主题> — 全AI集群并行分析
/状态 — 查看系统状态
/模型 — 列出可用模型"""

        else:
            return "未知命令。输入 /帮助 查看可用命令"

    print(f"[*] 启动飞书Bot Webhook (端口 {port})")
    start_server(port=port, on_message=on_message)


def cmd_status():
    """系统状态检查"""
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.exists() else {}
    models = cfg.get("models", {})

    print("\n=== AI专家研讨集群 状态 ===\n")
    print(f"AI模型 ({len(models)}):")
    for key, mc in models.items():
        key_status = "✅" if mc.get("api_key") else "⛔"
        print(f"  {key_status} {key}: {mc.get('name', mc.get('model', '?'))}")

    fc = cfg.get("feishu", {})
    feishu_status = "✅" if fc.get("app_id") and fc.get("app_secret") else "⛔"
    print(f"\n飞书集成: {feishu_status}")
    print(f"  App ID: {'已配置' if fc.get('app_id') else '未配置'}")
    print(f"  Webhook端口: {fc.get('webhook_port', 8080)}")
    print(f"  群聊ID: {'已配置' if fc.get('group_chat_id') else '未配置'}")

    oc = cfg.get("obsidian", {})
    obsidian_status = "✅" if oc.get("api_key") else "⚠️ (文件直写可用)"
    print(f"\nObsidian同步: {obsidian_status}")
    print(f"  Vault路径: {oc.get('vault_path', 'E:/MyCodeProjects')}")

    print(f"\n并行配置:")
    pc = cfg.get("parallel", {})
    print(f"  最大并行: {pc.get('max_workers', 4)}")
    print(f"  辩论轮数: {pc.get('debate_rounds', 2)}")
    print(f"  共识阈值: {pc.get('consensus_threshold', 0.7)}")


def main():
    parser = argparse.ArgumentParser(description="AI专家研讨集群")
    parser.add_argument("action", nargs="?", default="status",
                        choices=["setup", "analyze", "bot", "status"])
    args = parser.parse_args()

    actions = {
        "setup": cmd_setup,
        "analyze": cmd_analyze,
        "bot": cmd_bot,
        "status": cmd_status,
    }
    actions[args.action]()


if __name__ == "__main__":
    import argparse
    main()
