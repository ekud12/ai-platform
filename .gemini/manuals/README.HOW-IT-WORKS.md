# AI Corporate Agent OS: How It Works

## 1. System Philosophy
This is not a chatbot. It is a **Constitutionally Governed Operating System** for AI agents.
*   **Text-First:** The "Brain" is defined entirely in Markdown files.
*   **Role-Based:** Agents are not generalists; they have strict Roles (Coder, Reviewer, Meta).
*   **Safety-Hardened:** The `Constitution` prevents rogue behavior at the prompt level.

## 2. The Execution Loop (Protocol)
Every complex task follows the **Orchestration Protocol**:

1.  **Input:** User types `/agents:planner "Build a Login API"`
2.  **Phase 1 (Architect):** `PLANNER` breaks it down into steps.
3.  **Phase 2 (Build):** `CODER` writes the code.
4.  **Phase 3 (Gatekeep):** `REVIEWER` checks `security.rules.md`.
    *   *Fail:* Loop back to Phase 2.
    *   *Pass:* Proceed.
5.  **Phase 4 (Finalize):** `META` checks for OS consistency.

## 3. Directory Structure (The Brain)
*   **`.gemini/agents/roles/`**: The Workers (Strict JSON Prompts).
*   **`.gemini/rules/`**: The Knowledge (Constraints & Patterns).
*   **`.gemini/protocols/`**: The Algorithms (How-To guides).
*   **`.gemini/policies/`**: The Laws (Permissions & Termination).
*   **`.gemini/topology/`**: The Collaboration Graph.
*   **`.gemini/manuals/`**: The System Documentation.
*   **`.gemini/tools/`**: The OS Utilities.