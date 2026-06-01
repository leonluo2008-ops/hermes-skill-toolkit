# hermes-skill-toolkit

> **4 个 skill 协作的工具包** —— 一次安装，跟 git pull 一起更新。

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

## 这是什么

一个**单仓库**管理 4 个 skill 的工具包。每个 skill 保留自己的 SKILL.md（独立可加载单位），但通过 **monorepo + symlink install** 的方式统一管理。

**解决什么问题**：
- ❌ **之前**：4 个 skill 分散在 3 个独立仓库 + 1 个本地装（**push 一次得切 3 个 repo**）
- ✅ **现在**：1 个仓库管 4 skill，`git pull` 即更新

## 4 skill 分工

| Skill | 职责 | 类型 |
|-------|------|------|
| **skill-creator** | 编写/编辑/evals/触发词优化 | **主管道**（新 skill 走它）|
| **gardener-skill** | 优化**思维类** skill | 人类判断（启发质量）|
| **darwin-skill** | 优化**流程类** skill | 8 维评分 + 棘轮机制 |
| **skill-organizer** | 整理/审计/归档**全 skill 集合** | 5 步流程 + 双轨分类 |

完整协作规则：见 [`docs/skill-toolkit-coordination.md`](docs/skill-toolkit-coordination.md)

## 安装

### 1. 克隆本仓库
```bash
git clone https://github.com/leonluo2008-ops/hermes-skill-toolkit.git ~/hermes-skill-toolkit
cd ~/hermes-skill-toolkit
```

### 2. 跑安装脚本
```bash
bash scripts/install.sh
```

**它会做的事**：
- 在 `~/.hermes/skills/` 下创建 symlink：
  - `gardener-skill` → `~/hermes-skill-toolkit/skills/gardener-skill`
  - `darwin-skill` → `~/hermes-skill-toolkit/skills/darwin-skill`
  - `software-development/skill-creator` → `~/hermes-skill-toolkit/skills/skill-creator`
  - `software-development/skill-organizer` → `~/hermes-skill-toolkit/skills/skill-organizer`
- **symlink 而非 copy** —— 改 monorepo 立即生效

### 3. 验证
```bash
ls -la ~/.hermes/skills/software-development/ | grep -E 'skill-(creator|organizer)'
ls -la ~/.hermes/skills/ | grep -E '(gardener|darwin)-skill'
```

## 更新

```bash
bash scripts/update.sh
```

**它会做的事**：
- `git pull` 拉最新 monorepo
- 重跑 install.sh 验证 symlink（**幂等**）

## 目录结构

```
hermes-skill-toolkit/
├── README.md                 # 你正在读
├── LICENSE                   # Apache-2.0
├── .gitignore
├── CHANGELOG.md
├── skills/                   # 4 个 skill
│   ├── skill-creator/
│   ├── gardener-skill/
│   ├── darwin-skill/
│   └── skill-organizer/
├── docs/                     # 协作文档
│   ├── skill-toolkit-coordination.md
│   ├── anthropic-skill-creator-comparison.md
│   └── skill-git-audit.md
└── scripts/
    ├── install.sh            # 核心安装
    └── update.sh             # 更新
```

## 仓库治理

- **本仓库 = 唯一真源**（**single source of truth**）
- 历史来源（**已 archive**）：
  - `leonluo2008-ops/gardener-skill` ← history
  - `leonluo2008-ops/darwin-skill` ← history
  - `leonluo2008-ops/skill-organizer` ← history
  - `leonluo2008-ops/skills`（fork of `anthropics/skills`）← 仍保留作 skill-creator 升级源
- **skill-creator 升级**（**手动**）：
  ```bash
  cd /tmp && rm -rf skills && git clone --depth 1 https://github.com/leonluo2008-ops/skills.git
  cp -r /tmp/skills/skills/skill-creator/* ~/hermes-skill-toolkit/skills/skill-creator/
  cd ~/hermes-skill-toolkit && git add skills/skill-creator/ && git commit -m "bump: skill-creator from upstream"
  ```

## License

Apache License 2.0 —— 见 [LICENSE](LICENSE)
