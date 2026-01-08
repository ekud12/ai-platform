# C# Forbidden Patterns Rules

## Purpose

This rulebook explicitly defines patterns that are banned from C# codebases. These patterns are known to cause problems and must not be used.

## Authority

These rules define absolute prohibitions. No exception mechanism exists for forbidden patterns.

## Scope

Applies to all C# code without exception.

## Constraints

- Forbidden patterns must be eliminated, not waived
- Legacy code must be refactored to remove violations
- No new code may introduce forbidden patterns

## Rule Format

All rules use the CS-FORBID prefix.

---

## CS-FORBID-001 — No Dynamic Type

**Rule**
The dynamic keyword is forbidden except for COM interop scenarios.

**Rationale**
Dynamic bypasses compile-time type checking. It hides bugs that would be caught by the compiler and reduces code maintainability.

**Enforcement**
Build must fail on dynamic usage outside COM interop. Code review must reject dynamic. Existing usage must be refactored.

---

## CS-FORBID-002 — No Reflection for Business Logic

**Rule**
Reflection must not be used for business logic. Reflection is permitted only for framework code.

**Rationale**
Reflection is slow, fragile, and difficult to maintain. Business logic must use compile-time safe patterns.

**Enforcement**
Code review must identify reflection usage. Business logic with reflection must be refactored. Framework-level reflection must be isolated.

---

## CS-FORBID-003 — No Thread.Sleep

**Rule**
Thread.Sleep is forbidden. Task.Delay must be used for delays in async code.

**Rationale**
Thread.Sleep blocks the thread, wasting resources. It cannot be cancelled and does not work correctly in async contexts.

**Enforcement**
Build analyzers must flag Thread.Sleep. Code review must reject thread blocking. Async code must use Task.Delay.

---

## CS-FORBID-004 — No Empty Catch

**Rule**
Empty catch blocks are forbidden. All exceptions must be logged or rethrown.

**Rationale**
Empty catches hide failures and make debugging impossible. Every exception must be recorded or propagated.

**Enforcement**
Build analyzers must flag empty catches. Code review must verify exception handling. Comments are not sufficient justification.

---

## CS-FORBID-005 — No Catch Exception

**Rule**
Catching base Exception is forbidden except at top-level handlers.

**Rationale**
Catching all exceptions masks specific failures. It catches fatal exceptions that should not be handled.

**Enforcement**
Code review must verify exception specificity. Specific exception types must be caught. Top-level handlers must log before suppressing.

---

## CS-FORBID-006 — No Mutable Statics

**Rule**
Mutable static fields are forbidden except for thread-safe caches.

**Rationale**
Mutable statics create hidden state and race conditions. They make testing difficult and behavior unpredictable.

**Enforcement**
Build analyzers must flag mutable statics. Caches must use ConcurrentDictionary or equivalent. Other mutable statics must be refactored.

---

## CS-FORBID-007 — No Service Locator

**Rule**
Service locator pattern is forbidden. Dependency injection must be used.

**Rationale**
Service locator hides dependencies and complicates testing. Constructor injection makes dependencies explicit.

**Enforcement**
Code review must identify service locator usage. IServiceProvider usage outside composition root is forbidden.

---

## CS-FORBID-008 — No God Classes

**Rule**
Classes exceeding 500 lines or 20 public members must be refactored.

**Rationale**
Large classes violate single responsibility. They are difficult to understand, test, and maintain.

**Enforcement**
Build must warn on class size thresholds. Code review must require refactoring plan. New code must stay within limits.

---

## CS-FORBID-009 — No Magic Strings

**Rule**
String literals used as identifiers or configuration keys must be constants or nameof expressions.

**Rationale**
Magic strings break refactoring and enable typo bugs. Constants and nameof enable compile-time validation.

**Enforcement**
Code review must identify magic strings. Configuration keys must be constants. Property names must use nameof.

---

## CS-FORBID-010 — No Obsolete API Usage

**Rule**
APIs marked Obsolete must not be used in new code.

**Rationale**
Obsolete APIs will be removed in future versions. Using them creates technical debt and upgrade blockers.

**Enforcement**
Build warnings for obsolete usage must be errors. New code must use recommended alternatives. Migration plan required for existing usage.

---

## CS-FORBID-011 — No GC.Collect

**Rule**
Manual `GC.Collect()` calls are forbidden except in benchmarks or test cleanup.

**Rationale**
Manual GC disrupts the runtime's optimization. It causes performance issues and indicates design problems.

**Enforcement**
Build analyzers must flag GC.Collect. Code review must reject manual collection. Benchmark code must be clearly marked.

---

## CS-FORBID-012 — No Direct Thread Creation

**Rule**
Direct `new Thread()` is forbidden. Use `Task.Run` or thread pool.

**Rationale**
Manual threads bypass the thread pool and its optimizations. They make resource management difficult.

**Enforcement**
Build analyzers must flag Thread constructor. Task-based patterns must be used. Background services must use IHostedService.

---

## CS-FORBID-013 — No Ambient Context

**Rule**
`ThreadLocal<T>` and `AsyncLocal<T>` for passing dependencies are forbidden. Use dependency injection.

**Rationale**
Ambient context hides dependencies and complicates testing. It creates implicit coupling that is hard to reason about.

**Enforcement**
Code review must identify ambient context patterns. Dependencies must be explicit constructor parameters. HttpContext.Current patterns must be refactored.
