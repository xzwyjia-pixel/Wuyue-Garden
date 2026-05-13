#!/bin/bash
# 规则甄查 · 快速发布脚本
# 功能：stage → test → commit → push
# 用法：bash scripts/ship.sh [commit-message]
#       不传 message 则自动生成

set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo ""
echo "=== 规则甄查 · 发布流水线 ==="

# 1. 检查变更
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
    echo "[SAME] 无文件变更，跳过"
    exit 0
fi
echo "[INFO] 待提交变更:"
echo "$CHANGES" | head -20

# 2. 运行测试
echo ""
echo "[TEST] 运行 pytest..."
python -m pytest tests/ -q
echo "[PASS] 测试通过"

# 3. 暂存全部
git add -A
echo "[STAGE] 已暂存"

# 4. 生成 commit message
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    # 自动摘要：检测改动范围
    HAS_AUDIT=$(echo "$CHANGES" | grep -c "audit_core.py" || true)
    HAS_RULES=$(echo "$CHANGES" | grep -c "rules.json" || true)
    HAS_TESTS=$(echo "$CHANGES" | grep -c "tests/" || true)
    HAS_SENTINEL=$(echo "$CHANGES" | grep -c "platform_sentinel" || true)
    HAS_REFINE=$(echo "$CHANGES" | grep -c "ai_refine" || true)
    HAS_EVOLVER=$(echo "$CHANGES" | grep -c "rules_evolver" || true)
    HAS_OBSIDIAN=$(echo "$CHANGES" | grep -c "obsidian_sync\|notes/" || true)
    HAS_HOOKS=$(echo "$CHANGES" | grep -c ".githooks\|scripts/ship" || true)

    PARTS=()
    [ "$HAS_AUDIT" -gt 0 ] && PARTS+=("audit_core")
    [ "$HAS_RULES" -gt 0 ] && PARTS+=("rules")
    [ "$HAS_TESTS" -gt 0 ] && PARTS+=("tests")
    [ "$HAS_SENTINEL" -gt 0 ] && PARTS+=("platform_sentinel")
    [ "$HAS_REFINE" -gt 0 ] && PARTS+=("ai_refine")
    [ "$HAS_EVOLVER" -gt 0 ] && PARTS+=("rules_evolver")
    [ "$HAS_OBSIDIAN" -gt 0 ] && PARTS+=("obsidian_sync")
    [ "$HAS_HOOKS" -gt 0 ] && PARTS+=("hooks")

    SCOPE=$(IFS=/; echo "${PARTS[*]}")
    TS=$(date "+%Y-%m-%d %H:%M")
    COMMIT_MSG="chore: ${SCOPE} update — ${TS}"
fi

# 5. 提交
git commit -m "$COMMIT_MSG"
echo "[COMMIT] $COMMIT_MSG"

# 6. 推送
if git remote -v 2>/dev/null | grep -q "origin"; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "[PUSH] 推送到 origin/$BRANCH ..."
    git push origin "$BRANCH" 2>&1 || echo "[WARN] 推送失败（远程未配置/无权限）"
else
    echo "[WARN] 未配置 remote origin，跳过推送"
fi

echo ""
echo "=== 发布完成 ==="
