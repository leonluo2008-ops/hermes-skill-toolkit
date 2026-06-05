# ADR 0003: gardener_memory.md = 园丁元层 (借鉴 SkillOpt meta_skill)

- **状态**: ✅ Accepted
- **日期**: 2026-06-05
- **来源**: 建议 2 (来自研究笔记 §5.6.2)
- **影响**: gardener-skill / 跨次诊断 / 长期

## 背景

gardener-skill 当前是**单次深度分析**——Phase 1-6 一次性出方案。

问题: 优化 skill X 总结的教训, **不会**自动迁移到 skill Y 的诊断。每次从零开始。

调研发现 SkillOpt 有 `meta_skill.md`——**跨 epoch 滚动的简短结构化战略笔记**。园丁的痛点跟 SkillOpt meta_skill 的设计场景**高度相似**:

| SkillOpt | gardener-skill |
|----------|---------------|
| 训练 N 个 epoch | 诊断 N 个 skill |
| 跨 epoch 战略记忆 | 跨次诊断策略记忆 |
| `meta_skill.md` | `gardener_memory.md` |
| 短 / 结构 / 滚动 | 短 / 结构 / 滚动 |

## 决策

**新增 `gardener_memory.md`** 作为园丁元层配置文件, 借鉴 SkillOpt `meta_skill.md` 的设计:

1. **轻量, 不进 SKILL.md** —— 元层配置, 跟 skill 文档解耦
2. **滚动 10 条上限** —— 超过自动淘汰最早的
3. **沉淀通用规律** —— 移到别的 skill 也成立, 不绑具体内容
4. **Phase 5.5 写, Phase 1 读头部 5 条** —— 闭环

## 关键设计

```markdown
## 写入规则 (硬约束)
- 时机: Phase 5.5 完成后 + Phase 6 人类判断通过
- 量: 1-3 条/次, 每条 1 行, 动词开头
- 内容: 通用规律 (反绑定具体内容铁律)
- 容量: 10 条上限, 滚动淘汰

## 读取规则
- 时机: Phase 1 对话分析开始前
- 量: 头部 5 条
- 用法: 叠加进分析上下文

## 格式 (严格)
## YYYY-MM-DD | <skill name 或 "通用">
- 教训 1: <1 行, 动词开头, 可执行>
- 适用场景: <一类 skill 关键词>
```

## 后果

### 正向
- ✅ **跨次诊断经验复用** —— 优化 A 的教训带到 B
- ✅ **补园丁唯一缺的元层** —— 4-skill 工具包对齐
- ✅ **借鉴成熟设计** —— SkillOpt meta_skill 已被验证
- ✅ **轻量可丢弃** —— 写错了可重置, 不影响主流程

### 负向
- ⚠️ **内容质量依赖 Phase 5.5** —— 扫描质量决定 memory 质量
- ⚠️ **可能沉淀偏见** —— 早期错误教训可能被反复应用
- ⚠️ **隐私红线** —— 不写用户原话, 只写"模式" (沿用园丁 §1 隐私原则)

### 缓解
- 质量: 写入规则严格 (1-3 条 + 通用规律), 沉淀标准**反绑定具体内容**
- 偏见: 10 条上限滚动淘汰, 6 个月内的条目需二次确认
- 隐私: 写入格式模板 + gardener_memory.md 头部明确隐私红线

## 备选

### A. 把元层写进 SKILL.md (❌ 拒绝)
**理由**: 1) 混淆"skill 文档"和"元层配置" 2) 跨 profile 不隔离 3) SKILL.md 应该稳定, 元层应该易变。

### B. 用 memory 工具 / 外部数据库 (❌ 拒绝)
**理由**: 1) 跨 profile 复杂 2) 引入新依赖 3) 本地 markdown 文件已够用。

### C. **当前方案: 独立 gardener_memory.md, 借鉴 SkillOpt** (✅ 接受)
**理由**: 1) 跟 SkillOpt 设计对齐 2) 文件级管理, 简单 3) 跨 profile 隔离天然支持。

## 相关

- SkillOpt meta_skill 设计: https://github.com/microsoft/SkillOpt (skillopt/meta_skill 模块)
- 4-skill 元层对齐表: gardener-skill SKILL.md §F.5
- 隐私红线: gardener-skill 总体原则 (沿用)
