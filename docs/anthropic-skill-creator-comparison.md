---
note: Reference for hermes-agent-skill-authoring — the de-facto official "skill for writing skills"
last_updated: 2026-06-02
source: https://github.com/anthropics/skills/tree/main/skills/skill-creator
---

# Anthropic Official `skill-creator` — Reference

`hermes-agent-skill-authoring` is **self-authored** (a Hermes-internal convention document), not an industry standard. The de-facto official "skill for writing skills" is Anthropic's own `skill-creator` from the [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) public repo.

The two are **complementary, not competing**:

| Local `hermes-agent-skill-authoring` | Official `anthropics/skills/skill-creator` |
|---|---|
| File-level contract (frontmatter, validator, structure, size limits) | Lifecycle contract (draft → test → eval → iterate) |
| In-repo placement + peer-matched structure | A/B test harness, eval viewer, trigger optimization |
| Migration recipes from OpenClaw / Dify / Coze | Quantitative measurement (pass rate / latency / tokens) |
| Common pitfalls list | Description trigger accuracy iteration |

## What the official skill-creator provides (that local skill does not)

1. **A/B parallel testing** — run prompts *with* the skill vs *without* the skill in parallel, capture timing + token usage for quantitative comparison.
2. **Interactive browser eval viewer** — `eval-viewer/generate_review.py` script generates a page showing pass rates, latency, token efficiency across iterations.
3. **Description trigger optimization** — tests 20 realistic trigger/non-trigger queries against the skill's description, iterates up to 5 rounds to improve triggering accuracy.
4. **Explicit iterate loop** — the skill's core job is "figure out where the user is in [draft → test → eval → rewrite] and jump in to help them progress."

## What local skill provides (that official does not document)

- Exact frontmatter constraints (`name` regex, 1024 char `description` limit, 100,000 char body limit) with validator source location (`tools/skill_manager_tool.py`)
- In-repo file placement rules + peer-matched structure
- Common pitfalls (cross-system migration, hardcoded paths, format vs. principle, trigger-word drift)
- OpenClaw / Dify / Coze / plain-text → Hermes migration recipes
- 3-layer separation rule (SKILL.md orchestrates, `references/*.md` holds prompts, `scripts/*.py` holds tool calls)

## Install (for Claude Code, independent of Hermes)

```bash
npx skills add https://github.com/anthropics/skills --skill skill-creator
```

Installs into Claude Code's skill directory (`~/.claude/skills/` on most setups). **Independent of** Hermes's `~/.hermes/skills/` — both can coexist. Not a substitute for the local skill.

## When to use which

| Task | Use |
|---|---|
| Draft a new in-repo SKILL.md, validate frontmatter, place in repo | `hermes-agent-skill-authoring` |
| Test whether a skill actually changes agent behavior | `anthropics/skills/skill-creator` |
| Optimize skill description trigger accuracy | `anthropics/skills/skill-creator` |
| Run a quantitative eval loop (pass rate, latency, tokens) | `anthropics/skills/skill-creator` |
| Migrate a non-Hermes agent (OpenClaw/Dify/Coze) to a Hermes skill | `hermes-agent-skill-authoring` |
| Get the iterator's *job description* (how to guide the user through the loop) | `anthropics/skills/skill-creator` |

## Borrow-worthy patterns not yet adopted locally

These are gaps that future sessions may want to close:

- **A/B harness** → could augment `darwin-skill` (currently runs test prompts but has no control / no parallel-without-skill comparison)
- **Trigger optimization** → could replace manual frontmatter trigger-words maintenance (which `hermes-agent-skill-authoring` pitfall #11 already flags as Darwin T=7 inconsistency risk)
- **Eval viewer** → could augment `gardener-skill` (which currently lacks any quantitative output for evaluating 思维类 skill changes)
- **Iterate-loop framing** → could be added to SKILL.md's "Workflow" section as an explicit step 7 ("Run eval/iterate loop") after the current step 5 (git commit)

## Related: `frontend-design` benchmark

While reading the official repo, note that `anthropics/skills/frontend-design` is Anthropic's reference example of a high-quality production skill (~486K uses). Useful as a quality benchmark when in doubt whether your SKILL.md is "rich enough".
