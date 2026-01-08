# TypeScript Async Rules

## Purpose

This rulebook defines standards for asynchronous programming in TypeScript. Correct async patterns prevent bugs and improve reliability.

## Authority

These rules govern all Promise-based and async/await code in TypeScript.

## Scope

Applies to all asynchronous operations including network requests, timers, and concurrent operations.

## Constraints

- Promises must not be dropped
- Errors must be handled
- Cancellation must be supported

## Rule Format

All rules use the TS-ASYNC prefix.

---

## TS-ASYNC-001 — Await Promises

**Rule**
All Promises must be awaited or explicitly handled. Floating promises are forbidden.

**Rationale**
Unhandled promises swallow errors silently. They indicate fire-and-forget patterns that lose error context.

**Enforcement**
ESLint no-floating-promises must be enabled. All promise chains must terminate. Code review must verify promise handling.

---

## TS-ASYNC-002 — AbortSignal Required

**Rule**
Long-running async operations must accept AbortSignal for cancellation.

**Rationale**
Without cancellation, operations continue after callers no longer need results. AbortSignal enables graceful cancellation.

**Enforcement**
Network requests must accept AbortSignal. Long operations must check signal. Code review must verify cancellation support.

---

## TS-ASYNC-003 — Timeout All Requests

**Rule**
All external requests must have explicit timeouts configured.

**Rationale**
Without timeouts, external failures hang indefinitely. Timeouts enable graceful degradation and resource protection.

**Enforcement**
Fetch calls must have timeout via AbortSignal. Default timeouts must be configured. Timeout values must be documented.

---

## TS-ASYNC-004 — Promise.all for Parallel

**Rule**
Independent concurrent operations must use Promise.all, not sequential await.

**Rationale**
Sequential await of independent operations wastes time. Promise.all enables concurrent execution.

**Enforcement**
Code review must identify parallelizable operations. Independent awaits must be refactored. Promise.all must be used for concurrency.

---

## TS-ASYNC-005 — Promise.allSettled for Resilience

**Rule**
Concurrent operations that should not fail together must use Promise.allSettled.

**Rationale**
Promise.all fails fast on first rejection. allSettled enables partial success handling.

**Enforcement**
Batch operations must use allSettled when appropriate. Results must handle settled status. Partial failures must be reported.

---

## TS-ASYNC-006 — No Async IIFE

**Rule**
Async immediately-invoked function expressions are forbidden. Use named functions or proper async initialization.

**Rationale**
Async IIFEs hide complexity and make errors hard to trace. Named functions improve debugging and testing.

**Enforcement**
ESLint must flag async IIFE. Code review must reject anonymous async. Named async functions must be used.

---

## TS-ASYNC-007 — Error Propagation

**Rule**
Async functions must either handle errors or propagate them. Swallowing errors is forbidden.

**Rationale**
Swallowed errors make debugging impossible. Error propagation ensures issues are visible.

**Enforcement**
Try-catch must rethrow or log at minimum. Empty catch blocks are forbidden. Error boundaries must be documented.

---

## TS-ASYNC-008 — Race Condition Prevention

**Rule**
State mutations in async contexts must account for race conditions.

**Rationale**
Async operations can complete out of order. State mutations without protection cause data corruption.

**Enforcement**
Shared state updates must be atomic or guarded. Code review must identify race condition potential. Testing must include concurrent scenarios.

---

## TS-ASYNC-009 — Retry Logic

**Rule**
Transient failure scenarios must implement retry with exponential backoff.

**Rationale**
Transient failures are common in distributed systems. Proper retry improves reliability without overwhelming services.

**Enforcement**
Network operations must have retry configuration. Retry must use exponential backoff. Maximum retries must be bounded.

---

## TS-ASYNC-010 — No Callback Hell

**Rule**
Callback-based APIs must be wrapped in Promises. Nested callbacks are forbidden.

**Rationale**
Callback nesting creates unreadable code. Promise wrappers enable async/await usage.

**Enforcement**
Legacy callbacks must be promisified. New code must use Promise-based APIs. Code review must reject nesting.

---

## TS-ASYNC-011 — Async Generators for Streaming

**Rule**
Use async generators (`async function*`) for streaming data instead of collecting into arrays.

**Rationale**
Generators yield items one at a time, reducing memory usage. They enable processing before full data is available.

**Enforcement**
Large dataset processing must use generators. Code review must identify buffering anti-patterns. Memory usage must be monitored.

---

## TS-ASYNC-012 — No Promise Constructor Anti-pattern

**Rule**
Avoid wrapping existing promises in `new Promise()`. Return the promise directly.

**Rationale**
Unnecessary Promise wrapping adds overhead and can swallow errors. It indicates misunderstanding of promise chaining.

**Enforcement**
ESLint no-async-promise-executor must be enabled. Redundant wrappers must be removed. Code review must verify promise handling.
