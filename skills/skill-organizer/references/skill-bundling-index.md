# Skill 工具包分发模式补充

本文档是 `SKILL.md` 的补充，专门讲"多个 skill 形成工具包"的场景。

**核心参考**：`references/skill-bundling-patterns.md`

## 何时加载 references/skill-bundling-patterns.md

- 用户说"skill 工具包"/"打包 skill"/"统一管理 skill"
- 用户想建 monorepo / 写 install.sh
- 优化或迁移 skill 时，**SKILL.md 内文中的 URL 跟 `git remote -v` 不一致**

## 主要内容速览

- **4 种分发模式对比**：A. 单 monorepo（**用户偏好**） / B. polyrepo / C. 总+分 monorepo / D. polyrepo+install
- **monorepo 推荐目录结构**
- **install.sh 模板**（symlink 而非 copy + `HERMES_SKILLS_DIR` 占位符 env var）
- **SKILL.md URL 跟 git remote 一致 pitfall**（2026-06-01 踩坑实录：darwin-skill 写了 alchaincyf，实际是 leonluo2008-ops）
- **自查命令**（循环所有 skill，检测 remote vs doc URL 不一致）
- **用户偏好**：不维护多个仓库管同类型 / 命名约定 / 废弃目录物理删除

## 跟 superpowers 的关系

- superpowers 决定"何时做整理 / 何时建 monorepo"（规划层）
- skill-organizer 决定"monorepo 长什么样、install 怎么写"（执行层）
- 两者**互补不重叠**
