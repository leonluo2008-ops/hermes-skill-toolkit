# Skill Organizer v1.0.4 维度8评估报告

> 评估日期：2026-05-29  
> 评估目标：skill-organizer v1.0.4「调度型Agent排除规则」  
> 评估结果：**通过（8.7/10）**

---

## 评估框架：维度8实测

**定义**：在真实多Agent环境下，用实际prompt验证skill规则是否按预期工作，而非仅靠静态代码审查。

**测试方法**：
1. 构造包含Agent类型+SOUL.md关键词的测试prompt
2. 分别用with_skill和baseline运行，对比输出
3. 验证排除规则是否在正确时机（类型预分前）触发

---

## 测试用例

### Prompt 1：调度型Agent整理skill

**背景**：
- 当前Agent: default（系统中枢）
- SOUL.md包含"调度、中枢、路由、转发"

**用户消息**：「整理skill，告诉我哪些有用哪些没用」

**预期行为**：
1. 识别出调度型/中枢型Agent
2. 在类型预分前先排除跨Agent skill
3. 诊断范围 = 通用工具 + 自身业务专用型

**实际结果**：
- ✅ 识别出调度型Agent（SOUL.md关键词命中）
- ✅ 6个跨Agent skill被预分前排除（picturebook-creator、douyin-ops、ai-drama、ai-drama-storyboard、seedance2.0-tool、picturebook-video）
- ✅ 诊断范围正确（通用工具+自身业务专用型）

**评分**：9/10（扣1分：初始化流程会中断验证流程）

---

### Prompt 2：验证排除规则是否生效

**背景**：同Prompt 1

**用户消息**：「整理skill」

**预期行为**：
1. 步骤1读取SOUL.md判断Agent类型
2. 步骤2预分前检查调度型关键词
3. 跨Agent skill在预分前排除，不进入后续诊断

**实际结果**：
- ✅ SOUL.md读取正确
- ✅ 调度型关键词识别正确
- ✅ 排除在预分前完成
- ✅ 预分结果显示：通用工具（免检72个）、自身业务专用型、跨Agent型（已排除）

**评分**：10/10

---

### Prompt 3：执行型Agent整理skill

**背景**：
- 当前Agent: huiben（内容创作中枢）
- SOUL.md包含"创作、执行、运营"

**用户消息**：「整理skill」

**预期行为**：
1. 识别出执行型/专职型Agent
2. 调度型Agent排除规则不触发
3. 跨Agent skill作为业务专用型进入诊断

**实际结果**：
- ✅ 识别出执行型Agent（关键词"执行、创作"命中）
- ✅ 排除规则不触发（SOUL不包含调度关键词）
- ✅ 跨Agent skill作为业务专用型进入步骤3诊断

**评分**：10/10

---

## 问题发现

### 问题1：初始化流程干扰排除规则验证

**现象**：当 `data/user-universal-tools.yaml` 不存在时，skill-organizer会暂停诊断先做初始化。

**影响**：如果用户只想验证排除规则逻辑而非真正跑完整流程，会被初始化提示打断。

**已处理**：在SKILL.md中增加了时序说明：先完成排除规则判断（识别Agent类型+排除跨Agent skill），再进行初始化确认。

**评估建议**：测试排除规则时，可预先创建空的data文件绕过初始化检查：
```bash
mkdir -p ~/.hermes/skills/software-development/skill-organizer/data
echo 'version: "1.0"' > ~/.hermes/skills/software-development/skill-organizer/data/user-universal-tools.yaml
```

---

## 评分汇总

| Prompt | 得分 | 折算 |
|--------|------|------|
| Prompt 1 | 9/10 | 2.7/3 |
| Prompt 2 | 10/10 | 3.0/3 |
| Prompt 3 | 10/10 | 3.0/3 |
| **总分** | **29/30** | **8.7/10** |

---

## 评估结论

**调度型Agent排除规则（v1.0.4）工作正常**：

1. SOUL.md读取正确（`/profiles/default/SOUL.md`）
2. 调度型关键词识别正确（"调度"、"中枢"）
3. 跨Agent skill在预分前全部排除
4. 本Agent只保留通用工具 + 自身业务专用型
5. 执行型Agent（huiben）不受影响，排除规则正确不触发

**扣分原因**：初始化流程会延迟用户得到诊断范围的时间，但不影响核心规则正确性。

---

## 后续评估建议

如需评估其他维度或规则，可使用以下测试脚本方法：

```python
import subprocess

def run_hermes_chat(prompt):
    cmd = f'hermes chat -q "{prompt}" --provider minimax-cn -Q 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    return result.stdout + result.stderr

# 测试调度型Agent
prompt = "【评估任务】测试skill-organizer v1.0.4「调度型Agent排除规则」..."
output = run_hermes_chat(prompt)
```