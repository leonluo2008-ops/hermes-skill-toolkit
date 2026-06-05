# ADR 0005: SkillOpt minimaxi-cn 集成 = bridge wrapper (不改 SkillOpt 源码)

- **状态**: ✅ Accepted
- **日期**: 2026-06-05
- **来源**: PR #2 dogfood 阶段, 跑 searchqa 验证 PR #1 §E SkillOpt 集成时发现
- **影响**: darwin-skill / SkillOpt 集成 / 长期

## 背景

PR #1 给 darwin-skill 集成了 SkillOpt (opt-in + 双轨制)。dogfood 阶段跑 searchqa dry run 验证, 报 `SSL_ERROR_SYSCALL` 在 `api.minimax.cn:443`。

逐步排查发现 2 个**真因**:

### 真因 1: SkillOpt 默认 endpoint 死了
- SkillOpt 0.1.0 minimax backend 默认 `MINIMAX_BASE_URL=https://api.minimax.io/v1` (老域)
- 实际可用 endpoint: `https://api.minimaxi.com/anthropic` (minimaxi-cn 改名后)
- 来源: `~/.hermes/skills/.archive/hermes-model-config/SKILL.md` (v1.0.0, 2026-06-01, archive 6 月 2 日)

### 真因 2: 协议不匹配
- SkillOpt minimax backend 走 OpenAI chat.completions 协议
- minimaxi-cn 走 Anthropic messages 协议 (per `hermes-model-config` skill §"minimax / minimax-cn (MiniMax-M3, M3)")
- `hermes-agent` 自家 minimax-cn provider profile (`plugins/model-providers/minimax/__init__.py`) 也确认: `api_mode="anthropic_messages"`

## 决策

**写 bridge wrapper `tools/skillopt_minimaxi_bridge.py`**, 通过 monkey-patch 替换 `skillopt.model.minimax_backend._post_chat_completion`, 让它走 minimaxi-cn Anthropic 协议:

```python
# 用法 (在跑 SkillOpt 训练前 import)
from skillopt_minimaxi_bridge import patch_skillopt_minimax_backend
patch_skillopt_minimax_backend()
# 然后正常跑 SkillOpt
from skillopt.engine.trainer import ReflACTTrainer
...
```

**不**改 SkillOpt 源码, **不**fork (符合 ADR 0001 "集成 ≠ fork")。

## 关键设计

- **monkey-patch 替换** `_post_chat_completion` (SkillOpt minimax backend 内部函数)
- **OpenAI payload → Anthropic payload** 转换 (剥 OpenAI 字段, 加 system / max_tokens 必填)
- **Anthropic response → OpenAI response** 转换 (choices[0].message.content)
- **thinking 透传**: `chat_template_kwargs.enable_thinking` → Anthropic `thinking.type=enabled`
- **env var override**: `MINIMAX_BRIDGE_BASE_URL` / `MINIMAX_BRIDGE_API_VERSION` 可改 (默认 minimaxi.com)
- **key 来源**: `MINIMAX_CN_API_KEY` env var (跟 hermes 自家 provider profile 一致)

## 后果

### 正向
- ✅ **不 fork SkillOpt** (符合 ADR 0001)
- ✅ **SkillOpt 集成机制 (PR #1 §E) 真的能跑** (dogfood 验证)
- ✅ **wrapper 复用价值高** (任何后续 SkillOpt 训 minimaxi-cn 任务都能直接 import)
- ✅ **风险局部化** (patch 失败 → 立刻 4xx, 不污染 SkillOpt 主流程)

### 负向
- ⚠️ **SkillOpt 升级时 wrapper 要重测** (新版本可能改 `_post_chat_completion` 签名)
- ⚠️ **monkey-patch 在 IDE / type checker 看不见** (SkillOpt 内部 API 实际是 "private")
- ⚠️ **endpoint 改了 wrapper 要改** (如果 minimaxi-cn 再换 endpoint)

### 缓解
- 升级: 写 test `test_skillopt_minimaxi_bridge.py` 验证 patch 点仍存在 (本次未写, 下个 PR 补)
- monkey-patch: 在 wrapper docstring 写明 "SkillOpt 内部 API, 升级会断"
- endpoint 改动: env var 暴露 + ADR 决策树标明

## 备选

### A. 改 SkillOpt 源码 (`minimax_backend.py` 用 minimaxi.com + Anthropic) (❌ 拒绝)
**理由**: 违反 ADR 0001 "不 fork 第三方 skill", 而且改完要维护 fork, 失去上游更新。

### B. 走 minimax 国际版 (api.minimax.io) (❌ 拒绝)
**理由**: 1) 国际版域死了 (跟 minimaxi-cn 是同一死法) 2) 我们没国际版 key 3) 即便能用, 数据出境风险大。

### C. 不用 SkillOpt, 改其他训练框架 (❌ 拒绝)
**理由**: 1) SkillOpt 是当前最契合 4-skill 工具包定位的训练框架 (微软维护, PyPI 包) 2) 改框架 = 推翻 PR #1, 浪费成本 3) 其他框架也不一定调得通 minimaxi-cn。

### D. **当前方案: bridge wrapper monkey-patch** (✅ 接受)
**理由**: 1) 不 fork 2) 复用价值高 3) 风险局部化 4) 上游修了可以一行删 wrapper。

## 相关

- ADR 0001: 不 fork 第三方 skill (本 ADR 强依赖)
- ADR 0002: SkillOpt opt-in 集成 (本 ADR 配套)
- PR #1 §E: SkillOpt 集成 (本 ADR 是它的"配套补丁")
- PR #2: 本 PR (提交 wrapper + 本 ADR)
- 来源: `~/.hermes/skills/.archive/hermes-model-config/SKILL.md` §"minimax / minimax-cn (MiniMax-M3, M3)"
- 来源: `~/.hermes/hermes-agent/plugins/model-providers/minimax/__init__.py` (`api_mode="anthropic_messages"`)
- 工具: `tools/skillopt_minimaxi_bridge.py` (本 PR 提交)
- 报告: `docs/research/2026-06-05-skillopt-dogfood-gardener.md` §"发现 1"
