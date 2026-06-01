#!/bin/bash
# update.sh — pull latest monorepo + re-verify symlinks
# 改 monorepo 文件不需要跑这个；只有新版本才需要

set -euo pipefail

TOOLKIT_ROOT="${TOOLKIT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

cd "$TOOLKIT_ROOT"

# 1. Pull latest
echo "=== git pull ==="
if git remote -v | grep -q origin; then
    git pull --ff-only 2>&1 || log_warn "Pull failed (maybe diverged). Resolve manually: cd $TOOLKIT_ROOT && git status"
else
    log_warn "No remote configured. Skip pull."
fi

# 2. Re-run installer (idempotent — only creates missing symlinks)
echo ""
echo "=== Re-verify symlinks ==="
bash "$TOOLKIT_ROOT/scripts/install.sh"

echo ""
log_ok "Update done."