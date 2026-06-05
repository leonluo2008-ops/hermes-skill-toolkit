---
name: darwin-skill
description: "Darwin Skill (达尔文.skill): autonomous skill optimizer inspired by Karpathy's autoresearch. Evaluates SKILL.md files using an 8-dimension rubric (structure + effectiveness), runs hill-climbing with git version control, validates improvements through test prompts, and generates visual result cards. Use when user mentions \"优化skill\", \"skill评分\", \"自动优化\", \"auto optimize\", \"skill质量检查\", \"达尔文\", \"darwin\", \"帮我改改skill\", \"skill怎么样\", \"提升skill质量\", \"skill review\", \"skill打分\", \"园丁移交\", \"接收交接包\", \"验证园丁方案\", \"gardener 移交\"."
license: Apache-2.0
metadata:
  hermes:
    tags: [skills, optimization, darwin, hill-climbing, autoresearch, rubric, skillopt]
    related_skills: [skill-creator, gardener-skill, skill-organizer]
    toolkit_role: flow-optimizer
    engines: [llm-rubric, skillopt]
    engine_skillopt:
      mode: opt-in                    # opt-in | opt-out | off
      benchmark: searchqa              # searchqa | alfworld | docvqa | livemathematicianbench | spreadsheetbench | officeqa
      epochs: 4
      batch_size: 40
      cost_warning: high              # SkillOpt 跑训练动辄几小时/几十刀
      slow_update_gate_with_selection: true   # 跟 paper/ckpt 一致（保守）
    notes: 4-skill 工具包之一（流程类优化——棘轮 + 8维评分），与 skill-creator（编写）/gardener（思维优化）/organizer（整理）协作。可选 SkillOpt 引擎做客观 benchmark 验证（opt-in，不默认开）
---

# Darwin Skill

> 借鉴 Karpathy autoresearch 的自主实验循环，对 skills 进行持续优化。
> 核心理念：**评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚 → 生成成果卡片**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 设计哲学

autoresearch 的精髓：
1. **单一可编辑资产** — 每次只改一个 SKILL.md
2. **双重评估** — 结构评分（静态分析）+ 效果验证（跑测试看输出）
3. **棘轮机制** — 只保留改进，自动回滚退步
4. **独立评分** — 评分用子agent，避免「自己改自己评」的偏差
5. **人在回路** — 每个skill优化完后暂停，用户确认再继续

与纯结构审查的区别：不只看 SKILL.md 写得规不规范，更看改完后**实际跑出来的效果是否更好**。

---

## 评估 Rubric（8维度，总分100）

### 结构维度（60分）— 静态分析

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 1 | **Frontmatter质量** | 8 | name规范、description包含做什么+何时用+触发词、≤1024字符 |
| 2 | **工作流清晰度** | 15 | 步骤明确可执行、有序号、每步有明确输入/输出 |
| 3 | **边界条件覆盖** | 10 | 处理异常情况、有fallback路径、错误恢复 |
| 4 | **检查点设计** | 7 | 关键决策前有用户确认、防止自主失控 |
| 5 | **指令具体性** | 15 | 不模糊、有具体参数/格式/示例、可直接执行 |
| 6 | **资源整合度** | 5 | references/scripts/assets引用正确、路径可达 |

### 效果维度（40分）— 需要实测

| # | 维度 | 权重 | 评分标准 |
|---|------|------|---------|
| 7 | **整体架构** | 15 | 结构层次清晰、不冗余不遗漏、与花叔生态一致 |
| 8 | **实测表现** | 25 | 用测试prompt跑一遍，输出质量是否符合skill宣称的能力 |

### 评分规则
- 维度1-7：每个维度打 1-10 分，乘以权重得到该维度得分
- 维度8（实测表现）：跑2-3个测试prompt，按输出质量打1-10分
- **总分 = Σ(维度分 × 权重) / 10**，满分100
- 改进后总分必须 **严格高于** 改进前才保留

### 关于「实测表现」维度

这是与纯结构评分最大的区别。评分方式：

1. 为每个skill设计2-3个**典型用户prompt**（不是边缘case，是最常见的使用场景）
2. 用子agent执行：一个带skill跑，一个不带skill跑（baseline）
3. 对比输出质量，从以下角度打分：
   - 输出是否完成了用户意图？
   - 相比不带skill的baseline，质量提升明显吗？
   - 有没有skill引入的负面影响（过度冗余、跑偏、格式奇怪）？

如果无法跑子agent（时间/资源限制），可以退化为「干跑验证」：读完skill后模拟一个典型prompt的执行思路，判断流程是否合理。但要在results.tsv中标注 `dry_run`。

---

## 自主优化循环

### Phase 0: 初始化

```
1. 确认优化范围：
   - 全部skills → 扫描 .claude/skills/*/SKILL.md
   - 指定skills → 用户指定列表
2. 创建 git 分支：auto-optimize/YYYYMMDD-HHMM
3. 初始化 results.tsv（如不存在）
4. 读取现有 results.tsv 了解历史优化记录
```

### Phase 0.3: 接收园丁交接包（**2026-06-03 新增**）

> **触发条件**：本次任务**来自园丁**（gardener-skill Phase 9.5 移交）—— 不是用户直接发起的"优化 X skill"。

**接收清单**（来自园丁的"达尔文交接包"）：

1. **test-prompts.json** — 3-5 个测试 prompt + `expected_should_trigger` / `expected_reason`
2. **改动摘要**（≤200 字）— 改了什么 + 为什么改 + 预期提升哪个维度
3. **验证目标** — 基线分数 / 目标分数 / 重点关注维度
4. **耗时预估** — 预估分钟数 / 是否需要 subagent 嵌套 / `eval_mode` / 降级条件
5. **路径前置检查清单** — 园丁已自检 5 项（skill 目录存在 / SKILL.md 可写 / 格式合规 / rubric 适用 / results.tsv 存在）

**接收流程**：

```
收到园丁交接包
    ↓
【校验 1】test-prompts.json 格式合规？
  ├── ✅ 通过 → 写入 skill 目录的 test-prompts.json
  └── ❌ 失败 → **回退通知园丁**（"test-prompts 格式不合规"）→ 园丁补 → 重新接收
    ↓
【校验 2】路径前置检查清单 5 项都通过？
  ├── ✅ 全部通过 → 进入 Phase 0.5（沿用交接包的 test-prompts）
  └── ⚠️ 1+ 项未通过 → 评估：
      ├── 可自动修复（如 results.tsv 缺失 → 先跑基线补上）→ 修复后继续
      └── 不可自动修复（如 skill 目录不存在）→ **回退通知园丁** → 园丁重做路径检查
    ↓
【校验 3】耗时预估在可接受范围？
  ├── ✅ < 10 分钟 → eval_mode=full_test
  └── ⚠️ > 10 分钟 → eval_mode=dry_run 兜底（避免阻塞园丁流程）
    ↓
进入 Phase 0.5（test-prompts 已就位，跳过设计）
```

**关键原则**：
- 接收不等于接受——**每个校验步骤都可以回退给园丁**
- **不要再让园丁做一遍 test-prompts 设计**——达尔文从园丁那里继承
- **如果交接包某项缺失** → 不要猜，**回退给园丁补**（不替园丁做决定）

### Phase 0.5: 测试Prompt设计

在评估之前，为每个skill设计测试prompt。这步很关键——没有测试prompt，「实测表现」维度就打不了分。

```
for each skill:
  1. 读取 SKILL.md，理解它做什么
  2. 设计2-3个测试prompt，覆盖：
     - 最典型的使用场景（happy path）
     - 一个稍复杂或有歧义的场景
  3. 保存到 skill目录/test-prompts.json：
     [
       {"id": 1, "prompt": "用户会说的话", "expected": "期望输出的简短描述"},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

展示所有测试prompt给用户，**确认后再进入评估**。测试prompt的质量决定了优化方向是否正确。

### Phase 1: 基线评估（Baseline）

```
for each skill in 优化范围:

  # 结构评分（主agent可以做）
  1. 读取 SKILL.md 全文
  2. 按维度1-7逐项打分（附简短理由）

  # 效果评分（用子agent做，独立于主agent）
  3. 对每个测试prompt，spawn子agent：
     - with_skill: 带着SKILL.md执行测试prompt
     - baseline: 不带skill执行同一prompt
  4. 对比两组输出，打维度8的分

  # 汇总
  5. 计算加权总分
  6. 记录到 results.tsv
```

**如果子agent不可用**（超时、环境限制），维度8用干跑验证打分，标注 `dry_run`。不要因为跑不了测试就跳过这个维度——哪怕是模拟推演也比完全不看效果好。

基线评估完成后，展示评分卡：

```
┌──────────────────────────┬───────┬──────────────┬──────────────┐
│ Skill                    │ Score │ 结构短板      │ 效果短板      │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ huashu-proofreading      │ 78    │ 边界条件      │ 测试prompt2  │
│ huashu-slides            │ 72    │ 指令具体性    │ baseline持平  │
├──────────────────────────┼───────┼──────────────┼──────────────┤
│ 平均                     │ 75    │              │              │
└──────────────────────────┴───────┴──────────────┴──────────────┘
```

**暂停等用户确认，再进入优化循环。**

### Phase 2: 优化循环

用户确认后，按基线分数从低到高排序，先优化最弱的。

```
for each skill:
  round = 0
  while round < MAX_ROUNDS (默认3):
    round += 1

    # Step 1: 诊断
    找出得分最低的维度（结构或效果都算）

    # Step 2: 提出改进方案
    针对最低维度，生成1个具体改进方案：
      - 改什么（具体段落/行）
      - 为什么改（对应rubric哪条）
      - 预期提升多少分

    # Step 3: 执行改进
    编辑 SKILL.md
    git add + commit（message: "optimize {skill}: {改进摘要}"）

    # Step 4: 重新评估
    - 结构维度：主agent重新打分
    - 效果维度：spawn独立子agent重跑测试prompt（关键！不能自己评自己）

    # Step 5: 决策
    if 新总分 > 旧总分:
      status = "keep"，更新旧总分
    else:
      status = "revert"
      git revert HEAD（创建新commit回滚，不用reset --hard）
      记录失败尝试到 results.tsv
      break  # 该skill到瓶颈，跳到下一个

    # Step 6: 日志
    results.tsv 追加行

  # === 每个skill优化完后的人类检查点 ===
  展示该skill的改动摘要：
    - git diff（改前 vs 改后）
    - 分数变化（哪些维度提升/下降）
    - 测试prompt输出对比（如果跑过的话）
  等用户确认 OK 再继续下一个skill。
  如果用户说"不好"，回滚到该skill的优化前版本。
```

### Phase 2.5: 探索性重写（可选）

当 hill-climbing 连续2个skill都在 round 1 就 break（涨不动）时，提议一次「探索性重写」：

```
1. 选一个瓶颈skill
2. git stash 保存当前最优版本
3. 从头重写SKILL.md（不是微调，是重新组织结构和表达方式）
4. 重新评估
5. if 重写版 > stash版: 采用重写版
   else: git stash pop 恢复
```

这解决了 hill-climbing 的局部最优问题——有时候需要「先拆后建」才能突破瓶颈。
**必须征得用户同意后才执行。**

### Phase 3: 汇总报告

```
## 优化报告

### 总览
- 优化skills数：N
- 总实验次数：M
- 保留改进：X（Y%）
- 回滚次数：Z
- 实测验证：A次完整测试 / B次干跑

### 分数变化
┌──────────────────────────┬────────┬────────┬────────┐
│ Skill                    │ Before │ After  │ Δ      │
├──────────────────────────┼────────┼────────┼────────┤
│ huashu-proofreading      │ 78     │ 87     │ +9     │
│ huashu-slides            │ 72     │ 83     │ +11    │
├──────────────────────────┼────────┼────────┼────────┤
│ 平均                     │ 75     │ 85     │ +10    │
└──────────────────────────┴────────┴────────┴────────┘

### 主要改进
1. [skill-A] 补充了边界条件处理，测试输出质量提升明显
2. [skill-B] 重组了workflow结构，baseline对比优势增大
```

### Phase 3.5: 回退通知园丁（**2026-06-03 新增**）

> **触发条件**：本次任务**来自园丁**（Phase 0.3 接收过交接包）**且** 验证结果不理想。

**触发场景**：

| 场景 | 园丁需要什么 | 通知格式 |
|------|------------|---------|
| **棘轮 revert**（改后分数 ≤ 改前） | 重新分析诊断 | "X skill 改动 revert，原分数 Y，新分数 Z，建议回到 Phase 1 重新分析" |
| **路径前置检查发现不可修复** | 重新做路径检查 | "路径校验失败：[具体项]，需重新确认 [具体问题]" |
| **test-prompts 触发不到改动点** | 补 test-prompts | "test-prompts 触发不到 [具体改动点]，需补 [N] 个 prompt" |
| **耗时超时降级 dry_run** | 园丁接受 dry_run 结果 | "达尔文跑了 X 分钟超时，降级 dry_run，结果 [具体说明]" |
| **8 维 rubric 不适用**（创作类/元组件） | 跳过达尔文 | "本 skill 类型不适合 evals 量化，达尔文跳过，回到 Phase 6 人类判断" |

**通知格式**（写到 results.tsv + 飞书发用户）：

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode	source
2026-06-03T15:00	<commit>	<skill>	<old>	<new>	revert	<dim>	回退通知园丁：<具体原因>	full_test	gardener-handover
```

**关键字段**：
- `source = gardener-handover` — 标识这是园丁移交任务
- `note` 列写明回退的具体原因（园丁能据此回到 Phase 1 重新分析）

**不通知的情况**（达尔文自己发起的优化，不是园丁移交）：
- `source` 留空 —— `source = ""` 表示非园丁移交
- revert 写普通格式，不带"回退通知园丁"前缀

---

## results.tsv 格式

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	huashu-proofreading	-	78	baseline	-	初始评估	full_test
2026-03-31T10:05	a1b2c3d	huashu-proofreading	78	84	keep	边界条件	补充fallback	full_test
2026-03-31T10:10	b2c3d4e	huashu-proofreading	84	82	revert	指令具体性	过度细化	dry_run
2026-06-03T15:30	7fd7f80	hermes-multi-agent	88.3	88.3	validate	全维度	full_test 验证 dry_run 评分方法（delta=0.0）	full_test
```

**status 状态枚举**（4 个值）：

| status | 含义 | 何时用 |
|--------|------|--------|
| `baseline` | 初始评估 | 第一次跑某 skill 的 8 维打分时 |
| `keep` | 改动后分数 > 旧分数，保留 | 棘轮决策保留改动 |
| `revert` | 改动后分数 ≤ 旧分数，回退 | 棘轮决策回退改动 |
| `validate` | full_test 跑完分数无变化 | **用 full_test 校准 dry_run / 验证方法有效性**（不是改进也不是回退）|

**validate 与 keep 的关键区别**：
- `keep` 有"保留了某次具体改动"的语义（commit 引用了具体改动 commit）
- `validate` 无改动语义——只是"用 full_test 跑了一遍，没出 bug，方法对"
- validate 行**不计入棘轮决策**——只是评分方法学的元数据

**validate 适用场景**：
- 元组件类 skill（hermes-multi-agent 等）无法 subagent 独立评分，**用 full_test 校准 dry_run 准不准**
- 新 test-prompts 跑一遍 baseline，确认分母合理
- 定期 sanity check（防止评分方法本身腐化）

新增 `eval_mode` 列：`full_test`（跑了子agent测试）或 `dry_run`（模拟推演）。
文件位置：`.claude/skills/darwin-skill/results.tsv`

---

## 优化策略库

按优先级排序，每轮只做最高优先级的一个：

### P0: 效果问题（实测发现的）
- 测试输出偏离用户意图 → 检查skill是否有误导性指令
- 带skill比不带还差 → skill可能过度约束，考虑精简
- 输出格式不符合预期 → 补充明确的输出模板

### P1: 结构性问题
- Frontmatter缺少触发词 → 补充中英文触发词
- 缺少Phase/Step结构 → 重组为线性流程
- 缺少用户确认检查点 → 在关键决策处插入

### P2: 具体性问题
- 步骤模糊（"处理图片"）→ 改为具体操作和参数
- 缺少输入/输出规格 → 补充格式、路径、示例
- 缺少异常处理 → 补充 "如果X失败，则Y"

### P3: 可读性问题
- 段落过长 → 拆分+用表格
- 重复描述 → 合并去重
- 缺少速查 → 添加TL;DR或决策树

---

## 异常与边界条件

流程假设环境理想，但实操常遇异常。以下预定义 fallback，保证优化过程不会「一跑就卡住」。

| 场景 | 触发条件 | 处理动作 |
|---|---|---|
| 不在 git 仓库 | `git rev-parse` 失败 | 提示用户「建议 git init」；若拒绝，用 `cp SKILL.md SKILL.md.bak.YYYYMMDD-HHMM` 文件备份代替 revert |
| results.tsv 缺失 | 文件不存在 | 新建并写表头行（9列：含 eval_mode） |
| results.tsv 损坏 | 列数不匹配 / 非TSV | 备份为 `.bak.YYYYMMDD-HHMM` 后重建，告知用户 |
| 分支已存在 | `git checkout -b` 失败 | 分支名末尾加 `-2` / `-3`；第3次失败则切回现有分支并询问继续还是新起 |
| `git revert` 失败 | 冲突 / 工作树脏 | 先 `git stash`，重试；仍失败则从上一个 commit 的 SKILL.md 读出覆盖当前文件手动恢复 |
| MAX_ROUNDS 触顶（默认3） | 已跑3轮仍有短板 | 不强制 break，展示当前最弱维度问用户「继续加1轮 / 进入Phase 2.5 / 收工」 |
| 优化后超 150% 体积 | 新文件 > 原 × 1.5 | 拒绝提交，回到改进步骤精简（删冗余/合并重复），再评 |
| test-prompts.json 已存在 | 文件已在 skill 目录 | 默认复用并展示，问用户「复用 / 重写 / 追加」三选一 |
| SKILL.md 找不到 | 目录存在但无 SKILL.md | 该 skill 终止，results.tsv 记 `status=error`，继续下一个 |
| 分数计算规则 | 浮点精度漂移 | 总分保留 1 位小数，改进需严格 > 旧分（不靠四舍五入） |

**原则**：异常先告知用户，再按规则处理；绝不静默跳过或静默失败。

---

## 约束规则

1. **不改变skill的核心功能和用途** — 只优化"怎么写"和"怎么执行"，不改"做什么"
2. **不引入新依赖** — 不添加skill原本没有的scripts或references文件
3. **每轮只改一个维度** — 避免多个变更导致无法归因
4. **保持文件大小合理** — 优化后SKILL.md不应超过原始大小的150%
5. **尊重花叔风格** — 中文为主、简洁为上
6. **可回滚** — 所有改动在git分支上，用git revert而非reset --hard
7. **评分独立性** — 效果维度必须用子agent或至少干跑验证，不能在同一上下文里「改完直接评」

---

## 使用方式

### 全量优化（推荐首次使用）
```
用户："优化所有skills"
→ Phase 0-3 完整流程
→ 建议：先基线评估，选择分数最低的5-10个重点优化
```

### 单个优化
```
用户："优化 huashu-slides 这个skill"
→ 只对指定skill执行 Phase 0.5-2
```

### 仅评估不改
```
用户："评估所有skills的质量"
→ 只执行 Phase 0.5-1（设计测试prompt + 基线评估），不进入优化循环
```

### 查看历史
```
用户："看看skill优化历史"
→ 读取并展示 results.tsv
```

---

## 设计灵感

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> — Karpathy, autoresearch

本skill的对应关系：
- **program.md** → 本文件（评估rubric和约束规则）
- **train.py** → 每个SKILL.md
- **val_bpb** → 8维加权总分（含实测表现）
- **git ratchet** → 只保留有改进的commit
- **test set** → 每个skill的test-prompts.json

区别：增加了人在回路（autoresearch是全自主的，skill优化需要人的判断力），以及双重评估机制（结构+效果），因为skill的「好坏」比loss数值更微妙。

---

## 成果卡片生成（Result Card）

每个skill优化完成后（或全量汇总后），自动生成视觉成果卡片，截图保存为PNG。

### 卡片模板

模板位置：`templates/result-card.html`

3种风格，每次随机选择一种：

| 风格 | CSS类 | URL hash | 视觉特点 |
|------|--------|----------|---------|
| Warm Swiss | `.theme-swiss` | `#swiss` | 暖白底+赤陶橙，Inter字体，干净网格 |
| Dark Terminal | `.theme-terminal` | `#terminal` | 近黑底+荧光绿，等宽字体，扫描线 |
| Newspaper | `.theme-newspaper` | `#newspaper` | 暖白纸+深红，衬线字体，双栏编辑风 |

### 生成流程

```
1. 复制 templates/result-card.html 到临时工作文件
2. 用 sed/编辑工具 替换占位数据：
   - data-field="skill-name" → 实际skill名
   - data-field="score-before/after/delta" → 实际分数
   - 8个维度的 dim-bar-before/after width → 实际百分比
   - data-field="improvement-1/2/3" → 实际改进摘要
   - data-field="date" → 当前日期
3. 随机选择风格：hash 设为 swiss/terminal/newspaper 之一
4. 用 scripts/screenshot.mjs 截图（2x 高清，只截 .card 元素，自动 open 图片）：
   node scripts/screenshot.mjs /abs/path/to/card.html /abs/path/to/output.png
   # 回退方案（脚本失败时）：
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
5. 提示用户查看成果卡片 PNG

### 资源文件速查

| 路径 | 用途 |
|---|---|
| `templates/result-card.html` | 3风格主模板（swiss/terminal/newspaper，hash切换） |
| `templates/result-card-dark.html` / `-white.html` | 单一风格替代模板（需要锁定风格时用） |
| `scripts/screenshot.mjs` | 2x 高清截图，只截 .card，自动 open |
| `results.tsv` | 历次优化日志（9列含 eval_mode） |
| `{skill目录}/test-prompts.json` | 每个 skill 的测试 prompt 集（用于维度8实测） |
```

### 何时生成

- **单skill卡片**：每个skill优化完成后，展示该skill的分数变化
- **总览卡片**：全部优化完成后（Phase 3），展示全局战绩

### 品牌元素

- 顶部：Darwin.skill 品牌标识 + 日期
- 底部：「Train your Skills like you train your models」+ github.com/alchaincyf/darwin-skill

---

## §E SkillOpt 引擎 (可选, opt-in)

> **核心原则**: 8 维 LLM rubric 评分是 darwin 的**默认**和**主路径**。SkillOpt 是**可选增强**——用于「需要客观分数做背书」的场景 (如重要 skill 正式发版前、双盲评审、给老板/客户演示)。
>
> **绝不默认开**。SkillOpt 跑一次训练通常几小时 + 几十刀成本。

### E.1 触发条件

**满足以下任一条件才考虑启用 SkillOpt**:

1. **重要 skill 发版前** —— 比如 v0.x → v1.0 的关键 skill
2. **8 维评分卡在边缘** —— 总分 70-85 区间,LLM 评分"还行但说不出哪里差"
3. **多 skill 对比** —— 需要客观分数横评 2+ 个候选版本
4. **高 stakes 场景** —— 用户主动要求"用 benchmark 验证" / "出 best_skill.md"

**不满足** → 走 8 维 LLM rubric 路径,不要为了用而用。

### E.2 6 个内置 Benchmark 速查

| Benchmark | 类型 | 典型用时 | 适合验证什么 |
|-----------|------|---------|------------|
| `searchqa` | QA | 中 | 信息抽取 / 检索式问答 skill |
| `alfworld` | 具身 agent | 长 | 多步规划 / 工具调用 skill |
| `docvqa` | 文档 QA | 中 | 文档理解 / OCR 校对 skill |
| `livemathematicianbench` | 数学 | 中 | 推理 / 计算 skill |
| `spreadsheetbench` | 代码生成 | 中 | 数据处理 / 表格生成 skill |
| `officeqa` | 工具增强 QA | 中 | 工具编排 / API 调用 skill |

**没有合适的 benchmark** → 跳过 SkillOpt,8 维评分够用。

### E.3 最小调用样例

```bash
# 1. 安装 (一次性)
pip install skillopt

# 2. 准备数据 split
#   data/<your-skill>_split/{train,val,test}/items.json
#   格式见: https://github.com/microsoft/SkillOpt#data-preparation

# 3. 训练
python -m skillopt train \
  --config configs/searchqa/default.yaml \
  --split_dir /path/to/your/split \
  --optimizer_backend anthropic \
  --target_backend anthropic \
  --optimizer_model claude-sonnet-4-6 \
  --target_model claude-sonnet-4-6 \
  --out_root outputs/darwin-skillopt-$(date +%Y%m%d)

# 4. 拿 best_skill.md
ls outputs/darwin-skillopt-*/best_skill.md
```

### E.4 与 8 维评分的双轨制

**铁律**: 任何 SkillOpt 产出的 `best_skill.md` **必须**同时满足:

```
✅ SkillOpt validation 分数 > 原始 SKILL.md
✅ darwin 8 维 LLM 评分 不下降 (允许 ±1 浮动)
```

**任一不满足 → 拒绝 best_skill.md,继续用原版**。

这条双轨制 = 协调文档 `skill-toolkit-coordination.md` §注意事项第 6 条「防评分作弊铁律」的具体落地。

### E.5 失败回退

```
SkillOpt 启动失败 / 网络问题 / benchmark 无合适数据
  ↓
自动降级到 8 维 LLM rubric 路径
  ↓
在 results.tsv 记 status=fallback,reason=<具体错误>
```

**绝不**让 SkillOpt 故障阻塞 darwin 主流程。

### E.6 与上游 darwin-skill 关系

- 上游 `alchaincyf/darwin-skill` 2026-06-03 已整合 SkillOpt —— 我们的整合思路跟上游一致
- **不 fork** 上游; 本仓库保留自家 4-skill 工具包定位,只**调用** `pip install skillopt` 包
- 上游有更新 → 跟 monorepo update 流程走 (git pull + diff)

---

## ⚠️ Pitfall — 评分作弊 (2026-06-05 新增, 来自 gbrain-evals Result 2)

darwin 8 维 LLM rubric 评分 = **独立 judge** (合规)。

但**任何**用硬指标 (description 长度 / 章节数 / 关键词命中) 的扩展,**必须**配 held-out 测试集 + 真实质量 judge。

**反例** (gbrain-evals 验证): 只检查 section header 存在的 scorer, 把空 header 算通过, 分数 1.00 但实际质量 0.28。

**正面做法**:
- darwin 主路径 8 维评分 = 独立 judge ✅
- SkillOpt 集成 (本 §E) = 客观分数 = 硬指标 ✅
- 二者**双轨** = 当前 4-skill 工具包已合规 ✅

**来源**: gbrain-evals 2026-06-03-skillopt.md Result 2
