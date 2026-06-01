# Skill 工具包协作规则（2026-06-01 实施）

> 4 个 skill 组成的工具包，分工明确 + 互相引用 + 实时触发。

## 工具包成员

| Skill | 职责 | 视角 | 安装位置 |
|-------|------|------|----------|
| **skill-creator** | 编写/编辑/evals/触发词优化 | 单 skill | `~/.hermes/skills/software-development/skill-creator/` |
| **gardener-skill** | 优化思维类 skill | 单 skill + 思维诊断 | `~/.hermes/skills/gardener-skill/` |
| **darwin-skill** | 优化流程类 skill（棘轮 + 8维评分） | 单 skill + 流程评分 | `~/.hermes/skills/darwin-skill/` |
| **skill-organizer** | 整理/审计/归档/分类 | 全 skill 集合 | `~/.hermes/skills/software-development/skill-organizer/` |

## 互相引用

每个 skill 的 frontmatter `metadata.hermes.related_skills` 字段包含另外 3 个：

```yaml
metadata:
  hermes:
    related_skills: [skill-creator, gardener-skill, darwin-skill, skill-organizer]
```

## 路由决策树

用户消息进来后，**按以下顺序判断**：

```
用户消息
  ↓
【Q1】说的是"全局 skill 集合"吗？（"skill 太多"/"整理"/"哪些该删"）
  → YES → skill-organizer
  → NO  → 继续
  ↓
【Q2】说的是"新建/编辑/改内容/写新 skill"吗？
  → YES → skill-creator
  → NO  → 继续
  ↓
【Q3】说的是"思维启发质量好不好"吗？（"启发不准"/"思维乱"）
  → YES → gardener-skill
  → NO  → 继续
  ↓
【Q4】说的是"流程步骤清不清晰"吗？（"步骤乱"/"流程不清晰"/"自动优化"）
  → YES → darwin-skill
  → NO  → 默认进入 skill-creator（最常用）
```

## 触发词设计（避免冲突）

| Skill | 触发词（避免歧义） |
|-------|-------------------|
| **skill-creator** | 写、建、新建、create、author、edit、modify、create skill、写新 skill、create a skill、improve description |
| **gardener-skill** | 思维、启发、好不好、思维乱、启发不准、inspire、heuristic |
| **darwin-skill** | 流程、步骤、清晰、auto-optimize、auto optimize、棘轮、打分、rubric |
| **skill-organizer** | 整理、审计、归档、太多、清单、分类、organize、audit、archive、universal tools |

**冲突边界处理**：
- "**improve**"：skill-creator 优先（"improve description / improve skill content"），gardener 只在"思维启发"语境触发
- "**优化**"：gardener 思维类 + darwin 流程类都触发——**通过 description 区分**

## 4 个 skill 的核心方法论

### skill-creator（官方）
- **三级加载**：Metadata（始终）+ SKILL.md body（触发时）+ Bundled resources（按需）
- **流程**：Capture Intent → Interview → Write → Test Prompts → Run（with-skill + baseline）→ Grade → Iterate
- **关键文件**：`evals/evals.json` + `eval_metadata.json` + `grading.json` + `timing.json`
- **触发器**：`description` 包含 100 词级的 "what + when to use"

### gardener-skill
- **目标**：思维方式型 skill 的"培育"——不追求分数棘轮，追求启发质量
- **流程**：Phase 0 触发 → Phase 1 诊断 → Phase 2 建议 → Phase 3 测试设计 → Phase 5 监控 → Phase 5.5 成品扫描 → Phase 6 人类判断
- **关键文件**：skill 画像库（每 skill 一份诊断+方案+验证）
- **被动原则**：用户不指令不主动扫描；Phase 5 测试期间例外

### darwin-skill
- **目标**：操作流程型 skill 的"棘轮优化"——分数只升不降
- **流程**：Phase 0 初始化 → Phase 0.5 测试 prompt 设计 → Phase 1 基线评估 → Phase 2 改进 → Phase 3 评估 → Phase 4 keep/revert
- **关键文件**：`results.tsv`（每次优化结果）+ git 版本控制
- **8 维评分**：6 维结构（60分）+ 2 维效果（40分）

### skill-organizer
- **目标**：让 skill 清单保持精简、适配、有效
- **流程**：扫描 → 类型预分 → 诊断 → 分类确认 → 归档 → 报告
- **关键文件**：`data/user-universal-tools.yaml`（**不推远程**）
- **核心原则**："用不上的，就不要出现在对应 agent 的 skill 清单里"

## 协作时序示例

**典型用户场景**：

1. **写新 skill**：
   ```
   user: "我想做一个 skill 来管视频剪辑"
   → skill-creator（写新 skill）
   → 写完跑 skill-creator 的自检 + evals
   → 不满意？ → gardener（优化思维）或 darwin（优化流程）
   ```

2. **整理 skill 库**：
   ```
   user: "skill 太多了，整理下"
   → skill-organizer（先扫描分类）
   → 留下来的 skill 质量不行？ → gardener / darwin
   → 想新增一个？ → skill-creator
   ```

3. **优化现有 skill**：
   ```
   user: "这个 skill 思维不准"
   → gardener（思维类优化）
   → 测试发现描述触发词不准？
   → skill-creator（专门优化 description）
   → 改完发现流程乱了？
   → darwin（流程类优化）
   ```

## 注意事项

1. **不重复**：每个 skill 的方法论独立，不复制
2. **不重叠**：触发词不混；冲突时用 description 区分
3. **不冗余**：4 个 skill 不重复内容——单 skill 视角 3 个 + 集合视角 1 个
4. **互相引用**：每个 skill 的 `related_skills` 都包含另外 3 个
5. **协作而非替代**：skill-creator 也"improve existing skills"，但**默认**走 gardener/darwin（更专业）

## 历史

- 2026-06-01：建立工具包（首次明确分工）
- 之前：`hermes-agent-skill-authoring`（已废弃并删除）
- 之前：gardener-skill 包含 §A 写新 skill（已重构让位 skill-creator）
