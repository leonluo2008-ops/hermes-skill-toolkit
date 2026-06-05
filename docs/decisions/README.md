# Architecture Decision Records (ADRs)

> **位置**: `docs/decisions/`
> **目的**: 记录 4-skill 工具包的**重大架构决策**——为什么这么做, 不那么做
> **格式**: MADR (Markdown ADR) 风格, 每条 ≤ 100 行
> **约束**: 决策**不轻易**改; 改时写新 ADR 覆盖旧 ADR (保留旧 ADR 不删)

## 索引

| 编号 | 标题 | 状态 | 日期 | 影响 |
|------|------|------|------|------|
| [0001](./0001-not-fork-third-party-skill.md) | 不 fork 第三方 skill (SkillOpt / OpenSquilla) | ✅ Accepted | 2026-06-05 | 集成策略, 长期 |
| [0002](./0002-skillopt-integration-mode.md) | SkillOpt 集成 = opt-in + 双轨制 + 失败降级 | ✅ Accepted | 2026-06-05 | darwin 引擎, 中期 |
| [0003](./0003-gardener-memory-as-meta-layer.md) | gardener_memory.md = 园丁元层 (借鉴 SkillOpt meta_skill) | ✅ Accepted | 2026-06-05 | 园丁架构, 长期 |
| [0004](./0004-anti-cheat-double-track.md) | 防评分作弊 = held-out + 独立 judge + 双轨制 | ✅ Accepted | 2026-06-05 | 4-skill 全员, 长期 |

## 状态说明

- **Proposed** —— 提议中, 待评审
- **✅ Accepted** —— 已接受, 当前生效
- **⚠️ Deprecated** —— 已废弃, 有新 ADR 覆盖 (新 ADR 链接在文件内)
- **❌ Rejected** —— 被否决 (保留作历史)

## 添加新 ADR 的流程

1. 编号 `NNNN-<kebab-case-title>.md`
2. 状态写 `Proposed`
3. 填四节: 背景 / 决策 / 后果 / 备选
4. 改本文件加索引
5. PR 评审通过后 → 改状态 `Accepted`
6. **不删** 旧 ADR; 改决策时写新 ADR 覆盖

## 相关文档

- `skill-toolkit-coordination.md` —— 4-skill 协作规则
- `../.hermes/plans/2026-06-05-skillopt-gardener-toolkit.md` —— 实施 plan
- `~/.hermes/.research/metaskill-2026-06-05.md` —— 研究笔记 (本批 ADR 源头)
