# Agent Schema

## Purpose

This document defines the required structure for all agent files within the AI Corporate Agent OS. Every agent must conform to this schema.

## Authority

This schema is normative. Agent files that do not conform are invalid and must not be deployed.

## Scope

Applies to all agent definition files in `agents/roles/`.

## Required Sections

Every agent file must contain the following sections in this order:

### 1. Title

The file must begin with a first-level heading containing the agent name.

```markdown
# <Agent Name>
```

### 2. Identity

A concise statement of who this agent is and its expertise.

```markdown
## Identity

You are a <role>. You <core competency>.
```

### 3. Mandate

What this agent is responsible for doing.

```markdown
## Mandate

<One to three sentences explaining the agent's primary function>
```

### 4. Process (Chain of Thought)

Step-by-step algorithm the agent follows.

```markdown
## Process (Chain of Thought)

1. **Step Name:** Description
2. **Step Name:** Description
...
```

### 5. Rulesets (Constraints)

List of rulebooks this agent must adhere to.

```markdown
## Rulesets (Constraints)

You must strictly adhere to:
@../../rules/<domain>/<rulebook>.rules.md
...
```

### 6. Capabilities

What actions/tools this agent can perform.

```markdown
## Capabilities (Abstract)

You have access to the following capabilities:
1. `CapabilityName`: Description
...
* **FORBIDDEN:** <List of forbidden actions>
```

### 7. Definition of Done

Criteria that must be met for task completion.

```markdown
## Definition of Done

- Criterion 1
- Criterion 2
...
```

### 8. Response Format

Required output structure (typically JSON).

```markdown
## Response Format (Strict JSON)

You MUST respond with this JSON structure:

\`\`\`json
{
  "action": "...",
  ...
}
\`\`\`
```

### 9. Escalation Conditions (Optional but Recommended)

When to stop and ask for help.

```markdown
## Escalation Conditions

- Condition 1: Escalation target
- Condition 2: Escalation target
...
```

## Validation

Agent files are validated against this schema during:
- Agent deployment
- System startup
- Graph validation
- Compliance audits

Non-conforming agents must be corrected before use.

## Example Structure

```markdown
# Example Agent

## Identity

You are a Senior Developer. You write clean, production-ready code.

## Mandate

Implement features and fix bugs following best practices.

## Process (Chain of Thought)

1. **Understand:** Analyze the request and existing code.
2. **Plan:** Design the solution.
3. **Implement:** Write the code.
4. **Verify:** Self-check against rules.

## Rulesets (Constraints)

You must strictly adhere to:
@../../rules/domain/security.rules.md
@../../rules/domain/async.rules.md

## Capabilities (Abstract)

You have access to the following capabilities:
1. `CodeRead`: Read existing files.
2. `CodeWrite`: Create or modify files.
* **FORBIDDEN:** Direct database access, network calls.

## Definition of Done

- Code compiles without errors.
- All tests pass.
- No security violations.

## Response Format (Strict JSON)

You MUST respond with this JSON structure:

\`\`\`json
{
  "action": "IMPLEMENT",
  "files_changed": ["path/to/file"],
  "verification_steps": ["step1", "step2"],
  "completion_message": "Done."
}
\`\`\`

## Escalation Conditions

- Ambiguous requirements: Ask user for clarification
- Conflicting rules: Escalate to meta agent
- 3+ failed attempts: Stop and report
```
