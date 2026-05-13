"""
setup_ai_cluster.py — AI专家研讨集群 一键安装与配置
1. 安装依赖
2. 初始化配置文件
3. 创建飞书开发所需结构
4. 验证安装
"""
import sys, os, subprocess, yaml
from pathlib import Path

BASE = Path(__file__).parent
REQUIREMENTS = [
    "httpx",
    "pyyaml",
    "requests",
]

STEPS = [
    ("安装Python依赖", "pip"),
    ("生成配置文件", "config"),
    ("创建飞书开发目录", "feishu_dirs"),
    ("验证安装", "verify"),
]


def install_deps():
    print("\n=== 安装Python依赖 ===")
    for pkg in REQUIREMENTS:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            print(f"  ✅ {pkg}")
        else:
            print(f"  ❌ {pkg}: {r.stderr[:100]}")


def gen_config():
    print("\n=== 生成配置文件 ===")
    cfg_path = BASE / "ai_bridge" / "config.yaml"
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        key_count = sum(1 for m in cfg.get("models", {}).values() if m.get("api_key"))
        print(f"  ✅ 配置文件已存在 (已配置 {key_count}/{len(cfg.get('models', {}))} 个API密钥)")
        return

    config = {
        "models": {
            "gpt": {"name": "GPT-4o", "provider": "OpenAI", "api_base": "https://api.openai.com/v1",
                     "api_key": "", "model": "gpt-4o", "max_tokens": 4096, "temperature": 0.7},
            "gemini": {"name": "Gemini 2.0 Flash", "provider": "Google",
                       "api_base": "https://generativelanguage.googleapis.com/v1beta",
                       "api_key": "", "model": "gemini-2.0-flash", "max_tokens": 8192, "temperature": 0.7},
            "claude": {"name": "Claude 3.5 Sonnet", "provider": "Anthropic",
                       "api_base": "https://api.anthropic.com/v1",
                       "api_key": "", "model": "claude-3-5-sonnet-20241022", "max_tokens": 8192, "temperature": 0.7},
            "doubao": {"name": "豆包 Pro", "provider": "火山引擎",
                       "api_base": "https://ark.cn-beijing.volces.com/api/v3",
                       "api_key": "", "model": "doubao-pro-32k", "max_tokens": 4096, "temperature": 0.7},
            "tongyi": {"name": "通义千问 Max", "provider": "阿里云",
                       "api_base": "https://dashscope.aliyuncs.com/api/v1",
                       "api_key": "", "model": "qwen-max", "max_tokens": 4096, "temperature": 0.7},
            "wenxin": {"name": "文心一言 4.0", "provider": "百度",
                       "api_base": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
                       "api_key": "", "secret_key": "", "model": "ernie-4.0-8k", "max_tokens": 4096, "temperature": 0.7},
            "dpc": {"name": "DPC (DeepSeek)", "provider": "DeepSeek",
                    "api_base": "https://api.deepseek.com/v1",
                    "api_key": "", "model": "deepseek-chat", "max_tokens": 4096, "temperature": 0.7},
        },
        "feishu": {"app_id": "", "app_secret": "", "webhook_port": 8080, "group_chat_id": ""},
        "obsidian": {"api_url": "http://localhost:27123", "api_key": "",
                     "vault_path": "E:/MyCodeProjects", "output_dir": "AI研讨报告"},
        "parallel": {"max_workers": 4, "debate_rounds": 2, "consensus_threshold": 0.7},
    }
    cfg_path.write_text(
        yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    print("  ✅ 配置文件已生成: ai_bridge/config.yaml")
    print("  ⚠️ 请编辑该文件填入各平台API密钥后使用")


def create_feishu_dirs():
    print("\n=== 创建飞书开发目录 ===")
    dirs = [
        "feishu_bot/webhook",
        "feishu_bot/cards",
        "feishu_bot/events",
        "feishu_bot/handlers",
    ]
    for d in dirs:
        p = BASE / d
        p.mkdir(parents=True, exist_ok=True)
        (p / "__init__.py").touch()
    print(f"  ✅ 飞书开发目录已创建")


def verify():
    print("\n=== 验证安装 ===")
    checks = []

    # Python可用
    checks.append(("Python", sys.version[:6]))

    # 核心模块导入
    for mod in ["json", "yaml", "http.server", "threading"]:
        try:
            __import__(mod.replace("/", "."))
            checks.append((f"模块 {mod}", "✅"))
        except:
            checks.append((f"模块 {mod}", "❌"))

    # 配置文件
    cfg_path = BASE / "ai_bridge" / "config.yaml"
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        models = cfg.get("models", {})
        keyed = sum(1 for m in models.values() if m.get("api_key"))
        checks.append(("配置文件", f"✅ ({keyed}/{len(models)} 密钥已配置)"))
    else:
        checks.append(("配置文件", "❌ 未生成"))

    # 目录结构
    dirs_ok = all((BASE / d).exists() for d in ["ai_bridge", "feishu_bot"])
    checks.append(("模块目录", "✅" if dirs_ok else "❌"))

    # 输出
    for name, status in checks:
        print(f"  {status} {name}")

    all_ok = all("❌" not in s for _, s in checks)
    print(f"\n  总体: {'✅ 安装完成' if all_ok else '❌ 部分失败，请检查上述标记'}")


def main():
    print("=" * 50)
    print("  AI专家研讨集群 - 一键安装")
    print("=" * 50)

    for name, action in STEPS:
        if action == "pip":
            install_deps()
        elif action == "config":
            gen_config()
        elif action == "feishu_dirs":
            create_feishu_dirs()
        elif action == "verify":
            verify()

    print("\n" + "=" * 50)
    print("  安装完成!")
    print("=" * 50)
    print("""
下一步:
1. 编辑 ai_bridge/config.yaml 填入各平台API密钥
2. 飞书开放平台创建应用: https://open.feishu.cn
3. 配置飞书机器人Webhook地址
4. 启动: python feishu_bot/server_main.py bot
5. 执行分析: python -m ai_bridge.runner analyze
""")


if __name__ == "__main__":
    main()
