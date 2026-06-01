# Changelog

All notable changes to this monorepo will be documented here.

## [0.1.0] - 2026-06-01

### Initial Release

4-skill toolkit monorepo，合并自 3 个独立仓库：

- **skill-creator** (v0.1.0): 从 `leonluo2008-ops/skills` fork 导入
- **gardener-skill** (v3.10.0): 4-skill 协作 + §A 重构让位 skill-creator
- **darwin-skill** (未版本化): 4-skill 工具包 metadata + 流程类优化核心
- **skill-organizer** (v1.0.8): 4-skill 工具包 metadata + 通用工具安装优先级

### Features

- **install.sh**: symlink 模式安装，幂等
- **update.sh**: git pull + 重装
- **docs/**: 4 skill 协作规则 + Anthropic 官方对比 + git audit
- **LICENSE**: Apache-2.0

### Architecture Decisions

- **Polyrepo → Monorepo**: 合并 3 个独立仓库为 1 个（避免分散管理）
- **Symlink 而非 copy**: 改 monorepo 文件 → 立即生效
- **保留 leonluo2008-ops/skills fork**: skill-creator 升级仍从这里拉
- **废弃 hermes-agent-skill-authoring/**: 内容已并入 skill-creator

### Migration Notes

从 3 仓库迁移到本 monorepo：

```bash
# 1. 备份（如果还在用旧仓库路径）
# ~/.hermes/skills/gardener-skill/  →  旧
# ~/.hermes/skills/darwin-skill/    →  旧
# ~/.hermes/skills/software-development/skill-creator/     →  旧
# ~/.hermes/skills/software-development/skill-organizer/  →  旧

# 2. 跑本 monorepo 的 install.sh
# 旧目录会保留（install 跳过已存在），可以手动删
# 或用: rm -rf ~/.hermes/skills/{gardener-skill,darwin-skill,software-development/skill-creator,software-development/skill-organizer}

# 3. 跑 install.sh
bash scripts/install.sh
```
