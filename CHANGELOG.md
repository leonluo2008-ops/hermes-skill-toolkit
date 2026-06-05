# Changelog

All notable changes to this monorepo will be documented here.

## [0.2.0] - 2026-06-05

### SkillOpt 集成 + 园丁元层 + 防作弊铁律

基于 `microsoft/SkillOpt` 调研 (`v0.1.0` PyPI), 给 4-skill 工具包加 3 件事 (建议 1+2+4):

### Features

- **darwin-skill 接入 SkillOpt 引擎 (opt-in)**:
  - `metadata.hermes.engines: [llm-rubric, skillopt]` —— 默认仍是 8 维 LLM rubric
  - 新增 §E "SkillOpt 引擎" 章节: 触发条件 / 6 benchmark 速查 / 最小调用样例 / 失败回退
  - 新增 `references/prompts/skillopt-bridge.md` —— darwin → SkillOpt 桥接 prompt
  - 关键约束: `slow_update_gate_with_selection: true` (保守, 跟 paper/ckpt 一致)
  - **双轨制铁律**: best_skill.md 必须同时满足 (1) SkillOpt validation 提升 (2) 8 维评分不下降, 任一不满足 → 拒绝

- **gardener-skill 补 Slow Update 机制**:
  - 新增 `gardener_memory.md` —— 跨次诊断策略记忆 (模板态)
  - 借鉴 SkillOpt `meta_skill.md` 形式: 简短 / 结构化 / 滚动 10 条
  - SKILL.md 新增 §F "跨次诊断策略记忆" —— 写入规则 / 读取规则 / 跟其他 skill 的关系
  - 沉淀标准: 通用规律 vs 具体案例 (反"绑定具体内容"铁律)
  - 隐私红线: 不写用户原话, 只写"对话中暴露的**模式**"

- **防评分作弊铁律 (来自 gbrain-evals Result 2)**:
  - 协调文档 `skill-toolkit-coordination.md` 注意事项 §7
  - darwin-skill + gardener-skill SKILL.md 末尾都加 ⚠️ Pitfall 条目
  - 铁律 3 条: held-out 测试集 / 独立 judge / 双轨制

### Architecture Decisions

- **不 fork SkillOpt**: 4-skill 工具包定位不变, 只 `pip install skillopt` 调用
- **不复制训练循环**: SkillOpt 是 Python 库 / DL 范式, hermes 是 SKILL.md / LLM 范式, **集成 ≠ fork**
- **gardener_memory.md 不进 SKILL.md**: 元层配置文件, 跟 skill 文档解耦
- **跨 profile 隔离**: huiben / default profile 各自维护自己的 gardener_memory.md

### Pitfalls Added

- darwin-skill §末尾: 评分作弊 (硬指标必须配 held-out + 独立 judge)
- gardener-skill §末尾: 同上 (园丁主路径已合规, 未来硬指标扩展需双轨)
- darwin-skill §E.5: SkillOpt 失败自动降级 8 维 rubric

### Migration Notes

从 v0.1.0 升级:

```bash
# 1. 拉新分支 / 切到本 PR 合并后的 dev
cd ~/.hermes/monorepo/hermes-skill-toolkit
git pull

# 2. 重装 (新加的文件需要 symlink)
bash scripts/install.sh

# 3. 验证 (新增文件)
ls -la ~/.hermes/skills/darwin-skill/references/prompts/skillopt-bridge.md
ls -la ~/.hermes/skills/gardener-skill/gardener_memory.md

# 4. 跑 skill-creator evals (3 改的 skill 各跑 1 次, 确认默认路径无回归)
```

### Not Done (下个 PR)

- **建议 3 dogfood 演示**: 拿 gardener-skill 真跑 SkillOpt 训一遍, 出 best_skill.md 对比
- 决策记录「不 fork 第三方 skill」: 进协调文档

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
