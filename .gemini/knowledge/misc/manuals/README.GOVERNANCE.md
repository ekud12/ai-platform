# Governance & Policies

## 1. The Constitution
The **Constitution** is the root of trust.
*   **Immutable:** Agents cannot change it.
*   **Universal:** Applies to all files and actions.

## 2. Safety Policies (`.gemini/policies/`)
*   **Sandbox:** No execution outside the project root.
*   **Network:** No unauthorized external calls.
*   **Filesystem:** No modification of `.gemini/` without explicit "System Upgrade" authorization.

## 3. Emergency Protocol (The Kill Switch)
If the file `.panic` is detected:
1.  **ALL** agents halt immediately.
2.  **NO** further output is generated.
3.  **Human** intervention is required to resume.

## 4. Hierarchy of Authority
1.  **Human User** (God Mode)
2.  **Constitution** (Hard Constraints)
3.  **Meta Agent** (System Referee)
4.  **Domain Agents** (Workers)