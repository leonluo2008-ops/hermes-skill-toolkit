# 4-Skill 工具包定位 — 2026-06-01 决策记录

> **本文件是历史归档**。当前 gardener-skill 4-skill 工具包定位已迁移到主 SKILL.md：
> - 顶层路由表（"何时用什么"段，4-skill 入口）
> - §D 路由决策树（4-skill 详细决策路径）
> - 「园丁 → 达尔文 交接协议」节（新增，2026-06-03）
> - 「与达尔文的关系」段（已重写为联动工作流）
>
> 本文件**仅供查阅历史决策背景**——不要在新工作里引用此段。

---

## 决策背景（2026-06-01）

**触发事件**：发现 4 个 skill 在内容上有重叠区（gardener-skill、hermes-agent-skill-authoring、skill-creator、darwin-skill），需要明确分工。

**用户原话**："**用官方的 skill-creator 专门负责编写 skill，园丁和达尔文是优化 skill，你等我通知**"

## 4-skill 工具包定位

| Skill | 职责 | 输入 | 视角 |
|-------|------|------|------|
| `skill-creator`（Anthropic 官方） | 创建 + 编辑 + 加 evals + 优化 description | 单 skill | 编写视角 |
| `gardener-skill`（本 skill） | 优化 skill | 真实对话记录 | 对话信号视角 |
| `darwin-skill` | 优化 skill | evals 量化测试 | 量化评分视角 |
| `skill-organizer` | 整理/审计/归档全 skill 集合 | 全 skill 集合 | 库管理视角 |

**用户明确分工**（2026-06-01）："**用官方的 skill-creator 专门负责编写 skill，园丁和达尔文是优化 skill**"。

## §A 跟 skill-creator 的分工（2026-06-01 拍板）

**§A 重构后的内容**：
- A.1 三条铁律（**园丁独有**——占位符思维 / 示例≠模板素材 / 原理 > 格式）
- A.2 SKILL.md 落位（**园丁独有**——官方没明确说）
- A.3 主管道指引（直接指向 `skill-creator` 步骤表）

**A.4-A.5 已删除**（frontmatter 规范 / 目录结构 / 自检）——**官方 skill-creator 全部覆盖**。

**与 skill-creator 的关系**：
- `skill-creator` = **主管道**（写 SKILL.md + evals + 评分）
- `gardener-skill §A` = **园丁视角**（三条铁律 + 落位）——**不重复** skill-creator 的"如何写"
- `gardener-skill §B` = **优化主流程**（**核心**——对话信号诊断 + 方案）
- `darwin-skill` = **evals 量化优化**（**互补**）

**Pitfall 教训**：**新发现 4-skill 工具包后，园丁 §A 跟 skill-creator 不应撞车**——**前者管"园丁视角"，后者管"如何写"**。

## 维护模式（2026-06-01 拍板）

- **园丁** = 优化主流程（对话信号）
- **达尔文** = 优化副流程（evals 量化）
- **skill-creator** = 编写主管道
- **skill-organizer** = 整理/审计

## 2026-06-03 决策（**本文件归档触发**）

发现 gardener-skill 主 SKILL.md 中 L691-721 段（4-Skill 工具包定位）与顶层路由表 + §A 主管道指引 + §D 路由决策树**内容重叠**。

**用户决策**：删除主 SKILL.md L691-721 段，**归档到本文件**。
- 主 SKILL.md 改用顶层路由表 + §D 路由决策树 + 新增"园丁 → 达尔文 交接协议"作为 4-skill 工具包唯一入口
- 本文件仅作历史查阅
