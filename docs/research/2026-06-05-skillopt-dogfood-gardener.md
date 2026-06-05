# Dogfood 报告：SkillOpt × 4-skill 工具箱 (minimaxi-cn 集成发现)

**日期**: 2026-06-05
**目的**: 验证 PR #1 写的 SkillOpt 集成 + ADR 0002/0004 双轨制机制可行性
**结论**: ✅ **机制可行** (searchqa dry run 端到端通); 发现 **3 个真实世界问题**

---

## 1. 范围

**做了**:
- ✅ SkillOpt 0.1.0 装到 hermes venv
- ✅ SkillOpt minimax backend → minimaxi-cn 调通 (用 monkey-patch wrapper, 不改 SkillOpt 源码)
- ✅ searchqa 端到端 dry run (5 train + 2 val + 2 test, 1 epoch, 2 steps)
- ✅ 训练循环 6 步全部跑通 (rollout→reflect→aggregate→select→update→gate)

**没做** (留给下个 PR):
- ❌ 60 items 真训 gardener-skill (2-6 h, $20-80)
- ❌ 8 维 rubric 双轨验证
- ❌ 报 issue 给 microsoft/SkillOpt (wheel 漏打包 + endpoint 死了)

---

## 2. 关键发现 (3 个)

### 发现 1: SkillOpt 默认 minimax backend 不能调 minimaxi-cn (🔴 严重)

**症状**: `SSL_ERROR_SYSCALL` on `api.minimax.cn:443`

**根因**:
- SkillOpt 0.1.0 默认 endpoint = `https://api.minimax.io/v1` (**已死/无效**)
- minimaxi-cn 实际 endpoint = `https://api.minimaxi.com/anthropic` (来源: `~/.hermes/skills/.archive/hermes-model-config/SKILL.md`)
- 协议不匹配: SkillOpt minimax backend 走 OpenAI chat.completions, minimaxi-cn 走 Anthropic messages

**解决**:
- 写 `tools/skillopt_minimaxi_bridge.py` (~6.4 KB, monkey-patch)
- 替换 SkillOpt `minimax_backend._post_chat_completion` → 走 Anthropic 协议
- **不**改 SkillOpt 源码, **不**fork (符合 ADR 0001)

**复用价值**: 任何后续用 SkillOpt 训 minimaxi-cn 都能直接 import

**详见**: ADR 0005

### 发现 2: SkillOpt 0.1.0 wheel 漏打包 21 个 prompt 文件 (🟡 中等)

**症状**: `FileNotFoundError: Prompt 'analyst_error' not found. Searched: skillopt/prompts/analyst_error.md`

**根因**: PyPI v0.1.0 wheel 只打包 `__init__.py`, 漏了所有 `.md` prompt 文件 (analyst_*, merge_*, ranking, rewrite_skill, slow_update, meta_skill, lr_autonomous)

**解决**:
- 从 GitHub raw 拉 21 个 prompt 补到 `site-packages/skillopt/prompts/`
- 这是**临时**修, **正确**做法是: 报 issue 给 microsoft/SkillOpt, 或 pip install --no-binary 走 source

**详见**: ADR 0006

### 发现 3: hermes-model-config skill 6 月 2 日被 archive (🟢 正面)

**意外发现**: minimaxi-cn 正确配置藏在 `.archive/hermes-model-config/SKILL.md` 里
- API protocol: `anthropic_messages`
- Endpoint: `https://api.minimaxi.com/anthropic`
- Vision: 硬编码 override in `agent/models_dev.py`

**意义**:
- 园丁系列 ADR 0001 决策 "不 fork 第三方 skill" **得到了额外验证**——hermes 自己已经 archive 的 skill 反而是**当前**最权威的配置信息源
- archive 目录不是 "delete", 是 "保留 history" (跟 monorepo archive 同理念)

**建议** (本次不做): 把 `hermes-model-config` 从 archive 恢复, 或把其内容整合进 `hermes-multi-agent` skill

---

## 3. 复用工具沉淀 (本次入仓)

| 文件 (本 monorepo 路径) | 大小 | 用途 |
|------|------|------|
| `tools/skillopt_minimaxi_bridge.py` | ~6.4 KB | SkillOpt minimax backend → minimaxi-cn bridge (monkey-patch) |
| `docs/research/2026-06-05-skillopt-dogfood-gardener.md` | ~6 KB | 本报告 (引用) |
| `docs/decisions/0005-skillopt-minimaxi-cn-bridge.md` | ~4.6 KB | ADR 0005 |
| `docs/decisions/0006-skillopt-wheel-missing-prompts.md` | ~4 KB | ADR 0006 |

**留在本地 (不入仓)**:
- `~/.hermes/.research/skillopt_dogfood_searchqa.yaml` (1.7 KB) — searchqa config 模板 (用户级, 不用公开)
- `~/.hermes/.research/skillopt_dogfood_base.yaml` (4.5 KB) — base 缓存 (从 upstream 拉, 不需入仓)
- `~/.hermes/.research/skillopt_dryrun.py` (2.4 KB) — dry run 脚本 (用户级, 不用公开)
- `~/.hermes/.research/skillopt_dryrun_split/` (5+2+2 items) — 验证用 split (一次性, 不用入仓)
- `/home/luo/.hermes/hermes-agent/venv/lib/python3.11/site-packages/skillopt/prompts/*.md` (21 文件) — 漏打包 prompt 临时补 (venv 局部, 跟 venv 走)

---

## 4. 决策清单 (本次产生 / 建议)

### 已完成 (本次)
- ✅ Bridge wrapper 不 fork SkillOpt (符合 ADR 0001)
- ✅ Dry run 端到端通, 验证 PR #1 §E SkillOpt 集成机制
- ✅ ADR 0005/0006 入仓 (本 PR)
- ✅ dogfood 报告入仓 (本 PR)

### 建议下个 PR 做 (PR #3)
- 📋 真训 gardener-skill (60 items + 4 epochs, 预计 2-6 h, $20-80)
- 📋 8 维 rubric 双轨验证
- 📋 写 `tools/install_skillopt.sh` (pip install + 补 prompt 一行化)
- 📋 在 wrapper 加 prompt 存在性预检
- 📋 报 issue 给 microsoft/SkillOpt (zh-CN 描述)

### 远期
- 📋 恢复 hermes-model-config (从 archive 提出来) 或整合进 hermes-multi-agent (那是 hermes-agent 仓库的事)

---

## 5. 关键 takeaway

1. **wrapper 设计** = 临时 monkey-patch, 不改上游, 符合 ADR 0001
2. **SkillOpt 跟 minimaxi-cn 集成需要 wrapper** (这是 skill 沉淀的核心发现)
3. **hermes-model-config archive = 配置真相源** (反直觉但实用)
4. **下个 PR 必须做 ADR 0005/0006** (防止下次重踩)
5. **60 items 真训留给单独 PR** (时间盒 + cost 控制)
6. **dogfood 价值在"发现 bug" > "训出好 skill"** (这次发现 3 个真实问题, 比训出 best_skill.md 价值大)
