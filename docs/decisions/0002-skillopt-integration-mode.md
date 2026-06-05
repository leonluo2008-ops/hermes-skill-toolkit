# ADR 0002: SkillOpt 集成 = opt-in + 双轨制 + 失败降级

- **状态**: ✅ Accepted
- **日期**: 2026-06-05
- **来源**: 建议 1 (来自研究笔记 §5.6.1)
- **影响**: darwin-skill / 评估流程 / 中期

## 背景

darwin-skill 当前用 8 维 LLM rubric 做 skill 评分——**主观 / 低样本 / 一致性差**。

microsoft/SkillOpt 提供 6 个内置 benchmark (SearchQA / ALFWorld / DocVQA / LiveMathematicianBench / SpreadsheetBench / OfficeQA) + 客观分数 + 训练循环——是 darwin 的**强补充**。

但 SkillOpt 跑一次训练通常**几小时 + 几十刀**成本, 不能默认开。

## 决策

darwin-skill 集成 SkillOpt **采用三层防护**:

1. **opt-in 默认关闭** —— `engines: [llm-rubric, skillopt]` 中 llm-rubric 仍是主路径
2. **双轨制** —— SkillOpt best_skill.md 必须**同时**满足 SkillOpt validation 提升 + 8 维 LLM 评分不下降
3. **失败降级** —— SkillOpt 启动失败 / 网络问题 / benchmark 数据缺失 → 自动降级 8 维 LLM rubric, 记 status=fallback

## 关键配置

```yaml
metadata:
  hermes:
    engines: [llm-rubric, skillopt]   # 主路径 = llm-rubric
    engine_skillopt:
      mode: opt-in                      # opt-in | opt-out | off
      benchmark: searchqa               # 6 选 1
      epochs: 4
      batch_size: 40
      cost_warning: high                # 提示用户
      slow_update_gate_with_selection: true  # 保守, 跟 paper/ckpt 一致
```

## 后果

### 正向
- ✅ **darwin 评分更可信** —— 高 stakes 场景 (v1.0 发版前) 可上 SkillOpt
- ✅ **不破坏现有工作流** —— 默认 llm-rubric, 99% 场景不变
- ✅ **故障安全** —— SkillOpt 任何失败不阻塞 darwin
- ✅ **跟上上游** —— alchaincyf/darwin-skill 2026-06-03 已整合 SkillOpt, 我们同款策略

### 负向
- ⚠️ **配置复杂度增加** —— 用户要懂 SkillOpt benchmark 选择
- ⚠️ **成本不可控** —— 误触发 SkillOpt 可能花冤枉钱
- ⚠️ **慢更新差异** —— main 默认 force-accept, ckpt 用 gated 模式, 文档要标注清楚

### 缓解
- 复杂度: §E 章节给 6 benchmark 速查表 + 触发条件清单
- 成本: `cost_warning: high` + §E.1 触发条件白名单
- 慢更新: 默认 `slow_update_gate_with_selection: true` (保守)

## 备选

### A. 完整默认开 SkillOpt (❌ 拒绝)
**理由**: 1) 成本不可控 2) 99% 场景不需要 3) 现有 8 维评分够用。

### B. 完全不集成 SkillOpt (❌ 拒绝)
**理由**: 1) 失去客观分数背书 2) 上游已整合, 我们不跟显得落后 3) 高 stakes 场景没工具。

### C. **当前方案: opt-in + 双轨制 + 失败降级** (✅ 接受)
**理由**: 1) 风险最低 2) 用户主动选择 3) 失败不影响主流程。

## 相关

- ADR 0001: 不 fork 第三方 skill (本 ADR 依赖)
- ADR 0004: 防评分作弊双轨制 (本 ADR §E.4 引用)
- darwin-skill SKILL.md §E "SkillOpt 引擎 (可选, opt-in)"
- darwin-skill/references/prompts/skillopt-bridge.md
