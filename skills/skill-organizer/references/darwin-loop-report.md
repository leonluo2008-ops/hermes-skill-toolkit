# Skill Organizer 达尔文循环优化报告

> 记录 skill-organizer 通过达尔文循环的自我优化过程，供后续优化参考。

## 优化日期
2026-05-29

## 基线状态
- **版本**: v1.0.6
- **核心设计**: 物理删除规则替代排除规则
- **基线评分**: 84.9/100

---

## 达尔文循环 Round 1

### 测试场景设计（4个）

| 场景ID | 描述 | 测试方法 |
|--------|------|---------|
| s1-default-organize | 验证物理删除规则 | 说"整理skill"，检查跨Agent skill是否被删除 |
| s2-huiben-organize | 验证业务专用型不误判 | huiben说"整理skill"，douyin-ops应进入诊断 |
| s3-tl-dr-list | TL;DR决策树 | 说"有哪些skill"，不走完整流程 |
| s4-deletion-complete | 删除完整性 | 检查文件系统和huiben副本是否正确 |

### 测试结果

| 场景 | 结果 | 发现 |
|------|------|------|
| s1-default-organize | 初测失败→修复后通过 | `user-universal-tools.yaml`污染：跨Agent skill被错误标记 |
| s2-huiben-organize | ✅ 通过 | 业务专用型正确识别，不误判 |
| s3-tl-dr-list | ✅ 通过 | TL;DR决策树正确生效 |
| s4-deletion-complete | ✅ 通过 | 物理删除完整，huiben副本保留 |

### 问题发现

**问题**: `user-universal-tools.yaml` 中跨Agent skill被错误标记为"通用工具"

**根因**: 初始化流程生成yaml时，把跨Agent skill写入了business_specialized section，但这些skill实际应物理删除

**修复**: 从yaml的business_specialized中移除6个跨Agent skill条目

### 优化结果

| 版本 | 改动 | 得分 |
|------|------|------|
| v1.0.6 | 物理删除规则替代排除规则 | 84.9 |
| v1.0.7 | 修复yaml污染，移除跨Agent skill条目 | 85.8 |

**提升**: +0.9分（维度8实测修复）

---

## 关键教训

### 1. 数据文件污染检测必须前置
读取 universal_tools 列表后，立即遍历是否有 huiben 专属skill，有则移出并标记。污染检测优先于一切类型预分。

### 2. 物理删除规则的完整路径
跨Agent skill物理删除需要同时满足：
1. 文件系统：rm -rf 删除全局池副本
2. 数据文件：从 user-universal-tools.yaml 移除条目
3. 验证：skills_list() 中不应出现

只做文件系统删除而不断言数据文件，会导致skill通过免检列表"复活"。

### 3. Darwin循环的"棘轮机制"
只保留改进，自动回滚退步。子agent独立评分避免"自己改自己评"偏差。

---

## git分支策略

```
master: v1.0.6 基线
darwin/YYYYMMDD-HHMM: 优化开发分支
  → 优化commit后merge回master
  → push远程
  → 删除开发分支
```

---

## 参考命令

```bash
# 创建达尔文分支
cd ~/.hermes/skills/software-development/skill-organizer
git checkout -b darwin/YYYYMMDD-HHMM

# 测试场景执行（子agent）
delegate_task(context="...", goal="...", toolsets=["terminal", "file", "skills"])

# 检查物理删除完整性
ls -la ~/.hermes/skills/ | grep -E "picturebook-creator|douyin-ops|ai-drama"

# 检查yaml污染
grep -E "picturebook-creator|douyin-ops|ai-drama" data/user-universal-tools.yaml
```