# Skill 工具包协作规则（2026-06-01 实施，2026-06-02 调整）

> 4 个 skill 组成的工具包，分工明确 + 互相引用 + 实时触发。
>
> **2026-06-02 关键调整**：园丁定位从「**优化思维类 skill**」改为「**对话信号驱动的 skill 优化**」——不再限定 skill 类型。达尔文定位同步调整为「**evals 量化优化**」。

## 工具包成员

| Skill | 职责 | 输入 | 视角 | 安装位置 |
|-------|------|------|------|----------|
| **skill-creator** | 编写/编辑/evals/触发词优化 | 单 skill | 编写视角 | `~/.hermes/skills/software-development/skill-creator/` |
| **gardener-skill** | 优化 skill | **真实对话记录** | **对话信号视角** | `~/.hermes/skills/gardener-skill/` |
| **darwin-skill** | 优化 skill | **evals 量化测试** | 量化评分视角 | `~/.hermes/skills/darwin-skill/` |
| **skill-organizer** | 整理/审计/归档/分类 | 全 skill 集合 | 库管理视角 | `~/.hermes/skills/software-development/skill-organizer/` |

**核心差异**（2026-06-02 重新明确）：
- **达尔文 = 多 prompt 跑分对比**（适合能写 evals 的 skill）
- **园丁 = 单次对话深度分析**（适合不能量化的 skill——创作/对话/人在回路）
- **不是「思维类 vs 流程类」**——是「对话信号 vs evals 量化」

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
       → 用户已有 draft？→ 直接 skill-creator Phase 3+
       → 用户想"为什么要写"？→ 先 superpowers 脑暴 → 再 skill-creator
  → NO  → 继续
  ↓
【Q3】说的是"对话里发现的问题"吗？（"对话里这个 skill 不对"/"用户反馈"/"效果不好"）
  → YES → gardener-skill
  → NO  → 继续
  ↓
【Q4】说的是"evals 分数下降/自动优化"吗？（"分数掉"/"auto-optimize"/"流程不清晰"）
  → YES → darwin-skill
  → NO  → 默认进入 skill-creator（最常用）
```

> **superpowers 例外**：如果是「**通用任务**」（不是写 skill，比如写代码 / 写文章 / debug），superpowers 才是主管道。本文档只覆盖「**写 skill 场景**」下的 superpowers 融合。

## 触发词设计（避免冲突）

| Skill | 触发词（避免歧义） |
|-------|-------------------|
| **skill-creator** | 写、建、新建、create、author、edit、modify、create skill、写新 skill、create a skill、improve description |
| **gardener-skill** | 对话诊断、对话里发现问题、对话复盘、对话里 skill 出问题、对话信号、对话暴露问题 |
| **darwin-skill** | evals、跑分、打分、auto-optimize、auto optimize、棘轮、rubric、量化 |
| **skill-organizer** | 整理、审计、归档、太多、清单、分类、organize、audit、archive、universal tools |

**冲突边界处理**：
- "**improve**"：skill-creator 优先（"improve description / improve skill content"）
- "**优化**"：园丁（对话信号） + 达尔文（evals 量化）都触发——**通过 description 区分**

## 4 个 skill 的核心方法论

### skill-creator（官方）
- **三级加载**：Metadata（始终）+ SKILL.md body（触发时）+ Bundled resources（按需）
- **流程**：Capture Intent → Interview → Write → Test Prompts → Run（with-skill + baseline）→ Grade → Iterate
- **关键文件**：`evals/evals.json` + `eval_metadata.json` + `grading.json` + `timing.json`
- **触发器**：`description` 包含 100 词级的 "what + when to use"

### gardener-skill（2026-06-02 重新定位）
- **目标**：**从用户实际对话中提取问题 + 输出可执行的优化方案**
- **流程**：Phase 0 触发 → Phase 1 对话分析 → Phase 1.5 根本原因 → Phase 2 建议生成 → Phase 3 测试设计 → Phase 5 人在回路测试 → Phase 5.5 成品扫描 → Phase 6 人类判断
- **关键文件**：skill 画像库（每 skill 一份诊断+方案+验证）
- **被动原则**：用户不指令不主动扫描；Phase 5 测试期间例外
- **不限 skill 类型**：任何 skill 在对话里暴露问题都能介入

### darwin-skill
- **目标**：基于 evals 的"棘轮优化"——分数只升不降
- **流程**：Phase 0 初始化 → Phase 0.5 测试 prompt 设计 → Phase 1 基线评估 → Phase 2 改进 → Phase 3 评估 → Phase 4 keep/revert
- **关键文件**：`results.tsv`（每次优化结果）+ git 版本控制
- **8 维评分**：6 维结构（60分）+ 2 维效果（40分）

### skill-organizer
- **目标**：让 skill 清单保持精简、适配、有效
- **流程**：扫描 → 类型预分 → 诊断 → 分类确认 → 归档 → 报告
- **关键文件**：`data/user-universal-tools.yaml`（**不推远程**）
- **核心原则**："用不上的，就不要出现在对应 agent 的 skill 清单里"

---

## superpowers 融合（2026-06-02）

> **关键认知**：superpowers **不是工具包第 5 个 skill**——它是「**编写 skill 的方法论**」。
> 工具包管「**skill 写完之后**」（evals/优化/整理），superpowers 管「**skill 写之前 + 写之中**」（脑暴/计划/子agent/TDD）。
> 两者**正交**，流水线**串联**。

### 流水线串联（轻嵌方案，Q1=A）

```
[superpowers 阶段]                 [skill-creator 阶段]
─────────────────                  ────────────────────
Phase 1: Brainstorm        ─→      Capture Intent
Phase 2: Writing Plans     ─→      Write SKILL.md
                                    
                                    Phase 3: Test Prompts
                                    Phase 4: Run (with-skill + baseline)
                                    Phase 5: Grade
                                    Phase 6: Iterate
                                    
[superpowers Phase 4: Systematic Debugging] ←── 如果 evals 暴露问题
```

**关键决策**：
- **superpowers 负责**：脑暴 + 计划（Phase 1-2）—— 让"为什么写这个 skill"想清楚
- **skill-creator 负责**：写 + evals + 迭代（Phase 3-6）—— 这是它的强项
- **superpowers 不复制进 monorepo**——它仍是独立 skill，外部引用
- **不重叠部分**：TDD（skill 不是代码）/ Code Review（skill 没 review 这一关）—— **跳过**

### 触发词协调

| 触发 | 走谁 |
|------|------|
| "我想写个 skill"、"做一个新 skill" | 先 **superpowers 脑暴** → 再走 **skill-creator** |
| "我已经有 draft 了"、"改下这个 skill" | 直接 **skill-creator**（跳过 superpowers 脑暴） |
| "这个 skill evals 跑分不对"、"evals 分数掉了" | **darwin-skill**（不涉及 superpowers） |
| "对话里这个 skill 不对"、"用户反馈 skill 跑偏" | **gardener-skill**（不涉及 superpowers） |
| "skill 太多"、"整理下" | **skill-organizer**（不涉及 superpowers） |

**冲突边界**：
- "**build**"：superpowers 优先（"build a feature"语境）；skill-creator 只在"build a skill"语境触发
- "**plan**"：superpowers 优先（"writing plans"）；skill-creator 不直接接"plan"

### superpowers 跟 gardener 的分工（都做根因分析）

| 类型 | 走谁 |
|------|------|
| **代码/技术 bug**（"这个代码不工作"、"测试挂了"） | superpowers Phase 4（Systematic Debugging 4 阶段） |
| **skill 优化方向**（"对话里这个 skill 跑出来不对"） | gardener-skill（Phase 1.5 根本原因） |
| **skill eval 分数下降**（"evals 分数掉了"） | darwin-skill（8 维评分棘轮） |

**判断信号**：
- 听到「代码 / 测试 / git / commit」→ superpowers
- 听到「skill / SKILL.md / 触发词 / 对话暴露问题」→ gardener / darwin

### superpowers 不在 monorepo 里的原因

- **它本身已经成熟**——obra 维护，社区认可，重复维护无价值
- **不需要 monorepo 化的 git 流程**——它本身就有 release 流程
- **只引用不复制**——`docs/skill-toolkit-coordination.md` 写清楚怎么用，superpowers 自己仓库不动

**如果将来要把 superpowers 复制进 monorepo**，需要先回答「**维护痛点是什么**」——别为了"统一"而统一（园丁 vs authoring 教训）。

## 协作时序示例

**典型用户场景**：

1. **写新 skill**：
   ```
   user: "我想做一个 skill 来管视频剪辑"
   → skill-creator（写新 skill）
   → 写完跑 skill-creator 的自检 + evals
   → 不满意？→ 看问题来源：对话里暴露的→gardener / evals 分数下降→darwin
   ```

2. **整理 skill 库**：
   ```
   user: "skill 太多了，整理下"
   → skill-organizer（先扫描分类）
   → 留下来的 skill 质量不行？→ gardener（看对话） / darwin（跑 evals）
   → 想新增一个？→ skill-creator
   ```

3. **优化现有 skill（2026-06-02 调整后）**：
   ```
   user: "对话里这个 skill 跑出来不对"
   → gardener（对话信号诊断 + 方案）
   → 测试发现描述触发词不准？
   → skill-creator（专门优化 description）
   → 改完发现 evals 分数掉了？
   → darwin（evals 量化优化）
   ```

## 注意事项

1. **不重复**：每个 skill 的方法论独立，不复制
2. **不重叠**：触发词不混；冲突时用 description 区分
3. **不冗余**：4 个 skill 不重复内容——单 skill 视角 3 个 + 集合视角 1 个
4. **互相引用**：每个 skill 的 `related_skills` 都包含另外 3 个
5. **协作而非替代**：skill-creator 也"improve existing skills"，但**默认**走 gardener（对话） / darwin（evals）
6. **分工核心（2026-06-02）**：按**输入信号类型**分（对话 vs evals），不按 skill 类型分（思维 vs 流程）

## 历史

- 2026-06-02：superpowers 融合（Q1=A 轻嵌）—— superpowers 负责 Phase 1-2（脑暴+计划），skill-creator 接管 Phase 3+
- 2026-06-02：园丁定位调整——从「优化思维类 skill」→「对话信号驱动的 skill 优化」；达尔文同步从「优化流程类」→「evals 量化优化」
- 2026-06-01：建立工具包（首次明确分工）
- 之前：`hermes-agent-skill-authoring`（已废弃并删除）
- 之前：gardener-skill 包含 §A 写新 skill（已重构让位 skill-creator）
