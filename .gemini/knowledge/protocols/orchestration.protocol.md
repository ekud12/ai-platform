# Orchestration Protocol

## The "Brain" Algorithm
This protocol defines how the OS executes complex tasks using strict JSON schemas.

### Phase 1: Planning
**Skill:** `planner`
**Steps:**
1. **Analyze:** Understand user request and codebase context
2. **Decompose:** Break request into atomic steps
3. **Order:** Check dependencies ("Can Step B run before Step A?")
4. **Output:** JSON Execution Plan

**Example Plan:**
```json
{
  "status": "PLANNING",
  "plan": [
    { "step": 1, "skill": "coder-dotnet", "instruction": "Create User Entity" },
    { "step": 2, "skill": "reviewer-dotnet", "instruction": "Review User Entity" }
  ]
}
```

### Phase 2: Approval
**Action:** Present plan to user for approval
- If **approved** → proceed to Phase 3
- If **modified** → update plan, show again
- If **rejected** → ask for clarification

### Phase 3: Execution
**Skill:** `coder-dotnet` or `coder-typescript`
**Steps:**
1. **Read Context:** Load relevant files and rules
2. **Execute:** Implement the code
3. **Self-Verify:** Check against rules
4. **Output:** JSON completion report

### Phase 4: Review
**Skill:** `reviewer-dotnet` or `reviewer-typescript`
**Steps:**
1. **Receive:** Code from Phase 3
2. **Validate:** Check against all compiled rules
3. **Verdict:** PASS or BLOCK (JSON format)
4. **Output:** Review report with rule citations

### Phase 5: Fix Loop
**Rule:** If blocked, fix and re-review (max 5 iterations)
- If **PASS** → proceed to completion
- If **BLOCK** → fix issues, return to Phase 4

### Phase 6: Escalation
**Rule:** If stuck, **STOP**.
**Triggers:**
- Ambiguity ("I don't know what the user wants")
- Looping ("I tried 5 times and failed")
- Constitution Violation

**Action:** Output "I need human help: [Reason]"

---

## State Machine
1. **IDLE** → User Request → **PLANNING**
2. **PLANNING** → Plan Ready → **APPROVAL**
3. **APPROVAL** → Approved → **EXECUTING**
4. **EXECUTING** → Code Complete → **REVIEWING**
5. **REVIEWING** → Approved → **DONE**
6. **REVIEWING** → Blocked → **FIXING** → **REVIEWING**
7. *(Any State)* → Error/Stuck → **ESCALATING**
