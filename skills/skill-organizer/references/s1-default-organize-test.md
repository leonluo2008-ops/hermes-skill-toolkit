# s1-default-organize 测试场景验证

**日期：** 2026-05-29
**测试目标：** skill-organizer v1.0.6 物理删除规则是否生效
**测试场景：** s1-default-organize（主Agent全局池跨Agent skill整理）
**结果：** ❌ 失败 — 物理删除规则未生效

---

## 背景规则（v1.0.6）

skill-organizer v1.0.6 核心变更：
> 废除「调度型/专职型Agent」分类跃迁，跨Agent skill直接物理删除全局池副本，不存在「排除后保留文件」的中间状态。

跨Agent skill列表（huiben专属，主Agent池子里的全局池副本应被物理删除）：

| Skill | 所属Agent | 处理方式 |
|-------|-----------|---------|
| picturebook-creator | huiben | 全局池副本 → 物理删除 |
| picturebook-video | huiben | 全局池副本 → 物理删除 |
| douyin-ops | huiben | 全局池副本 → 物理删除 |
| ai-drama | huiben | 全局池副本 → 物理删除 |
| ai-drama-storyboard | huiben | 全局池副本 → 物理删除 |
| seedance2.0-tool | huiben | 全局池副本 → 物理删除 |

---

## 验证方法

1. 检查 `~/.hermes/skills/` 目录中6个跨Agent skill的物理存在状态
2. 检查 `user-universal-tools.yaml` 数据文件内容
3. 通过 `skills_list()` 验证全局池可见性

---

## 实际状态

### 1. `user-universal-tools.yaml` 中的记录

| Skill | 状态 | reason字段 |
|-------|------|-----------|
| picturebook-creator | ❌ 存在于universal_tools | "绘本创作，核心业务" |
| picturebook-video | ❌ 存在于universal_tools | （误判为通用工具） |
| douyin-ops | ❌ 存在于universal_tools | "抖音账号运营，核心业务" |
| ai-drama | ❌ 存在于universal_tools | （误判为通用工具） |
| ai-drama-storyboard | ❌ 存在于universal_tools | "漫剧分镜导演，业务相关" |
| seedance2.0-tool | ⚠️ 存在于universal_tools | "**归属huiben，本Agent仅转发**" — 识别正确但处理错误 |

### 2. 目录结构

| Skill | 实际状态 |
|-------|---------|
| ai-drama | 符号链接 → `/home/luo/.openclaw/workspace/skills/ai-drama` |
| ai-drama-storyboard | 符号链接 → `/home/luo/.openclaw/workspace/skills/ai-drama-storyboard` |
| 其他4个 | 无符号链接，但被写入 universal_tools |

### 3. skills_list() 输出

creative类目下可见：`ai-drama`、`ai-drama-storyboard`

---

## 根因分析

**问题本质：** `user-universal-tools.yaml` 生成后，6个跨Agent skill被**错误地写入 universal_tools 列表**，导致物理删除规则失效。

**根因链条：**
1. 初始化流程生成 universal_tools 候选清单时，未对「归属其他Agent」的skill做排除判断
2. 直接按「业务专用型」写入了免检列表（理由写的是「核心业务」或「业务相关」）
3. 其中 `seedance2.0-tool` 的 reason 字段写着「归属huiben，本Agent仅转发」——**识别是正确的，但处理方式错误**（应物理删除，不应写入免检列表）
4. ai-drama 系列使用符号链接形式存在，可能是历史遗留安装方式

**规则冲突：**
- SKILL.md 明确说：跨Agent skill → 物理删除
- 但 `user-universal-tools.yaml` 实际处理：跨Agent skill → 写入免检列表

---

## 修复方案

在 SKILL.md 的「步骤2：类型预分」中增加**污染检测**步骤：

```
【污染检测 - 跨Agent skill】（优先于一切类型预分）
读取 universal_tools 列表后，立即执行污染检测：

if skill in universal_tools AND skill in [huiben专属skill列表]:
    → 从 universal_tools 移出
    → 标记为「跨Agent skill（污染数据，已纠正）」
    → 归类为「B类业务专用型 → 建议物理移除」

⚠️ 注意：污染检测优先于一切类型预分。即使 universal_tools 文件存在且用户已确认过，也要先执行此检测。
```

---

## 教训

1. **数据文件污染比逻辑错误更难发现**：初始化流程生成的 universal_tools 文件，在后续运行中被直接读取使用，导致污染数据持续生效
2. **识别正确 ≠ 处理正确**：`seedance2.0-tool` 的 reason 字段已经写了「归属huiben，本Agent仅转发」，但代码仍然将它放入了 universal_tools，说明判断逻辑和处理逻辑是分离的
3. **符号链接是历史遗留**：ai-drama 系列使用符号链接，可能是早期安装方式，不代表当前状态
4. **测试场景设计的重要性**：s1-default-organize 场景能发现这个问题，说明测试驱动开发（TDD）思路在skill维护中同样适用