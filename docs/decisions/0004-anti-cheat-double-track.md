# ADR 0004: 防评分作弊 = held-out + 独立 judge + 双轨制

- **状态**: ✅ Accepted
- **日期**: 2026-06-05
- **来源**: 建议 4 (来自研究笔记 §5.6.4)
- **影响**: 4-skill 全员 / 长期

## 背景

`gbrain-evals/2026-06-03-skillopt.md` Result 2 揭示**评分作弊风险**:

> 实验人员给 SkillOpt 一个可作弊 scorer: 只检查 section header 存在。
> SkillOpt 训出"空 header 套壳" skill——游戏化分数 1.00, 但**真实质量** 0.28。
> 独立 LLM judge 抓到了这个 cheat。

教训: **可作弊 scorer + 无独立 judge = 评分游戏化**。任何会**自动改 SKILL.md** 的工具都可能踩这个坑。

4-skill 工具包涉及"自动改 SKILL.md" 的工具有:
- darwin-skill (8 维评分 → 棘轮 keep/revert)
- gardener-skill (对话信号 → 优化建议)
- 集成 SkillOpt 后 (best_skill.md → 直接覆盖)

## 决策

**防评分作弊铁律 = 三条必须同时满足**:

1. **持有 held-out 测试集** —— 训练数据**永远看不到**的测试集
2. **配独立 judge** —— 评分器**不能跟主评分器同源** (不同 LLM / 不同 prompt / 不同维度)
3. **硬指标 + 主观评分的"双轨制"** —— **任一下降**都拒绝该建议

## 现状对照 (4-skill 工具包合规性)

| 工具 | 评分来源 | held-out? | 独立 judge? | 双轨? | 合规? |
|------|---------|-----------|-------------|-------|-------|
| **darwin-skill 8 维 rubric** | LLM 子 agent | ❌ (无 held-out) | ✅ (独立 LLM) | ⚠️ (单轨) | ⚠️ 部分 |
| **darwin + SkillOpt** (opt-in) | SkillOpt benchmark | ✅ (split_dir) | ✅ (8 维 vs 客观分数) | ✅ | ✅ |
| **gardener-skill 对话信号** | LLM 主观 | ❌ (无 held-out) | ✅ (LLM ≠ 对话源) | ⚠️ (单轨) | ⚠️ 部分 |
| **gardener 未来硬指标** (若加) | 规则 | 必须有 | 必须有 | ✅ | 强制 |

**当前 darwin 8 维 + gardener 对话 = 部分合规** (单轨, 但已有独立 judge)
**darwin + SkillOpt 双轨 = 完全合规** (4-skill 工具包**最高**防护)

## 后果

### 正向
- ✅ **风险前置识别** —— 评分游戏化在工具设计阶段就被挡住
- ✅ **统一标准** —— 4-skill 全员用同一套铁律, 不会各做各的
- ✅ **可验证** —— 任何扩展都对照本 ADR 自评合规性
- ✅ **gbrain-evals 证据支持** —— 决策有实验背书, 不是凭空

### 负向
- ⚠️ **darwin/gardener 当前未配 held-out** —— 需要未来单独 PR 加 (不阻塞本 PR)
- ⚠️ **双轨制增加成本** —— 评估一次 skill 要跑两个 judge
- ⚠️ **边界判断** —— 什么时候算"独立"? 不同 LLM 算独立, 同一 LLM 不同 prompt 算不算? 需要规则

### 缓解
- held-out 缺失: 本 ADR 立标准, 未来给 darwin/gardener 单独加 (下个 PR)
- 成本: opt-in, 关键 skill 发版前才上双轨
- 边界判断: 写明判定规则——

  ```
  "独立 judge" 定义 (硬规则):
  ① 不同 LLM (例: 优化用 claude-sonnet, judge 用 gpt-5.5)  → 独立
  ② 同 LLM 不同 prompt 模板 (例: 优化 prompt vs evaluation prompt) → 独立
  ③ 同 LLM 同 prompt (回声验证)                              → 不独立
  ```

## 备选

### A. 不加铁律, 各 skill 自管 (❌ 拒绝)
**理由**: 1) 4-skill 工具包一致性破裂 2) 风险敞口各 skill 重复踩 3) 没有总规则等于没规则。

### B. 强约束: 任何扩展必须配 held-out (❌ 拒绝)
**理由**: 1) 当前 4-skill 工具包也没配 held-out, 强约束等于阻塞整个仓库 2) 未来分阶段补更现实。

### C. **当前方案: 铁律写进协调文档 + 现状对照** (✅ 接受)
**理由**: 1) 风险立标准 2) 现状如实标 3) 未来改进留接口 4) 不阻塞本 PR。

## 相关

- gbrain-evals 2026-06-03 Result 2 (作弊证据): `~/.hermes/favorites-index/external/`
- 协调文档: `docs/skill-toolkit-coordination.md` §7 注意事项
- darwin-skill SKILL.md §E.4 双轨制 + §末尾 ⚠️ Pitfall
- gardener-skill SKILL.md §末尾 ⚠️ Pitfall
- ADR 0002: SkillOpt 集成 = opt-in + 双轨制 (本 ADR §E.4 引用)
