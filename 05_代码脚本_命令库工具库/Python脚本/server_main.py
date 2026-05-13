"""
feishu_bot/server_main.py — 飞书机器人独立启动入口
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_bridge.runner import cmd_bot, cmd_status

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="飞书机器人服务器")
    parser.add_argument("action", nargs="?", default="bot", choices=["bot", "status"])
    args = parser.parse_args()
    if args.action == "bot":
        cmd_bot()
    else:
        cmd_status()
