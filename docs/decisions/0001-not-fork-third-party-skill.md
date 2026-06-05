# ADR 0001: 不 fork 第三方 skill (SkillOpt / OpenSquilla)

- **状态**: ✅ Accepted
- **日期**: 2026-06-05
- **来源**: 建议 5 (来自研究笔记 §5.6.5)
- **影响**: 4-skill 工具包 + 未来集成 / 长期

## 背景

调研发现两个**领域相邻**的第三方项目:
- **microsoft/SkillOpt** (PyPI v0.1.0) —— 把 SKILL.md 当神经网络权重做训练 (DL 范式)
- **opensquilla/opensquilla** (v0.3.1) —— 把多个 skill 串成工作流 (编排范式)

两个项目都**已经成熟**, 都有官方维护。问题: 4-skill 工具包要不要 fork 进去?

## 决策

**不 fork**。**只调用** (`pip install` / `import` / 触发词引用), 不复制源码进 monorepo。

## 后果

### 正向
- ✅ **monorepo 体量不爆炸** —— 第三方项目动辄上千行代码, fork 后 install.sh / git pull 慢
- ✅ **版本更新跟上游走** —— `pip install --upgrade skillopt` 即拿最新, 不需要自己 cherry-pick
- ✅ **不背维护债** —— 第三方 bug / 文档更新 / 架构变化, 由原作者负责
- ✅ **触发词引用代替代码复制** —— 描述 "什么时候用 SkillOpt" 在 frontmatter 一行写清

### 负向
- ⚠️ **依赖网络** —— 第一次安装要 `pip install`, 没网时失败
- ⚠️ **上游破坏性变更风险** —— 重大版本升级可能撞 API, 需要适配
- ⚠️ **不能魔改核心** —— 想要自定义功能, 得走 wrapper / fork (但目前 4-skill 工具包没这需求)

### 缓解
- 依赖风险: monorepo 内部用 SkillOpt 时加 try/except 失败回退 (见 0002)
- 破坏性变更: 锁版本 `skillopt>=0.1,<0.2`, 重大版本升级时单独评审
- 魔改需求: 真有需要时**才**评估 fork, 先提 ADR 评审

## 备选

### A. 完整 fork 进 monorepo (❌ 拒绝)
**理由**: 1) 维护债太大 2) 失去上游更新 3) 4-skill 工具包定位是「skill 工具包」, 不是「skill 训练平台」。

### B. 抽取子模块只 fork 核心 (❌ 拒绝)
**理由**: 1) 子模块拆分成本高 2) SkillOpt 训练循环是耦合的, 拆不开 3) 上游不维护拆分版。

### C. **C. 当前方案: 不 fork, 只调用** (✅ 接受)
**理由**: 1) SkillOpt 已是 PyPI 包, 集成成本低 2) 4-skill 工具包定位保持「工具包」 3) 风险可控, 失败有回退。

## 相关

- ADR 0002: SkillOpt opt-in 集成 (本决策的落地)
- 备注: 上游 `alchaincyf/darwin-skill` 也走同款策略 (不 fork SkillOpt, 只 import)
- 研究笔记: ~/.hermes/.research/metaskill-2026-06-05.md §5.6.5
