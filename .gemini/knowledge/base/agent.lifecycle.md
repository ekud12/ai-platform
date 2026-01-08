# Agent Lifecycle

## Purpose

This document defines the lifecycle stages for agents in the AI Corporate Agent OS, from initialization to termination.

## Authority

This lifecycle is mandatory. All agents must follow these stages exactly.

## Scope

Applies to all agent invocations regardless of domain or task type.

## Constraints

- Stages must execute in order
- No stage may be skipped
- Failures must be handled according to lifecycle rules
- Audit trail must be maintained throughout

## Lifecycle Stages

### Stage 1: Initialization

**Trigger**: Agent receives task assignment from orchestrator

**Actions**:
1. Validate task assignment format
2. Confirm agent identity matches assignment
3. Load relevant rulebooks
4. Verify access to required resources
5. Check for `.panic` file
6. Log initialization with timestamp

**Success Criteria**:
- All validations pass
- Resources are accessible
- No panic state detected

**Failure Handling**:
- Return initialization failure to orchestrator
- Log detailed error information
- Do not proceed to execution

### Stage 2: Context Loading

**Trigger**: Successful initialization

**Actions**:
1. Load input artifacts specified in task
2. Parse and validate input formats
3. Retrieve applicable rules from rulebooks
4. Establish context scope boundaries
5. Log loaded context summary

**Success Criteria**:
- All inputs are valid and loaded
- Rules are accessible
- Scope is clearly established

**Failure Handling**:
- Return context failure with details
- Specify which inputs or rules failed
- Do not proceed to analysis

### Stage 3: Analysis

**Trigger**: Context successfully loaded

**Actions**:
1. Apply rules to input artifacts
2. Identify violations and observations
3. Compute metrics if applicable
4. Document evidence for findings
5. Check escalation conditions
6. Log analysis progress

**Success Criteria**:
- Analysis complete within scope
- All applicable rules evaluated
- Findings documented with evidence

**Failure Handling**:
- Return partial results if possible
- Document analysis failure point
- Recommend manual review

### Stage 4: Synthesis

**Trigger**: Analysis complete

**Actions**:
1. Aggregate findings into coherent report
2. Prioritize issues by severity
3. Generate recommendations
4. Format output according to requirements
5. Validate output completeness
6. Log synthesis completion

**Success Criteria**:
- Output meets format requirements
- All findings are included
- Recommendations are actionable

**Failure Handling**:
- Return raw findings if synthesis fails
- Document synthesis failure reason
- Flag for human review

### Stage 5: Audit

**Trigger**: Synthesis complete

**Actions**:
1. Generate audit record
2. Include all inputs, outputs, and intermediate states
3. Record timing and resource usage
4. Hash outputs for integrity
5. Store audit record
6. Log audit completion

**Success Criteria**:
- Complete audit record created
- Integrity verification possible
- Record stored successfully

**Failure Handling**:
- Audit failure is critical
- Output may be invalid without audit
- Escalate immediately

### Stage 6: Termination

**Trigger**: Audit complete (success or handled failure)

**Actions**:
1. Release all resources
2. Clear any cached data
3. Return results to orchestrator
4. Log termination with status
5. Exit cleanly

**Success Criteria**:
- Resources released
- Results delivered
- Clean exit achieved

**Failure Handling**:
- Force resource release if needed
- Log termination failure
- Notify orchestrator of unclean exit

## Lifecycle Monitoring

### Timing Constraints

Each stage has maximum duration:
- Initialization: 5 seconds
- Context Loading: 30 seconds
- Analysis: Varies by task (must be specified)
- Synthesis: 30 seconds
- Audit: 10 seconds
- Termination: 5 seconds

Exceeding limits triggers timeout handling.

### Panic Handling

If `.panic` is detected at any stage:
1. Immediately halt current operation
2. Log panic detection
3. Skip to termination
4. Release resources
5. Return panic status to orchestrator

### State Recovery

If agent fails mid-lifecycle:
- Orchestrator receives failure status
- Audit record captures state at failure
- Task may be retried or escalated
- No partial state persists

## Lifecycle Visualization

```
[Task Assignment]
        ↓
   Initialization ──→ [Failure] ──→ Return Error
        ↓
  Context Loading ──→ [Failure] ──→ Return Error
        ↓
     Analysis ──────→ [Failure] ──→ Return Partial
        ↓
    Synthesis ──────→ [Failure] ──→ Return Raw
        ↓
      Audit ────────→ [Failure] ──→ Escalate
        ↓
   Termination
        ↓
   [Results]
```
