# Wiggum Protocol (Autonomous Iteration)

## Purpose
To autonomously execute a Markdown Feature Specification through a `Plan -> Code -> Review` loop without human interruption between steps.

## Trigger
User command: `/wiggum <path/to/spec.md>`

## The Loop Algorithm

### Phase 1: Ingestion
1.  **Read Spec:** Agent reads the target markdown file.
2.  **Validate Spec:** Ensure it contains "Goals", "Constraints", and "Acceptance Criteria".
3.  **Plan:** Invoke `planner.agent`.
    *   *Input:* Spec content.
    *   *Output:* JSON Plan.

### Phase 2: The Cycle (Repeat for each Step in Plan)
**State: EXECUTING**
1.  **Select Task:** Pick the next `PENDING` step.
2.  **Code:** Invoke `coder.*` (DotNet or TS based on task).
    *   *Input:* Task Instruction + Spec Context.
    *   *Output:* Code changes.

**State: REVIEWING**
3.  **Review:** Invoke `reviewer.*`.
    *   *Input:* The specific files changed by the Coder.
    *   *Output:* JSON Verdict (`PASS` or `BLOCK`).

**State: CORRECTION (If Blocked)**
4.  **Branch:**
    *   **If PASS:** Mark step `COMPLETE`. Go to next step.
    *   **If BLOCK:**
        *   Check **Retry Count** (Max 3).
        *   *If < 3:* Invoke `coder.*` again with Reviewer findings. -> Go back to **REVIEWING**.
        *   *If = 3:* **HALT**. Report "Stuck on Task X".

### Phase 3: Completion
1.  **Meta Audit:** Invoke `meta.agent` to check the entire run.
2.  **Final Report:** Output a summary of work done.

## Handling Interruptions
*   If the context window fills up, the Agent must output a **Checkpoint** (current step #) and ask the user to type "Continue".
*   The Agent must NOT ask for confirmation between steps unless `decision = "ask_user"` is triggered by a tool (e.g., `npm install`).
