# Orchestration Protocol

## The "Brain" Algorithm
This protocol defines how the OS "thinks" and executes complex tasks using the **Model Context Protocol (MCP)** and strict JSON schemas.

### Phase 1: Planning (The Architect)
**Agent:** `planner.agent`
**Algorithm:**
1.  **Refresh Memory:** Execute `MapRefresh` capability to ensure `.gemmem/snapshot.json` is current.
2.  **Decompose:** Break user request into atomic steps.
3.  **Dependency Check:** "Can Step B run before Step A?" -> No. Order them.
3.  **Risk Assessment:** "What if this fails?" -> Add fallback plan.
4.  **Output:** A Strict JSON Execution Plan.

**Example Plan:**
```json
{
  "status": "PLANNING",
  "plan": [
    { "step": 1, "role": "coder-dotnet", "capability": "CodeImplementation", "instruction": "Create User Entity" },
    { "step": 2, "role": "reviewer-dotnet", "capability": "CodeReview", "instruction": "Review User Entity" },
    { "step": 3, "role": "meta", "capability": "FinalApproval", "instruction": "Approve changes" }
  ]
}
```

### Phase 2: Execution (The Workers)
**Agent:** `coder-dotnet` or `coder-typescript`
**Algorithm:**
1.  **Read Context:** Load files + Rules + `.gemmem/history.json`.
2.  **Execute:** Perform the capability (Write Code, Run Test).
3.  **Self-Verify:** "Did I break a rule?" (Self-Correction).
4.  **Output:** JSON completion report.

### Phase 3: Review (The Gatekeepers)
**Agent:** `reviewer-dotnet` or `reviewer-typescript`
**Algorithm:**
1.  **Receive:** Code from Phase 2.
2.  **Validate:** Check against domain-specific rules.
3.  **Verdict:** APPROVE or REQUEST_CHANGES (JSON format).
4.  **Output:** Review report with rule citations.

### Phase 4: Finalize (The Meta)
**Agent:** `meta`
**Algorithm:**
1.  **Audit:** Read diff and review reports.
2.  **Constitutional Check:** Verify no constitution violations.
3.  **Verdict:** PASS or BLOCK (JSON format).

### Phase 5: Memory Commit (The Scribe)
**Rule:** NO task is done until memory is updated.
**Actions:**
1.  **Update Lessons:** Append new findings to `.gemmem/history.json`.
2.  **Execute Map Generation:** ALWAYS run `MapRefresh` to update `.gemmem/snapshot.json`.
3.  **Verify Map:** Check `.gemmem/snapshot.json` to ensure new files are visible.

### Phase 6: Escalation (The Panic Button)
**Rule:** If stuck, **STOP**.
**Triggers:**
*   Ambiguity ("I don't know what the user wants").
*   Looping ("I tried 3 times and failed").
*   Constitution Violation ("This requires deleting the OS").

**Action:**
1.  Log `ERROR`.
2.  Output: "I need human help: [Reason]."

---

## State Machine
1.  **IDLE** -> User Request -> **PLANNING**
2.  **PLANNING** -> Plan Ready -> **EXECUTING**
3.  **EXECUTING** -> Code Complete -> **REVIEWING**
4.  **REVIEWING** -> Approved -> **META_CHECK**
5.  **META_CHECK** -> Pass -> **MEMORY_COMMIT**
6.  **MEMORY_COMMIT** -> Complete -> **DONE**
7.  *(Any State)* -> Error/Stuck -> **ESCALATING**
