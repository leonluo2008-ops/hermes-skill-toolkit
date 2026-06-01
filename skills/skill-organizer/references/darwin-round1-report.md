# skill-organizer v1.0.7 变更记录

> Darwin循环实测发现的问题和修复，2026-05-29

---

## v1.0.7 变更：从排除规则到物理删除

### 核心原则确立

**用户明确（2026-05-29）：**
> 根本就不存在所谓的转发或专职agent分类。原则就是用不上的，就不要出现在对应agent的skill清单里

**旧规则（v1.0.4-v1.0.6）：**
- 跨Agent skill → 「排除后保留文件」（逻辑删除）
- 存在中间状态，导致skill仍在yaml中出现

**新规则（v1.0.7）：**
- 跨Agent skill → 直接物理删除全局池副本
- 不存在「排除后保留文件」的中间状态
- huiben profile有专属版本，全局池不应有副本

---

## 实测发现的问题

### 问题：user-universal-tools.yaml 污染

**现象：**
- 物理删除了6个跨Agent skill（picturebook-creator/video、douyin-ops、ai-drama、ai-drama-storyboard、seedance2.0-tool）
- 但它们仍出现在 `data/user-universal-tools.yaml` 的 `business_specialized` 列表中
- skill-organizer运行时仍会把这些skill当作"业务专用型"处理

**根因：**
初始化流程生成yaml时，把跨Agent skill写入了business_specialized section，但执行的是物理删除而非归档

**修复（v1.0.7）：**
```yaml
# === 业务专用型（需诊断评分）===
# 注意：跨Agent skill（picturebook-creator/picturebook-video/douyin-ops/ai-drama/ai-drama-storyboard/seedance2.0-tool）
# 已在全局池物理删除，此处仅记录huiben profile的业务专用型skill
business_specialized:
  - name: baoyu-comic
    reason: "知识漫画，业务相关"
  # ...（不含跨Agent skill）
```

---

## Darwin测试场景设计

### 测试场景（4个覆盖核心规则）

| 场景 | 描述 | 验证点 |
|------|------|--------|
| s1-default-organize | 主Agent调用skill-organizer | 跨Agent skill被物理删除，不在清单出现 |
| s2-huiben-organize | huiben profile调用 | douyin-ops作为业务专用型，不被误判 |
| s3-tl-dr-list | TL;DR快速查询 | 直接列出清单，不走完整流程 |
| s4-deletion-complete | 删除完整性验证 | 全局池删除干净，huiben副本保留 |

### 测试prompt设计原则

每个测试场景应包含：
1. **背景**：Agent类型、SOUL关键词、当前状态
2. **操作**：用户实际会说的话
3. **预期结果**：明确的验证点
4. **预期输出格式**：如何判断通过/失败

### 实测结果

| 场景 | 初始结果 | 修复后 |
|------|---------|--------|
| s1-default-organize | ❌ yaml污染导致规则失效 | ✅ 修复后通过 |
| s2-huiben-organize | ✅ 通过 | - |
| s3-tl-dr-list | ✅ 通过 | - |
| s4-deletion-complete | ✅ 通过 | - |

**评分变化：**
- baseline v1.0.6: 84.9
- v1.0.7: 85.8 (+0.9)

---

## huiben profile skill整理模式

### 安装的通用工具（symlink方式）

```
# 飞书套件（15个）
lark-calendar, lark-doc, lark-im, lark-drive, lark-task, lark-sheets, 
lark-vc, lark-mail, lark-contact, lark-approval, lark-attendance, 
lark-base, lark-event, lark-wiki, lark-minutes

# 文档工具（2）
docx, xlsx

# GitHub工具（6 via github/目录）
github-auth, github-pr-workflow, github-code-review, 
github-repo-management, github-issues, codebase-inspection

# Skill工具（4）
skill-organizer (→ v1.0.7 symlink), hermes-agent-skill-authoring, 
find-skills, darwin-skill
```

### 用户明确移除的类别

- 情报类（5）：children-content-intelligence, image-gen-intelligence, audio-gen-intelligence, blogwatcher, youtube-content
- Apple生态（5）：macos-computer-use, imessage, apple-reminders, apple-notes, findmy
- 其他（3）：superpowers, video-timing, gif-search

### symlink安装命令模板

```bash
HUIBEN_SKILLS=~/.hermes/profiles/huiben/skills
GLOBAL_SKILLS=~/.hermes/skills

# 单个skill
ln -s "$GLOBAL_SKILLS/<skill-name>" "$HUIBEN_SKILLS/<skill-name>"

# 批量（飞书套件）
for name in lark-calendar lark-doc lark-im lark-drive lark-task lark-sheets lark-vc lark-mail lark-contact; do
  ln -s "$GLOBAL_SKILLS/$name" "$HUIBEN_SKILLS/$name"
done
```

---

## 关键教训

1. **物理删除后必须清理yaml** — 删除文件不够，user-universal-tools.yaml里的条目也要同步移除
2. **测试要跑实际场景** — 静态分析发现不了"yaml污染"这种运行时问题
3. **通用工具安装用symlink** — 维护成本低，更新一次全局有效
4. **用户明确不要的类别立即移除** — 不要留着"可能有用"