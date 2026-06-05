# ADR 0006: SkillOpt 0.1.0 wheel 漏打包 21 个 prompt 文件 — 临时修法手动补

- **状态**: ✅ Accepted
- **日期**: 2026-06-05
- **来源**: PR #2 dogfood 阶段, 跑 searchqa 跑到 reflect 阶段报 `FileNotFoundError: Prompt 'analyst_error' not found`
- **影响**: SkillOpt 集成 / 任何 pip install 4-skill 工具包的人 / 中期

## 背景

PR #1 集成 SkillOpt 后, PR #2 dogfood 跑 searchqa 验证, 跑到 reflect 阶段报:

```
FileNotFoundError: Prompt 'analyst_error' not found.
Searched: skillopt/prompts/analyst_error.md
```

调查 `~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/skillopt/prompts/` 发现**只打包了 `__init__.py`**, 21 个 prompt `.md` 文件**全没**进 wheel:

| 漏掉文件 | 数量 | 类型 |
|---------|------|------|
| `analyst_error*.md` | 3 | reflect 用 (失败分析) |
| `analyst_success*.md` | 3 | reflect 用 (成功分析) |
| `merge_failure*.md` | 3 | aggregate 用 |
| `merge_success*.md` | 3 | aggregate 用 |
| `merge_final*.md` | 3 | 最终合并 |
| `meta_skill.md` | 1 | 跨 epoch 战略记忆 |
| `ranking*.md` | 2 | 排序 + rewrite |
| `rewrite_skill.md` | 1 | skill 改写主 prompt |
| `slow_update.md` | 1 | 慢更新 |
| `lr_autonomous.md` | 1 | 学习率自主调度 |
| **合计** | **21** | - |

## 决策

**临时修法 = 手动从 GitHub raw 补到 `site-packages/skillopt/prompts/`**:

```bash
# 21 个文件, 一行命令补全
cd ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/skillopt/prompts
for f in analyst_error*.md analyst_success*.md merge_*.md meta_skill.md \
         ranking*.md rewrite_skill.md slow_update.md lr_autonomous.md; do
  curl -sL "https://raw.githubusercontent.com/microsoft/SkillOpt/main/skillopt/prompts/$f" -o "$f"
done
```

**每次** `pip install --upgrade skillopt` / 换 venv / 同事 pip install 都要重做。

## 后果

### 正向
- ✅ **立即能跑** (dogfood 验证端到端)
- ✅ **不污染 SkillOpt** (本地修, 不 fork)
- ✅ **命令可重入** (脚本化, 一行补齐)

### 负向
- ⚠️ **每次重装/升级都要手动补** —— onboarding 文档要写清
- ⚠️ **venv 隔离** —— 同事 / CI / 不同 profile 各自 venv 都要补
- ⚠️ **没自动化检测** —— 不补就 silent 跑不通, 错误信息不直观 (只到 reflect 阶段才挂)

### 缓解
- onboarding: 写进 `tools/skillopt_minimaxi_bridge.py` 旁边的 README, 跑前必跑
- venv 隔离: 写 install script `tools/install_skillopt.sh` 一行补 (本次没写, 留 PR #2.1)
- 自动化检测: 在 wrapper `patch_skillopt_minimax_backend()` 里加 prompt 存在性检查, 缺则报错

## 备选

### A. 走 source install (`pip install --no-binary :all: skillopt`) (❌ 拒绝)
**理由**: 1) 编译慢, 引入 C 依赖 2) 跟 hermes venv 兼容风险 3) 上游源不稳定 (可能 dev 分支)。

### B. 报 issue 给 microsoft/SkillOpt, 等修复 (❌ 拒绝)
**理由**: 1) 时间不可控 (上游响应可能几天到几周) 2) 我们 PR #2 不能等 3) 即便修了, v0.1.0 wheel 还是要重装。

### C. 不用 SkillOpt, 换其他框架 (❌ 拒绝)
**理由**: 1) 失去 PR #1 价值 2) 其他框架打包问题不一定少 3) 推翻重做成本大。

### D. **当前方案: 手动从 GitHub 补** (✅ 接受)
**理由**: 1) 立即生效 2) 不污染 3) 命令可重入 4) 上游修了一行删命令。

## 相关

- ADR 0001: 不 fork 第三方 skill (本 ADR 强依赖)
- ADR 0002: SkillOpt opt-in 集成 (本 ADR 配套)
- ADR 0005: SkillOpt minimaxi-cn 集成发现 (同期发现, 同一集成)
- 来源 issue 跟踪: 待报给 microsoft/SkillOpt (PR #2 不阻塞, 留给后续)
- 来源: `~/.hermes/.research/dogfood-report-2026-06-05.md` §"发现 2"
- 报告: `docs/research/2026-06-05-skillopt-dogfood-gardener.md` §"发现 2"

## 后续行动

- 📋 PR #2.1: 写 `tools/install_skillopt.sh` (pip install + 补 prompt 一行化)
- 📋 PR #2.2: 在 `skillopt_minimaxi_bridge.py` 加 prompt 存在性预检
- 📋 报 issue 给 microsoft/SkillOpt (zh-CN 描述)
