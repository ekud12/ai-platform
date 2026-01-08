# Agent Roles & Responsibilities

## Directives
Agents are **specialized**. They do not cross boundaries.

## The Team

### 1. The Architect (`planner.agent.md`)
*   **Role:** Project Manager & System Designer.
*   **Output:** Strict JSON Execution Plans.
*   **Directives:** `@orchestration.protocol.md`.

### 2. The Builders (`coder.*.agent.md`)
*   **Role:** Implementation Specialists (.NET, TypeScript).
*   **Output:** Strict JSON with Action Details.
*   **Directives:** Adhere to `language.rules.md` and `performance.rules.md`.

### 3. The Gatekeepers (`reviewer.*.agent.md`)
*   **Role:** QA & Security Audit.
*   **Output:** Strict JSON Audit Reports (`PASS`/`BLOCK`).
*   **Directives:** Enforce `security.rules.md` and `api.rules.md`.

### 4. The Critic (`red-team.agent.md`)
*   **Role:** Adversarial Tester.
*   **Output:** Strict JSON Vulnerability Reports.
*   **Directives:** "Try to break it."

### 5. The Referee (`meta.agent.md`)
*   **Role:** Governance & Consistency.
*   **Output:** Strict JSON Final Approval.
*   **Directives:** Enforce the `Constitution` and Memory Compliance (`.gemmem/LESSONS.md`).