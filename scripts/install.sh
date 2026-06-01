#!/bin/bash
# install.sh — 4-skill toolkit installer
# 通过 symlink 装到 ~/.hermes/skills/ 下对应分类
# 改 monorepo 文件 → 立即生效（symlink 透明）

set -euo pipefail

# ============================================================================
# 占位符：所有可能因环境/用户而变的值都在这里
# ============================================================================
TOOLKIT_ROOT="${TOOLKIT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
HERMES_SKILLS_DIR="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills}"

# 4 skill 必装（4-skill 工具包核心）
# 注意：gardener-skill 和 darwin-skill 在根，skill-creator/organizer 在 software-development/
SKILLS_ROOT=(
    "gardener-skill"
    "darwin-skill"
)

SKILLS_SOFTWARE=(
    "skill-creator"
    "skill-organizer"
)

# ============================================================================
# 颜色（无依赖）
# ============================================================================
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "${RED}✗${NC} $1"; }

# ============================================================================
# 安装函数
# ============================================================================
install_skill() {
    local skill="$1"
    local category="$2"
    local target_base="$HERMES_SKILLS_DIR/$category"
    local target="$target_base/$skill"
    local source="$TOOLKIT_ROOT/skills/$skill"

    # 1. 源存在性检查
    if [ ! -d "$source" ]; then
        log_err "Source missing: $source"
        return 1
    fi

    # 2. 目标目录创建
    mkdir -p "$target_base"

    # 3. 已存在处理
    if [ -L "$target" ]; then
        # 是 symlink（可能链到 cc-switch 旧位置）
        if [ "$(readlink -f "$target")" = "$(readlink -f "$source")" ]; then
            log_ok "$skill → already linked correctly"
            return 0
        fi
        # symlink 但指向别处（**如 cc-switch**）—— **重链**
        rm "$target"
        log_warn "$skill → old symlink removed, re-linking"
    elif [ -e "$target" ]; then
        # 是真目录（**用户可能有未提交修改**）—— **跳过**
        log_warn "$skill → already exists at $target (not a symlink). Skip."
        return 0
    fi

    # 4. 创建 symlink
    ln -s "$source" "$target"
    log_ok "$skill → $target (symlink)"
}

# ============================================================================
# 验证
# ============================================================================
verify() {
    echo ""
    echo "=== Verification ==="
    local all_ok=1

    for skill in "${SKILLS_ROOT[@]}"; do
        local target="$HERMES_SKILLS_DIR/$skill"
        if [ -L "$target" ] && [ -d "$target" ]; then
            local link_target=$(readlink "$target")
            log_ok "$skill → $link_target"
        else
            log_err "$skill → NOT LINKED"
            all_ok=0
        fi
    done

    for skill in "${SKILLS_SOFTWARE[@]}"; do
        local target="$HERMES_SKILLS_DIR/software-development/$skill"
        if [ -L "$target" ] && [ -d "$target" ]; then
            local link_target=$(readlink "$target")
            log_ok "$skill → $link_target"
        else
            log_err "$skill → NOT LINKED"
            all_ok=0
        fi
    done

    echo ""
    if [ $all_ok -eq 1 ]; then
        log_ok "All 4 skills installed and verified"
        echo ""
        echo "Quick test: ls -la $HERMES_SKILLS_DIR/software-development/ | grep -E 'skill-(creator|organizer)'"
        echo "            ls -la $HERMES_SKILLS_DIR/ | grep -E '(gardener|darwin)-skill'"
    else
        log_err "Some skills failed to install. Check above."
        return 1
    fi
}

# ============================================================================
# 主流程
# ============================================================================
echo "=== hermes-skill-toolkit installer ==="
echo "TOOLKIT_ROOT:  $TOOLKIT_ROOT"
echo "HERMES_SKILLS: $HERMES_SKILLS_DIR"
echo ""

# 检查 toolkit 源
if [ ! -d "$TOOLKIT_ROOT/skills" ]; then
    log_err "TOOLKIT_ROOT does not look like the monorepo (no skills/ dir): $TOOLKIT_ROOT"
    exit 1
fi

# 装 4 skill
for skill in "${SKILLS_ROOT[@]}"; do
    install_skill "$skill" ""
done

for skill in "${SKILLS_SOFTWARE[@]}"; do
    install_skill "$skill" "software-development"
done

# 验证
verify