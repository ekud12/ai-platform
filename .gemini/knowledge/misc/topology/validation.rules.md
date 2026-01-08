# Graph Validation Rules

## Purpose
Ensures the Agent Graph remains valid and acyclic.

## Directives

### 1. Single Path to Production
**Rule:** Code MUST flow: `Coder` -> `Reviewer` -> `Meta`.
**Forbidden:** `Coder` -> `User` (Bypassing Review).

### 2. Role Exclusivity
**Rule:** A node CANNOT be both `Coder` and `Reviewer` for the same task.
**Reason:** Conflict of Interest.

### 3. Acyclic Flow
**Rule:** Feedback loops are allowed (Reviewer -> Coder), but Infinite Loops are FORBIDDEN.
**Limit:** Maximum 3 retry loops before Escalation.

### 4. Constitutional Root
**Rule:** All agents MUST trace their authority back to the `Constitution` via `Meta`.