#!/bin/bash
# 规则甄查 · Hook 安装脚本
# 启用项目级自定义 hooks 路径

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$ROOT_DIR/.githooks"

git config core.hooksPath "$HOOKS_DIR"
echo "[OK] hooksPath → $HOOKS_DIR"
echo "     pre-commit: pytest 校验"
echo ""
echo "用法: bash scripts/ship.sh [提交信息]"
