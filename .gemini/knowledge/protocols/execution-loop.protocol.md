# Execution Loop Protocol

## Purpose
Execute a request through a `Plan -> Approve -> Code -> Review -> Fix` loop.

## Trigger
User command: `/plan <request>`

## The Loop Algorithm

### Phase 1: Planning
1. **Analyze:** Use `planner` skill to analyze the request
2. **Output:** JSON Plan with steps and assigned skills

### Phase 2: Approval
1. **Present:** Show plan summary to user
2. **Wait:** User approves, modifies, or rejects
3. **Branch:**
   - If **approved** → proceed to Phase 3
   - If **modified** → update plan, show again
   - If **rejected** → ask for clarification, go to Phase 1

### Phase 3: Execution Cycle (Repeat for each Step)

**State: CODING**
1. **Select Task:** Pick the next `PENDING` step
2. **Code:** Use `coder-dotnet` or `coder-typescript` skill
   - *Input:* Task instruction + context
   - *Output:* Code changes

**State: REVIEWING**
3. **Review:** Use `reviewer-dotnet` or `reviewer-typescript` skill
   - *Input:* Files changed by the coder
   - *Output:* JSON Verdict (`PASS` or `BLOCK`)

**State: CORRECTION (If Blocked)**
4. **Branch:**
   - **If PASS:** Mark step `COMPLETE`. Go to next step.
   - **If BLOCK:**
     - Check **Retry Count** (Max 5)
     - *If < 5:* Fix issues, go back to **REVIEWING**
     - *If = 5:* **HALT**. Report "Stuck on Task X"

### Phase 4: Completion
1. **Final Report:** Output summary of work done
2. **Output:** `{ "success": true, "files": [...], "iterations": N }`

## Handling Interruptions
- If context fills up, output a **Checkpoint** and ask user to type "Continue"
- Agent must NOT skip approval step in Phase 2
