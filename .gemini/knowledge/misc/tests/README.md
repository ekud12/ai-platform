# Compliance Tests

These files are **Static Analysis Contracts** for the AI Operating System itself.

## Purpose
They define the "Unit Tests" for your Agent Definitions (Prompts). They are not tests for your C# code; they are tests to ensure your *Agents* are correctly configured.

## Usage
These tests are run by the **Meta Agent** (or a future CI pipeline script) during a "System Audit".

*   **`agent-contracts.md`**: Verifies that every agent file (`agents/roles/*.md`) has the required sections (Identity, Mandate, Strict JSON Output).
*   **`topology-validation.md`**: Verifies that the `.gemini/topology/` rules are logical (no loops, no isolated agents).
*   **`rule-coverage.md`**: Verifies that every rule ID cited in an agent (e.g., `CS-SEC-001`) actually exists in a `rules/*.md` file.

## How to Run (Manual)
Ask the Meta Agent:
> "Meta, please audit the system against .gemini/tests/agent-contracts.md"
