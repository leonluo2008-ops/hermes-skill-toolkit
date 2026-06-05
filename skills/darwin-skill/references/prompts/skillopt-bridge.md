---
name: skillopt-bridge
description: |
  darwin-skill → SkillOpt 桥接 prompt 模板。**仅在 darwin 用户明确选择 skillopt 引擎时使用**。
  调用方: darwin-skill Phase 0 初始化时,如果 metadata.hermes.engines 含 skillopt 且 mode=opt-in。
  不要默认调用。
license: Apache-2.0
metadata:
  hermes:
    tags: [skills, darwin, skillopt, bridge, prompt-template]
    parent_skill: darwin-skill
    when_to_use: darwin-skill 评估阶段、用户明确要求 SkillOpt 引擎时
---

# darwin-skill → SkillOpt 桥接模板

> **位置**: `darwin-skill/references/prompts/skillopt-bridge.md`
> **触发条件**: darwin-skill Phase 0 初始化, 用户在 `engines: [skillopt]` 且 `mode: opt-in` 下
> **不要在默认 8 维 rubric 路径调用**——本模板只用于 opt-in 走 SkillOpt 引擎时

---

## 模板 (用户实际调用时填变量)

```
[darwin → skillopt bridge | {{date}}]
═══════════════════════════════════════════════

## 上下文
- 触发源: darwin-skill Phase 0 (用户 opt-in SkillOpt 引擎)
- 目标 skill: {{skill_path}}  (如: ~/.hermes/skills/gardener-skill/SKILL.md)
- 优化目标: {{optimize_goal}}  (如: "提升 description 触发词命中率")
- 评估模式: 双轨制 (SkillOpt 客观分数 + darwin 8 维 LLM rubric)

## SkillOpt 配置
- benchmark: {{benchmark}}                # searchqa | alfworld | docvqa | livemathematicianbench | spreadsheetbench | officeqa
- epochs: {{epochs}}                       # 默认 4
- batch_size: {{batch_size}}               # 默认 40
- optimizer_backend: {{optimizer_backend}} # anthropic | openai | azure | qwen | MiniMax
- target_backend: {{target_backend}}       # 同上
- optimizer_model: {{optimizer_model}}     # 推荐 claude-sonnet-4-6 / gpt-5.5
- target_model: {{target_model}}
- slow_update_gate_with_selection: true    # 保守模式 (跟 paper/ckpt 一致)
- workers: {{workers}}                     # 默认 8

## 输出位置
- 输出根目录: outputs/darwin-skillopt-{{date}}/
  ├─ best_skill.md        # ⭐ 最终候选
  ├─ history.json         # 训练历史 (供 darwin Phase 5 引用)
  ├─ runtime_state.json   # 断点续训
  ├─ skills/skill_v*.md   # 每步快照
  └─ steps/step_*/        # 每步 artifacts (patches + evals)

## 双轨验证要求 (来自协调文档 §6 防评分作弊铁律)
1. SkillOpt validation split 分数严格 > 原 SKILL.md 基线
2. darwin 8 维 LLM rubric 评分 不下降 (允许 ±1 浮动)
3. 任一不满足 → 拒绝 best_skill.md, 保留原 SKILL.md, 在 darwin results.tsv 记 status=rejected_anti_cheat

## 失败回退
- SkillOpt 启动失败 → 自动降级 8 维 LLM rubric
- benchmark 数据缺失 → 跳过 SkillOpt, 走 8 维
- 训练超时 / 超预算 → 中止 SkillOpt, 走 8 维
- 任何失败 → darwin results.tsv 记 status=fallback, reason=<具体错误>

## 完成后必做
- [ ] 把 outputs/darwin-skillopt-{{date}}/ 路径记入 darwin results.tsv
- [ ] best_skill.md 不直接覆盖原 SKILL.md (用 git diff 留底)
- [ ] 通知用户双轨验证结果
```

---

## 最小可执行样例

```bash
# 用户说: "用 SkillOpt 训一遍 gardener-skill"
# darwin 接到指令, 走 skillopt-bridge 模板

# 1. 准备数据 split
#   data/gardener-skill_split/{train,val,test}/items.json
#   items 至少要 40 train + 20 val (SkillOpt 最低要求)
#   每个 item: {id, question, context, answers} 或对应 benchmark 格式

# 2. 调用 SkillOpt
python -m skillopt train \
  --config configs/searchqa/default.yaml \
  --split_dir /path/to/gardener-skill_split \
  --optimizer_backend anthropic \
  --target_backend anthropic \
  --optimizer_model claude-sonnet-4-6 \
  --target_model claude-sonnet-4-6 \
  --out_root outputs/darwin-skillopt-2026-06-05

# 3. 双轨验证
# - SkillOpt 端: cat outputs/darwin-skillopt-2026-06-05/history.json | jq '.best_score'
# - darwin 端: 拿 best_skill.md 跑 8 维 rubric, 对比原 SKILL.md
# - 都通过 → 接受 / 任一失败 → 拒绝

# 4. 写入 results.tsv
echo -e "2026-06-05\tgardener-skill\tskillopt\taccepted\tskillopt=+5.2,rubric=+0.5" \
  >> ~/.hermes/state/darwin-results.tsv
```

---

## 重要铁律 (再强调一次)

> 1. **绝不默认开**——只在 §E.1 触发条件满足时
> 2. **绝不直接覆盖**原 SKILL.md——所有改动经 git 留底
> 3. **绝不忽略双轨制**——8 维评分下降时拒绝 best_skill.md
> 4. **绝不让 SkillOpt 故障阻塞**darwin——失败回退到 8 维路径
