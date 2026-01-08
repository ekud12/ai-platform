# Rule Coverage Matrix

## Purpose

This file defines rule-to-agent coverage requirements.

## Authority

Every rule must have enforcement coverage.

## Scope

All rules in all rulebooks.

## Constraints

- No orphaned rules
- Complete coverage required
- Matrix must be current

## Coverage Requirements

### Minimum Coverage

- Every rule has at least one enforcing agent
- Critical rules have at least two agents
- Security rules have dedicated agents

### Coverage Matrix

| Rule Prefix | Primary Agent | Secondary Agent |
|-------------|---------------|-----------------|
| CONST-* | All agents | Adversarial agents |
| CS-LANG-* | DN-LANG-SYN | META-REV |
| CS-ASYNC-* | DN-LANG-ASY | DN-PERF-HOT |
| CS-PERF-* | DN-PERF-HOT | DN-PERF-AOT |
| CS-MEM-* | DN-LANG-MEM | DN-PERF-HOT |
| CS-SEC-* | DN-SEC-* | ADV-* |
| CS-API-* | DN-API-* | META-REV |
| CS-DATA-* | DN-DATA-* | DN-SEC-* |
| CS-OBS-* | DN-OBS-* | META-CON |
| TS-TYPES-* | TS-LANG-* | META-REV |
| TS-RUNTIME-* | TS-RUN-* | TS-SEC-* |
| TS-ASYNC-* | TS-ASY-* | META-REV |
| TS-SEC-* | TS-SEC-* | ADV-* |
| TS-PERF-* | TS-PERF-* | META-REV |
| JS-MOD-* | JS-MOD | META-CON |
| JS-SAFE-* | JS-SAFE | TS-SEC-* |

## Coverage Verification

```
TEST: AllRulesCovered
VERIFY: Every rule ID maps to at least one agent
RESULT: List uncovered rules

TEST: CriticalRulesDoubleCovered
VERIFY: CONST-*, *-SEC-* have 2+ agents
RESULT: List under-covered critical rules

TEST: AgentsEnforceOwnRulebooks
VERIFY: Agents only enforce declared rulebooks
RESULT: List out-of-scope enforcement
```

## Gap Report

```markdown
# Rule Coverage Gaps

## Uncovered Rules
- [rule-id]: No enforcing agent

## Under-covered Critical Rules
- [rule-id]: Only [count] agent(s)

## Out-of-scope Enforcement
- [agent-id] enforcing [rule-id] not in declared rulebooks
```
