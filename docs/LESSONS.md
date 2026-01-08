# Lessons Learned

> Auto-updated by Wiggum after each implementation cycle.
> Contains patterns that worked, mistakes to avoid, and project-specific knowledge.

## Last Updated
2026-01-08

## Successful Patterns

*   **Minimal API Structure**: Using a `public class Program` with `static void Main` instead of top-level statements allows for easier integration testing and follows strict organization rules.
*   **Handler Separation**: Extracting Minimal API handlers to `internal static` methods within `Program` (or a dedicated class) keeps `Main` clean and satisfies `CS-API-002`.
*   **Strict Project Configuration**: enabling `AnalysisLevel`, `EnforceCodeStyleInBuild`, and `TreatWarningsAsErrors` ensures high code quality from the start.

## Mistakes to Avoid

*   **Top-Level Statements**: Avoid them in strict mode (`CS-SEC-001`).
*   **Inline Lambdas**: Do not use inline lambdas for Minimal API endpoints (`CS-API-002`). Use method groups.

## Project-Specific Knowledge

*   **Rule Enforcement**: The strict "Hard Enforcement Mode" requires all classes (including Tests) to be `sealed` and fully XML documented.
*   **Safety**: `string?` must be used for potentially null inputs, even if `IsNullOrWhiteSpace` handles it.

## Rule Violations Encountered

| Date | Rule ID | Issue | Resolution |
|------|---------|-------|------------|
| 2026-01-08 | CS-DOC-001 | Missing XML docs on public class | Added /// comments |
| 2026-01-08 | CS-LANG-010 | Single-line if statement | Added braces |
| 2026-01-08 | CS-API-002 | Inline lambda in Minimal API | Extracted to static method |
| 2026-01-08 | CS-SEC-001 | Top-level statements | Converted to Program.Main |
