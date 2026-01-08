# Agent Contract Tests

## Purpose

This file defines validation rules for agent scope compliance.

## Authority

All agents must pass these tests.

## Scope

Agent definition validation.

## Constraints

- All tests must pass
- No exceptions permitted
- Tests run at startup

## Test Categories

### Schema Compliance

```
TEST: AgentSchemaComplete
VERIFY: All required sections present
SECTIONS: Purpose, Authority, Scope, Constraints,
         Responsibilities, Forbidden Actions,
         Rulebooks Enforced, Required Inputs,
         Output Requirements, Escalation Conditions
RESULT: PASS if all present, FAIL if any missing
```

### Scope Validity

```
TEST: ScopeWellDefined
VERIFY: Scope has both "Applies to" and "Does not apply to"
RESULT: PASS if both present and non-empty
```

### Forbidden Actions

```
TEST: ForbiddenActionsPresent
VERIFY: At least one forbidden action defined
MINIMUM: 2 forbidden actions
RESULT: PASS if minimum met
```

### Rulebook References

```
TEST: RulebookReferencesValid
VERIFY: All referenced rulebooks exist
FORMAT: path/to/rulebook.md (PREFIX-*)
RESULT: PASS if all exist
```

### Output Requirements

```
TEST: OutputIsStrictJSON
VERIFY: Agent explicitly states "Response Format (Strict JSON)"
RESULT: PASS if JSON schema is defined
```

### Escalation Paths

```
TEST: EscalationPathsTerminate
VERIFY: All escalation paths reach human or system
RESULT: PASS if all paths terminate
```

## Validation Report

```markdown
# Agent Contract Validation

## Agent: [agent-name]

| Test | Result | Details |
|------|--------|---------|
| SchemaComplete | PASS/FAIL | [missing sections] |
| ScopeWellDefined | PASS/FAIL | [issues] |
| ForbiddenActionsPresent | PASS/FAIL | [count] |
| RulebookReferencesValid | PASS/FAIL | [invalid refs] |
| EscalationPathsTerminate | PASS/FAIL | [unterminated] |

## Overall: PASS/FAIL
```
