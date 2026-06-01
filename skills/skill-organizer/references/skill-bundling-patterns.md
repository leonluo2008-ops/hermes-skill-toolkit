---
note: 多个 skill 形成工具包时的分发组织方式 + 本机安装模式
last_updated: 2026-06-02
source: 2026-06-01 用户二大爷关于 4-skill 工具包的真实对话
---

# Skill 工具包分发与本机安装模式

## 何时读这个文件

- 用户想把 2+ 个相关 skill 绑成"工具包"统一维护
- 决定 monorepo vs polyrepo 时
- 准备写 `install.sh` / `update.sh` 时
- 优化或迁移 skill 时，**SKILL.md 内文中的 URL 跟 `git remote -v` 不一致**时

## 4 种分发模式对比

| 模式 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **A. 单 monorepo** | 工具包内 2+ skill 强关联 | 一次 clone 拉全部，**更新同步** | 共享 commit history |
| **B. polyrepo（每 skill 一 repo）** | skill 各自独立演进 | 完全解耦 | **用户原话**："东一个西一个，不方便维护更新" |
| **C. polyrepo + 总 monorepo（subtree/submodule）** | 想两者兼得 | 双活 | 同步开销大，门槛高 |
| **D. polyrepo + install script** | skill 独立但有统一安装入口 | 各 skill 独立 + 一次安装 | 仓库数量多 |

**用户偏好（2026-06-01）**：**A（单 monorepo）**——"我 fork 了官方仓库和达尔文仓库，我想把这个工具包构建一个专门的新仓库来进行管理"。

## 推荐的 monorepo 目录结构

```
hermes-skill-toolkit/
├── README.md                     ← 总览 + 安装说明
├── LICENSE                       ← 跟官方 skill 同 license (Apache-2.0)
├── skills/
│   ├── skill-creator/            ← 来自官方 fork
│   ├── mcp-builder/              ← 来自官方仓库
│   ├── gardener-skill/           ← 用户已有
│   ├── darwin-skill/             ← 来自用户 fork
│   └── skill-organizer/          ← 用户已有
├── docs/
│   ├── skill-toolkit-coordination.md   ← 4 skill 协作规则
│   └── anthropic-skill-creator-comparison.md  ← 官方 vs 本地对比
└── scripts/
    ├── install.sh                ← 一次性安装脚本（核心）
    └── update.sh                 ← 更新脚本
```

**关键**：
- 每个 skill 子目录保持自己独立 SKILL.md（**skill 仍是可加载单位**）
- `scripts/install.sh` 是入口
- `docs/` 放跨 skill 文档
- LICENSE 跟官方 skill 一致

## install.sh 设计模式

**核心原则：symlink，不是 copy**

```bash
#!/bin/bash
set -e

TOOLKIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_BASE="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills/software-development}"

SKILLS=(skill-creator mcp-builder gardener-skill darwin-skill skill-organizer)

for skill in "${SKILLS[@]}"; do
  src="$TOOLKIT_ROOT/skills/$skill"
  dst="$TARGET_BASE/$skill"
  
  if [ -d "$dst" ] || [ -L "$dst" ]; then
    echo "✓ $skill already installed at $dst"
    continue
  fi
  
  ln -s "$src" "$dst"
  echo "✓ $skill → $dst (symlink)"
done
```

**为什么用 symlink**：
- 改 monorepo 文件，**立即**生效（无需重新 install）
- `git pull` = `update`，跟 `install` 是同一个动作
- 不占双倍磁盘
- 占位符思维：`HERMES_SKILLS_DIR` 留 env var 覆盖点

**注意事项**：
- 飞书套件（lark-*）是**直接目录**（如 `lark-calendar` 而非 `lark/lark-calendar`）—— 跟 npm 包不同
- 已存在的目标不覆盖（`if [ -d "$dst" ]` 检查）
- `set -e` 让任何错误立即中止

## polyrepo 时期的 metadata.hermes.related_skills 互引

在 monorepo 之前，每个 skill 是独立 repo，**仍然要互引**（用 `metadata.hermes.related_skills` 字段）：

```yaml
metadata:
  hermes:
    related_skills: [skill-creator, gardener-skill, darwin-skill]
    toolkit_role: organizer
    notes: 4-skill 工具包之一（全 skill 集合整理），与其他 3 个协作
```

**4 个 toolkit_role**：
- `skill-creator` = `creator`（编写/evals）
- `gardener-skill` = `mindset-optimizer`（思维类优化）
- `darwin-skill` = `flow-optimizer`（流程类优化）
- `skill-organizer` = `organizer`（整理/审计/归档）

## SKILL.md URL 必须与 git remote 一致（pitfall）

**踩坑实录（2026-06-01）**：`darwin-skill` 的 SKILL.md 写 `GitHub: https://github.com/alchaincyf/darwin-skill`（上游），但本机 `git remote -v` 实际是 `leonluo2008-ops/darwin-skill`（用户 fork）。**文字凭印象写会跟实际脱节**。

**修复原则**：
1. 优化或迁移任何 skill **前**，先跑 `git -C <skill-dir> remote -v` 确认真源
2. SKILL.md 头部写的 GitHub 链接 = `git remote -v` 的输出
3. 如果有 fork / upstream 区分，两者都写明（"fork of <upstream> at <fork>"）

**自查命令**：
```bash
for d in ~/.hermes/skills/*/; do
  skill=$(basename "$d")
  [ -d "$d/.git" ] || continue
  remote=$(git -C "$d" config --get remote.origin.url 2>/dev/null)
  doc_url=$(grep -m1 -oE 'https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+' "$d/SKILL.md" 2>/dev/null)
  if [ -n "$remote" ] && [ -n "$doc_url" ] && ! echo "$remote" | grep -q "$(echo $doc_url | sed 's|https://github.com/||' | sed 's|/|.|')"; then
    echo "⚠️  $skill: remote=$remote but doc=$doc_url"
  fi
done
```

## 用户偏好（2026-06-01 已确认）

- **不维护多个仓库管同类型**：1 个工具包只用一个 monorepo
- **命名约定（不严格）**：用户自创 skill 用 `-skill` 后缀（gardener-skill、darwin-skill），但 `skill-organizer` 用 `skill-` 前缀
- **不写新 SKILL.md 时不算真正"加新 skill"**——update monorepo = `git pull` 即可
- **废弃合并**：当一个目录被并入 monorepo，旧目录**物理删除**（不是保留为"参考"）

## 跟 superpowers 的关系

**superpowers 是流程**，**skill-organizer 是结构**：
- superpowers 决定"何时做整理 / 何时建 monorepo"（规划层）
- skill-organizer 决定"monorepo 长什么样、install 怎么写"（执行层）
- 两者**互补不重叠**

## 相关文件

- `~/.hermes/.docs/skill-toolkit-coordination.md` — 4 skill 协作规则（写于 2026-06-01）
- `~/.hermes/.docs/anthropic-skill-creator-comparison.md` — 官方 vs 本地对比
- `~/.hermes/.docs/skill-git-audit.md` — skill 的 git 审计方法
