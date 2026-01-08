---
name: compliance-checklists
description: Final validation checklists for C# 14/.NET 10 and TypeScript Boomcore compliance. Review-only validation before merge or deployment.
allowed-tools: Read, Grep, Glob
---

# Compliance Validation Checklists (Rules Only)

## Purpose
Final validation of code against all rules, patterns, and tags. Ensures complete compliance with C# 14/.NET 10 or TypeScript Boomcore requirements before merge/deployment.

## .NET Compliance Checklist

### C# 14 & .NET 10 Feature Usage
- [ ] **Primary constructors** used where applicable for DI
- [ ] **Collection expressions** (`[...]`) used instead of `new[]` or `new List<>`
- [ ] **Required init** properties on models/records
- [ ] **File-scoped namespaces** throughout
- [ ] **Record types** for DTOs, responses, immutable models
- [ ] **Readonly struct** for configurations and value types
- [ ] **Ref readonly** for large struct parameters
- [ ] **TimeProvider** injected instead of `DateTime.UtcNow`
- [ ] **IExceptionHandler** used for global error handling
- [ ] **ProblemDetails** for all API error responses
- [ ] **FluentValidation** for input validation
- [ ] **ValueTask<T>** in hot paths where sync-fast is common
- [ ] **Extension members** (C# 14) used where appropriate
- [ ] **Field keyword** (C# 14) in property accessors
- [ ] **File-based apps** (C# 14) for scripts and tools

### Forbidden Pattern Detection (.NET)
- [ ] No `dynamic` or `object` in core logic
- [ ] No `Dictionary<string, object>` (use strongly-typed models)
- [ ] No `.Result`, `.Wait()`, or blocking on async operations
- [ ] No `DateTime.UtcNow` (must use `TimeProvider`)
- [ ] No raw `Environment.GetEnvironmentVariable` (use `IOptions<T>`)
- [ ] No inline `if (isDev)` branching (config-driven only)
- [ ] No missing `CancellationToken` in async methods
- [ ] No missing `.ConfigureAwait(false)` in library code
- [ ] No deep nesting (early returns enforced)
- [ ] No missing `{}` braces on if/else/loops
- [ ] No missing logs at return points
- [ ] No TODOs, placeholders, or scaffolds
- [ ] No `new Error(...)` without cause
- [ ] No unbounded `Include()` in EF queries
- [ ] No missing XML comments on public APIs

### Type Safety & Immutability (.NET)
- [ ] All collections are readonly where appropriate
- [ ] Constants use appropriate patterns
- [ ] Access modifiers appropriate (`private` by default)
- [ ] `sealed` on classes not designed for inheritance
- [ ] `readonly` on fields that shouldn't change after init
- [ ] Nullable reference types used correctly
- [ ] Guard clauses with pattern matching where applicable
- [ ] Exhaustive switch expressions with never/exception fallback

### Security Validation (.NET)
- [ ] Input validation at all boundaries (FluentValidation or guards)
- [ ] No hardcoded secrets or credentials
- [ ] `SECRET_*` pattern for secret identifiers
- [ ] Proper auth/authz on all endpoints
- [ ] No SQL injection vectors (parameterized queries only)
- [ ] No XSS vulnerabilities
- [ ] Content Security Policy configured
- [ ] Time-constant comparison for secrets
- [ ] Proper CORS configuration
- [ ] Post-quantum cryptography (.NET 10) for long-term data

### Observability Coverage (.NET)
- [ ] `ILogger<T>` used consistently
- [ ] Logs at all exit points (success and failure)
- [ ] `ILogger.BeginScope()` used for operation grouping
- [ ] Structured logging (no string interpolation in log messages)
- [ ] TraceId/CorrelationId in all logs
- [ ] OpenTelemetry configured if distributed
- [ ] Custom metrics for business KPIs
- [ ] Health checks implemented
- [ ] Error responses include trace identifiers

## TypeScript Compliance Checklist

### Type System Enforcement
- [ ] No `any`, `object`, `{}`, or `Function` types
- [ ] All arrays/tuples are `readonly`
- [ ] Constants use `as const`
- [ ] Explicit return types on all exports
- [ ] `satisfies` used for contract verification
- [ ] No `!` non-null assertions (safe narrowing only)
- [ ] Exhaustiveness via `never` or `assertUnreachable()`
- [ ] Branded types for identifiers (e.g., `UserId`)
- [ ] Discriminated unions with exhaustive switches
- [ ] Template literal types for identifier formats
- [ ] Generic constraints enforced (no open `T`)

### Runtime Validation
- [ ] External data wrapped in zod/valibot/io-ts schemas
- [ ] `.safeParse` used (not `.parse`)
- [ ] Types derived from schemas (`z.infer`)
- [ ] Validation logic separated from model logic
- [ ] `env.ts` validated at runtime start
- [ ] No loose shapes (`z.any`, `z.unknown` without guards)

### Forbidden Pattern Detection (TypeScript)
- [ ] No `any`, `object`, `Function`, `{}`
- [ ] No default exports (named exports only)
- [ ] No floating promises (all awaited)
- [ ] No unwrapped `process.env` or `JSON.parse`
- [ ] No circular imports
- [ ] No mutable exports
- [ ] No implicit returns
- [ ] No logic in index files
- [ ] No top-level await
- [ ] No `console.*` in production code
- [ ] No errors without cause
- [ ] No regexes with catastrophic backtracking
- [ ] No event listeners without cleanup
- [ ] No shared top-level promises
- [ ] No dynamic property access without type guarantee

### Async & Concurrency (TypeScript)
- [ ] All promises awaited (no floating)
- [ ] `AbortSignal` supported in async entry points
- [ ] Timeouts configured for long operations
- [ ] `p-limit`, `p-queue`, or `Promise.allSettled` for parallelism
- [ ] No global top-level promises (use functions)
- [ ] `.abort()` or cancellation exposed on long-lived tasks
- [ ] No `async forEach` (use `for await` or `Promise.all`)
- [ ] No `Promise<void>` (return structured outputs)

### Performance Patterns (TypeScript)
- [ ] `Map`/`Set` used over objects for collections
- [ ] Single-pass transforms (avoid `.map().filter()` chains)
- [ ] Pre-allocated arrays in hot paths
- [ ] Typed arrays for binary/large data
- [ ] Regexes compiled and reused (not inline)
- [ ] Config trees deep-frozen
- [ ] No spreading in hot paths
- [ ] Lazy evaluation in logging
- [ ] `Number.isFinite()`/`isInteger()` over coercion
- [ ] No `JSON.stringify` in hot paths
- [ ] `Set.has` over `Array.includes` for large arrays
- [ ] Retry loops with backoff/limits/abort

### Security Validation (TypeScript)
- [ ] Schema + sanitizer + access check at boundaries
- [ ] Constant-time comparison for secrets
- [ ] CSP/XSS actively enforced (no `innerHTML`)
- [ ] `Object.create(null)` for key stores
- [ ] `SECRET_*` isolation pattern
- [ ] No prototype pollution vectors

### Documentation (TypeScript)
- [ ] JSDoc on all exported members
- [ ] `@example` on all exported functions/types
- [ ] Naming conventions: kebab-case files, PascalCase types, camelCase variables, SCREAMING_SNAKE_CASE constants

## Cross-Language Validation

### Architecture & Structure
- [ ] Feature-first folder organization
- [ ] Named exports only (no default exports)
- [ ] Canonical file suffixes (`.service`, `.guard`, `.schema`)
- [ ] Aliased imports (no relative traversals like `../../`)
- [ ] No circular imports (acyclic import graph)
- [ ] Strict layer boundaries (no upward violations)
- [ ] Shared logic in `@shared`, not between features
- [ ] One primary class per file (.NET)

### Error Handling
- [ ] `Result<T, E>` or discriminated unions for expected failures
- [ ] Branded errors with `kind` property
- [ ] Never throw raw `Error` (use domain wrappers)
- [ ] `cause` preserved on all throws
- [ ] Error paths logged with trace context
- [ ] Errors fail loudly (no silent recovery)

### Production Readiness
- [ ] No TODOs in code
- [ ] No placeholders or scaffolds
- [ ] No commented-out code
- [ ] All dependencies version-locked
- [ ] No >25 KB dead dependencies
- [ ] Startup validation for config
- [ ] Health checks implemented
- [ ] Graceful shutdown handlers

## Review Process

1. **Scan all modified files** for language-specific compliance
2. **Check tag usage** - ensure all applicable tags are used
3. **Validate forbidden patterns** - ensure none are present
4. **Review architecture** - check boundaries and dependencies
5. **Verify security** - validate all security patterns applied
6. **Check observability** - ensure logging/tracing coverage
7. **Validate documentation** - JSDoc/XML comments complete
8. **Confirm production readiness** - no TODOs, scaffolds, or placeholders

## Output Requirements
- Comprehensive compliance report
- List of violations found (if any)
- Missed opportunities for strict features
- Recommendations for improvements
- Pass/fail status with specific line references
- Priority classification (blocking vs. nice-to-have)
- No code generation - review only
