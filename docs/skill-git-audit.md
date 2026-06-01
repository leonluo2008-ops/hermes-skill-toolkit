# Skill Git Audit — Multi-System Workflow

_场景: 用户-local skill 同时在 GitHub 有多个分支，对应 OpenClaw/Hermes 不同平台版本，需要梳理版本关系、找到最新提交、规划分支合并。_

---

## 快速审计命令链

```bash
cd ~/.hermes/skills/<skill-name>

# 1. 看当前分支状态（与上游是否同步）
git status
git remote -v

# 2. 拉取所有远程分支更新
git fetch origin

# 3. 列出所有分支（本地+远程）
git branch -a

# 4. 快速扫描每条远程分支的最新3条提交
for branch in "master" "hermes-dev" "main" "skill-picturebook-v2"; do
  echo "=== origin/$branch ==="
  git log "origin/$branch" --oneline -3 2>/dev/null || echo "not found"
done

# 5. 对比本地与某远程分支的 SKILL.md 差异
git diff HEAD origin/hermes-dev --stat
git diff origin/master:SKILL.md SKILL.md | less

# 6. 确认本地 HEAD 对应的远程分支
git show-ref | grep HEAD
git rev-parse HEAD
git rev-parse origin/hermes-dev
git rev-parse origin/master
```

---

## 分支定性判断依据

| 分支模式 | 典型命名 | 内容阶段 | 处理建议 |
|---------|---------|---------|---------|
| OpenClaw 存档 | `archive/*`, `darwin-*`, `cross-platform-*` | 早期迭代存档 | 移入 archive/ 或删远程 |
| 主稳定分支 | `master`, `main` | 活跃生产版本 | 保留，设保护 |
| Hermes 开发分支 | `hermes-dev` | 基于最新 OpenClaw 版本的 Hermes 适配 | 升为默认开发分支 |
| 用户提交分支 | `skill-*-v2`, `pr/*` | 用户在其他设备的提交 | 评估后合并或删除 |
| 修复小PR | `fix/*`, `pr/hermes-*` | 单个小修复 | 评估后合并或关闭 |

---

## 本次 picturebook-creator 审计结果（参考案例）

```
本地 hermes-dev (1f7a757) ← → origin/hermes-dev (同步)
远程 master (257de14)    ← 包含 skill-picturebook-v2 的合并结果
远程 skill-picturebook-v2 (f30d70c) ← 用户昨天在另一台电脑的提交
```

**关键发现：**
- `skill-picturebook-v2` 是用户在其他设备上的最新开发版本
- `origin/master` 已包含该版本的合并（f30d70c merge commit）
- `hermes-dev` 与 `origin/hermes-dev` 同步，但落后于 `skill-picturebook-v2`

---

## 合并决策流程

```
收到"昨天在另一台电脑提交了新版本"后的操作：

1. git fetch origin            # 拉取所有分支包括新提交的
2. git log origin/<新分支>     # 确认内容
3. git diff HEAD origin/<新分支> --stat  # 对比本地当前版本
4. 选择合并策略：
   - 如果本地干净 → git merge origin/<新分支>
   - 如果有冲突且本地也有修改 → 手动解决，优先以外部提交为准
5. git push                    # 推送合并结果
```

---

## 常见陷阱

1. **未 fetch 就比较** — 只比较了上次 fetch 时的快照，导致漏掉最新提交
2. **只看本地分支** — 远程分支可能已经更新，需要 `git fetch origin` 后再比较
3. **忽略远程分支的合并结构** — `f30d70c merge: resolve conflicts` 说明有冲突解决，单独看 diff 会漏掉这个上下文
4. **`git branch -a` 显示本地已删但远程还存在的分支** — 需要手动 `git remote prune origin` 清理