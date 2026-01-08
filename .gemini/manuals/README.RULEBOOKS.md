# Rulebooks & Knowledge Base

## Directives
Rulebooks are **Few-Shot Instructions**. They contain "Good Pattern" vs "Bad Pattern" examples.

## The Library (`.gemini/rules/`)

### 1. Constitution (`rules/constitution/`)
*   **Supreme Law:** Human Supremacy, No Deception, No Self-Preservation.
*   **Enforcement:** Hard-coded into every agent's context.

### 2. .NET Domain (`rules/dotnet/`)
*   **Security:** SQLi prevention, Secret management.
*   **Performance:** Hot path allocations, Span usage.
*   **API:** Minimal APIs, RFC 9457 errors.
*   **Async:** CancellationTokens, No `async void`.

### 3. TypeScript Domain (`rules/typescript/`)
*   **Security:** XSS prevention, Dependency checks.
*   **Types:** Strict null checks, No `any`.
*   **Performance:** Bundle budgets, Lazy loading.

## Citation Protocol
Agents MUST cite rules by ID (e.g., `[CS-SEC-001]`) when flagging issues.